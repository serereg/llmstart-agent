"""Shared helpers for sending agent replies."""

import logging

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from bot.backend_client import ChatResult
from bot.html_formatter import markdown_to_telegram_html
from bot.session_registry import set_session_id

logger = logging.getLogger(__name__)


async def send_agent_reply(
    message: Message,
    result: ChatResult,
) -> None:
    """Send backend reply as HTML with plain-text fallback."""
    if result.session_id is not None:
        set_session_id(message.chat.id, result.session_id)

    html_reply = markdown_to_telegram_html(result.reply)
    try:
        await message.answer(html_reply, parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        logger.warning(
            "Telegram HTML parse failed, falling back to plain text",
            extra={"chat_id": message.chat.id, "session_id": result.session_id},
        )
        await message.answer(result.reply)
