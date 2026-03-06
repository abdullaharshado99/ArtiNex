# Use Python 3.11 for consistent behavior with your lockfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for document processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first (better layer caching)
COPY requirements.txt .
COPY libraries/requirements.txt ./libraries/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY Anna_pipeline/ ./Anna_pipeline/
COPY endpoint.py pipeline.py .
COPY templates/ ./templates/
COPY static/ ./static/

# Set environment variables for production
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CHROMADB_TELEMETRY=0

EXPOSE $PORT

# Run with gunicorn optimized for RAG workloads
CMD gunicorn endpoint:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120
