# Backend API Service

This directory contains the Todo API backend service, built with Flask and PostgreSQL.

## Features

- RESTful API for Todo management
- PostgreSQL database for data persistence
- Comprehensive test suite with high code coverage
- Containerized with Docker

## Development Setup

1. Install dependencies:
   ```bash
   pip install -e ".[dev,test]"
   ```

2. Run development server:
   ```bash
   todo-api --debug
   ```

## Testing

Run tests with pytest:

```bash
pytest
```

### Test Coverage

Coverage reports are generated in two formats:
- Terminal output (--cov-report=term-missing)
- XML report (--cov-report=xml)

HTML coverage reports have been disabled due to potential permission issues in Docker environments.

## Troubleshooting

### Permission Issues with Coverage Reports

If you encounter permission errors with coverage files:

```
PermissionError: [Errno 13] Permission denied: 'htmlcov/app_py.html'
```

Use the cleanup script to fix it:

**Windows:**
```
backend\scripts\cleanup_coverage.bat
```

**Linux/Mac:**
```
bash backend/scripts/cleanup_coverage.sh
```

This script forcibly removes the old coverage files and recreates the directory with proper permissions.

## Docker

Build and run with Docker:

```bash
docker-compose up --build backend
```

The API will be available at http://localhost:5000.
