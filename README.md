# Full-Stack Todo List Application

A complete microservices-based Todo List application built with React, Flask, and PostgreSQL, all orchestrated with Docker Compose.

## Architecture

This application follows a microservices architecture with the following components:

- **Frontend**: React 18 with TypeScript (Port 3000)
- **Backend**: Flask RESTful API (Port 5000)
- **Database**: PostgreSQL 15 (Port 5432)
- **Database Admin**: CloudBeaver web interface (Port 8978)

## Tech Stack

### Frontend

- React 18.2.0 with TypeScript 4.9.5
- Axios for API calls with type-safe interfaces
- Modern CSS with responsive design
- State management with React Hooks
- Strict TypeScript configuration for type safety
- Custom type definitions for API models

### Backend

- Python 3.11
- Flask 3.0.0
- Flask-CORS for cross-origin requests
- psycopg2 for PostgreSQL integration

### Database

- PostgreSQL 15 (Alpine)
- Automated schema initialization
- Indexed queries for performance

### Infrastructure

- Docker & Docker Compose
- Microservices architecture
- Health checks for service reliability
- Volume persistence for data

## Features

### Complete CRUD Operations

- **Create**: Add new todos with title and description
- **Read**: View all todos with real-time updates
- **Update**: Edit todo details and toggle completion status
- **Delete**: Remove todos with confirmation

### User Interface

- Clean, modern, and responsive design
- Real-time todo statistics (Total, Completed, Pending)
- Inline editing functionality
- Error handling with user-friendly messages
- Loading states for better UX

### API Endpoints

| Method | Endpoint         | Description         |
| ------ | ---------------- | ------------------- |
| GET    | `/health`        | Health check        |
| GET    | `/api/todos`     | Get all todos       |
| GET    | `/api/todos/:id` | Get a specific todo |
| POST   | `/api/todos`     | Create a new todo   |
| PUT    | `/api/todos/:id` | Update a todo       |
| DELETE | `/api/todos/:id` | Delete a todo       |

## Project Structure

```
.
├── backend/
│   ├── Dockerfile              # Backend container configuration
│   ├── requirements.txt        # Python dependencies
│   ├── app.py                 # Flask application with API endpoints
│   └── init.sql               # Database schema and initial data
├── frontend/
│   ├── Dockerfile             # Frontend container configuration
│   ├── package.json           # Node dependencies + TypeScript
│   ├── tsconfig.json         # TypeScript configuration
│   ├── public/
│   │   └── index.html        # HTML template
│   └── src/
│       ├── types/
│       │   └── todo.ts       # TypeScript type definitions
│       ├── index.tsx         # React entry point (TypeScript)
│       ├── index.css         # Global styles
│       ├── App.tsx           # Main React component (TypeScript)
│       ├── App.css           # Component styles
│       └── react-app-env.d.ts  # React type declarations
├── docker-compose.yaml        # Orchestration configuration
├── .env                       # Environment variables (git-ignored)
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine + Docker Compose (Linux)
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd selenium-flask-python-docker
```

### 2. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

The default configuration works out of the box. To customize, edit `.env`:

```env
# Database Configuration
POSTGRES_DB=tododb
POSTGRES_USER=todouser
POSTGRES_PASSWORD=todopass

# Backend Configuration
FLASK_ENV=development
FLASK_APP=app.py

# Frontend Configuration
REACT_APP_API_URL=http://localhost:5000
```

### 3. Start the Application

```bash
docker-compose up
```

This single command will:

- Build all Docker images
- Start all services (PostgreSQL, Flask, React, CloudBeaver)
- Initialize the database with schema and sample data
- Make the application available at the URLs below

### 4. Access the Services

- **Frontend (React)**: http://localhost:3000
- **Backend API (Flask)**: http://localhost:5000
- **API Health Check**: http://localhost:5000/health
- **CloudBeaver (DB Admin)**: http://localhost:8978

## Using the Application

### Frontend Interface

1. **Create a Todo**:

   - Enter a title (required) and description (optional)
   - Click "Add Todo"

2. **View Todos**:

   - All todos are displayed in reverse chronological order
   - See completion status, title, description, and creation date

3. **Update a Todo**:

   - Click "Edit" button on any todo
   - Modify the title or description
   - Click "Save" or "Cancel"

4. **Toggle Completion**:

   - Click the checkbox to mark as complete/incomplete

5. **Delete a Todo**:
   - Click "Delete" button
   - Confirm the deletion

### API Usage

You can also interact directly with the API:

```bash
# Get all todos
curl http://localhost:5000/api/todos

# Create a new todo
curl -X POST http://localhost:5000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "My Todo", "description": "Description here"}'

# Update a todo
curl -X PUT http://localhost:5000/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Delete a todo
curl -X DELETE http://localhost:5000/api/todos/1
```

## Database Management with CloudBeaver

1. Navigate to http://localhost:8978
2. Complete the initial setup wizard
3. Create a new connection:

   - **Host**: `postgres`
   - **Port**: `5432`
   - **Database**: `tododb`
   - **Username**: `todouser`
   - **Password**: `todopass`

4. Browse the database schema, run queries, and manage data

## Development

### Running in Development Mode

The application is already configured for development:

- **Backend**: Flask runs with debug mode enabled, auto-reloads on code changes
- **Frontend**: React development server with hot-reloading
- **Volumes**: Local code is mounted into containers for live updates

### Making Changes

1. **Backend**: Edit files in `backend/` - Flask will auto-reload
2. **Frontend**: Edit files in `frontend/src/` - React will hot-reload
3. **Database**: Modify `backend/init.sql` and restart containers

### Stopping the Application

```bash
# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (clears database)
docker-compose down -v
```

### Rebuilding After Changes

```bash
# Rebuild and restart all services
docker-compose up --build

# Rebuild specific service
docker-compose up --build backend
```

## Testing

This application includes comprehensive testing at multiple levels:

- **Backend API Tests**: Pytest-based unit tests with 94% coverage (40 test cases)
- **Frontend Selenium Tests**: Browser automation tests with dual-mode execution

### Testing Strategy

The project uses a **dual-mode testing strategy** for frontend tests:

1. **Unit Mode** (Fast, Isolated)

   - Tests run against frontend only
   - All backend APIs mocked via browser-level JavaScript injection
   - No dependencies on backend or database
   - Ideal for rapid development feedback

2. **Integration Mode** (E2E, Real System)
   - Same test code runs against fully deployed system
   - Tests use real backend API endpoints
   - Validates complete end-to-end workflows
   - Ensures system integration works correctly

**Key Advantage**: Zero code duplication - single test codebase switches modes via configuration.

### Quick Start - Running Tests

**Backend API Tests:**

```bash
# Inside backend container
docker exec -it todo_backend pytest -v --cov=. --cov-report=term
```

**Frontend Selenium Tests:**

Linux/Mac:
```bash
cd tests
./run_unit_tests.sh          # Unit mode (fast, mocked APIs)
./run_integration_tests.sh   # Integration mode (full E2E)
```

Windows PowerShell:
```powershell
cd tests
.\run_unit_tests.ps1         # Unit mode (fast, mocked APIs)
.\run_integration_tests.ps1  # Integration mode (full E2E)
```

Windows Command Prompt:
```cmd
cd tests
run_unit_tests.bat           # Unit mode (fast, mocked APIs)
run_integration_tests.bat    # Integration mode (full E2E)
```

### Test Structure

```
tests/                          # Frontend Selenium tests
├── config.py                   # Configuration management (mode switching)
├── conftest.py                 # Pytest fixtures (browser setup, interceptor injection)
├── pytest.ini                  # Pytest configuration
├── .env.unit                   # Unit mode configuration
├── .env.integration            # Integration mode configuration
├── run_unit_tests.sh           # Unit test runner (Linux/Mac)
├── run_integration_tests.sh    # Integration test runner (Linux/Mac)
├── run_unit_tests.ps1          # Unit test runner (Windows PowerShell)
├── run_integration_tests.ps1   # Integration test runner (Windows PowerShell)
├── run_unit_tests.bat          # Unit test runner (Windows CMD)
├── run_integration_tests.bat   # Integration test runner (Windows CMD)
├── Dockerfile                  # Test container image
├── mocks/
│   ├── __init__.py
│   └── api_interceptor.js      # Browser-level API mocking
├── pages/
│   ├── __init__.py
│   └── todo_page.py            # Page Object Model
└── test_todo_crud.py           # Example tests (work in both modes)

backend/tests/                  # Backend API tests
├── conftest.py                 # Test fixtures and configuration
├── test_api.py                 # 40 comprehensive API tests
├── pytest.ini                  # Pytest configuration
└── .coveragerc                 # Coverage configuration
```

### How Dual-Mode Testing Works

**Architecture Overview:**

```
Unit Mode (Mocked):
┌─────────────────────┐
│ Selenium WebDriver  │
│  └─ Browser         │
│     ├─ React App    │
│     └─ API Mocks    │ ← JavaScript injected
└─────────────────────┘

Integration Mode (Real):
┌─────────────────────┐
│ Selenium WebDriver  │
│  └─ Browser         │
│     └─ React App    │
└─────────┬───────────┘
          │ HTTP
          ↓
┌─────────────────────┐
│ Flask Backend       │
│  └─ PostgreSQL      │
└─────────────────────┘
```

**Key Components:**

1. **API Interceptor** (`mocks/api_interceptor.js`)

   - JavaScript code injected into browser in unit mode
   - Intercepts `fetch()` and `XMLHttpRequest` calls
   - Returns mock responses for all CRUD operations
   - Maintains in-memory mock data store

2. **Configuration System** (`config.py`)

   - Switches modes via `TEST_MODE` environment variable
   - `TEST_MODE=unit` → Mocked APIs
   - `TEST_MODE=integration` → Real backend

3. **Page Object Model** (`pages/todo_page.py`)

   - Abstracts all UI interactions
   - Works identically in both modes
   - 30+ reusable methods for todo operations

4. **Pytest Fixtures** (`conftest.py`)
   - Automatically injects interceptor in unit mode
   - Sets up WebDriver (Chrome/Firefox)
   - Captures screenshots on failure

### Test Coverage

**Backend API Tests** (94% coverage):

- ✅ Health check and root endpoint
- ✅ GET operations (all todos, single todo, not found)
- ✅ POST operations (create with validation)
- ✅ PUT operations (update title, description, completion)
- ✅ DELETE operations (remove todos)
- ✅ Edge cases (special chars, unicode, long strings)
- ✅ Data integrity (timestamps, defaults)
- ✅ Error handling (404s, invalid data)
- ✅ Concurrency scenarios

**Frontend Selenium Tests**:

- ✅ Todo creation with various inputs
- ✅ Todo reading and display
- ✅ Todo updating (inline editing)
- ✅ Todo deletion with confirmation
- ✅ Completion status toggling
- ✅ Mode-specific tests (mock manipulation, persistence)

### Comprehensive Documentation

For detailed information about the testing strategy, including:

- Architecture deep-dive
- How to write new tests
- Running tests in Docker
- Debugging tips
- Best practices
- Troubleshooting guide

**See [TESTING.md](TESTING.md) for complete documentation.**

### Example: Writing Mode-Agnostic Tests

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
    assert todo['completed'] is False

    # Mark complete
    page.toggle_todo_completion("Buy groceries")
    page.wait_for_todo_status("Buy groceries", completed=True)

    # Verify completed
    todo = page.find_todo_by_title("Buy groceries")
    assert todo['completed'] is True
```

**No changes needed to run in either mode** - just set `TEST_MODE` environment variable!

## Troubleshooting

### Port Already in Use

If you see port conflict errors:

```bash
# Windows
netstat -ano | findstr :<port>
taskkill /PID <pid> /F

# Linux/Mac
lsof -ti:<port> | xargs kill -9
```

Or change the port in `docker-compose.yaml`.

### Database Connection Errors

1. Ensure PostgreSQL is healthy:

   ```bash
   docker-compose ps
   ```

2. Check backend logs:

   ```bash
   docker-compose logs backend
   ```

3. Restart services:
   ```bash
   docker-compose restart
   ```

### Frontend Not Loading

1. Clear browser cache
2. Check backend is running: http://localhost:5000/health
3. Verify REACT_APP_API_URL in `.env`
4. Check frontend logs:
   ```bash
   docker-compose logs frontend
   ```

### Permission Issues (Linux)

If you encounter permission issues:

```bash
sudo chown -R $USER:$USER .
```

## Production Deployment

For production deployment, consider:

1. **Security**:

   - Change default database credentials
   - Enable HTTPS/SSL
   - Implement authentication and authorization
   - Use environment-specific configurations

2. **Performance**:

   - Use production builds for React
   - Enable PostgreSQL query optimization
   - Implement caching strategies
   - Use a reverse proxy (nginx)

3. **Monitoring**:
   - Add logging and monitoring
   - Set up health checks
   - Implement error tracking

## Database Schema

```sql
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Response Examples

### Get All Todos

```json
[
  {
    "id": 1,
    "title": "Welcome to Todo App",
    "description": "This is your first todo item",
    "completed": false,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
]
```

### Create Todo

```json
{
  "id": 2,
  "title": "New Todo",
  "description": "Todo description",
  "completed": false,
  "created_at": "2024-01-15T11:00:00",
  "updated_at": "2024-01-15T11:00:00"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

- Built with React, Flask, and PostgreSQL
- Containerized with Docker
- Inspired by modern microservices architecture
