"""Bot configuration loaded from environment variables."""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from bot import __version__

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = REPO_ROOT / ".env"

if not os.environ.get("PYTEST_CURRENT_TEST"):
    load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    """Bot settings — fail fast when required env vars are missing."""

    model_config = SettingsConfigDict(
        extra="ignore",
        populate_by_name=True,
    )

    telegram_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")
    backend_url: str = Field(default="http://localhost:8000", alias="BACKEND_URL")
    backend_api_key: str = Field(alias="BACKEND_API_KEY")
    backend_timeout_sec: int = Field(default=60, alias="BACKEND_TIMEOUT_SEC")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    app_version: str = __version__

    @property
    def chat_api_url(self) -> str:
        return f"{self.backend_url.rstrip('/')}/api/v1/chat"


def _format_settings_error(exc: ValidationError) -> str:
    missing_vars: list[str] = []
    for error in exc.errors():
        if error["type"] != "missing":
            continue
        field_name = str(error["loc"][0])
        field = Settings.model_fields.get(field_name)
        if field is not None and field.validation_alias is not None:
            alias = field.validation_alias
            env_name = alias if isinstance(alias, str) else str(alias)
        else:
            env_name = field_name.upper()
        missing_vars.append(env_name)
    if missing_vars:
        return f"Missing required environment variables: {', '.join(sorted(missing_vars))}"
    return str(exc)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings singleton; raises on invalid/missing config."""
    try:
        return Settings()
    except ValidationError as exc:
        raise RuntimeError(_format_settings_error(exc)) from exc
