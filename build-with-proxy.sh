#!/bin/bash
# Build Docker images with proxy configuration from .env.build file
# This script reads proxy settings from .env.build and passes them as build arguments

set -e

echo "========================================"
echo "Building Docker Images with Proxy Config"
echo "========================================"
echo ""

# Check if .env.build exists
if [ ! -f ".env.build" ]; then
    echo "[WARNING] .env.build file not found"
    if [ -f ".env.build.example" ]; then
        echo "Creating from .env.build.example..."
        cp .env.build.example .env.build
        echo "[INFO] Created .env.build - please edit it with your proxy settings"
        echo ""
    else
        echo "[ERROR] .env.build.example not found"
        exit 1
    fi
fi

# Read proxy settings from .env.build
echo "Reading proxy configuration from .env.build..."
export $(grep -v '^#' .env.build | xargs)

echo "HTTP_PROXY=${HTTP_PROXY}"
echo "HTTPS_PROXY=${HTTPS_PROXY}"
echo "NO_PROXY=${NO_PROXY}"
echo ""

# Build with docker-compose using build args
echo "Building all services with docker-compose..."
docker-compose build \
    --build-arg HTTP_PROXY="${HTTP_PROXY}" \
    --build-arg HTTPS_PROXY="${HTTPS_PROXY}" \
    --build-arg NO_PROXY="${NO_PROXY}"

echo ""
echo "[SUCCESS] Build completed successfully"
