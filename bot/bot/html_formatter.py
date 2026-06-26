"""Convert agent Markdown replies to Telegram HTML subset."""

import html
import re

_BOLD_PATTERN = re.compile(r"\*\*(.+?)\*\*")
_CODE_PATTERN = re.compile(r"`([^`]+)`")
_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def escape_html(text: str) -> str:
    """Escape characters reserved in Telegram HTML."""
    return html.escape(text, quote=False)


def markdown_to_telegram_html(text: str) -> str:
    """Convert a Markdown subset to Telegram-compatible HTML."""
    escaped = escape_html(text)
    escaped = _LINK_PATTERN.sub(r'<a href="\2">\1</a>', escaped)
    escaped = _BOLD_PATTERN.sub(r"<b>\1</b>", escaped)
    return _CODE_PATTERN.sub(r"<code>\1</code>", escaped)
