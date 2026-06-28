# ruff: noqa: T201, INP001
"""Upload validation dataset JSONL to Langfuse as a dataset with items."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

from dotenv import load_dotenv
from langfuse import Langfuse

ROOT = Path(__file__).resolve().parents[1]
LANGFUSE_LOCAL_ENV = ROOT / "infra" / "langfuse" / ".env"
DEFAULT_JSONL = ROOT / "datasets" / "v1" / "all.jsonl"
DEFAULT_LOCAL_HOST = "http://localhost:3001"
DEFAULT_DATASET_NAME = "llmstart-agent-v1"
DEFAULT_DESCRIPTION = (
    "LLMStart agent validation dataset v1 — hybrid extraction + synthesis (60 records)."
)
AUTH_HELP = (
    "Langfuse authentication failed. For local self-hosted: create API keys at "
    "http://localhost:3001 → Project Settings → API Keys, then set "
    "LANGFUSE_HOST=http://localhost:3001 in .env."
)
NO_PROJECTS = "No Langfuse projects available for the configured credentials."


class UploadError(Exception):
    """Upload failed with a user-facing message."""


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            msg = f"{path}:{line_no}: invalid JSON: {exc}"
            raise UploadError(msg) from exc
        for field in ("id", "input", "expected_output", "metadata"):
            if field not in record:
                msg = f"{path}:{line_no}: missing required field '{field}'"
                raise UploadError(msg)
        records.append(record)
    if not records:
        msg = f"{path}: no records found"
        raise UploadError(msg)
    return records


def apply_local_langfuse_env() -> None:
    """Load self-hosted credentials from infra/langfuse/.env (headless init keys)."""
    if LANGFUSE_LOCAL_ENV.exists():
        load_dotenv(LANGFUSE_LOCAL_ENV, override=True)
    public_key = os.environ.get("LANGFUSE_INIT_PROJECT_PUBLIC_KEY")
    secret_key = os.environ.get("LANGFUSE_INIT_PROJECT_SECRET_KEY")
    if public_key:
        os.environ["LANGFUSE_PUBLIC_KEY"] = public_key
    if secret_key:
        os.environ["LANGFUSE_SECRET_KEY"] = secret_key
    os.environ["LANGFUSE_HOST"] = DEFAULT_LOCAL_HOST


def build_client(host: str | None) -> Langfuse:
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
    if not public_key or not secret_key:
        msg = (
            "LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY must be set "
            "(repo .env or environment)."
        )
        raise UploadError(msg)

    resolved_host = host or os.environ.get("LANGFUSE_HOST", "http://localhost:3001")
    return Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host=resolved_host,
        tracing_enabled=False,
    )


def _is_not_found(exc: Exception) -> bool:
    not_found = 404
    if getattr(exc, "status_code", None) == not_found:
        return True
    message = str(exc).lower()
    return "404" in message or "not found" in message


def ensure_dataset(client: Langfuse, name: str, description: str, host: str) -> str:
    encoded_name = quote(name, safe="")
    try:
        existing = client.api.datasets.get(dataset_name=encoded_name)
    except Exception as exc:
        if not _is_not_found(exc):
            msg = f"Failed to check dataset '{name}' at {host}: {exc}"
            raise UploadError(msg) from exc
    else:
        return existing.id

    try:
        created = client.create_dataset(name=name, description=description)
    except Exception as exc:
        msg = f"Failed to create dataset '{name}': {exc}"
        raise UploadError(msg) from exc
    return created.id


def list_item_ids(client: Langfuse, dataset_name: str) -> list[str]:
    item_ids: list[str] = []
    page = 1
    while True:
        response = client.api.dataset_items.list(
            dataset_name=dataset_name,
            page=page,
            limit=100,
        )
        if not response.data:
            break
        item_ids.extend(item.id for item in response.data)
        total_pages = getattr(response.meta, "total_pages", page)
        if page >= total_pages:
            break
        page += 1
    return item_ids


def delete_items(client: Langfuse, item_ids: list[str]) -> int:
    deleted = 0
    for item_id in item_ids:
        client.api.dataset_items.delete(id=item_id)
        deleted += 1
    return deleted


def upload_items(
    client: Langfuse,
    *,
    dataset_name: str,
    records: list[dict[str, Any]],
) -> int:
    uploaded = 0
    for record in records:
        client.create_dataset_item(
            dataset_name=dataset_name,
            id=record["id"],
            input=record["input"],
            expected_output=record["expected_output"],
            metadata=record["metadata"],
        )
        uploaded += 1
    return uploaded


def resolve_project_id(client: Langfuse) -> str:
    try:
        projects = client.api.projects.get()
    except Exception as exc:
        raise UploadError(AUTH_HELP) from exc
    if not projects.data:
        raise UploadError(NO_PROJECTS)
    return projects.data[0].id


def dataset_ui_url(host: str, project_id: str, dataset_id: str) -> str:
    base = host.rstrip("/")
    return f"{base}/project/{project_id}/datasets/{dataset_id}/items"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload JSONL validation dataset to Langfuse.",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_JSONL,
        help=f"JSONL file (default: {DEFAULT_JSONL.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--dataset-name",
        default=DEFAULT_DATASET_NAME,
        help=f"Langfuse dataset name (default: {DEFAULT_DATASET_NAME})",
    )
    parser.add_argument(
        "--description",
        default=DEFAULT_DESCRIPTION,
        help="Dataset description for newly created datasets",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Langfuse host override (default: LANGFUSE_HOST or http://localhost:3001)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Delete existing dataset items before upload (full replace)",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help=(
            "Use self-hosted Langfuse at localhost:3001 with keys from "
            "infra/langfuse/.env (LANGFUSE_INIT_PROJECT_*)."
        ),
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv(ROOT / ".env")
    args = parse_args()
    if args.local:
        apply_local_langfuse_env()
        if args.host is None:
            args.host = DEFAULT_LOCAL_HOST

    jsonl_path = args.file if args.file.is_absolute() else ROOT / args.file
    if not jsonl_path.exists():
        print(f"File not found: {jsonl_path}", file=sys.stderr)
        return 1

    try:
        records = load_records(jsonl_path)
        host = args.host or os.environ.get("LANGFUSE_HOST", "http://localhost:3001")
        client = build_client(args.host)

        dataset_id = ensure_dataset(client, args.dataset_name, args.description, host)
        project_id = resolve_project_id(client)

        deleted = 0
        if args.reload:
            existing_ids = list_item_ids(client, args.dataset_name)
            deleted = delete_items(client, existing_ids)

        uploaded = upload_items(client, dataset_name=args.dataset_name, records=records)
        client.flush()

        url = dataset_ui_url(host, project_id, dataset_id)
        mode = "reload" if args.reload else "upsert"
        print(f"Dataset: {args.dataset_name}")
        print(f"Mode: {mode}")
        print(f"Source: {jsonl_path}")
        if args.reload:
            print(f"Deleted existing items: {deleted}")
        print(f"Uploaded items: {uploaded}")
        print(f"Langfuse UI: {url}")
    except UploadError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
