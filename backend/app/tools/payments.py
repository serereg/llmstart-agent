"""Payment mock tools — create_payment_link and confirm_payment."""

import json
import uuid
from pathlib import Path

from langchain_core.tools import tool

from app.sessions.models import PaymentState, PaymentStatus
from app.tools.context import get_tool_context
from app.tools.products import load_products_catalog


def _find_product(products_file: Path, product_id: str) -> dict[str, object] | None:
    for product in load_products_catalog(products_file):
        if product.get("id") == product_id:
            return product
    return None


@tool
async def create_payment_link(product_id: str) -> str:
    """Generate a mock payment link for the selected B2C product.

    Sets session payment status to pending. Use after the user chooses a product.
    """
    ctx = get_tool_context()
    products_file = Path(ctx.products_file_path)
    product = _find_product(products_file, product_id)
    if product is None:
        return json.dumps(
            {"error": f"Product '{product_id}' not found in catalog"},
            ensure_ascii=False,
        )

    mock_link = f"https://pay.llmstart.ru/mock/{uuid.uuid4()}"
    payment = PaymentState(status=PaymentStatus.PENDING, mock_link=mock_link)
    await ctx.store.update(ctx.session_id, payment=payment, segment="b2c")

    return json.dumps(
        {
            "product_id": product_id,
            "product_name": product.get("name"),
            "mock_link": mock_link,
            "status": PaymentStatus.PENDING.value,
        },
        ensure_ascii=False,
    )


@tool
async def confirm_payment() -> str:
    """Confirm mock payment after the user says they have paid.

    Updates session payment status to paid. Requires a pending payment link first.
    """
    ctx = get_tool_context()
    session = await ctx.store.get(ctx.session_id)
    if session is None:
        return json.dumps({"error": "Session not found"}, ensure_ascii=False)

    if session.payment.status != PaymentStatus.PENDING:
        return json.dumps(
            {
                "error": "No pending payment to confirm",
                "current_status": session.payment.status.value,
            },
            ensure_ascii=False,
        )

    payment = PaymentState(
        status=PaymentStatus.PAID,
        mock_link=session.payment.mock_link,
    )
    await ctx.store.update(ctx.session_id, payment=payment)

    return json.dumps(
        {"status": PaymentStatus.PAID.value, "mock_link": session.payment.mock_link},
        ensure_ascii=False,
    )
