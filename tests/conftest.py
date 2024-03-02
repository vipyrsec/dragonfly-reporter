from unittest.mock import MagicMock

import httpx
import pytest

from dragonfly_reporter.app import app
from dragonfly_reporter.http_client import http_client


@pytest.fixture(scope="session")
def mock_http_client() -> MagicMock:
    return MagicMock(spec=httpx.AsyncClient)


@pytest.fixture(scope="session", autouse=True)
def _override_dependencies(  # type: ignore
    mock_http_client: MagicMock,
):
    app.dependency_overrides[http_client] = lambda: mock_http_client
