"""Unit tests for business tools."""

import asyncio
import json
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest

from app.rag.indexer import build_chroma_index
from app.rag.retriever import KnowledgeRetriever
from app.sessions.models import Channel, PaymentStatus
from app.sessions.store import SessionStore
from app.tools.context import ToolContext, clear_tool_context, set_tool_context
from app.tools.knowledge import search_knowledge_base
from app.tools.leads import save_lead
from app.tools.payments import confirm_payment, create_payment_link
from app.tools.products import list_b2c_products
from tests.test_rag import FakeEmbeddings

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@pytest.fixture
def store() -> SessionStore:
    return SessionStore()


@pytest.fixture
def retriever() -> KnowledgeRetriever:
    vectorstore = build_chroma_index(FakeEmbeddings(), DATA_DIR)
    return KnowledgeRetriever(vectorstore)


@pytest.fixture
def leads_file(tmp_path: Path) -> Path:
    return tmp_path / "leads.txt"


@pytest.fixture
async def tool_context(
    store: SessionStore,
    retriever: KnowledgeRetriever,
    leads_file: Path,
) -> AsyncGenerator[ToolContext, None]:
    session = await store.create(Channel.WEB)
    ctx = ToolContext(
        session_id=session.session_id,
        channel="web",
        store=store,
        retriever=retriever,
        leads_file_path=str(leads_file),
        products_file_path=str(DATA_DIR / "b2c" / "products.json"),
    )
    set_tool_context(ctx)
    yield ctx
    clear_tool_context()


@pytest.mark.asyncio
async def test_list_b2c_products_returns_catalog(tool_context: ToolContext) -> None:
    result = await list_b2c_products.ainvoke({})
    products = json.loads(result)

    assert len(products) >= 3
    assert any(product["id"] == "agents" for product in products)


@pytest.mark.asyncio
async def test_search_knowledge_base_filters_by_audience(
    store: SessionStore,
    tool_context: ToolContext,
    retriever: KnowledgeRetriever,
) -> None:
    query = "курс Agents LangChain ReAct"
    result = await search_knowledge_base.ainvoke(
        {"query": query, "audience": "b2c"},
    )

    docs = retriever.search(query, "b2c")
    assert len(docs) >= 1
    assert all(doc.metadata["audience"] == "b2c" for doc in docs)
    assert result.strip()

    session = await store.get(tool_context.session_id)
    assert session is not None
    assert session.segment == "b2c"


@pytest.mark.asyncio
async def test_create_payment_link_sets_pending(
    store: SessionStore,
    tool_context: ToolContext,
) -> None:
    result = await create_payment_link.ainvoke({"product_id": "agents"})
    payload = json.loads(result)

    assert payload["status"] == "pending"
    assert "mock_link" in payload

    session = await store.get(tool_context.session_id)
    assert session is not None
    assert session.payment.status == PaymentStatus.PENDING
    assert session.payment.mock_link is not None


@pytest.mark.asyncio
async def test_confirm_payment_pending_to_paid(
    store: SessionStore,
    tool_context: ToolContext,
) -> None:
    await create_payment_link.ainvoke({"product_id": "agents"})
    result = await confirm_payment.ainvoke({})
    payload = json.loads(result)

    assert payload["status"] == "paid"

    session = await store.get(tool_context.session_id)
    assert session is not None
    assert session.payment.status == PaymentStatus.PAID


@pytest.mark.asyncio
async def test_confirm_payment_without_pending_returns_error(tool_context: ToolContext) -> None:
    result = await confirm_payment.ainvoke({})
    payload = json.loads(result)

    assert "error" in payload


@pytest.mark.asyncio
async def test_save_lead_appends_to_file(
    store: SessionStore,
    tool_context: ToolContext,
    leads_file: Path,
) -> None:
    result = await save_lead.ainvoke(
        {
            "name": "Иван",
            "contact": "ivan@example.com",
            "product": "agents",
            "segment": "b2c",
        },
    )

    assert "Lead saved" in result
    content = await asyncio.to_thread(leads_file.read_text, encoding="utf-8")
    assert "ivan@example.com" in content
    assert "b2c" in content

    session = await store.get(tool_context.session_id)
    assert session is not None
    assert session.segment == "b2c"


@pytest.mark.asyncio
async def test_create_payment_link_unknown_product(tool_context: ToolContext) -> None:
    result = await create_payment_link.ainvoke({"product_id": "nonexistent"})
    payload = json.loads(result)
    assert "error" in payload
