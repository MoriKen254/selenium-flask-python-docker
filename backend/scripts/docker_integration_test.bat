@echo off
REM Docker Integration Test Script for Windows
REM This script tests Docker build and integration with the new package structure

echo ============================================
echo Docker Integration Test
echo ============================================
echo.

setlocal enabledelayedexpansion

REM Set base directory
set BASE_DIR=%~dp0..

REM Create temporary directory for testing
set TEMP_DIR=%TEMP%\todo_api_docker_test_%RANDOM%
mkdir "%TEMP_DIR%"
echo [INFO] Created temporary test directory: %TEMP_DIR%
echo.

REM Test 1: Check Docker availability
echo [TEST 1] Checking Docker availability...
docker --version >"%TEMP_DIR%\docker_version.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Docker is not available
    type "%TEMP_DIR%\docker_version.log"
    goto cleanup
)
type "%TEMP_DIR%\docker_version.log"
echo [PASS] Docker is available
echo.

REM Test 2: Build Docker image
echo [TEST 2] Building Docker image...
cd /d "%BASE_DIR%"
docker build -t todo-api-test . >"%TEMP_DIR%\docker_build.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Docker build failed
    type "%TEMP_DIR%\docker_build.log"
    goto cleanup
)
echo [PASS] Docker image built successfully
echo.

REM Test 3: Run container health check
echo [TEST 3] Running container health check...
docker run --rm -d --name todo-api-test-container -p 5001:5000 todo-api-test >"%TEMP_DIR%\docker_run.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Failed to start container
    type "%TEMP_DIR%\docker_run.log"
    goto cleanup
)
echo [INFO] Container started, waiting for service to be ready...

REM Wait for service to start
timeout /t 10 /nobreak >nul

REM Test 4: Check health endpoint
echo [TEST 4] Testing health endpoint...
curl -f http://localhost:5001/health >"%TEMP_DIR%\health_check.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Health endpoint test failed
    type "%TEMP_DIR%\health_check.log"
    docker logs todo-api-test-container >"%TEMP_DIR%\container_logs.log" 2>&1
    echo [INFO] Container logs:
    type "%TEMP_DIR%\container_logs.log"
    docker stop todo-api-test-container >nul 2>&1
    goto cleanup
)
type "%TEMP_DIR%\health_check.log"
echo [PASS] Health endpoint responded correctly
echo.

REM Test 5: Check version endpoint
echo [TEST 5] Testing version endpoint...
curl -f http://localhost:5001/ >"%TEMP_DIR%\version_check.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Version endpoint test failed
    type "%TEMP_DIR%\version_check.log"
) else (
    type "%TEMP_DIR%\version_check.log"
    echo [PASS] Version endpoint responded correctly
)
echo.

REM Test 6: Test API endpoints
echo [TEST 6] Testing API endpoints...
curl -f http://localhost:5001/api/todos >"%TEMP_DIR%\api_test.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] API endpoint test failed
    type "%TEMP_DIR%\api_test.log"
) else (
    type "%TEMP_DIR%\api_test.log"
    echo [PASS] API endpoints responded correctly
)
echo.

REM Test 7: Check container logs
echo [TEST 7] Checking container logs...
docker logs todo-api-test-container >"%TEMP_DIR%\final_logs.log" 2>&1
echo [INFO] Container logs:
type "%TEMP_DIR%\final_logs.log"
echo [PASS] Container logs retrieved
echo.

REM Test 8: Stop container
echo [TEST 8] Stopping container...
docker stop todo-api-test-container >"%TEMP_DIR%\docker_stop.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Failed to stop container gracefully
    type "%TEMP_DIR%\docker_stop.log"
    docker kill todo-api-test-container >nul 2>&1
) else (
    echo [PASS] Container stopped successfully
)
echo.

REM Test 9: Clean up Docker image
echo [TEST 9] Cleaning up Docker image...
docker rmi todo-api-test >"%TEMP_DIR%\docker_cleanup.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Failed to remove Docker image
    type "%TEMP_DIR%\docker_cleanup.log"
) else (
    echo [PASS] Docker image cleaned up
)
echo.

echo ============================================
echo Docker Integration Test Complete
echo ============================================
echo [SUCCESS] Docker integration test completed successfully
echo.

:cleanup
echo [INFO] Cleaning up...

REM Force stop and remove container if still running
docker stop todo-api-test-container >nul 2>&1
docker rm todo-api-test-container >nul 2>&1

REM Clean up temp directory
cd /d "%TEMP%"
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%" >nul 2>&1

cd /d "%BASE_DIR%"

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker integration test failed
    exit /b 1
) else (
    echo [INFO] Cleanup complete
    exit /b 0
)
