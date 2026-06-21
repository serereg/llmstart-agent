"""Unit tests for the ReAct agent service."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from app.agent.core import (
    FALLBACK_MESSAGE,
    AgentService,
    create_agent_service,
    session_messages_to_langchain,
)
from app.sessions.models import Message, MessageRole
from tests.fakes import FailingChatModel

MOCK_REPLY = "Рекомендую курс agents для старта."


@pytest.fixture
def agent_service() -> AgentService:
    llm = FakeListChatModel(responses=[MOCK_REPLY])
    return create_agent_service(llm)


@pytest.mark.asyncio
async def test_invoke_returns_mock_reply(agent_service: AgentService) -> None:
    result = await agent_service.invoke("Какой курс выбрать?", [])

    assert result.reply == MOCK_REPLY
    assert result.error is False


@pytest.mark.asyncio
async def test_invoke_openai_error_returns_fallback() -> None:
    service = create_agent_service(FailingChatModel(responses=[MOCK_REPLY]))
    result = await service.invoke("Привет", [])

    assert result.reply == FALLBACK_MESSAGE
    assert result.error is True


@pytest.mark.asyncio
async def test_stream_sse_emits_reasoning_token_done(agent_service: AgentService) -> None:
    session_id = uuid4()
    events = [event async for event in agent_service.stream_sse("Привет", [], session_id)]

    event_types = [event_type for event_type, _ in events]
    assert "reasoning" in event_types
    assert "token" in event_types
    assert event_types[-1] == "done"

    _, done_data = events[-1]
    assert done_data["session_id"] == str(session_id)
    assert done_data["reply"] == MOCK_REPLY
    assert done_data["error"] is False


@pytest.mark.asyncio
async def test_stream_sse_openai_error_emits_error_and_done() -> None:
    service = create_agent_service(FailingChatModel(responses=[MOCK_REPLY]))
    session_id = uuid4()
    events = [event async for event in service.stream_sse("Привет", [], session_id)]

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
