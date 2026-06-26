"""save_lead tool — append lead to data/leads.txt mock CRM."""

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from langchain_core.tools import tool

from app.tools.context import get_tool_context

Segment = Literal["b2b", "b2c"]


def _append_lead_line(leads_path: Path, line: str) -> None:
    leads_path.parent.mkdir(parents=True, exist_ok=True)
    with leads_path.open("a", encoding="utf-8") as leads_file:
        leads_file.write(line)


@tool
async def save_lead(
    name: str,
    contact: str,
    product: str,
    segment: Segment,
) -> str:
    """Save a lead to the CRM file after collecting user contact details.

    Call after payment confirmation (B2C) or when a B2B prospect agrees to be contacted.
    """
    ctx = get_tool_context()
    await ctx.store.update(ctx.session_id, segment=segment)

    timestamp = datetime.now(UTC).isoformat()
    line = f"{timestamp}|{segment}|{name}|{contact}|{product}\n"
    leads_path = Path(ctx.leads_file_path)
    await asyncio.to_thread(_append_lead_line, leads_path, line)

    return f"Lead saved: {name} ({segment}), product={product}"
