# Sprint 04: telegram-bot

> **Версия roadmap:** v0.1 — MVP
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** 📋 Planned
> **Открыт:** —
> **Закрыт:** —

---

## Цель спринта

Telegram-бот (aiogram) как тонкий адаптер к backend API, handoff из виджета с сохранением контекста, docker-compose для полного локального стека — `make dev` поднимает backend + frontend + bot + Langfuse.

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `make up` поднимает Langfuse + зависимости (из корня) | `curl http://localhost:3001` → 200; `curl http://localhost:8000/health` после backend |
| 2 | `make dev` поднимает backend + frontend + bot | все три процесса работают; bot отвечает в Telegram |
| 3 | Текстовое сообщение в бот → `POST /api/v1/chat` (`channel=telegram`) → HTML-ответ | manual: бот отвечает осмысленно |
| 4 | Handoff B2C-6: deep link из виджета → `/start session_{uuid}` → история сохранена | manual: продолжить диалог в Telegram с контекстом |
| 5 | B2C flow end-to-end через Telegram: продукт → мок-оплата → лид | manual + `data/leads.txt` |
| 6 | B2B flow end-to-end через Telegram: RAG → лид | manual |
| 7 | docker-compose: healthcheck на backend; bot restart policy | `docker compose ps` → healthy |
| 8 | `make ci` проходит (backend + frontend + bot tests) | exit 0 |
| 9 | STU-1: студент поднимает стек по README, проходит сценарий | manual checklist |

---

## Scope

### В scope

| Область | Что делаем |
|---------|-----------|
| **Bot scaffold** | `bot/` — Python 3.14 (минимум `>=3.12`), uv, aiogram 3.x, long polling |
| **Handlers** | `/start` (с парсингом `session_{uuid}`), текстовые сообщения |
| **Backend client** | `backend_client.py` — `POST /api/v1/chat`, Bearer auth, timeout |
| **HTML formatter** | Markdown → Telegram HTML (bold, code, links) |
| **Config** | `TELEGRAM_BOT_TOKEN`, `BACKEND_URL`, `BACKEND_API_KEY` — fail fast |
| **docker-compose** | Корневой `docker-compose.yml`: backend, frontend, bot, langfuse (reuse `infra/langfuse/`) |
| **Makefile** | `up`, `down`, `dev`, `dev-bot`, `test-bot`; `ci` включает bot tests |
| **Handoff** | Bot при `/start session_{uuid}` отправляет handoff message в backend |
| **Tests** | Unit: html_formatter, start parser; integration: backend_client с mock httpx |
| **Docs** | Root README: quick start `make dev`; обновить `.env.example` |

### Вне scope

- Webhook mode (только long polling для local dev)
- Inline keyboards, payment buttons в Telegram
- Production deploy (VPS, CI/CD)
- Guardrails — sprint-05
- Per-user auth — sprint-06
- PostgreSQL для сессий — roadmap TBD

---

## Шаги реализации

### 1. Bot scaffold

- [ ] Инициализировать `bot/` через uv: Python 3.14 (`.python-version`), `requires-python = ">=3.12"`; aiogram 3.x, httpx, pydantic-settings, pytest
- [ ] Структура по [architecture.md](../../concept/architecture.md): `main.py`, `handlers/`, `backend_client.py`, `html_formatter.py`, `config.py`
- [ ] `make dev-bot` — запуск long polling
- [ ] Smoke-тест: bot module imports, config validation

> 💡 **Скиллы:** `modern-python`, `uv-package-manager`

### 2. Config и backend client

- [ ] `bot/config.py` — `TELEGRAM_BOT_TOKEN`, `BACKEND_URL`, `BACKEND_API_KEY`; fail fast при старте
- [ ] `bot/backend_client.py` — async `chat(session_id, message, channel="telegram")` → `{session_id, reply, error?}`
- [ ] Timeout 60s; обработка network errors → fallback message
- [ ] Unit-тесты client с httpx mock

> 💡 **Скиллы:** `python-design-patterns`, `python-testing-patterns`, `sharp-edges`
> **Ref:** [api-contracts.md](../../concept/api-contracts.md)

### 3. HTML formatter

- [ ] `bot/html_formatter.py` — Markdown → Telegram HTML subset
- [ ] Экранирование `<`, `>`, `&`; поддержка `**bold**`, `` `code` ``, ссылки
- [ ] Unit-тесты: типовые ответы агента с markdown

> 💡 **Скиллы:** `python-testing-patterns`

### 4. Handlers — /start и messages

- [ ] `handlers/start.py` — `/start` без args: приветствие; `/start session_{uuid}`: handoff
- [ ] Handoff: `POST /api/v1/chat` с `message="/start session_{uuid}"`, `channel=telegram`, `session_id=null`
- [ ] In-memory mapping `telegram_chat_id → session_id` (dict в процессе бота)
- [ ] `handlers/messages.py` — текст → backend с сохранённым `session_id`
- [ ] Ответ: `sendMessage` с `parse_mode=HTML`
- [ ] Обработка `error: true` в ответе backend

> 💡 **Скиллы:** `python-design-patterns`
> **Ref:** [user-scenarios.md](../../concept/user-scenarios.md) — B2C-6

### 5. Bot entry point

- [ ] `bot/main.py` — Dispatcher, routers, startup logging (version, backend URL)
- [ ] Graceful shutdown (SIGINT)
- [ ] Логирование: chat_id, session_id — без текста сообщений

> 💡 **Скиллы:** `modern-python`

### 6. docker-compose — полный стек

- [ ] Корневой `docker-compose.yml` с сервисами: `backend`, `frontend`, `bot`, langfuse stack
- [ ] Langfuse: include/extends из `infra/langfuse/docker-compose.yml` или merge services
- [ ] `backend`: Dockerfile multi-stage, healthcheck `GET /health`, env from `.env`
- [ ] `frontend`: Dockerfile, port 3000, env `BACKEND_URL=http://backend:8000`
- [ ] `bot`: Dockerfile, depends_on backend healthy, no exposed port
- [ ] Volumes: `data/` mount для leads и knowledge base
- [ ] Networks: internal bridge

> 💡 **Скиллы:** `docker-expert`

### 7. Makefile — единая точка входа

- [ ] `make up` — `docker compose up -d` (langfuse + опционально весь стек)
- [ ] `make down` — `docker compose down`
- [ ] `make dev` — backend + frontend + bot локально (parallel или `docker compose` profile)
- [ ] `make dev-bot` — только bot (backend уже запущен)
- [ ] `make test-bot` — pytest в `bot/`
- [ ] `make ci` — lint + typecheck + test-backend + test-frontend + test-bot
- [ ] Согласовать с [10-conventions.mdc](../../../.cursor/rules/methodology/10-conventions.mdc)

### 8. Dockerfiles

- [ ] `backend/Dockerfile` — multi-stage: uv sync → slim runtime, non-root user
- [ ] `frontend/Dockerfile` — pnpm build → standalone Next.js output
- [ ] `bot/Dockerfile` — аналогично backend, entrypoint `python -m bot.main` или `uv run`
- [ ] `.dockerignore` для каждого сервиса

> 💡 **Скиллы:** `docker-expert`

### 9. End-to-end сценарии (manual verification)

- [ ] **Прямой Telegram:** новый пользователь → B2C воронка → лид
- [ ] **Handoff B2C-6:** виджет → «Перейти в Telegram» → продолжение с историей
- [ ] **B2B:** корпоративный запрос → RAG → лид
- [ ] **ADM-1:** trace в Langfuse после диалога через бот
- [ ] **STU-1:** `make dev` с нуля по README

> **Ref:** [user-scenarios.md](../../concept/user-scenarios.md)

### 10. Документация и CI

- [ ] Обновить корневой `README.md` — quick start: clone → `.env` → `make up` → `make dev`
- [ ] Дополнить `.env.example` всеми переменными bot + compose
- [ ] `make ci` green
- [ ] Обновить [roadmap.md](../../roadmap.md): v0.1 MVP ✅
- [ ] Обновить sprint README: статус ✅, итог

---

## Зависимости

| Зависимость | Откуда |
|-------------|--------|
| Backend API (chat JSON, handoff parsing) | Sprint 01–02 |
| Python runtime | 3.14 (`backend/.python-version`, `bot/.python-version`), минимум `>=3.12` |
| Web widget + TelegramHandoff deep link | Sprint 03 |
| Langfuse stack | `infra/langfuse/` (sprint-02) |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME` | `.env` + [@BotFather](https://t.me/BotFather) |
| Concept docs, ADRs | `docs/concept/`, `docs/adrs/` |

---

## Риски и допущения

| Риск | Митигация |
|------|-----------|
| In-memory `chat_id → session_id` теряется при рестарте бота | Допустимо для MVP; handoff повторяем |
| Telegram HTML parse errors | Fallback: plain text без parse_mode |
| docker-compose сложность (langfuse deps) | Reuse `infra/langfuse/`; profile `full` vs `observability-only` |
| Long polling + hot reload | `make dev-bot` отдельно от compose в dev |
| CORS не нужен для bot | Bot — server-to-server |

---

## Артефакты (ожидаемые)

```
bot/
├── main.py
├── config.py
├── backend_client.py
├── html_formatter.py
├── handlers/
│   ├── __init__.py
│   ├── start.py
│   └── messages.py
├── tests/
│   ├── test_html_formatter.py
│   ├── test_start_handler.py
│   └── test_backend_client.py
├── pyproject.toml
├── .python-version       # 3.14
└── Dockerfile
docker-compose.yml           # корень: backend, frontend, bot, langfuse
backend/Dockerfile
frontend/Dockerfile
Makefile                     # up, down, dev, dev-bot, test-bot, ci
README.md                    # quick start
```

---

## Связанные документы

- [architecture.md](../../concept/architecture.md) — bot structure, docker-compose services
- [api-contracts.md](../../concept/api-contracts.md) — telegram channel, handoff message format
- [user-scenarios.md](../../concept/user-scenarios.md) — B2C-6, STU-1, ADM-1
- [integrations.md](../../concept/integrations.md) — Telegram Bot API, env
- [infra/langfuse/README.md](../../../infra/langfuse/README.md) — Langfuse local setup

---

## Итог (заполняется после закрытия)

_Не заполнено._

**Следующий этап roadmap:** v0.2 — [sprint-05 safety-guardrails](../../roadmap.md) (планируется отдельно).
