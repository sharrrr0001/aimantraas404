# AI Mantraas Student Portal - Dockerfile
# =======================================
# Multi-stage build for production deployment

# Stage 1: Python dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production image
FROM python:3.11-slim

WORKDIR /app

# Install production dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    gunicorn \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Add local bin to PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application files (excluding .env and local-data)
COPY app.py .
COPY google_sheets.py .
COPY wsgi.py .
COPY requirements.txt .
COPY Procfile .
COPY runtime.txt .

# Create directories
RUN mkdir -p local-data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=app.py
ENV DEBUG_MODE=False

# Expose port
EXPOSE $PORT

# Run with Gunicorn (use dynamic port for cloud platforms)
CMD ["gunicorn", "--bind", ":$PORT", "--workers", "4", "--timeout", "120", "wsgi:application"]
