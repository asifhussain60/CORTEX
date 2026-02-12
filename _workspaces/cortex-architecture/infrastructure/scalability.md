# Scalability

**Purpose:** CORTEX scaling strategies and patterns  
**Audience:** Architects, SRE  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Horizontal Scaling](#horizontal-scaling)
- [Vertical Scaling](#vertical-scaling)
- [Caching Strategies](#caching-strategies)
- [Database Scaling](#database-scaling)
- [Performance Optimization](#performance-optimization)
- [Related Documents](#related-documents)

---

## Overview

CORTEX is designed for horizontal scalability with stateless MCP servers and centralized state management.

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
        CommentAnalyzer(),
        PatternAnalyzer()
    ]
    
    # Execute all in parallel
    tasks = [a.analyze(target) for a in analyzers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return LENSResult(
        git=results[0],
        ast=results[1],
        comments=results[2],
        patterns=results[3]
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
