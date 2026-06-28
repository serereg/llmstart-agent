#!/usr/bin/env python3
"""Flatten JSON dialog exports to plain text for Level-1 analysis."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROLE_LABELS = {
    "peer": "USER",
    "me": "EXPERT",
}


def flatten_dialog(dialog_path: Path) -> str:
    data = json.loads(dialog_path.read_text(encoding="utf-8"))
    lines: list[str] = [f"# Dialog: {dialog_path.stem}", ""]

    for msg in data.get("messages", []):
        role = ROLE_LABELS.get(msg.get("from", ""), msg.get("from", "UNKNOWN").upper())
        date = msg.get("date", "")
        text = msg.get("text", "").strip()
        if not text:
            continue
        lines.append(f"[{date}] {role}:")
        lines.append(text)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    input_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("datasets/dialogs")
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else input_dir / "flat"
    output_dir.mkdir(parents=True, exist_ok=True)

    dialog_files = sorted(input_dir.glob("CHAT_*.json"))
    if not dialog_files:
        print(f"No CHAT_*.json files found in {input_dir}", file=sys.stderr)
        return 1

    for dialog_path in dialog_files:
        flat_path = output_dir / f"{dialog_path.stem}.txt"
        flat_path.write_text(flatten_dialog(dialog_path), encoding="utf-8")
        print(f"Wrote {flat_path}")

    print(f"Flattened {len(dialog_files)} dialogs → {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
