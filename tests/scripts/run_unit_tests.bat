@echo off
REM Batch script to run unit tests on Windows
REM Run Unit Tests (Stubbed APIs - Frontend Only)
REM No backend or database required

echo ========================================
echo Running UNIT Tests (Stubbed APIs)
echo ========================================
echo.

REM Check if frontend is running
echo Checking if frontend container is running...
docker ps --filter "name=frontend" --filter "status=running" --format "{{.Names}}" | findstr /r "frontend" >nul
if errorlevel 1 (
    echo Frontend container is not running. Starting frontend...
    docker-compose up frontend -d
    timeout /t 5 /nobreak >nul
)

REM Create directories if they don't exist
echo Creating test artifact directories...
if not exist "test_reports" mkdir test_reports
if not exist "test_screenshots" mkdir test_screenshots

REM Get the network name (try todo_network first)
for /f "tokens=*" %%i in ('docker network ls --filter "name=todo_network" --format "{{.Name}}"') do set NETWORK=%%i

if "%NETWORK%"=="" (
    echo ERROR: Docker network not found. Make sure docker-compose is running.
    echo Run: docker-compose up -d
    exit /b 1
)

echo Using network: %NETWORK%
echo.

REM Stop backend and database for unit tests (frontend only with mocked APIs)
echo Stopping backend and database containers for unit tests...
docker stop todo_backend todo_postgres >nul 2>&1
echo Backend and database stopped - tests will use mocked APIs only
echo.

REM Run tests
echo Running unit tests...
docker run --rm ^
    --network %NETWORK% ^
    -e TEST_MODE=unit ^
    -e FRONTEND_URL=http://frontend:3000 ^
    -e BROWSER=firefox ^
    -e HEADLESS=true ^
    -v "%cd%/test_reports:/tests/test_reports" ^
    -v "%cd%/test_screenshots:/tests/test_screenshots" ^
    todo-tests python -m pytest -v --html=test_reports/unit_report.html --self-contained-html -m "not integration"

set EXIT_CODE=%ERRORLEVEL%

REM Restart backend and database
echo.
echo Restarting backend and database containers...
docker start todo_postgres todo_backend >nul 2>&1
echo Containers restarted

echo.
echo ========================================
echo Unit Tests Complete
echo Report: test_reports/unit_report.html
echo Screenshots: test_screenshots/
echo ========================================

exit /b %EXIT_CODE%
