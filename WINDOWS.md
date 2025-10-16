# Windows Users Quick Guide

This guide provides Windows-specific instructions for running the Todo application and tests.

## Prerequisites

- **Docker Desktop for Windows** installed and running
- **Git for Windows** (optional, for cloning the repository)

## Quick Start

### 1. Start the Application

Open PowerShell or Command Prompt and navigate to the project directory:

```powershell
cd C:\path\to\selenium-flask-python-docker
docker-compose up
```

### 2. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- CloudBeaver: http://localhost:8978

## Running Tests on Windows

### Option 1: PowerShell Scripts (Recommended)

Open PowerShell in the `tests` directory:

```powershell
cd tests

# Run unit tests (fast, no backend needed)
.\run_unit_tests.ps1

# Run integration tests (requires full system)
.\run_integration_tests.ps1
```

**Features:**
- ✅ Automatically checks if Docker containers are running
- ✅ Starts required containers if needed
- ✅ Creates test directories automatically
- ✅ Colored console output
- ✅ Auto-detects Docker network name

### Option 2: Batch Scripts

Open Command Prompt in the `tests` directory:

```cmd
cd tests

# Run unit tests
run_unit_tests.bat

# Run integration tests
run_integration_tests.bat
```

### Option 3: Manual Docker Commands

**PowerShell:**

```powershell
cd tests

# Build test image (first time only)
docker build -t todo-tests .

# Run unit tests
docker run --rm `
  --network selenium-flask-python-docker_default `
  -e TEST_MODE=unit `
  -e FRONTEND_URL=http://frontend:3000 `
  -v "${PWD}/test_reports:/tests/test_reports" `
  -v "${PWD}/test_screenshots:/tests/test_screenshots" `
  todo-tests

# Run integration tests
docker run --rm `
  --network selenium-flask-python-docker_default `
  -e TEST_MODE=integration `
  -e FRONTEND_URL=http://frontend:3000 `
  -e BACKEND_URL=http://backend:5000 `
  -v "${PWD}/test_reports:/tests/test_reports" `
  -v "${PWD}/test_screenshots:/tests/test_screenshots" `
  todo-tests
```

**Command Prompt:**

```cmd
cd tests

# Build test image (first time only)
docker build -t todo-tests .

# Run unit tests
docker run --rm ^
  --network selenium-flask-python-docker_default ^
  -e TEST_MODE=unit ^
  -e FRONTEND_URL=http://frontend:3000 ^
  -v "%cd%/test_reports:/tests/test_reports" ^
  -v "%cd%/test_screenshots:/tests/test_screenshots" ^
  todo-tests

# Run integration tests
docker run --rm ^
  --network selenium-flask-python-docker_default ^
  -e TEST_MODE=integration ^
  -e FRONTEND_URL=http://frontend:3000 ^
  -e BACKEND_URL=http://backend:5000 ^
  -v "%cd%/test_reports:/tests/test_reports" ^
  -v "%cd%/test_screenshots:/tests/test_screenshots" ^
  todo-tests
```

## Key Differences from Linux/Mac

### Path Separators
- Windows uses backslashes `\` in file paths
- Docker expects forward slashes `/` in container paths
- The scripts handle this automatically

### Line Continuation
- **PowerShell**: Use backtick `` ` `` at end of line
- **CMD**: Use caret `^` at end of line
- **Bash** (Linux/Mac): Use backslash `\` at end of line

### Current Directory Variable
- **PowerShell**: `${PWD}` or `$PWD`
- **CMD**: `%cd%`
- **Bash**: `$(pwd)`

### Script Execution

**PowerShell Execution Policy:**

If you get an error about execution policy, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then you can run scripts like:
```powershell
.\run_unit_tests.ps1
```

**Batch Files:**

No special permissions needed:
```cmd
run_unit_tests.bat
```

## Common Issues on Windows

### Issue: Docker Network Not Found

**Error:** `ERROR: Docker network not found`

**Solution:**
1. Make sure Docker Desktop is running
2. Start the application first:
   ```powershell
   docker-compose up -d
   ```
3. Verify network exists:
   ```powershell
   docker network ls
   ```

### Issue: Volume Mount Errors

**Error:** Issues with volume mounting or path not found

**Solution:**
- Ensure you're in the correct directory (`tests/` folder)
- Use absolute paths if needed:
  ```powershell
  -v "C:/Users/YourName/Projects/selenium-flask-python-docker/tests/test_reports:/tests/test_reports"
  ```

### Issue: PowerShell Script Won't Run

**Error:** `cannot be loaded because running scripts is disabled`

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Port Already in Use

**Error:** `port is already allocated`

**Solution:**
Find and kill the process using the port:
```powershell
# Find process using port 3000 (for example)
netstat -ano | findstr :3000

# Kill process by PID
taskkill /PID <pid> /F
```

### Issue: Line Ending Problems

**Error:** Bash scripts fail with `^M: bad interpreter` or similar

**Solution:**
This happens when Git converts line endings. Configure Git:
```bash
git config --global core.autocrlf input
```

Or convert line endings for shell scripts:
```powershell
# In PowerShell
(Get-Content run_unit_tests.sh -Raw) -replace "`r`n", "`n" | Set-Content run_unit_tests.sh -NoNewline
```

## Test Reports

After running tests, view the HTML reports:

**PowerShell:**
```powershell
# Open unit test report
Start-Process tests/test_reports/unit_report.html

# Open integration test report
Start-Process tests/test_reports/integration_report.html
```

**Command Prompt:**
```cmd
# Open unit test report
start tests\test_reports\unit_report.html

# Open integration test report
start tests\test_reports\integration_report.html
```

**File Explorer:**
Navigate to `tests\test_reports\` and double-click the HTML files.

## Screenshots

Test failure screenshots are saved to:
```
tests\test_screenshots\
```

Open them with any image viewer or browser.

## Docker Desktop Settings

For best performance on Windows:

1. **Resources:**
   - Settings → Resources → Advanced
   - Allocate at least 4GB RAM
   - Allocate at least 2 CPUs

2. **File Sharing:**
   - Settings → Resources → File Sharing
   - Ensure your project directory is shared

3. **WSL 2 Backend** (Recommended):
   - Settings → General
   - Enable "Use the WSL 2 based engine"

## Tips for Windows Users

1. **Use PowerShell ISE or Windows Terminal** for better experience
2. **Run Docker Desktop as Administrator** if you encounter permission issues
3. **Add project directory to Windows Defender exclusions** for better performance
4. **Use Git Bash** if you prefer Unix-like commands
5. **Tab completion works in PowerShell** - use it for long paths

## Running Backend Tests on Windows

Backend tests can be run the same way:

**PowerShell:**
```powershell
docker exec -it todo-backend pytest -v --cov=. --cov-report=html --cov-report=term
```

**View coverage report:**
```powershell
Start-Process backend\htmlcov\index.html
```

## Additional Resources

- **Main Documentation**: [README.md](README.md)
- **Testing Guide**: [TESTING.md](TESTING.md)
- **Docker Desktop Docs**: https://docs.docker.com/desktop/windows/

## Getting Help

If you encounter issues:

1. Check Docker Desktop is running
2. Check all containers are healthy: `docker-compose ps`
3. Check container logs: `docker-compose logs [service-name]`
4. Restart Docker Desktop
5. Review [TESTING.md](TESTING.md) troubleshooting section

## PowerShell vs CMD Quick Reference

| Task | PowerShell | Command Prompt |
|------|------------|----------------|
| Change directory | `cd tests` | `cd tests` |
| List files | `ls` or `dir` | `dir` |
| Current directory | `${PWD}` | `%cd%` |
| Line continuation | `` ` `` | `^` |
| Run script | `.\script.ps1` | `script.bat` |
| Environment variable | `$env:VAR` | `%VAR%` |
| Clear screen | `cls` or `clear` | `cls` |

---

For complete testing documentation, see [TESTING.md](TESTING.md)
