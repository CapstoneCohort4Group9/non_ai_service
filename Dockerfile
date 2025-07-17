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
ENV AWS_REGION: us-east-1
ENV DB_MIN_CONNECTIONS: 5
ENV DB_MAX_CONNECTIONS: 20
ENV DB_HOST: hopjetair-postgres.cepc0wqo22hd.us-east-1.rds.amazonaws.com
ENV DB_NAME: hopjetairline_db
ENV DB_PORT: 5432
ENV DB_USER: hopjetair
ENV DB_PASS: SecurePass123!
ENV DB_SECRET_NAME: db_credentials

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8003/health || exit 1

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8003"]