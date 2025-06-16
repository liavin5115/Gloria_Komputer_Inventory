#!/bin/sh

# Start Gunicorn
exec gunicorn \
    --workers ${GUNICORN_WORKERS:-4} \
    --threads ${GUNICORN_THREADS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --bind ${GUNICORN_BIND:-0.0.0.0:5000} \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    "run:create_app()"
