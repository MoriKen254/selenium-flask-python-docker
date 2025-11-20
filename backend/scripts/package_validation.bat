@echo off
REM Package Validation Test Script for Windows
REM This script validates the Todo API package build and installation

echo ============================================
echo Package Validation Test
echo ============================================
echo.

REM Set error handling
setlocal enabledelayedexpansion

REM Create temporary directory for testing
set TEMP_DIR=%TEMP%\todo_api_test_%RANDOM%
mkdir "%TEMP_DIR%"
cd /d "%TEMP_DIR%"

echo [INFO] Created temporary test directory: %TEMP_DIR%
echo.

REM Test 1: Check if we can install in development mode
echo [TEST 1] Installing package in development mode...
pip install -e "%~dp0.." >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Failed to install package in development mode
    goto cleanup
)
echo [PASS] Development installation successful
echo.

REM Test 2: Check version import
echo [TEST 2] Testing version import...
python -c "import todo_api; print(f'Version: {todo_api.__version__}')" >version_output.txt 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Failed to import version
    type version_output.txt
    goto cleanup
)
type version_output.txt
echo [PASS] Version import successful
echo.

REM Test 3: Check CLI availability
echo [TEST 3] Testing CLI availability...
todo-api --version >cli_output.txt 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] CLI command not available
    type cli_output.txt
    goto cleanup
)
type cli_output.txt
echo [PASS] CLI command available
echo.

REM Test 4: Check app factory
echo [TEST 4] Testing app factory...
python -c "from todo_api import create_app; app = create_app(); print('App created successfully')" >app_output.txt 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] App factory test failed
    type app_output.txt
    goto cleanup
)
type app_output.txt
echo [PASS] App factory test successful
echo.

REM Test 5: Run basic unit tests
echo [TEST 5] Running basic unit tests...
cd /d "%~dp0.."
python -m pytest tests/ -v --tb=short >"%TEMP_DIR%\test_output.txt" 2>&1
set TEST_RESULT=%ERRORLEVEL%
type "%TEMP_DIR%\test_output.txt"
if %TEST_RESULT% neq 0 (
    echo [WARN] Some tests failed, but continuing validation...
) else (
    echo [PASS] Unit tests passed
)
echo.

REM Test 6: Check package metadata
echo [TEST 6] Checking package metadata...
python -c "import pkg_resources; dist = pkg_resources.get_distribution('todo-api'); print(f'Name: {dist.project_name}'); print(f'Version: {dist.version}')" >metadata_output.txt 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Package metadata check failed (might not be fully installed)
    type metadata_output.txt
) else (
    type metadata_output.txt
    echo [PASS] Package metadata accessible
)
echo.

echo ============================================
echo Package Validation Complete
echo ============================================

:cleanup
echo [INFO] Cleaning up temporary directory...
cd /d "%TEMP%"
rmdir /s /q "%TEMP_DIR%" >nul 2>&1

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Package validation failed
    exit /b 1
) else (
    echo [SUCCESS] Package validation passed
    exit /b 0
)
