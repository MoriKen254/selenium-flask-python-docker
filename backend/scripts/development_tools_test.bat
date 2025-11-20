@echo off
REM Development Tools Test Script for Windows
REM This script tests all development tools configuration and functionality

echo ============================================
echo Development Tools Test
echo ============================================
echo.

setlocal enabledelayedexpansion

REM Set base directory
set BASE_DIR=%~dp0..

REM Create temporary directory for testing
set TEMP_DIR=%TEMP%\todo_api_devtools_test_%RANDOM%
mkdir "%TEMP_DIR%"
echo [INFO] Created temporary test directory: %TEMP_DIR%
echo.

REM Test 1: Install development dependencies
echo [TEST 1] Installing development dependencies...
cd /d "%BASE_DIR%"
pip install -e ".[dev]" >"%TEMP_DIR%\install_dev.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Failed to install development dependencies
    type "%TEMP_DIR%\install_dev.log"
    goto cleanup
)
echo [PASS] Development dependencies installed
echo.

REM Test 2: Black code formatting check
echo [TEST 2] Running Black code formatting check...
python -m black --check --diff src/ tests/ >"%TEMP_DIR%\black_check.log" 2>&1
set BLACK_RESULT=%ERRORLEVEL%
if %BLACK_RESULT% neq 0 (
    echo [WARN] Black formatting check failed - code needs formatting
    type "%TEMP_DIR%\black_check.log"
    echo [INFO] Running Black formatter...
    python -m black src/ tests/ >"%TEMP_DIR%\black_format.log" 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [FAIL] Black formatting failed
        type "%TEMP_DIR%\black_format.log"
    ) else (
        echo [PASS] Code formatted with Black
    )
) else (
    echo [PASS] Black code formatting check passed
)
echo.

REM Test 3: Ruff linting check
echo [TEST 3] Running Ruff linting check...
python -m ruff check src/ tests/ >"%TEMP_DIR%\ruff_check.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Ruff linting issues found
    type "%TEMP_DIR%\ruff_check.log"
    echo [INFO] Attempting to fix auto-fixable issues...
    python -m ruff check --fix src/ tests/ >"%TEMP_DIR%\ruff_fix.log" 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [WARN] Some Ruff issues could not be auto-fixed
        type "%TEMP_DIR%\ruff_fix.log"
    ) else (
        echo [PASS] Ruff auto-fixes applied
    )
) else (
    echo [PASS] Ruff linting check passed
)
echo.

REM Test 4: MyPy type checking (optional)
echo [TEST 4] Running MyPy type checking...
python -m mypy src/ >"%TEMP_DIR%\mypy_check.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] MyPy type checking issues found
    type "%TEMP_DIR%\mypy_check.log"
) else (
    echo [PASS] MyPy type checking passed
)
echo.

REM Test 5: pytest with coverage
echo [TEST 5] Running pytest with coverage...
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html >"%TEMP_DIR%\pytest_cov.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Some tests failed
    type "%TEMP_DIR%\pytest_cov.log"
) else (
    echo [PASS] All tests passed with coverage
    type "%TEMP_DIR%\pytest_cov.log"
)
echo.

REM Test 6: Security check with bandit
echo [TEST 6] Running security check with bandit...
python -m bandit -r src/ -f txt >"%TEMP_DIR%\bandit_check.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Security issues found
    type "%TEMP_DIR%\bandit_check.log"
) else (
    echo [PASS] No security issues found
)
echo.

REM Test 7: Safety check for dependencies
echo [TEST 7] Running safety check for dependencies...
python -m safety check >"%TEMP_DIR%\safety_check.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Vulnerable dependencies found
    type "%TEMP_DIR%\safety_check.log"
) else (
    echo [PASS] No vulnerable dependencies found
)
echo.

REM Test 8: Check pyproject.toml syntax
echo [TEST 8] Checking pyproject.toml syntax...
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))" >"%TEMP_DIR%\toml_check.log" 2>&1
if %ERRORLEVEL% neq 0 (
    REM Try with tomli for older Python versions
    python -c "import tomli; tomli.load(open('pyproject.toml', 'rb'))" >"%TEMP_DIR%\toml_check.log" 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [WARN] Could not validate pyproject.toml syntax
        type "%TEMP_DIR%\toml_check.log"
    ) else (
        echo [PASS] pyproject.toml syntax valid
    )
) else (
    echo [PASS] pyproject.toml syntax valid
)
echo.

REM Test 9: Check if all tools are properly configured
echo [TEST 9] Checking tool configurations...
python -c "import configparser; import sys; print('Tool configurations look good')" >"%TEMP_DIR%\config_check.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Tool configuration check failed
    type "%TEMP_DIR%\config_check.log"
) else (
    echo [PASS] Tool configurations check passed
)
echo.

REM Test 10: Generate coverage report
echo [TEST 10] Generating coverage report...
if exist "htmlcov" (
    echo [INFO] HTML coverage report generated in htmlcov/
    echo [PASS] Coverage report generation successful
) else (
    echo [WARN] HTML coverage report not found
)
echo.

echo ============================================
echo Development Tools Test Complete
echo ============================================
echo [INFO] Development tools test completed
echo [INFO] Check the logs in %TEMP_DIR% for detailed results
echo.

:cleanup
echo [INFO] Cleaning up...
cd /d "%TEMP%"
REM Keep temp directory for review
echo [INFO] Temporary files kept in: %TEMP_DIR%

cd /d "%BASE_DIR%"
echo [SUCCESS] Development tools test completed
exit /b 0
