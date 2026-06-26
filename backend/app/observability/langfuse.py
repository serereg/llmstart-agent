"""Langfuse observability — client init and LangChain callback handler."""

import os
from functools import lru_cache

from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

from app.config import get_settings


@lru_cache
def get_langfuse_client() -> Langfuse:
    """Initialize and return the process-wide Langfuse client."""
    settings = get_settings()
    tracing_enabled = os.environ.get("PYTEST_CURRENT_TEST") is None
    return Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
        tracing_enabled=tracing_enabled,
    )


def create_langfuse_handler() -> CallbackHandler:
    """Create a LangChain callback handler for a single agent invocation."""
    settings = get_settings()
    get_langfuse_client()
    return CallbackHandler(public_key=settings.langfuse_public_key)


def build_invoke_config(
    *,
    session_id: str,
    channel: str,
    segment: str | None,
) -> dict[str, object]:
    """Build RunnableConfig with Langfuse callback and trace metadata."""
    metadata: dict[str, object] = {
        "session_id": session_id,
        "channel": channel,
    }
    if segment is not None:
        metadata["segment"] = segment

    config: dict[str, object] = {"metadata": metadata}
    if os.environ.get("PYTEST_CURRENT_TEST") is None:
        config["callbacks"] = [create_langfuse_handler()]
    return config
