"""Unit tests for RAG indexer and retriever."""

from pathlib import Path

import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.rag.indexer import build_chroma_index, load_documents
from app.rag.retriever import KnowledgeRetriever


class FakeEmbeddings(Embeddings):
    """Deterministic embeddings for tests (no API calls)."""

    def _vector(self, text: str) -> list[float]:
        lowered = text.lower()
        agents = float("agent" in lowered or "агент" in lowered)
        corporate = float("корпоратив" in lowered or "enterprise" in lowered or "b2b" in lowered)
        fundamentals = float("fundamental" in lowered or "основ" in lowered)
        return [agents, corporate, fundamentals, float(len(text))]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)


@pytest.fixture
def data_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "data"


def test_load_documents_finds_b2c_and_b2b_files(data_dir: Path) -> None:
    b2c_docs = load_documents(data_dir, "b2c")
    b2b_docs = load_documents(data_dir, "b2b")

    assert len(b2c_docs) >= 2
    assert len(b2b_docs) >= 2
    assert all(doc.metadata["audience"] == "b2c" for doc in b2c_docs)
    assert all(doc.metadata["audience"] == "b2b" for doc in b2b_docs)


def test_build_chroma_index_creates_searchable_store(data_dir: Path) -> None:
    embeddings = FakeEmbeddings()
    vectorstore = build_chroma_index(embeddings, data_dir)

    retriever = KnowledgeRetriever(vectorstore, top_k=2)
    b2c_results = retriever.search("курс agents", "b2c")
    b2b_results = retriever.search("корпоративное обучение", "b2b")

    assert len(b2c_results) >= 1
    assert all(doc.metadata["audience"] == "b2c" for doc in b2c_results)
    assert len(b2b_results) >= 1
    assert all(doc.metadata["audience"] == "b2b" for doc in b2b_results)


def test_retriever_format_results_empty() -> None:
    retriever = KnowledgeRetriever(
        build_chroma_index(FakeEmbeddings(), Path("/nonexistent")),
    )
    formatted = retriever.format_results([])
    assert "не найдено" in formatted.lower()


def test_retriever_format_results_includes_source() -> None:
    retriever = KnowledgeRetriever(
        build_chroma_index(FakeEmbeddings(), Path("/nonexistent")),
    )
    docs = [Document(page_content="Test content", metadata={"source": "test.md"})]
    formatted = retriever.format_results(docs)
    assert "test.md" in formatted
    assert "Test content" in formatted
