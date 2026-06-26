"""search_knowledge_base tool — RAG retrieval with audience filter."""

from typing import Literal

from langchain_core.tools import tool

from app.tools.context import get_tool_context

Audience = Literal["b2b", "b2c"]


@tool
async def search_knowledge_base(query: str, audience: Audience) -> str:
    """Search the LLMStart knowledge base for information relevant to the query.

    Use audience='b2c' for individual learners and course questions.
    Use audience='b2b' for corporate training and enterprise services.
    """
    ctx = get_tool_context()
    await ctx.store.update(ctx.session_id, segment=audience)
    documents = ctx.retriever.search(query, audience)
    return ctx.retriever.format_results(documents)
