"""Unit tests for the ReAct agent service."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.agent.core import (
    FALLBACK_MESSAGE,
    AgentService,
    create_agent_service,
    session_messages_to_langchain,
)
from app.config import get_settings
from app.rag.indexer import build_chroma_index
from app.rag.retriever import KnowledgeRetriever
from app.sessions.models import Channel, Message, MessageRole, Session
from app.sessions.store import SessionStore
from tests.fakes import FailingChatModel, ToolCapableFakeChatModel
from tests.test_rag import FakeEmbeddings

MOCK_REPLY = "Рекомендую курс agents для старта."
DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@pytest.fixture
def store() -> SessionStore:
    return SessionStore()


@pytest.fixture
def retriever() -> KnowledgeRetriever:
    return KnowledgeRetriever(build_chroma_index(FakeEmbeddings(), DATA_DIR))


@pytest.fixture
def agent_service(store: SessionStore, retriever: KnowledgeRetriever) -> AgentService:
    llm = ToolCapableFakeChatModel(responses=[MOCK_REPLY])
    return create_agent_service(
        llm,
        store=store,
        retriever=retriever,
        settings=get_settings(),
    )


@pytest.fixture
async def session(store: SessionStore) -> Session:
    return await store.create(Channel.WEB)


@pytest.mark.asyncio
async def test_invoke_returns_mock_reply(
    agent_service: AgentService,
    session: Session,
) -> None:
    result = await agent_service.invoke("Какой курс выбрать?", [], session)

    assert result.reply == MOCK_REPLY
    assert result.error is False


@pytest.mark.asyncio
async def test_invoke_openai_error_returns_fallback(
    store: SessionStore,
    retriever: KnowledgeRetriever,
    session: Session,
) -> None:
    service = create_agent_service(
        FailingChatModel(responses=[MOCK_REPLY]),
        store=store,
        retriever=retriever,
        settings=get_settings(),
    )
    result = await service.invoke("Привет", [], session)

    assert result.reply == FALLBACK_MESSAGE
    assert result.error is True


@pytest.mark.asyncio
async def test_stream_sse_emits_reasoning_token_done(
    agent_service: AgentService,
    session: Session,
) -> None:
    events = [event async for event in agent_service.stream_sse("Привет", [], session)]

    event_types = [event_type for event_type, _ in events]
    assert "reasoning" in event_types
    assert "token" in event_types
    assert event_types[-1] == "done"

    _, done_data = events[-1]
    assert done_data["session_id"] == str(session.session_id)
    assert done_data["reply"] == MOCK_REPLY
    assert done_data["error"] is False


@pytest.mark.asyncio
async def test_stream_sse_openai_error_emits_error_and_done(
    store: SessionStore,
    retriever: KnowledgeRetriever,
    session: Session,
) -> None:
    service = create_agent_service(
        FailingChatModel(responses=[MOCK_REPLY]),
        store=store,
        retriever=retriever,
        settings=get_settings(),
    )
    events = [event async for event in service.stream_sse("Привет", [], session)]

    event_types = [event_type for event_type, _ in events]
    assert "error" in event_types
    assert event_types[-1] == "done"

    _, done_data = events[-1]
    assert done_data["reply"] == FALLBACK_MESSAGE
    assert done_data["error"] is True


def test_session_messages_to_langchain_maps_roles() -> None:
    now = datetime.now(UTC)
    messages = [
        Message(role=MessageRole.USER, content="Hi", timestamp=now),
        Message(role=MessageRole.ASSISTANT, content="Hello", timestamp=now),
    ]

    lc_messages = session_messages_to_langchain(messages)

    assert len(lc_messages) == 2
    assert lc_messages[0].content == "Hi"
    assert lc_messages[1].content == "Hello"
