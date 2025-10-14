@echo off
REM Batch script to run integration tests on Windows
REM Run Integration Tests (Real APIs - Full System)
REM Requires backend and database to be running

echo ========================================
echo Running INTEGRATION Tests (Real Backend)
echo ========================================
echo.

REM Check if all required containers are running
echo Checking if all containers are running...
set ALL_RUNNING=1

docker ps --filter "name=frontend" --filter "status=running" --format "{{.Names}}" | findstr /r "frontend" >nul
if errorlevel 1 set ALL_RUNNING=0

docker ps --filter "name=backend" --filter "status=running" --format "{{.Names}}" | findstr /r "backend" >nul
if errorlevel 1 set ALL_RUNNING=0

docker ps --filter "name=postgres" --filter "status=running" --format "{{.Names}}" | findstr /r "postgres" >nul
if errorlevel 1 set ALL_RUNNING=0

if %ALL_RUNNING%==0 (
    echo Not all required containers are running. Starting all services...
    docker-compose up -d
    echo Waiting for services to be ready...
    timeout /t 10 /nobreak >nul
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

REM Run tests
echo Running integration tests...
docker run --rm ^
    --network %NETWORK% ^
    -e TEST_MODE=integration ^
    -e FRONTEND_URL=http://frontend:3000 ^
    -e BACKEND_URL=http://backend:5000 ^
    -e DB_HOST=todo_postgres ^
    -e DB_PORT=5432 ^
    -e POSTGRES_DB=tododb ^
    -e POSTGRES_USER=todouser ^
    -e POSTGRES_PASSWORD=todopass ^
    -e BROWSER=firefox ^
    -e HEADLESS=true ^
    -v "%cd%/test_reports:/tests/test_reports" ^
    -v "%cd%/test_screenshots:/tests/test_screenshots" ^
    todo-tests python -m pytest test_todo_crud.py -v --html=test_reports/integration_report.html --self-contained-html

set EXIT_CODE=%ERRORLEVEL%

echo.
echo ========================================
echo Integration Tests Complete
echo Report: test_reports/integration_report.html
echo Screenshots: test_screenshots/
echo ========================================

exit /b %EXIT_CODE%
