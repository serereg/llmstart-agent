.PHONY: dev-backend dev-frontend lint lint-frontend format format-frontend typecheck test test-backend test-frontend ci

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && pnpm dev

lint: lint-backend lint-frontend

lint-backend:
	cd backend && uv run ruff check .

lint-frontend:
	cd frontend && pnpm lint

format: format-backend format-frontend

format-backend:
	cd backend && uv run ruff format .

format-frontend:
	cd frontend && pnpm format

typecheck:
	cd backend && uv run mypy app tests

test: test-backend test-frontend

test-backend:
	cd backend && uv run pytest -v

test-frontend:
	cd frontend && pnpm test

ci: lint typecheck test-backend lint-frontend test-frontend
