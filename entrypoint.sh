#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Waiting for PostgreSQL session pool at $DB_HOST:$DB_PORT..."

# Wait until the database is reachable
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

echo "PostgreSQL is available. Running migrations..."
alembic upgrade head

echo "Starting FastAPI app..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
