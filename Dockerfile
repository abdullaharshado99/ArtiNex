# Use Python 3.11 for consistent behavior with your lockfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
COPY libraries/requirements.txt ./libraries/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY endpoint.py .
COPY templates/ ./templates/
COPY static/ ./static/

# Railway sets PORT; default for local runs
ENV PORT=8080
EXPOSE $PORT

# Same Python that has gunicorn installed
CMD gunicorn endpoint:app --bind 0.0.0.0:$PORT
