"""Domain models for in-memory chat sessions."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class Channel(StrEnum):
    WEB = "web"
    TELEGRAM = "telegram"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class PaymentStatus(StrEnum):
    NONE = "none"
    PENDING = "pending"
    PAID = "paid"


class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime


class PaymentState(BaseModel):
    status: PaymentStatus = PaymentStatus.NONE
    mock_link: str | None = None


class Session(BaseModel):
    session_id: UUID
    channel: Channel
    segment: str | None = None
    messages: list[Message] = Field(default_factory=list)
    payment: PaymentState = Field(default_factory=PaymentState)
    created_at: datetime
    updated_at: datetime
