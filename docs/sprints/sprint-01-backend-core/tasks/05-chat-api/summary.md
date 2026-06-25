# Summary: Task 05 — chat-api

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-06-21

---

## Что реализовано

- `backend/app/api/schemas/chat.py` — `ChatRequest` (session_id, message, channel), `ChatResponse` (session_id, reply, error); валидация max 4000 chars
- `backend/app/api/sse.py` — `format_sse_event`, `stream_sse_events` (формат `event:` / `data:` JSON, graceful cancel)
- `backend/app/api/chat.py` — `POST /api/v1/chat`: session lifecycle, handoff `/start session_{uuid}`, ветвление web→SSE / telegram→JSON, persist messages, disconnect handling
- `backend/app/api/router.py` — chat router в защищённом `v1_router`
- `backend/tests/test_chat_api.py` — integration-тесты SSE, JSON, 404, 422, 401, handoff, SSE format

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| Stub reply заменён ReAct-агентом в task 06 | По плану task 05 — заглушка; task 06 подключил `AgentService` в тот же `chat.py` |
| SSE events расширены до `reasoning`, `token`, `error` | Добавлено в task 06 поверх SSE-helper из task 05 |

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| `channel` определяет формат ответа (SSE vs JSON) | Контракт api-contracts.md | [api-contracts.md](../../../../concept/api-contracts.md) |
| Handoff: парсинг UUID из message, не из session_id | Bot отправляет `/start session_{uuid}` как message | [api-contracts.md](../../../../concept/api-contracts.md) |
| `resolve_session` + `is_handoff` flag | Handoff не дублирует user message в историю | — |
| SSE через async generator + `request.is_disconnected()` | Graceful cancel при disconnect клиента | — |
| Отдельный модуль `sse.py` | Переиспользование форматтера при расширении events в task 06 | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| Handoff не должен сохранять `/start session_{uuid}` как user message | `skip_user_message=is_handoff` при persist |
| SSE parsing в тестах | Helper `parse_sse_events` разбирает `event:` / `data:` блоки |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `channel=web` → SSE с event `done` | ✅ `test_web_channel_returns_sse_done_event` |
| 2 | `channel=telegram` → JSON `{session_id, reply}` | ✅ `test_telegram_channel_returns_json` |
| 3 | Новая сессия при session_id=null | ✅ `test_null_session_id_creates_new_session` |
| 4 | Unknown session_id → 404 | ✅ `test_unknown_session_id_returns_404` |
| 5 | Пустой message / invalid channel → 422 | ✅ `test_empty_message_returns_422`, `test_invalid_channel_returns_422` |
| 6 | Handoff `/start session_{uuid}` привязывает сессию | ✅ `test_handoff_binds_existing_session` |
| 7 | Lint + tests | ✅ `make ci` — 39 passed |

---

## Что дальше

- **Task 06: react-agent-skeleton** — замена stub reply на LangChain ReAct agent ✅ (выполнено)

---

## Ссылки

- [api-contracts.md](../../../../concept/api-contracts.md) — контракт `POST /api/v1/chat`
- [architecture.md](../../../../concept/architecture.md) — SSE-протокол
- [Task 06 summary](../06-react-agent-skeleton/summary.md) — agent wiring
