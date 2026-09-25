# Use official lightweight Python runtime
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first for efficient layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code, data, and tests
COPY app/ ./app/
COPY data/ ./data/
COPY tests/ ./tests/

# Create a non-privileged user for security
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Expose the API port
EXPOSE 8000

# Container healthcheck using standard Python library
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start FastAPI application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
