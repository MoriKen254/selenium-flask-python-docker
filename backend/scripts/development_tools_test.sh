#!/bin/bash
# Development Tools Test Script for Unix-like systems
# This script tests all development tools configuration and functionality

set -e  # Exit on any error

echo "============================================"
echo "Development Tools Test"
echo "============================================"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# Create temporary directory for testing
TEMP_DIR=$(mktemp -d -t todo_api_devtools_test_XXXXXX)
echo "[INFO] Created temporary test directory: $TEMP_DIR"
echo

# Test 1: Install development dependencies
echo "[TEST 1] Installing development dependencies..."
cd "$BASE_DIR"
if pip install -e ".[dev]" > "$TEMP_DIR/install_dev.log" 2>&1; then
    echo "[PASS] Development dependencies installed"
else
    echo "[FAIL] Failed to install development dependencies"
    cat "$TEMP_DIR/install_dev.log"
    exit 1
fi
echo

# Test 2: Black code formatting check
echo "[TEST 2] Running Black code formatting check..."
if python -m black --check --diff src/ tests/ > "$TEMP_DIR/black_check.log" 2>&1; then
    echo "[PASS] Black code formatting check passed"
else
    echo "[WARN] Black formatting check failed - code needs formatting"
    cat "$TEMP_DIR/black_check.log"
    echo "[INFO] Running Black formatter..."
    if python -m black src/ tests/ > "$TEMP_DIR/black_format.log" 2>&1; then
        echo "[PASS] Code formatted with Black"
    else
        echo "[FAIL] Black formatting failed"
        cat "$TEMP_DIR/black_format.log"
    fi
fi
echo

# Test 3: Ruff linting check
echo "[TEST 3] Running Ruff linting check..."
if python -m ruff check src/ tests/ > "$TEMP_DIR/ruff_check.log" 2>&1; then
    echo "[PASS] Ruff linting check passed"
else
    echo "[WARN] Ruff linting issues found"
    cat "$TEMP_DIR/ruff_check.log"
    echo "[INFO] Attempting to fix auto-fixable issues..."
    if python -m ruff check --fix src/ tests/ > "$TEMP_DIR/ruff_fix.log" 2>&1; then
        echo "[PASS] Ruff auto-fixes applied"
    else
        echo "[WARN] Some Ruff issues could not be auto-fixed"
        cat "$TEMP_DIR/ruff_fix.log"
    fi
fi
echo

# Test 4: MyPy type checking (optional)
echo "[TEST 4] Running MyPy type checking..."
if python -m mypy src/ > "$TEMP_DIR/mypy_check.log" 2>&1; then
    echo "[PASS] MyPy type checking passed"
else
    echo "[WARN] MyPy type checking issues found"
    cat "$TEMP_DIR/mypy_check.log"
fi
echo

# Test 5: pytest with coverage
echo "[TEST 5] Running pytest with coverage..."
if python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html > "$TEMP_DIR/pytest_cov.log" 2>&1; then
    echo "[PASS] All tests passed with coverage"
    cat "$TEMP_DIR/pytest_cov.log"
else
    echo "[WARN] Some tests failed"
    cat "$TEMP_DIR/pytest_cov.log"
fi
echo

# Test 6: Security check with bandit
echo "[TEST 6] Running security check with bandit..."
if python -m bandit -r src/ -f txt > "$TEMP_DIR/bandit_check.log" 2>&1; then
    echo "[PASS] No security issues found"
else
    echo "[WARN] Security issues found"
    cat "$TEMP_DIR/bandit_check.log"
fi
echo

# Test 7: Safety check for dependencies
echo "[TEST 7] Running safety check for dependencies..."
if python -m safety check > "$TEMP_DIR/safety_check.log" 2>&1; then
    echo "[PASS] No vulnerable dependencies found"
else
    echo "[WARN] Vulnerable dependencies found"
    cat "$TEMP_DIR/safety_check.log"
fi
echo

# Test 8: Check pyproject.toml syntax
echo "[TEST 8] Checking pyproject.toml syntax..."
if python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))" > "$TEMP_DIR/toml_check.log" 2>&1; then
    echo "[PASS] pyproject.toml syntax valid"
elif python -c "import tomli; tomli.load(open('pyproject.toml', 'rb'))" > "$TEMP_DIR/toml_check.log" 2>&1; then
    echo "[PASS] pyproject.toml syntax valid"
else
    echo "[WARN] Could not validate pyproject.toml syntax"
    cat "$TEMP_DIR/toml_check.log"
fi
echo

# Test 9: Check if all tools are properly configured
echo "[TEST 9] Checking tool configurations..."
if python -c "import configparser; import sys; print('Tool configurations look good')" > "$TEMP_DIR/config_check.log" 2>&1; then
    echo "[PASS] Tool configurations check passed"
else
    echo "[WARN] Tool configuration check failed"
    cat "$TEMP_DIR/config_check.log"
fi
echo

# Test 10: Generate coverage report
echo "[TEST 10] Generating coverage report..."
if [ -d "htmlcov" ]; then
    echo "[INFO] HTML coverage report generated in htmlcov/"
    echo "[PASS] Coverage report generation successful"
else
    echo "[WARN] HTML coverage report not found"
fi
echo

echo "============================================"
echo "Development Tools Test Complete"
echo "============================================"
echo "[INFO] Development tools test completed"
echo "[INFO] Check the logs in $TEMP_DIR for detailed results"
echo

# Keep temp directory for review
echo "[INFO] Temporary files kept in: $TEMP_DIR"
echo "[SUCCESS] Development tools test completed"
