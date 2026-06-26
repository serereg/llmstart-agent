"""Test doubles for LangChain chat models."""

from collections.abc import AsyncIterator, Callable, Iterator, Sequence
from typing import Any
from unittest.mock import MagicMock

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.outputs import ChatGenerationChunk
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from openai import APIError

_OPENAI_ERROR_MESSAGE = "Service unavailable"


def _raise_openai_error() -> None:
    raise APIError(_OPENAI_ERROR_MESSAGE, request=MagicMock(), body=None)


class ToolCapableFakeChatModel(FakeListChatModel):
    """FakeListChatModel that supports bind_tools for ReAct agent tests."""

    def bind_tools(
        self,
        tools: Sequence[dict[str, Any] | type | Callable[..., Any] | BaseTool],
        *,
        tool_choice: str | None = None,
        **kwargs: Any,
    ) -> Runnable[Any, Any]:
        return self


class FailingChatModel(ToolCapableFakeChatModel):
    """Chat model that always raises an OpenAI APIError."""

    def _call(self, *args: object, **kwargs: object) -> str:
        _raise_openai_error()
        return ""

    def _stream(
        self,
        *args: object,
        **kwargs: object,
    ) -> Iterator[ChatGenerationChunk]:
        _raise_openai_error()
        yield ChatGenerationChunk(message=MagicMock())  # pragma: no cover

    async def _astream(
        self,
        *args: object,
        **kwargs: object,
    ) -> AsyncIterator[ChatGenerationChunk]:
        _raise_openai_error()
        yield ChatGenerationChunk(message=MagicMock())  # pragma: no cover
        return
