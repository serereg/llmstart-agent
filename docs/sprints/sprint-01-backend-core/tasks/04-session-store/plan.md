# Task 04: session-store

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/backend-4-session-store`
> **Spec:** без spec — [ADR-0002](../../../../adrs/0002-in-memory-sessions.md), [api-contracts.md](../../../../concept/api-contracts.md)

---

## Цель

In-memory хранилище сессий диалога и REST-эндпоинт `GET /api/v1/sessions/{session_id}` для чтения истории и метаданных.

---

## Состав работ

- [ ] Определить Pydantic/dataclass модели: Session, Message, PaymentState
- [ ] Поля: session_id (UUID), channel, segment, messages[], payment {status, mock_link}, created_at, updated_at
- [ ] Реализовать `SessionStore` — dict in-memory, методы create/get/update/add_message
- [ ] Thread-safety: asyncio.Lock или threading.Lock (выбор зафиксировать в summary)
- [ ] Singleton store через dependency injection
- [ ] `GET /api/v1/sessions/{session_id}` — 200 / 404 по api-contracts.md
- [ ] Pydantic response schema SessionResponse
- [ ] Unit-тесты store; integration-тест GET endpoint с auth
- [ ] Самопроверка по критериям DoD

---

## Критерии готовности (DoD)

| # | Kритерий | Способ проверки |
|---|----------|-----------------|
| 1 | create + get session работает | pytest unit |
| 2 | add_message обновляет updated_at | pytest unit |
| 3 | GET unknown → 404 `"Session not found"` | pytest integration |
| 4 | GET existing → 200 с полной схемой | pytest integration |
| 5 | Endpoint требует auth | pytest |
| 6 | Lint + tests | `make test-backend` |

---

## Артефакты

- `backend/app/sessions/models.py`
- `backend/app/sessions/store.py`
- `backend/app/api/sessions.py`
- `backend/app/api/schemas/session.py`
- `backend/app/api/router.py` — include sessions router
- `backend/tests/test_sessions.py`

---

## Scope

**Трогаем:** sessions module, GET sessions endpoint, schemas, tests.

**НЕ трогаем:**
- POST /chat session lifecycle — task 05
- Payment state updates — sprint-02 (tools)
- PostgreSQL persistence — roadmap TBD

---

## Риски и допущения

- In-memory: данные теряются при рестарте — допустимо по ADR-0002
- Один инстанс backend — достаточно для MVP
- segment изначально null, определяется агентом в sprint-02

---

## Открытые вопросы

- [ ] Нет
