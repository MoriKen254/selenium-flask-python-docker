# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack microservices Todo application with React+TypeScript frontend, Flask backend, and PostgreSQL database. All components run in Docker containers. The project features a unique **dual-mode testing strategy** where the same Selenium test code can run in either unit mode (mocked APIs) or integration mode (real backend).

## Architecture

- **Frontend**: React 18 + TypeScript (port 3000) - Single-page application with type-safe API interfaces
- **Backend**: Flask 3.0 REST API (port 5000) - Python 3.11 with psycopg2 for PostgreSQL
- **Database**: PostgreSQL 15 (port 5432) - Initialized via `backend/init.sql`
- **Admin Tool**: CloudBeaver (port 8978) - Web-based database management

### Key Architecture Patterns

**Database Connection**: Backend uses `get_db_connection()` helper that creates connections using `DATABASE_URL` environment variable. Each request opens and closes a connection (no connection pooling).

**CORS**: Flask backend has CORS enabled to accept requests from the React frontend on different ports.

**TypeScript Types**: Frontend has custom type definitions in `frontend/src/types/todo.ts` defining `Todo`, `NewTodo`, and `UpdateTodo` interfaces. These must stay in sync with the backend API responses.

**Datetime Serialization**: Backend uses `serialize_datetime()` to convert Python datetime objects to ISO strings before sending to frontend.

## Development Commands

### Starting the Application

```bash
# Start all services
docker-compose up

# Start specific service
docker-compose up frontend

# Rebuild after code changes
docker-compose up --build

# Run in background
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (clear database)
docker-compose down -v
```

### Running Tests

**Backend API Tests** (94% coverage, 40 test cases):
```bash
# Inside backend container
docker exec -it todo_backend pytest -v --cov=. --cov-report=html --cov-report=term

# Or from backend directory on host
cd backend
pytest -v --cov=. --cov-report=html --cov-report=term
```

**Frontend Selenium Tests** (dual-mode):

The test system has two modes controlled by `TEST_MODE` environment variable:
- **Unit mode**: Tests run against frontend only with browser-injected mocks (`mocks/api_interceptor.js`)
- **Integration mode**: Tests run against full system with real backend

```bash
# Run ALL tests (recommended) - Rebuilds images and runs backend + frontend tests
# Linux/Mac
cd tests/scripts
./run_all_tests.sh

# Windows CMD
cd tests\scripts
run_all_tests.bat

# Run individual test suites
# Linux/Mac
cd tests/scripts
./run_unit_tests.sh           # Fast, no backend needed
./run_integration_tests.sh    # Full E2E, requires all services

# Windows PowerShell
cd tests\scripts
.\run_unit_tests.ps1
.\run_integration_tests.ps1

# Windows CMD
cd tests\scripts
run_unit_tests.bat
run_integration_tests.bat

# Run specific test
./run_unit_tests.sh test_todo_crud.py::TestTodoCreation::test_create_todo_with_title_only
```

### Accessing Services

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- API Docs: http://localhost:5000 (returns endpoint list)
- Health Check: http://localhost:5000/health
- CloudBeaver: http://localhost:8978

### Database Management with CloudBeaver

CloudBeaver provides a web-based interface for managing the PostgreSQL database:

1. Navigate to http://localhost:8978
2. Complete the initial setup wizard with default admin credentials:
   - **Admin Username**: `todouser`
   - **Admin Password**: `Password_00`
3. Create a new database connection:
   - **Host**: `postgres` (or `localhost` if connecting from host machine)
   - **Port**: `5432`
   - **Database**: `tododb`
   - **Username**: `todouser`
   - **Password**: `todopass`
4. Browse the database schema, run SQL queries, and manage data through the UI

**Note**: Use internal DNS name `postgres` when connecting from within Docker network, or `localhost` when connecting from host machine.

## Testing Strategy Deep Dive

### Dual-Mode Testing Architecture

**Key Concept**: The same test code runs in two modes by switching `TEST_MODE` environment variable.

**Unit Mode Implementation**:
1. `conftest.py` fixture detects `TEST_MODE=unit`
2. Reads `mocks/api_interceptor.js` JavaScript file
3. Injects script into browser using `driver.execute_script()`
4. Interceptor overrides `window.fetch()` and `XMLHttpRequest`
5. All API calls get intercepted and return mock responses
6. Mock data store maintained in browser memory

**Integration Mode Implementation**:
- No interceptor injected
- Frontend makes real HTTP requests to Flask backend
- Tests verify actual database operations

**Configuration Files**:
- `tests/.env.unit` - Unit mode configuration
- `tests/.env.integration` - Integration mode configuration
- `tests/config.py` - TestConfig class that reads environment variables

**Page Object Model**:
- `tests/pages/todo_page.py` - Abstracts all UI interactions
- Methods like `create_todo()`, `toggle_todo_completion()`, `edit_todo()` work in both modes
- 30+ reusable methods for todo operations

**Mode-Specific Tests**:
Use decorators to skip tests that don't apply to a mode:
```python
@pytest.mark.skipif(is_integration_mode(), reason="Unit-only test")
def test_mock_manipulation(browser, mock_api):
    # Test mock data manipulation

@pytest.mark.skipif(is_unit_mode(), reason="Integration-only test")
def test_database_persistence(browser):
    # Test data persists across page refreshes
```

### Test Reports and Artifacts

- **HTML Reports**: `tests/test_reports/unit_report.html` and `integration_report.html`
- **Screenshots**: `tests/test_screenshots/` (captured on test failure)
- **Coverage**: `backend/htmlcov/index.html` (backend only)

## Code Editing Guidelines

### Backend Changes

**When editing `backend/app.py`**:
- All endpoints must return JSON responses
- Use `get_db_connection()` helper for database access
- Always use `RealDictCursor` for dictionary-style results
- Call `serialize_datetime()` on datetime fields before returning
- Close connections with `conn.close()` in try/finally or after operations
- Return appropriate HTTP status codes (200, 201, 400, 404, 500)
- Update `backend/tests/test_api.py` with new test cases (target >90% coverage)

**When editing database schema**:
- Modify `backend/init.sql`
- Restart containers to reinitialize: `docker-compose down -v && docker-compose up`
- Update TypeScript types in `frontend/src/types/todo.ts` to match

### Frontend Changes

**When editing `frontend/src/App.tsx`**:
- Maintain strict TypeScript typing (no `any` types)
- Use async/await for all API calls
- Handle loading states and errors gracefully
- Update types in `frontend/src/types/todo.ts` if API contract changes
- CSS classes must match selectors in `tests/pages/todo_page.py`

**Important CSS Selectors** (used by tests):
- `.todo-item` - Each todo card
- `.todo-title` - Todo title text
- `.todo-description` - Todo description text
- `.checkbox` - Completion checkbox
- `.btn-edit` - Edit button
- `.btn-delete` - Delete button
- `.btn-success` - Save button (in edit mode)
- `.empty-state` - Empty state message
- `.error-message` - Error display

**If changing UI structure**: Update `tests/pages/todo_page.py` locators to match.

### Test Changes

**Adding new tests**:
1. Write test in `tests/test_todo_crud.py` using Page Object Model methods
2. Ensure it works in both modes by default (no mode-specific code)
3. Use `@pytest.mark.skipif()` only if test is genuinely mode-specific
4. Add appropriate waits using `wait_for_todo_to_appear()`, `wait_for_todo_count()`, etc.
5. Tests must clean up after themselves in integration mode (delete created todos)

**Adding new Page Object methods**:
- Edit `tests/pages/todo_page.py`
- Follow existing patterns: use explicit waits, return typed data
- Add docstrings explaining what the method does
- Test the new method in both unit and integration modes

**Modifying mock behavior**:
- Edit `tests/mocks/api_interceptor.js`
- The interceptor intercepts `fetch()` and `XMLHttpRequest` at browser level
- Mock data stored in `window.__MOCK_TODOS__` (persists across page refreshes)
- Injected via Chrome DevTools Protocol (CDP) before page load for proper timing
- Available programmatically via `window.__TEST_API__`:
  - `setMockData(todos)` - Replace all mock todos (persists across refreshes)
  - `getMockData()` - Get current mock todos
  - `resetMockData()` - Reset to default mock data
  - `addMockTodo(todo)` - Add a single todo to mock store

## Common Development Tasks

### Running all tests (comprehensive)
```bash
# This rebuilds images and runs backend unit, frontend unit, and integration tests
cd tests/scripts
./run_all_tests.sh              # Linux/Mac
run_all_tests.bat               # Windows CMD
```

### Running a single test file
```bash
cd tests/scripts
./run_unit_tests.sh test_todo_crud.py
```

### Running tests with visible browser (debug mode)
```bash
cd tests/scripts
export HEADLESS=false
./run_unit_tests.sh
```

### Rebuilding after dependency changes
```bash
# Frontend (package.json changed)
docker-compose up --build frontend

# Backend (requirements.txt changed)
docker-compose up --build backend

# Tests (tests/requirements.txt changed)
cd tests
docker build -t todo-tests .
```

### Viewing backend logs
```bash
docker-compose logs backend
docker-compose logs -f backend  # Follow mode

# Or use container name directly
docker logs todo_backend
docker logs -f todo_backend  # Follow mode
```

### Resetting database to initial state
```bash
docker-compose down -v
docker-compose up
```

### Running backend tests with coverage
```bash
# Using container name
docker exec -it todo_backend pytest -v --cov=. --cov-report=term --cov-report=html

# Or from backend directory on host (if Python is installed locally)
cd backend
pytest -v --cov=. --cov-report=term --cov-report=html
```

## Environment Variables

**Backend** (`.env` file in root):
- `POSTGRES_DB` - Database name (default: tododb)
- `POSTGRES_USER` - Database user (default: todouser)
- `POSTGRES_PASSWORD` - Database password (default: todopass)
- `FLASK_ENV` - Flask environment (development/production)
- `DATABASE_URL` - Full PostgreSQL connection string

**Frontend**:
- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:5000)

**Tests** (in `tests/.env.unit` or `tests/.env.integration`):
- `TEST_MODE` - unit or integration
- `FRONTEND_URL` - Frontend URL for tests
- `BACKEND_URL` - Backend URL (integration mode only)
- `BROWSER` - chrome or firefox
- `HEADLESS` - true or false
- `SCREENSHOT_ON_FAILURE` - Capture screenshots on test failures

## Docker Network

All services run on `todo_network` bridge network. Services communicate using container names:
- Frontend → Backend: `http://backend:5000`
- Backend → Database: `postgresql://todouser:todopass@postgres:5432/tododb`
- Tests → Frontend: `http://frontend:3000`
- Tests → Backend: `http://backend:5000` (integration mode)

When running tests in Docker, use container names. When accessing from host machine, use `localhost`.

### Service Name Reference

| Service | Container Name | Internal DNS | Host Access |
|---------|---------------|--------------|-------------|
| PostgreSQL | `todo_postgres` | `postgres` | `localhost:5432` |
| Backend | `todo_backend` | `backend` | `localhost:5000` |
| Frontend | `todo_frontend` | `frontend` | `localhost:3000` |
| CloudBeaver | `todo_cloudbeaver` | `cloudbeaver` | `localhost:8978` |

**Docker Commands**: Use container names (e.g., `docker exec -it todo_backend bash`)
**Inter-service Communication**: Use internal DNS names (e.g., `http://backend:5000`)
**Browser/Host Access**: Use localhost (e.g., `http://localhost:3000`)

## API Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/health` | Health check | None | `{status, database}` |
| GET | `/api/todos` | Get all todos | None | `Todo[]` |
| GET | `/api/todos/:id` | Get single todo | None | `Todo` or 404 |
| POST | `/api/todos` | Create todo | `{title, description?, completed?}` | `Todo` (201) |
| PUT | `/api/todos/:id` | Update todo | `{title?, description?, completed?}` | `Todo` |
| DELETE | `/api/todos/:id` | Delete todo | None | `{message}` |

**Todo Object Structure**:
```json
{
  "id": 1,
  "title": "Task title",
  "description": "Optional description",
  "completed": false,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

## Windows-Specific Notes

- PowerShell scripts use backtick `` ` `` for line continuation, `${PWD}` for current directory
- CMD scripts use `^` for line continuation, `%cd%` for current directory
- Test runner scripts auto-detect Docker network and start containers if needed
- Path separators: Use `/` in Docker commands, `\` in Windows file paths
- Line endings: Git should use `autocrlf=input` to prevent issues with shell scripts

See `WINDOWS.md` for detailed Windows instructions.

## Troubleshooting

**Port conflicts**: Change ports in `docker-compose.yaml` or kill processes using:
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <pid> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

**Database connection errors**: Check PostgreSQL health with `docker-compose ps` and `docker-compose logs postgres`

**Frontend can't reach backend**: Verify `REACT_APP_API_URL` matches your backend URL

**Tests fail with "connection refused"**: Ensure all required containers are running for the test mode

**"Stale element reference" in tests**: Page Object Model re-queries elements after updates to prevent this

## Test Directory Structure

The `tests/` directory is organized as follows:

```
tests/
├── scripts/              # All test runner scripts
│   ├── run_all_tests.sh/bat       # Comprehensive test runner (recommended)
│   ├── run_unit_tests.sh/bat/ps1  # Frontend unit tests only
│   ├── run_integration_tests.sh/bat/ps1  # Integration tests only
│   └── README.md         # Test scripts documentation
├── .archived/            # Debug and diagnostic tests (not in main suite)
├── pages/                # Page Object Model classes
├── mocks/                # API mock interceptors
├── test_todo_crud.py     # Main test suite (works in both modes)
├── test_reports/         # HTML test reports
└── test_screenshots/     # Failure screenshots
```

## Additional Documentation

- `README.md` - Comprehensive project documentation with setup instructions
- `TESTING.md` - Detailed testing guide with architecture diagrams and examples
- `WINDOWS.md` - Windows-specific development and testing instructions
- `tests/QUICKSTART.md` - Quick reference for running tests
- `tests/scripts/README.md` - Test scripts documentation
- `tests/.archived/README.md` - Archived debug tests documentation
