#!/bin/bash

# Run Unit Tests (Stubbed APIs - Frontend Only)
# No backend or database required

echo "========================================"
echo "Running UNIT Tests (Stubbed APIs)"
echo "========================================"

# Check if frontend is running
if ! docker ps | grep -q "frontend"; then
    echo "Frontend container not running. Starting frontend..."
    docker-compose up frontend -d
    sleep 5
fi

# Load unit test configuration
export $(cat .env.unit | xargs)

# Run pytest
pytest -v \
    --html=test_reports/unit_report.html \
    --self-contained-html \
    -m "not integration" \
    "$@"

EXIT_CODE=$?

echo ""
echo "========================================"
echo "Unit Tests Complete"
echo "Report: test_reports/unit_report.html"
echo "========================================"

exit $EXIT_CODE
