# Summary: Task 06 — react-agent-skeleton

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-06-21

---

## Что реализовано

- `backend/pyproject.toml` — зависимости `langchain`, `langchain-openai`, `langchain-core` (зафиксированы в `uv.lock`)
- `backend/app/agent/prompts.py` — system prompt LLMStart Agent (консультант llmstart.ru) и `HANDOFF_USER_MESSAGE` для Telegram handoff
- `backend/app/agent/core.py` — `AgentService`: `create_agent(tools=[])`, `invoke`, `stream_sse`; singleton `get_agent_service()`; fallback при OpenAI errors
- `backend/app/agent/__init__.py` — пакет agent
- `backend/app/api/chat.py` — stub заменён на agent wiring: web → SSE (`reasoning`, `token`, `done`/`error`), telegram → JSON; persist user/assistant messages
- `backend/tests/test_agent.py` — unit-тесты invoke, SSE, error fallback, маппинг истории
- `backend/tests/test_chat_api.py` — расширение: mock LLM через `dependency_overrides`, GET sessions, SSE format, OpenAI error fallback
- `backend/tests/fakes.py` — `FailingChatModel` для симуляции `APIError` в invoke и streaming

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| `create_agent` (LangChain 1.x / LangGraph) вместо legacy `AgentExecutor` | В установленной версии LangChain 1.3.x API — `langchain.agents.create_agent`, возвращает `CompiledStateGraph` |
| Reasoning step — один статический шаг «Формирую ответ...» | Без tools ReAct loop не даёт промежуточных шагов; полноценный reasoning появится в sprint-02 с business tools |
| `tests/fakes.py` — отдельный файл с `FailingChatModel` | Streaming идёт через `_astream`, а не `_call`; общий fake нужен и в unit-, и в integration-тестах |

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| `create_agent(llm, tools=[], system_prompt=...)` | Skeleton без business tools; соответствует ADR ReAct + tools | [ADR-0001](../../../../adrs/0001-react-agent-core.md) |
| Token streaming через `astream_events(version="v2")` + `on_chat_model_stream` | Нативный streaming LangChain/LangGraph; character-by-character chunks от LLM | — |
| `AgentService` как DI-зависимость (`get_agent_service`) | Тестируемость: override mock LLM без реального API key | — |
| OpenAI errors → HTTP 200 + `error: true` + fallback message | Контракт api-contracts.md: ошибка передаётся в теле, не через 5xx | [api-contracts.md](../../../../concept/api-contracts.md) |
| Persist assistant message после SSE `done` | История сессии полная; user message сохраняется до invoke | — |
| Handoff: agent получает `HANDOFF_USER_MESSAGE`, не `/start session_{uuid}` | Служебное сообщение Telegram не должно попадать в историю как user turn | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| LangChain 1.x: нет `AgentExecutor` / `create_react_agent` | Использован `langchain.agents.create_agent` |
| mypy: overload mismatch для `ainvoke` / `astream_events` | `self._agent: Any` — типы LangGraph stubs неполные |
| SSE error-тесты падали: `_call` не вызывается при streaming | `FailingChatModel` переопределяет `_astream` и `_stream` |
| ruff RUF001 на кириллице в system prompt | `per-file-ignores` для `app/agent/prompts.py` |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Chat invoke с mock LLM → reply в response | ✅ `test_telegram_channel_returns_json`, `test_invoke_returns_mock_reply` |
| 2 | SSE stream содержит `done` с session_id и reply | ✅ `test_web_channel_returns_sse_done_event`, `test_sse_event_format` |
| 3 | Messages сохранены в session | ✅ `test_messages_persisted_and_visible_via_get_session`, `test_null_session_id_creates_new_session` |
| 4 | OpenAI exception → fallback, error flag | ✅ `test_openai_error_returns_fallback_telegram/sse`, `test_invoke_openai_error_returns_fallback` |
| 5 | Agent без business tools (`tools=[]`) | ✅ `create_agent(llm, tools=[], ...)` в `core.py` |
| 6 | Full CI green | ✅ `make ci` — 39 passed |

---

## Что дальше

- **Sprint 02: agent-rag** — business tools (`search_knowledge_base`, `list_b2c_products`, `save_lead`, payments), Langfuse tracing, полноценный ReAct reasoning/tool events
- **Manual smoke** — реальный запрос с `OPENAI_API_KEY` → осмысленный ответ агента (не в CI)

---

## Ссылки

- [ADR-0001](../../../../adrs/0001-react-agent-core.md) — ReAct agent core
- [api-contracts.md](../../../../concept/api-contracts.md) — SSE events, error fallback
- [architecture.md](../../../../concept/architecture.md) — поток web SSE / telegram JSON
- [Sprint 02 README](../../../sprint-02-agent-rag/README.md) — следующий спринт
