"""list_b2c_products tool — B2C product catalog."""

import json
from pathlib import Path

from langchain_core.tools import tool

from app.tools.context import get_tool_context


def load_products_catalog(products_file: Path) -> list[dict[str, object]]:
    """Load B2C products from JSON catalog file."""
    if not products_file.is_file():
        return []
    raw = products_file.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, list):
        msg = "products.json must contain a JSON array"
        raise TypeError(msg)
    return data


@tool
def list_b2c_products() -> str:
    """Return the catalog of B2C courses and products as JSON."""
    ctx = get_tool_context()
    products = load_products_catalog(Path(ctx.products_file_path))
    return json.dumps(products, ensure_ascii=False, indent=2)
