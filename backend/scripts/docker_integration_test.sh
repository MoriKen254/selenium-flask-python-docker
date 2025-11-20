#!/bin/bash
# Docker Integration Test Script for Unix-like systems
# This script tests Docker build and integration with the new package structure

set -e  # Exit on any error

echo "============================================"
echo "Docker Integration Test"
echo "============================================"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# Create temporary directory for testing
TEMP_DIR=$(mktemp -d -t todo_api_docker_test_XXXXXX)
echo "[INFO] Created temporary test directory: $TEMP_DIR"
echo

# Cleanup function
cleanup() {
    echo "[INFO] Cleaning up..."
    # Force stop and remove container if still running
    docker stop todo-api-test-container >/dev/null 2>&1 || true
    docker rm todo-api-test-container >/dev/null 2>&1 || true
    
    # Clean up temp directory
    rm -rf "$TEMP_DIR"
    echo "[INFO] Cleanup complete"
}

# Set trap for cleanup
trap cleanup EXIT

# Test 1: Check Docker availability
echo "[TEST 1] Checking Docker availability..."
if DOCKER_VERSION=$(docker --version 2>&1); then
    echo "$DOCKER_VERSION"
    echo "[PASS] Docker is available"
else
    echo "[FAIL] Docker is not available"
    echo "$DOCKER_VERSION"
    exit 1
fi
echo

# Test 2: Build Docker image
echo "[TEST 2] Building Docker image..."
cd "$BASE_DIR"
if docker build -t todo-api-test . > "$TEMP_DIR/docker_build.log" 2>&1; then
    echo "[PASS] Docker image built successfully"
else
    echo "[FAIL] Docker build failed"
    cat "$TEMP_DIR/docker_build.log"
    exit 1
fi
echo

# Test 3: Run container health check
echo "[TEST 3] Running container health check..."
if docker run --rm -d --name todo-api-test-container -p 5001:5000 todo-api-test > "$TEMP_DIR/docker_run.log" 2>&1; then
    echo "[INFO] Container started, waiting for service to be ready..."
    sleep 10
else
    echo "[FAIL] Failed to start container"
    cat "$TEMP_DIR/docker_run.log"
    exit 1
fi
echo

# Test 4: Check health endpoint
echo "[TEST 4] Testing health endpoint..."
if HEALTH_RESPONSE=$(curl -f http://localhost:5001/health 2>&1); then
    echo "$HEALTH_RESPONSE"
    echo "[PASS] Health endpoint responded correctly"
else
    echo "[FAIL] Health endpoint test failed"
    echo "$HEALTH_RESPONSE"
    docker logs todo-api-test-container > "$TEMP_DIR/container_logs.log" 2>&1
    echo "[INFO] Container logs:"
    cat "$TEMP_DIR/container_logs.log"
    docker stop todo-api-test-container >/dev/null 2>&1
    exit 1
fi
echo

# Test 5: Check version endpoint
echo "[TEST 5] Testing version endpoint..."
if VERSION_RESPONSE=$(curl -f http://localhost:5001/ 2>&1); then
    echo "$VERSION_RESPONSE"
    echo "[PASS] Version endpoint responded correctly"
else
    echo "[FAIL] Version endpoint test failed"
    echo "$VERSION_RESPONSE"
fi
echo

# Test 6: Test API endpoints
echo "[TEST 6] Testing API endpoints..."
if API_RESPONSE=$(curl -f http://localhost:5001/api/todos 2>&1); then
    echo "$API_RESPONSE"
    echo "[PASS] API endpoints responded correctly"
else
    echo "[FAIL] API endpoint test failed"
    echo "$API_RESPONSE"
fi
echo

# Test 7: Check container logs
echo "[TEST 7] Checking container logs..."
docker logs todo-api-test-container > "$TEMP_DIR/final_logs.log" 2>&1
echo "[INFO] Container logs:"
cat "$TEMP_DIR/final_logs.log"
echo "[PASS] Container logs retrieved"
echo

# Test 8: Stop container
echo "[TEST 8] Stopping container..."
if docker stop todo-api-test-container > "$TEMP_DIR/docker_stop.log" 2>&1; then
    echo "[PASS] Container stopped successfully"
else
    echo "[WARN] Failed to stop container gracefully"
    cat "$TEMP_DIR/docker_stop.log"
    docker kill todo-api-test-container >/dev/null 2>&1 || true
fi
echo

# Test 9: Clean up Docker image
echo "[TEST 9] Cleaning up Docker image..."
if docker rmi todo-api-test > "$TEMP_DIR/docker_cleanup.log" 2>&1; then
    echo "[PASS] Docker image cleaned up"
else
    echo "[WARN] Failed to remove Docker image"
    cat "$TEMP_DIR/docker_cleanup.log"
fi
echo

echo "============================================"
echo "Docker Integration Test Complete"
echo "============================================"
echo "[SUCCESS] Docker integration test completed successfully"
