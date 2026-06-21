.PHONY: dev-backend lint format typecheck test test-backend ci

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint:
	cd backend && uv run ruff check .

format:
	cd backend && uv run ruff format .

typecheck:
	cd backend && uv run mypy app tests

test: test-backend

test-backend:
	cd backend && uv run pytest -v

ci: lint typecheck test-backend
