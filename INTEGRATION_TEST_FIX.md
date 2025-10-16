# Integration Test Database Connection Fix

## Issue Identified

The integration tests were failing with database connection errors:
```
[TEST] Warning: Could not clean database: connection to server at "localhost" (::1), port 5432 failed
```

## Root Cause

The integration tests have a fixture that cleans the database before each test. This fixture was trying to connect to `localhost` instead of the `postgres` container because the database configuration environment variables were not being set properly.

## Fixes Applied

### 1. Updated `.env.integration` File

Added missing database configuration variables:

```env
# Database configuration for cleanup
DB_HOST=postgres
DB_PORT=5432
POSTGRES_DB=tododb
POSTGRES_USER=todouser
POSTGRES_PASSWORD=todopass
```

### 2. Updated `run_all_tests.bat` (Windows)

Added database environment variables to the Docker run command for integration tests:

```batch
docker run --rm ^
    --network !NETWORK! ^
    -e TEST_MODE=integration ^
    -e FRONTEND_URL=http://frontend:3000 ^
    -e BACKEND_URL=http://backend:5000 ^
    -e DB_HOST=postgres ^
    -e DB_PORT=5432 ^
    -e POSTGRES_DB=tododb ^
    -e POSTGRES_USER=todouser ^
    -e POSTGRES_PASSWORD=todopass ^
    ...
```

### 3. Updated `run_all_tests.sh` (Linux/Mac)

Changed from sourcing `.env` files to explicitly setting environment variables:

```bash
TEST_MODE=integration \
FRONTEND_URL=http://frontend:3000 \
BACKEND_URL=http://backend:5000 \
DB_HOST=postgres \
DB_PORT=5432 \
POSTGRES_DB=tododb \
POSTGRES_USER=todouser \
POSTGRES_PASSWORD=todopass \
BROWSER=chrome \
HEADLESS=true \
pytest -v --html=test_reports/integration_report.html --self-contained-html
```

## Why This Fix Works

1. **Explicit Environment Variables**: Instead of relying on `.env` file sourcing (which can be unreliable in Docker contexts), we now explicitly set all required environment variables.

2. **Correct Database Host**: `DB_HOST=postgres` ensures tests running in Docker containers connect to the `postgres` container on the Docker network, not to `localhost`.

3. **Complete Configuration**: All database parameters (host, port, database name, user, password) are now properly passed to the test container.

## Testing the Fix

Run the comprehensive test script:

**Windows:**
```cmd
cd tests\scripts
run_all_tests.bat
```

**Linux/Mac:**
```bash
cd tests/scripts
./run_all_tests.sh
```

The integration tests should now:
1. Successfully connect to the database
2. Clean the database before each test
3. Run all integration tests without connection errors

## Files Modified

1. `tests/.env.integration` - Added database configuration
2. `tests/scripts/run_all_tests.bat` - Added DB environment variables
3. `tests/scripts/run_all_tests.sh` - Changed to explicit environment variables

## Next Steps

If you still encounter issues:

1. **Check Docker Network**: Ensure all containers are on the same network
   ```bash
   docker network inspect selenium-flask-python-docker_todo_network
   ```

2. **Check PostgreSQL Container**: Verify postgres is running and healthy
   ```bash
   docker ps | grep postgres
   docker logs todo_postgres
   ```

3. **Manual Database Test**: Test connection from test container
   ```bash
   docker run --rm --network selenium-flask-python-docker_todo_network \
     -e PGPASSWORD=todopass \
     postgres:15 psql -h postgres -U todouser -d tododb -c "SELECT 1;"
   ```

## Notes

- The individual test scripts (`run_unit_tests.*` and `run_integration_tests.*`) were not modified in this update. They already use the `.env.*` files which now have the correct configuration.
- The comprehensive test runner (`run_all_tests.*`) uses explicit environment variables for better reliability.
- This is a pre-existing issue that was uncovered during the test reorganization, not caused by it.
