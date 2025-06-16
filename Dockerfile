# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    FLASK_ENV=production \
    GUNICORN_WORKERS=4 \
    GUNICORN_THREADS=2 \
    GUNICORN_TIMEOUT=120 \
    GUNICORN_BIND=0.0.0.0:5000

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn

# Copy project
COPY . .

# Create volume directory
RUN mkdir -p /app/instance \
    && chmod 777 /app/instance

# Copy healthcheck script
COPY docker-healthcheck.py /usr/local/bin/docker-healthcheck
RUN chmod +x /usr/local/bin/docker-healthcheck

# Healthcheck configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["python", "/usr/local/bin/docker-healthcheck"]

# Run with gunicorn
CMD ["gunicorn", "--workers", "$GUNICORN_WORKERS", "--threads", "$GUNICORN_THREADS", \
     "--timeout", "$GUNICORN_TIMEOUT", "--bind", "$GUNICORN_BIND", \
     "--access-logfile", "-", "--error-logfile", "-", \
     "--log-level", "info", "run:create_app()"]
