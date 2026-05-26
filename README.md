# MedRelay (Python)

Medical event CAD dispatch system — Python port of MedRelay (Laravel), built with FastAPI, Jinja2, SQLAlchemy, MySQL, and Server-Sent Events for realtime updates.

## Requirements

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- Node.js 22+ (frontend assets)
- MySQL 8.x (production / local)

## Setup

```bash
cp .env.example .env
# Edit DATABASE_URL and SECRET_KEY

uv sync
uv run alembic upgrade head
uv run medrelay user-create

npm install
npm run build
```

## Development

```bash
uv run uvicorn medrelay.main:app --reload --host 0.0.0.0 --port 8000
# In another terminal:
npm run dev
```

Open http://localhost:8000

## Tests

```bash
uv run pytest
```

Tests use SQLite in-memory (`APP_ENV=testing`).

## Docker (production)

```bash
docker compose -f docker-compose.prod.yml up --build
```

Set `SECRET_KEY`, `DB_PASSWORD`, and `MYSQL_ROOT_PASSWORD` in your environment.

## Stack

| Layer | Technology |
|-------|------------|
| Web | FastAPI + Jinja2 |
| ORM | SQLAlchemy 2 + Alembic |
| DB | MySQL 8 |
| Realtime | SSE (native EventSource) |
| Frontend | Tailwind CSS 4, DaisyUI, Alpine.js, Vite |
| Tests | pytest |
