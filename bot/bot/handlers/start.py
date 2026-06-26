"""Handler for /start command — greeting and widget handoff."""

import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.filters.command import CommandObject
from aiogram.types import Message

from bot.backend_client import BackendClient
from bot.handlers.start_parser import build_handoff_message, parse_handoff_session_id
from bot.reply import send_agent_reply

logger = logging.getLogger(__name__)

router = Router(name="start")

GREETING = (
    "Привет! Я LLMStart Agent — AI-консультант образовательной платформы llmstart.ru.\n\n"
    "Расскажите, чем могу помочь: подбор курса, корпоративное обучение или вопросы о продуктах."
)


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    command: CommandObject,
    backend_client: BackendClient,
) -> None:
    """Handle /start — plain greeting or widget handoff via deep link."""
    if message.from_user is None:
        return

    handoff_id = parse_handoff_session_id(command.args)
    if handoff_id is None:
        await message.answer(GREETING)
        return

    handoff_message = build_handoff_message(handoff_id)
    logger.info(
        "Widget handoff",
        extra={"chat_id": message.chat.id, "session_id": str(handoff_id)},
    )

    result = await backend_client.chat(handoff_message, session_id=None)
    await send_agent_reply(message, result)
