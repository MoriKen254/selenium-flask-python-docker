# Network Deployment Guide

This guide explains how to deploy the Todo application across multiple independent servers on a network, allowing clients to access different application instances via IP addresses.

## Architecture Overview

```
Network: 192.168.1.0/24

┌─────────────────────────────────────────────────────────────┐
│                     Corporate Network                        │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ app_server1  │    │ app_server2  │    │ app_server3  │  │
│  │ 192.168.1.10 │    │ 192.168.1.11 │    │ 192.168.1.12 │  │
│  │              │    │              │    │              │  │
│  │ ┌──────────┐ │    │ ┌──────────┐ │    │ ┌──────────┐ │  │
│  │ │ Frontend │ │    │ │ Frontend │ │    │ │ Frontend │ │  │
│  │ │ :3000    │ │    │ │ :3000    │ │    │ │ :3000    │ │  │
│  │ └──────────┘ │    │ └──────────┘ │    │ └──────────┘ │  │
│  │ ┌──────────┐ │    │ ┌──────────┐ │    │ ┌──────────┐ │  │
│  │ │ Backend  │ │    │ │ Backend  │ │    │ │ Backend  │ │  │
│  │ │ :5000    │ │    │ │ :5000    │ │    │ │ :5000    │ │  │
│  │ └──────────┘ │    │ └──────────┘ │    │ └──────────┘ │  │
│  │ ┌──────────┐ │    │ ┌──────────┐ │    │ ┌──────────┐ │  │
│  │ │PostgreSQL│ │    │ │PostgreSQL│ │    │ │PostgreSQL│ │  │
│  │ │ :5432    │ │    │ │ :5432    │ │    │ │ :5432    │ │  │
│  │ └──────────┘ │    │ └──────────┘ │    │ └──────────┘ │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         ▲                   ▲                   ▲           │
│         │                   │                   │           │
│         │                   │                   │           │
│  ┌──────┴───────────────────┴───────────────────┴──────┐   │
│  │                                                       │   │
│  │         Client Machines (192.168.1.x)               │   │
│  │         - Access any server via browser             │   │
│  │         - http://192.168.1.10:3000                  │   │
│  │         - http://192.168.1.11:3000                  │   │
│  │         - http://192.168.1.12:3000                  │   │
│  │                                                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key Characteristics**:
- Each server runs a complete, independent application stack
- Each server has its own database (data is NOT shared)
- Clients connect to servers via IP address, not localhost
- Switching servers = changing URL in browser
- Servers operate completely independently

## How It Works

### Dynamic API URL Detection

The frontend automatically detects the correct backend API URL based on the hostname used to access it:

**Client accesses**: `http://192.168.1.10:3000`
**Frontend detects hostname**: `192.168.1.10`
**Backend API URL becomes**: `http://192.168.1.10:5000`

**Client accesses**: `http://192.168.1.11:3000`
**Frontend detects hostname**: `192.168.1.11`
**Backend API URL becomes**: `http://192.168.1.11:5000`

This happens in `frontend/public/config.js` which runs before React initializes:

```javascript
function getApiUrl() {
    const hostname = window.location.hostname;

    // For localhost or network access
    const apiUrl = `http://${hostname}:5000`;

    window.__API_URL__ = apiUrl;
    return apiUrl;
}
```

### Network Binding

All services bind to `0.0.0.0` (all network interfaces) instead of `127.0.0.1` (localhost only):

- **Frontend**: `0.0.0.0:3000` → accessible from network
- **Backend**: `0.0.0.0:5000` → accessible from network
- **PostgreSQL**: `0.0.0.0:5432` → accessible from network
- **CloudBeaver**: `0.0.0.0:8978` → accessible from network

This is configured in `docker-compose.yaml`:

```yaml
ports:
  - "${FRONTEND_HOST:-0.0.0.0}:${FRONTEND_PORT:-3000}:3000"
```

## Deployment Instructions

### Prerequisites

Each application server needs:
- Docker and Docker Compose installed
- Network connectivity (ports 3000, 5000, 5432, 8978 open)
- Static IP address or hostname on the network
- Git (for cloning the repository)

### Step 1: Clone Repository on Each Server

On **app_server1** (192.168.1.10):
```bash
git clone <repository-url>
cd selenium-flask-python-docker
```

Repeat for **app_server2** (192.168.1.11), **app_server3** (192.168.1.12), etc.

### Step 2: Configure Environment Variables

Each server needs a `.env` file. Copy the example:

```bash
cp .env.example .env
```

**IMPORTANT**: The `.env` file defaults are already configured for network deployment:

```bash
# Database Configuration
POSTGRES_DB=tododb
POSTGRES_USER=todouser
POSTGRES_PASSWORD=todopass
POSTGRES_HOST=0.0.0.0        # Binds to all interfaces
POSTGRES_PORT=5432
POSTGRES_HOST_AUTH_METHOD=md5

# Backend Configuration
BACKEND_HOST=0.0.0.0         # Binds to all interfaces
BACKEND_PORT=5000

# Frontend Configuration
FRONTEND_HOST=0.0.0.0        # Binds to all interfaces
FRONTEND_PORT=3000

# CloudBeaver Configuration
CLOUDBEAVER_HOST=0.0.0.0     # Binds to all interfaces
CLOUDBEAVER_PORT=8978
```

**You can use these defaults without changes** for standard network deployment.

### Step 3: Configure Proxy (If Behind Corporate Proxy)

If your servers are behind a corporate proxy (like `squid.alpine.co.jp:8080`):

```bash
cp .env.build.example .env.build
```

Edit `.env.build`:
```bash
HTTP_PROXY=http://your-proxy-server:port
HTTPS_PROXY=http://your-proxy-server:port
NO_PROXY=localhost,127.0.0.1,frontend,backend,postgres
```

See `PROXY-CONFIG.md` for detailed proxy configuration.

### Step 4: Build and Start Services

On each server:

```bash
# Build images (with proxy if needed)
docker-compose build

# Start all services
docker-compose up -d

# Verify all containers are running
docker-compose ps
```

Expected output:
```
NAME                 STATUS              PORTS
todo_backend        Up 30 seconds       0.0.0.0:5000->5000/tcp
todo_cloudbeaver    Up 30 seconds       0.0.0.0:8978->8978/tcp
todo_frontend       Up 30 seconds       0.0.0.0:3000->3000/tcp
todo_postgres       Up 30 seconds       0.0.0.0:5432->5432/tcp
```

### Step 5: Verify Health

Check backend health on each server:

```bash
# On the server itself
curl http://localhost:5000/health

# From another machine on the network
curl http://192.168.1.10:5000/health
```

Expected response:
```json
{"status": "healthy", "database": "connected"}
```

## Client Access

### Accessing from Client Machines

Clients can access any server by opening a browser and navigating to:

- **Server 1**: `http://192.168.1.10:3000`
- **Server 2**: `http://192.168.1.11:3000`
- **Server 3**: `http://192.168.1.12:3000`

### Switching Between Servers

To switch servers, simply change the URL in the browser:

1. Currently on Server 1: `http://192.168.1.10:3000`
2. Want to use Server 2: Navigate to `http://192.168.1.11:3000`
3. The frontend automatically connects to the correct backend

**Data is NOT shared**: Each server has its own database. Todos created on Server 1 will NOT appear on Server 2.

### Bookmarking Servers

Users can bookmark specific servers for quick access:

```
My Servers:
- Development: http://192.168.1.10:3000
- Testing: http://192.168.1.11:3000
- Production: http://192.168.1.12:3000
```

## Network Requirements

### Required Ports

Each application server must have these ports accessible from the network:

| Service | Port | Protocol | Required For |
|---------|------|----------|--------------|
| Frontend | 3000 | TCP | Web UI access |
| Backend API | 5000 | TCP | API requests from frontend |
| PostgreSQL | 5432 | TCP | Database admin (CloudBeaver, external tools) |
| CloudBeaver | 8978 | TCP | Database management UI |

### Firewall Rules

#### On Application Servers

**Windows Firewall**:
```powershell
# Allow incoming connections on required ports
New-NetFirewallRule -DisplayName "Todo App Frontend" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow
New-NetFirewallRule -DisplayName "Todo App Backend" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
New-NetFirewallRule -DisplayName "Todo App PostgreSQL" -Direction Inbound -Protocol TCP -LocalPort 5432 -Action Allow
New-NetFirewallRule -DisplayName "Todo App CloudBeaver" -Direction Inbound -Protocol TCP -LocalPort 8978 -Action Allow
```

**Linux (ufw)**:
```bash
sudo ufw allow 3000/tcp comment "Todo Frontend"
sudo ufw allow 5000/tcp comment "Todo Backend"
sudo ufw allow 5432/tcp comment "Todo PostgreSQL"
sudo ufw allow 8978/tcp comment "Todo CloudBeaver"
sudo ufw reload
```

**Linux (firewalld)**:
```bash
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=5432/tcp
sudo firewall-cmd --permanent --add-port=8978/tcp
sudo firewall-cmd --reload
```

#### Network-Level Firewall

Ensure your network firewall allows:
- **Inbound**: TCP ports 3000, 5000, 5432, 8978 to application servers
- **Outbound**: HTTP/HTTPS for Docker image pulls (if using proxy, configure `.env.build`)

### Network Discovery

Clients need to know server IP addresses. Options:

1. **Static IP Assignment**: Assign fixed IPs to servers (recommended)
2. **DNS Entries**: Create DNS records (e.g., `todoapp1.company.local`)
3. **Documentation**: Maintain a list of server addresses

## Testing Connectivity

### From Server Itself

On each application server, verify local access:

```bash
# Frontend
curl -s http://localhost:3000 | head -n 5

# Backend health
curl -s http://localhost:5000/health

# Backend API
curl -s http://localhost:5000/api/todos

# PostgreSQL (requires psql)
docker exec -it todo_postgres psql -U todouser -d tododb -c "SELECT 1;"
```

### From Client Machines

Test network connectivity from client machines:

```bash
# Replace 192.168.1.10 with your server's IP

# Frontend reachable
curl -s http://192.168.1.10:3000 | head -n 5

# Backend health
curl -s http://192.168.1.10:5000/health

# Backend API
curl -s http://192.168.1.10:5000/api/todos
```

### Browser Testing

Open browser on client machine and test:

1. **Access Frontend**: `http://192.168.1.10:3000`
2. **Open Developer Console** (F12)
3. **Check Console Logs** for API URL detection:
   ```
   [CONFIG] Detecting API URL for hostname: 192.168.1.10
   [CONFIG] External access detected, using: http://192.168.1.10:5000
   [CONFIG] API URL configured as: http://192.168.1.10:5000
   ```
4. **Create a Todo** to verify full functionality
5. **Check Network Tab** to confirm API requests go to correct URL

### Server Independence Verification

Verify each server operates independently:

1. Create a todo on Server 1 (`http://192.168.1.10:3000`)
   - Example: "Task on Server 1"
2. Navigate to Server 2 (`http://192.168.1.11:3000`)
3. Verify the todo does NOT appear (separate databases)
4. Create different todo on Server 2
   - Example: "Task on Server 2"
5. Navigate back to Server 1
6. Verify only original todo appears

**Expected**: Each server maintains its own data.

## Configuration Examples

### Scenario 1: Standard Office Network

**Network**: `192.168.1.0/24`
**Servers**:
- `app_server1`: 192.168.1.10
- `app_server2`: 192.168.1.11

**`.env` on both servers**:
```bash
POSTGRES_HOST=0.0.0.0
BACKEND_HOST=0.0.0.0
FRONTEND_HOST=0.0.0.0
CLOUDBEAVER_HOST=0.0.0.0
```

**Client access**:
- Server 1: `http://192.168.1.10:3000`
- Server 2: `http://192.168.1.11:3000`

### Scenario 2: Different Port Numbers

If port 3000 conflicts, change it per server:

**app_server1 `.env`**:
```bash
FRONTEND_PORT=3000
BACKEND_PORT=5000
```

**app_server2 `.env`**:
```bash
FRONTEND_PORT=3001
BACKEND_PORT=5001
```

**Client access**:
- Server 1: `http://192.168.1.10:3000`
- Server 2: `http://192.168.1.11:3001`

**IMPORTANT**: Dynamic API detection still works because it uses `hostname:5000` pattern. If you change backend port, you need to update `frontend/public/config.js`.

### Scenario 3: Using Hostnames with DNS

If your network has DNS:

**DNS entries**:
```
todo-dev.company.local  → 192.168.1.10
todo-test.company.local → 192.168.1.11
todo-prod.company.local → 192.168.1.12
```

**Client access**:
- Development: `http://todo-dev.company.local:3000`
- Testing: `http://todo-test.company.local:3000`
- Production: `http://todo-prod.company.local:3000`

Frontend automatically detects hostname and constructs correct backend URL.

### Scenario 4: Behind Corporate Proxy

**app_server1 `.env.build`**:
```bash
HTTP_PROXY=http://squid.alpine.co.jp:8080
HTTPS_PROXY=http://squid.alpine.co.jp:8080
NO_PROXY=localhost,127.0.0.1,frontend,backend,postgres,192.168.1.0/24
```

**Build with proxy**:
```bash
# Windows
tests\scripts\build-with-proxy.bat

# Linux
tests/scripts/build-with-proxy.sh
```

See `PROXY-CONFIG.md` for details.

## Security Considerations

### Database Access

PostgreSQL is exposed on `0.0.0.0:5432` for network access. Consider:

1. **Change default password** in `.env`:
   ```bash
   POSTGRES_PASSWORD=YourSecurePassword123!
   ```

2. **Restrict PostgreSQL access** using `pg_hba.conf`:
   ```bash
   # Only allow connections from specific network
   host    all             all             192.168.1.0/24          md5
   ```

3. **Use firewall rules** to limit database access to admin machines only

### HTTPS / TLS

The application runs on HTTP by default. For production:

1. **Use reverse proxy** (nginx, Apache) with SSL certificates
2. **Terminate TLS** at proxy level
3. **Proxy to Docker** containers on localhost

Example nginx configuration:
```nginx
server {
    listen 443 ssl;
    server_name todo-prod.company.local;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Authentication

The application has NO authentication. Anyone with network access can:
- View all todos
- Create, edit, delete todos
- Access database via CloudBeaver

For production, implement:
1. User authentication (login system)
2. Authorization (user-specific todos)
3. API authentication (JWT tokens, API keys)

## Troubleshooting

### Cannot Access Frontend from Client Machine

**Symptoms**: Browser shows "Cannot connect" or "Connection refused"

**Checks**:
1. Verify server is reachable:
   ```bash
   ping 192.168.1.10
   ```

2. Check if port 3000 is open:
   ```bash
   # Windows (PowerShell)
   Test-NetConnection -ComputerName 192.168.1.10 -Port 3000

   # Linux
   nc -zv 192.168.1.10 3000
   ```

3. Check firewall on application server:
   ```bash
   # Windows
   Get-NetFirewallRule -DisplayName "Todo*"

   # Linux
   sudo ufw status
   ```

4. Check Docker port binding:
   ```bash
   docker-compose ps
   # Should show: 0.0.0.0:3000->3000/tcp
   ```

5. Check if frontend container is running:
   ```bash
   docker ps --filter "name=frontend"
   ```

### Frontend Loads But Shows API Errors

**Symptoms**: Frontend UI appears but todos don't load, console shows 404 or network errors

**Checks**:
1. Open browser console (F12) and check API URL:
   ```
   [CONFIG] API URL configured as: http://192.168.1.10:5000
   ```

2. Verify backend is accessible:
   ```bash
   curl http://192.168.1.10:5000/health
   ```

3. Check backend container logs:
   ```bash
   docker-compose logs backend
   ```

4. Verify CORS is working (check browser console for CORS errors)

5. Check if backend port 5000 is open on firewall

### Database Connection Errors

**Symptoms**: Backend logs show "could not connect to server"

**Checks**:
1. Check PostgreSQL container:
   ```bash
   docker-compose ps postgres
   ```

2. Check database health:
   ```bash
   docker-compose exec postgres pg_isready -U todouser
   ```

3. Check database connection from backend:
   ```bash
   docker-compose exec backend python -c "
   import psycopg2
   conn = psycopg2.connect('postgresql://todouser:todopass@postgres:5432/tododb')
   print('Connected!')
   conn.close()
   "
   ```

4. Check `DATABASE_URL` environment variable:
   ```bash
   docker-compose exec backend env | grep DATABASE_URL
   ```

### Corporate Proxy Blocking Requests

**Symptoms**: Build fails, cannot pull Docker images, or external requests fail

**Solution**: Configure proxy settings in `.env.build`:

```bash
cp .env.build.example .env.build
# Edit with your proxy settings
```

See `PROXY-CONFIG.md` for complete proxy configuration guide.

### Different Client Machines See Different Behavior

**Symptoms**: Works on some clients but not others

**Common Causes**:
1. **Client firewall** blocking outbound connections
2. **Corporate web filter** (like InterSafe WebFilter) blocking requests
3. **DNS issues** if using hostnames instead of IPs
4. **Proxy settings** on client browser

**Checks**:
1. Test from client using curl:
   ```bash
   curl http://192.168.1.10:3000
   curl http://192.168.1.10:5000/health
   ```

2. Check browser proxy settings (Settings → Network → Proxy)

3. Try different browser or incognito mode

4. Check client machine hosts file for overrides

### Todos Not Persisting After Restart

**Symptoms**: Created todos disappear after `docker-compose down`

**Cause**: Database volume was removed

**Solution**: Use `docker-compose down` WITHOUT `-v` flag:

```bash
# WRONG - Removes volumes (deletes data)
docker-compose down -v

# CORRECT - Preserves volumes (keeps data)
docker-compose down
```

**Verify volumes exist**:
```bash
docker volume ls | grep postgres_data
```

## Monitoring and Maintenance

### Checking Server Status

Create a monitoring script that checks all servers:

**check_servers.sh** (Linux/Mac):
```bash
#!/bin/bash

SERVERS=("192.168.1.10" "192.168.1.11" "192.168.1.12")

for server in "${SERVERS[@]}"; do
    echo "Checking $server..."
    response=$(curl -s -o /dev/null -w "%{http_code}" http://$server:5000/health)

    if [ "$response" = "200" ]; then
        echo "  ✓ $server is healthy"
    else
        echo "  ✗ $server is DOWN (HTTP $response)"
    fi
done
```

**check_servers.bat** (Windows):
```batch
@echo off
setlocal enabledelayedexpansion

set "SERVERS=192.168.1.10 192.168.1.11 192.168.1.12"

for %%s in (%SERVERS%) do (
    echo Checking %%s...
    curl -s -o nul -w "%%{http_code}" http://%%s:5000/health > temp.txt
    set /p response=<temp.txt

    if "!response!"=="200" (
        echo   [OK] %%s is healthy
    ) else (
        echo   [FAILED] %%s is DOWN
    )
)

del temp.txt
```

### Viewing Logs

**On each server**:
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend

# Follow mode (real-time)
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Updating Application

To update the application on all servers:

1. **Pull latest code**:
   ```bash
   git pull
   ```

2. **Rebuild images**:
   ```bash
   docker-compose build
   ```

3. **Restart services** (minimal downtime):
   ```bash
   docker-compose up -d
   ```

4. **Verify health**:
   ```bash
   curl http://localhost:5000/health
   ```

### Backing Up Database

**Create backup**:
```bash
# Create backup directory
mkdir -p backups

# Backup database
docker exec todo_postgres pg_dump -U todouser tododb > backups/backup_$(date +%Y%m%d_%H%M%S).sql
```

**Restore backup**:
```bash
# Stop backend to prevent conflicts
docker stop todo_backend

# Restore database
cat backups/backup_20240115_103000.sql | docker exec -i todo_postgres psql -U todouser tododb

# Restart backend
docker start todo_backend
```

## Migration from Localhost to Network

If you have an existing localhost deployment and want to migrate to network deployment:

### Step 1: Backup Data
```bash
docker exec todo_postgres pg_dump -U todouser tododb > backup.sql
```

### Step 2: Update Configuration

Update `.env` to use `0.0.0.0` binding:
```bash
POSTGRES_HOST=0.0.0.0
BACKEND_HOST=0.0.0.0
FRONTEND_HOST=0.0.0.0
CLOUDBEAVER_HOST=0.0.0.0
```

### Step 3: Rebuild and Restart
```bash
docker-compose down
docker-compose up -d
```

### Step 4: Restore Data
```bash
cat backup.sql | docker exec -i todo_postgres psql -U todouser tododb
```

### Step 5: Test Network Access

From another machine:
```bash
curl http://<server-ip>:5000/health
```

Open browser:
```
http://<server-ip>:3000
```

## Additional Services

### CloudBeaver Database Administration

Each server has CloudBeaver for database management:

**Access**: `http://192.168.1.10:8978`

**First-time setup**:
1. Create admin user
2. Add PostgreSQL connection:
   - Host: `postgres`
   - Port: `5432`
   - Database: `tododb`
   - Username: `todouser`
   - Password: `todopass`

**Note**: Default credentials from previous setup may be:
- Username: `todouser`
- Password: `Password_00`

See `CLAUDE.md` for more CloudBeaver details.

## Related Documentation

- **README.md** - Project overview and quick start
- **TESTING.md** - Comprehensive testing guide
- **WINDOWS.md** - Windows-specific development instructions
- **PROXY-CONFIG.md** - Proxy configuration for corporate networks
- **CLAUDE.md** - Development guidelines for Claude Code

## Support

For issues specific to network deployment:

1. Check **Troubleshooting** section above
2. Verify **Network Requirements** are met
3. Review **Docker logs** on the affected server
4. Test **connectivity** from client to server
5. Check **firewall rules** on both server and client

For general application issues, see main `README.md` and `TESTING.md`.
