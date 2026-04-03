#!/usr/bin/env bash
set -e

export DATABASE_URL="sqlite:////app/inventory.db"

# Load service configuration
source /app/service.conf

echo "[start.sh] Running database migrations..."
cd /app
alembic -c /app/alembic.ini upgrade head

echo "[start.sh] Starting inventory service on ${SERVICE_HOST}:${SERVICE_PORT}..."
exec uvicorn main:app --host "${SERVICE_HOST}" --port "${SERVICE_PORT}"
