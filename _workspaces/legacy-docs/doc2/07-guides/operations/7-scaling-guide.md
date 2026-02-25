# Scaling Guide

> Auto-generated from cortex-impl-map.yaml on 2026-01-21

**Last Updated:** 2026-01-21  
**Audience:** Operations, SRE, Architects

## Overview

This guide covers horizontal and vertical scaling strategies for CORTEX, including capacity planning, scaling triggers, and performance optimization.

## Architecture Scaling Points

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CORTEX Scaling Architecture                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐               │
│   │ Load Balancer│────▶│ MCP Server   │────▶│ Orchestrators│               │
│   │ (Horizontal) │     │ (Horizontal) │     │ (Stateless)  │               │
│   └──────────────┘     └──────────────┘     └──────────────┘               │
│                               │                    │                        │
│                               ▼                    ▼                        │
│                        ┌──────────────┐     ┌──────────────┐               │
│                        │ Rule Cache   │     │ Knowledge    │               │
│                        │ (Redis)      │     │ Cache        │               │
│                        └──────────────┘     └──────────────┘               │
│                               │                                             │
│                               ▼                                             │
│                        ┌──────────────┐                                    │
│                        │ Governance DB│                                    │
│                        │ (SQLite→PG)  │                                    │
│                        └──────────────┘                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Scaling Dimensions

### Horizontal Scaling (Scale Out)

| Component | Scalable | Strategy |
|-----------|----------|----------|
| MCP Server | ✅ Yes | Add instances behind load balancer |
| Orchestrators | ✅ Yes | Stateless, any instance can handle |
| Rule Cache | ✅ Yes | Redis Cluster |
| Governance DB | ⚠️ Limited | Read replicas only |

### Vertical Scaling (Scale Up)

| Component | Recommended Max | Notes |
|-----------|-----------------|-------|
| MCP Server | 4 CPU, 8GB RAM | Beyond this, scale horizontally |
| Governance DB | 8 CPU, 32GB RAM | Consider PostgreSQL at scale |
| Rule Cache | 2 CPU, 4GB RAM | Redis memory-bound |

## Scaling Triggers

### Auto-Scale Policies

| Metric | Scale Up | Scale Down |
|--------|----------|------------|
| CPU | > 70% for 5 min | < 30% for 15 min |
| Memory | > 80% for 5 min | < 40% for 15 min |
| Request Latency | p95 > 2s | p95 < 500ms |
| Queue Depth | > 100 pending | < 10 pending |

### Manual Scaling Checklist

- [ ] Current metrics reviewed
- [ ] Capacity plan updated
- [ ] Load test results analyzed
- [ ] Rollback plan prepared
- [ ] Team notified

## Capacity Planning

### Baseline Metrics

| Metric | Single Instance | Target (10x) |
|--------|-----------------|--------------|
| Requests/sec | 50 | 500 |
| Concurrent users | 20 | 200 |
| Latency (p50) | 100ms | 100ms |
| Latency (p99) | 500ms | 1s |

### Sizing Formula

```
Instances = ceil(
    (Target RPS × Safety Factor) / 
    (Single Instance RPS × Efficiency)
)

Example:
Instances = ceil((500 × 1.5) / (50 × 0.8)) = ceil(18.75) = 19 instances
```

## Scaling Procedures

### Scale MCP Servers

```powershell
# Using container orchestrator (example: Kubernetes)
kubectl scale deployment cortex-mcp --replicas=5

# Verify scaling
kubectl get pods -l app=cortex-mcp
```

### Add Read Replicas (Database)

```powershell
# For production, use PostgreSQL with read replicas
# 1. Create read replica
# 2. Configure connection pooling
# 3. Update application config

# cortex-config.yaml
database:
  primary: postgresql://primary:5432/cortex
  replicas:
    - postgresql://replica1:5432/cortex
    - postgresql://replica2:5432/cortex
  read_strategy: round_robin
```

### Configure Redis Cluster

```yaml
# redis-cluster.yaml
cache:
  type: redis_cluster
  nodes:
    - redis://node1:6379
    - redis://node2:6379
    - redis://node3:6379
  max_connections: 100
  timeout: 5s
```

## Performance Optimization

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_rules_tier ON governance_rules(tier);
CREATE INDEX idx_rules_enforcement ON governance_rules(enforcement);

-- Analyze tables after bulk operations
ANALYZE governance_rules;
```

### Caching Strategy

| Data Type | Cache TTL | Strategy |
|-----------|-----------|----------|
| Tier 0 Rules | 1 hour | Cache-aside |
| Tier 1/2 Rules | 15 min | Cache-aside |
| Query Results | 5 min | TTL-based |
| User Sessions | 30 min | Session store |

### Connection Pooling

```python
# Database connection pool
from cortex.infrastructure.connection_pool import ConnectionPool

pool = ConnectionPool(
    min_connections=5,
    max_connections=20,
    timeout=30,
    recycle=3600
)
```

## Load Testing

### Test Scenarios

| Scenario | Users | Duration | Target |
|----------|-------|----------|--------|
| Baseline | 10 | 5 min | Establish baseline |
| Normal Load | 50 | 15 min | Verify stability |
| Peak Load | 200 | 30 min | Stress test |
| Spike Test | 500 | 5 min | Burst handling |

### Running Load Tests

```powershell
# Using locust (Python load testing)
pip install locust

# Create locustfile.py
# Run load test
locust -f locustfile.py --headless -u 100 -r 10 --run-time 5m
```

## Migration Path

### SQLite → PostgreSQL

When to migrate:
- Concurrent writes > 10/sec
- Data size > 1GB
- Need read replicas

```powershell
# 1. Export SQLite data
sqlite3 cortex_brain/state/governance.db .dump > backup.sql

# 2. Create PostgreSQL database
psql -c "CREATE DATABASE cortex"

# 3. Migrate schema and data
# (Use migration tool like pgloader)

# 4. Update configuration
# cortex-config.yaml
database:
  url: postgresql://user:pass@host:5432/cortex
```

## Related

- [Runbook](5-runbook.md)
- [Disaster Recovery](6-disaster-recovery.md)
- [CI/CD Pipeline](../../_diagrams/ci-cd-pipeline.mmd)
