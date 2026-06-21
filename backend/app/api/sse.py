"""Server-Sent Events streaming helpers."""

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any


def format_sse_event(event_type: str, data: dict[str, Any]) -> str:
    """Format a single SSE frame with event type and JSON payload."""
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event_type}\ndata: {payload}\n\n"


async def stream_sse_events(
    events: AsyncIterator[tuple[str, dict[str, Any]]],
) -> AsyncIterator[str]:
    """Yield formatted SSE frames from an async sequence of (event_type, data) pairs."""
    try:
        async for event_type, data in events:
            yield format_sse_event(event_type, data)
    except asyncio.CancelledError:
        return
