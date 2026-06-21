# Task 01: backend-scaffold

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/backend-1-scaffold`
> **Spec:** без spec — [architecture.md](../../../../concept/architecture.md)

---

## Цель

Инициализирован Python-проект `backend/` с uv, Makefile, базовой структурой FastAPI и smoke-тестами — основа для всех последующих задач спринта.

---

## Состав работ

- [ ] Создать `backend/` через `uv init`, Python 3.12+
- [ ] Добавить зависимости: fastapi, uvicorn[standard], pydantic-settings, httpx, pytest, pytest-asyncio, ruff, mypy
- [ ] Настроить ruff (`select = ["ALL"]`, минимальный ignore) и mypy strict в `pyproject.toml`
- [ ] Создать структуру каталогов: `app/main.py`, `app/api/router.py`, `app/config.py` (заглушка), `tests/`
- [ ] Реализовать `app/main.py`: FastAPI app, lifespan, include router, CORS placeholder
- [ ] Создать корневой `Makefile` с целями: `dev-backend`, `lint`, `format`, `typecheck`, `test`, `test-backend`, `ci`
- [ ] Smoke-тест: app импортируется, TestClient возвращает 200 на `/docs`
- [ ] Самопроверка по критериям DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `make dev-backend` поднимает сервер | `curl http://localhost:8000/docs` → 200 |
| 2 | Структура каталогов соответствует architecture.md | code review |
| 3 | Smoke-тест проходит | `make test-backend` |
| 4 | Lint проходит | `make lint` |
| 5 | Typecheck проходит | `make typecheck` |

---

## Артефакты

- `backend/pyproject.toml` — зависимости, ruff, mypy, pytest config
- `backend/app/__init__.py`
- `backend/app/main.py` — FastAPI entry point
- `backend/app/api/__init__.py`, `backend/app/api/router.py` — пустой APIRouter
- `Makefile` — единая точка входа для dev/lint/test/ci
- `backend/tests/conftest.py` — TestClient fixture
- `backend/tests/test_app.py` — smoke-тест startup и /docs

---

## Scope

**Трогаем:** только файлы из списка «Артефакты» + корневой `Makefile`.

**НЕ трогаем:**
- Реализацию config, health, auth, sessions, chat, agent — следующие задачи
- frontend, bot, docker-compose — другие спринты
- `docs/` кроме ссылок в plan (не меняем concept)

---

## Риски и допущения

- Репозиторий пустой — scaffold с нуля, без миграции существующего кода
- `uv` установлен локально; при отсутствии — документировать в summary
- CORS настраивается полностью в task 02 или 05 — здесь только placeholder

---

## Открытые вопросы

- [ ] Нет — структура зафиксирована в architecture.md
