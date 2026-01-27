# CORTEX Docker Deployment Guide
## Complete Step-by-Step Instructions

**Document:** 09-DEPLOYMENT-GUIDE.md  
**Date:** 2026-01-27  
**Phase:** 0 Complete  
**Status:** PRODUCTION READY  
**Authority:** CORTEX Master Orchestrator

---

## 📋 Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Python Tooling Architecture](#2-python-tooling-architecture)
3. [Quick Start (5 Minutes)](#3-quick-start-5-minutes)
4. [Development Deployment](#4-development-deployment)
5. [Production Deployment](#5-production-deployment)
6. [Docker MCP Gateway Integration](#6-docker-mcp-gateway-integration)
7. [Client Integrations](#7-client-integrations)
8. [Configuration Reference](#8-configuration-reference)
9. [Health Monitoring](#9-health-monitoring)
10. [Troubleshooting](#10-troubleshooting)
11. [Upgrade & Rollback](#11-upgrade--rollback)

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

## 2. Python Tooling Architecture

### 2.1 Installation Model: Centralized (ONE-TIME)

**Key Concept:** Python is NOT installed per-user. Instead, it's installed ONCE during Docker image build and reused by ALL users.

```
Docker Image Build (ONCE by CI/CD)
    ├─ Python 3.11 installed (143 MB)
    ├─ All 142 dependencies installed (350 MB)
    ├─ CORTEX source code packaged (15 MB)
    └─ Result: cortex/mcp-server:latest (600-800 MB)
    
                      ↓ SHARED BY ALL USERS
    
User Environment (NO Python install needed!)
    ├─ docker pull cortex/mcp-server:latest (~3-5 min, first time)
    ├─ docker run -d -p 8443:8443 cortex/mcp-server:latest
    ├─ MCP server starts (Python already in image!)
    └─ IDE connects to localhost:8443
```

### 2.2 How It Works

#### When Happens: Image Build Time (ONCE)

```dockerfile
# Dockerfile (executed ONCE in CI/CD pipeline)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git curl

# Install Python dependencies (HAPPENS HERE - ONE TIME)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir fastapi uvicorn[standard]

# Copy source code
COPY cortex/ ./cortex/
COPY cortex_brain/ ./cortex_brain/

# Result: Docker image with EVERYTHING pre-installed
```

**What This Means:**
- Python 3.11 is installed INSIDE the image, not on user's machine
- All 142 dependencies are installed INSIDE the image
- This happens ONCE when image is built
- User's machine doesn't need Python installed ✅

#### When Happens: User Runtime (Per Session)

```bash
# User just needs to run (NO Python setup needed!):
$ docker pull cortex/mcp-server:latest    # First time: ~3-5 min (downloads image)
$ docker run -d -p 8443:8443 cortex/mcp-server:latest

# Result: MCP server starts instantly
# Python is already in the image!
# No pip install needed on user's machine!
```

### 2.3 Installation Models by Deployment Type

#### Model 1: Solo Developer (Local Docker Desktop)

```bash
# Developer's machine
$ git clone https://github.com/asifhussain60/CORTEX.git
$ cd CORTEX/_workspaces/docker-plan
$ docker compose up -d

# Result:
# - Docker builds image locally (first time: ~10 min, includes Python)
# - Starts container
# - Python already in container! ✅
# - MCP server ready at localhost:8443

# Subsequent runs (Day 2, 3, ...):
$ docker compose up -d    # Instant! (cached layers)

# Per-developer cost: 10 min (one-time), then instant
```

#### Model 2: Team Collaboration (Shared Central Server)

```yaml
# Architecture:
# Central CI/CD Pipeline (GitHub Actions)
#   └─ Builds cortex/mcp-server:latest image
#   └─ Pushes to Docker Hub
#
# Team Members:
#   ├─ docker pull cortex/mcp-server:latest (first time: ~3-5 min)
#   ├─ All get IDENTICAL Python version
#   ├─ All get IDENTICAL dependencies
#   ├─ No conflicts between team members
#   └─ No "works on my machine" problems ✅

# Each team member:
$ docker run -d -p 8443:8443 cortex/mcp-server:latest
$ # Configure IDE → Done! ✅
```

#### Model 3: Enterprise (100-500+ Users)

```
Architecture:
    Central Docker Registry (Docker Hub / ECR / Artifactory)
        └─ cortex/mcp-server:latest (pre-built, all deps)
    
    Kubernetes Cluster
        ├─ 3-10 pod replicas (auto-scaling)
        ├─ Load balancer (routes requests)
        ├─ Persistent storage (Docker volumes)
        └─ All pods run IDENTICAL image
    
    Users (100-500+)
        ├─ Point IDE to: enterprise.cortex.example.com:8443
        ├─ Load balancer routes to replica containers
        ├─ All users get consistent environment
        └─ All using IDENTICAL Python + dependencies ✅

Per-User Cost: ~2 min (first IDE config), then instant
Central Cost: One image build + deployment
Scaling: Horizontal (add more pod replicas as needed)
```

### 2.4 Installation Location Breakdown

```
Docker Image Contents:

Base Layer (FROM python:3.11-slim):
  ├─ Python 3.11: 143 MB (included in slim image)
  ├─ System libs: ~50 MB
  └─ Total: ~200 MB

Dependencies Layer (pip install):
  ├─ Core: pyyaml, pydantic (parsing, validation)
  ├─ MCP: websockets, aiofiles, httptools (communication)
  ├─ Web: fastapi, uvicorn (API server)
  ├─ Optional: pandas, numpy, scikit-learn (analytics)
  └─ Total: 350 MB (pre-compiled, cached)

Application Layer:
  ├─ cortex/ directory (1,592 Python files)
  ├─ cortex_brain/ directory (brain files)
  ├─ Test suite (500+ test files)
  └─ Total: ~15 MB

─────────────────────────────────
TOTAL IMAGE SIZE: ~600-800 MB
SHARED ACROSS: ALL users (storage efficient!)
```

**Key Point:** The entire image is built ONCE and reused by everyone. No per-user duplication of Python or dependencies!

### 2.5 Comparison: Local Python vs. Docker

```
LOCAL PYTHON INSTALLATION (❌ NOT RECOMMENDED):
├─ User must install Python 3.11
├─ User must run: pip install -r requirements.txt
├─ Time per user: 30-60 minutes
├─ Disk space per user: 500+ MB (separate environment)
├─ Version conflicts: Common (different Python versions per user)
├─ Dependency conflicts: Common (pip conflicts)
├─ Maintenance: Per-user (each user manages their own setup)
└─ Scaling issue: N users × 30-60 min = massive overhead

DOCKER CONTAINER (✅ RECOMMENDED):
├─ Python pre-installed in image
├─ All dependencies pre-installed in image
├─ Time per user (first run): <5 minutes
├─ Disk space per user: 0 MB (shared image!)
├─ Version consistency: 100% (all users identical)
├─ Dependency conflicts: Impossible (all in image)
├─ Maintenance: Central (one image build, all users get it)
└─ Scaling solution: 1 image → any number of users ✅
```

### 2.6 Python Tooling FAQ

**Q: I don't have Python installed on my machine. Is that a problem?**
```
A: No problem! ✅

Python is inside the Docker container, not on your machine.
Docker handles everything. Just install Docker (not Python).
```

**Q: Do I need to run pip install?**
```
A: No! ✅

All dependencies are pre-installed in the Docker image.
When you run the container, Python and all packages are ready.
No pip commands needed on your machine.
```

**Q: What if I have Python 3.9 but CORTEX needs 3.11?**
```
A: Doesn't matter! ✅

Your Python version is irrelevant. Container has Python 3.11.
Your local Python is never used by CORTEX.
Container is completely isolated from your machine.
```

**Q: How do I update Python or dependencies?**
```
A: Central team rebuilds image:

1. Update requirements.txt in repo
2. CI/CD pipeline rebuilds image (Python 3.11 + new deps)
3. Image pushed to registry (Docker Hub, ECR, etc.)
4. All users: docker pull cortex/mcp-server:latest
5. Everyone gets updated Python + deps ✅

No per-user setup needed!
```

**Q: What if I want to run development version (with editable install)?**
```
A: Use docker-compose with volume mount:

# docker-compose.yml
services:
  cortex-mcp:
    build: .
    volumes:
      - ./cortex:/app/cortex    # Mount source code
      - ./cortex_brain:/app/cortex_brain
    # Changes to source are reflected instantly!
```

**Q: Does this work with my IDE (VS Code, Cursor, Claude)?**
```
A: Yes! ✅

1. Start CORTEX in Docker: docker run -d -p 8443:8443 ...
2. Configure IDE: Point MCP endpoint to localhost:8443
3. IDE connects to MCP server in container
4. Use /CORTEX commands normally
5. Python in container handles everything ✅
```

### 2.7 Troubleshooting Python Tooling Issues

**Issue: "docker: command not found"**
```
Solution: Install Docker
  - macOS: brew install --cask docker
  - Windows: Download Docker Desktop
  - Linux: curl -fsSL https://get.docker.com | sh
```

**Issue: "Container exits immediately after starting"**
```
Solution: Check logs
  $ docker logs <container-id>
  Look for Python import errors or missing dependencies.
  If you see Python errors, report with logs attached.
```

**Issue: "Python version mismatch error"**
```
Solution: You're probably using local Python (wrong!)
  
  Don't run Python directly:
    ❌ python -c "import cortex"
  
  Use container instead:
    ✅ docker run cortex/mcp-server:latest
    OR
    ✅ Configure IDE to connect to container
```

---

## 3. Quick Start (5 Minutes)

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

**🎉 CORTEX is now running!** Skip to [Section 7](#7-client-integrations) to connect your IDE.

---

## 4. Development Deployment

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

## 5. Production Deployment

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

## 6. Docker MCP Gateway Integration

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

## 7. Client Integrations

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

## 8. Configuration Reference

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

## 9. Health Monitoring

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

## 10. Troubleshooting

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

## 11. Upgrade ## 10. Upgrade & Rollback Rollback

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
