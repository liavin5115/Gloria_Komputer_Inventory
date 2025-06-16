#!/bin/sh
set -e

echo "Checking database directory..."
mkdir -p /app/instance
chmod 777 /app/instance

echo "Initializing database..."
python <<EOF
from app.src import create_app, db
from app.src.models.inventory import Inventory

app = create_app()

with app.app_context():
    try:
        db.create_all()
        print("Database tables created")
    except Exception as e:
        print(f"Database initialization error: {e}")
        print("Will continue anyway to allow for database setup...")
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
