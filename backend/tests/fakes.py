"""Test doubles for LangChain chat models."""

from collections.abc import AsyncIterator, Iterator
from unittest.mock import MagicMock

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.outputs import ChatGenerationChunk
from openai import APIError

_OPENAI_ERROR_MESSAGE = "Service unavailable"


def _raise_openai_error() -> None:
    raise APIError(_OPENAI_ERROR_MESSAGE, request=MagicMock(), body=None)


class FailingChatModel(FakeListChatModel):
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
