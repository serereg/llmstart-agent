from fastapi.testclient import TestClient


def test_app_imports(client: TestClient) -> None:
    assert client.app is not None


def test_create_app_factory() -> None:
    from app.main import create_app  # noqa: PLC0415

    assert create_app() is not None


def test_docs_returns_200(client: TestClient) -> None:
    response = client.get("/docs")
    assert response.status_code == 200
