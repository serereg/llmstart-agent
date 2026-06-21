"""LangChain ReAct agent — skeleton without business tools."""

from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, cast
from uuid import UUID

from langchain.agents import create_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from openai import APIConnectionError, APIError, APITimeoutError, RateLimitError

from app.agent.prompts import SYSTEM_PROMPT
from app.config import Settings, get_settings
from app.sessions.models import Message, MessageRole

FALLBACK_MESSAGE = "Сервис временно недоступен, попробуйте позже"

_OPENAI_ERRORS = (APIError, APIConnectionError, APITimeoutError, RateLimitError)


@dataclass(frozen=True, slots=True)
class AgentInvokeResult:
    """Result of a non-streaming agent invocation."""

    reply: str
    error: bool = False


def session_messages_to_langchain(messages: Sequence[Message]) -> list[BaseMessage]:
    """Convert session history to LangChain chat messages."""
    result: list[BaseMessage] = []
    for message in messages:
        if message.role == MessageRole.USER:
            result.append(HumanMessage(content=message.content))
        elif message.role == MessageRole.ASSISTANT:
            result.append(AIMessage(content=message.content))
    return result


def _build_agent_input(
    user_message: str,
    history: Sequence[Message],
) -> dict[str, list[BaseMessage]]:
    messages = [*session_messages_to_langchain(history), HumanMessage(content=user_message)]
    return {"messages": messages}


def _extract_reply(result: dict[str, Any]) -> str:
    messages = result.get("messages", [])
    if not messages:
        return ""
    last_message = messages[-1]
    content = last_message.content
    if isinstance(content, str):
        return content
    return str(content)


def _chunk_content(chunk: AIMessageChunk) -> str:
    content = chunk.content
    if not content:
        return ""
    if isinstance(content, str):
        return content
    return str(content)


class AgentService:
    """ReAct agent wrapper with invoke and SSE streaming."""

    def __init__(self, llm: BaseChatModel) -> None:
        self._agent: Any = create_agent(llm, tools=[], system_prompt=SYSTEM_PROMPT)

    async def invoke(self, user_message: str, history: Sequence[Message]) -> AgentInvokeResult:
        """Run agent and return the final reply."""
        agent_input: dict[str, Any] = _build_agent_input(user_message, history)
        try:
            result = await self._agent.ainvoke(agent_input)
        except _OPENAI_ERRORS:
            return AgentInvokeResult(reply=FALLBACK_MESSAGE, error=True)
        return AgentInvokeResult(reply=_extract_reply(result))

    async def stream_sse(
        self,
        user_message: str,
        history: Sequence[Message],
        session_id: UUID,
    ) -> AsyncIterator[tuple[str, dict[str, object]]]:
        """Yield SSE event tuples: reasoning, token, error, done."""
        agent_input: dict[str, Any] = _build_agent_input(user_message, history)
        reply_parts: list[str] = []

        yield ("reasoning", {"step": 1, "content": "Формирую ответ..."})

        try:
            async for event in self._agent.astream_events(agent_input, version="v2"):
                if event["event"] != "on_chat_model_stream":
                    continue
                chunk = cast("AIMessageChunk", event["data"]["chunk"])
                token = _chunk_content(chunk)
                if not token:
                    continue
                reply_parts.append(token)
                yield ("token", {"content": token})
        except _OPENAI_ERRORS:
            yield ("error", {"message": FALLBACK_MESSAGE})
            yield (
                "done",
                {
                    "session_id": str(session_id),
                    "reply": FALLBACK_MESSAGE,
                    "error": True,
                },
            )
            return

        reply = "".join(reply_parts)
        yield (
            "done",
            {
                "session_id": str(session_id),
                "reply": reply,
                "error": False,
            },
        )


def create_agent_service(llm: BaseChatModel) -> AgentService:
    """Build an agent service with the given chat model."""
    return AgentService(llm)


@lru_cache
def get_agent_service() -> AgentService:
    """Return the process-wide agent service singleton."""
    settings = get_settings()
    llm = ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        timeout=settings.openai_timeout_sec,
    )
    return create_agent_service(llm)


def build_agent_service(settings: Settings) -> AgentService:
    """Create an agent service from explicit settings (used in tests)."""
    llm = ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        timeout=settings.openai_timeout_sec,
    )
    return create_agent_service(llm)
