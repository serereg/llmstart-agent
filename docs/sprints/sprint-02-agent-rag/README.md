# Sprint 02: agent-rag

> **Версия roadmap:** v0.1 — MVP
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-06-22
> **Закрыт:** 2026-06-26

---

## Цель спринта

Агент с полным набором business tools, RAG по базе знаний B2B/B2C, observability в Langfuse и проходимая воронка: продукт → мок-оплата → лид — end-to-end через backend API.

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | RAG: `search_knowledge_base` возвращает релевантные chunks из `data/b2b/` и `data/b2c/` с фильтром audience | pytest + manual query |
| 2 | Tool `list_b2c_products` возвращает каталог B2C продуктов | pytest |
| 3 | Tools `create_payment_link`, `confirm_payment` — мок-воронка в Session | pytest: pending → paid |
| 4 | Tool `save_lead` пишет в `data/leads.txt` | pytest: файл содержит запись |
| 5 | ReAct-агент вызывает tools по сценариям B2C-2…B2C-5, B2B-2…B2B-3 | manual curl / pytest integration |
| 6 | Langfuse traces видны в UI (`http://localhost:3001`) для каждого chat invoke | manual: trace с steps и tools |
| 7 | SSE-стрим содержит `tool_start`, `tool_end` при вызовах tools (web channel) | pytest SSE parser |
| 8 | `make ci` проходит | `make ci` exit 0 |

---

## Scope

### В scope

| Область | Что делаем |
|---------|-----------|
| **RAG** | Индексация `data/b2b/`, `data/b2c/` (PDF, MD) в Chroma in-memory при startup; retrieval с metadata filter `audience` |
| **Tools** | `search_knowledge_base`, `list_b2c_products`, `save_lead`, `create_payment_link`, `confirm_payment` |
| **Agent** | Подключение tools к ReAct loop; system prompt с инструкциями воронки и сегментации |
| **Sessions** | Обновление segment (b2b/b2c), payment state через tools |
| **Observability** | Langfuse SDK + LangChain callback; traces на каждый invoke |
| **Data** | Seed-файлы knowledge base, каталог B2C products, `data/leads.txt` (gitkeep) |
| **Tests** | Unit tools, RAG indexer; integration agent+tools с mocks |

### Вне scope

- frontend, bot, docker-compose — sprint-03/04
- Guardrails / safety — sprint-05
- PostgreSQL, production CRM/payments — roadmap TBD
- Telegram handoff UI — sprint-03

---

## Шаги реализации

### 1. Knowledge base и seed data

- [x] Создать `data/b2b/`, `data/b2c/` с seed MD/PDF (минимум 2–3 документа на audience)
- [x] Создать `data/b2c/products.json` — каталог продуктов для `list_b2c_products`
- [x] Создать `data/leads.txt` (пустой) + `.gitkeep` если нужно
- [x] Документировать формат products в summary спринта

> 💡 **Скиллы:** `python-design-patterns`

### 2. RAG — Chroma in-memory

- [x] `app/rag/indexer.py` — загрузка PDF/MD, chunking, embeddings (`OPENAI_EMBEDDING_MODEL`)
- [x] `app/rag/retriever.py` — similarity_search с filter `audience: b2b | b2c`
- [x] Startup hook в lifespan: rebuild index при каждом старте backend
- [x] Unit-тесты indexer/retriever с mock embeddings

> 💡 **Скиллы:** `modern-python`, `python-testing-patterns`

### 3. Business tools

- [x] `app/tools/knowledge.py` — `search_knowledge_base(query, audience)` → formatted context
- [x] `app/tools/products.py` — `list_b2c_products()` → JSON каталог
- [x] `app/tools/payments.py` — `create_payment_link(product_id)`, `confirm_payment()` → update Session.payment
- [x] `app/tools/leads.py` — `save_lead(name, contact, product, segment)` → append `data/leads.txt`
- [x] Каждый tool — LangChain `@tool` decorator, typed args
- [x] Unit-тесты каждого tool (mock session store, temp leads file)

> 💡 **Скиллы:** `python-design-patterns`, `python-testing-patterns`
> **ADR:** [0003-mock-payments-crm](../../adrs/0003-mock-payments-crm.md)

### 4. Agent — tools + prompts

- [x] Расширить `app/agent/prompts.py`: сегментация B2B/B2C, сценарии воронки, когда вызывать tools
- [x] Подключить все tools к ReAct agent в `app/agent/core.py`
- [x] Agent определяет/фиксирует segment в Session (b2b/b2c)
- [x] Integration-тест: mock LLM с forced tool calls → session updated

> 💡 **Скиллы:** `fastapi-templates`
> **ADR:** [0001-react-agent-core](../../adrs/0001-react-agent-core.md)

### 5. Langfuse observability

- [x] Подключить Langfuse LangChain callback handler в agent invoke
- [x] Metadata trace: session_id, channel, segment
- [x] Убедиться, что backend стартует только с валидными Langfuse keys (уже в sprint-01 config)
- [x] Manual check: trace в Langfuse UI после chat request

> 💡 **Скиллы:** `sharp-edges`
> **Ref:** [integrations.md](../../concept/integrations.md)

### 6. Chat API — tool events в SSE

- [x] Расширить SSE stream: emit `tool_start`, `tool_end` при вызовах tools (web channel)
- [x] Callback/hook из LangChain agent events → SSE emitter
- [x] Integration-тест: SSE содержит tool events при mock tool call

> 💡 **Скиллы:** `api-design-principles`
> **Ref:** [api-contracts.md](../../concept/api-contracts.md)

### 7. End-to-end сценарии (manual verification)

- [x] **B2C flow:** вопрос → list_b2c_products / RAG → create_payment_link → confirm_payment → save_lead
- [x] **B2B flow:** корпоративный запрос → RAG b2b → save_lead
- [x] Проверить `data/leads.txt` и Session.payment.status после flow
- [x] Проверить traces в Langfuse

> **Ref:** [user-scenarios.md](../../concept/user-scenarios.md)

### 8. CI и самопроверка

- [x] `make lint`, `make typecheck`, `make test-backend` — green
- [x] `make ci` — full cycle
- [x] Обновить sprint README: статус ✅, итог

---

## Зависимости

| Зависимость | Откуда |
|-------------|--------|
| Backend scaffold, config, auth, sessions, chat API, ReAct skeleton | Sprint 01 |
| Langfuse running locally | `make up` (docker-compose — sprint-04; до этого manual docker) |
| LLM API credentials | `.env` (`OPENAI_API_KEY`, при необходимости `OPENAI_API_BASE`) |
| Concept docs, ADRs | `docs/concept/`, `docs/adrs/` |

---

## Риски и допущения

| Риск | Митигация |
|------|-----------|
| Chroma in-memory — индекс пересобирается при каждом рестарте | Допустимо для MVP; startup hook |
| Embeddings API cost | Минимальный seed data; кеш embeddings в dev |
| LangChain tool calling API changes | Pin versions в uv.lock |
| Segment detection качество | Явные инструкции в system prompt; улучшение в sprint-05 guardrails |

---

## Артефакты (ожидаемые)

```
backend/app/
├── agent/
│   ├── core.py          # + tools wiring
│   └── prompts.py       # + funnel instructions
├── tools/
│   ├── knowledge.py
│   ├── products.py
│   ├── payments.py
│   └── leads.py
├── rag/
│   ├── indexer.py
│   └── retriever.py
data/
├── b2b/                 # seed docs
├── b2c/                 # seed docs
├── b2c/products.json
└── leads.txt
backend/tests/
├── test_rag.py
├── test_tools.py
└── test_agent_integration.py
```

---

## Связанные документы

- [architecture.md](../../concept/architecture.md) — RAG flow, tools list
- [api-contracts.md](../../concept/api-contracts.md) — SSE tool events
- [user-scenarios.md](../../concept/user-scenarios.md) — B2C/B2B flows
- [integrations.md](../../concept/integrations.md) — LLM API, Langfuse
- [ADR-0001](../../adrs/0001-react-agent-core.md), [ADR-0003](../../adrs/0003-mock-payments-crm.md)

---

## Итог (заполняется после закрытия)

Backend Agent с полным business toolset и RAG:

- Chroma in-memory RAG по `data/b2b/` и `data/b2c/` с filter `audience`
- Tools: `search_knowledge_base`, `list_b2c_products`, `create_payment_link`, `confirm_payment`, `save_lead`
- ReAct agent вызывает tools; segment и payment state обновляются в Session
- Langfuse traces на каждый invoke (cloud или self-hosted через `LANGFUSE_HOST`)
- SSE web channel: `tool_start`, `tool_end` при вызовах tools
- B2C/B2B воронки проверены manual; `make ci` — 53 теста, lint + mypy green

**Summary:** [summary.md](./summary.md)

**Следующий спринт:** [sprint-03-web-widget](../sprint-03-web-widget/README.md) — Next.js виджет, SSE UI, Telegram handoff.
