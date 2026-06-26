"""Process-wide RAG index singleton."""

from functools import lru_cache

from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings

from app.config import Settings, get_settings
from app.rag.indexer import build_chroma_index
from app.rag.retriever import KnowledgeRetriever

_vectorstore: Chroma | None = None


def _build_embeddings(settings: Settings) -> OpenAIEmbeddings | AzureOpenAIEmbeddings:
    common_kwargs = {
        "api_key": settings.openai_api_key,
        "timeout": settings.openai_timeout_sec,
    }
    if settings.openai_api_base:
        return AzureOpenAIEmbeddings(
            azure_endpoint=settings.openai_api_base.rstrip("/"),
            openai_api_version=settings.openai_api_version,
            deployment=settings.openai_embedding_model,
            openai_api_base=None,
            **common_kwargs,
        )
    return OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        **common_kwargs,
    )


def init_rag_index(settings: Settings | None = None) -> Chroma:
    """Build or rebuild the in-memory knowledge base index."""
    global _vectorstore  # noqa: PLW0603
    resolved = settings or get_settings()
    _vectorstore = build_chroma_index(
        _build_embeddings(resolved),
        resolved.data_dir,
    )
    return _vectorstore


def get_vectorstore() -> Chroma:
    """Return the initialized vector store."""
    if _vectorstore is None:
        msg = "RAG index not initialized — call init_rag_index() at startup"
        raise RuntimeError(msg)
    return _vectorstore


@lru_cache
def get_knowledge_retriever() -> KnowledgeRetriever:
    """Return the process-wide knowledge retriever."""
    return KnowledgeRetriever(get_vectorstore())


def reset_rag_state() -> None:
    """Clear singleton state (used in tests)."""
    global _vectorstore  # noqa: PLW0603
    _vectorstore = None
    get_knowledge_retriever.cache_clear()
