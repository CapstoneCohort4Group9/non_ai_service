# Use official Python runtime as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
  gcc \
  libpq-dev \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and configuration
COPY app/ ./app/


# Set environment variable
ENV DATABASE_URL=postgresql+asyncpg://hopjetair:SecurePass123!@localhost:5432/hopjetair
ENV DB_MIN_CONNECTIONS=5
ENV DB_MAX_CONNECTIONS=20

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8003/health-deep || exit 1

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8003"]