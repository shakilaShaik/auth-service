#!/bin/bash
set -eo pipefail

# Configuration
MAX_RETRIES=30
RETRY_DELAY=2

echo "🚀 Starting application initialization..."

wait_for_db() {
    echo "🔍 Checking database connection to ${POSTGRES_USER}@auth_db:5432/${POSTGRES_DB}"
    for ((i=1; i<=MAX_RETRIES; i++)); do
        if PGPASSWORD=$POSTGRES_PASSWORD psql -h auth_db -U $POSTGRES_USER -d $POSTGRES_DB -c '\q' >/dev/null 2>&1; then
            echo "✅ Database connection established"
            return 0
        fi
        echo "⌛ Database not ready (attempt ${i}/${MAX_RETRIES})..."
        sleep $RETRY_DELAY
    done
    echo "❌ Failed to connect to database after ${MAX_RETRIES} attempts"
    return 1
}

run_migrations() {
    echo "🔄 Running database migrations..."
    if alembic upgrade head; then
        echo "✅ Migrations completed successfully"
        return 0
    else
        echo "❌ Migration failed"
        return 1
    fi
}

start_app() {
    echo "🚀 Starting FastAPI application..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
}

# Main execution flow
wait_for_db && run_migrations && start_app

exit $?