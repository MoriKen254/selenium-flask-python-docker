#!/bin/bash

# Comprehensive Test Runner
# Rebuilds images and runs all tests: backend unit, frontend unit, and integration tests

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo ""
    echo "========================================"
    echo -e "${BLUE}$1${NC}"
    echo "========================================"
    echo ""
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Track overall status
BACKEND_TESTS_PASSED=0
FRONTEND_UNIT_PASSED=0
FRONTEND_INTEGRATION_PASSED=0
OVERALL_SUCCESS=1

# Change to project root directory
cd "$(dirname "$0")/../.."

# Load proxy configuration from .env.build if it exists
if [ -f ".env.build" ]; then
    echo "[INFO] Loading proxy configuration from .env.build"
    export $(grep -v '^#' .env.build | xargs)
    echo "[INFO] Proxy: ${HTTP_PROXY}"
    BUILD_HTTP_PROXY="${HTTP_PROXY}"
    BUILD_HTTPS_PROXY="${HTTPS_PROXY}"
    BUILD_NO_PROXY="${NO_PROXY}"
else
    echo "[INFO] No .env.build found, building without proxy"
    BUILD_HTTP_PROXY=""
    BUILD_HTTPS_PROXY=""
    BUILD_NO_PROXY="localhost,127.0.0.1"
fi

print_header "Starting Comprehensive Test Suite"
echo "This will:"
echo "  1. Rebuild all Docker images"
echo "  2. Run backend unit tests (pytest with coverage)"
echo "  3. Run frontend unit tests (Selenium with mocked APIs)"
echo "  4. Run integration tests (Selenium with real backend)"
echo ""

# Step 1: Rebuild Docker images
print_header "Step 1/4: Rebuilding Docker Images"
echo "Stopping existing containers..."
docker-compose down

echo "Building fresh images with proxy configuration..."
if docker-compose build \
    --build-arg HTTP_PROXY="${BUILD_HTTP_PROXY}" \
    --build-arg HTTPS_PROXY="${BUILD_HTTPS_PROXY}" \
    --build-arg NO_PROXY="${BUILD_NO_PROXY}"; then
    print_success "Docker images rebuilt successfully"
else
    print_error "Failed to rebuild Docker images"
    exit 1
fi

# Step 2: Run Backend Unit Tests
print_header "Step 2/4: Backend Unit Tests (pytest with coverage)"
echo "Starting backend and database containers..."
docker-compose up -d backend postgres

echo "Waiting for backend to be ready..."
sleep 5

# Wait for backend health check
echo "Checking backend health..."
for i in {1..30}; do
    # Use --noproxy to bypass corporate proxy for localhost
    if curl -s --noproxy localhost http://localhost:5000/health > /dev/null 2>&1; then
        print_success "Backend is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Backend failed to start"
        exit 1
    fi
    sleep 1
done

echo "Running backend tests with coverage..."
if docker exec todo_backend pytest -v --cov=. --cov-report=html --cov-report=term; then
    print_success "Backend tests passed"
    BACKEND_TESTS_PASSED=1
else
    print_error "Backend tests failed"
    OVERALL_SUCCESS=0
fi

# Step 3: Run Frontend Unit Tests
print_header "Step 3/4: Frontend Unit Tests (Selenium with mocked APIs)"
echo "Starting frontend container..."
docker-compose up -d frontend

echo "Waiting for frontend to be ready..."
sleep 5

# Wait for frontend
for i in {1..30}; do
    # Use --noproxy to bypass corporate proxy for localhost
    if curl -s --noproxy localhost http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Frontend failed to start"
        exit 1
    fi
    sleep 1
done

cd tests

echo "Running frontend unit tests..."
# Use environment variables directly
TEST_MODE=unit \
FRONTEND_URL=http://frontend:3000 \
BROWSER=chrome \
HEADLESS=true \
pytest -v --html=test_reports/unit_report.html --self-contained-html -m "not integration"

if [ $? -eq 0 ]; then
    print_success "Frontend unit tests passed"
    FRONTEND_UNIT_PASSED=1
else
    print_error "Frontend unit tests failed"
    OVERALL_SUCCESS=0
fi

# Step 4: Run Integration Tests
print_header "Step 4/4: Integration Tests (Full E2E with real backend)"
echo "Ensuring all services are running..."
cd ..
docker-compose up -d

echo "Waiting for all services to be ready..."
sleep 5

cd tests

echo "Running integration tests..."
# Use environment variables directly instead of sourcing .env file
# This ensures proper database connectivity
TEST_MODE=integration \
FRONTEND_URL=http://frontend:3000 \
BACKEND_URL=http://backend:5000 \
DB_HOST=postgres \
DB_PORT=5432 \
POSTGRES_DB=tododb \
POSTGRES_USER=todouser \
POSTGRES_PASSWORD=todopass \
BROWSER=chrome \
HEADLESS=true \
pytest -v --html=test_reports/integration_report.html --self-contained-html

if [ $? -eq 0 ]; then
    print_success "Integration tests passed"
    FRONTEND_INTEGRATION_PASSED=1
else
    print_error "Integration tests failed"
    OVERALL_SUCCESS=0
fi

# Final Summary
print_header "Test Suite Summary"
echo ""
echo "Results:"
echo "--------"

if [ $BACKEND_TESTS_PASSED -eq 1 ]; then
    print_success "Backend Unit Tests: PASSED"
else
    print_error "Backend Unit Tests: FAILED"
fi

if [ $FRONTEND_UNIT_PASSED -eq 1 ]; then
    print_success "Frontend Unit Tests: PASSED"
else
    print_error "Frontend Unit Tests: FAILED"
fi

if [ $FRONTEND_INTEGRATION_PASSED -eq 1 ]; then
    print_success "Integration Tests: PASSED"
else
    print_error "Integration Tests: FAILED"
fi

echo ""
echo "Reports:"
echo "--------"
echo "Backend Coverage: backend/htmlcov/index.html"
echo "Frontend Unit: tests/test_reports/unit_report.html"
echo "Integration: tests/test_reports/integration_report.html"
echo ""

if [ $OVERALL_SUCCESS -eq 1 ]; then
    print_header "✓ ALL TESTS PASSED"
    exit 0
else
    print_header "✗ SOME TESTS FAILED"
    exit 1
fi
