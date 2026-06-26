"""LangChain ReAct agent with business tools, Langfuse tracing, and SSE streaming."""

from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, cast

from langchain.agents import create_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from openai import APIConnectionError, APIError, APITimeoutError, RateLimitError

from app.agent.prompts import SYSTEM_PROMPT
from app.config import Settings, get_settings
from app.observability.langfuse import build_invoke_config
from app.rag.retriever import KnowledgeRetriever
from app.rag.store import get_knowledge_retriever
from app.sessions.models import Message, MessageRole, Session
from app.sessions.store import SessionStore, get_session_store
from app.tools.context import ToolContext, clear_tool_context, set_tool_context
from app.tools.registry import BUSINESS_TOOLS

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


def _serialize_tool_output(output: object) -> str:
    if isinstance(output, str):
        return output
    if hasattr(output, "content"):
        content = output.content
        if isinstance(content, str):
            return content
    return str(output)


def _parse_stream_event(event: dict[str, Any]) -> tuple[str, dict[str, object]] | None:
    """Map LangChain astream_events v2 events to SSE event tuples."""
    event_type = event.get("event")
    if event_type == "on_chat_model_stream":
        chunk = cast("AIMessageChunk", event["data"]["chunk"])
        token = _chunk_content(chunk)
        if token:
            return ("token", {"content": token})
        return None

    if event_type == "on_tool_start":
        return (
            "tool_start",
            {
                "name": event.get("name", ""),
                "args": event.get("data", {}).get("input", {}),
            },
        )

    if event_type == "on_tool_end":
        output = event.get("data", {}).get("output")
        return (
            "tool_end",
            {
                "name": event.get("name", ""),
                "result": _serialize_tool_output(output) if output is not None else "",
            },
        )

    return None


class AgentService:
    """ReAct agent wrapper with invoke and SSE streaming."""

    def __init__(
        self,
        llm: BaseChatModel,
        *,
        store: SessionStore,
        retriever: KnowledgeRetriever,
        settings: Settings,
    ) -> None:
        self._agent: Any = create_agent(llm, tools=BUSINESS_TOOLS, system_prompt=SYSTEM_PROMPT)
        self._store = store
        self._retriever = retriever
        self._settings = settings

    def _bind_tool_context(self, session: Session) -> None:
        set_tool_context(
            ToolContext(
                session_id=session.session_id,
                channel=session.channel.value,
                store=self._store,
                retriever=self._retriever,
                leads_file_path=str(self._settings.leads_file),
                products_file_path=str(self._settings.products_file),
            ),
        )

    def _invoke_config(self, session: Session) -> dict[str, object]:
        return build_invoke_config(
            session_id=str(session.session_id),
            channel=session.channel.value,
            segment=session.segment,
        )

    async def invoke(
        self,
        user_message: str,
        history: Sequence[Message],
        session: Session,
    ) -> AgentInvokeResult:
        """Run agent and return the final reply."""
        agent_input: dict[str, Any] = _build_agent_input(user_message, history)
        self._bind_tool_context(session)
        try:
            result = await self._agent.ainvoke(agent_input, config=self._invoke_config(session))
        except _OPENAI_ERRORS:
            return AgentInvokeResult(reply=FALLBACK_MESSAGE, error=True)
        finally:
            clear_tool_context()
        return AgentInvokeResult(reply=_extract_reply(result))

    async def stream_sse(
        self,
        user_message: str,
        history: Sequence[Message],
        session: Session,
    ) -> AsyncIterator[tuple[str, dict[str, object]]]:
        """Yield SSE event tuples: reasoning, tool_start, tool_end, token, error, done."""
        agent_input: dict[str, Any] = _build_agent_input(user_message, history)
        reply_parts: list[str] = []
        reasoning_step = 0

        yield ("reasoning", {"step": 1, "content": "Анализирую запрос..."})
        self._bind_tool_context(session)

        try:
            async for event in self._agent.astream_events(
                agent_input,
                config=self._invoke_config(session),
                version="v2",
            ):
                parsed = _parse_stream_event(event)
                if parsed is None:
                    continue
                event_name, payload = parsed
                if event_name == "token":
                    reply_parts.append(str(payload["content"]))
                elif event_name == "tool_start":
                    reasoning_step += 1
                    yield (
                        "reasoning",
                        {
                            "step": reasoning_step + 1,
                            "content": f"Вызываю инструмент: {payload['name']}",
                        },
                    )
                yield event_name, payload
        except _OPENAI_ERRORS:
            yield ("error", {"message": FALLBACK_MESSAGE})
            yield (
                "done",
                {
                    "session_id": str(session.session_id),
                    "reply": FALLBACK_MESSAGE,
                    "error": True,
                },
            )
            return
        finally:
            clear_tool_context()

        reply = "".join(reply_parts)
        yield (
            "done",
            {
                "session_id": str(session.session_id),
                "reply": reply,
                "error": False,
            },
        )


def create_agent_service(
    llm: BaseChatModel,
    *,
    store: SessionStore,
    retriever: KnowledgeRetriever,
    settings: Settings,
) -> AgentService:
    """Build an agent service with the given dependencies."""
    return AgentService(
        llm,
        store=store,
        retriever=retriever,
        settings=settings,
    )


def _build_chat_model(settings: Settings) -> BaseChatModel:
    """Create a chat model for OpenAI or Azure-compatible endpoints."""
    common_kwargs = {
        "api_key": settings.openai_api_key,
        "timeout": settings.openai_timeout_sec,
    }
    if settings.openai_api_base:
        return AzureChatOpenAI(
            azure_endpoint=settings.openai_api_base.rstrip("/"),
            api_version=settings.openai_api_version,
            azure_deployment=settings.openai_model,
            **common_kwargs,
        )
    return ChatOpenAI(
        model=settings.openai_model,
        **common_kwargs,
    )


@lru_cache
def get_agent_service() -> AgentService:
    """Return the process-wide agent service singleton."""
    settings = get_settings()
    return create_agent_service(
        _build_chat_model(settings),
        store=get_session_store(),
        retriever=get_knowledge_retriever(),
        settings=settings,
    )


def build_agent_service(settings: Settings) -> AgentService:
    """Create an agent service from explicit settings (used in tests)."""
    return create_agent_service(
        _build_chat_model(settings),
        store=get_session_store(),
        retriever=get_knowledge_retriever(),
        settings=settings,
    )
