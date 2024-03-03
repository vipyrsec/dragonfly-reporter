from collections.abc import Generator
from functools import cache
from typing import Annotated

import httpx
from fastapi import Depends

from dragonfly_reporter.constants import PyPI


class BearerAuthentication(httpx.Auth):
    def __init__(self, *, token: str) -> None:
        self.token = token

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


@cache
def http_client() -> httpx.AsyncClient:
    auth = BearerAuthentication(token=PyPI.api_token)
    http_client = httpx.AsyncClient(auth=auth, base_url=PyPI.base_url)

    return http_client


HTTPClientDependency = Annotated[httpx.AsyncClient, Depends(http_client)]
