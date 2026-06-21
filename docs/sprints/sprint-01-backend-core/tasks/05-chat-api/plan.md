# Task 05: chat-api

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/backend-5-chat-api`
> **Spec:** без spec — [api-contracts.md](../../../../concept/api-contracts.md)

---

## Цель

Эндпоинт `POST /api/v1/chat` с маршрутизацией SSE (web) / JSON (telegram), lifecycle сессий и stub-ответом до подключения ReAct-агента.

---

## Состав работ

- [ ] Pydantic-схемы: ChatRequest (session_id, message, channel), ChatResponse (telegram)
- [ ] Валидация: message required, max 4000 chars, channel ∈ {web, telegram}
- [ ] Session lifecycle: null session_id → create; unknown id → 404
- [ ] Handoff: парсинг `/start session_{uuid}` в message для channel=telegram
- [ ] Ветка `channel=telegram`: JSON 200 `{session_id, reply}` со stub reply
- [ ] Ветка `channel=web`: SSE `text/event-stream`, минимум event `done` со stub
- [ ] Заготовка SSE helper: emit `event:` / `data:` JSON
- [ ] Сохранение user message в session (assistant — stub)
- [ ] Integration-тесты: SSE parsing, JSON response, validation errors, 401
- [ ] Самопроверка по критериям DoD

---

## Критерии готовности (DoD)

| # | Kритерий | Способ проверки |
|---|----------|-----------------|
| 1 | `channel=web` → SSE с event `done` | pytest |
| 2 | `channel=telegram` → JSON `{session_id, reply}` | pytest |
| 3 | Новая сессия при session_id=null | pytest |
| 4 | Unknown session_id → 404 | pytest |
| 5 | Пустой message / invalid channel → 422 | pytest |
| 6 | Handoff `/start session_{uuid}` привязывает сессию | pytest |
| 7 | Lint + tests | `make test-backend` |

---

## Артефакты

- `backend/app/api/chat.py`
- `backend/app/api/schemas/chat.py`
- `backend/app/api/sse.py` — SSE streaming helper (optional module)
- `backend/app/api/router.py` — include chat router
- `backend/tests/test_chat_api.py`

---

## Scope

**Трогаем:** chat endpoint, schemas, SSE helper, chat tests.

**НЕ трогаем:**
- ReAct agent / OpenAI calls — task 06
- Business tools events (tool_start/tool_end) — stub only или sprint-02
- CORS full config — минимально если нужно для тестов

---

## Риски и допущения

- Stub reply: фиксированная строка или echo — заменяется в task 06
- SSE client disconnect — graceful cancel (базовая обработка)

---

## Открытые вопросы

- [ ] Нет — SSE event types зафиксированы в api-contracts.md
