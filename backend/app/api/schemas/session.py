"""Pydantic schemas for session API responses."""

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from app.sessions.models import Session


class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: datetime


class PaymentResponse(BaseModel):
    status: str
    mock_link: str | None


class SessionResponse(BaseModel):
    session_id: UUID
    channel: str
    segment: str | None
    messages: list[MessageResponse]
    payment: PaymentResponse
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_session(cls, session: Session) -> Self:
        return cls(
            session_id=session.session_id,
            channel=session.channel.value,
            segment=session.segment,
            messages=[
                MessageResponse(
                    role=message.role.value,
                    content=message.content,
                    timestamp=message.timestamp,
                )
                for message in session.messages
            ],
            payment=PaymentResponse(
                status=session.payment.status.value,
                mock_link=session.payment.mock_link,
            ),
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
