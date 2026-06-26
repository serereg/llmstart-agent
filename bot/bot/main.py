"""Telegram bot entry point — long polling."""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.backend_client import BackendClient
from bot.config import get_settings
from bot.handlers import messages_router, start_router

logger = logging.getLogger(__name__)


def configure_logging(level: str) -> None:
    """Configure stdout logging for the bot process."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        stream=sys.stdout,
    )


async def run_bot() -> None:
    """Start aiogram long polling with graceful shutdown."""
    settings = get_settings()
    configure_logging(settings.log_level)

    logger.info(
        "Starting LLMStart bot v%s (backend=%s)",
        settings.app_version,
        settings.backend_url,
    )

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher()
    backend_client = BackendClient(settings)

    dispatcher.include_router(start_router)
    dispatcher.include_router(messages_router)

    try:
        await dispatcher.start_polling(bot, backend_client=backend_client)
    finally:
        await bot.session.close()
        logger.info("Bot stopped")


def main() -> None:
    """CLI entry point."""
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
