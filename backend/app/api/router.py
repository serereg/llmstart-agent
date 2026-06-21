from fastapi import APIRouter, Depends

from app.api.chat import router as chat_router
from app.api.deps import verify_api_key
from app.api.health import router as health_router
from app.api.sessions import router as sessions_router

api_router = APIRouter()
api_router.include_router(health_router)

v1_router = APIRouter(
    prefix="/api/v1",
    dependencies=[Depends(verify_api_key)],
    tags=["v1"],
)


@v1_router.get("/ping")
async def ping() -> dict[str, str]:
    """Stub protected endpoint for auth integration tests."""
    return {"status": "ok"}


v1_router.include_router(sessions_router)
v1_router.include_router(chat_router)

api_router.include_router(v1_router)
