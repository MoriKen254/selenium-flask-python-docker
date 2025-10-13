# PowerShell script to run unit tests on Windows
# Run Unit Tests (Stubbed APIs - Frontend Only)
# No backend or database required

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running UNIT Tests (Stubbed APIs)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if frontend is running
Write-Host "Checking if frontend container is running..." -ForegroundColor Yellow
$frontendRunning = docker ps --filter "name=frontend" --filter "status=running" --format "{{.Names}}"

if (-not $frontendRunning) {
    Write-Host "Frontend container is not running. Starting frontend..." -ForegroundColor Yellow
    docker-compose up frontend -d
    Start-Sleep -Seconds 5
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
Write-Host "Running unit tests..." -ForegroundColor Yellow
docker run --rm `
    --network $network `
    -e TEST_MODE=unit `
    -e FRONTEND_URL=http://frontend:3000 `
    -e BROWSER=chrome `
    -e HEADLESS=true `
    -v "${PWD}/test_reports:/tests/test_reports" `
    -v "${PWD}/test_screenshots:/tests/test_screenshots" `
    todo-tests python -m pytest -v --html=test_reports/unit_report.html --self-contained-html -m "not integration"

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Unit Tests Complete" -ForegroundColor Cyan
Write-Host "Report: test_reports/unit_report.html" -ForegroundColor Green
Write-Host "Screenshots: test_screenshots/" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

exit $exitCode
