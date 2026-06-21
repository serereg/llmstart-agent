"""Tests for in-memory session store and GET /api/v1/sessions/{session_id}."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.sessions.models import Channel, Message, MessageRole
from app.sessions.store import SessionStore, get_session_store

VALID_AUTH_HEADER = {"Authorization": "Bearer test-backend-key"}


@pytest.fixture
def store() -> SessionStore:
    return SessionStore()


@pytest.fixture
def client_with_store(store: SessionStore) -> TestClient:
    from app.main import create_app  # noqa: PLC0415

    app = create_app()
    app.dependency_overrides[get_session_store] = lambda: store
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_and_get_session(store: SessionStore) -> None:
    session = await store.create(Channel.WEB)

    loaded = await store.get(session.session_id)

    assert loaded is not None
    assert loaded.session_id == session.session_id
    assert loaded.channel == Channel.WEB
    assert loaded.segment is None
    assert loaded.messages == []
    assert loaded.payment.status.value == "none"
    assert loaded.payment.mock_link is None
    assert loaded.created_at == session.created_at
    assert loaded.updated_at == session.updated_at


@pytest.mark.asyncio
async def test_add_message_updates_updated_at(store: SessionStore) -> None:
    session = await store.create(Channel.TELEGRAM)
    message_time = datetime.now(UTC)
    message = Message(
        role=MessageRole.USER,
        content="Hello",
        timestamp=message_time,
    )

    updated = await store.add_message(session.session_id, message)

    assert updated is not None
    assert len(updated.messages) == 1
    assert updated.messages[0].content == "Hello"
    assert updated.updated_at >= session.updated_at
    assert updated.updated_at >= message_time


def test_get_unknown_session_returns_404(client_with_store: TestClient) -> None:
    unknown_id = uuid4()
    response = client_with_store.get(
        f"/api/v1/sessions/{unknown_id}",
        headers=VALID_AUTH_HEADER,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Session not found"}


@pytest.mark.asyncio
async def test_get_existing_session_returns_full_schema(
    store: SessionStore,
    client_with_store: TestClient,
) -> None:
    session = await store.create(Channel.WEB, session_id=uuid4())
    message_time = datetime(2026, 6, 21, 10, 0, 0, tzinfo=UTC)
    await store.add_message(
        session.session_id,
        Message(
            role=MessageRole.USER,
            content="Хочу научиться делать AI-агентов",
            timestamp=message_time,
        ),
    )
    await store.add_message(
        session.session_id,
        Message(
            role=MessageRole.ASSISTANT,
            content="Рекомендую курс agents...",
            timestamp=message_time + timedelta(seconds=5),
        ),
    )
    await store.update(session.session_id, segment="b2c")

    response = client_with_store.get(
        f"/api/v1/sessions/{session.session_id}",
        headers=VALID_AUTH_HEADER,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == str(session.session_id)
    assert body["channel"] == "web"
    assert body["segment"] == "b2c"
    assert len(body["messages"]) == 2
    assert body["messages"][0]["role"] == "user"
    assert body["messages"][0]["content"] == "Хочу научиться делать AI-агентов"
    assert body["messages"][1]["role"] == "assistant"
    assert body["payment"]["status"] == "none"
    assert body["payment"]["mock_link"] is None
    assert body["created_at"] is not None
    assert body["updated_at"] is not None


def test_get_session_without_auth_returns_401(client_with_store: TestClient) -> None:
    response = client_with_store.get(f"/api/v1/sessions/{uuid4()}")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key"}
