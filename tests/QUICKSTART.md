# Quick Start - Running Tests

## Recommended: Run All Tests

The easiest way to run all tests is to use the comprehensive test runner:

**Linux/Mac:**
```bash
cd tests/scripts
./run_all_tests.sh
```

**Windows:**
```cmd
cd tests\scripts
run_all_tests.bat
```

This will:
1. Rebuild all Docker images
2. Run backend unit tests (pytest with coverage)
3. Run frontend unit tests (Selenium with mocked APIs)
4. Run integration tests (Selenium with real backend)

## Running Individual Test Suites

### For Windows Users

**PowerShell (Recommended):**
```powershell
cd tests\scripts
.\run_unit_tests.ps1
.\run_integration_tests.ps1
```

**Command Prompt:**
```cmd
cd tests\scripts
run_unit_tests.bat
run_integration_tests.bat
```

### For Linux/Mac Users

```bash
cd tests/scripts
./run_unit_tests.sh
./run_integration_tests.sh
```

## What the Scripts Do

1. ✅ Check if required Docker containers are running
2. ✅ Start containers if needed
3. ✅ Create test artifact directories
4. ✅ Auto-detect the correct Docker network
5. ✅ Run tests in Docker container with proper configuration
6. ✅ Generate HTML reports

## View Test Reports

After tests complete:

**Windows:**
- Unit tests: `start test_reports\unit_report.html`
- Integration tests: `start test_reports\integration_report.html`

**Linux/Mac:**
- Unit tests: `open test_reports/unit_report.html` (Mac) or `xdg-open test_reports/unit_report.html` (Linux)
- Integration tests: Similar for `integration_report.html`

## Troubleshooting

### Error: Docker network not found

**Solution:** Start the application first:
```bash
docker-compose up -d
```

### Error: Cannot find test container image

**Solution:** Build the test image:
```bash
cd tests
docker build -t todo-tests .
```

### Tests fail to connect to frontend

**Solution:** Verify frontend is accessible:
```bash
# Check if frontend is running
docker ps | grep frontend

# Test frontend is responding
curl http://localhost:3000
```

## Manual Docker Commands

If you prefer to run Docker commands manually:

**Network name:** `selenium-flask-python-docker_todo_network` (auto-detected by scripts)

**PowerShell:**
```powershell
$network = docker network ls --filter "name=todo_network" --format "{{.Name}}" | Select-Object -First 1

# Unit tests
docker run --rm `
  --network $network `
  -e TEST_MODE=unit `
  -e FRONTEND_URL=http://frontend:3000 `
  -v "${PWD}/test_reports:/tests/test_reports" `
  -v "${PWD}/test_screenshots:/tests/test_screenshots" `
  todo-tests python -m pytest -v --html=test_reports/unit_report.html --self-contained-html -m "not integration"

# Integration tests
docker run --rm `
  --network $network `
  -e TEST_MODE=integration `
  -e FRONTEND_URL=http://frontend:3000 `
  -e BACKEND_URL=http://backend:5000 `
  -v "${PWD}/test_reports:/tests/test_reports" `
  -v "${PWD}/test_screenshots:/tests/test_screenshots" `
  todo-tests python -m pytest -v --html=test_reports/integration_report.html --self-contained-html
```

**Bash (Linux/Mac):**
```bash
network=$(docker network ls --filter "name=todo_network" --format "{{.Name}}" | head -n 1)

# Unit tests
docker run --rm \
  --network $network \
  -e TEST_MODE=unit \
  -e FRONTEND_URL=http://frontend:3000 \
  -v $(pwd)/test_reports:/tests/test_reports \
  -v $(pwd)/test_screenshots:/tests/test_screenshots \
  todo-tests python -m pytest -v --html=test_reports/unit_report.html --self-contained-html -m "not integration"

# Integration tests
docker run --rm \
  --network $network \
  -e TEST_MODE=integration \
  -e FRONTEND_URL=http://frontend:3000 \
  -e BACKEND_URL=http://backend:5000 \
  -v $(pwd)/test_reports:/tests/test_reports \
  -v $(pwd)/test_screenshots:/tests/test_screenshots \
  todo-tests python -m pytest -v --html=test_reports/integration_report.html --self-contained-html
```

## Test Directory Structure

```
tests/
├── scripts/              # All test runner scripts (run scripts from here!)
│   ├── run_all_tests.sh/bat       # Comprehensive test runner (recommended)
│   ├── run_unit_tests.sh/bat/ps1  # Frontend unit tests only
│   └── run_integration_tests.sh/bat/ps1  # Integration tests only
├── .archived/            # Debug and diagnostic tests (not in main suite)
├── test_todo_crud.py     # Main test suite
└── test_reports/         # HTML test reports generated here
```

## For More Details

- See [TESTING.md](../TESTING.md) for comprehensive testing documentation
- See [scripts/README.md](scripts/README.md) for detailed script documentation
