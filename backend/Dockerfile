# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy pyproject.toml and install package
COPY pyproject.toml .
COPY src/ ./src/
RUN pip install -e .

# Copy initialization files
COPY init.sql .

# Create non-root user for security
RUN groupadd -r todouser && useradd -r -g todouser todouser

# Create htmlcov directory with proper permissions
RUN mkdir -p /app/htmlcov && chown -R todouser:todouser /app

USER todouser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Use the CLI entry point
CMD ["todo-api", "--host", "0.0.0.0", "--port", "5000"]
