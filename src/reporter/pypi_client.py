from collections.abc import Generator
from functools import cache
from typing import Annotated

import httpx
from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from reporter.constants import PyPI
from reporter.models import Observation


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
        self.http_client = httpx.AsyncClient(auth=auth, base_url=PyPI.base_url)

    async def send_observation(self, project_name: str, observation: Observation):
        path = f"/danger-api/projects/{project_name}/observations"
        json = jsonable_encoder(observation)

        await self.http_client.post(path, json=json)


@cache
def get_pypi_client() -> PyPIClient:
    return PyPIClient()


PyPIClientDependency = Annotated[PyPIClient, Depends(get_pypi_client)]
