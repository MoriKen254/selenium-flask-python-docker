# Testing Guide

This document explains the comprehensive testing strategy for the Todo application, covering both backend API tests and frontend Selenium tests.

## Table of Contents

- [Overview](#overview)
- [Backend API Testing](#backend-api-testing)
- [Frontend Selenium Testing](#frontend-selenium-testing)
- [Dual-Mode Testing Strategy](#dual-mode-testing-strategy)
- [Running Tests](#running-tests)
- [Writing New Tests](#writing-new-tests)
- [Troubleshooting](#troubleshooting)

---

## Overview

The application has two testing layers:

1. **Backend API Tests** - pytest-based unit tests for Flask REST API endpoints
2. **Frontend Selenium Tests** - Browser automation tests with dual-mode execution

---

## Backend API Testing

### Location

- `backend/tests/test_api.py` - All backend API test cases
- `backend/pytest.ini` - Pytest configuration
- `backend/.coveragerc` - Coverage configuration

### Test Coverage

- ✅ 40 comprehensive test cases
- ✅ 94% code coverage
- ✅ All CRUD operations tested
- ✅ Edge cases and error handling
- ✅ Data integrity and concurrency tests

### Running Backend Tests

**From host machine:**

```bash
cd backend
pytest -v --cov=. --cov-report=html --cov-report=term
```

**Using Docker:**

```bash
docker exec -it todo_backend pytest -v --cov=. --cov-report=html --cov-report=term
```

### Test Categories

- **Health & Root Endpoints** - Service availability
- **GET Operations** - Retrieve todos (all, single, not found)
- **POST Operations** - Create todos with validation
- **PUT Operations** - Update todos (title, description, completion status)
- **DELETE Operations** - Remove todos
- **Edge Cases** - Special characters, unicode, long strings, malformed data
- **Data Integrity** - Timestamp validation, field immutability
- **Concurrency** - Multiple operations in sequence

### Coverage Report

View detailed coverage report:

```bash
open backend/htmlcov/index.html  # macOS
start backend/htmlcov/index.html  # Windows
```

---

## Frontend Selenium Testing

### Architecture

The frontend uses a **dual-mode testing strategy** that allows the same test code to run in two different modes:

1. **Unit Mode** (Isolated) - Tests run against frontend only with mocked APIs
2. **Integration Mode** (E2E) - Tests run against full system with real backend

### Key Design Principles

✅ **Zero Code Duplication** - Single test codebase for both modes
✅ **Configuration-Based Switching** - Change mode via environment variables
✅ **Browser-Level API Mocking** - JavaScript injection intercepts fetch/XHR
✅ **Page Object Model** - Reusable abstractions for UI interactions
✅ **Mode-Agnostic Tests** - Most tests work identically in both modes

---

## Dual-Mode Testing Strategy

### How It Works

#### Unit Mode (Mocked APIs)

```
┌─────────────────────────────────────────┐
│  Selenium WebDriver                     │
│  ├─ Browser (Chrome/Firefox)            │
│  │   ├─ React Frontend                  │
│  │   └─ API Interceptor (injected JS)   │
│  │       └─ Mock Data Store             │
│  └─ Test Code (Python)                  │
└─────────────────────────────────────────┘
```

When TEST_MODE=unit:

1. Selenium loads the React frontend
2. Python injects `api_interceptor.js` into browser
3. JavaScript intercepts all `fetch()` and `XMLHttpRequest` calls
4. Mock responses returned from in-memory store
5. Tests interact with UI, which uses mocked APIs

**Advantages:**

- ⚡ Fast execution (no network calls)
- 🚀 No backend/database dependencies
- 🔄 Easy to test edge cases with mock data
- 💻 Great for rapid development feedback

#### Integration Mode (Real APIs)

```
┌─────────────────────────────────────────┐
│  Selenium WebDriver                     │
│  ├─ Browser                             │
│  │   └─ React Frontend                  │
│  │       └─ Real HTTP Requests          │
│  └─ Test Code (Python)                  │
└─────────────────────────────────────────┘
         │
         ├── HTTP → Flask Backend
         │            └── PostgreSQL
```

When TEST_MODE=integration:

1. Selenium loads the React frontend
2. No interceptor injected
3. Frontend makes real HTTP requests to Flask backend
4. Backend queries PostgreSQL database
5. Tests verify complete end-to-end behavior

**Advantages:**

- ✅ Tests real system interactions
- 🔍 Catches integration issues
- 📊 Validates database operations
- 🌐 Tests network error handling

### Configuration Files

**`.env.unit`** - Unit test settings

```bash
TEST_MODE=unit
FRONTEND_URL=http://frontend:3000
BACKEND_URL=http://backend:5000  # Not used in unit mode
BROWSER=chrome
HEADLESS=true
IMPLICIT_WAIT=10
PAGE_LOAD_TIMEOUT=30
SCREENSHOT_ON_FAILURE=true
SCREENSHOTS_DIR=./test_screenshots
```

**`.env.integration`** - Integration test settings

```bash
TEST_MODE=integration
FRONTEND_URL=http://frontend:3000
BACKEND_URL=http://backend:5000
BROWSER=chrome
HEADLESS=true
IMPLICIT_WAIT=10
PAGE_LOAD_TIMEOUT=30
SCREENSHOT_ON_FAILURE=true
SCREENSHOTS_DIR=./test_screenshots
ENABLE_REQUEST_LOGGING=true
```

### API Interceptor Mechanism

The `mocks/api_interceptor.js` file provides browser-level API mocking:

**Key Features:**

- Intercepts both `fetch()` and `XMLHttpRequest` (for Axios compatibility)
- Maintains in-memory mock data store
- Simulates network delays for realistic testing
- Provides programmatic control via `window.__TEST_API__`

**Available Methods:**

```javascript
// Reset mock data to initial state
window.__TEST_API__.resetMockData();

// Set custom mock data
window.__TEST_API__.setMockData([
  { id: 1, title: 'Test', description: 'Test', completed: false },
]);

// Get current mock data
const data = window.__TEST_API__.getMockData();

// Add new mock todo
window.__TEST_API__.addMockTodo({
  title: 'New Todo',
  description: 'Description',
  completed: false,
});
```

**Request Handling:**

- `GET /api/todos` → Returns all mock todos
- `GET /api/todos/:id` → Returns specific todo or 404
- `POST /api/todos` → Creates new todo with auto-incremented ID
- `PUT /api/todos/:id` → Updates existing todo
- `DELETE /api/todos/:id` → Removes todo from mock store

### Page Object Model

The `pages/todo_page.py` provides a clean abstraction layer:

```python
class TodoPage:
    def create_todo(self, title: str, description: str = "")
    def get_all_todos(self) -> List[Dict]
    def find_todo_by_title(self, title: str) -> Optional[Dict]
    def toggle_todo_completion(self, todo_title: str)
    def edit_todo(self, old_title: str, new_title: str, new_description: str)
    def delete_todo(self, todo_title: str)
    def wait_for_todo_count(self, expected_count: int, timeout: int)
    # ... 30+ more methods
```

**Benefits:**

- Works identically in both unit and integration modes
- Encapsulates all UI interactions
- Provides waiting strategies for async operations
- Makes tests readable and maintainable

---

## Running Tests

### Prerequisites

**For Unit Tests:**

- Frontend container running: `docker-compose up frontend -d`

**For Integration Tests:**

- All containers running: `docker-compose up -d`

### Method 1: Using Test Runner Scripts (Recommended)

#### Linux/Mac

**Unit Tests (Mocked APIs):**

```bash
cd tests
./run_unit_tests.sh
```

**Integration Tests (Real Backend):**

```bash
cd tests
./run_integration_tests.sh
```

**Run specific test file:**

```bash
./run_unit_tests.sh test_todo_crud.py
```

**Run specific test class:**

```bash
./run_unit_tests.sh test_todo_crud.py::TestTodoCreation
```

**Run specific test method:**

```bash
./run_unit_tests.sh test_todo_crud.py::TestTodoCreation::test_create_todo_with_title_only
```

#### Windows

**Option 1: PowerShell (Recommended)**

```powershell
cd tests

# Unit tests
.\run_unit_tests.ps1

# Integration tests
.\run_integration_tests.ps1
```

**Option 2: Command Prompt (CMD)**

```cmd
cd tests

# Unit tests
run_unit_tests.bat

# Integration tests
run_integration_tests.bat
```

**Features of Windows scripts:**
- ✅ Automatically checks if containers are running
- ✅ Starts required containers if needed
- ✅ Creates test artifact directories
- ✅ Auto-detects Docker network name
- ✅ Colored output (PowerShell only)
- ✅ Generates HTML reports

### Method 2: Manual pytest Execution

**Unit Mode:**

```bash
cd tests
export TEST_MODE=unit
export FRONTEND_URL=http://localhost:3000
export BROWSER=chrome
export HEADLESS=true
pytest -v
```

**Integration Mode:**

```bash
cd tests
export TEST_MODE=integration
export FRONTEND_URL=http://localhost:3000
export BACKEND_URL=http://localhost:5000
export BROWSER=chrome
export HEADLESS=true
pytest -v
```

### Method 3: Using Docker Directly

**Build test container:**

```bash
cd tests
docker build -t todo-tests .
```

#### Linux/Mac

**Run unit tests:**

```bash
docker run --rm \
  --network selenium-flask-python-docker_default \
  -e TEST_MODE=unit \
  -e FRONTEND_URL=http://frontend:3000 \
  -v $(pwd)/test_reports:/tests/test_reports \
  -v $(pwd)/test_screenshots:/tests/test_screenshots \
  todo-tests
```

**Run integration tests:**

```bash
docker run --rm \
  --network selenium-flask-python-docker_default \
  -e TEST_MODE=integration \
  -e FRONTEND_URL=http://frontend:3000 \
  -e BACKEND_URL=http://backend:5000 \
  -v $(pwd)/test_reports:/tests/test_reports \
  -v $(pwd)/test_screenshots:/tests/test_screenshots \
  todo-tests
```

#### Windows PowerShell

**Run unit tests:**

```powershell
docker run --rm `
  --network selenium-flask-python-docker_default `
  -e TEST_MODE=unit `
  -e FRONTEND_URL=http://frontend:3000 `
  -v "${PWD}/test_reports:/tests/test_reports" `
  -v "${PWD}/test_screenshots:/tests/test_screenshots" `
  todo-tests
```

**Run integration tests:**

```powershell
docker run --rm `
  --network selenium-flask-python-docker_default `
  -e TEST_MODE=integration `
  -e FRONTEND_URL=http://frontend:3000 `
  -e BACKEND_URL=http://backend:5000 `
  -v "${PWD}/test_reports:/tests/test_reports" `
  -v "${PWD}/test_screenshots:/tests/test_screenshots" `
  todo-tests
```

#### Windows Command Prompt

**Run unit tests:**

```cmd
docker run --rm ^
  --network selenium-flask-python-docker_default ^
  -e TEST_MODE=unit ^
  -e FRONTEND_URL=http://frontend:3000 ^
  -v "%cd%/test_reports:/tests/test_reports" ^
  -v "%cd%/test_screenshots:/tests/test_screenshots" ^
  todo-tests
```

**Run integration tests:**

```cmd
docker run --rm ^
  --network selenium-flask-python-docker_default ^
  -e TEST_MODE=integration ^
  -e FRONTEND_URL=http://frontend:3000 ^
  -e BACKEND_URL=http://backend:5000 ^
  -v "%cd%/test_reports:/tests/test_reports" ^
  -v "%cd%/test_screenshots:/tests/test_screenshots" ^
  todo-tests
```

**Important Notes for Windows:**
- PowerShell: Use backticks `` ` `` for line continuation and `${PWD}` for current directory
- CMD: Use `^` for line continuation and `%cd%` for current directory
- Path should be `/tests/` not `/app/` (matches Dockerfile WORKDIR)
- Network name may vary - check with `docker network ls`

### Test Reports

HTML reports are generated after each run:

- **Unit Tests**: `tests/test_reports/unit_report.html`
- **Integration Tests**: `tests/test_reports/integration_report.html`

Screenshots on failure saved to: `tests/test_screenshots/`

---

## Writing New Tests

### Example: Mode-Agnostic Test

This test works in both unit and integration modes:

```python
def test_create_and_complete_todo(browser):
    """Test creating a todo and marking it complete"""
    page = TodoPage(browser)
    page.wait_for_page_load()

    # Create todo
    page.create_todo("Buy groceries", "Milk, eggs, bread")
    page.wait_for_todo_to_appear("Buy groceries")

    # Verify created
    todo = page.find_todo_by_title("Buy groceries")
    assert todo is not None
    assert todo['description'] == "Milk, eggs, bread"
    assert todo['completed'] is False

    # Mark complete
    page.toggle_todo_completion("Buy groceries")
    page.wait_for_todo_status("Buy groceries", completed=True)

    # Verify completed
    todo = page.find_todo_by_title("Buy groceries")
    assert todo['completed'] is True
```

### Example: Unit-Only Test

Test specific to unit mode (testing mock manipulation):

```python
import pytest
from config import is_integration_mode

@pytest.mark.skipif(is_integration_mode(), reason="Unit-only test")
def test_mock_data_manipulation(browser, mock_api):
    """Test programmatic mock data control"""
    page = TodoPage(browser)

    # Set custom mock data
    mock_api.set_mock_data([
        {'id': 999, 'title': 'Mocked Todo', 'description': 'Test', 'completed': False}
    ])

    browser.refresh()
    page.wait_for_page_load()

    # Verify mock data appears
    todo = page.find_todo_by_title("Mocked Todo")
    assert todo is not None
    assert todo['id'] == 999
```

### Example: Integration-Only Test

Test specific to integration mode (testing persistence):

```python
import pytest
from config import is_unit_mode

@pytest.mark.skipif(is_unit_mode(), reason="Integration-only test")
def test_data_persists_after_page_refresh(browser):
    """Test that data persists in database"""
    page = TodoPage(browser)
    page.wait_for_page_load()

    # Create todo
    page.create_todo("Persistent Todo")
    page.wait_for_todo_to_appear("Persistent Todo")

    # Refresh page
    browser.refresh()
    page.wait_for_page_load()

    # Verify still exists (would fail in unit mode with mock reset)
    todo = page.find_todo_by_title("Persistent Todo")
    assert todo is not None
```

### Best Practices

1. **Prefer Mode-Agnostic Tests** - Write tests that work in both modes when possible
2. **Use Page Object Model** - Always use TodoPage methods, never raw Selenium calls
3. **Wait for Elements** - Use explicit waits (`wait_for_todo_to_appear`, `wait_for_todo_count`)
4. **Clean Up After Tests** - Delete created todos at end of test (integration mode)
5. **Use Descriptive Names** - Test names should clearly describe what's being tested
6. **Test One Thing** - Each test should verify a single behavior
7. **Add Markers** - Use `@pytest.mark.smoke` for quick tests, `@pytest.mark.slow` for long tests

### Adding New Page Object Methods

To add a new interaction to the Page Object Model:

```python
# pages/todo_page.py

def search_todos(self, search_term: str) -> None:
    """Search for todos by keyword"""
    search_input = self.wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
    )
    search_input.clear()
    search_input.send_keys(search_term)
    time.sleep(0.5)  # Wait for search results to update
```

Then use in tests:

```python
def test_search_functionality(browser):
    page = TodoPage(browser)
    page.create_todo("Buy milk")
    page.create_todo("Buy eggs")
    page.search_todos("milk")

    todos = page.get_all_todos()
    assert len(todos) == 1
    assert todos[0]['title'] == "Buy milk"
```

---

## Troubleshooting

### Issue: "No mock data found" in unit mode

**Cause:** API interceptor not injected properly
**Solution:** Ensure frontend is fully loaded before tests start

```python
def test_example(browser):
    page = TodoPage(browser)
    page.wait_for_page_load()  # Always call this first!
    # ... rest of test
```

### Issue: Tests pass in unit mode but fail in integration mode

**Cause:** Timing differences or database state issues
**Solution:** Add explicit waits and clean up test data

```python
def test_example(browser):
    page = TodoPage(browser)

    # Create todo
    page.create_todo("Test Todo")
    page.wait_for_todo_to_appear("Test Todo")  # Wait for backend response

    # Test logic here...

    # Clean up (integration mode)
    if is_integration_mode():
        page.delete_todo("Test Todo")
```

### Issue: "Element not interactable" errors

**Cause:** Element not ready or obscured
**Solution:** Use Page Object Model methods which include proper waits

```python
# ❌ Bad - raw Selenium
button = driver.find_element(By.ID, "submit")
button.click()

# ✅ Good - Page Object Model
page.create_todo("Test")  # Includes all necessary waits
```

### Issue: Tests fail with "connection refused" in integration mode

**Cause:** Backend not ready or incorrect URLs
**Solution:**

1. Verify all containers running: `docker-compose ps`
2. Check container logs: `docker-compose logs backend`
3. Verify environment variables:
   ```bash
   echo $FRONTEND_URL
   echo $BACKEND_URL
   ```

### Issue: Screenshots not saved on failure

**Cause:** Screenshot directory doesn't exist or permissions issue
**Solution:**

```bash
mkdir -p tests/test_screenshots
chmod 777 tests/test_screenshots
```

### Issue: "Stale element reference" errors

**Cause:** DOM updated after element was located
**Solution:** Re-query elements after page updates

```python
# Page Object Model handles this automatically
page.toggle_todo_completion("Test")
page.wait_for_todo_status("Test", completed=True)  # Re-queries element
```

### Debugging Tips

**1. Run tests in non-headless mode:**

```bash
export HEADLESS=false
pytest -v test_todo_crud.py::test_specific_test
```

**2. Add debugging breakpoints:**

```python
def test_example(browser):
    page = TodoPage(browser)
    page.create_todo("Test")

    import pdb; pdb.set_trace()  # Debugger here

    todo = page.find_todo_by_title("Test")
```

**3. Enable verbose logging:**

```python
# conftest.py - add to browser fixture
import logging
logging.basicConfig(level=logging.DEBUG)
```

**4. Inspect mock data (unit mode):**

```python
def test_example(browser, mock_api):
    # Check current mock data
    data = mock_api.get_mock_data()
    print(f"Mock data: {data}")
```

**5. Check browser console logs:**

```python
def test_example(browser):
    # ... test code ...

    # Print browser console logs
    for entry in browser.get_log('browser'):
        print(entry)
```

---

## Summary

This testing strategy provides:

✅ **Comprehensive Coverage** - Backend APIs + Frontend UI
✅ **Fast Feedback Loop** - Unit mode for rapid development
✅ **End-to-End Validation** - Integration mode for release confidence
✅ **Zero Code Duplication** - Single test codebase for both modes
✅ **Easy Maintenance** - Page Object Model abstracts UI changes
✅ **Flexible Execution** - Run tests locally or in Docker

**Recommended Workflow:**

1. **During Development:**

   - Run unit tests frequently for quick feedback
   - Use non-headless mode to see browser interactions
   - Add new tests as you add features

2. **Before Commits:**

   - Run full unit test suite
   - Ensure all tests pass
   - Check code coverage

3. **Before Releases:**

   - Run integration test suite
   - Verify all containers healthy
   - Review test reports and screenshots

4. **In CI/CD Pipeline:**
   - Run unit tests on every commit (fast)
   - Run integration tests on main branch (slower)
   - Fail pipeline if any tests fail

---

For questions or issues, please refer to the main README.md or open an issue in the repository.
