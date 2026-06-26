.PHONY: up down up-langfuse down-langfuse dev dev-backend dev-frontend dev-bot lint lint-backend lint-frontend lint-bot format format-backend format-frontend typecheck typecheck-bot test test-backend test-frontend test-bot ci

up:
	docker compose up -d

down:
	docker compose down

up-langfuse:
	docker compose -f infra/langfuse/docker-compose.yml up -d

down-langfuse:
	docker compose -f infra/langfuse/docker-compose.yml down

dev:
	@echo "Starting backend, frontend, and bot (Ctrl+C stops all)..."
	trap 'kill 0' EXIT INT TERM; \
	$(MAKE) dev-backend & \
	$(MAKE) dev-frontend & \
	$(MAKE) dev-bot & \
	wait

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && pnpm dev

dev-bot:
	cd bot && uv run python -m bot.main

lint: lint-backend lint-frontend lint-bot

lint-backend:
	cd backend && uv run ruff check .

lint-frontend:
	cd frontend && pnpm lint

lint-bot:
	cd bot && uv run ruff check .

format: format-backend format-frontend format-bot

format-backend:
	cd backend && uv run ruff format .

format-frontend:
	cd frontend && pnpm format

format-bot:
	cd bot && uv run ruff format .

typecheck: typecheck-backend typecheck-bot

typecheck-backend:
	cd backend && uv run mypy app tests

typecheck-bot:
	cd bot && uv run mypy bot tests

test: test-backend test-frontend test-bot

test-backend:
	cd backend && uv run pytest -v

test-frontend:
	cd frontend && pnpm test

test-bot:
	cd bot && uv run pytest -v

ci: lint typecheck test-backend lint-frontend test-frontend test-bot
