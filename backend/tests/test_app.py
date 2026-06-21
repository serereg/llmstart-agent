from fastapi.testclient import TestClient

from app.main import app, create_app


def test_app_imports() -> None:
    assert app is not None
    assert create_app() is not None


def test_docs_returns_200(client: TestClient) -> None:
    response = client.get("/docs")
    assert response.status_code == 200
