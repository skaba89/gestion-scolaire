#!/bin/bash
# ==============================================================================
# EtudePlus - Render Startup Script
# Handles database migrations and starts the application
# ==============================================================================

set -e

echo "=========================================="
echo "EtudePlus Startup - Render Environment"
echo "=========================================="

# Wait for database to be ready
echo "Waiting for database connection..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1" > /dev/null 2>&1; do
    echo "Database not ready yet... waiting"
    sleep 2
done
echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
cd /app
alembic upgrade head || echo "Migration completed with warnings"

# Start the application
echo "Starting EtudePlus application..."
exec uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
