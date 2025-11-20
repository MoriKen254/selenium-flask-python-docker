@echo off
REM Version Consistency Test Script for Windows
REM This script checks that version information is consistent across all files

echo ============================================
echo Version Consistency Test
echo ============================================
echo.

setlocal enabledelayedexpansion

REM Set base directory
set BASE_DIR=%~dp0..

echo [INFO] Checking version consistency across project files...
echo.

REM Test 1: Extract version from pyproject.toml
echo [TEST 1] Extracting version from pyproject.toml...
for /f "tokens=3 delims= " %%a in ('findstr "^version = " "%BASE_DIR%\pyproject.toml"') do (
    set PYPROJECT_VERSION=%%a
    set PYPROJECT_VERSION=!PYPROJECT_VERSION:"=!
)
echo [INFO] pyproject.toml version: !PYPROJECT_VERSION!
echo.

REM Test 2: Extract version from __init__.py
echo [TEST 2] Extracting version from __init__.py...
for /f "tokens=3 delims= " %%a in ('findstr "__version__ = " "%BASE_DIR%\src\todo_api\__init__.py"') do (
    set INIT_VERSION=%%a
    set INIT_VERSION=!INIT_VERSION:"=!
)
echo [INFO] __init__.py version: !INIT_VERSION!
echo.

REM Test 3: Get version from Python import
echo [TEST 3] Getting version from Python import...
cd /d "%BASE_DIR%"
pip install -e . >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Could not install package, skipping Python import test
    set PYTHON_VERSION=SKIP
) else (
    for /f "delims=" %%a in ('python -c "import todo_api; print(todo_api.__version__)"') do set PYTHON_VERSION=%%a
    echo [INFO] Python import version: !PYTHON_VERSION!
)
echo.

REM Test 4: Get version from CLI
echo [TEST 4] Getting version from CLI...
for /f "tokens=2 delims= " %%a in ('todo-api --version 2^>nul') do set CLI_VERSION=%%a
if "!CLI_VERSION!"=="" (
    echo [WARN] Could not get CLI version
    set CLI_VERSION=SKIP
) else (
    echo [INFO] CLI version: !CLI_VERSION!
)
echo.

REM Test 5: Check API endpoint version (if running)
echo [TEST 5] Checking API endpoint version...
REM This would require the API to be running, so we'll skip for now
set API_VERSION=SKIP
echo [INFO] API endpoint version: SKIP (requires running server)
echo.

REM Version comparison
echo ============================================
echo Version Comparison Results
echo ============================================
echo pyproject.toml: !PYPROJECT_VERSION!
echo __init__.py:    !INIT_VERSION!
echo Python import:  !PYTHON_VERSION!
echo CLI:            !CLI_VERSION!
echo API endpoint:   !API_VERSION!
echo.

REM Check consistency
set CONSISTENT=true
if not "!PYPROJECT_VERSION!"=="!INIT_VERSION!" (
    echo [FAIL] pyproject.toml and __init__.py versions do not match
    set CONSISTENT=false
)
if not "!PYTHON_VERSION!"=="SKIP" if not "!INIT_VERSION!"=="!PYTHON_VERSION!" (
    echo [FAIL] __init__.py and Python import versions do not match
    set CONSISTENT=false
)
if not "!CLI_VERSION!"=="SKIP" if not "!INIT_VERSION!"=="!CLI_VERSION!" (
    echo [FAIL] __init__.py and CLI versions do not match
    set CONSISTENT=false
)

if "!CONSISTENT!"=="true" (
    echo [SUCCESS] All checked versions are consistent
    echo ============================================
    exit /b 0
) else (
    echo [ERROR] Version inconsistencies detected
    echo ============================================
    exit /b 1
)
