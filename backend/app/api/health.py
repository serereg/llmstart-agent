"""Health check endpoint with dependency probes."""

import asyncio
import logging
from typing import Annotated, Literal

import httpx
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

ProbeStatus = Literal["ok", "error"]
HealthStatus = Literal["ok", "degraded"]

HEALTH_PROBE_TIMEOUT_SEC = 5.0
OPENAI_MODELS_URL = "https://api.openai.com/v1/models"
DIAL_MODELS_PATH = "/openai/models"
LANGFUSE_HEALTH_PATH = "/api/public/health"


class DependenciesStatus(BaseModel):
    openai: ProbeStatus
    langfuse: ProbeStatus


class HealthResponse(BaseModel):
    status: HealthStatus
    version: str
    dependencies: DependenciesStatus


def _openai_models_probe(settings: Settings) -> tuple[str, dict[str, str]]:
    if settings.openai_api_base:
        url = f"{settings.openai_api_base.rstrip('/')}{DIAL_MODELS_PATH}"
        headers = {"api-key": settings.openai_api_key}
        return url, headers
    return OPENAI_MODELS_URL, {"Authorization": f"Bearer {settings.openai_api_key}"}


async def probe_openai(settings: Settings) -> ProbeStatus:
    """Lightweight OpenAI check via models list (no token usage)."""
    url, headers = _openai_models_probe(settings)
    try:
        async with httpx.AsyncClient(timeout=HEALTH_PROBE_TIMEOUT_SEC) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == httpx.codes.OK:
                return "ok"
    except httpx.HTTPError:
        logger.exception("OpenAI health probe failed")
    return "error"


async def probe_langfuse(settings: Settings) -> ProbeStatus:
    """Check Langfuse web container health endpoint."""
    url = f"{settings.langfuse_host.rstrip('/')}{LANGFUSE_HEALTH_PATH}"
    try:
        async with httpx.AsyncClient(timeout=HEALTH_PROBE_TIMEOUT_SEC) as client:
            response = await client.get(url)
            if response.status_code == httpx.codes.OK:
                return "ok"
    except httpx.HTTPError:
        logger.exception("Langfuse health probe failed")
    return "error"


@router.get("/health")
async def health(
    settings: Annotated[Settings, Depends(get_settings)],
) -> JSONResponse:
    """Return service health and critical dependency status."""
    openai_result, langfuse_result = await asyncio.gather(
        probe_openai(settings),
        probe_langfuse(settings),
    )

    dependencies = DependenciesStatus(openai=openai_result, langfuse=langfuse_result)
    all_ok = openai_result == "ok" and langfuse_result == "ok"
    body = HealthResponse(
        status="ok" if all_ok else "degraded",
        version=settings.app_version,
        dependencies=dependencies,
    )
    status_code = 200 if all_ok else 503
    return JSONResponse(content=body.model_dump(), status_code=status_code)
