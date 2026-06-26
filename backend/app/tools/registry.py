"""Registry of all business tools wired into the ReAct agent."""

from langchain_core.tools import BaseTool

from app.tools.knowledge import search_knowledge_base
from app.tools.leads import save_lead
from app.tools.payments import confirm_payment, create_payment_link
from app.tools.products import list_b2c_products

BUSINESS_TOOLS: list[BaseTool] = [
    search_knowledge_base,
    list_b2c_products,
    create_payment_link,
    confirm_payment,
    save_lead,
]
