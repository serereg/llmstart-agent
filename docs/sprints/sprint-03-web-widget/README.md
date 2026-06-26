# Sprint 03: web-widget

> **Версия roadmap:** v0.1 — MVP
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-06-26
> **Закрыт:** 2026-06-26

---

## Цель спринта

Standalone Next.js виджет: чат с агентом через SSE, отображение reasoning и tool calls в реальном времени, кнопка handoff в Telegram — end-to-end B2C/B2B сценарии через браузер.

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `make dev-frontend` поднимает виджет на `:3000` | `curl -s -o /dev/null -w '%{http_code}' http://localhost:3000` → 200 |
| 2 | Отправка сообщения → SSE-стрим: `reasoning`, `tool_start`, `tool_end`, `token`, `done` | manual: UI + Network tab; vitest SSE parser |
| 3 | История сообщений отображается; `session_id` сохраняется в localStorage | manual: перезагрузка страницы → история восстановлена |
| 4 | Панель AgentActivity показывает шаги ReAct и вызванные tools | manual: B2C-2 запрос → видны tool cards |
| 5 | Кнопка «Перейти в Telegram» — deep link `https://t.me/{bot}?start=session_{uuid}` | manual: ссылка содержит текущий session_id (B2C-6) |
| 6 | `BACKEND_API_KEY` не попадает в браузерный bundle | inspect bundle / Route Handler proxy |
| 7 | B2C flow end-to-end через виджет: продукт → мок-оплата → лид | manual + `data/leads.txt` |
| 8 | `make lint`, `make test-frontend`, `make ci` проходят | exit 0 |

---

## Scope

### В scope

| Область | Что делаем |
|---------|-----------|
| **Scaffold** | `frontend/` — Next.js 16 App Router, pnpm, Tailwind 4, shadcn/ui, TypeScript strict |
| **API client** | Server Route Handler proxy → `POST /api/v1/chat`; SSE consumer (`reasoning`, `tool_*`, `token`, `error`, `done`) |
| **Chat UI** | `ChatWindow`, `MessageList`, input, loading/streaming states |
| **AgentActivity** | Collapsible панель: шаги reasoning, tool_start/tool_end с name/args/result |
| **Session** | `session_id` в localStorage; опционально restore через `GET /api/v1/sessions/{id}` |
| **TelegramHandoff** | Кнопка с deep link; `TELEGRAM_BOT_USERNAME` из env (server-side) |
| **Makefile** | `dev-frontend`, `lint` (eslint), `test-frontend` (vitest), расширение `ci` |
| **CORS** | Backend уже поддерживает `CORS_ORIGINS`; proxy снимает необходимость CORS для chat |
| **Tests** | Unit: SSE parser, types; component smoke (MessageList, AgentActivity) |
| **Env** | Дополнить `.env.example`: `NEXT_PUBLIC_*` только для публичных URL, ключ — server-only |

### Вне scope

- Telegram-бот (реализация handoff на стороне бота) — sprint-04
- docker-compose, `make dev` (полный стек) — sprint-04
- Embeddable script для llmstart.ru — roadmap TBD
- Guardrails / safety UI — sprint-05
- Per-user auth — sprint-06

---

## Шаги реализации

### 1. Frontend scaffold

- [x] Инициализировать `frontend/` через pnpm: Next.js 16, React 19, Tailwind 4, TypeScript strict
- [x] Подключить shadcn/ui (Button, Input, ScrollArea, Collapsible, Card)
- [x] Структура каталогов по [architecture.md](../../concept/architecture.md): `app/`, `components/chat/`, `lib/`
- [x] Добавить в корневой `Makefile`: `dev-frontend`, `lint-frontend`, `test-frontend`, `format-frontend`
- [x] Smoke-тест: страница рендерится

> 💡 **Скиллы:** `nextjs-app-router-patterns`, `shadcn`, `modern-python` (только Makefile-цели)

### 2. Types и SSE client

- [x] `lib/types.ts` — ChatRequest, SSE events (`ReasoningEvent`, `ToolStartEvent`, `ToolEndEvent`, `TokenEvent`, `DoneEvent`, `ErrorEvent`)
- [x] `lib/sse-parser.ts` — парсинг `event:` / `data:` из ReadableStream
- [x] Unit-тесты parser: success stream, error stream, partial chunks

> 💡 **Скиллы:** `vercel-react-best-practices`
> **Ref:** [api-contracts.md](../../concept/api-contracts.md)

### 3. Server-side API proxy

- [x] `app/api/chat/route.ts` — Route Handler: принимает `{session_id, message}`, добавляет `channel: web`, проксирует в backend с `Authorization: Bearer`
- [x] Стриминг ответа backend → клиент без буферизации (pass-through SSE)
- [x] Env: `BACKEND_URL`, `BACKEND_API_KEY` — только server-side (`process.env`, не `NEXT_PUBLIC_`)
- [x] Обработка 401/404/422 → JSON error для UI

> 💡 **Скиллы:** `nextjs-app-router-patterns`, `api-design-principles`, `sharp-edges`

### 4. Session management

- [x] `lib/session.ts` — get/set `session_id` в localStorage
- [x] При mount: если есть сохранённый id → `GET /api/sessions/[id]` (proxy) для restore истории
- [x] `app/api/sessions/[id]/route.ts` — proxy к `GET /api/v1/sessions/{id}`

> 💡 **Скиллы:** `vercel-react-best-practices`

### 5. Chat UI components

- [x] `components/chat/ChatWindow.tsx` — orchestrator: input, send, streaming state
- [x] `components/chat/MessageList.tsx` — user/assistant bubbles, markdown render (assistant)
- [x] `components/chat/ChatInput.tsx` — textarea + send button, disabled while streaming
- [x] `app/page.tsx` — layout: чат + боковая/нижняя панель AgentActivity
- [x] Стилизация: чистый dev-виджет, пригодный для ADM-2 (демо на занятии)

> 💡 **Скиллы:** `frontend-design`, `shadcn`, `web-design-guidelines`

### 6. AgentActivity panel

- [x] `components/chat/AgentActivity.tsx` — список reasoning steps и tool invocations
- [x] `tool_start` → card с name + args; `tool_end` → result (truncate long JSON)
- [x] Collapsible: свёрнута по умолчанию на mobile, развёрнута на desktop
- [x] Очистка activity при новом сообщении пользователя

> 💡 **Скиллы:** `vercel-react-best-practices`

### 7. Telegram handoff

- [x] `components/chat/TelegramHandoff.tsx` — кнопка «Перейти в Telegram»
- [x] Deep link: `https://t.me/${TELEGRAM_BOT_USERNAME}?start=session_${sessionId}`
- [x] Кнопка disabled пока нет `session_id` (до первого `done`)
- [x] Env `TELEGRAM_BOT_USERNAME` — server component или API route (не в client bundle)

> 💡 **Скиллы:** `nextjs-app-router-patterns`
> **Ref:** [user-scenarios.md](../../concept/user-scenarios.md) — B2C-6

### 8. Error handling и UX

- [x] SSE `error` event → toast/banner «Сервис временно недоступен»
- [x] Network failure → понятное сообщение, retry
- [x] Пустой input → disabled send
- [x] Max message length 4000 — client-side validation

### 9. End-to-end сценарии (manual verification)

- [x] **B2C-1…B2C-5:** вопрос → продукт → оплата → лид через виджет
- [x] **B2B-1…B2B-3:** корпоративный запрос → RAG → лид
- [x] **B2C-6:** handoff link генерируется с корректным session_id
- [x] **ADM-2:** reasoning/tools видны в реальном времени на проекторе

> **Ref:** [user-scenarios.md](../../concept/user-scenarios.md)

### 10. CI и самопроверка

- [x] `make lint-frontend`, `make test-frontend` — green
- [x] `make ci` — backend + frontend
- [x] Обновить sprint README: статус ✅, итог

---

## Зависимости

| Зависимость | Откуда |
|-------------|--------|
| Backend API (chat SSE, sessions) | Sprint 01–02 |
| Backend runtime | Python 3.14 (`backend/.python-version`), минимум `>=3.12` |
| `BACKEND_API_KEY`, `BACKEND_URL` | `.env` |
| `TELEGRAM_BOT_USERNAME` | `.env` (для deep link; бот — sprint-04) |
| Langfuse traces | Sprint 02 (для ADM-1 при тестировании) |
| Concept docs | `docs/concept/` |

---

## Риски и допущения

| Риск | Митигация |
|------|-----------|
| API key в client bundle | Только Route Handler proxy; проверка `next build` output |
| SSE buffering в Next.js | `export const dynamic = 'force-dynamic'`; ReadableStream pass-through |
| Длинные tool results ломают UI | Truncate + expand в AgentActivity |
| localStorage недоступен (SSR) | Проверка `typeof window`; session создаётся при первом ответе |

---

## Артефакты (ожидаемые)

```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── api/
│       ├── chat/route.ts
│       └── sessions/[id]/route.ts
├── components/
│   ├── chat/
│   │   ├── ChatWindow.tsx
│   │   ├── MessageList.tsx
│   │   ├── ChatInput.tsx
│   │   ├── AgentActivity.tsx
│   │   └── TelegramHandoff.tsx
│   └── ui/              # shadcn
├── lib/
│   ├── api-client.ts
│   ├── sse-parser.ts
│   ├── session.ts
│   └── types.ts
├── __tests__/
│   └── sse-parser.test.ts
└── package.json
Makefile                   # + dev-frontend, lint-frontend, test-frontend
```

---

## Связанные документы

- [architecture.md](../../concept/architecture.md) — frontend structure, SSE protocol
- [api-contracts.md](../../concept/api-contracts.md) — SSE events, auth proxy pattern
- [user-scenarios.md](../../concept/user-scenarios.md) — B2C-2 (tools UI), B2C-6 (handoff)
- [integrations.md](../../concept/integrations.md) — env variables

---

## Итог (заполняется после закрытия)

Standalone Next.js виджет на `:3000`: чат с SSE-стримингом, панель AgentActivity (reasoning + tools), восстановление сессии из localStorage, кнопка handoff в Telegram. API-ключ backend — только в server-side Route Handlers.

**Summary:** [summary.md](./summary.md)

**Следующий спринт:** [sprint-04-telegram-bot](../sprint-04-telegram-bot/README.md) — aiogram бот, docker-compose, `make dev`, E2E.
