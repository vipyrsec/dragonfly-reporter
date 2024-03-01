from collections.abc import Generator
import httpx
from dragonfly_reporter.constants import reporter_settings

BASE_URL = "https://pypi.org/danger-api"

class BearerAuthentication(httpx.Auth):
    def __init__(self, *, token: str) -> None:
        self.token = token

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request

auth = BearerAuthentication(token=reporter_settings.observation_api_token)

http_client = httpx.AsyncClient(auth=auth, base_url=BASE_URL)
