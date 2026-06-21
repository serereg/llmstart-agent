# ADR 0003 — Моки платежей и CRM

> **Статус:** ✅ Accepted
> **Дата:** 2026-06-21
> **Автор:** LLMStart Agent team
> **Область:** продукт LLMStart Agent
> **Supersedes:** —

---

## 1. Контекст

### 1.1 Текущая ситуация

Воронка агента включает оплату и сохранение лида. Реальные платёжные системы и CRM требуют договоров, секретов и compliance.

### 1.2 Что породило необходимость решения

Учебный проект с production-grade **архитектурой**, но без production **интеграций** на MVP.

---

## 2. Решение

**Принимаем: моки для платежей и CRM.**

### Платежи
- Tool `create_payment_link` — генерирует фиктивную ссылку (UUID / placeholder URL)
- Tool `confirm_payment` — принимает текстовое «оплатил», меняет status в сессии
- Без webhook'ов от платёжного провайдера

### CRM
- Tool `save_lead` — append в `data/leads.txt` (имя, контакт, продукт, segment, timestamp)
- Не CRM-система, не API HubSpot/AmoCRM

---

## 3. Последствия

### 4.1 Позитивные

- Полная воронка проходится end-to-end локально
- Tools и agent flow идентичны production-паттерну

### 4.2 Негативные (и митигация)

| Риск | Митигация |
|------|----------|
| Нет реальной оплаты | Roadmap: production-платёжка |
| leads.txt не масштабируется | Roadmap: Postgres + CRM |

---

## 4. Ссылки

- [`docs/concept/idea.md`](../concept/idea.md)
- [`docs/concept/user-scenarios.md`](../concept/user-scenarios.md)
