# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

WORKDIR /app/bot

COPY bot/pyproject.toml ./
RUN uv sync --no-dev --no-install-project

COPY bot/ ./
RUN uv sync --no-dev

FROM python:3.14-slim-bookworm AS runtime

RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

COPY --from=builder --chown=appuser:appuser /app/bot /app/bot

ENV PATH="/app/bot/.venv/bin:$PATH"
WORKDIR /app/bot

USER appuser

CMD ["python", "-m", "bot.main"]
