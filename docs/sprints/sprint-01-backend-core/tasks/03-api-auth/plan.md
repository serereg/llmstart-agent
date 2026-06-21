# Task 03: api-auth

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/backend-3-api-auth`
> **Spec:** без spec — [api-contracts.md](../../../../concept/api-contracts.md)

---

## Цель

Bearer-аутентификация для всех эндпоинтов `/api/v1/*` через shared secret `BACKEND_API_KEY`; `/health` остаётся публичным.

---

## Состав работ

- [ ] Реализовать `verify_api_key` dependency в `app/api/deps.py`
- [ ] Парсинг заголовка `Authorization: Bearer <token>`
- [ ] Сравнение с `settings.backend_api_key` (constant-time compare)
- [ ] HTTP 401 + `{"detail": "Invalid or missing API key"}` при ошибке
- [ ] Подключить dependency к APIRouter с prefix `/api/v1`
- [ ] Заглушка protected endpoint для тестирования (или использовать будущий sessions/chat)
- [ ] Integration-тесты: missing header, wrong token, valid token
- [ ] Самопроверка по критериям DoD

---

## Критерии готовности (DoD)

| # | Kритерий | Способ проверки |
|---|----------|-----------------|
| 1 | `/api/v1/*` без ключа → 401 | pytest |
| 2 | Неверный ключ → 401 с корректным detail | pytest |
| 3 | Верный ключ → не 401 | pytest |
| 4 | `/health` без ключа → 200 | pytest |
| 5 | Lint + tests | `make test-backend` |

---

## Артефакты

- `backend/app/api/deps.py` — verify_api_key
- `backend/app/api/router.py` — auth на /api/v1 router
- `backend/tests/test_auth.py`

---

## Scope

**Трогаем:** deps.py, router wiring, auth tests.

**НЕ трогаем:**
- Реализацию chat/sessions — tasks 04–05
- Per-user JWT auth — roadmap v1.0
- frontend/bot clients — sprint-03/04

---

## Риски и допущения

- MVP: один shared secret для bot и frontend — по api-contracts.md
- Timing-safe compare через `secrets.compare_digest`

---

## Открытые вопросы

- [ ] Нет
