"""Tests for backend HTTP client."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from bot.backend_client import NETWORK_ERROR_MESSAGE, BackendClient
from bot.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        TELEGRAM_BOT_TOKEN="test-token",
        BACKEND_URL="http://localhost:8000",
        BACKEND_API_KEY="test-api-key",
    )


@pytest.fixture
def client(settings: Settings) -> BackendClient:
    return BackendClient(settings)


@pytest.mark.asyncio
async def test_chat_success(client: BackendClient) -> None:
    mock_response = httpx.Response(
        200,
        json={
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "reply": "Привет!",
            "error": False,
        },
        request=httpx.Request("POST", "http://localhost:8000/api/v1/chat"),
    )

    with patch("bot.backend_client.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await client.chat("Привет", session_id=None)

    assert result.session_id == "550e8400-e29b-41d4-a716-446655440000"
    assert result.reply == "Привет!"
    assert result.error is False
    assert result.network_error is False

    mock_client.post.assert_awaited_once()
    call_kwargs = mock_client.post.await_args.kwargs
    assert call_kwargs["json"] == {
        "message": "Привет",
        "channel": "telegram",
    }


@pytest.mark.asyncio
async def test_chat_with_existing_session(client: BackendClient) -> None:
    session_id = "550e8400-e29b-41d4-a716-446655440000"
    mock_response = httpx.Response(
        200,
        json={"session_id": session_id, "reply": "Ответ", "error": False},
        request=httpx.Request("POST", "http://localhost:8000/api/v1/chat"),
    )

    with patch("bot.backend_client.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await client.chat("Вопрос", session_id=session_id)

    assert result.session_id == session_id
    call_kwargs = mock_client.post.await_args.kwargs
    assert call_kwargs["json"]["session_id"] == session_id


@pytest.mark.asyncio
async def test_chat_network_error(client: BackendClient) -> None:
    with patch("bot.backend_client.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post.side_effect = httpx.ConnectError("connection refused")
        mock_client_cls.return_value = mock_client

        result = await client.chat("Привет")

    assert result.reply == NETWORK_ERROR_MESSAGE
    assert result.error is True
    assert result.network_error is True


@pytest.mark.asyncio
async def test_chat_http_error(client: BackendClient) -> None:
    mock_response = httpx.Response(
        500,
        json={"detail": "Internal error"},
        request=httpx.Request("POST", "http://localhost:8000/api/v1/chat"),
    )

    with patch("bot.backend_client.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await client.chat("Привет")

    assert result.error is True
    assert result.network_error is False


@pytest.mark.asyncio
async def test_chat_backend_error_flag(client: BackendClient) -> None:
    mock_response = httpx.Response(
        200,
        json={
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "reply": "Сервис временно недоступен, попробуйте позже",
            "error": True,
        },
        request=httpx.Request("POST", "http://localhost:8000/api/v1/chat"),
    )

    with patch("bot.backend_client.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await client.chat("Привет")

    assert result.error is True
