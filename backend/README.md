# Todo API - Modern Python Package

A modern Flask REST API for Todo List management with comprehensive packaging, version management, and testing infrastructure.

## Features

- **Modern Package Structure**: Follows PEP 518/621 standards with `pyproject.toml`
- **Comprehensive Version Management**: Single source of truth with automated version consistency
- **Development Tools Integration**: Black, Ruff, MyPy, pytest with coverage
- **Docker Support**: Containerized deployment with health checks
- **CLI Interface**: Command-line interface for easy server management
- **Comprehensive Testing**: Unit tests, integration tests, and validation scripts

## Project Structure

```
backend/
├── pyproject.toml          # Modern Python project configuration
├── src/
│   └── todo_api/           # Main package
│       ├── __init__.py     # Package initialization and version
│       ├── app.py          # Flask application factory
│       └── cli.py          # Command-line interface
├── tests/                  # Test suite
│   ├── conftest.py         # Test configuration
│   └── test_api.py         # API tests
├── scripts/                # Validation and testing scripts
│   ├── package_validation.*
│   ├── version_consistency_test.*
│   ├── build_and_install_test.*
│   ├── development_tools_test.*
│   └── docker_integration_test.*
└── requirements.txt        # Runtime dependencies
```

## Installation

### Development Installation

```bash
# Install in development mode with all dependencies
pip install -e ".[dev]"
```

### Production Installation

```bash
# Install from built package
pip install dist/todo_api-*.whl
```

## Usage

### Command Line Interface

The package provides a CLI for easy server management:

```bash
# Start server with default settings
todo-api

# Start with custom host and port
todo-api --host 0.0.0.0 --port 8000

# Enable debug mode
todo-api --debug

# Show version
todo-api --version
```

### Python API

```python
from todo_api import create_app

# Create Flask app instance
app = create_app()

# Run the app
app.run(host='0.0.0.0', port=5000)
```

## Development

### Setting up Development Environment

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Code Quality Tools

The project uses modern Python development tools:

- **Black**: Code formatting
- **Ruff**: Fast linting
- **MyPy**: Type checking
- **pytest**: Testing framework
- **Coverage**: Test coverage reporting

### Running Development Tools

```bash
# Format code with Black
black src/ tests/

# Lint with Ruff
ruff check src/ tests/

# Type check with MyPy
mypy src/

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html
```

## Version Management

### Current Version System

- **Single Source of Truth**: Version defined in `src/todo_api/__init__.py`
- **Automatic Propagation**: Version automatically used in:
  - `pyproject.toml` (via bumpver)
  - API responses (root endpoint)
  - CLI version command
  - Package metadata

### Updating Versions

Using bumpver (recommended):

```bash
# Patch version (1.0.0 -> 1.0.1)
bumpver update --patch

# Minor version (1.0.0 -> 1.1.0)
bumpver update --minor

# Major version (1.0.0 -> 2.0.0)
bumpver update --major
```

Manual update:
1. Update version in `src/todo_api/__init__.py`
2. Update version in `pyproject.toml`
3. Run version consistency test to verify

## Testing and Validation

### Comprehensive Test Suite

The project includes multiple validation scripts:

#### 1. Package Validation
Tests package installation and basic functionality:
```bash
# Windows
scripts\package_validation.bat

# Unix/Linux/macOS
bash scripts/package_validation.sh
```

#### 2. Version Consistency Test
Verifies version consistency across all files:
```bash
# Windows
scripts\version_consistency_test.bat

# Unix/Linux/macOS
bash scripts/version_consistency_test.sh
```

#### 3. Build and Install Test
Tests complete build and installation process:
```bash
# Windows
scripts\build_and_install_test.bat

# Unix/Linux/macOS
bash scripts/build_and_install_test.sh
```

#### 4. Development Tools Test
Tests all development tools configuration:
```bash
# Windows
scripts\development_tools_test.bat

# Unix/Linux/macOS
bash scripts/development_tools_test.sh
```

#### 5. Docker Integration Test
Tests Docker build and container functionality:
```bash
# Windows
scripts\docker_integration_test.bat

# Unix/Linux/macOS
bash scripts/docker_integration_test.sh
```

### Running All Tests

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run all validation scripts (example for Unix)
bash scripts/package_validation.sh
bash scripts/version_consistency_test.sh
bash scripts/build_and_install_test.sh
bash scripts/development_tools_test.sh
bash scripts/docker_integration_test.sh
```

## Building and Distribution

### Building Packages

```bash
# Install build dependencies
pip install build

# Build source and wheel distributions
python -m build

# Validate distributions
python -m twine check dist/*
```

### Docker Deployment

```bash
# Build Docker image
docker build -t todo-api .

# Run container
docker run -p 5000:5000 todo-api

# Run with environment variables
docker run -p 5000:5000 -e DATABASE_URL=your_db_url todo-api
```

## API Endpoints

- `GET /` - API information and version
- `GET /health` - Health check
- `GET /api/todos` - List all todos
- `GET /api/todos/<id>` - Get specific todo
- `POST /api/todos` - Create new todo
- `PUT /api/todos/<id>` - Update todo
- `DELETE /api/todos/<id>` - Delete todo

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_ENV`: Flask environment (development/production)

### Default Configuration

- Host: `0.0.0.0`
- Port: `5000`
- Database: `postgresql://todouser:todopass@postgres:5432/tododb`

## Migration from Legacy Structure

The project has been migrated from a legacy structure to a modern Python package:

### Key Changes

1. **Structure**: Moved from flat structure to `src/` layout
2. **Configuration**: Migrated from `setup.py` to `pyproject.toml`
3. **Version Management**: Centralized version management
4. **CLI**: Added command-line interface
5. **Testing**: Comprehensive validation scripts
6. **Development Tools**: Modern toolchain integration

### Backward Compatibility

The API endpoints and functionality remain unchanged. Only the package structure and development workflow have been modernized.

## Contributing

1. Install development dependencies: `pip install -e ".[dev]"`
2. Run tests: `pytest tests/`
3. Format code: `black src/ tests/`
4. Lint code: `ruff check src/ tests/`
5. Update version appropriately
6. Run validation scripts before submitting

## License

MIT License - see LICENSE file for details.
