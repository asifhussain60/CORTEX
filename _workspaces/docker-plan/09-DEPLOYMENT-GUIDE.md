# CORTEX Docker Deployment Guide
## Complete Step-by-Step Instructions

**Document:** 09-DEPLOYMENT-GUIDE.md  
**Version:** 1.0  
**Date:** 2026-01-27  
**Author:** Asif Hussain  
**Status:** PRODUCTION READY

---

## 📋 Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Quick Start (5 Minutes)](#2-quick-start-5-minutes)
3. [Development Deployment](#3-development-deployment)
4. [Production Deployment](#4-production-deployment)
5. [Docker MCP Gateway Integration](#5-docker-mcp-gateway-integration)
6. [Client Integrations](#6-client-integrations)
7. [Configuration Reference](#7-configuration-reference)
8. [Health Monitoring](#8-health-monitoring)
9. [Troubleshooting](#9-troubleshooting)
10. [Upgrade & Rollback](#10-upgrade--rollback)

---

## 1. Prerequisites

### 1.1 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Docker** | 24.0+ | 25.0+ |
| **Docker Desktop** | 4.48+ | Latest |
| **RAM** | 4 GB | 8 GB |
| **Disk** | 10 GB | 20 GB |
| **CPU** | 2 cores | 4 cores |

### 1.2 Software Installation

#### macOS
```bash
# Install Docker Desktop
brew install --cask docker

# Verify installation
docker --version
docker compose version
```

#### Windows
```powershell
# Install Docker Desktop via winget
winget install Docker.DockerDesktop

# Or download from: https://www.docker.com/products/docker-desktop/
# Verify installation
docker --version
docker compose version
```

#### Linux (Ubuntu/Debian)
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose plugin
sudo apt-get install docker-compose-plugin

# Verify
docker --version
docker compose version
```

### 1.3 Clone CORTEX Repository

```bash
# Clone the repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# Checkout the docker-clean branch (after migration)
git checkout CORTEX-docker
```

---

## 2. Quick Start (5 Minutes)

For users who want to get CORTEX running immediately:

```bash
# Step 1: Navigate to CORTEX directory
cd /path/to/CORTEX

# Step 2: Build and start CORTEX
docker compose up -d

# Step 3: Verify it's running
docker compose ps

# Step 4: Check health
curl http://localhost:8443/health

# Step 5: List available tools
curl http://localhost:8443/mcp/tools
```

**Expected Output:**
```json
{
  "status": "healthy",
  "wired": true,
  "wiring_hash": "a1b2c3d4e5f6g7h8",
  "orchestrator_count": 23,
  "uptime_seconds": 45.2
}
```

**🎉 CORTEX is now running!** Skip to [Section 6](#6-client-integrations) to connect your IDE.

---

## 3. Development Deployment

### 3.1 Directory Structure

```
CORTEX/
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Development compose file
├── docker-compose.prod.yml       # Production compose file
├── .dockerignore                 # Excluded files
├── cortex/                       # Source code
│   ├── mcp/                      # MCP server
│   ├── orchestrators/            # 23 orchestrators
│   └── wiring/                   # Git-backed wiring
├── cortex_brain/                 # Brain modules
└── deployment/                   # Deployment configs
    ├── mcp-gateway-config.yaml   # MCP Gateway config
    ├── prometheus.yml            # Metrics config
    └── nginx.conf                # Load balancer config
```

### 3.2 Development docker-compose.yml

Create or verify `docker-compose.yml`:

```yaml
version: '3.8'

services:
  cortex-mcp:
    build:
      context: .
      dockerfile: Dockerfile
    image: cortex/mcp-server:dev
    container_name: cortex-mcp
    ports:
      - "8443:8443"
    environment:
      - CORTEX_ENV=development
      - CORTEX_LOG_LEVEL=DEBUG
      - CORTEX_MCP_HOST=0.0.0.0
      - CORTEX_MCP_PORT=8443
    volumes:
      # Mount wiring specs for live updates during development
      - ./cortex/wiring/specifications:/app/cortex/wiring/specifications:ro
      # Mount logs for debugging
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8443/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    networks:
      - cortex-network

networks:
  cortex-network:
    driver: bridge
```

### 3.3 Build and Run (Development)

```bash
# Build the image
docker compose build

# Start in foreground (see logs)
docker compose up

# Or start in background
docker compose up -d

# View logs
docker compose logs -f cortex-mcp

# Stop
docker compose down
```

### 3.4 Development Workflow

```bash
# Rebuild after code changes
docker compose build --no-cache
docker compose up -d

# Or use watch mode (requires Docker Compose 2.22+)
docker compose watch

# Execute commands inside container
docker compose exec cortex-mcp python -c "from cortex.wiring import is_wired; print(is_wired())"

# Run tests inside container
docker compose exec cortex-mcp pytest tests/ -v
```

---

## 4. Production Deployment

### 4.1 Production docker-compose.prod.yml

```yaml
version: '3.8'

services:
  cortex-mcp:
    image: cortex/mcp-server:${CORTEX_VERSION:-latest}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
    ports:
      - "8443:8443"
    environment:
      - CORTEX_ENV=production
      - CORTEX_LOG_LEVEL=INFO
      - CORTEX_MCP_HOST=0.0.0.0
      - CORTEX_MCP_PORT=8443
      - CORTEX_METRICS_ENABLED=true
      - CORTEX_METRICS_PORT=9090
    volumes:
      # Persistent volumes
      - cortex-audit-logs:/app/logs
      - cortex-state:/app/.cortex/state
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8443/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - cortex-network
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"

  # Prometheus for metrics
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./deployment/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    networks:
      - cortex-network
    profiles:
      - monitoring

  # Nginx load balancer with TLS
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./deployment/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./deployment/ssl:/etc/nginx/ssl:ro
    depends_on:
      - cortex-mcp
    networks:
      - cortex-network
    profiles:
      - loadbalancer

volumes:
  cortex-audit-logs:
  cortex-state:
  prometheus-data:

networks:
  cortex-network:
    driver: bridge
```

### 4.2 Production Deployment Steps

```bash
# Step 1: Set version
export CORTEX_VERSION=2.0.0

# Step 2: Pull/Build production image
docker compose -f docker-compose.prod.yml build
# Or pull from registry:
# docker pull cortex/mcp-server:${CORTEX_VERSION}

# Step 3: Deploy with 3 replicas
docker compose -f docker-compose.prod.yml up -d

# Step 4: Verify all replicas are healthy
docker compose -f docker-compose.prod.yml ps

# Step 5: Check logs across replicas
docker compose -f docker-compose.prod.yml logs -f
```

### 4.3 TLS/SSL Configuration

Create `deployment/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream cortex_backend {
        least_conn;
        server cortex-mcp:8443;
    }

    server {
        listen 80;
        server_name cortex.company.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name cortex.company.com;

        ssl_certificate /etc/nginx/ssl/cortex.crt;
        ssl_certificate_key /etc/nginx/ssl/cortex.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        location / {
            proxy_pass http://cortex_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            proxy_read_timeout 300;
        }

        location /health {
            proxy_pass http://cortex_backend/health;
            access_log off;
        }

        location /metrics {
            proxy_pass http://cortex_backend/metrics;
            # Restrict to internal network
            allow 10.0.0.0/8;
            deny all;
        }
    }
}
```

### 4.4 Generate SSL Certificates

```bash
# Development (self-signed)
mkdir -p deployment/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout deployment/ssl/cortex.key \
  -out deployment/ssl/cortex.crt \
  -subj "/CN=cortex.local"

# Production (Let's Encrypt)
# Use certbot or your preferred ACME client
```

---

## 5. Docker MCP Gateway Integration

### 5.1 Why Use MCP Gateway?

| Feature | Without Gateway | With Gateway |
|---------|-----------------|--------------|
| Client config | Manual JSON per client | One-click in Docker Desktop |
| Authentication | Custom implementation | Built-in |
| Secrets | Environment variables | Centralized management |
| Multi-client | Custom routing | Automatic |
| Discoverability | None | Docker MCP Catalog |

### 5.2 Add MCP Gateway to docker-compose.yml

```yaml
services:
  # Add this service
  mcp-gateway:
    image: docker/mcp-gateway:latest
    container_name: cortex-mcp-gateway
    ports:
      - "6600:6600"
    environment:
      - MCP_GATEWAY_LOG_LEVEL=info
      - MCP_GATEWAY_AUTH_ENABLED=true
    volumes:
      - ./deployment/mcp-gateway-config.yaml:/etc/mcp-gateway/config.yaml:ro
    depends_on:
      cortex-mcp:
        condition: service_healthy
    networks:
      - cortex-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6600/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  cortex-mcp:
    # ... existing configuration ...
```

### 5.3 Create Gateway Configuration

Create `deployment/mcp-gateway-config.yaml`:

```yaml
# Docker MCP Gateway Configuration for CORTEX
version: "1.0"

servers:
  cortex:
    name: "CORTEX Orchestrator"
    description: "AI-powered development orchestrator with 23 specialized orchestrators"
    url: "http://cortex-mcp:8443"
    health_endpoint: "/health"
    tools_endpoint: "/mcp/tools"
    execute_endpoint: "/mcp/execute"
    
    capabilities:
      - intent_classification
      - tdd_workflow
      - code_refactoring
      - documentation_generation
      - governance_enforcement
      - planning
      - deployment
    
    auth:
      type: "api_key"
      header: "X-CORTEX-API-KEY"
    
    rate_limit:
      requests_per_minute: 60
      burst: 10

clients:
  - name: "vscode"
    enabled: true
  - name: "claude-desktop"
    enabled: true
  - name: "cursor"
    enabled: true
  - name: "windsurf"
    enabled: true
```

### 5.4 Start with Gateway

```bash
# Start all services including Gateway
docker compose up -d

# Verify Gateway is running
curl http://localhost:6600/health

# List available servers through Gateway
curl http://localhost:6600/v1/servers
```

---

## 6. Client Integrations

### 6.1 VS Code Integration

#### Option A: Via Docker MCP Toolkit (Recommended)

1. Open **Docker Desktop**
2. Navigate to **MCP Toolkit** (left sidebar)
3. Go to **My Servers** tab
4. Find **CORTEX Orchestrator**
5. Click **Connect to VS Code**
6. VS Code will open with CORTEX tools available

#### Option B: Manual Configuration

Create/edit `.vscode/settings.json`:

```json
{
  "mcp.servers": {
    "cortex": {
      "url": "http://localhost:8443",
      "name": "CORTEX Orchestrator",
      "tools": {
        "discovery": "/mcp/tools",
        "execute": "/mcp/execute"
      }
    }
  }
}
```

#### Option C: With MCP Gateway

```json
{
  "mcp.servers": {
    "cortex": {
      "url": "http://localhost:6600",
      "name": "CORTEX (via Gateway)"
    }
  }
}
```

### 6.2 Claude Desktop Integration

#### Option A: Via Docker MCP Toolkit (Recommended)

1. Open **Docker Desktop**
2. Navigate to **MCP Toolkit**
3. Click **Connect to Claude Desktop**
4. Claude Desktop will auto-configure

#### Option B: Manual Configuration

Edit Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "cortex": {
      "command": "curl",
      "args": ["-X", "POST", "http://localhost:8443/mcp/execute"],
      "env": {}
    }
  }
}
```

### 6.3 Cursor Integration

1. Open **Docker Desktop** → **MCP Toolkit**
2. Click **Connect to Cursor**
3. Or manually configure in Cursor settings

### 6.4 Windsurf Integration

1. Open **Docker Desktop** → **MCP Toolkit**
2. Click **Connect to Windsurf**
3. Or add MCP server URL in Windsurf settings

### 6.5 Verify Integration

Test CORTEX is accessible from your IDE:

```
# In VS Code/Claude/Cursor chat:
"Use CORTEX to analyze this code for refactoring opportunities"

# Expected: CORTEX tools appear and can be invoked
```

---

## 7. Configuration Reference

### 7.1 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CORTEX_ENV` | `development` | Environment: `development`, `production` |
| `CORTEX_LOG_LEVEL` | `INFO` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `CORTEX_MCP_HOST` | `0.0.0.0` | MCP server bind host |
| `CORTEX_MCP_PORT` | `8443` | MCP server port |
| `CORTEX_METRICS_ENABLED` | `false` | Enable Prometheus metrics |
| `CORTEX_METRICS_PORT` | `9090` | Metrics endpoint port |
| `CORTEX_API_KEY` | (none) | API key for authentication |
| `CORTEX_WIRING_LAZY` | `true` | Lazy orchestrator initialization |

### 7.2 Ports Reference

| Port | Service | Description |
|------|---------|-------------|
| `8443` | CORTEX MCP Server | Main MCP endpoint |
| `6600` | MCP Gateway | Docker MCP Gateway |
| `9090` | Prometheus | Metrics collection |
| `443` | Nginx | HTTPS (production) |
| `80` | Nginx | HTTP redirect |

### 7.3 Volume Reference

| Volume | Path in Container | Description |
|--------|-------------------|-------------|
| `cortex-audit-logs` | `/app/logs` | Audit trail persistence |
| `cortex-state` | `/app/.cortex/state` | Conversation state |
| `prometheus-data` | `/prometheus` | Metrics storage |

---

## 8. Health Monitoring

### 8.1 Health Check Endpoints

```bash
# Basic health check
curl http://localhost:8443/health

# Detailed wiring status
curl http://localhost:8443/wiring/hash

# Wiring order
curl http://localhost:8443/wiring/order

# Prometheus metrics
curl http://localhost:8443/metrics
```

### 8.2 Health Response Format

```json
{
  "status": "healthy",
  "wired": true,
  "wiring_hash": "a1b2c3d4e5f6g7h8",
  "orchestrator_count": 23,
  "uptime_seconds": 3600.5
}
```

### 8.3 Prometheus Metrics

```prometheus
# HELP cortex_wired Whether CORTEX is fully wired
# TYPE cortex_wired gauge
cortex_wired{} 1

# HELP cortex_orchestrator_count Number of wired orchestrators
# TYPE cortex_orchestrator_count gauge
cortex_orchestrator_count{} 23

# HELP cortex_uptime_seconds Server uptime in seconds
# TYPE cortex_uptime_seconds counter
cortex_uptime_seconds{} 3600.5

# HELP cortex_requests_total Total MCP requests
# TYPE cortex_requests_total counter
cortex_requests_total{tool="refactoring",status="success"} 42
```

### 8.4 Create Prometheus Config

Create `deployment/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'cortex'
    static_configs:
      - targets: ['cortex-mcp:8443']
    metrics_path: '/metrics'
```

### 8.5 Docker Health Checks

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' cortex-mcp

# View health check logs
docker inspect --format='{{json .State.Health}}' cortex-mcp | jq

# Manual health check
docker compose exec cortex-mcp curl -f http://localhost:8443/health
```

---

## 9. Troubleshooting

### 9.1 Common Issues

#### Container Won't Start

```bash
# Check logs
docker compose logs cortex-mcp

# Common causes:
# 1. Port already in use
lsof -i :8443
# Fix: Stop conflicting service or change port

# 2. Wiring failure
docker compose logs cortex-mcp | grep "WIRING"
# Fix: Check wiring.yaml syntax

# 3. Missing dependencies
docker compose exec cortex-mcp pip list
# Fix: Rebuild image
```

#### Health Check Failing

```bash
# Check if server is responding
docker compose exec cortex-mcp curl -v http://localhost:8443/health

# Check wiring status
docker compose exec cortex-mcp python -c "
from cortex.wiring import is_wired, get_cortex
print(f'Wired: {is_wired()}')
print(f'Orchestrators: {len(get_cortex().registry.get_all_specs())}')
"
```

#### MCP Gateway Can't Connect to CORTEX

```bash
# Verify network connectivity
docker compose exec mcp-gateway ping cortex-mcp

# Check CORTEX is healthy first
curl http://localhost:8443/health

# Verify Gateway config
docker compose exec mcp-gateway cat /etc/mcp-gateway/config.yaml
```

#### Client Can't Connect

```bash
# 1. Verify CORTEX is running
curl http://localhost:8443/health

# 2. Verify tools are discoverable
curl http://localhost:8443/mcp/tools

# 3. Check firewall/network
# macOS:
sudo pfctl -s rules

# Linux:
sudo iptables -L
```

### 9.2 Debug Mode

```bash
# Start with debug logging
CORTEX_LOG_LEVEL=DEBUG docker compose up

# Or modify environment in compose file
environment:
  - CORTEX_LOG_LEVEL=DEBUG
```

### 9.3 Reset Everything

```bash
# Stop and remove all containers, volumes, and networks
docker compose down -v

# Remove all CORTEX images
docker rmi $(docker images cortex/* -q)

# Clean Docker system
docker system prune -af

# Start fresh
docker compose up -d --build
```

### 9.4 Logs Location

| Log Type | Location | Access |
|----------|----------|--------|
| Container stdout | Docker logs | `docker compose logs cortex-mcp` |
| Audit trail | `/app/logs/audit.log` | `docker compose exec cortex-mcp cat /app/logs/audit.log` |
| Wiring logs | `/app/logs/wiring.log` | `docker compose exec cortex-mcp cat /app/logs/wiring.log` |

---

## 10. Upgrade & Rollback

### 10.1 Upgrade Process

```bash
# Step 1: Check current version
docker compose exec cortex-mcp python -c "import cortex; print(cortex.__version__)"

# Step 2: Pull new version
export CORTEX_VERSION=2.1.0
docker pull cortex/mcp-server:${CORTEX_VERSION}

# Step 3: Backup current state
docker compose exec cortex-mcp tar -czf /tmp/backup.tar.gz /app/logs /app/.cortex
docker cp cortex-mcp:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz

# Step 4: Rolling update (zero downtime)
docker compose -f docker-compose.prod.yml up -d --no-deps cortex-mcp

# Step 5: Verify new version
docker compose exec cortex-mcp python -c "import cortex; print(cortex.__version__)"
curl http://localhost:8443/health
```

### 10.2 Rollback Process

```bash
# Step 1: Identify previous version
docker images cortex/mcp-server --format "{{.Tag}}"

# Step 2: Rollback to previous version
export CORTEX_VERSION=2.0.0
docker compose -f docker-compose.prod.yml up -d --no-deps cortex-mcp

# Step 3: Verify rollback
curl http://localhost:8443/health

# Step 4: Restore backup if needed
docker cp ./backup-20260127.tar.gz cortex-mcp:/tmp/
docker compose exec cortex-mcp tar -xzf /tmp/backup.tar.gz -C /
```

### 10.3 Version Pinning

Always pin versions in production:

```yaml
# docker-compose.prod.yml
services:
  cortex-mcp:
    image: cortex/mcp-server:2.0.0  # Pinned version
    # NOT: cortex/mcp-server:latest
```

---

## 📋 Quick Reference Card

### Essential Commands

```bash
# Start CORTEX
docker compose up -d

# Stop CORTEX
docker compose down

# View logs
docker compose logs -f cortex-mcp

# Health check
curl http://localhost:8443/health

# List tools
curl http://localhost:8443/mcp/tools

# Execute tool
curl -X POST http://localhost:8443/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "refactoring", "args": {"code": "..."}}'

# Enter container shell
docker compose exec cortex-mcp /bin/bash

# Rebuild after changes
docker compose build --no-cache && docker compose up -d
```

### Important URLs

| URL | Description |
|-----|-------------|
| `http://localhost:8443` | CORTEX MCP Server |
| `http://localhost:8443/health` | Health check |
| `http://localhost:8443/mcp/tools` | Tool discovery |
| `http://localhost:8443/mcp/execute` | Tool execution |
| `http://localhost:8443/metrics` | Prometheus metrics |
| `http://localhost:6600` | MCP Gateway (if enabled) |
| `http://localhost:9090` | Prometheus UI (if enabled) |

---

## 📞 Support

- **GitHub Issues:** https://github.com/asifhussain60/CORTEX/issues
- **Documentation:** `docs/` folder in repository
- **Migration Plan:** `_workspaces/docker-plan/`

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-27  
**Next Review:** After migration completion
