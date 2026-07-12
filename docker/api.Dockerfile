# FastAPI Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for data factory
# - gcc: Compilation of Python extensions
# - postgresql-client: Database connectivity
# - libgomp1: OpenMP for ML libraries (SDV/numpy)
# - libhdf5-dev: HDF5 for data storage
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    libgomp1 \
    libhdf5-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY apps/api/requirements.txt .
COPY apps/api/requirements-docker.txt .

# Install Python dependencies (using docker-specific file with SDV)
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy application code
COPY apps/api/ .

# Create necessary directories for data factory
RUN mkdir -p /app/data/generated /app/data/uploads /app/data/models /app/logs

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
