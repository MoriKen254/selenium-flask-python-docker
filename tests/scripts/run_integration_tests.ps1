# PowerShell script to run integration tests on Windows
# Run Integration Tests (Real APIs - Full System)
# Requires backend and database to be running

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running INTEGRATION Tests (Real Backend)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if all required containers are running
Write-Host "Checking if all containers are running..." -ForegroundColor Yellow
$frontendRunning = docker ps --filter "name=frontend" --filter "status=running" --format "{{.Names}}"
$backendRunning = docker ps --filter "name=backend" --filter "status=running" --format "{{.Names}}"
$postgresRunning = docker ps --filter "name=postgres" --filter "status=running" --format "{{.Names}}"

if (-not $frontendRunning -or -not $backendRunning -or -not $postgresRunning) {
    Write-Host "Not all required containers are running. Starting all services..." -ForegroundColor Yellow
    docker-compose up -d
    Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

# Create directories if they don't exist
Write-Host "Creating test artifact directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "test_reports" | Out-Null
New-Item -ItemType Directory -Force -Path "test_screenshots" | Out-Null

# Get the network name (try todo_network first, then fall back to default)
$network = docker network ls --filter "name=todo_network" --format "{{.Name}}" | Select-Object -First 1

if (-not $network) {
    Write-Host "ERROR: Docker network not found. Make sure docker-compose is running." -ForegroundColor Red
    Write-Host "Run: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

Write-Host "Using network: $network" -ForegroundColor Green
Write-Host ""

# Run tests
Write-Host "Running integration tests..." -ForegroundColor Yellow
docker run --rm `
    --network $network `
    -e TEST_MODE=integration `
    -e FRONTEND_URL=http://frontend:3000 `
    -e BACKEND_URL=http://backend:5000 `
    -e BROWSER=chrome `
    -e HEADLESS=true `
    -v "${PWD}/test_reports:/tests/test_reports" `
    -v "${PWD}/test_screenshots:/tests/test_screenshots" `
    todo-tests python -m pytest -v --html=test_reports/integration_report.html --self-contained-html

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Integration Tests Complete" -ForegroundColor Cyan
Write-Host "Report: test_reports/integration_report.html" -ForegroundColor Green
Write-Host "Screenshots: test_screenshots/" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

exit $exitCode
