#!/bin/bash
# ============================================================
# scripts/start.sh
# ============================================================
# Entrypoint for the Docker container. Runs in sequence:
# 1. Alembic migrations (create/update tables)
# 2. Seed data (idempotent — safe to run multiple times)
# 3. Uvicorn server
# ============================================================

set -e

echo "==> Running database migrations..."
alembic upgrade head

echo "==> Seeding database..."
python -m app.seed

echo "==> Starting TaskFlow API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info
