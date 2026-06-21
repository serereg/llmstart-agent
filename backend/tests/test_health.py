from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def test_health_returns_200_when_all_dependencies_ok(client: TestClient) -> None:
    with (
        patch("app.api.health.probe_openai", new=AsyncMock(return_value="ok")),
        patch("app.api.health.probe_langfuse", new=AsyncMock(return_value="ok")),
    ):
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": "0.1.0",
        "dependencies": {"openai": "ok", "langfuse": "ok"},
    }


def test_health_returns_503_when_langfuse_degraded(client: TestClient) -> None:
    with (
        patch("app.api.health.probe_openai", new=AsyncMock(return_value="ok")),
        patch("app.api.health.probe_langfuse", new=AsyncMock(return_value="error")),
    ):
        response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "version": "0.1.0",
        "dependencies": {"openai": "ok", "langfuse": "error"},
    }


def test_health_returns_503_when_openai_degraded(client: TestClient) -> None:
    with (
        patch("app.api.health.probe_openai", new=AsyncMock(return_value="error")),
        patch("app.api.health.probe_langfuse", new=AsyncMock(return_value="ok")),
    ):
        response = client.get("/health")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["dependencies"]["openai"] == "error"
    assert body["dependencies"]["langfuse"] == "ok"


def test_health_does_not_require_auth(client: TestClient) -> None:
    with (
        patch("app.api.health.probe_openai", new=AsyncMock(return_value="ok")),
        patch("app.api.health.probe_langfuse", new=AsyncMock(return_value="ok")),
    ):
        response = client.get("/health")

    assert response.status_code == 200
    assert "Authorization" not in response.request.headers
