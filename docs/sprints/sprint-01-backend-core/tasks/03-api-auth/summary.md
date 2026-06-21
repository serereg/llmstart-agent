# Summary: Task 03 — api-auth

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-06-21

---

## Что реализовано

- `backend/app/api/deps.py` — dependency `verify_api_key`: парсинг `Authorization: Bearer <token>`, constant-time сравнение с `settings.backend_api_key`, HTTP 401 с `{"detail": "Invalid or missing API key"}`
- `backend/app/api/router.py` — разделение роутеров: `/health` публичный, `/api/v1/*` защищён через `dependencies=[Depends(verify_api_key)]`; заглушка `GET /api/v1/ping` для интеграционных тестов
- `backend/tests/test_auth.py` — integration-тесты: missing header, wrong token, valid token, `/health` без auth

---

## Отклонения от плана

нет отклонений

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| `HTTPBearer(auto_error=False)` для парсинга Bearer | Стандартный FastAPI-паттерн; единая точка 401 с кастомным `detail` | — |
| `secrets.compare_digest` для сравнения ключей | Timing-safe compare по api-contracts.md и plan.md | — |
| Auth на уровне `APIRouter` (`dependencies=[...]`) | Все будущие эндпоинты `/api/v1/*` автоматически защищены без дублирования | — |
| Заглушка `GET /api/v1/ping` вместо chat/sessions | Chat и sessions — tasks 04–05; ping достаточен для проверки auth | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| — | — |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `/api/v1/*` без ключа → 401 | ✅ `test_api_v1_without_api_key_returns_401` |
| 2 | Неверный ключ → 401 с корректным detail | ✅ `test_api_v1_with_wrong_api_key_returns_401` |
| 3 | Верный ключ → не 401 | ✅ `test_api_v1_with_valid_api_key_returns_200` |
| 4 | `/health` без ключа → 200 | ✅ `test_health_without_api_key_returns_200` |
| 5 | Lint + tests | ✅ `make test-backend` — 16 passed |

---

## Что дальше

- **Task 04: session-store** — in-memory `SessionStore` и `GET /api/v1/sessions/{session_id}`
- **Task 05: chat-api** — `POST /api/v1/chat` подключится к уже защищённому v1 router

---

## Ссылки

- [api-contracts.md](../../../../concept/api-contracts.md) — контракт аутентификации
- [Task 04 plan](../04-session-store/plan.md) — следующая задача спринта
