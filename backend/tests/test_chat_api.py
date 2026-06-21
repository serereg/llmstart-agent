"""Integration tests for POST /api/v1/chat."""

import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.sessions.models import Channel, Message, MessageRole
from app.sessions.store import SessionStore, get_session_store

VALID_AUTH_HEADER = {"Authorization": "Bearer test-backend-key"}
CHAT_URL = "/api/v1/chat"


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


def parse_sse_events(content: str) -> list[tuple[str, dict[str, object]]]:
    """Parse SSE response body into (event_type, data) pairs."""
    events: list[tuple[str, dict[str, object]]] = []
    for block in content.strip().split("\n\n"):
        if not block.strip():
            continue
        lines = block.split("\n")
        event_type = lines[0].removeprefix("event: ")
        data = json.loads(lines[1].removeprefix("data: "))
        events.append((event_type, data))
    return events


def test_web_channel_returns_sse_done_event(client_with_store: TestClient) -> None:
    response = client_with_store.post(
        CHAT_URL,
        headers=VALID_AUTH_HEADER,
        json={"session_id": None, "message": "Hello from web", "channel": "web"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    events = parse_sse_events(response.text)
    assert len(events) >= 1
    event_type, data = events[-1]
    assert event_type == "done"
    assert "session_id" in data
    assert data["reply"] == "Stub response from LLMStart Agent."
    assert data["error"] is False


def test_telegram_channel_returns_json(client_with_store: TestClient) -> None:
    response = client_with_store.post(
        CHAT_URL,
        headers=VALID_AUTH_HEADER,
        json={"session_id": None, "message": "Hello from telegram", "channel": "telegram"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    body = response.json()
    assert "session_id" in body
    assert body["reply"] == "Stub response from LLMStart Agent."
    assert body.get("error", False) is False


@pytest.mark.asyncio
async def test_null_session_id_creates_new_session(
    store: SessionStore,
    client_with_store: TestClient,
) -> None:
    response = client_with_store.post(
        CHAT_URL,
        headers=VALID_AUTH_HEADER,
        json={"session_id": None, "message": "New session", "channel": "telegram"},
    )

    assert response.status_code == 200
    session_id = response.json()["session_id"]

    session = await store.get(UUID(session_id))
    assert session is not None
    assert session.channel == Channel.TELEGRAM
    assert len(session.messages) == 2
    assert session.messages[0].role == MessageRole.USER
    assert session.messages[0].content == "New session"
    assert session.messages[1].role == MessageRole.ASSISTANT


def test_unknown_session_id_returns_404(client_with_store: TestClient) -> None:
    unknown_id = uuid4()
    response = client_with_store.post(
        CHAT_URL,
        headers=VALID_AUTH_HEADER,
        json={"session_id": str(unknown_id), "message": "Hello", "channel": "web"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Session not found"}


def test_empty_message_returns_422(client_with_store: TestClient) -> None:
    response = client_with_store.post(
        CHAT_URL,
        headers=VALID_AUTH_HEADER,
        json={"session_id": None, "message": "", "channel": "web"},
    )

    assert response.status_code == 422


def test_message_exceeds_max_length_returns_422(client_with_store: TestClient) -> None:
    response = client_with_store.post(
        CHAT_URL,
        headers=VALID_AUTH_HEADER,
        json={"session_id": None, "message": "x" * 4001, "channel": "web"},
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any("4000" in err.get("msg", "") for err in detail if isinstance(err, dict))


def test_invalid_channel_returns_422(client_with_store: TestClient) -> None:
    response = client_with_store.post(
        CHAT_URL,
        headers=VALID_AUTH_HEADER,
        json={"session_id": None, "message": "Hello", "channel": "email"},
    )

    assert response.status_code == 422


def test_chat_without_auth_returns_401(client_with_store: TestClient) -> None:
    response = client_with_store.post(
        CHAT_URL,
        json={"session_id": None, "message": "Hello", "channel": "web"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key"}


@pytest.mark.asyncio
async def test_handoff_binds_existing_session(
    store: SessionStore,
    client_with_store: TestClient,
) -> None:
    web_session = await store.create(Channel.WEB)
    await store.add_message(
        web_session.session_id,
        Message(
            role=MessageRole.USER,
            content="Widget message",
            timestamp=datetime.now(UTC),
        ),
    )

    handoff_message = f"/start session_{web_session.session_id}"
    response = client_with_store.post(
        CHAT_URL,
        headers=VALID_AUTH_HEADER,
        json={"session_id": None, "message": handoff_message, "channel": "telegram"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == str(web_session.session_id)

    session = await store.get(web_session.session_id)
    assert session is not None
    assert session.channel == Channel.TELEGRAM
    assert len(session.messages) == 2
    assert session.messages[0].content == "Widget message"
    assert session.messages[1].role == MessageRole.ASSISTANT


def test_sse_event_format(client_with_store: TestClient) -> None:
    response = client_with_store.post(
        CHAT_URL,
        headers=VALID_AUTH_HEADER,
        json={"session_id": None, "message": "SSE format check", "channel": "web"},
    )

    assert response.status_code == 200
    text = response.text
    assert text.startswith("event: done\n")
    assert "data: {" in text
    assert text.endswith("\n\n")
