import httpx

from .constants import reporter_settings


def async_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(auth=auth, base_url="https://pypi.org/danger-api")


def auth(r: httpx.Request) -> httpx.Request:
    """Add authentication headers to a request"""

    r.headers["Authorization"] = f"Bearer {reporter_settings.observation_api_token}"
    return r


async def echo() -> str:
    """Return the username of the PyPI User."""

    async with async_client() as client:
        resp = await client.get("/echo")
    return resp.text


async def send_report() -> None:
    ...
