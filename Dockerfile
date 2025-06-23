# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY app/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Create /data directory for persistent storage (Railway best practice)
RUN mkdir -p /data

# Expose port 5000
EXPOSE 5000

# Set environment variable for database path (Railway will mount /data)
ENV DATABASE_URL=/data/inventory.db

# Start the app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "wsgi:app"]
