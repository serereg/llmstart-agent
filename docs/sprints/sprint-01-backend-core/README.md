# Sprint 01: backend-core

> **Версия roadmap:** v0.1 — MVP
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** 🚧 In Progress
> **Открыт:** 2026-06-21
> **Закрыт:** —

---

## Цель спринта

Рабочий backend Agent Core: FastAPI-сервис с конфигурацией, аутентификацией, in-memory сессиями, healthcheck и ReAct-скелетом — готов принимать сообщения через REST/SSE без бизнес-tools.

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Backend стартует локально через `make dev-backend` | `curl http://localhost:8000/health` → `200 {"status": "ok"}` |
| 2 | `/health` без auth; `/api/v1/*` требуют Bearer token | `curl /health` → 200; `curl /api/v1/chat` без ключа → 401 |
| 3 | In-memory сессии: создание, чтение, история сообщений | `GET /api/v1/sessions/{id}` после chat → 200 с messages |
| 4 | `POST /api/v1/chat`: `channel=web` → SSE; `channel=telegram` → JSON | httpx/pytest: события `reasoning`, `token`, `done` / JSON `{reply, session_id}` |
| 5 | ReAct-скелет вызывает OpenAI и стримит ответ в chat | Сообщение в chat → ответ LLM в SSE/JSON (без business tools) |
| 6 | `make ci` проходит (lint, typecheck, test) | `make ci` exit 0 |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | backend-scaffold | ✅ | [plan](tasks/01-backend-scaffold/plan.md) | [summary](tasks/01-backend-scaffold/summary.md) |
| 02 | config-and-health | 📋 | [plan](tasks/02-config-and-health/plan.md) | — |
| 03 | api-auth | 📋 | [plan](tasks/03-api-auth/plan.md) | — |
| 04 | session-store | 📋 | [plan](tasks/04-session-store/plan.md) | — |
| 05 | chat-api | 📋 | [plan](tasks/05-chat-api/plan.md) | — |
| 06 | react-agent-skeleton | 📋 | [plan](tasks/06-react-agent-skeleton/plan.md) | — |

---

## Задача 01: backend-scaffold ✅

### Цель

Инициализирован Python-проект backend с uv, Makefile, базовой структурой FastAPI и smoke-тестами.

> 💡 **Скиллы:** `modern-python`, `uv-package-manager`, `fastapi-templates`

### Состав работ

- [x] Инициализировать `backend/` через uv (Python 3.12+, FastAPI, uvicorn, pydantic-settings, httpx, pytest)
- [x] Создать структуру каталогов по [architecture.md](../../concept/architecture.md)
- [x] Добавить корневой `Makefile` с целями `dev-backend`, `lint`, `format`, `typecheck`, `test`, `test-backend`, `ci`
- [x] Реализовать `app/main.py` с lifespan и подключением роутера
- [x] Добавить smoke-тест `GET /` или app startup
- [x] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `make dev-backend` поднимает сервер на :8000 | `curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/docs` → 200 |
| 2 | Smoke-тест проходит | `make test-backend` |
| 3 | Lint проходит | `make lint` |

**Пользователь проверяет:**

- Swagger UI доступен на `http://localhost:8000/docs`
- Структура `backend/app/` соответствует architecture.md

### Артефакты

- `backend/pyproject.toml` — зависимости и настройки ruff/mypy
- `backend/app/main.py` — точка входа FastAPI
- `backend/app/api/router.py` — агрегатор роутеров
- `Makefile` — dev/lint/test/ci
- `backend/tests/conftest.py`, `backend/tests/test_app.py` — smoke-тесты

### Документы

- 📋 [План задачи](tasks/01-backend-scaffold/plan.md)
- 📝 [Summary](tasks/01-backend-scaffold/summary.md)

---

## Задача 02: config-and-health 📋

### Цель

Fail-fast конфигурация из env и эндпоинт `GET /health` с проверкой зависимостей.

> 💡 **Скиллы:** `fastapi-templates`, `sharp-edges`

### Состав работ

- [ ] Реализовать `app/config.py` (Pydantic Settings): обязательные env из [integrations.md](../../concept/integrations.md)
- [ ] Создать `.env.example` в корне репозитория
- [ ] Реализовать `GET /health` по [api-contracts.md](../../concept/api-contracts.md) (без auth)
- [ ] Добавить probes OpenAI и Langfuse (async, timeout)
- [ ] Тесты health: 200 ok / 503 degraded
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Backend падает при отсутствии `OPENAI_API_KEY` | Запуск без env → понятная ошибка |
| 2 | `GET /health` → 200 с `status: ok` при доступных deps | `curl http://localhost:8000/health` |
| 3 | Тесты проходят | `make test-backend` |

**Пользователь проверяет:**

- `.env.example` содержит все переменные из integrations.md
- `/health` не требует Authorization

### Артефакты

- `backend/app/config.py`
- `backend/app/api/health.py`
- `.env.example`
- `backend/tests/test_health.py`

### Документы

- 📋 [План задачи](tasks/02-config-and-health/plan.md)
- 📝 [Summary](tasks/02-config-and-health/summary.md)

---

## Задача 03: api-auth 📋

### Цель

Bearer-аутентификация для всех эндпоинтов `/api/v1/*` по shared secret `BACKEND_API_KEY`.

> 💡 **Скиллы:** `fastapi-templates`, `api-design-principles`

### Состав работ

- [ ] Реализовать FastAPI dependency `verify_api_key` (Bearer token)
- [ ] Подключить dependency к роутеру `/api/v1`
- [ ] Обеспечить 401 с `{"detail": "Invalid or missing API key"}`
- [ ] Убедиться, что `/health` остаётся без auth
- [ ] Integration-тесты: valid key → pass; missing/invalid → 401
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Запрос без ключа → 401 | pytest + curl |
| 2 | Запрос с верным ключом → не 401 | pytest |
| 3 | `/health` без ключа → 200 | pytest |

**Пользователь проверяет:**

- Формат ошибки соответствует api-contracts.md

### Артефакты

- `backend/app/api/deps.py` — auth dependency
- `backend/app/api/router.py` — подключение auth
- `backend/tests/test_auth.py`

### Документы

- 📋 [План задачи](tasks/03-api-auth/plan.md)
- 📝 [Summary](tasks/03-api-auth/summary.md)

---

## Задача 04: session-store 📋

### Цель

In-memory хранилище сессий и эндпоинт `GET /api/v1/sessions/{session_id}` по ADR-0002.

> 💡 **Скиллы:** `python-design-patterns`, `fastapi-templates`

### Состав работ

- [ ] Реализовать модели Session (id, messages, channel, segment, payment, timestamps)
- [ ] Реализовать `SessionStore` — thread-safe in-memory dict
- [ ] Реализовать `GET /api/v1/sessions/{session_id}` по api-contracts.md
- [ ] Pydantic-схемы запроса/ответа
- [ ] Unit-тесты store; integration-тест GET sessions (404 / 200)
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Store создаёт/читает/обновляет сессию | pytest unit |
| 2 | GET unknown session → 404 | pytest integration |
| 3 | GET existing session → 200 с messages | pytest integration |

**Пользователь проверяет:**

- Поля ответа соответствуют api-contracts.md (segment, payment, messages)

### Артефакты

- `backend/app/sessions/models.py`
- `backend/app/sessions/store.py`
- `backend/app/api/sessions.py`
- `backend/tests/test_sessions.py`

### Документы

- 📋 [План задачи](tasks/04-session-store/plan.md)
- 📝 [Summary](tasks/04-session-store/summary.md)

---

## Задача 05: chat-api 📋

### Цель

Эндпоинт `POST /api/v1/chat` с маршрутизацией SSE (web) / JSON (telegram), lifecycle сессий и stub-ответом.

> 💡 **Скиллы:** `fastapi-templates`, `api-design-principles`

### Состав работ

- [ ] Pydantic-схемы ChatRequest / ChatResponse по api-contracts.md
- [ ] Логика создания сессии при `session_id=null` и 404 при unknown id
- [ ] Ветвление по `channel`: web → SSE, telegram → JSON
- [ ] SSE-формат: события `done` (stub reply); заготовка под reasoning/token
- [ ] Парсинг handoff `/start session_{uuid}` для telegram channel
- [ ] Валидация: message required, max 4000, channel enum
- [ ] Integration-тесты SSE и JSON
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Kритерий | Способ проверки |
|---|----------|-----------------|
| 1 | `channel=web` → `Content-Type: text/event-stream`, event `done` | pytest |
| 2 | `channel=telegram` → JSON `{session_id, reply}` | pytest |
| 3 | Новая сессия при null session_id | pytest |
| 4 | 422 на невалидный channel / пустой message | pytest |

**Пользователь проверяет:**

- SSE-события парсятся (формат `event:` / `data:`)

### Артефакты

- `backend/app/api/chat.py`
- `backend/app/api/schemas/chat.py`
- `backend/tests/test_chat_api.py`

### Документы

- 📋 [План задачи](tasks/05-chat-api/plan.md)
- 📝 [Summary](tasks/05-chat-api/summary.md)

---

## Задача 06: react-agent-skeleton 📋

### Цель

LangChain ReAct-агент (без business tools) подключён к chat API: вызов OpenAI, SSE-события reasoning/token/done.

> 💡 **Скиллы:** `fastapi-templates`, `python-design-patterns`

### Состав работ

- [ ] Реализовать `app/agent/core.py` — ReAct agent с пустым/минимальным toolset
- [ ] Реализовать `app/agent/prompts.py` — system prompt LLMStart Agent
- [ ] Интегрировать agent invoke в chat endpoint (web SSE + telegram JSON)
- [ ] Стриминг SSE: `reasoning`, `token`, `done`; fallback при ошибке OpenAI
- [ ] Сохранение user/assistant messages в Session
- [ ] Mock OpenAI в тестах; smoke с реальным ключом — manual
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Chat с mock LLM возвращает reply и обновляет session | pytest |
| 2 | SSE содержит `done` с session_id и reply | pytest |
| 3 | OpenAI error → fallback message, `error: true` | pytest |
| 4 | `make ci` проходит | `make ci` |

**Пользователь проверяет:**

- Реальный запрос с OPENAI_API_KEY → осмысленный ответ агента
- История видна через `GET /api/v1/sessions/{id}`

### Артефакты

- `backend/app/agent/core.py`
- `backend/app/agent/prompts.py`
- `backend/app/api/chat.py` — wiring agent
- `backend/tests/test_agent.py`, `backend/tests/test_chat_api.py` (расширение)

### Документы

- 📋 [План задачи](tasks/06-react-agent-skeleton/plan.md)
- 📝 [Summary](tasks/06-react-agent-skeleton/summary.md)

---

## Итог (заполняется после закрытия)

—
