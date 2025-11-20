#!/bin/bash
# Build and Install Test Script for Unix-like systems
# This script tests the complete build and installation process

set -e  # Exit on any error

echo "============================================"
echo "Build and Install Test"
echo "============================================"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# Create temporary directory for testing
TEMP_DIR=$(mktemp -d -t todo_api_build_test_XXXXXX)
echo "[INFO] Created temporary test directory: $TEMP_DIR"
echo

# Cleanup function
cleanup() {
    echo "[INFO] Cleaning up..."
    # Deactivate virtual environment if active
    if [[ -n "$VIRTUAL_ENV" ]]; then
        deactivate || true
    fi
    
    # Clean up temp directory
    rm -rf "$TEMP_DIR"
    echo "[INFO] Cleanup complete"
}

# Set trap for cleanup
trap cleanup EXIT

# Test 1: Clean previous builds
echo "[TEST 1] Cleaning previous builds..."
cd "$BASE_DIR"
if [ -d "dist" ]; then
    rm -rf "dist"
    echo "[INFO] Cleaned dist directory"
fi
if [ -d "build" ]; then
    rm -rf "build"
    echo "[INFO] Cleaned build directory"
fi
if [ -d "src/todo_api.egg-info" ]; then
    rm -rf "src/todo_api.egg-info"
    echo "[INFO] Cleaned egg-info directory"
fi
echo "[PASS] Build cleanup complete"
echo

# Test 2: Install build dependencies
echo "[TEST 2] Installing build dependencies..."
if pip install build twine >/dev/null 2>&1; then
    echo "[PASS] Build dependencies installed"
else
    echo "[FAIL] Failed to install build dependencies"
    exit 1
fi
echo

# Test 3: Build source distribution
echo "[TEST 3] Building source distribution..."
if python -m build --sdist > "$TEMP_DIR/build_sdist.log" 2>&1; then
    echo "[PASS] Source distribution built successfully"
else
    echo "[FAIL] Failed to build source distribution"
    cat "$TEMP_DIR/build_sdist.log"
    exit 1
fi
echo

# Test 4: Build wheel distribution
echo "[TEST 4] Building wheel distribution..."
if python -m build --wheel > "$TEMP_DIR/build_wheel.log" 2>&1; then
    echo "[PASS] Wheel distribution built successfully"
else
    echo "[FAIL] Failed to build wheel distribution"
    cat "$TEMP_DIR/build_wheel.log"
    exit 1
fi
echo

# Test 5: Check built artifacts
echo "[TEST 5] Checking built artifacts..."
if ! ls dist/*.tar.gz >/dev/null 2>&1; then
    echo "[FAIL] Source distribution not found"
    exit 1
fi
if ! ls dist/*.whl >/dev/null 2>&1; then
    echo "[FAIL] Wheel distribution not found"
    exit 1
fi
echo "[PASS] All distribution artifacts present"
echo

# Test 6: Validate distributions with twine
echo "[TEST 6] Validating distributions with twine..."
if python -m twine check dist/* > "$TEMP_DIR/twine_check.log" 2>&1; then
    echo "[PASS] Distribution validation successful"
else
    echo "[FAIL] Distribution validation failed"
    cat "$TEMP_DIR/twine_check.log"
    exit 1
fi
echo

# Test 7: Create fresh virtual environment for installation test
echo "[TEST 7] Creating fresh virtual environment..."
cd "$TEMP_DIR"
if python -m venv test_env >/dev/null 2>&1; then
    source test_env/bin/activate
    echo "[PASS] Fresh virtual environment created"
else
    echo "[FAIL] Failed to create virtual environment"
    exit 1
fi
echo

# Test 8: Install from wheel
echo "[TEST 8] Installing from wheel..."
WHEEL_FILE=$(ls "$BASE_DIR"/dist/*.whl | head -1)
if pip install "$WHEEL_FILE" > "$TEMP_DIR/install_wheel.log" 2>&1; then
    echo "[PASS] Installation from wheel successful"
else
    echo "[FAIL] Failed to install from wheel"
    cat "$TEMP_DIR/install_wheel.log"
    exit 1
fi
echo

# Test 9: Test installed package
echo "[TEST 9] Testing installed package..."
if IMPORT_OUTPUT=$(python -c "import todo_api; print(f'Imported todo_api version: {todo_api.__version__}')" 2>&1); then
    echo "$IMPORT_OUTPUT"
    echo "[PASS] Package import successful"
else
    echo "[FAIL] Failed to import installed package"
    echo "$IMPORT_OUTPUT"
    exit 1
fi
echo

# Test 10: Test CLI from installed package
echo "[TEST 10] Testing CLI from installed package..."
if CLI_OUTPUT=$(todo-api --version 2>&1); then
    echo "$CLI_OUTPUT"
    echo "[PASS] CLI test successful"
else
    echo "[FAIL] CLI not available after installation"
    echo "$CLI_OUTPUT"
    exit 1
fi
echo

# Test 11: Test app factory from installed package
echo "[TEST 11] Testing app factory from installed package..."
if APP_OUTPUT=$(python -c "from todo_api import create_app; app = create_app(); print('App factory test successful')" 2>&1); then
    echo "$APP_OUTPUT"
    echo "[PASS] App factory test successful"
else
    echo "[FAIL] App factory test failed"
    echo "$APP_OUTPUT"
    exit 1
fi
echo

echo "============================================"
echo "Build and Install Test Complete"
echo "============================================"
echo "[SUCCESS] All build and install tests passed"
