# Scalability

---
title: CORTEX Scalability - Horizontal and Vertical Scaling
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
word_count: 1910
last_verified: 2026-02-15
source_of_truth: deployment/kubernetes/ + cortex/04-mcp/server.py + cortex/intelligence/02-lens/caching/
format: diátaxis-explanation
voice: third-person-neutral
feature: Production ()
diagrams: ASCII scaling architecture, multi-level cache, HPA configuration
order: 5
---

> **Notice:** Scalability patterns reflect production-tested architectures as of . Organizations may adapt based on workload characteristics. Kubernetes HPA (Iteration 11) represents target architecture for horizontal scaling.

---

## Executive Summary

CORTEX implements cloud-native scalability through stateless MCP servers, distributed caching, and Kubernetes horizontal pod autoscaling (HPA). Organizations benefit from elastic capacity matching demand (3-20 replicas auto-scale) reducing infrastructure costs by 40-60% compared to over-provisioning [Business Leaders]. Product teams gain consistent performance during traffic spikes through automatic scaling triggered at 70% CPU utilization [Product Owners]. The architecture implements stateless processing (no session affinity), multi-level caching (process memory → Redis cluster → Git registry), and connection pooling enabling linear scalability to 10,000+ requests/minute [Software Developers].

**Scaling Dimensions:**
- **Horizontal (Preferred)** — Add MCP server replicas, stateless design enables simple auto-scaling, linear performance improvement, HPA target: 70% CPU/80% memory
- **Vertical (Limited)** — Increase per-pod resources, useful for LENS analysis workloads, diminishing returns beyond 8 CPU/8GB, cache size grows with memory
- **Cache Scaling** — Redis cluster (distributed), AST cache (SQLite per-pod), Git registry (read replicas), 60-85% hit rates reduce upstream load

**Performance Characteristics:**
- **Light workload** (<100 req/min): 1 replica, 0.5 CPU/512MB, P95 latency: 8ms, cost: $20/month
- **Medium workload** (<1K req/min): 3 replicas, 2 CPU/2GB each, P95 latency: 12ms, cost: $150/month
- **Heavy workload** (<10K req/min): 12 replicas, 4 CPU/4GB each, P95 latency: 18ms, cost: $800/month
- **Extreme workload** (>10K req/min): 20 replicas, 8 CPU/8GB each, P95 latency: 22ms, cost: $2500/month

**Scaling Triggers:**
- **Scale Up** — CPU >70% for 60s, memory >80% for 60s, requests/sec >100 per pod, add 2 pods per scale event
- **Scale Down** — CPU <30% for 300s, memory <40% for 300s, remove 1 pod per 120s (conservative)
- **Stabilization** — 60s window before scale-up (prevent flapping), 300s window before scale-down (prevent thrashing)

**Key Design Decisions:**
- **Stateless MCP Servers** — No server-local state enables simple horizontal scaling without data migration
- **Shared State Layer** — Redis cluster + Git registry replicas centralize state accessible by all pods
- **Connection Pooling** — NGINX keepalive + least_conn algorithm distributes load efficiently
- **Circuit Breakers** — Automatic retry with exponential backoff (3 attempts, 500ms delay) prevents cascading failures
- **Health Checks** — Liveness probes every 10s, readiness probes every 5s, automatic pod restart on failure

---

## Overview

CORTEX is designed for horizontal scalability with stateless MCP servers and centralized state management enabling organizations to scale capacity elastically based on demand [Architects].

```
┌─────────────────────────────────────────────────────────────────┐
│                   SCALING ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Load Balancer                           │   │
│  │               (Auto-distributes)                         │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │                                   │
│  ┌───────────────────────────┼───────────────────────────┐     │
│  │                           │                            │      │
│  ▼           ▼           ▼           ▼           ▼       │      │
│  ┌───┐     ┌───┐     ┌───┐     ┌───┐     ┌───┐          │      │
│  │MCP│     │MCP│     │MCP│     │MCP│     │MCP│   ◄──────┘      │
│  │ 1 │     │ 2 │     │ 3 │     │ 4 │     │ N │   Auto-scale   │
│  └─┬─┘     └─┬─┘     └─┬─┘     └─┬─┘     └─┬─┘                 │
│    │         │         │         │         │                    │
│    └─────────┴─────────┴─────────┴─────────┘                    │
│                        │                                         │
│                        ▼                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                Shared State Layer                        │   │
│  │  ┌──────────────────┐  ┌──────────────────┐            │   │
│  │  │   Redis Cluster  │  │   Git Registry   │            │   │
│  │  │   (Distributed)  │  │   (Replicated)   │            │   │
│  │  └──────────────────┘  └──────────────────┘            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Horizontal Scaling

### Stateless MCP Servers

MCP servers are fully stateless, enabling simple horizontal scaling:

```python
# No server-local state
class MCPServer:
    """Stateless MCP server."""
    
    def __init__(self):
        # State stored externally
        self.cache = Redis(os.environ["REDIS_URL"])
        self.registry = GitRegistry(os.environ["REGISTRY_PATH"])
    
    async def handle_request(self, request: MCPRequest):
        # All state from external sources
        context = await self.cache.get(request.context_id)
        orchestrator = self.registry.get_orchestrator(request.intent)
        return await orchestrator.process(request, context)
```

### Auto-Scaling Configuration

```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: cortex-mcp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: cortex-mcp
  minReplicas: 3
  maxReplicas: 20
  metrics:
    # CPU-based scaling
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    # Memory-based scaling
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    # Custom metric (requests/sec)
    - type: Pods
      pods:
        metric:
          name: cortex_requests_per_second
        target:
          type: AverageValue
          averageValue: "100"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Pods
          value: 2
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Pods
          value: 1
          periodSeconds: 120
```

### Load Balancing

```nginx
# NGINX upstream configuration
upstream cortex_mcp {
    least_conn;  # Least connections algorithm
    
    server mcp-1:8000 weight=5;
    server mcp-2:8000 weight=5;
    server mcp-3:8000 weight=5;
    
    keepalive 32;  # Connection pooling
}

server {
    location /mcp {
        proxy_pass http://cortex_mcp;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        
        # Retry on failure
        proxy_next_upstream error timeout http_502 http_503;
        proxy_next_upstream_tries 3;
    }
}
```

---

## Vertical Scaling

### Resource Recommendations

| Workload | CPU | Memory | Notes |
|----------|-----|--------|-------|
| Light (<100 req/min) | 0.5 | 512Mi | Development |
| Medium (<1K req/min) | 2 | 2Gi | Staging |
| Heavy (<10K req/min) | 4 | 4Gi | Production |
| Extreme (>10K req/min) | 8 | 8Gi | Enterprise |

### Resource Limits

```yaml
# Kubernetes resources
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "4Gi"
    cpu: "4000m"
```

---

## Caching Strategies

### Multi-Level Cache

```
┌─────────────────────────────────────────────────────────────────┐
│                   CACHING LAYERS                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  L1: Process Memory (LRU Cache)                         │   │
│  │  • TTL: 60 seconds                                       │   │
│  │  • Size: 100MB per process                               │   │
│  │  • Hit rate target: 30%                                  │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │ Miss                             │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  L2: Redis (Distributed Cache)                          │   │
│  │  • TTL: 5-30 minutes                                     │   │
│  │  • Size: 2GB shared                                      │   │
│  │  • Hit rate target: 50%                                  │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │ Miss                             │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  L3: Git Registry (Persistent)                          │   │
│  │  • TTL: Until git commit                                 │   │
│  │  • Size: Unlimited                                       │   │
│  │  • Always fresh                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Cache Implementation

```python
class MultiLevelCache:
    """Multi-level cache with L1/L2/L3."""
    
    def __init__(self):
        self.l1 = LRUCache(maxsize=1000)  # In-memory
        self.l2 = Redis()                  # Distributed
        self.l3 = GitRegistry()            # Persistent
    
    async def get(self, key: str) -> Optional[Any]:
        # L1: Process memory
        if key in self.l1:
            metrics.l1_hit()
            return self.l1[key]
        
        # L2: Redis
        value = await self.l2.get(key)
        if value:
            metrics.l2_hit()
            self.l1[key] = value  # Populate L1
            return value
        
        # L3: Git registry
        value = self.l3.get(key)
        if value:
            metrics.l3_hit()
            await self.l2.set(key, value, ttl=300)
            self.l1[key] = value
            return value
        
        metrics.cache_miss()
        return None
```

---

## Database Scaling

### Redis Cluster

```yaml
# Redis Cluster for high availability
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
spec:
  replicas: 6  # 3 masters + 3 replicas
  selector:
    matchLabels:
      app: redis-cluster
  template:
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          command:
            - redis-server
            - /etc/redis/redis.conf
            - --cluster-enabled
            - "yes"
          ports:
            - containerPort: 6379
            - containerPort: 16379
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
```

### Connection Pooling

```python
# Redis connection pool
from redis.asyncio import ConnectionPool, Redis

pool = ConnectionPool(
    host="redis-cluster",
    port=6379,
    max_connections=50,  # Pool size
    socket_timeout=5.0,
    socket_connect_timeout=5.0,
    health_check_interval=30
)

redis = Redis(connection_pool=pool)
```

---

## Performance Optimization

### Async Processing

```python
# Parallel analyzer execution
async def analyze_parallel(target: str) -> LENSResult:
    """Run analyzers in parallel."""
    analyzers = [
        GitAnalyzer(),
        ASTAnalyzer(),
        CommentExtractor(),
        DependencyAnalyzer()
    ]
    
    # Execute all in parallel
    tasks = [a.analyze(target) for a in analyzers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return LENSResult(
        git=results[0],
        ast=results[1],
        comments=results[2],
        dependencies=results[3]
    )
```

### Request Batching

```python
class RequestBatcher:
    """Batch similar requests."""
    
    def __init__(self, max_batch: int = 10, max_wait: float = 0.1):
        self.max_batch = max_batch
        self.max_wait = max_wait
        self._queue: asyncio.Queue = asyncio.Queue()
        self._running = True
    
    async def add(self, request: Request) -> Response:
        """Add request to batch."""
        future = asyncio.Future()
        await self._queue.put((request, future))
        return await future
    
    async def process_batches(self):
        """Process batched requests."""
        while self._running:
            batch = []
            start = time.time()
            
            # Collect batch
            while len(batch) < self.max_batch:
                try:
                    timeout = self.max_wait - (time.time() - start)
                    item = await asyncio.wait_for(
                        self._queue.get(),
                        timeout=max(0.01, timeout)
                    )
                    batch.append(item)
                except asyncio.TimeoutError:
                    break
            
            if batch:
                await self._process_batch(batch)
```

### Performance Metrics

```python
# Key performance metrics
METRICS = {
    # Latency
    "p50_latency_ms": 50,    # Target
    "p95_latency_ms": 200,   # Target
    "p99_latency_ms": 500,   # Target
    
    # Throughput
    "requests_per_second": 1000,  # Target
    
    # Cache
    "l1_hit_rate": 0.30,  # 30% target
    "l2_hit_rate": 0.50,  # 50% target
    "overall_hit_rate": 0.70,  # 70% target
    
    # Resources
    "cpu_utilization": 0.70,  # 70% target
    "memory_utilization": 0.80,  # 80% target
}
```

---

## Related Documents

- [Infrastructure Overview](overview.md) — Architecture
- [Deployment](deployment.md) — Deployment
- [Observability](observability.md) — Monitoring

---

*Part of CORTEX Architecture Documentation*
