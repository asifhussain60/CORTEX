# CORTEX Docker Setup
## Container Configuration for Enterprise Deployment

**Document:** docker-configuration-guide.md  
**Date:** 2026-01-27  

---

## 🐳 Dockerfile

```dockerfile
# CORTEX MCP Server - Production Container
# Entry Point: /CORTEX commands via MCP
#
# Build: docker build -t cortex/mcp-server:latest .
# Run:   docker run -d -p 8443:8443 cortex/mcp-server:latest

FROM python:3.11-slim AS base

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    CORTEX_ENV=production \
    CORTEX_LOG_LEVEL=INFO

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir fastapi uvicorn[standard]

# Copy source code
COPY cortex/ ./cortex/
COPY cortex_brain/ ./cortex_brain/

# Copy wiring specifications (Git-backed SSOT)
# These are the ONLY files that control wiring
COPY cortex/wiring/specifications/ ./cortex/wiring/specifications/

# Create non-root user for security
RUN useradd -m -u 1000 cortex && \
    chown -R cortex:cortex /app
USER cortex

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8443/health || exit 1

# Expose MCP port
EXPOSE 8443

# Start CORTEX MCP Server
# Wiring happens ONCE at container startup
CMD ["python", "-m", "uvicorn", "cortex.mcp.server:app", \
     "--host", "0.0.0.0", "--port", "8443", \
     "--workers", "4", "--loop", "uvloop"]
```

---

## 📦 docker-compose.yml (Development)

```yaml
version: '3.8'

services:
  cortex-mcp:
    build:
      context: .
      dockerfile: Dockerfile
    image: cortex/mcp-server:latest
    container_name: cortex-mcp
    ports:
      - "8443:8443"
    environment:
      - CORTEX_ENV=development
      - CORTEX_LOG_LEVEL=DEBUG
      - CORTEX_MCP_HOST=0.0.0.0
      - CORTEX_MCP_PORT=8443
    volumes:
      # Mount wiring specs for live updates during dev
      - ./cortex/wiring/specifications:/app/cortex/wiring/specifications:ro
      # Mount logs for debugging
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8443/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - cortex-network

networks:
  cortex-network:
    driver: bridge
```

---

## 🏭 docker-compose.prod.yml (Production)

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
    ports:
      - "8443:8443"
    environment:
      - CORTEX_ENV=production
      - CORTEX_LOG_LEVEL=INFO
      - CORTEX_MCP_HOST=0.0.0.0
      - CORTEX_MCP_PORT=8443
      - CORTEX_METRICS_ENABLED=true
      - CORTEX_METRICS_PORT=9090
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

  # Optional: Prometheus metrics
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./deployment/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    networks:
      - cortex-network
    profiles:
      - monitoring

  # Optional: Load balancer for multiple instances
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./deployment/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./deployment/ssl:/etc/nginx/ssl:ro
    depends_on:
      - cortex-mcp
    networks:
      - cortex-network
    profiles:
      - loadbalancer

networks:
  cortex-network:
    driver: bridge
```

---

## 📋 .dockerignore

```
# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
.venv
venv/
ENV/

# Testing
.pytest_cache
.coverage
htmlcov/
tests/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Documentation (not needed in container)
docs/
*.md
!README.md

# Archives and backups
_backups/
_workspaces/
*.bak

# Database files (should not exist, but just in case)
.cortex/
*.db
*.db-journal
*.db-wal
*.db-shm

# Development files
Makefile
docker-compose.override.yml
.env.local

# Logs
*.log
logs/

# Build artifacts
dist/
build/
*.egg-info/
```

---

## 🔧 MCP Server (cortex/mcp/server.py)

```python
"""
CORTEX MCP Server - FastAPI Implementation

Entry point for all MCP requests.
Wiring happens ONCE at startup.

Usage:
    uvicorn cortex.mcp.server:app --host 0.0.0.0 --port 8443
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from cortex.wiring import bootstrap_cortex, get_cortex, is_wired, get_wiring_hash
from cortex.infrastructure.logging.structured_logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Lifespan: Wire CORTEX once at startup
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Wiring happens HERE and ONLY HERE.
    Container startup = CORTEX wiring.
    """
    logger.info("=" * 60)
    logger.info("CORTEX MCP Server Starting")
    logger.info("=" * 60)
    
    # Wire CORTEX (happens ONCE)
    start_time = time.time()
    try:
        cortex = bootstrap_cortex()
        wiring_time = time.time() - start_time
        
        logger.info(f"✅ CORTEX wired in {wiring_time:.2f}s")
        logger.info(f"   Wiring hash: {cortex.wiring_hash}")
        logger.info(f"   Ready to serve requests")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.critical(f"❌ CORTEX wiring failed: {e}")
        raise
    
    yield  # Server runs here
    
    # Shutdown
    logger.info("CORTEX MCP Server Shutting Down")


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="CORTEX MCP Server",
    description="Cognitive Real-Time Execution System - MCP API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Request/Response Models
# =============================================================================

class MCPExecuteRequest(BaseModel):
    """Request to execute an MCP tool."""
    tool: str
    args: Dict[str, Any] = {}


class MCPExecuteResponse(BaseModel):
    """Response from MCP tool execution."""
    success: bool
    result: Any = None
    error: str = None
    execution_time_ms: float


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    wired: bool
    wiring_hash: str
    orchestrator_count: int
    uptime_seconds: float


class ToolInfo(BaseModel):
    """Information about an MCP tool."""
    name: str
    description: str
    parameters: Dict[str, Any]
    orchestrator: str


# =============================================================================
# Endpoints
# =============================================================================

_start_time = time.time()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns wiring status and orchestrator count.
    """
    cortex = get_cortex()
    
    return HealthResponse(
        status="healthy" if is_wired() else "unhealthy",
        wired=is_wired(),
        wiring_hash=get_wiring_hash() if is_wired() else "",
        orchestrator_count=len(cortex.registry.get_all_specs()),
        uptime_seconds=time.time() - _start_time
    )


@app.get("/mcp/tools", response_model=List[ToolInfo])
async def list_tools():
    """
    List all available MCP tools.
    
    Returns tool names, descriptions, and parameters.
    """
    cortex = get_cortex()
    tools = []
    
    for name, spec in cortex.registry.get_all_specs().items():
        tools.append(ToolInfo(
            name=name.lower().replace("orchestrator", ""),
            description=f"Execute {name} operations",
            parameters=spec.requires_params,
            orchestrator=name
        ))
    
    return tools


@app.post("/mcp/execute", response_model=MCPExecuteResponse)
async def execute_tool(request: MCPExecuteRequest):
    """
    Execute an MCP tool.
    
    This is the main entry point for /CORTEX commands.
    """
    start_time = time.time()
    
    try:
        cortex = get_cortex()
        
        # Map tool to orchestrator
        tool_name = request.tool.lower()
        orchestrator_name = f"{tool_name.title()}Orchestrator"
        
        # Execute through master orchestrator
        result = cortex.execute(
            operation=tool_name,
            orchestrator=orchestrator_name,
            **request.args
        )
        
        return MCPExecuteResponse(
            success=True,
            result=result,
            execution_time_ms=(time.time() - start_time) * 1000
        )
        
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return MCPExecuteResponse(
            success=False,
            error=str(e),
            execution_time_ms=(time.time() - start_time) * 1000
        )


@app.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus metrics endpoint.
    
    Returns metrics in Prometheus format.
    """
    cortex = get_cortex()
    
    metrics = []
    metrics.append(f'cortex_wired{{}} {1 if is_wired() else 0}')
    metrics.append(f'cortex_orchestrator_count{{}} {len(cortex.registry.get_all_specs())}')
    metrics.append(f'cortex_uptime_seconds{{}} {time.time() - _start_time}')
    
    return "\n".join(metrics)


@app.get("/wiring/hash")
async def wiring_hash():
    """
    Get the current wiring hash.
    
    Useful for verifying all instances have same wiring.
    """
    return {"wiring_hash": get_wiring_hash()}


@app.get("/wiring/order")
async def wiring_order():
    """
    Get the wiring order.
    
    Returns deterministic order orchestrators are wired.
    """
    cortex = get_cortex()
    return {"wiring_order": cortex.registry.get_wiring_order()}
```

---

## 🚀 Deployment Commands

### Development (Your Mac)

```bash
# Build image
docker build -t cortex/mcp-server:dev .

# Run single container
docker run -d \
  --name cortex-mcp-dev \
  -p 8443:8443 \
  -e CORTEX_ENV=development \
  -e CORTEX_LOG_LEVEL=DEBUG \
  cortex/mcp-server:dev

# View logs
docker logs -f cortex-mcp-dev

# Test health
curl http://localhost:8443/health

# Stop
docker stop cortex-mcp-dev && docker rm cortex-mcp-dev
```

### Production (Windows Server)

```powershell
# Pull latest image (or build)
docker pull cortex/mcp-server:latest

# Run with production settings
docker run -d `
  --name cortex-mcp `
  -p 8443:8443 `
  -e CORTEX_ENV=production `
  -e CORTEX_LOG_LEVEL=INFO `
  --restart unless-stopped `
  cortex/mcp-server:latest

# Or use docker-compose for multiple instances
docker-compose -f docker-compose.prod.yml up -d
```

### Scaling (100 → 500 → 1000 users)

```bash
# Scale to 3 containers
docker-compose -f docker-compose.prod.yml up -d --scale cortex-mcp=3

# Scale to 5 containers
docker-compose -f docker-compose.prod.yml up -d --scale cortex-mcp=5

# Check all instances have same wiring hash
for i in 1 2 3; do
  curl -s http://localhost:844$i/wiring/hash
done
# All should return same hash
```

---

## 📊 Resource Requirements

| Scale | Containers | CPU | RAM | Disk |
|-------|------------|-----|-----|------|
| 100 users | 1 | 2 cores | 4 GB | 2 GB |
| 500 users | 3 | 6 cores | 12 GB | 6 GB |
| 1000 users | 5 | 10 cores | 20 GB | 10 GB |

---

## 🔒 Security Considerations

1. **Run as non-root user** (configured in Dockerfile)
2. **Use HTTPS in production** (NGINX with SSL)
3. **Configure CORS properly** (restrict origins)
4. **Use API tokens** (configure in MCP settings)
5. **Network isolation** (Docker network)
6. **Log rotation** (configured in docker-compose)
