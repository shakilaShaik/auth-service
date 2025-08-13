#!/bin/bash
set -eo pipefail

# Configuration
MAX_RETRIES=30
RETRY_DELAY=2

echo "🚀 Starting application initialization..."

wait_for_db() {
    echo "🔍 Checking database connection to ${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME} with SSL..."
    for ((i=1; i<=MAX_RETRIES; i++)); do
        echo "   (Attempt ${i}/${MAX_RETRIES})"
        echo "PG password is: $DB_PASSWORD"

        if PGPASSWORD="$DB_PASSWORD" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            "sslmode=require" \
            -c '\q' >/dev/null 2>&1; then
            echo "✅ Database connection established"
            return 0
        fi

        echo "⌛ Database not ready, retrying in ${RETRY_DELAY}s..."
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
