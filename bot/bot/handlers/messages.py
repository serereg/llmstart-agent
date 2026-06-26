"""Handler for plain text messages."""

import logging

from aiogram import F, Router
from aiogram.types import Message

from bot.backend_client import BackendClient
from bot.reply import send_agent_reply
from bot.session_registry import get_session_id

logger = logging.getLogger(__name__)

router = Router(name="messages")


@router.message(F.text)
async def handle_text_message(
    message: Message,
    backend_client: BackendClient,
) -> None:
    """Forward user text to backend and reply with agent response."""
    if message.text is None:
        return

    session_id = get_session_id(message.chat.id)
    logger.info(
        "Incoming message",
        extra={"chat_id": message.chat.id, "session_id": session_id},
    )

    result = await backend_client.chat(message.text, session_id=session_id)
    await send_agent_reply(message, result)
