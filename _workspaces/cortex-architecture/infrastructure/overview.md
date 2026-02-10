# Infrastructure Overview

**Purpose:** Introduction to CORTEX infrastructure  
**Audience:** SRE, DevOps, Architects  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Core Components](#core-components)
- [Deployment Environments](#deployment-environments)
- [Health and Monitoring](#health-and-monitoring)
- [Related Documents](#related-documents)

---

## Overview

CORTEX is designed as a cloud-native platform with container-first deployment, horizontal scalability, and comprehensive observability.

```
┌─────────────────────────────────────────────────────────────────┐
│                CORTEX INFRASTRUCTURE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Load Balancer                         │   │
│  │                    (NGINX/ALB)                           │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         │                    │                    │              │
│         ▼                    ▼                    ▼              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │ MCP Server  │     │ MCP Server  │     │ MCP Server  │       │
│  │  Pod 1      │     │  Pod 2      │     │  Pod N      │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│         │                    │                    │              │
│         └────────────────────┼────────────────────┘             │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Data Layer                             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │  Redis   │  │ PostgreSQL│  │ Registry │              │   │
│  │  │  Cache   │  │  Metrics │  │  (Git)   │              │   │
│  │  └──────────┘  └──────────┘  └──────────┘              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 Observability                            │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │Prometheus│  │  Grafana │  │  Jaeger  │              │   │
│  │  │ Metrics  │  │ Dashboards│  │ Tracing │              │   │
│  │  └──────────┘  └──────────┘  └──────────┘              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Architecture

### Container-First Design

CORTEX runs in containers using a microservices architecture:

| Container | Purpose | Scale |
|-----------|---------|-------|
| `cortex-mcp` | MCP server | Horizontal (2-N pods) |
| `cortex-worker` | Background jobs | Horizontal (1-N pods) |
| `cortex-cache` | Redis cache | Single/Cluster |
| `cortex-registry` | Git-backed config | Single (stateful) |

### Network Topology

```
┌─────────────────────────────────────────────────────────────────┐
│  External Network                                                │
│                                                                  │
│  ┌──────────┐                                                   │
│  │ Clients  │───────┐                                           │
│  └──────────┘       │                                           │
│                     ▼                                           │
├─────────────────────────────────────────────────────────────────┤
│  DMZ (Port 443)                                                  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Load Balancer (NGINX)                       │   │
│  │              TLS Termination                             │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │                                   │
├─────────────────────────────────────────────────────────────────┤
│  Application Network                                             │
│                                                                  │
│  ┌─────────────┐     ┌─────────────┐                           │
│  │ MCP Servers │     │  Workers    │                           │
│  │ Port 8000   │◄───►│  Internal   │                           │
│  └─────────────┘     └─────────────┘                           │
│         │                                                        │
├─────────────────────────────────────────────────────────────────┤
│  Data Network                                                    │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │  Redis   │  │ PostgreSQL│  │  Git     │                      │
│  │  6379    │  │   5432   │  │  SSH     │                      │
│  └──────────┘  └──────────┘  └──────────┘                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### MCP Server

The primary service handling all client requests:

```yaml
# Kubernetes Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cortex-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cortex-mcp
  template:
    spec:
      containers:
        - name: mcp
          image: cortex/mcp-server:latest
          ports:
            - containerPort: 8000
          env:
            - name: REDIS_URL
              value: "redis://cortex-cache:6379"
            - name: LOG_LEVEL
              value: "INFO"
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "2000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
```

### Redis Cache

Caching layer for LENS results and session state:

```yaml
# Redis Configuration
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: cortex-cache
spec:
  replicas: 1
  serviceName: cortex-cache
  template:
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          command: ["redis-server", "/etc/redis/redis.conf"]
          ports:
            - containerPort: 6379
          volumeMounts:
            - name: redis-config
              mountPath: /etc/redis
            - name: redis-data
              mountPath: /data
```

### Git Registry

Persistent storage for orchestrator configurations:

```yaml
# Git Registry Volume
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cortex-registry-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

---

## Deployment Environments

### Development

```
┌───────────────────────────────────────┐
│  Local Development                     │
│                                        │
│  ┌────────────────────────────────┐   │
│  │  docker-compose up              │   │
│  │                                 │   │
│  │  • cortex-mcp:8000             │   │
│  │  • cortex-redis:6379           │   │
│  │  • prometheus:9090             │   │
│  │  • grafana:3000                │   │
│  └────────────────────────────────┘   │
│                                        │
│  Config: development.env              │
│  Registry: Local git                  │
└───────────────────────────────────────┘
```

### Staging

```
┌───────────────────────────────────────┐
│  Staging Environment                   │
│                                        │
│  ┌────────────────────────────────┐   │
│  │  Kubernetes Cluster             │   │
│  │                                 │   │
│  │  • 2x MCP pods                 │   │
│  │  • 1x Redis (non-HA)           │   │
│  │  • Prometheus + Grafana        │   │
│  └────────────────────────────────┘   │
│                                        │
│  Config: staging.env                  │
│  Registry: Git (main branch)          │
└───────────────────────────────────────┘
```

### Production

```
┌───────────────────────────────────────┐
│  Production Environment                │
│                                        │
│  ┌────────────────────────────────┐   │
│  │  Kubernetes Cluster (HA)        │   │
│  │                                 │   │
│  │  • 3-5x MCP pods (auto-scale)  │   │
│  │  • Redis Cluster (3 nodes)     │   │
│  │  • PostgreSQL (metrics)        │   │
│  │  • Full observability stack    │   │
│  └────────────────────────────────┘   │
│                                        │
│  Config: production.env               │
│  Registry: Git (release tags)         │
└───────────────────────────────────────┘
```

---

## Health and Monitoring

### Health Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/health` | Basic liveness |
| `/health/ready` | Readiness check |
| `/health/wiring` | Orchestrator status |
| `/health/dependencies` | External dependencies |

### Key Metrics

```
# Latency
cortex_request_duration_seconds

# Throughput
cortex_requests_total

# Error Rate
cortex_errors_total

# Cache Performance
cortex_cache_hits_total
cortex_cache_misses_total

# Orchestrator Status
cortex_orchestrators_registered
```

---

## Related Documents

- [Tech Stack](tech-stack.md) — Technologies used
- [Deployment](deployment.md) — Deployment process
- [Scalability](scalability.md) — Scaling strategies
- [Observability](observability.md) — Monitoring

---

*Part of CORTEX Architecture Documentation*
