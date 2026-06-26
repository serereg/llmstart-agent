"""Chat API — POST /api/v1/chat with SSE (web) and JSON (telegram) responses."""

import re
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.agent.core import AgentService, get_agent_service
from app.agent.prompts import HANDOFF_USER_MESSAGE
from app.api.schemas.chat import ChatRequest, ChatResponse
from app.api.sse import stream_sse_events
from app.sessions.models import Channel, Message, MessageRole, Session
from app.sessions.store import SessionStore, get_session_store

router = APIRouter(tags=["chat"])

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


async def save_user_message(
    store: SessionStore,
    session_id: UUID,
    content: str,
) -> Session:
    """Persist a user message and return the updated session."""
    updated = await store.add_message(
        session_id,
        Message(role=MessageRole.USER, content=content, timestamp=datetime.now(UTC)),
    )
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return updated


async def save_assistant_message(
    store: SessionStore,
    session_id: UUID,
    content: str,
) -> Session:
    """Persist an assistant message and return the updated session."""
    updated = await store.add_message(
        session_id,
        Message(role=MessageRole.ASSISTANT, content=content, timestamp=datetime.now(UTC)),
    )
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return updated


def agent_history(session: Session, *, is_handoff: bool) -> list[Message]:
    """Return message history passed to the agent (excludes the latest user turn)."""
    if is_handoff:
        return list(session.messages)
    if not session.messages:
        return []
    return list(session.messages[:-1])


async def agent_sse_with_persist(
    agent: AgentService,
    store: SessionStore,
    session: Session,
    user_message: str,
    history: list[Message],
) -> AsyncIterator[tuple[str, dict[str, object]]]:
    """Stream agent SSE events and persist the assistant reply on completion."""
    reply = ""
    async for event_type, data in agent.stream_sse(user_message, history, session):
        if event_type == "done":
            reply = str(data["reply"])
        yield event_type, data

    if reply:
        await save_assistant_message(store, session.session_id, reply)


@router.post("/chat", response_model=None)
async def chat(
    body: ChatRequest,
    request: Request,
    store: Annotated[SessionStore, Depends(get_session_store)],
    agent: Annotated[AgentService, Depends(get_agent_service)],
) -> ChatResponse | StreamingResponse:
    """Handle chat message: SSE stream for web, JSON for telegram."""
    session, is_handoff = await resolve_session(store, body)

    if is_handoff:
        user_message = HANDOFF_USER_MESSAGE
        history = agent_history(session, is_handoff=True)
    else:
        session = await save_user_message(store, session.session_id, body.message)
        user_message = body.message
        history = agent_history(session, is_handoff=False)

    if body.channel == "telegram":
        result = await agent.invoke(user_message, history, session)
        await save_assistant_message(store, session.session_id, result.reply)
        return ChatResponse(
            session_id=session.session_id,
            reply=result.reply,
            error=result.error,
        )

    async def sse_with_disconnect() -> AsyncIterator[str]:
        if await request.is_disconnected():
            return
        async for chunk in stream_sse_events(
            agent_sse_with_persist(agent, store, session, user_message, history),
        ):
            if await request.is_disconnected():
                break
            yield chunk

    return StreamingResponse(
        sse_with_disconnect(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
