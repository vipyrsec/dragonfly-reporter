import httpx
from fastapi.testclient import TestClient

from reporter.app import app
from reporter.pypi_client import PyPIClient

test_client = TestClient(app)


def test_report(mock_pypi_client: PyPIClient) -> None:
    project_name = "remmy"
    json = {
        "kind": "is_malware",
        "summary": "badguy package",
        "inspector_url": "test inspector url",
        "extra": {"yara_rules": ["abc", "def"]},
    }
    test_client.post(f"/report/{project_name}", json=json)

    mock_pypi_client.http_client.post.assert_called_with("/projects/remmy/observations", json=json)  # type: ignore[attr-defined]


def test_invalid_report_payload() -> None:
    project_name = "remmy"
    json = {
        "kind": "is_malware",
        "summary": "badguy package",
        "extra": {"yara_rules": ["abc", "def"]},
    }

    response = test_client.post(f"/report/{project_name}", json=json)
    assert response.status_code == httpx.codes.UNPROCESSABLE_ENTITY
