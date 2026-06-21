"""In-memory session store with asyncio-based concurrency control."""

import asyncio
from datetime import UTC, datetime
from functools import lru_cache
from typing import TypedDict, Unpack
from uuid import UUID, uuid4

from app.sessions.models import Channel, Message, PaymentState, Session


class SessionUpdate(TypedDict, total=False):
    segment: str | None
    payment: PaymentState
    channel: Channel


class SessionStore:
    """Thread-safe in-memory store for chat sessions."""

    def __init__(self) -> None:
        self._sessions: dict[UUID, Session] = {}
        self._lock = asyncio.Lock()

    async def create(
        self,
        channel: Channel,
        *,
        session_id: UUID | None = None,
    ) -> Session:
        async with self._lock:
            sid = session_id or uuid4()
            now = datetime.now(UTC)
            session = Session(
                session_id=sid,
                channel=channel,
                created_at=now,
                updated_at=now,
            )
            self._sessions[sid] = session
            return session.model_copy()

    async def get(self, session_id: UUID) -> Session | None:
        async with self._lock:
            session = self._sessions.get(session_id)
            return session.model_copy() if session is not None else None

    async def update(self, session_id: UUID, **fields: Unpack[SessionUpdate]) -> Session | None:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None
            updated = session.model_copy(update={**fields, "updated_at": datetime.now(UTC)})
            self._sessions[session_id] = updated
            return updated.model_copy()

    async def add_message(self, session_id: UUID, message: Message) -> Session | None:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None
            now = datetime.now(UTC)
            updated = session.model_copy(
                update={
                    "messages": [*session.messages, message],
                    "updated_at": now,
                },
            )
            self._sessions[session_id] = updated
            return updated.model_copy()


@lru_cache
def get_session_store() -> SessionStore:
    """Return the process-wide session store singleton."""
    return SessionStore()
