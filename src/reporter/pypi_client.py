from collections.abc import Generator
from functools import cache
from typing import Annotated

import httpx
from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from reporter.constants import PyPI
from reporter.models import Observation


class ObservationsAPIFailure(Exception):
    def __init__(self, response: httpx.Response) -> None:
        self.response = response


class BearerAuthentication(httpx.Auth):
    def __init__(self, *, token: str) -> None:
        self.token = token

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


class PyPIClient:
    """PyPI client to interact with the PyPI API."""

    def __init__(self) -> None:
        auth = BearerAuthentication(token=PyPI.api_token)
        headers = {"Content-Type": "application/vnd.pypi.api-v0-danger+json"}
        self.http_client = httpx.AsyncClient(auth=auth, base_url=PyPI.base_url, headers=headers)

    async def echo(self) -> str:
        response = await self.http_client.get("/echo")
        json = response.json()
        return json["username"]

    async def send_observation(self, project_name: str, observation: Observation) -> None:
        path = f"/projects/{project_name}/observations"
        json = jsonable_encoder(observation)

        response = await self.http_client.post(path, json=json)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            raise ObservationsAPIFailure(response)


@cache
def get_pypi_client() -> PyPIClient:
    return PyPIClient()


PyPIClientDependency = Annotated[PyPIClient, Depends(get_pypi_client)]
