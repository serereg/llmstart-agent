# Plan: Sprint 04 — Telegram Bot

> **Статус:** In Progress
> **Спринт:** [README.md](../README.md)
> **Архитектура:** [architecture.md](../../../concept/architecture.md)

## Цель

Telegram-бот (aiogram) как тонкий адаптер к backend API: long polling, handoff из виджета, docker-compose для полного локального стека.

## Состав работ

1. Bot scaffold (`bot/`) — uv, aiogram 3.x, config, backend_client, html_formatter
2. Handlers — `/start` (greeting + handoff), текстовые сообщения
3. Entry point — `bot/main.py`, graceful shutdown
4. Tests — html_formatter, start parser, backend_client mock
5. Docker — Dockerfiles (backend, frontend, bot), корневой `docker-compose.yml`
6. Makefile — `up`, `down`, `dev`, `dev-bot`, `test-bot`, `ci`
7. Docs — root README, `.env.example` (уже актуален)

## DoD

| # | Критерий | Статус |
|---|----------|--------|
| 1 | `make up` поднимает Langfuse | ⬜ |
| 2 | `make dev` — backend + frontend + bot | ⬜ |
| 3 | Telegram → POST chat (channel=telegram) → HTML | ⬜ |
| 4 | Handoff deep link → история сохранена | ⬜ |
| 5 | B2C/B2B flow через Telegram | ⬜ manual |
| 6 | docker-compose healthcheck + restart | ⬜ |
| 7 | `make ci` green | ⬜ |
| 8 | Root README quick start | ⬜ |

## Scope

**В scope:** bot/, docker-compose, Dockerfiles, Makefile, tests, README
**Вне scope:** webhook, inline keyboards, production deploy, guardrails

## Артефакты

- `bot/` — полный пакет
- `docker-compose.yml` — backend, frontend, bot + langfuse
- `backend/Dockerfile`, `frontend/Dockerfile`, `bot/Dockerfile`
- `Makefile` — обновлённые цели
- `README.md` — quick start
