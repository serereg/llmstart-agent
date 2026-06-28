#!/usr/bin/env python3
"""Validate dataset JSONL records against schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "datasets" / "schemas"))

from dataset_record import DatasetRecord  # noqa: E402


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            DatasetRecord.model_validate(data)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path.name}:{i}: {exc}")
    return errors


def main() -> int:
    v1 = ROOT / "datasets" / "v1"
    extracted = v1 / "extracted"
    synthesized = v1 / "synthesized"
    files = [
        v1 / "all.jsonl",
        v1 / "b2c.jsonl",
        v1 / "b2b.jsonl",
        extracted / "all.jsonl",
        extracted / "b2c.jsonl",
        extracted / "b2b.jsonl",
        synthesized / "all.jsonl",
        synthesized / "b2c.jsonl",
        synthesized / "b2b.jsonl",
    ]
    all_errors: list[str] = []
    for path in files:
        if path.exists():
            all_errors.extend(validate_file(path))

    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        return 1

    print(f"OK: validated {len(files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
