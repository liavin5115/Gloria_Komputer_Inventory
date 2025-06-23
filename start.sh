#!/bin/sh
set -e

echo "Checking database directory..."
mkdir -p /data
chmod 777 /data

echo "Initializing database..."
python init_db.py || {
    echo "Database initialization failed"
    exit 1
}

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
