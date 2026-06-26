"""Integration tests for agent with business tools."""

from collections.abc import AsyncIterator
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.agent.core import _parse_stream_event, create_agent_service
from app.config import get_settings
from app.rag.indexer import build_chroma_index
from app.rag.retriever import KnowledgeRetriever
from app.sessions.models import Channel, PaymentStatus
from app.sessions.store import SessionStore
from app.tools.context import ToolContext, set_tool_context
from tests.fakes import ToolCapableFakeChatModel
from tests.test_rag import FakeEmbeddings

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@pytest.fixture
def store() -> SessionStore:
    return SessionStore()


@pytest.fixture
def retriever() -> KnowledgeRetriever:
    return KnowledgeRetriever(build_chroma_index(FakeEmbeddings(), DATA_DIR))


@pytest.mark.asyncio
async def test_stream_sse_emits_tool_events_from_parsed_events() -> None:
    tool_start = {
        "event": "on_tool_start",
        "name": "list_b2c_products",
        "data": {"input": {}},
    }
    tool_end = {
        "event": "on_tool_end",
        "name": "list_b2c_products",
        "data": {"output": "[]"},
    }

    start_event = _parse_stream_event(tool_start)
    end_event = _parse_stream_event(tool_end)

    assert start_event is not None
    assert start_event[0] == "tool_start"
    assert start_event[1]["name"] == "list_b2c_products"

    assert end_event is not None
    assert end_event[0] == "tool_end"
    assert end_event[1]["result"] == "[]"


@pytest.mark.asyncio
async def test_agent_stream_sse_yields_tool_events_when_emitted(
    store: SessionStore,
    retriever: KnowledgeRetriever,
) -> None:
    settings = get_settings()
    service = create_agent_service(
        ToolCapableFakeChatModel(responses=["ok"]),
        store=store,
        retriever=retriever,
        settings=settings,
    )

    session = await store.create(Channel.WEB)

    async def fake_astream_events(
        *_args: object,
        **_kwargs: object,
    ) -> AsyncIterator[dict[str, object]]:
        yield {
            "event": "on_tool_start",
            "name": "save_lead",
            "data": {"input": {"name": "Test"}},
        }
        yield {
            "event": "on_tool_end",
            "name": "save_lead",
            "data": {"output": "Lead saved"},
        }
        yield {
            "event": "on_chat_model_stream",
            "data": {"chunk": MagicMock(content="Done")},
        }

    service._agent.astream_events = fake_astream_events  # noqa: SLF001

    events = [event async for event in service.stream_sse("hi", [], session)]
    event_types = [event_type for event_type, _ in events]

    assert "tool_start" in event_types
    assert "tool_end" in event_types


@pytest.mark.asyncio
async def test_tools_update_session_via_context(
    store: SessionStore,
    retriever: KnowledgeRetriever,
    tmp_path: Path,
) -> None:
    """Forced tool calls via direct context — session payment and segment updated."""
    session = await store.create(Channel.WEB)
    leads_file = tmp_path / "leads.txt"

    set_tool_context(
        ToolContext(
            session_id=session.session_id,
            channel="web",
            store=store,
            retriever=retriever,
            leads_file_path=str(leads_file),
            products_file_path=str(DATA_DIR / "b2c" / "products.json"),
        ),
    )

    from app.tools.leads import save_lead  # noqa: PLC0415
    from app.tools.payments import confirm_payment, create_payment_link  # noqa: PLC0415

    await create_payment_link.ainvoke({"product_id": "agents"})
    updated = await store.get(session.session_id)
    assert updated is not None
    assert updated.payment.status == PaymentStatus.PENDING

    await confirm_payment.ainvoke({})
    updated = await store.get(session.session_id)
    assert updated is not None
    assert updated.payment.status == PaymentStatus.PAID

    await save_lead.ainvoke(
        {
            "name": "Анна",
            "contact": "anna@test.ru",
            "product": "agents",
            "segment": "b2c",
        },
    )
    assert "anna@test.ru" in leads_file.read_text(encoding="utf-8")
