
import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings


def test_get_settings_returns_configured_values() -> None:
    settings = get_settings()
    assert settings.openai_api_key == "test-openai-key"
    assert settings.langfuse_public_key == "pk-test"
    assert settings.langfuse_secret_key == "sk-test"  # noqa: S105
    assert settings.backend_api_key == "test-backend-key"
    assert settings.openai_model == "gpt-4o"
    assert settings.langfuse_host == "http://localhost:3001"
    assert settings.app_version == "0.1.0"


def test_missing_openai_api_key_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()
    with pytest.raises(ValidationError):
        Settings()


def test_get_settings_missing_openai_api_key_raises_runtime_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        get_settings()


def test_cors_origins_list_parses_comma_separated_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000, http://localhost:3001")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.cors_origins_list == [
        "http://localhost:3000",
        "http://localhost:3001",
    ]


def test_create_app_fails_without_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ("OPENAI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "BACKEND_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    get_settings.cache_clear()
    with pytest.raises(RuntimeError, match="Missing required environment variables"):
        get_settings()
