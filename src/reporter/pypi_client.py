"""A PyPI client."""

from collections.abc import Generator
from functools import cache
from typing import Annotated

import httpx
from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from reporter.constants import PyPI
from reporter.models import Observation


class ObservationsAPIFailure(Exception):
    """A failure of PyPI's Observations API.

    Attributes:
        response: The HTTP error response associated with this failure.
    """

    def __init__(self, response: httpx.Response) -> None:
        """Initlalize the ObservationsAPIFailure instance.

        Args:
            response: The HTTP error response associated with this failure.
        """
        self.response = response


class BearerAuthentication(httpx.Auth):
    """An implementation of bearer authentication for HTTPX.

    Attributes:
        token: The bearer token to use.
    """

    def __init__(self, *, token: str) -> None:
        """Initialize the BearerAuthentication instance.

        Args:
            token: The bearer token to use.
        """
        self.token = token

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        """Implement the bearer authentication flow.

        Args:
            request: The HTTPX request.

        Yields:
            The request bearing the bearer token.
        """
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


class PyPIClient:
    """A client to interact with the PyPI API."""

    def __init__(self) -> None:
        """Initialize the client instance."""
        auth = BearerAuthentication(token=PyPI.api_token)
        headers = {"Content-Type": "application/vnd.pypi.api-v0-danger+json"}
        self.http_client = httpx.AsyncClient(auth=auth, base_url=PyPI.base_url, headers=headers)

    async def echo(self) -> str:
        """Echo the PyPI username of the token's user.

        Returns:
            The PyPI username of the token's user.
        """
        response = await self.http_client.get("/echo")
        json = response.json()
        return json["username"]

    async def send_observation(self, project_name: str, observation: Observation) -> None:
        """Send an observation about a project to PyPI.

        Args:
            project_name: The name of the PyPI project.
            observation: THe observation to send.

        Raises:
            ObservationsAPIFailure: In case the request fails.
        """
        path = f"/projects/{project_name}/observations"
        json = jsonable_encoder(observation)

        response = await self.http_client.post(path, json=json)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ObservationsAPIFailure(response) from exc


@cache
def get_pypi_client() -> PyPIClient:
    """Return an instance of the PyPI client.

    Returns:
        An instance of the PyPI client.
    """
    return PyPIClient()


PyPIClientDependency = Annotated[PyPIClient, Depends(get_pypi_client)]
