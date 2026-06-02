# syntax=docker/dockerfile:1

FROM node:22-alpine AS frontend
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY frontend ./frontend
COPY vite.config.js ./
RUN npm run build

FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS app
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY --from=frontend /app/static/dist ./static/dist
COPY app ./app
COPY web.py ./web.py
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
HEALTHCHECK CMD curl -f http://127.0.0.1:8000/up || exit 1
CMD ["uvicorn", "web:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--timeout-keep-alive", "75"]
