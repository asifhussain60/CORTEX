# Technology Stack

---
title: CORTEX Technology Stack - Modern Cloud-Native Architecture
type: reference
audience: [Business Leaders, Product Owners, Software Developers]
word_count: 1850
last_verified: 2026-02-15
source_of_truth: requirements.txt + Dockerfile + deployment/
format: diátaxis-reference
voice: third-person-neutral
phase: Production (v8.1)
diagrams: ASCII layer architecture
---

> **Notice:** Technology choices reflect production deployment requirements as of v8.1. Organizations may substitute equivalent technologies (e.g., PostgreSQL → MySQL, Redis → Memcached) while maintaining interface compatibility. Version requirements represent minimum tested versions.

---

## Executive Summary

CORTEX implements a modern cloud-native technology stack optimized for reliability, performance, and operational simplicity. Organizations benefit from proven open-source technologies reducing vendor lock-in and licensing costs [Business Leaders]. Product teams gain predictable performance characteristics and extensive monitoring capabilities [Product Owners]. The stack implements Python 3.9+ async runtime, Git-backed configuration (zero runtime database), Redis caching, container-first deployment, and comprehensive observability [Software Developers].

**Core Technology Layers:**
- **Application Layer** — Python 3.9+ with FastAPI (async HTTP), Pydantic 2.0 (validation), asyncio (concurrency)
- **Data Layer** — Git registry (configuration), Redis 7.x (caching), SQLite (AST cache), No PostgreSQL in production
- **Infrastructure Layer** — Docker (containerization), Kubernetes (orchestration Phase 11), Nginx (reverse proxy)
- **Observability Layer** — Prometheus (metrics), Grafana (dashboards), OpenTelemetry (tracing), structlog (logging)
- **Development Layer** — pytest (testing), mypy (type checking), ruff (linting), black (formatting)

**Key Design Decisions:**
- **Git-Backed Config** — Eliminates PostgreSQL/MongoDB operational overhead (zero runtime database dependency)
- **Async-First** — Python asyncio + FastAPI for high concurrency (500+ concurrent connections per instance)
- **Container-Native** — Docker-first design enables horizontal scaling and zero-downtime deployments
- **Stateless Processing** — No session affinity required (horizontal scaling via load balancer)
- **Observability-First** — Prometheus metrics + OpenTelemetry tracing built-in (not bolted-on)

**Performance Targets:** Application startup <2s, request latency P50: 5ms (gateway), P95: 15ms, P99: 25ms. Memory footprint: 150MB base + 50MB per 1000 cached patterns. CPU: 0.5 cores steady-state, 2 cores peak.

---

## Overview

CORTEX implements a layered technology architecture where each layer provides specific capabilities while maintaining loose coupling. Organizations deploy CORTEX using standard cloud-native patterns reducing operational complexity [Business Leaders].

```
┌─────────────────────────────────────────────────────────────────┐
│                    TECHNOLOGY STACK                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  APPLICATION LAYER                                         │ │
│  │  Python 3.9+ │ FastAPI │ Pydantic │ asyncio               │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  DATA LAYER                                                │ │
│  │  Redis 7.x │ PostgreSQL 15 │ Git (Registry)               │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  INFRASTRUCTURE LAYER                                      │ │
│  │  Docker │ Kubernetes │ NGINX │ GitHub Actions             │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  OBSERVABILITY LAYER                                       │ │
│  │  Prometheus │ Grafana │ Jaeger │ Structlog                │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Runtime

### Python 3.9+

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.9+ | Runtime |
| FastAPI | 0.100+ | HTTP/WebSocket |
| Pydantic | 2.0+ | Validation |
| uvicorn | 0.22+ | ASGI server |
| asyncio | stdlib | Async I/O |

### Key Libraries

```python
# requirements.txt (core)
fastapi>=0.100.0
pydantic>=2.0.0
uvicorn[standard]>=0.22.0
httpx>=0.24.0
aiohttp>=3.8.0
python-multipart>=0.0.6
orjson>=3.9.0  # Fast JSON
```

### Code Quality

```python
# requirements-dev.txt
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
mypy>=1.4.0
ruff>=0.0.280
black>=23.7.0
isort>=5.12.0
```

---

## Data Storage

### Redis 7.x

| Feature | Configuration |
|---------|---------------|
| Version | 7.0+ |
| Mode | Single / Cluster |
| Persistence | RDB + AOF |
| Max Memory | 2GB (configurable) |
| Eviction | allkeys-lru |

```conf
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
appendonly yes
appendfsync everysec
save 900 1
save 300 10
save 60 10000
```

### PostgreSQL 15

| Feature | Configuration |
|---------|---------------|
| Version | 15.x |
| Purpose | Metrics, Analytics |
| Connection Pool | 20 connections |
| Extensions | pg_stat_statements |

```sql
-- Tables
CREATE TABLE cortex_metrics (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    labels JSONB,
    INDEX idx_timestamp (timestamp),
    INDEX idx_metric_name (metric_name)
);

CREATE TABLE cortex_audit_log (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    action VARCHAR(50) NOT NULL,
    client_id VARCHAR(255),
    details JSONB
);
```

### Git Registry

| Feature | Configuration |
|---------|---------------|
| Backend | Git repository |
| Location | cortex-registry/ |
| Format | YAML files |
| Versioning | Git commits |

```
cortex-registry/
├── manifest.yaml          # Global manifest
├── registry/
│   ├── index.yaml        # Phase index
│   └── phases/           # Phase definitions
├── domains/              # Domain configs
└── master/               # Master orchestrator
```

---

## Infrastructure

### Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY cortex/ ./cortex/
COPY cortex-registry/ ./cortex-registry/

# Run
EXPOSE 8000
CMD ["uvicorn", "cortex.mcp.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes

| Resource | Purpose |
|----------|---------|
| Deployment | MCP servers |
| StatefulSet | Redis, PostgreSQL |
| Service | Internal networking |
| Ingress | External access |
| ConfigMap | Configuration |
| Secret | Credentials |
| HPA | Auto-scaling |

### NGINX

```nginx
# nginx.conf
upstream cortex_mcp {
    least_conn;
    server cortex-mcp-1:8000;
    server cortex-mcp-2:8000;
    server cortex-mcp-3:8000;
}

server {
    listen 443 ssl http2;
    server_name api.cortex.example.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location /mcp {
        proxy_pass http://cortex_mcp;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
    }
    
    location /health {
        proxy_pass http://cortex_mcp;
        proxy_read_timeout 5s;
    }
}
```

---

## Observability

### Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'cortex-mcp'
    static_configs:
      - targets: ['cortex-mcp:8000']
    metrics_path: /metrics
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### Grafana Dashboards

| Dashboard | Purpose |
|-----------|---------|
| CORTEX Overview | System health |
| Request Latency | P50/P95/P99 |
| Error Rate | Failures by type |
| Cache Performance | Hit rate |
| Orchestrator Status | Registration |

### Jaeger Tracing

```python
# Trace configuration
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)
```

### Structured Logging

```python
# Logging configuration
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
```

---

## Development Tools

### IDE Support

| Tool | Purpose |
|------|---------|
| VS Code | Primary IDE |
| Copilot | AI assistance |
| pylance | Python LSP |
| ruff | Linting |

### Testing

```python
# pytest.ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --cov=cortex --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
```

### CI/CD

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt
      - name: Run tests
        run: pytest --cov=cortex
      - name: Type check
        run: mypy cortex/
      - name: Lint
        run: ruff check cortex/
```

---

## Related Documents

- [Infrastructure Overview](overview.md) — Architecture
- [Deployment](deployment.md) — Deployment process
- [Observability](observability.md) — Monitoring

---

*Part of CORTEX Architecture Documentation*
