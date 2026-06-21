from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

VALID_AUTH_HEADER = {"Authorization": "Bearer test-backend-key"}


def test_api_v1_without_api_key_returns_401(client: TestClient) -> None:
    response = client.get("/api/v1/ping")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key"}


def test_api_v1_with_wrong_api_key_returns_401(client: TestClient) -> None:
    response = client.get(
        "/api/v1/ping",
        headers={"Authorization": "Bearer wrong-key"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key"}


def test_api_v1_with_valid_api_key_returns_200(client: TestClient) -> None:
    response = client.get("/api/v1/ping", headers=VALID_AUTH_HEADER)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_without_api_key_returns_200(client: TestClient) -> None:
    with (
        patch("app.api.health.probe_openai", new=AsyncMock(return_value="ok")),
        patch("app.api.health.probe_langfuse", new=AsyncMock(return_value="ok")),
    ):
        response = client.get("/health")

    assert response.status_code == 200
