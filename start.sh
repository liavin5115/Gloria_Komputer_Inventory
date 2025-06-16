#!/bin/sh
set -e

echo "Checking database directory..."
if [ ! -d "/app/instance" ]; then
    echo "Creating instance directory..."
    mkdir -p /app/instance
    chmod 777 /app/instance
fi

echo "Using existing database..."
if [ -f "/app/instance/inventory.db" ]; then
    echo "Database exists, skipping initialization"
else
    echo "Database not found, this should not happen in production!"
    exit 1
fi

echo "Starting Gunicorn..."
exec gunicorn \
    --workers ${GUNICORN_WORKERS:-4} \
    --threads ${GUNICORN_THREADS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --bind ${GUNICORN_BIND:-0.0.0.0:5000} \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    "run:app"
