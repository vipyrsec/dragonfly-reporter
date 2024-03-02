from collections.abc import Generator
from typing import Annotated
from fastapi import Depends
import httpx
from dragonfly_reporter.constants import reporter_settings
from functools import cache

BASE_URL = "https://pypi.org/danger-api"

class BearerAuthentication(httpx.Auth):
    def __init__(self, *, token: str) -> None:
        self.token = token

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request

@cache
def http_client() -> httpx.AsyncClient:
    auth = BearerAuthentication(token=reporter_settings.observation_api_token)
    http_client = httpx.AsyncClient(auth=auth, base_url=BASE_URL)

    return http_client

HTTPClientDependency = Annotated[httpx.AsyncClient, Depends(http_client)]
