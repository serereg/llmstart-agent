# Task 06: react-agent-skeleton

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/backend-6-react-skeleton`
> **Spec:** без spec — [ADR-0001](../../../../adrs/0001-react-agent-core.md), [api-contracts.md](../../../../concept/api-contracts.md)

---

## Цель

LangChain ReAct-агент (без business tools) подключён к `POST /api/v1/chat`: вызов OpenAI, SSE-события reasoning/token/done, сохранение истории в сессии.

---

## Состав работ

- [x] Добавить зависимости: langchain, langchain-openai, langchain-core
- [x] Реализовать `app/agent/prompts.py` — system prompt LLMStart Agent (консультант llmstart.ru)
- [x] Реализовать `app/agent/core.py` — create_agent / AgentExecutor с пустым tools list
- [x] Callback/hook для SSE: reasoning steps, token streaming
- [x] Интегрировать agent в chat endpoint: заменить stub reply
- [x] Web: SSE events `reasoning`, `token`, `done`; Telegram: JSON final reply
- [x] OpenAI error handling: fallback «Сервис временно недоступен...», `error: true`
- [x] Persist user + assistant messages в Session после invoke
- [x] Тесты с mock LLM (pytest); не требовать реальный API key в CI
- [x] Самопроверка по критериям DoD

---

## Критерии готовности (DoD)

| # | Kритерий | Способ проверки |
|---|----------|-----------------|
| 1 | Chat invoke с mock LLM → reply в response | pytest |
| 2 | SSE stream содержит `done` с session_id и reply | pytest |
| 3 | Messages сохранены в session | pytest + GET sessions |
| 4 | OpenAI exception → fallback, error flag | pytest |
| 5 | Agent без business tools (tools=[] или minimal) | code review |
| 6 | Full CI green | `make ci` |

---

## Артефакты

- `backend/app/agent/core.py`
- `backend/app/agent/prompts.py`
- `backend/app/api/chat.py` — agent wiring
- `backend/pyproject.toml` — langchain deps
- `backend/tests/test_agent.py`
- `backend/tests/test_chat_api.py` — расширение

---

## Scope

**Трогаем:** agent module, chat integration, langchain deps, agent/chat tests.

**НЕ трогаем:**
- Business tools (RAG, products, payments, leads) — sprint-02
- Langfuse callback/tracing — sprint-02
- frontend, bot — sprint-03/04

---

## Риски и допущения

- LangChain API может меняться — фиксация версий в uv.lock
- Streaming tokens зависит от LangChain API — допустим batch reply в MVP skeleton если streaming сложен (зафиксировать в summary)
- Langfuse keys уже в config (task 02), но tracing подключается в sprint-02

---

## Открытые вопросы

- [x] Streaming: token-by-token vs single chunk — выбрать при реализации, зафиксировать в summary
