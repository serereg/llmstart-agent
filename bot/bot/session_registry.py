"""In-memory mapping of Telegram chat_id to backend session_id."""

_chat_sessions: dict[int, str] = {}


def get_session_id(chat_id: int) -> str | None:
    """Return stored session_id for a Telegram chat, if any."""
    return _chat_sessions.get(chat_id)


def set_session_id(chat_id: int, session_id: str) -> None:
    """Bind a Telegram chat to a backend session."""
    _chat_sessions[chat_id] = session_id


def clear_sessions() -> None:
    """Clear all bindings — for tests only."""
    _chat_sessions.clear()
