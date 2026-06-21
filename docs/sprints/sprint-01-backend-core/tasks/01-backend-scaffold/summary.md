# Summary: Task 01 — backend-scaffold

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-06-21

---

## Что реализовано

- `backend/pyproject.toml` — зависимости (FastAPI, uvicorn, pydantic-settings, httpx), dev-группа (pytest, ruff, mypy), ruff `select = ["ALL"]`, mypy strict, pytest config
- `backend/uv.lock` — зафиксированные версии зависимостей (создаётся `uv sync`)
- `backend/app/main.py` — FastAPI app с lifespan, CORS placeholder (`localhost:3000`), подключение `api_router`
- `backend/app/api/router.py` — пустой `APIRouter` (агрегатор для будущих роутеров)
- `backend/app/config.py` — заглушка (на момент закрытия task 01; реализован в task 02)
- `backend/app/__init__.py`, `backend/app/api/__init__.py` — пакетная структура
- `Makefile` — цели `dev-backend`, `lint`, `format`, `typecheck`, `test`, `test-backend`, `ci`
- `backend/tests/conftest.py` — fixture `TestClient`
- `backend/tests/test_app.py` — smoke-тесты: импорт app, `GET /docs` → 200
- `backend/tests/__init__.py` — пакет tests (требование ruff)

---

## Отклонения от плана

- Python **3.14.2** вместо 3.12 — локально установлен только 3.14; `requires-python = ">=3.12"` сохранён
- Добавлен `backend/tests/__init__.py` — требование ruff (`INP001`) для implicit namespace package
- Добавлены `[build-system]` и `[tool.hatch.build.targets.wheel]` — editable install через uv для корректного импорта `app` в тестах
- Виртуальное окружение `backend/.venv/` создаётся `uv sync --group dev` (поведение uv по умолчанию, не отдельный артефакт плана)

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| `create_app()` factory + module-level `app` | Тесты используют изолированный экземпляр через fixture; uvicorn — `app.main:app` | — |
| CORS placeholder с `localhost:3000` | Соответствует architecture.md; полная настройка — в task 02/05 | — |
| `pythonpath = ["."]` в pytest | Простой импорт `app` без дополнительных env-переменных | — |
| Команды через `uv run` в Makefile | Соглашение проекта: package manager = uv, единая точка входа — make | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| `uv sync` долго скачивал Python 3.12 | Использован локальный Python 3.14.2 (`.python-version` → `3.14`) |
| Dev-зависимости не устанавливались при первом `uv sync` | Явный `uv sync --group dev` |
| `ModuleNotFoundError: app` в pytest | `pythonpath = ["."]` + hatchling wheel config для editable install |
| Ruff `INP001` в tests/ | Добавлен `tests/__init__.py` |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `make dev-backend` поднимает сервер | ✅ `curl http://localhost:8000/docs` → 200 |
| 2 | Структура каталогов соответствует architecture.md | ✅ `app/main.py`, `app/config.py`, `app/api/router.py`, `tests/` |
| 3 | Smoke-тест проходит | ✅ `make test-backend` — 2 passed |
| 4 | Lint проходит | ✅ `make lint` — All checks passed |
| 5 | Typecheck проходит | ✅ `make typecheck` — Success |

---

## Что дальше

- **Task 02: config-and-health** — fail-fast конфиг из env, `GET /health`
- CORS и auth — в task 02/03

---

## Ссылки

- [architecture.md](../../../../concept/architecture.md) — структура backend
- [Task 02 plan](../02-config-and-health/plan.md) — следующая задача спринта
- [.methodology/ci/git-conventions.md](../../../../../.methodology/ci/git-conventions.md) — `.venv/` и `.uv/` в gitignore
