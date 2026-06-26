# Summary: Sprint 03 — web-widget

> **Sprint README:** [README.md](./README.md)
> **Дата закрытия:** 2026-06-26

---

## Что реализовано

- `frontend/` — Next.js 16 App Router, React 19, Tailwind 4, TypeScript strict, pnpm (локальный `node_modules`)
- `frontend/components/ui/` — shadcn/ui-совместимые компоненты: Button, Input, Textarea, ScrollArea, Collapsible, Card
- `frontend/lib/types.ts` — ChatRequest, SessionResponse, SSE event types, ActivityItem
- `frontend/lib/sse-parser.ts` — парсинг `event:` / `data:` из ReadableStream, partial chunks
- `frontend/lib/api-client.ts` — клиент к Route Handlers + SSE consumer
- `frontend/lib/session.ts` — `session_id` в localStorage
- `frontend/lib/backend-config.ts` — server-only env (`BACKEND_URL`, `BACKEND_API_KEY`, `TELEGRAM_BOT_USERNAME`)
- `frontend/app/api/chat/route.ts` — proxy `POST /api/v1/chat` с SSE pass-through
- `frontend/app/api/sessions/[id]/route.ts` — proxy `GET /api/v1/sessions/{id}`
- `frontend/components/chat/` — ChatWindow, MessageList, ChatInput, AgentActivity, TelegramHandoff
- `frontend/__tests__/` — sse-parser (unit), MessageList, AgentActivity, page (smoke)
- Корневой `Makefile` — `dev-frontend`, `lint-frontend`, `test-frontend`, `format-frontend`; `ci` включает frontend
- `.env.example` — комментарии про server-only переменные frontend
- `frontend/next.config.ts` — загрузка корневого `.env` через `dotenv`

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| shadcn/ui подключён вручную (без `shadcn init`) | Быстрее и без интерактивного CLI; компоненты по паттерну shadcn |
| `dotenv` вместо `@next/env` | `@next/env` не резолвился при `next build`; `dotenv` загружает корневой `.env` |
| `pnpm-workspace.yaml` в `frontend/` с `allowBuilds` | pnpm 11 блокировал build scripts `sharp` / `unrs-resolver` без явного approve |
| B2C/B2B E2E через виджет — manual only | Автотесты покрывают parser и UI smoke; полный E2E с LLM — manual при запущенном backend |

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Route Handler proxy для chat/sessions | `BACKEND_API_KEY` не попадает в браузерный bundle |
| `export const dynamic = 'force-dynamic'` на API routes | SSE pass-through без буферизации |
| `TELEGRAM_BOT_USERNAME` передаётся из server component в client | Имя бота не в client bundle; deep link формируется на клиенте из prop |
| Корневой `.env` через `dotenv` в `next.config.ts` | Единый файл конфигурации для monorepo (backend + frontend) |
| AgentActivity: collapsed на mobile, expanded на desktop | `matchMedia` + Collapsible по DoD спринта |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| pnpm `ERR_PNPM_IGNORED_BUILDS` при `pnpm lint` / `pnpm test` | `frontend/pnpm-workspace.yaml` с `allowBuilds: sharp, unrs-resolver` |
| ESLint `react-hooks/set-state-in-effect` | Lazy `useState` init + async setState только в `.then()` / `.finally()` |
| `window.matchMedia` / `localStorage` в vitest | Моки в `vitest.setup.ts` |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `make dev-frontend` → `:3000` HTTP 200 | ✅ `curl` → 200 |
| 2 | SSE: reasoning, tool_*, token, done | ✅ UI + 7 unit-тестов parser |
| 3 | История + localStorage `session_id` | ✅ restore через `GET /api/sessions/[id]` |
| 4 | AgentActivity: ReAct steps и tools | ✅ |
| 5 | Telegram deep link `session_{uuid}` | ✅ |
| 6 | `BACKEND_API_KEY` не в client bundle | ✅ проверка `.next/static` |
| 7 | B2C flow E2E через виджет | ✅ manual (при `make dev-backend` + `make dev-frontend`) |
| 8 | `make lint`, `make test-frontend`, `make ci` | ✅ 12 frontend + 53 backend тестов |

---

## Что дальше

- [Sprint 04 — telegram-bot](../sprint-04-telegram-bot/README.md): aiogram бот, handoff handler, docker-compose, `make dev`
- Embeddable widget для llmstart.ru — roadmap TBD

---

## Ссылки

- [architecture.md](../../concept/architecture.md)
- [api-contracts.md](../../concept/api-contracts.md)
- [user-scenarios.md](../../concept/user-scenarios.md)
