# Proxy Configuration Guide

This document explains how to configure proxy settings for Docker builds in corporate environments.

## Overview

The project is configured to support building Docker images behind corporate proxies without hardcoding proxy URLs in Dockerfiles. This keeps sensitive proxy information out of version control.

## Quick Start

### 1. Create Proxy Configuration File

```bash
# Copy the example file
cp .env.build.example .env.build

# Edit .env.build with your proxy settings
# (This file is git-ignored and won't be committed)
```

### 2. Configure Your Proxy Settings

Edit `.env.build`:

```bash
# HTTP/HTTPS Proxy (leave empty if no proxy needed)
HTTP_PROXY=http://your-proxy-server:port
HTTPS_PROXY=http://your-proxy-server:port

# No Proxy - addresses that should bypass the proxy
NO_PROXY=localhost,127.0.0.1,frontend,backend,postgres
```

### 3. Build with Proxy Settings

All build commands will automatically use the proxy configuration from `.env.build` if it exists.

**Option A: Use the test runner (automatically includes builds)**

Windows:
```cmd
cd tests\scripts
run_all_tests.bat
```

Linux/Mac:
```bash
cd tests/scripts
./run_all_tests.sh
```

**Option B: Use the dedicated build script**

Windows:
```cmd
build-with-proxy.bat
```

Linux/Mac:
```bash
./build-with-proxy.sh
```

**Option C: Manual docker-compose build**

Windows:
```cmd
docker-compose build ^
    --build-arg HTTP_PROXY=%HTTP_PROXY% ^
    --build-arg HTTPS_PROXY=%HTTPS_PROXY% ^
    --build-arg NO_PROXY=%NO_PROXY%
```

Linux/Mac:
```bash
docker-compose build \
    --build-arg HTTP_PROXY="${HTTP_PROXY}" \
    --build-arg HTTPS_PROXY="${HTTPS_PROXY}" \
    --build-arg NO_PROXY="${NO_PROXY}"
```

> **Note**: The test runner scripts (`run_all_tests.bat`/`run_all_tests.sh`) automatically detect and use `.env.build` for all Docker build operations, so you don't need to manually pass build arguments.

## How It Works

### Dockerfile Configuration

Each Dockerfile uses `ARG` instructions to accept build-time proxy configuration:

```dockerfile
# Build arguments for proxy configuration (optional)
ARG HTTP_PROXY=""
ARG HTTPS_PROXY=""
ARG NO_PROXY="localhost,127.0.0.1"

# Set proxy environment variables only if provided
ENV http_proxy="${HTTP_PROXY}"
ENV https_proxy="${HTTPS_PROXY}"
ENV no_proxy="${NO_PROXY}"
```

### Benefits

1. **No Hardcoded Proxies**: Proxy URLs are not committed to version control
2. **Flexible**: Works with or without proxy (empty values = no proxy)
3. **Team-Friendly**: Each developer can configure their own proxy
4. **Secure**: `.env.build` is git-ignored

## Building Without Proxy

If you don't need a proxy, simply don't create `.env.build` or leave the values empty:

```bash
HTTP_PROXY=
HTTPS_PROXY=
NO_PROXY=localhost,127.0.0.1
```

Then build normally:
```bash
docker-compose build
```

## Troubleshooting

### Build Fails with "Could not resolve host"

This means the proxy settings are incorrect or the proxy is blocking the request.

**Solution:**
1. Verify your proxy URL in `.env.build`
2. Check that the proxy is accessible
3. Ensure `NO_PROXY` includes `localhost,127.0.0.1`

### npm/pip Install Fails

Some package managers need additional configuration.

**For npm (frontend):**
The proxy settings are automatically applied from environment variables.

**For pip (backend/tests):**
The proxy settings are automatically applied from environment variables.

### Proxy Works for Some Services But Not Others

Check that all Dockerfiles have the same ARG/ENV structure. All three Dockerfiles (backend, frontend, tests) should have matching proxy configuration.

## Files

- `.env.build.example` - Template file (committed to git)
- `.env.build` - Your actual configuration (git-ignored)
- `build-with-proxy.bat` - Windows build helper script
- `build-with-proxy.sh` - Linux/Mac build helper script

## For Developers in Different Environments

### Corporate Network (with proxy)

1. Create `.env.build` with your corporate proxy
2. Use `build-with-proxy.bat` or `build-with-proxy.sh`

### Home Network (no proxy)

1. Don't create `.env.build`, or leave it empty
2. Use regular `docker-compose build`

### CI/CD Pipeline

Set proxy as environment variables in your CI/CD system:

```yaml
# Example GitLab CI
variables:
  HTTP_PROXY: "http://proxy:8080"
  HTTPS_PROXY: "http://proxy:8080"
  NO_PROXY: "localhost,127.0.0.1"

build:
  script:
    - docker-compose build
        --build-arg HTTP_PROXY=$HTTP_PROXY
        --build-arg HTTPS_PROXY=$HTTPS_PROXY
        --build-arg NO_PROXY=$NO_PROXY
```

## See Also

- [Docker Documentation: Use build-time variables](https://docs.docker.com/build/building/variables/)
- [Docker Compose build arguments](https://docs.docker.com/compose/compose-file/build/#args)
