#!/bin/sh
set -e

echo "Checking database directory..."
mkdir -p /app/instance
chmod 777 /app/instance

echo "Waiting for database directory to be ready..."
until [ -w /app/instance ]; do
    echo "Waiting for write permissions..."
    sleep 1
done

echo "Initializing database..."
python <<EOF
from app.src import create_app, db
app = create_app()
with app.app_context():
    try:
        db.create_all()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        exit(1)
EOF

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
