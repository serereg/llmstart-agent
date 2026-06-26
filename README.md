# LLMStart Agent

Мультиканальный AI-ассистент для llmstart.ru: веб-виджет (Next.js), Telegram-бот (aiogram) и Agent Core (FastAPI + ReAct + RAG).

## Быстрый старт

### 1. Клонировать и настроить окружение

```bash
git clone <repo-url> llmstart-agent
cd llmstart-agent
cp .env.example .env
```

Заполните `.env`:

| Переменная | Описание |
|------------|----------|
| `OPENAI_API_KEY` | Ключ LLM API |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` | Ключи Langfuse (см. `make up`) |
| `BACKEND_API_KEY` | Shared secret для frontend и bot |
| `TELEGRAM_BOT_TOKEN` | Токен от [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_BOT_USERNAME` | Username бота без `@` (для deep link в виджете) |

### 2. Поднять Langfuse

```bash
make up
```

Langfuse UI: http://localhost:3001 (логин: `admin@local.dev` / `langfuse-local-dev`).

Скопируйте ключи из UI или используйте значения из `infra/langfuse/README.md`.

### 3. Запустить весь стек локально

```bash
make dev
```

| Сервис | URL |
|--------|-----|
| Frontend (виджет) | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Langfuse | http://localhost:3001 |
| Telegram bot | long polling (без порта) |

Проверка backend: `curl http://localhost:8000/health`

### 4. Docker Compose (полный стек в контейнерах)

```bash
docker compose up -d --build
```

Сервисы: `backend`, `frontend`, `bot` + Langfuse stack.

## Команды Make

```bash
make up            # Langfuse + зависимости (docker compose up -d)
make down          # Остановить compose
make dev           # backend + frontend + bot локально
make dev-backend   # только backend :8000
make dev-frontend  # только frontend :3000
make dev-bot       # только bot (backend должен быть запущен)
make test          # все тесты
make test-bot      # pytest в bot/
make lint          # ruff + eslint
make typecheck     # mypy (backend + bot)
make ci            # полный CI-цикл
```

## Структура проекта

```
backend/     # Agent Core — FastAPI, ReAct, RAG, sessions
frontend/    # Next.js виджет — SSE, reasoning/tools UI
bot/         # Telegram adapter — aiogram, long polling
data/        # База знаний (b2b/b2c) и leads.txt
infra/       # Langfuse docker-compose
docs/        # Архитектура, спринты, ADR
```

## Сценарии

1. **Web:** откройте http://localhost:3000 → диалог с агентом → SSE streaming.
2. **Handoff:** после ответа агента нажмите «Перейти в Telegram» → продолжите диалог в боте с сохранённой историей.
3. **Telegram:** напишите боту напрямую → B2C/B2B воронка через `channel=telegram`.

## Документация

- [Архитектура](docs/concept/architecture.md)
- [API контракты](docs/concept/api-contracts.md)
- [Roadmap](docs/roadmap.md)
