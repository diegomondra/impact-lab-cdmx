# Deploy container for the Marimo notebooks.
# Chosen so the same image can serve any notebook via $MARIMO_NOTEBOOK —
# primary entry is notebooks/tus_100_pesos.py once Agent 3 has it landing;
# falls back to notebooks/budget_dashboard.py so the image is never broken.

FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

COPY notebooks ./notebooks
COPY data/clean ./data/clean
COPY scripts ./scripts

ENV MARIMO_NOTEBOOK=notebooks/budget_dashboard.py \
    PORT=8080

EXPOSE 8080

CMD uv run marimo run "$MARIMO_NOTEBOOK" \
    --host 0.0.0.0 \
    --port "$PORT" \
    --headless \
    --no-token
