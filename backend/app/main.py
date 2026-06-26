from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import get_settings
from app.observability.langfuse import get_langfuse_client, shutdown_langfuse_client
from app.rag.store import init_rag_index


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    get_langfuse_client()
    init_rag_index(settings)
    yield
    shutdown_langfuse_client()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="LLMStart Agent Core",
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    return app


app = create_app()
