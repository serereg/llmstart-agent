"""Parse /start command arguments for widget handoff."""

import re
from uuid import UUID

SESSION_ARG_PATTERN = re.compile(
    r"^session_([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$",
    re.IGNORECASE,
)


def parse_handoff_session_id(args: str | None) -> UUID | None:
    """Extract session UUID from Telegram deep-link args `session_{uuid}`."""
    if args is None:
        return None
    match = SESSION_ARG_PATTERN.match(args.strip())
    if match is None:
        return None
    return UUID(match.group(1))


def build_handoff_message(session_id: UUID) -> str:
    """Build backend handoff message for widget → Telegram transition."""
    return f"/start session_{session_id}"
