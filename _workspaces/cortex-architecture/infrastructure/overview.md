# Infrastructure Overview

**Purpose:** The nervous system that keeps the CORTEX brain running  
**Audience:** SRE, DevOps, Architects  
**Last Updated:** 2026-02-10

---

## Overview

**CORTEX Infrastructure: The Nervous System and Life Support**

Just as the human brain requires a sophisticated circulatory system, nervous system, and life support mechanisms to function, CORTEX relies on cloud-native infrastructure to keep its **AI brain** healthy and operational.

**Infrastructure as Brain Life Support:**
- **🩸 Circulatory System** → Load balancers and network routing (delivers requests like blood flow)
- **🫁 Respiratory System** → Container orchestration and scaling (provides computational oxygen)
- **💓 Cardiac System** → Health monitoring and auto-recovery (keeps the brain alive)
- **🧠 Nervous System** → Observability and metrics (brain monitoring and feedback)
- **🦴 Skeletal System** → Persistent storage and databases (structural foundation)

CORTEX is designed as a **cloud-native cognitive platform** with container-first deployment, horizontal scalability, and comprehensive observability—ensuring the AI brain can think clearly under any workload.

**NEW - Phase 71 Learning Infrastructure:**
The learning system adds a distributed pattern capture layer that operates non-blocking at <10ms overhead per operation. YAML-based knowledge storage integrates seamlessly with existing infrastructure, requiring no additional databases or services. Validation pipelines ensure learning integrity across all components.

```
┌─────────────────────────────────────────────────────────────────┐
│              🧠 CORTEX BRAIN LIFE SUPPORT SYSTEM                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                🩸 Circulatory System                    │   │
│  │               Load Balancer (NGINX/ALB)                 │   │
│  │          (Distributes neural traffic like blood flow)   │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         │                    │                    │              │
│         ▼                    ▼                    ▼              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │🧠 Brain Pod │     │🧠 Brain Pod │     │🧠 Brain Pod │       │
│  │ MCP Server 1│     │ MCP Server 2│     │ MCP Server N│       │
│  │(Neural Net) │     │(Neural Net) │     │(Neural Net) │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│         │                    │                    │              │
│         └────────────────────┼────────────────────┘             │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                🦴 Structural Foundation                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │💾 Memory │  │📊 Metrics│  │📚 Neural │              │   │
│  │  │  Cache   │  │Database  │  │Registry  │              │   │
│  │  │ (Redis)  │  │(PostgreSQL)│ │  (Git)  │              │   │
│  │  └──────────┘  └──────────┘  └──────────┘              │   │
│  └─────────────────────────────────────────────────────────┘   ││                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                💓 Monitoring & Health                    │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │Prometheus│  │ Grafana  │  │   ELK    │              │   │
│  │  │ Metrics  │  │Dashboards│  │ Logging  │              │   │
│  │  └──────────┘  └──────────┘  └──────────┘              │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### D3.js Infrastructure Health Dashboard

```json
{
  "type": "infrastructure_dashboard",
  "title": "CORTEX Brain Health Monitor",
  "real_time": true,
  "refresh_interval": "5s",
  "sections": [
    {
      "name": "🧠 Brain Pod Health",
      "type": "node_status_grid",
      "data": [
        {"pod": "cortex-brain-1", "status": "healthy", "cpu": 45, "memory": 62, "rps": 180},
        {"pod": "cortex-brain-2", "status": "healthy", "cpu": 52, "memory": 58, "rps": 165},
        {"pod": "cortex-brain-3", "status": "healthy", "cpu": 38, "memory": 71, "rps": 195},
        {"pod": "cortex-brain-4", "status": "warning", "cpu": 78, "memory": 85, "rps": 95},
        {"pod": "cortex-brain-5", "status": "healthy", "cpu": 41, "memory": 55, "rps": 175}
      ]
    },
    {
      "name": "🩸 Neural Traffic Flow",
      "type": "real_time_line_chart",
      "metrics": [
        {"name": "Requests/Second", "current": 845, "trend": "+12%", "color": "#4CAF50"},
        {"name": "Response Time (p95)", "current": "342ms", "trend": "-8%", "color": "#2196F3"},
        {"name": "Error Rate", "current": "0.23%", "trend": "-45%", "color": "#FF5722"},
        {"name": "Queue Depth", "current": 12, "trend": "-15%", "color": "#FF9800"}
      ]
    },
    {
      "name": "🫁 Resource Utilization",
      "type": "gauge_cluster", 
      "gauges": [
        {"metric": "CPU", "value": 52, "threshold": 80, "color": "#4CAF50"},
        {"metric": "Memory", "value": 68, "threshold": 85, "color": "#FF9800"},
        {"metric": "Network", "value": 34, "threshold": 90, "color": "#4CAF50"},
        {"metric": "Storage", "value": 23, "threshold": 75, "color": "#4CAF50"}
      ]
    },
    {
      "name": "💓 Orchestrator Heartbeats",
      "type": "status_timeline",
      "orchestrators": [
        {"name": "MasterOrchestrator", "status": "active", "last_heartbeat": "2s ago"},
        {"name": "IntentRouter", "status": "active", "last_heartbeat": "1s ago"},
        {"name": "TDDOrchestrator", "status": "active", "last_heartbeat": "3s ago"},
        {"name": "LENS", "status": "active", "last_heartbeat": "1s ago"},
        {"name": "RefactoringOrchestrator", "status": "idle", "last_heartbeat": "45s ago"},
        {"name": "PlanningOrchestrator", "status": "active", "last_heartbeat": "12s ago"}
      ]
    }
  ]
}
```

### D3.js Scalability Architecture

```json
{
  "type": "scalability_diagram",
  "title": "CORTEX Brain Scaling Architecture",
  "components": [
    {
      "layer": "Load Balancing",
      "components": [
        {
          "name": "NGINX/ALB",
          "type": "load_balancer",
          "position": {"x": 400, "y": 50},
          "scaling": "Auto-scaling based on connection count",
          "capacity": "10,000 concurrent connections"
        }
      ]
    },
    {
      "layer": "Application Tier",
      "components": [
        {
          "name": "MCP Server Pods", 
          "type": "horizontal_pod_autoscaler",
          "position": {"x": 200, "y": 200},
          "current_replicas": 5,
          "min_replicas": 2,
          "max_replicas": 20,
          "scaling_metrics": ["CPU > 70%", "Memory > 80%", "Queue Depth > 50"]
        },
        {
          "name": "Orchestrator Workers",
          "type": "job_queue_scaler", 
          "position": {"x": 400, "y": 200},
          "current_workers": 12,
          "scaling_trigger": "Queue wait time > 100ms"
        },
        {
          "name": "LENS Analyzers",
          "type": "vertical_pod_autoscaler",
          "position": {"x": 600, "y": 200}, 
          "resource_optimization": "Memory-optimized for large codebases"
        }
      ]
    },
    {
      "layer": "Data Tier", 
      "components": [
        {
          "name": "Redis Cluster",
          "type": "cache_cluster",
          "position": {"x": 200, "y": 350},
          "sharding": "Automatic",
          "replication": "Master-Slave",
          "capacity": "100GB memory"
        },
        {
          "name": "PostgreSQL",
          "type": "database_cluster", 
          "position": {"x": 400, "y": 350},
          "read_replicas": 3,
          "connection_pooling": "PgBouncer",
          "backup_strategy": "Point-in-time recovery"
        }
      ]
    }
  ],
  "scaling_policies": [
    {"trigger": "CPU > 70% for 2 min", "action": "Scale out MCP pods +2"},
    {"trigger": "Memory > 85% for 1 min", "action": "Scale up pod resources"},
    {"trigger": "Queue depth > 100 for 30s", "action": "Add orchestrator workers +5"},
    {"trigger": "Error rate > 1% for 5 min", "action": "Circuit breaker activation"}
  ]
}
```

### System Topology Map

```json
{
  "type": "network_topology",
  "title": "CORTEX Brain Network Topology",
  "nodes": [
    {
      "id": "internet",
      "label": "🌍 Internet",
      "type": "external",
      "position": {"x": 400, "y": 0}
    },
    {
      "id": "cdn",
      "label": "📡 CDN",
      "type": "edge",
      "position": {"x": 400, "y": 100},
      "specs": "Global edge locations"
    },
    {
      "id": "lb",
      "label": "⚖️ Load Balancer", 
      "type": "infrastructure",
      "position": {"x": 400, "y": 200},
      "specs": "NGINX/ALB - 99.99% uptime"
    },
    {
      "id": "mcp_cluster",
      "label": "🧠 MCP Brain Cluster",
      "type": "application",
      "position": {"x": 400, "y": 300},
      "specs": "2-20 pods, auto-scaling"
    },
    {
      "id": "redis",
      "label": "💾 Redis Cache",
      "type": "cache",
      "position": {"x": 200, "y": 400},
      "specs": "100GB, 6 shards"
    },
    {
      "id": "postgres",
      "label": "🗄️ PostgreSQL",
      "type": "database", 
      "position": {"x": 600, "y": 400},
      "specs": "Primary + 3 read replicas"
    },
    {
      "id": "monitoring",
      "label": "📊 Monitoring Stack",
      "type": "observability",
      "position": {"x": 400, "y": 500},
      "specs": "Prometheus, Grafana, ELK"
    }
  ],
  "connections": [
    {"from": "internet", "to": "cdn", "type": "https", "bandwidth": "10 Gbps"},
    {"from": "cdn", "to": "lb", "type": "https", "bandwidth": "10 Gbps"},
    {"from": "lb", "to": "mcp_cluster", "type": "http", "bandwidth": "1 Gbps"},
    {"from": "mcp_cluster", "to": "redis", "type": "tcp", "bandwidth": "100 Mbps"},
    {"from": "mcp_cluster", "to": "postgres", "type": "tcp", "bandwidth": "100 Mbps"},
    {"from": "mcp_cluster", "to": "monitoring", "type": "metrics", "bandwidth": "10 Mbps"}
  ]
}
```│                                                                  │
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
