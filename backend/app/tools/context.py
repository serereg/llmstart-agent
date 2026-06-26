"""Per-invocation context for session-aware tools."""

from contextvars import ContextVar
from dataclasses import dataclass
from uuid import UUID

from app.rag.retriever import KnowledgeRetriever
from app.sessions.store import SessionStore


@dataclass(frozen=True, slots=True)
class ToolContext:
    """Runtime dependencies available to tools during an agent invoke."""

    session_id: UUID
    channel: str
    store: SessionStore
    retriever: KnowledgeRetriever
    leads_file_path: str
    products_file_path: str


_tool_context: ContextVar[ToolContext | None] = ContextVar("tool_context", default=None)


def set_tool_context(ctx: ToolContext) -> None:
    """Bind tool context for the current agent invocation."""
    _tool_context.set(ctx)


def get_tool_context() -> ToolContext:
    """Return the active tool context or raise if unset."""
    ctx = _tool_context.get()
    if ctx is None:
        msg = "Tool context is not set for this invocation"
        raise RuntimeError(msg)
    return ctx


def clear_tool_context() -> None:
    """Reset tool context after invocation."""
    _tool_context.set(None)
