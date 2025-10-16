#!/bin/bash

# Script to run tests with coverage

echo "Running tests with coverage..."
pytest --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml -v

echo ""
echo "Coverage report generated in htmlcov/index.html"
echo "To view: open htmlcov/index.html in a browser"
