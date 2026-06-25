# Roadmap — LLMStart Agent

> **Vision:** [./concept/vision.md](./concept/vision.md)
> **Последнее обновление:** 2026-06-21

---

## Цель продукта

**LLMStart Agent** — публичный AI-ассистент llmstart.ru: первая линия консультаций и продаж для B2C/B2B. Снижает нагрузку на поддержку, ведёт воронку до лида. Учебный проект курса с production-grade архитектурой.

---

## Легенда

- 📋 Planned — запланирован
- 🚧 In Progress — в работе
- ✅ Done — завершён
- ⏸ Paused — на паузе
- 🗄 Archived — отменён

---

## Версии / Этапы

### v0.1 — MVP: локальный мультиканальный агент 📋

**Цель:** Рабочий стенд — агент консультирует, продаёт (мок), собирает лиды через web + Telegram, с observability.

**Ключевые результаты:**
- [ ] Диалог B2C end-to-end: вопрос → продукт → мок-оплата → лид
- [ ] Диалог B2B: RAG по b2b-базе → лид
- [ ] Web-виджет со SSE + reasoning/tools
- [ ] Telegram-бот + handoff из виджета
- [ ] Traces в Langfuse
- [ ] `make dev` поднимает весь стек локально

**Спринты:**

| # | Sprint | Цель | Статус | Документ |
|---|--------|------|--------|----------|
| 01 | backend-core | FastAPI, config, sessions, health, auth, ReAct skeleton | ✅ | [sprint-01](sprints/sprint-01-backend-core/README.md) |
| 02 | agent-rag | Tools, RAG (Chroma), Langfuse, воронка (products, payment, leads) | 📋 | [sprint-02](sprints/sprint-02-agent-rag/README.md) |
| 03 | web-widget | Next.js, SSE, reasoning/tools UI, Telegram handoff | 📋 | [sprint-03](sprints/sprint-03-web-widget/README.md) |
| 04 | telegram-bot | aiogram, long polling, handoff, docker-compose, E2E | 📋 | [sprint-04](sprints/sprint-04-telegram-bot/README.md) |

---

### v0.2 — Safety & guardrails 📋

**Цель:** Безопасность и качество ответов — фильтрация off-topic, политики safety, защита от злоупотреблений.

**Ключевые результаты:**
- [ ] Guardrails: off-topic → «не знаю», без выдумывания услуг
- [ ] Safety-политики: запрещённый контент, prompt injection mitigation
- [ ] Метрики качества в Langfuse (отклонённые / flagged запросы)

**Спринты:**

| # | Sprint | Цель | Статус | Документ |
|---|--------|------|--------|----------|
| 05 | safety-guardrails | Guardrails, safety policies, тесты на edge cases | 📋 | — |

---

### v1.0 — Production: per-user auth 📋

**Цель:** Аутентификация пользователей вместо shared API key; готовность к production-развёртыванию.

**Ключевые результаты:**
- [ ] Per-user auth (JWT / session) для API и каналов
- [ ] Замена shared `BACKEND_API_KEY` на user-scoped tokens
- [ ] Production-деплой (VPS / CI/CD) — по согласованию
- [ ] Production-платежи и CRM — roadmap после auth

**Спринты:**

| # | Sprint | Цель | Статус | Документ |
|---|--------|------|--------|----------|
| 06 | user-auth | Per-user authentication, миграция с shared API key | 📋 | — |

---

## За пределами текущего roadmap

| Фича | Этап | Статус |
|------|------|--------|
| PostgreSQL (сессии, диалоги, лиды) | TBD | 📋 |
| Production-платежи | TBD | 📋 |
| CRM-интеграция | TBD | 📋 |
| Эскалация эксперту | TBD | 📋 |
| Embeddable widget для llmstart.ru | TBD | 📋 |
| Выдача доступа после оплаты | TBD | 📋 |

---

## История изменений

| Дата | Изменение |
|------|-----------|
| 2026-06-21 | Создан roadmap (онбординг concept → roadmap) |
