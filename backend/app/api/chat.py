"""Chat API — POST /api/v1/chat with SSE (web) and JSON (telegram) responses."""

import re
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.api.schemas.chat import ChatRequest, ChatResponse
from app.api.sse import stream_sse_events
from app.sessions.models import Channel, Message, MessageRole, Session
from app.sessions.store import SessionStore, get_session_store

router = APIRouter(tags=["chat"])

STUB_REPLY = "Stub response from LLMStart Agent."
HANDOFF_PATTERN = re.compile(
    r"^/start session_([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$",
    re.IGNORECASE,
)


def parse_handoff_session_id(message: str) -> UUID | None:
    """Extract session UUID from Telegram handoff message `/start session_{uuid}`."""
    match = HANDOFF_PATTERN.match(message.strip())
    if match is None:
        return None
    return UUID(match.group(1))


async def resolve_session(
    store: SessionStore,
    body: ChatRequest,
) -> tuple[Session, bool]:
    """Resolve or create session. Returns (session, is_handoff)."""
    handoff_id = parse_handoff_session_id(body.message) if body.channel == "telegram" else None

    if handoff_id is not None:
        session = await store.get(handoff_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
        updated = await store.update(handoff_id, channel=Channel.TELEGRAM)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
        return updated, True

    if body.session_id is not None:
        session = await store.get(body.session_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
        return session, False

    channel = Channel.WEB if body.channel == "web" else Channel.TELEGRAM
    session = await store.create(channel)
    return session, False


async def persist_exchange(
    store: SessionStore,
    session: Session,
    user_message: str,
    *,
    skip_user_message: bool,
) -> Session:
    """Save user and assistant stub messages to session history."""
    session_id = session.session_id
    now = datetime.now(UTC)

    if not skip_user_message:
        updated = await store.add_message(
            session_id,
            Message(role=MessageRole.USER, content=user_message, timestamp=now),
        )
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
        session = updated

    updated = await store.add_message(
        session_id,
        Message(
            role=MessageRole.ASSISTANT,
            content=STUB_REPLY,
            timestamp=datetime.now(UTC),
        ),
    )
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return updated


async def stub_done_events(
    session_id: UUID,
    reply: str,
) -> AsyncIterator[tuple[str, dict[str, object]]]:
    """Yield stub SSE events — only `done` until ReAct agent is wired in task 06."""
    yield (
        "done",
        {
            "session_id": str(session_id),
            "reply": reply,
            "error": False,
        },
    )


@router.post("/chat", response_model=None)
async def chat(
    body: ChatRequest,
    request: Request,
    store: Annotated[SessionStore, Depends(get_session_store)],
) -> ChatResponse | StreamingResponse:
    """Handle chat message: SSE stream for web, JSON for telegram."""
    session, is_handoff = await resolve_session(store, body)
    session = await persist_exchange(
        store,
        session,
        body.message,
        skip_user_message=is_handoff,
    )

    if body.channel == "telegram":
        return ChatResponse(session_id=session.session_id, reply=STUB_REPLY)

    async def sse_with_disconnect() -> AsyncIterator[str]:
        if await request.is_disconnected():
            return
        async for chunk in stream_sse_events(stub_done_events(session.session_id, STUB_REPLY)):
            if await request.is_disconnected():
                break
            yield chunk

    return StreamingResponse(
        sse_with_disconnect(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
