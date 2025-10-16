# Test Scripts Directory

This directory contains all test runner scripts for the project.

## Quick Start

### Run All Tests (Recommended)

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

## Individual Test Suites

### Backend Unit Tests
Backend API tests with pytest and coverage reporting.

**Linux/Mac:**
```bash
# From project root
docker-compose up -d backend postgres
docker exec todo_backend pytest -v --cov=. --cov-report=html --cov-report=term
```

**Coverage Report:** `backend/htmlcov/index.html`

### Frontend Unit Tests
Selenium tests with mocked APIs (no backend required).

**Linux/Mac:**
```bash
cd tests/scripts
./run_unit_tests.sh
```

**Windows:**
```cmd
cd tests\scripts
run_unit_tests.bat
```

**Report:** `tests/test_reports/unit_report.html`

### Integration Tests
Full end-to-end tests with real backend and database.

**Linux/Mac:**
```bash
cd tests/scripts
./run_integration_tests.sh
```

**Windows:**
```cmd
cd tests\scripts
run_integration_tests.bat
```

**Report:** `tests/test_reports/integration_report.html`

## Test Script Files

### Comprehensive Test Runners
- `run_all_tests.sh` - Linux/Mac comprehensive test runner
- `run_all_tests.bat` - Windows comprehensive test runner

### Individual Test Runners
- `run_unit_tests.sh` - Linux/Mac frontend unit tests
- `run_unit_tests.bat` - Windows frontend unit tests
- `run_unit_tests.ps1` - PowerShell frontend unit tests
- `run_integration_tests.sh` - Linux/Mac integration tests
- `run_integration_tests.bat` - Windows integration tests
- `run_integration_tests.ps1` - PowerShell integration tests

## Test Reports

All test reports are generated in `tests/test_reports/`:
- `unit_report.html` - Frontend unit test results
- `integration_report.html` - Integration test results
- Backend coverage: `backend/htmlcov/index.html`

## Screenshots

Test failure screenshots are saved to `tests/test_screenshots/`.

## Exit Codes

All scripts return:
- `0` - All tests passed
- `1` - One or more tests failed

This allows you to use them in CI/CD pipelines:
```bash
./run_all_tests.sh && echo "Deploy!" || echo "Fix tests first"
```

## Notes

- The comprehensive test runners (`run_all_tests.*`) rebuild Docker images before running tests
- Individual test runners reuse existing containers for faster iteration
- Unit tests stop the backend container to ensure tests use mocked APIs
- Integration tests require all services (frontend, backend, database) to be running
