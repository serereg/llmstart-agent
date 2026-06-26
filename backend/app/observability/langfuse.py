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


def shutdown_langfuse_client() -> None:
    """Flush pending traces and shut down the Langfuse client."""
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return
    get_langfuse_client().shutdown()


def create_langfuse_handler() -> CallbackHandler:
    """Create a LangChain callback handler for a single agent invocation."""
    get_langfuse_client()
    return CallbackHandler()


def _build_langfuse_tags(channel: str, segment: str | None) -> list[str]:
    tags = [f"channel:{channel}"]
    if segment is not None:
        tags.append(f"segment:{segment}")
    return tags


def build_invoke_config(
    *,
    session_id: str,
    channel: str,
    segment: str | None,
) -> dict[str, object]:
    """Build RunnableConfig with Langfuse callback and trace metadata."""
    metadata: dict[str, object] = {
        "langfuse_session_id": session_id,
        "channel": channel,
        "langfuse_tags": _build_langfuse_tags(channel, segment),
    }
    if segment is not None:
        metadata["segment"] = segment

    config: dict[str, object] = {"metadata": metadata}
    if os.environ.get("PYTEST_CURRENT_TEST") is None:
        config["callbacks"] = [create_langfuse_handler()]
    return config
