from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.agent.core import get_agent_service
from app.config import get_settings

TEST_ENV = {
    "OPENAI_API_KEY": "test-openai-key",
    "LANGFUSE_PUBLIC_KEY": "pk-test",
    "LANGFUSE_SECRET_KEY": "sk-test",
    "BACKEND_API_KEY": "test-backend-key",
    "OPENAI_MODEL": "gpt-4o",
}


@pytest.fixture(autouse=True)
def test_env(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    for key, value in TEST_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("OPENAI_API_BASE", raising=False)
    monkeypatch.delenv("OPENAI_API_VERSION", raising=False)
    get_settings.cache_clear()
    get_agent_service.cache_clear()
    yield
    get_settings.cache_clear()
    get_agent_service.cache_clear()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    from app.main import create_app  # noqa: PLC0415

    with TestClient(create_app()) as test_client:
        yield test_client
