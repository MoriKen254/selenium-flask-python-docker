@echo off
REM Build Docker images with proxy configuration from .env.build file
REM This script reads proxy settings from .env.build and passes them as build arguments

echo ========================================
echo Building Docker Images with Proxy Config
echo ========================================
echo.

REM Check if .env.build exists
if not exist ".env.build" (
    echo [WARNING] .env.build file not found
    echo Creating from .env.build.example...
    if exist ".env.build.example" (
        copy .env.build.example .env.build
        echo [INFO] Created .env.build - please edit it with your proxy settings
        echo.
    ) else (
        echo [ERROR] .env.build.example not found
        exit /b 1
    )
)

REM Read proxy settings from .env.build
echo Reading proxy configuration from .env.build...
for /f "usebackq tokens=1,2 delims==" %%a in (".env.build") do (
    set "line=%%a"
    if not "!line:~0,1!"=="#" (
        if "%%a"=="HTTP_PROXY" set "HTTP_PROXY=%%b"
        if "%%a"=="HTTPS_PROXY" set "HTTPS_PROXY=%%b"
        if "%%a"=="NO_PROXY" set "NO_PROXY=%%b"
    )
)

echo HTTP_PROXY=%HTTP_PROXY%
echo HTTPS_PROXY=%HTTPS_PROXY%
echo NO_PROXY=%NO_PROXY%
echo.

REM Build with docker-compose using build args
echo Building all services with docker-compose...
docker-compose build ^
    --build-arg HTTP_PROXY=%HTTP_PROXY% ^
    --build-arg HTTPS_PROXY=%HTTPS_PROXY% ^
    --build-arg NO_PROXY=%NO_PROXY%

if errorlevel 1 (
    echo.
    echo [FAILED] Build failed
    exit /b 1
) else (
    echo.
    echo [SUCCESS] Build completed successfully
    exit /b 0
)
