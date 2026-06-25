"""Application configuration loaded from environment variables."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_VERSION = "0.1.0"
REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = REPO_ROOT / ".env"

if not os.environ.get("PYTEST_CURRENT_TEST"):
    load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    """Backend settings — fail fast when required env vars are missing."""

    model_config = SettingsConfigDict(
        extra="ignore",
        populate_by_name=True,
    )

    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    langfuse_public_key: str = Field(alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str = Field(alias="LANGFUSE_SECRET_KEY")
    backend_api_key: str = Field(alias="BACKEND_API_KEY")

    openai_api_base: str | None = Field(default=None, alias="OPENAI_API_BASE")
    openai_api_version: str = Field(default="2024-02-01", alias="OPENAI_API_VERSION")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        alias="OPENAI_EMBEDDING_MODEL",
    )
    openai_timeout_sec: int = Field(default=60, alias="OPENAI_TIMEOUT_SEC")
    langfuse_host: str = Field(default="http://localhost:3001", alias="LANGFUSE_HOST")
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        alias="LOG_LEVEL",
    )
    app_version: str = APP_VERSION

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


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
