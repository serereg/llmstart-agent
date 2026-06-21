# API Contracts

> **Базовый URL:** `http://localhost:8000` (локально)
> **Версия API:** `v1` — все эндпоинты бизнес-логики по `/api/v1/...`

---

## Общие конвенции

### Версионирование

Все эндпоинты бизнес-логики: `/api/v1/...`
Служебные эндпоинты (`/health`): без версии.

### Формат запросов и ответов

- `Content-Type: application/json` (кроме SSE-ответа)
- Все тела — JSON, кодировка UTF-8.

### Формат ошибок

```json
{
  "detail": "Human-readable описание ошибки"
}
```

Для ошибок валидации (422):

```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "missing"
    }
  ]
}
```

### HTTP-коды

| Код | Смысл |
|-----|-------|
| 200 | Успешный ответ |
| 401 | Неверный или отсутствующий API-ключ |
| 404 | Сессия не найдена |
| 422 | Ошибка валидации схемы |
| 503 | Критическая зависимость недоступна (только `/health`) |

### Аутентификация

Все эндпоинты `/api/v1/*` требуют API-ключ. Эндпоинт `/health` — **без аутентификации** (docker healthcheck).

| Параметр | Значение |
|----------|----------|
| Механизм | Bearer token |
| Заголовок | `Authorization: Bearer <BACKEND_API_KEY>` |
| Переменная окружения | `BACKEND_API_KEY` — общий ключ для `frontend` и `bot` |
| MVP | Один shared secret; per-user auth — в roadmap |

**Клиенты:**

| Клиент | Как передаёт ключ |
|--------|-------------------|
| bot | `Authorization` header из env при каждом запросе к backend |
| frontend | Server-side proxy (Next.js Route Handler) или env на build; ключ **не** попадает в браузерный bundle |

При неверном ключе: `401 Unauthorized`:

```json
{
  "detail": "Invalid or missing API key"
}
```

### Режим ответа chat (SSE vs JSON)

Определяется полем `channel` в теле запроса:

| `channel` | Формат ответа | `Content-Type` |
|-----------|---------------|----------------|
| `web` | SSE-стрим | `text/event-stream` |
| `telegram` | JSON | `application/json` |

### Язык ответа

Явное поле `locale` **не передаётся**. Агент определяет язык (RU/EN) из текста сообщения пользователя.

---

## Сводная таблица эндпоинтов

| Метод | Путь | Auth | Успешный код | Сценарий |
|-------|------|:----:|:---:|---------|
| `POST` | `/api/v1/chat` | ✅ | 200 | Отправить сообщение агенту |
| `GET` | `/api/v1/sessions/{session_id}` | ✅ | 200 | Получить историю сессии |
| `GET` | `/health` | ❌ | 200 | Healthcheck + статус зависимостей |

---

## Эндпоинты

### POST /api/v1/chat

**Сценарий:** Отправка сообщения пользователя агенту. Для `channel=web` — SSE-стрим с reasoning, tools, tokens. Для `channel=telegram` — JSON с финальным ответом.

**Заголовки:**

| Заголовок | Обязательный | Описание |
|-----------|:---:|---------|
| `Authorization` | ✅ | `Bearer <BACKEND_API_KEY>` |
| `Content-Type` | ✅ | `application/json` |

**Запрос:**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Хочу научиться делать AI-агентов",
  "channel": "web"
}
```

| Поле | Тип | Обязательное | Описание |
|------|-----|:---:|---------|
| `session_id` | string (UUID) \| null | ❌ | ID сессии. `null` или отсутствие — backend создаёт новую сессию |
| `message` | string | ✅ | Текст сообщения пользователя. Max **4000** символов |
| `channel` | string | ✅ | `web` или `telegram` |

**Handoff виджет → Telegram:** bot отправляет как есть:

```json
{
  "session_id": null,
  "message": "/start session_550e8400-e29b-41d4-a716-446655440000",
  "channel": "telegram"
}
```

Backend парсит `session_{uuid}` из сообщения и привязывает Telegram chat к существующей Session.

---

#### Ответ для `channel=telegram` — JSON `200 OK`

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "reply": "Рекомендую начать с курса **agents**..."
}
```

| Поле | Тип | Описание |
|------|-----|---------|
| `session_id` | string (UUID) | ID сессии (новый или существующий) |
| `reply` | string | Текст ответа агента (Markdown; bot конвертирует в HTML) |
| `error` | boolean | `true` при fallback-ошибке (OpenAI недоступен). Optional, default `false` |

**Пример ошибки OpenAI (fallback):**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "reply": "Сервис временно недоступен, попробуйте позже",
  "error": true
}
```

HTTP-код остаётся **200** — ошибка передаётся через поле `error`.

---

#### Ответ для `channel=web` — SSE `200 OK`

`Content-Type: text/event-stream`

Формат каждого события:

```
event: <type>
data: <JSON>

```

| Event | Payload | Описание |
|-------|---------|----------|
| `reasoning` | `{"step": 1, "content": "..."}` | Шаг ReAct / промежуточное рассуждение |
| `tool_start` | `{"name": "search_knowledge_base", "args": {...}}` | Начало вызова tool |
| `tool_end` | `{"name": "search_knowledge_base", "result": "..."}` | Результат tool |
| `token` | `{"content": "фрагмент"}` | Фрагмент финального ответа |
| `error` | `{"message": "Сервис временно недоступен, попробуйте позже"}` | Fallback при ошибке OpenAI |
| `done` | `{"session_id": "uuid", "reply": "полный текст", "error": false}` | Завершение стрима |

**Пример стрима (успех):**

```
event: reasoning
data: {"step": 1, "content": "Пользователь интересуется курсами по агентам"}

event: tool_start
data: {"name": "list_b2c_products", "args": {}}

event: tool_end
data: {"name": "list_b2c_products", "result": "[{\"id\": \"agents\", ...}]"}

event: token
data: {"content": "Рекомендую"}

event: token
data: {"content": " курс agents"}

event: done
data: {"session_id": "550e8400-e29b-41d4-a716-446655440000", "reply": "Рекомендую курс agents", "error": false}

```

**Пример стрима (ошибка OpenAI):**

```
event: error
data: {"message": "Сервис временно недоступен, попробуйте позже"}

event: done
data: {"session_id": "550e8400-e29b-41d4-a716-446655440000", "reply": "Сервис временно недоступен, попробуйте позже", "error": true}

```

---

**Ошибки POST /api/v1/chat:**

| Код | Условие | Пример `detail` |
|-----|---------|-----------------|
| 401 | Нет или неверный API-ключ | `"Invalid or missing API key"` |
| 404 | `session_id` указан, но сессия не найдена | `"Session not found"` |
| 422 | Пустой `message` | `"field required"` |
| 422 | `message` > 4000 символов | `"Message exceeds maximum length of 4000 characters"` |
| 422 | Невалидный `channel` | `"channel must be 'web' or 'telegram'"` |

---

### GET /api/v1/sessions/{session_id}

**Сценарий:** Получить историю диалога и метаданные сессии (для восстановления UI виджета, отладки).

**Заголовки:**

| Заголовок | Обязательный | Описание |
|-----------|:---:|---------|
| `Authorization` | ✅ | `Bearer <BACKEND_API_KEY>` |

**Path-параметры:**

| Параметр | Тип | Описание |
|----------|-----|---------|
| `session_id` | string (UUID) | ID сессии |

**Ответ `200 OK`:**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "channel": "web",
  "segment": "b2c",
  "messages": [
    {
      "role": "user",
      "content": "Хочу научиться делать AI-агентов",
      "timestamp": "2026-06-21T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Рекомендую курс agents...",
      "timestamp": "2026-06-21T10:00:05Z"
    }
  ],
  "payment": {
    "status": "pending",
    "mock_link": null
  },
  "created_at": "2026-06-21T10:00:00Z",
  "updated_at": "2026-06-21T10:00:05Z"
}
```

| Поле | Тип | Описание |
|------|-----|---------|
| `session_id` | string | UUID сессии |
| `channel` | string | `web` или `telegram` |
| `segment` | string \| null | `b2b`, `b2c` или `null` если ещё не определён |
| `messages` | array | История сообщений user/assistant |
| `payment.status` | string | `none`, `pending`, `paid` |
| `payment.mock_link` | string \| null | Мок-ссылка на оплату |

**Ошибки:**

| Код | Условие | Пример `detail` |
|-----|---------|-----------------|
| 401 | Нет или неверный API-ключ | `"Invalid or missing API key"` |
| 404 | Сессия не найдена | `"Session not found"` |

---

### GET /health

**Сценарий:** Проверка работоспособности backend и критических зависимостей. **Без аутентификации.**

**Ответ `200 OK`** (все зависимости доступны):

```json
{
  "status": "ok",
  "version": "0.1.0",
  "dependencies": {
    "openai": "ok",
    "langfuse": "ok"
  }
}
```

**Ответ `503 Service Unavailable`** (хотя бы одна зависимость недоступна):

```json
{
  "status": "degraded",
  "version": "0.1.0",
  "dependencies": {
    "openai": "ok",
    "langfuse": "error"
  }
}
```

| Поле | Тип | Описание |
|------|-----|---------|
| `status` | string | `ok` — все deps доступны; `degraded` — есть проблемы |
| `version` | string | Версия из конфига / package |
| `dependencies.openai` | string | `ok` / `error` — probe к OpenAI API |
| `dependencies.langfuse` | string | `ok` / `error` — probe к Langfuse |

> Backend **не стартует** без валидного конфига Langfuse ([integrations.md](integrations.md)). `/health` probes актуальны при runtime-сбоях.

---

## Переменные окружения (auth)

| Переменная | Компонент | Описание |
|------------|-----------|----------|
| `BACKEND_API_KEY` | backend | Secret для проверки входящих запросов |
| `BACKEND_API_KEY` | bot, frontend | Тот же ключ для исходящих запросов к backend |

Добавить в `.env.example` вместе с остальными переменными из [integrations.md](integrations.md).

---

## Связанные документы

- [architecture.md](architecture.md) — SSE-протокол, потоки
- [integrations.md](integrations.md) — внешние системы, env
- [user-scenarios.md](user-scenarios.md) — сценарии B2C-6 (handoff)
