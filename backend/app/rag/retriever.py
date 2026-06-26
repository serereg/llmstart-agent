"""Knowledge base retriever — similarity search with audience filter."""

from typing import Literal

from langchain_chroma import Chroma
from langchain_core.documents import Document

Audience = Literal["b2b", "b2c"]
DEFAULT_TOP_K = 4


class KnowledgeRetriever:
    """Wrapper around Chroma vector store with audience filtering."""

    def __init__(self, vectorstore: Chroma, *, top_k: int = DEFAULT_TOP_K) -> None:
        self._vectorstore = vectorstore
        self._top_k = top_k

    def search(self, query: str, audience: Audience) -> list[Document]:
        """Return top-k chunks filtered by audience metadata."""
        return self._vectorstore.similarity_search(
            query,
            k=self._top_k,
            filter={"audience": audience},
        )

    def format_results(self, documents: list[Document]) -> str:
        """Format retrieved chunks as context for the agent."""
        if not documents:
            return "Релевантных материалов в базе знаний не найдено."

        parts: list[str] = []
        for index, doc in enumerate(documents, start=1):
            source = doc.metadata.get("source", "unknown")
            parts.append(f"[{index}] ({source})\n{doc.page_content.strip()}")
        return "\n\n".join(parts)
