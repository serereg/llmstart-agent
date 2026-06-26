# Summary: Sprint 02 — agent-rag

> **Sprint README:** [README.md](./README.md)
> **Дата закрытия:** 2026-06-26

---

## Что реализовано

- `data/b2b/`, `data/b2c/` — seed MD (3 документа на audience): corporate-training, custom-development, enterprise-packages; agents-course, llm-fundamentals, rag-workshop
- `data/b2c/products.json` — каталог B2C продуктов (`id`, `name`, `description`, `price_rub`, `duration_weeks`, `level`)
- `data/leads.txt` — файл для append лидов; `data/.gitkeep`
- `backend/app/rag/indexer.py` — загрузка MD/PDF, chunking, Chroma in-memory index
- `backend/app/rag/retriever.py` — similarity search с filter `audience`
- `backend/app/rag/store.py` — startup hook `init_rag_index()`, singleton retriever
- `backend/app/tools/` — `search_knowledge_base`, `list_b2c_products`, `create_payment_link`, `confirm_payment`, `save_lead`; `context.py` для session-scoped state; `registry.py`
- `backend/app/agent/core.py` — ReAct agent с business tools, Langfuse tracing, SSE `tool_start`/`tool_end`
- `backend/app/agent/prompts.py` — сегментация B2B/B2C, инструкции воронки
- `backend/app/observability/langfuse.py` — Langfuse client + LangChain callback handler
- `infra/langfuse/` — docker-compose для self-hosted Langfuse v3
- `backend/tests/test_rag.py`, `test_tools.py`, `test_agent_integration.py` — unit + integration
- `backend/tests/conftest.py` — изоляция `LANGFUSE_HOST` в тестовом окружении

---

## Формат `data/b2c/products.json`

Массив объектов:

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string | Уникальный slug продукта (используется в `create_payment_link`) |
| `name` | string | Название курса |
| `description` | string | Краткое описание |
| `price_rub` | number | Цена в рублях |
| `duration_weeks` | number | Длительность в неделях |
| `level` | string | Уровень: `beginner` / `intermediate` |

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| Seed data — только MD, без PDF | Достаточно для MVP; PDF loader реализован, но seed-файлы MD |
| Langfuse — `infra/langfuse/` вместо общего `make up` | Полный docker-compose стека — sprint-04; отдельный compose для observability |
| Langfuse host — cloud или self-hosted | `LANGFUSE_HOST` настраивается через `.env`; manual check на cloud Langfuse |

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| Chroma in-memory, rebuild при старте | MVP; без персистентного vector store | — |
| Tools обновляют Session через `contextvars` | Session store sync; tools не получают session_id в args от LLM | [ADR-0003](../../adrs/0003-mock-payments-crm.md) |
| Mock payments в Session, не внешний API | Учебный проект; воронка end-to-end без Stripe | [ADR-0003](../../adrs/0003-mock-payments-crm.md) |
| `astream_events` → SSE tool events | Нативные `on_tool_start` / `on_tool_end` из LangGraph | [api-contracts.md](../../concept/api-contracts.md) |
| Langfuse callback в `RunnableConfig` | Trace metadata: session_id, channel, segment | [integrations.md](../../concept/integrations.md) |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| `make ci` падал: `LANGFUSE_HOST` из `.env` протекал в тесты | Добавлен `LANGFUSE_HOST` в `TEST_ENV` в `conftest.py` |
| Embeddings API в тестах | `FakeEmbeddings` + monkeypatch `init_rag_index` в conftest |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | RAG: `search_knowledge_base` с filter audience | ✅ pytest + manual |
| 2 | `list_b2c_products` | ✅ pytest |
| 3 | `create_payment_link`, `confirm_payment` — pending → paid | ✅ pytest |
| 4 | `save_lead` → `data/leads.txt` | ✅ pytest |
| 5 | ReAct + сценарии B2C/B2B | ✅ manual (curl/chat) |
| 6 | Langfuse traces в UI | ✅ manual |
| 7 | SSE `tool_start`, `tool_end` | ✅ pytest |
| 8 | `make ci` | ✅ 53 теста, lint + mypy green |

---

## Что дальше

- [Sprint 03 — web-widget](../sprint-03-web-widget/README.md): Next.js виджет, SSE UI, reasoning/tools, Telegram handoff
- Segment detection quality — улучшение в sprint-05 guardrails

---

## Ссылки

- [architecture.md](../../concept/architecture.md)
- [user-scenarios.md](../../concept/user-scenarios.md)
- [ADR-0001](../../adrs/0001-react-agent-core.md), [ADR-0003](../../adrs/0003-mock-payments-crm.md)
- [infra/langfuse/README.md](../../../infra/langfuse/README.md)
