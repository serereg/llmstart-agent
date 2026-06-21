"""Pydantic schemas for chat API."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

MAX_MESSAGE_LENGTH = 4000


class ChatRequest(BaseModel):
    session_id: UUID | None = None
    message: str = Field(..., min_length=1)
    channel: Literal["web", "telegram"]

    @field_validator("message")
    @classmethod
    def validate_message_length(cls, value: str) -> str:
        if len(value) > MAX_MESSAGE_LENGTH:
            msg = f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters"
            raise ValueError(msg)
        return value


class ChatResponse(BaseModel):
    session_id: UUID
    reply: str
    error: bool = False
