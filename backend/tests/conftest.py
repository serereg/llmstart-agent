from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.agent.core import get_agent_service
from app.config import get_settings
from app.observability.langfuse import get_langfuse_client
from app.rag.store import get_knowledge_retriever, init_rag_index, reset_rag_state

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
    get_langfuse_client.cache_clear()
    get_knowledge_retriever.cache_clear()
    reset_rag_state()
    yield
    get_settings.cache_clear()
    get_agent_service.cache_clear()
    get_langfuse_client.cache_clear()
    get_knowledge_retriever.cache_clear()
    reset_rag_state()


@pytest.fixture(autouse=True)
def mock_rag_index(monkeypatch: pytest.MonkeyPatch) -> None:
    """Avoid OpenAI embedding API calls during tests."""
    from tests.test_rag import FakeEmbeddings  # noqa: PLC0415

    def _fake_init(settings=None):
        from app.config import get_settings as gs  # noqa: PLC0415
        from app.rag.indexer import build_chroma_index  # noqa: PLC0415

        resolved = settings or gs()
        return build_chroma_index(FakeEmbeddings(), resolved.data_dir)

    monkeypatch.setattr("app.rag.store._build_embeddings", lambda _s: FakeEmbeddings())
    monkeypatch.setattr("app.rag.store.init_rag_index", _fake_init)
    init_rag_index()
    get_knowledge_retriever.cache_clear()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    from app.main import create_app  # noqa: PLC0415

    with TestClient(create_app()) as test_client:
        yield test_client
