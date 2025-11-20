#!/bin/bash
# Version Consistency Test Script for Unix-like systems
# This script checks that version information is consistent across all files

set -e  # Exit on any error

echo "============================================"
echo "Version Consistency Test"
echo "============================================"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

echo "[INFO] Checking version consistency across project files..."
echo

# Test 1: Extract version from pyproject.toml
echo "[TEST 1] Extracting version from pyproject.toml..."
PYPROJECT_VERSION=$(grep '^version = ' "$BASE_DIR/pyproject.toml" | cut -d '"' -f 2)
echo "[INFO] pyproject.toml version: $PYPROJECT_VERSION"
echo

# Test 2: Extract version from __init__.py
echo "[TEST 2] Extracting version from __init__.py..."
INIT_VERSION=$(grep '__version__ = ' "$BASE_DIR/src/todo_api/__init__.py" | cut -d '"' -f 2)
echo "[INFO] __init__.py version: $INIT_VERSION"
echo

# Test 3: Get version from Python import
echo "[TEST 3] Getting version from Python import..."
cd "$BASE_DIR"
if pip install -e . >/dev/null 2>&1; then
    PYTHON_VERSION=$(python -c "import todo_api; print(todo_api.__version__)")
    echo "[INFO] Python import version: $PYTHON_VERSION"
else
    echo "[WARN] Could not install package, skipping Python import test"
    PYTHON_VERSION="SKIP"
fi
echo

# Test 4: Get version from CLI
echo "[TEST 4] Getting version from CLI..."
if CLI_OUTPUT=$(todo-api --version 2>/dev/null); then
    CLI_VERSION=$(echo "$CLI_OUTPUT" | awk '{print $2}')
    echo "[INFO] CLI version: $CLI_VERSION"
else
    echo "[WARN] Could not get CLI version"
    CLI_VERSION="SKIP"
fi
echo

# Test 5: Check API endpoint version (if running)
echo "[TEST 5] Checking API endpoint version..."
# This would require the API to be running, so we'll skip for now
API_VERSION="SKIP"
echo "[INFO] API endpoint version: SKIP (requires running server)"
echo

# Version comparison
echo "============================================"
echo "Version Comparison Results"
echo "============================================"
echo "pyproject.toml: $PYPROJECT_VERSION"
echo "__init__.py:    $INIT_VERSION"
echo "Python import:  $PYTHON_VERSION"
echo "CLI:            $CLI_VERSION"
echo "API endpoint:   $API_VERSION"
echo

# Check consistency
CONSISTENT=true

if [ "$PYPROJECT_VERSION" != "$INIT_VERSION" ]; then
    echo "[FAIL] pyproject.toml and __init__.py versions do not match"
    CONSISTENT=false
fi

if [ "$PYTHON_VERSION" != "SKIP" ] && [ "$INIT_VERSION" != "$PYTHON_VERSION" ]; then
    echo "[FAIL] __init__.py and Python import versions do not match"
    CONSISTENT=false
fi

if [ "$CLI_VERSION" != "SKIP" ] && [ "$INIT_VERSION" != "$CLI_VERSION" ]; then
    echo "[FAIL] __init__.py and CLI versions do not match"
    CONSISTENT=false
fi

if [ "$CONSISTENT" = true ]; then
    echo "[SUCCESS] All checked versions are consistent"
    echo "============================================"
    exit 0
else
    echo "[ERROR] Version inconsistencies detected"
    echo "============================================"
    exit 1
fi
