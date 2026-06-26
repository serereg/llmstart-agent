"""HTTP client for backend chat API."""

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from bot.config import Settings

logger = logging.getLogger(__name__)

NETWORK_ERROR_MESSAGE = "Сервис временно недоступен, попробуйте позже"
HTTP_ERROR_MESSAGE = "Не удалось получить ответ от сервера, попробуйте позже"


@dataclass(frozen=True, slots=True)
class ChatResult:
    """Result of a chat API call."""

    session_id: str | None
    reply: str
    error: bool = False
    network_error: bool = False


class BackendClient:
    """Async client for POST /api/v1/chat with channel=telegram."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._headers = {
            "Authorization": f"Bearer {settings.backend_api_key}",
            "Content-Type": "application/json",
        }

    async def chat(
        self,
        message: str,
        *,
        session_id: str | None = None,
        channel: str = "telegram",
    ) -> ChatResult:
        """Send a message to the backend and return the agent reply."""
        payload: dict[str, Any] = {
            "message": message,
            "channel": channel,
        }
        if session_id is not None:
            payload["session_id"] = session_id

        try:
            async with httpx.AsyncClient(timeout=self._settings.backend_timeout_sec) as client:
                response = await client.post(
                    self._settings.chat_api_url,
                    headers=self._headers,
                    json=payload,
                )
        except httpx.RequestError:
            logger.exception(
                "Backend request failed",
                extra={"chat_api_url": self._settings.chat_api_url},
            )
            return ChatResult(
                session_id=session_id,
                reply=NETWORK_ERROR_MESSAGE,
                error=True,
                network_error=True,
            )

        if response.status_code != httpx.codes.OK:
            logger.error(
                "Backend returned non-200 status",
                extra={"status_code": response.status_code},
            )
            return ChatResult(
                session_id=session_id,
                reply=HTTP_ERROR_MESSAGE,
                error=True,
            )

        body = response.json()
        return ChatResult(
            session_id=str(body["session_id"]),
            reply=str(body["reply"]),
            error=bool(body.get("error", False)),
        )
