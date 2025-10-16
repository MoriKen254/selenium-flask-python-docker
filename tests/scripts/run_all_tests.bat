@echo off
REM Comprehensive Test Runner for Windows
REM Rebuilds images and runs all tests: backend unit, frontend unit, and integration tests

setlocal enabledelayedexpansion

REM Colors (using Windows console codes - limited support)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Track overall status
set BACKEND_TESTS_PASSED=0
set FRONTEND_UNIT_PASSED=0
set FRONTEND_INTEGRATION_PASSED=0
set OVERALL_SUCCESS=1

REM Change to project root directory
cd /d "%~dp0..\.."

echo.
echo ========================================
echo Starting Comprehensive Test Suite
echo ========================================
echo.
echo This will:
echo   1. Rebuild all Docker images
echo   2. Run backend unit tests (pytest with coverage)
echo   3. Run frontend unit tests (Selenium with mocked APIs)
echo   4. Run integration tests (Selenium with real backend)
echo.

REM Step 1: Rebuild Docker images
echo.
echo ========================================
echo Step 1/4: Rebuilding Docker Images
echo ========================================
echo.
echo Stopping existing containers...
docker-compose down

echo Building fresh images...
docker-compose build
if errorlevel 1 (
    echo %RED%Failed to rebuild Docker images%NC%
    exit /b 1
)
echo %GREEN%Docker images rebuilt successfully%NC%

REM Step 2: Run Backend Unit Tests
echo.
echo ========================================
echo Step 2/4: Backend Unit Tests
echo ========================================
echo.
echo Starting backend and database containers...
docker-compose up -d backend postgres

echo Waiting for backend to be ready...
timeout /t 5 /nobreak >nul

REM Wait for backend health check
echo Checking backend health...
set RETRY=0
:BACKEND_HEALTH_CHECK
set /a RETRY+=1
curl -s http://localhost:5000/health >nul 2>&1
if errorlevel 1 (
    if !RETRY! LSS 30 (
        timeout /t 1 /nobreak >nul
        goto BACKEND_HEALTH_CHECK
    ) else (
        echo %RED%Backend failed to start%NC%
        exit /b 1
    )
)
echo %GREEN%Backend is healthy%NC%

echo Running backend tests with coverage...
docker exec todo_backend pytest -v --cov=. --cov-report=html --cov-report=term
if errorlevel 1 (
    echo %RED%Backend tests failed%NC%
    set OVERALL_SUCCESS=0
) else (
    echo %GREEN%Backend tests passed%NC%
    set BACKEND_TESTS_PASSED=1
)

REM Step 3: Run Frontend Unit Tests
echo.
echo ========================================
echo Step 3/4: Frontend Unit Tests
echo ========================================
echo.
echo Starting frontend container...
docker-compose up -d frontend

echo Waiting for frontend to be ready...
timeout /t 5 /nobreak >nul

REM Wait for frontend
set RETRY=0
:FRONTEND_HEALTH_CHECK
set /a RETRY+=1
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    if !RETRY! LSS 30 (
        timeout /t 1 /nobreak >nul
        goto FRONTEND_HEALTH_CHECK
    ) else (
        echo %RED%Frontend failed to start%NC%
        exit /b 1
    )
)
echo %GREEN%Frontend is ready%NC%

cd tests

REM Create test directories
if not exist "test_reports" mkdir test_reports
if not exist "test_screenshots" mkdir test_screenshots

REM Get network name
for /f "tokens=*" %%i in ('docker network ls --filter "name=todo_network" --format "{{.Name}}"') do set NETWORK=%%i

if "!NETWORK!"=="" (
    echo %RED%Docker network not found%NC%
    cd ..
    exit /b 1
)

echo Using network: !NETWORK!

REM Stop backend for unit tests
echo Stopping backend for unit tests (frontend only with mocked APIs)...
docker stop todo_backend todo_postgres >nul 2>&1

echo Running frontend unit tests...
docker run --rm ^
    --network !NETWORK! ^
    -e TEST_MODE=unit ^
    -e FRONTEND_URL=http://frontend:3000 ^
    -e BROWSER=firefox ^
    -e HEADLESS=true ^
    -v "%cd%/test_reports:/tests/test_reports" ^
    -v "%cd%/test_screenshots:/tests/test_screenshots" ^
    todo-tests python -m pytest -v --html=test_reports/unit_report.html --self-contained-html -m "not integration"

if errorlevel 1 (
    echo %RED%Frontend unit tests failed%NC%
    set OVERALL_SUCCESS=0
) else (
    echo %GREEN%Frontend unit tests passed%NC%
    set FRONTEND_UNIT_PASSED=1
)

REM Restart backend
echo Restarting backend and database...
docker start todo_postgres todo_backend >nul 2>&1
timeout /t 3 /nobreak >nul

REM Step 4: Run Integration Tests
echo.
echo ========================================
echo Step 4/4: Integration Tests
echo ========================================
echo.
echo Ensuring all services are running...
cd ..
docker-compose up -d

echo Waiting for all services to be ready...
timeout /t 5 /nobreak >nul

cd tests

echo Running integration tests...
docker run --rm ^
    --network !NETWORK! ^
    -e TEST_MODE=integration ^
    -e FRONTEND_URL=http://frontend:3000 ^
    -e BACKEND_URL=http://backend:5000 ^
    -e DB_HOST=postgres ^
    -e DB_PORT=5432 ^
    -e POSTGRES_DB=tododb ^
    -e POSTGRES_USER=todouser ^
    -e POSTGRES_PASSWORD=todopass ^
    -e BROWSER=firefox ^
    -e HEADLESS=true ^
    -v "%cd%/test_reports:/tests/test_reports" ^
    -v "%cd%/test_screenshots:/tests/test_screenshots" ^
    todo-tests python -m pytest -v --html=test_reports/integration_report.html --self-contained-html

if errorlevel 1 (
    echo %RED%Integration tests failed%NC%
    set OVERALL_SUCCESS=0
) else (
    echo %GREEN%Integration tests passed%NC%
    set FRONTEND_INTEGRATION_PASSED=1
)

REM Final Summary
echo.
echo ========================================
echo Test Suite Summary
echo ========================================
echo.
echo Results:
echo --------

if %BACKEND_TESTS_PASSED%==1 (
    echo %GREEN%Backend Unit Tests: PASSED%NC%
) else (
    echo %RED%Backend Unit Tests: FAILED%NC%
)

if %FRONTEND_UNIT_PASSED%==1 (
    echo %GREEN%Frontend Unit Tests: PASSED%NC%
) else (
    echo %RED%Frontend Unit Tests: FAILED%NC%
)

if %FRONTEND_INTEGRATION_PASSED%==1 (
    echo %GREEN%Integration Tests: PASSED%NC%
) else (
    echo %RED%Integration Tests: FAILED%NC%
)

echo.
echo Reports:
echo --------
echo Backend Coverage: backend/htmlcov/index.html
echo Frontend Unit: tests/test_reports/unit_report.html
echo Integration: tests/test_reports/integration_report.html
echo.

if %OVERALL_SUCCESS%==1 (
    echo ========================================
    echo %GREEN%ALL TESTS PASSED%NC%
    echo ========================================
    cd ..
    exit /b 0
) else (
    echo ========================================
    echo %RED%SOME TESTS FAILED%NC%
    echo ========================================
    cd ..
    exit /b 1
)
