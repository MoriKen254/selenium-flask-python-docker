@echo off
REM Build and Install Test Script for Windows
REM This script tests the complete build and installation process

echo ============================================
echo Build and Install Test
echo ============================================
echo.

setlocal enabledelayedexpansion

REM Set base directory
set BASE_DIR=%~dp0..

REM Create temporary directory for testing
set TEMP_DIR=%TEMP%\todo_api_build_test_%RANDOM%
mkdir "%TEMP_DIR%"
echo [INFO] Created temporary test directory: %TEMP_DIR%
echo.

REM Test 1: Clean previous builds
echo [TEST 1] Cleaning previous builds...
cd /d "%BASE_DIR%"
if exist "dist" (
    rmdir /s /q "dist"
    echo [INFO] Cleaned dist directory
)
if exist "build" (
    rmdir /s /q "build"
    echo [INFO] Cleaned build directory
)
if exist "src\todo_api.egg-info" (
    rmdir /s /q "src\todo_api.egg-info"
    echo [INFO] Cleaned egg-info directory
)
echo [PASS] Build cleanup complete
echo.

REM Test 2: Install build dependencies
echo [TEST 2] Installing build dependencies...
pip install build twine >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Failed to install build dependencies
    goto cleanup
)
echo [PASS] Build dependencies installed
echo.

REM Test 3: Build source distribution
echo [TEST 3] Building source distribution...
python -m build --sdist >"%TEMP_DIR%\build_sdist.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Failed to build source distribution
    type "%TEMP_DIR%\build_sdist.log"
    goto cleanup
)
echo [PASS] Source distribution built successfully
echo.

REM Test 4: Build wheel distribution
echo [TEST 4] Building wheel distribution...
python -m build --wheel >"%TEMP_DIR%\build_wheel.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Failed to build wheel distribution
    type "%TEMP_DIR%\build_wheel.log"
    goto cleanup
)
echo [PASS] Wheel distribution built successfully
echo.

REM Test 5: Check built artifacts
echo [TEST 5] Checking built artifacts...
if not exist "dist\*.tar.gz" (
    echo [FAIL] Source distribution not found
    goto cleanup
)
if not exist "dist\*.whl" (
    echo [FAIL] Wheel distribution not found
    goto cleanup
)
echo [PASS] All distribution artifacts present
echo.

REM Test 6: Validate distributions with twine
echo [TEST 6] Validating distributions with twine...
python -m twine check dist/* >"%TEMP_DIR%\twine_check.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Distribution validation failed
    type "%TEMP_DIR%\twine_check.log"
    goto cleanup
)
echo [PASS] Distribution validation successful
echo.

REM Test 7: Create fresh virtual environment for installation test
echo [TEST 7] Creating fresh virtual environment...
cd /d "%TEMP_DIR%"
python -m venv test_env >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Failed to create virtual environment
    goto cleanup
)
call test_env\Scripts\activate.bat
echo [PASS] Fresh virtual environment created
echo.

REM Test 8: Install from wheel
echo [TEST 8] Installing from wheel...
for %%f in ("%BASE_DIR%\dist\*.whl") do (
    set WHEEL_FILE=%%f
    goto install_wheel
)
:install_wheel
pip install "!WHEEL_FILE!" >"%TEMP_DIR%\install_wheel.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Failed to install from wheel
    type "%TEMP_DIR%\install_wheel.log"
    goto cleanup
)
echo [PASS] Installation from wheel successful
echo.

REM Test 9: Test installed package
echo [TEST 9] Testing installed package...
python -c "import todo_api; print(f'Imported todo_api version: {todo_api.__version__}')" >"%TEMP_DIR%\import_test.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Failed to import installed package
    type "%TEMP_DIR%\import_test.log"
    goto cleanup
)
type "%TEMP_DIR%\import_test.log"
echo [PASS] Package import successful
echo.

REM Test 10: Test CLI from installed package
echo [TEST 10] Testing CLI from installed package...
todo-api --version >"%TEMP_DIR%\cli_test.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] CLI not available after installation
    type "%TEMP_DIR%\cli_test.log"
    goto cleanup
)
type "%TEMP_DIR%\cli_test.log"
echo [PASS] CLI test successful
echo.

REM Test 11: Test app factory from installed package
echo [TEST 11] Testing app factory from installed package...
python -c "from todo_api import create_app; app = create_app(); print('App factory test successful')" >"%TEMP_DIR%\app_test.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] App factory test failed
    type "%TEMP_DIR%\app_test.log"
    goto cleanup
)
type "%TEMP_DIR%\app_test.log"
echo [PASS] App factory test successful
echo.

echo ============================================
echo Build and Install Test Complete
echo ============================================
echo [SUCCESS] All build and install tests passed
echo.

:cleanup
echo [INFO] Cleaning up...
REM Deactivate virtual environment if active
if defined VIRTUAL_ENV call deactivate

REM Clean up temp directory
cd /d "%TEMP%"
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%" >nul 2>&1

REM Return to base directory
cd /d "%BASE_DIR%"

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Build and install test failed
    exit /b 1
) else (
    echo [INFO] Cleanup complete
    exit /b 0
)
