# Project Name
AI Lead Qualification System

## What it does
Automate manual lead scoring with a LangGraph multi-agent pipeline

## Stack
FastAPI · PostgreSQL · SQLAlchemy · Alembic · Python 3.13

## Setup
\```bash
uv sync
cp .env.example .env
# Fill in your .env values

alembic upgrade head
uv run uvicorn app.main:app --reload
\```

## Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |

## Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | PostgreSQL connection string |
| MISTRAL_API_KEY | No | For LLM features |