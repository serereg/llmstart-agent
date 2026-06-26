"""Tests for Markdown → Telegram HTML conversion."""

from bot.html_formatter import escape_html, markdown_to_telegram_html


def test_escape_html_special_chars() -> None:
    assert escape_html("<script>&") == "&lt;script&gt;&amp;"


def test_bold_markdown() -> None:
    assert markdown_to_telegram_html("Рекомендую **agents** курс") == (
        "Рекомендую <b>agents</b> курс"
    )


def test_inline_code() -> None:
    assert markdown_to_telegram_html("Используйте `search_knowledge_base`") == (
        "Используйте <code>search_knowledge_base</code>"
    )


def test_markdown_link() -> None:
    assert markdown_to_telegram_html("[курс](https://llmstart.ru/agents)") == (
        '<a href="https://llmstart.ru/agents">курс</a>'
    )


def test_combined_markdown() -> None:
    source = "Курс **agents** — см. [описание](https://example.com) и `pip install`"
    result = markdown_to_telegram_html(source)
    assert "<b>agents</b>" in result
    assert '<a href="https://example.com">описание</a>' in result
    assert "<code>pip install</code>" in result


def test_escapes_raw_html_in_agent_reply() -> None:
    assert markdown_to_telegram_html("Ответ <b>не тег</b>") == ("Ответ &lt;b&gt;не тег&lt;/b&gt;")
