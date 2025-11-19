# ==============================
# FastAPI Service Dockerfile
# ==============================

FROM python:3.11-slim

# Set working directory to project root
WORKDIR /app

# Disable .pyc and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency list first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose FastAPI port (each service overrides this in docker-compose)
EXPOSE 8000

# Add optional healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8001/health || exit 1

# ✅ Correct entrypoint for your structure
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

