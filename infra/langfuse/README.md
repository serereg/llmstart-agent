# Langfuse — optional self-hosted stack

> **По умолчанию** проект использует [Langfuse Cloud](https://cloud.langfuse.com).
> Локальный docker-compose нужен только если вы хотите self-hosted observability.

| Режим | `LANGFUSE_HOST` | Как поднять |
|-------|-----------------|-------------|
| **Cloud (default)** | `https://cloud.langfuse.com` | Ключи из cloud UI → `.env` |
| Self-hosted local | `http://localhost:3001` | `make up-langfuse` |

## Langfuse Cloud (рекомендуется)

1. Создайте проект на https://cloud.langfuse.com
2. Скопируйте API keys в корневой `.env`:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

3. Запустите backend: `make dev-backend`
4. Проверка: `curl -s http://localhost:8000/health` → `"langfuse": "ok"`

## Self-hosted local (опционально)

| Сервис | URL |
|--------|-----|
| Langfuse UI | http://localhost:3001 |
| MinIO console | http://localhost:9091 |

```bash
make up-langfuse
```

Логин по умолчанию: `admin@local.dev` / `langfuse-local-dev`.

Ключи для `.env`:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-llmstart-local
LANGFUSE_SECRET_KEY=sk-lf-llmstart-local
LANGFUSE_HOST=http://localhost:3001
```

Остановка: `make down-langfuse`.

## Примечания

- Postgres проброшен на `127.0.0.1:5433` (не 5432), чтобы не конфликтовать с локальным PostgreSQL.
- Данные хранятся в Docker volumes (`langfuse_*`).
- Self-hosted production: [Langfuse self-hosting guide](https://langfuse.com/self-hosting).
