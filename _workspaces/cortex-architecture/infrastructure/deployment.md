# Deployment Guide

**Purpose:** CORTEX deployment procedures  
**Audience:** DevOps, SRE  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Configuration Management](#configuration-management)
- [Rollback Procedures](#rollback-procedures)
- [Related Documents](#related-documents)

---

## Overview

CORTEX supports multiple deployment modes:

| Mode | Use Case | Complexity |
|------|----------|------------|
| Local | Development | Low |
| Docker Compose | Testing | Medium |
| Kubernetes | Production | High |

```
┌─────────────────────────────────────────────────────────────────┐
│                   DEPLOYMENT PIPELINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│  │   Code   │───▶│   Test   │───▶│  Build   │───▶│  Deploy  │ │
│  │  Commit  │    │   Suite  │    │  Image   │    │   K8s    │ │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│                                                                  │
│       │              │              │              │            │
│       ▼              ▼              ▼              ▼            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Lint +   │  │ Unit +   │  │  Docker  │  │ Rolling  │       │
│  │ Type     │  │ Integ    │  │  Push    │  │ Update   │       │
│  │ Check    │  │ Tests    │  │  to ECR  │  │          │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Software Requirements

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.9+ | Runtime |
| Docker | 20.10+ | Containers |
| kubectl | 1.25+ | K8s CLI |
| helm | 3.10+ | K8s packages |
| make | 4.0+ | Build automation |

### Environment Variables

```bash
# Required
export CORTEX_ENV=development|staging|production
export CORTEX_LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
export REDIS_URL=redis://localhost:6379

# Optional
export CORTEX_PORT=8000
export CORTEX_WORKERS=4
export PROMETHEUS_ENABLED=true
```

---

## Local Development

### Quick Start

```bash
# Clone repository
git clone https://github.com/your-org/cortex.git
cd cortex

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run MCP server
python -m cortex.mcp.server
```

### Development Server

```bash
# With auto-reload
uvicorn cortex.mcp.server:app --reload --port 8000

# With debug logging
CORTEX_LOG_LEVEL=DEBUG uvicorn cortex.mcp.server:app --reload
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=cortex

# Specific test file
pytest tests/test_mcp_server.py -v

# Integration tests only
pytest -m integration
```

---

## Docker Deployment

### Building Image

```bash
# Build image
docker build -t cortex/mcp-server:latest .

# Build with specific tag
docker build -t cortex/mcp-server:v1.0.0 .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 \
  -t cortex/mcp-server:latest .
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  mcp:
    image: cortex/mcp-server:latest
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - CORTEX_ENV=development
      - REDIS_URL=redis://redis:6379
      - CORTEX_LOG_LEVEL=INFO
    depends_on:
      - redis
    volumes:
      - ./cortex-registry:/app/cortex-registry
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes

  prometheus:
    image: prom/prometheus:v2.45.0
    ports:
      - "9090:9090"
    volumes:
      - ./deployment/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:10.0.0
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
      - ./deployment/grafana-dashboards:/etc/grafana/provisioning/dashboards

volumes:
  redis-data:
  grafana-data:
```

### Running with Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f mcp

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

---

## Kubernetes Deployment

### Namespace Setup

```bash
# Create namespace
kubectl create namespace cortex

# Set default namespace
kubectl config set-context --current --namespace=cortex
```

### Helm Deployment

```bash
# Add Helm repo (if using external charts)
helm repo add cortex https://charts.cortex.example.com

# Install
helm install cortex ./helm/cortex \
  --namespace cortex \
  --values ./helm/values-production.yaml

# Upgrade
helm upgrade cortex ./helm/cortex \
  --namespace cortex \
  --values ./helm/values-production.yaml
```

### Kubernetes Manifests

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cortex-mcp
  namespace: cortex
  labels:
    app: cortex-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cortex-mcp
  template:
    metadata:
      labels:
        app: cortex-mcp
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
        - name: mcp
          image: cortex/mcp-server:v1.0.0
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: cortex-config
            - secretRef:
                name: cortex-secrets
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
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          volumeMounts:
            - name: registry
              mountPath: /app/cortex-registry
      volumes:
        - name: registry
          persistentVolumeClaim:
            claimName: cortex-registry-pvc
---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: cortex-mcp
  namespace: cortex
spec:
  selector:
    app: cortex-mcp
  ports:
    - port: 8000
      targetPort: 8000
  type: ClusterIP
---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cortex-ingress
  namespace: cortex
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.cortex.example.com
      secretName: cortex-tls
  rules:
    - host: api.cortex.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: cortex-mcp
                port:
                  number: 8000
```

### Auto-Scaling

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: cortex-mcp-hpa
  namespace: cortex
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: cortex-mcp
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

---

## Configuration Management

### ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cortex-config
  namespace: cortex
data:
  CORTEX_ENV: "production"
  CORTEX_LOG_LEVEL: "INFO"
  CORTEX_PORT: "8000"
  REDIS_URL: "redis://cortex-redis:6379"
  PROMETHEUS_ENABLED: "true"
```

### Secrets

```yaml
# secrets.yaml (encrypted in production)
apiVersion: v1
kind: Secret
metadata:
  name: cortex-secrets
  namespace: cortex
type: Opaque
data:
  API_KEY: <base64-encoded>
  DATABASE_URL: <base64-encoded>
```

---

## Rollback Procedures

### Kubernetes Rollback

```bash
# View rollout history
kubectl rollout history deployment/cortex-mcp -n cortex

# Rollback to previous version
kubectl rollout undo deployment/cortex-mcp -n cortex

# Rollback to specific revision
kubectl rollout undo deployment/cortex-mcp -n cortex --to-revision=3

# Check rollout status
kubectl rollout status deployment/cortex-mcp -n cortex
```

### Helm Rollback

```bash
# View release history
helm history cortex -n cortex

# Rollback to previous release
helm rollback cortex -n cortex

# Rollback to specific revision
helm rollback cortex 3 -n cortex
```

---

## Related Documents

- [Infrastructure Overview](overview.md) — Architecture
- [Tech Stack](tech-stack.md) — Technologies
- [Scalability](scalability.md) — Scaling
- [CI/CD](ci-cd.md) — Automation

---

*Part of CORTEX Architecture Documentation*
