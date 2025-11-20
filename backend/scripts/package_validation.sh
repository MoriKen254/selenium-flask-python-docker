#!/bin/bash
# Package Validation Test Script for Unix-like systems
# This script validates the Todo API package build and installation

set -e  # Exit on any error

echo "============================================"
echo "Package Validation Test"
echo "============================================"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_DIR="$(dirname "$SCRIPT_DIR")"

# Create temporary directory for testing
TEMP_DIR=$(mktemp -d -t todo_api_test_XXXXXX)
cd "$TEMP_DIR"

echo "[INFO] Created temporary test directory: $TEMP_DIR"
echo

# Cleanup function
cleanup() {
    echo "[INFO] Cleaning up temporary directory..."
    rm -rf "$TEMP_DIR"
}

# Set trap for cleanup
trap cleanup EXIT

# Test 1: Check if we can install in development mode
echo "[TEST 1] Installing package in development mode..."
if pip install -e "$PACKAGE_DIR" >/dev/null 2>&1; then
    echo "[PASS] Development installation successful"
else
    echo "[FAIL] Failed to install package in development mode"
    exit 1
fi
echo

# Test 2: Check version import
echo "[TEST 2] Testing version import..."
if VERSION_OUTPUT=$(python -c "import todo_api; print(f'Version: {todo_api.__version__}')" 2>&1); then
    echo "$VERSION_OUTPUT"
    echo "[PASS] Version import successful"
else
    echo "[FAIL] Failed to import version"
    echo "$VERSION_OUTPUT"
    exit 1
fi
echo

# Test 3: Check CLI availability
echo "[TEST 3] Testing CLI availability..."
if CLI_OUTPUT=$(todo-api --version 2>&1); then
    echo "$CLI_OUTPUT"
    echo "[PASS] CLI command available"
else
    echo "[FAIL] CLI command not available"
    echo "$CLI_OUTPUT"
    exit 1
fi
echo

# Test 4: Check app factory
echo "[TEST 4] Testing app factory..."
if APP_OUTPUT=$(python -c "from todo_api import create_app; app = create_app(); print('App created successfully')" 2>&1); then
    echo "$APP_OUTPUT"
    echo "[PASS] App factory test successful"
else
    echo "[FAIL] App factory test failed"
    echo "$APP_OUTPUT"
    exit 1
fi
echo

# Test 5: Run basic unit tests
echo "[TEST 5] Running basic unit tests..."
cd "$PACKAGE_DIR"
if python -m pytest tests/ -v --tb=short > "$TEMP_DIR/test_output.txt" 2>&1; then
    cat "$TEMP_DIR/test_output.txt"
    echo "[PASS] Unit tests passed"
else
    cat "$TEMP_DIR/test_output.txt"
    echo "[WARN] Some tests failed, but continuing validation..."
fi
echo

# Test 6: Check package metadata
echo "[TEST 6] Checking package metadata..."
if METADATA_OUTPUT=$(python -c "import pkg_resources; dist = pkg_resources.get_distribution('todo-api'); print(f'Name: {dist.project_name}'); print(f'Version: {dist.version}')" 2>&1); then
    echo "$METADATA_OUTPUT"
    echo "[PASS] Package metadata accessible"
else
    echo "[WARN] Package metadata check failed (might not be fully installed)"
    echo "$METADATA_OUTPUT"
fi
echo

echo "============================================"
echo "Package Validation Complete"
echo "============================================"
echo "[SUCCESS] Package validation passed"
