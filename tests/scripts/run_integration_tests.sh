#!/bin/bash

# Run Integration Tests (Real APIs - Full System)
# Requires backend and database to be running

echo "========================================"
echo "Running INTEGRATION Tests (Real Backend)"
echo "========================================"

# Check if all required containers are running
if ! docker ps | grep -q "frontend" || ! docker ps | grep -q "backend" || ! docker ps | grep -q "postgres"; then
    echo "Not all containers running. Starting all services..."
    docker-compose up -d
    echo "Waiting for services to be ready..."
    sleep 10
fi

# Load integration test configuration
export $(cat .env.integration | xargs)

# Run pytest
pytest -v \
    --html=test_reports/integration_report.html \
    --self-contained-html \
    "$@"

EXIT_CODE=$?

echo ""
echo "========================================"
echo "Integration Tests Complete"
echo "Report: test_reports/integration_report.html"
echo "========================================"

exit $EXIT_CODE
