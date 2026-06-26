"""Smoke tests for bot module imports and config."""

import pytest

from bot import __version__
from bot.config import get_settings


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("BACKEND_API_KEY", "test-key")
    monkeypatch.setenv("BACKEND_URL", "http://localhost:8000")
    get_settings.cache_clear()

    settings = get_settings()
    assert settings.telegram_bot_token == "test-token"
    assert settings.backend_api_key == "test-key"
    assert settings.chat_api_url == "http://localhost:8000/api/v1/chat"

    get_settings.cache_clear()


def test_settings_fail_fast_on_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("BACKEND_API_KEY", raising=False)
    get_settings.cache_clear()

    with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN"):
        get_settings()

    get_settings.cache_clear()
