from unittest.mock import MagicMock

import httpx
import pytest

from reporter.app import app
from reporter.pypi_client import PyPIClient, get_pypi_client


@pytest.fixture(scope="session")
def mock_pypi_client() -> PyPIClient:
    client = PyPIClient()
    client.http_client = MagicMock(spec=httpx.AsyncClient)
    return client


@pytest.fixture(scope="session", autouse=True)
def override_dependencies(mock_pypi_client: PyPIClient) -> None:
    app.dependency_overrides[get_pypi_client] = lambda: mock_pypi_client
