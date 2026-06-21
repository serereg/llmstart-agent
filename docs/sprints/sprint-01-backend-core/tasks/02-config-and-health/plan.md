# Task 02: config-and-health

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/backend-2-config-health`
> **Spec:** без spec — [api-contracts.md](../../../../concept/api-contracts.md), [integrations.md](../../../../concept/integrations.md)

---

## Цель

Fail-fast конфигурация из переменных окружения и эндпоинт `GET /health` с проверкой критических зависимостей (OpenAI, Langfuse).

---

## Состав работ

- [ ] Реализовать `Settings` в `app/config.py` (pydantic-settings): все env из integrations.md
- [ ] Fail fast при старте: отсутствие обязательных переменных → понятная ошибка с именем переменной
- [ ] Singleton/get_settings dependency для DI
- [ ] Создать `.env.example` в корне репозитория со всеми переменными и комментариями
- [ ] Реализовать `GET /health` в `app/api/health.py` (без auth)
- [ ] Async probes: OpenAI (models list или lightweight call), Langfuse (health/ping endpoint)
- [ ] Ответ 200 `status: ok` / 503 `status: degraded` по api-contracts.md
- [ ] Тесты: mock probes ok/degraded; config validation
- [ ] Самопроверка по критериям DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Запуск без `OPENAI_API_KEY` → fail fast | manual / pytest |
| 2 | `GET /health` без auth → 200 | `curl http://localhost:8000/health` |
| 3 | При недоступном Langfuse → 503 degraded | pytest с mock probe |
| 4 | `.env.example` полный | code review |
| 5 | Lint + tests | `make ci` |

---

## Артефакты

- `backend/app/config.py` — Settings class, get_settings()
- `backend/app/api/health.py` — health router + dependency probes
- `backend/app/api/router.py` — подключить health router (без auth prefix)
- `.env.example` — шаблон env
- `backend/tests/test_health.py`
- `backend/tests/test_config.py`

---

## Scope

**Трогаем:** config, health, router wiring, `.env.example`, тесты.

**НЕ трогаем:**
- Auth middleware — task 03
- Chat/sessions endpoints — tasks 04–06
- Langfuse callback/tracing — sprint-02
- docker-compose — sprint-04

---

## Риски и допущения

- Langfuse может быть недоступен при первом запуске без `make up` — health показывает degraded, но config keys всё равно обязательны
- OpenAI probe не должен тратить tokens — использовать минимальный API call
- Version берётся из pyproject.toml или константы `0.1.0`

---

## Открытые вопросы

- [ ] Нет — контракт health зафиксирован в api-contracts.md
