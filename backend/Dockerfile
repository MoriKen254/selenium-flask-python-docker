FROM python:3.11-slim

# Build arguments for proxy configuration (optional)
# Pass these at build time: docker build --build-arg HTTP_PROXY=http://proxy:port ...
ARG HTTP_PROXY=""
ARG HTTPS_PROXY=""
ARG NO_PROXY="localhost,127.0.0.1"

# Set proxy environment variables only if provided
ENV http_proxy="${HTTP_PROXY}"
ENV https_proxy="${HTTPS_PROXY}"
ENV no_proxy="${NO_PROXY}"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
