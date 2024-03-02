from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from dragonfly_reporter.app import app

test_client = TestClient(app)


def test_report(mock_http_client: MagicMock):
    project_name = "remmy"
    json = {
        "kind": "is_malware",
        "summary": "badguy package",
        "inspector_url": "test inspector url",
        "extra": {"yara_rules": ["abc", "def"]},
    }
    test_client.post(f"/report/{project_name}", json=json)

    mock_http_client.post.assert_called_with("/danger-api/projects/remmy/observations", json=json)  # type: ignore
