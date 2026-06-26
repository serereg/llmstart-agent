"""Telegram bot handlers."""

from bot.handlers.messages import router as messages_router
from bot.handlers.start import router as start_router

__all__ = ["messages_router", "start_router"]
