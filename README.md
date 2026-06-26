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
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` | Ключи проекта в [Langfuse Cloud](https://cloud.langfuse.com) |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` (по умолчанию) |
| `BACKEND_API_KEY` | Shared secret для frontend и bot |
| `TELEGRAM_BOT_TOKEN` | Токен от [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_BOT_USERNAME` | Username бота без `@` (для deep link в виджете) |

Ключи Langfuse: Project Settings → API Keys в cloud UI.

### 2. Запустить стек локально

```bash
make dev
```

| Сервис | URL |
|--------|-----|
| Frontend (виджет) | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Langfuse traces | https://cloud.langfuse.com |
| Telegram bot | long polling (без порта) |

Проверка backend: `curl http://localhost:8000/health` → `"langfuse": "ok"`.

### 3. Docker Compose (стек в контейнерах)

```bash
make up
# или с пересборкой:
docker compose up -d --build
```

Сервисы: `backend`, `frontend`, `bot`. Langfuse — в облаке, не в compose.

## Команды Make

```bash
make dev           # backend + frontend + bot локально
make up            # docker compose: backend + frontend + bot
make down          # остановить compose
make up-langfuse   # опционально: self-hosted Langfuse локально
make down-langfuse # остановить локальный Langfuse
make dev-backend   # только backend :8000
make dev-frontend  # только frontend :3000
make dev-bot       # только bot (backend должен быть запущен)
make test          # все тесты
make ci            # полный CI-цикл
```

## Структура проекта

```
backend/     # Agent Core — FastAPI, ReAct, RAG, sessions
frontend/    # Next.js виджет — SSE, reasoning/tools UI
bot/         # Telegram adapter — aiogram, long polling
data/        # База знаний (b2b/b2c) и leads.txt
infra/       # Опциональный self-hosted Langfuse (make up-langfuse)
docs/        # Архитектура, спринты, ADR
```

## Сценарии

1. **Web:** откройте http://localhost:3000 → диалог с агентом → SSE streaming.
2. **Handoff:** после ответа агента нажмите «Перейти в Telegram» → продолжите диалог в боте с сохранённой историей.
3. **Telegram:** напишите боту напрямую → B2C/B2B воронка через `channel=telegram`.
4. **Observability:** traces агента смотрите в Langfuse Cloud после каждого диалога.

## Документация

- [Архитектура](docs/concept/architecture.md)
- [API контракты](docs/concept/api-contracts.md)
- [Roadmap](docs/roadmap.md)
