# Resilience Patterns# Resilience Patterns



**Last Updated:** 2026-01-20  CORTEX provides built-in resilience patterns for handling failures gracefully.

**Version:** 1.0.0  

**Status:** Production Ready  ## Circuit Breaker Pattern

**Audience:** Architects, Developers, Operators

Prevent cascading failures by failing fast:

## Overview

```

CORTEX implements comprehensive resilience patterns to ensure reliable operation in production environments. This document covers the patterns, their configuration, and how they work together to provide graceful degradation and automatic recovery.┌─ Request → Check Circuit

│

---├─ If CLOSED: Forward request

│  └─ Success → Stay closed

## Table of Contents│  └─ Failure → Track failure

│     └─ If failure_rate > threshold → OPEN

1. [Resilience Philosophy](#resilience-philosophy)│

2. [Circuit Breaker Pattern](#circuit-breaker-pattern)├─ If OPEN: Reject immediately (fail fast)

3. [Retry with Backoff](#retry-with-backoff)│  └─ After timeout → Try HALF_OPEN

4. [Partial Functionality Mode](#partial-functionality-mode)│

5. [Rollback Capability](#rollback-capability)└─ If HALF_OPEN: Allow test request

6. [Bulkhead Pattern](#bulkhead-pattern)   └─ Success → Return to CLOSED

7. [Timeout Management](#timeout-management)   └─ Failure → Return to OPEN

8. [Health Checking](#health-checking)```

9. [Configuration Reference](#configuration-reference)

10. [Monitoring Resilience](#monitoring-resilience)Configuration options:

- Failure threshold (default: 50%)

---- Timeout (default: 30s)

- Success threshold before close (default: 2 requests)

## Resilience Philosophy

## Partial Functionality Mode

CORTEX's resilience approach follows these principles:

When a component fails, degrade gracefully:

1. **Fail fast**: When failure is certain, fail immediately

2. **Degrade gracefully**: Partial operation beats total failure```

3. **Recover automatically**: Transient failures shouldn't require interventionNormal Operation:

4. **Audit everything**: Every failure is recorded for analysis├─ Retrieve knowledge from Domain Brain

5. **Isolate failures**: One component's failure shouldn't cascade├─ Validate against governance rules

├─ Execute full orchestrator logic

### Failure Categories└─ Return complete result



| Category | Response | Example |Partial Failure:

|----------|----------|---------|├─ Retrieve knowledge: FAILED → Use cache

| **Transient** | Retry with backoff | Network blip |├─ Validate rules: SUCCESS

| **Persistent** | Circuit breaker | Service down |├─ Execute simplified logic

| **Partial** | Degraded mode | Cache unavailable |└─ Return partial result with warnings

| **Critical** | Graceful shutdown | Database corruption |```



---## Automatic Retry



## Circuit Breaker PatternTransient failures are retried automatically:



The circuit breaker prevents cascading failures by failing fast when a service is unhealthy.- **Exponential Backoff**: Wait times: 100ms → 200ms → 400ms → 800ms → ...

- **Max Retries**: Default 3, configurable per orchestrator

### State Machine- **Jitter**: Add randomness to prevent thundering herd



```## Rollback Capability

                    success

                 ┌──────────┐Failed transactions are rolled back atomically:

                 │          │

                 ▼          │1. Execute transaction steps

            ┌─────────┐     │2. If error at step N: Rollback steps 1..N-1

   ─────────▶  CLOSED  ├────┘3. Return error with transaction ID for audit trail

            └────┬────┘4. All changes recorded (even rollbacks)

                 │ failure_rate > threshold

                 ▼---

            ┌─────────┐

            │  OPEN   │◀────────────────┐See [Advanced Configuration](../guides/advanced/0-overview.md) for detailed configuration.

            └────┬────┘                 │
                 │ after timeout        │
                 ▼                      │
            ┌──────────┐                │
            │HALF_OPEN │────────────────┘
            └────┬─────┘   failure
                 │
                 │ success_count >= threshold
                 ▼
            ┌─────────┐
            │ CLOSED  │
            └─────────┘
```

### States Explained

| State | Behavior | Transition |
|-------|----------|------------|
| **CLOSED** | Normal operation, requests pass through | Opens if failure rate exceeds threshold |
| **OPEN** | All requests fail immediately | Moves to HALF_OPEN after timeout |
| **HALF_OPEN** | Test requests allowed | Closes on success, opens on failure |

### Configuration

```yaml
# cortex-config.yaml
resilience:
  circuit_breaker:
    enabled: true
    failure_threshold: 5        # Failures before opening
    failure_rate_threshold: 0.5 # 50% failure rate
    timeout_seconds: 30         # Time in OPEN state
    success_threshold: 2        # Successes to close
    
    # Per-service overrides
    services:
      domain_brain:
        failure_threshold: 3
        timeout_seconds: 60
      
      external_api:
        failure_threshold: 10
        timeout_seconds: 15
```

### Code Usage

```python
from src.infrastructure.resilience import circuit_breaker

class MyOrchestrator:
    @circuit_breaker("domain_brain")
    async def query_knowledge(self, query: str) -> KnowledgeResult:
        """Query protected by circuit breaker."""
        return await self.domain_brain.search(query)
    
    async def process(self, intent: str) -> Result:
        try:
            knowledge = await self.query_knowledge(intent)
        except CircuitOpenError:
            # Circuit is open - use fallback
            knowledge = await self._get_cached_knowledge(intent)
        
        return await self._execute(intent, knowledge)
```

### Metrics

| Metric | Description |
|--------|-------------|
| `cortex_circuit_state` | Current state (0=closed, 1=open, 2=half_open) |
| `cortex_circuit_failures_total` | Total failure count |
| `cortex_circuit_opens_total` | Times circuit opened |

---

## Retry with Backoff

Transient failures are handled with automatic retry using exponential backoff.

### Algorithm

```
retry_wait = base_delay * (multiplier ^ attempt) + random_jitter

Example (base=100ms, multiplier=2):
  Attempt 1: wait 100ms + jitter
  Attempt 2: wait 200ms + jitter
  Attempt 3: wait 400ms + jitter
  Attempt 4: wait 800ms + jitter (capped at max_delay)
```

### Configuration

```yaml
# cortex-config.yaml
resilience:
  retry:
    enabled: true
    max_attempts: 3
    base_delay_ms: 100
    max_delay_ms: 5000
    multiplier: 2.0
    jitter_factor: 0.1  # 10% random jitter
    
    # Retryable exceptions
    retryable_errors:
      - ConnectionError
      - TimeoutError
      - TransientDatabaseError
    
    # Non-retryable (fail immediately)
    non_retryable_errors:
      - AuthenticationError
      - ValidationError
      - GovernanceViolation
```

### Code Usage

```python
from src.infrastructure.resilience import retry_with_backoff

class MyOrchestrator:
    @retry_with_backoff(
        max_attempts=3,
        base_delay=0.1,
        retryable=(ConnectionError, TimeoutError),
    )
    async def call_external_service(self, request: dict) -> Response:
        """Call with automatic retry."""
        return await self.http_client.post("/api/endpoint", json=request)
```

### Jitter Importance

Jitter prevents the "thundering herd" problem:

```
Without jitter (bad):
  All clients retry at: 100ms, 200ms, 400ms
  → Service overwhelmed at same moments

With jitter (good):
  Client A: 95ms, 210ms, 380ms
  Client B: 108ms, 195ms, 420ms
  → Load distributed over time
```

---

## Partial Functionality Mode

When non-critical components fail, CORTEX continues operating with reduced functionality.

### Degradation Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                     FULL FUNCTIONALITY                          │
│  All services operational                                       │
├─────────────────────────────────────────────────────────────────┤
│                     PARTIAL MODE - LEVEL 1                      │
│  Cache unavailable → Use stale data with warning               │
├─────────────────────────────────────────────────────────────────┤
│                     PARTIAL MODE - LEVEL 2                      │
│  Domain Brain unavailable → Use local knowledge only           │
├─────────────────────────────────────────────────────────────────┤
│                     PARTIAL MODE - LEVEL 3                      │
│  Telemetry unavailable → Continue without metrics              │
├─────────────────────────────────────────────────────────────────┤
│                     MINIMAL MODE                                │
│  Only governance + core execution                              │
└─────────────────────────────────────────────────────────────────┘
```

### Component Criticality

| Component | Criticality | Failure Behavior |
|-----------|-------------|------------------|
| **Governance Engine** | CRITICAL | Cannot degrade - must be available |
| **Audit Trail** | CRITICAL | Queue if unavailable, flush on recovery |
| **Orchestrator Core** | CRITICAL | Fail request if unavailable |
| **Domain Brain** | HIGH | Use cached knowledge |
| **Telemetry** | MEDIUM | Continue without metrics |
| **External APIs** | LOW | Skip with warning |

### Configuration

```yaml
# cortex-config.yaml
resilience:
  partial_mode:
    enabled: true
    
    components:
      domain_brain:
        criticality: high
        fallback: cache
        cache_ttl_seconds: 3600
        
      telemetry:
        criticality: medium
        fallback: skip
        
      external_api:
        criticality: low
        fallback: skip
        timeout_ms: 5000
```

### Code Implementation

```python
class ResilientOrchestrator:
    async def process(self, intent: str) -> Result:
        """Process with partial mode support."""
        warnings = []
        
        # Try Domain Brain, fall back to cache
        try:
            knowledge = await self.domain_brain.query(intent)
        except ServiceUnavailable:
            knowledge = await self._get_cached_knowledge(intent)
            warnings.append("Using cached knowledge - Domain Brain unavailable")
        
        # Try telemetry, skip if unavailable
        try:
            await self.telemetry.record_intent(intent)
        except ServiceUnavailable:
            warnings.append("Telemetry skipped - service unavailable")
        
        # Execute core logic (no fallback - must succeed)
        result = await self._execute(intent, knowledge)
        
        # Attach warnings to result
        result.warnings = warnings
        result.partial_mode = len(warnings) > 0
        
        return result
```

---

## Rollback Capability

CORTEX supports atomic transactions with automatic rollback on failure.

### Transaction Model

```
┌─────────────────────────────────────────────────────────────────┐
│                      Transaction Flow                           │
│                                                                 │
│  BEGIN TRANSACTION                                              │
│  ├── Step 1: Update knowledge base                             │
│  │   ├── Execute                                               │
│  │   └── Record rollback action                                │
│  ├── Step 2: Update governance rules                           │
│  │   ├── Execute                                               │
│  │   └── Record rollback action                                │
│  ├── Step 3: Notify external systems ← FAILURE                 │
│  │                                                             │
│  ROLLBACK                                                       │
│  ├── Undo Step 2: Restore governance rules                     │
│  ├── Undo Step 1: Restore knowledge base                       │
│  └── Record rollback in audit trail                            │
│                                                                 │
│  RETURN ERROR with transaction_id                               │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
from src.infrastructure.resilience import transaction

class TransactionalOrchestrator:
    async def complex_operation(self, params: dict) -> Result:
        """Execute with transaction support."""
        async with transaction() as txn:
            # Step 1: Update knowledge
            old_knowledge = await self.knowledge.get(params["id"])
            await self.knowledge.update(params["id"], params["new_data"])
            txn.add_rollback(
                lambda: self.knowledge.update(params["id"], old_knowledge)
            )
            
            # Step 2: Update rules
            old_rules = await self.governance.get_rules(params["scope"])
            await self.governance.update_rules(params["scope"], params["rules"])
            txn.add_rollback(
                lambda: self.governance.update_rules(params["scope"], old_rules)
            )
            
            # Step 3: Notify (might fail)
            await self.notify_external(params)
            
            # If we get here, commit
            txn.commit()
        
        # If exception in any step, automatic rollback
        return Result(status="success", transaction_id=txn.id)
```

### Audit Trail Integration

Every transaction (including rollbacks) is recorded:

```json
{
  "entry_id": "TXN-00001234",
  "type": "transaction_rollback",
  "transaction_id": "txn-abc-123",
  "steps_completed": 2,
  "steps_rolled_back": 2,
  "failure_step": 3,
  "failure_reason": "External notification timeout",
  "duration_ms": 456,
  "timestamp": "2026-01-20T14:30:00.000Z"
}
```

---

## Bulkhead Pattern

Isolate resources to prevent one component from consuming all capacity.

### Resource Isolation

```
┌─────────────────────────────────────────────────────────────────┐
│                     Connection Pools                            │
├───────────────┬───────────────┬───────────────┬─────────────────┤
│  Domain Brain │  Governance   │  External API │    Reserved     │
│   (20 conn)   │   (10 conn)   │   (15 conn)   │   (5 conn)      │
└───────────────┴───────────────┴───────────────┴─────────────────┘
                              Total: 50 connections

If External API hangs:
├── External API: All 15 connections blocked
├── Domain Brain: 20 connections still available
├── Governance: 10 connections still available
└── System continues operating (degraded)
```

### Configuration

```yaml
# cortex-config.yaml
resilience:
  bulkhead:
    enabled: true
    
    pools:
      domain_brain:
        max_connections: 20
        max_pending: 50
        timeout_ms: 5000
        
      governance:
        max_connections: 10
        max_pending: 20
        timeout_ms: 2000
        
      external_api:
        max_connections: 15
        max_pending: 30
        timeout_ms: 10000
```

### Thread Pool Isolation

```python
from src.infrastructure.resilience import bulkhead

class IsolatedOrchestrator:
    @bulkhead("domain_brain", max_concurrent=20)
    async def query_domain_brain(self, query: str):
        """Query with bulkhead isolation."""
        return await self.domain_brain.search(query)
    
    @bulkhead("external_api", max_concurrent=15)
    async def call_external_api(self, request: dict):
        """External call with isolation."""
        return await self.http_client.post(request)
```

---

## Timeout Management

Prevent operations from hanging indefinitely.

### Timeout Hierarchy

```
Request Timeout (30s)
├── Orchestrator Timeout (25s)
│   ├── LENS Processing (5s)
│   ├── Governance Check (3s)
│   ├── Execution (15s)
│   │   ├── Domain Brain Query (5s)
│   │   ├── External API Call (8s)
│   │   └── Response Composition (2s)
│   └── Audit Recording (2s)
└── Buffer (5s)
```

### Configuration

```yaml
# cortex-config.yaml
resilience:
  timeouts:
    request: 30.0
    orchestrator: 25.0
    
    operations:
      lens_processing: 5.0
      governance_check: 3.0
      domain_brain_query: 5.0
      external_api_call: 8.0
      response_composition: 2.0
      audit_recording: 2.0
```

### Implementation

```python
from src.infrastructure.resilience import timeout

class TimeoutAwareOrchestrator:
    @timeout(seconds=25)
    async def process(self, intent: str) -> Result:
        """Process with timeout."""
        async with timeout(5):
            comprehension = await self.lens.comprehend(intent)
        
        async with timeout(3):
            governance = await self.governance.check(intent)
        
        async with timeout(15):
            result = await self._execute(intent, comprehension)
        
        return result
```

---

## Health Checking

Proactive health monitoring for all components.

### Health Check Types

| Type | Frequency | Purpose |
|------|-----------|---------|
| **Liveness** | 5s | Is the process alive? |
| **Readiness** | 10s | Can it accept requests? |
| **Deep Health** | 60s | All dependencies healthy? |

### Health Check Implementation

```python
class HealthChecker:
    async def liveness(self) -> HealthResult:
        """Basic liveness check."""
        return HealthResult(healthy=True, checks={"alive": True})
    
    async def readiness(self) -> HealthResult:
        """Readiness for traffic."""
        checks = {
            "governance_loaded": self.governance.is_ready(),
            "database_connected": self.db.is_connected(),
        }
        return HealthResult(
            healthy=all(checks.values()),
            checks=checks,
        )
    
    async def deep_health(self) -> HealthResult:
        """Comprehensive health check."""
        checks = {}
        
        # Check database
        try:
            await self.db.execute("SELECT 1")
            checks["database"] = {"healthy": True}
        except Exception as e:
            checks["database"] = {"healthy": False, "error": str(e)}
        
        # Check Domain Brain
        try:
            await self.domain_brain.ping()
            checks["domain_brain"] = {"healthy": True}
        except Exception as e:
            checks["domain_brain"] = {"healthy": False, "error": str(e)}
        
        # Check governance rules
        rule_count = await self.governance.count_rules()
        checks["governance"] = {
            "healthy": rule_count >= 29,  # Expect at least CORE rules
            "rule_count": rule_count,
        }
        
        return HealthResult(
            healthy=all(c.get("healthy", False) for c in checks.values()),
            checks=checks,
        )
```

### Endpoints

```
GET /health/live      → 200 OK (if process running)
GET /health/ready     → 200 OK or 503 Service Unavailable
GET /health/deep      → 200 OK with detailed JSON
```

---

## Configuration Reference

### Complete Resilience Configuration

```yaml
# cortex-config.yaml
resilience:
  # Master enable/disable
  enabled: true
  
  # Circuit breaker settings
  circuit_breaker:
    enabled: true
    failure_threshold: 5
    failure_rate_threshold: 0.5
    timeout_seconds: 30
    success_threshold: 2
    
  # Retry settings
  retry:
    enabled: true
    max_attempts: 3
    base_delay_ms: 100
    max_delay_ms: 5000
    multiplier: 2.0
    jitter_factor: 0.1
    
  # Partial mode settings
  partial_mode:
    enabled: true
    components:
      domain_brain:
        criticality: high
        fallback: cache
      telemetry:
        criticality: medium
        fallback: skip
        
  # Bulkhead settings
  bulkhead:
    enabled: true
    pools:
      domain_brain:
        max_connections: 20
      governance:
        max_connections: 10
        
  # Timeout settings
  timeouts:
    request: 30.0
    orchestrator: 25.0
    operations:
      lens_processing: 5.0
      governance_check: 3.0
      
  # Health check settings
  health:
    liveness_interval_seconds: 5
    readiness_interval_seconds: 10
    deep_health_interval_seconds: 60
```

---

## Monitoring Resilience

### Key Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `cortex_circuit_state` | Gauge | Circuit breaker state per service |
| `cortex_retry_attempts_total` | Counter | Total retry attempts |
| `cortex_retry_success_total` | Counter | Successful retries |
| `cortex_partial_mode_active` | Gauge | 1 if in partial mode |
| `cortex_rollback_total` | Counter | Total rollbacks |
| `cortex_timeout_total` | Counter | Timeout occurrences |
| `cortex_health_check_duration_seconds` | Histogram | Health check latency |

### Alerting Rules

```yaml
# prometheus-alerts.yaml
groups:
  - name: cortex_resilience
    rules:
      - alert: CircuitBreakerOpen
        expr: cortex_circuit_state == 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Circuit breaker open for {{ $labels.service }}"
          
      - alert: HighRetryRate
        expr: rate(cortex_retry_attempts_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High retry rate detected"
          
      - alert: PartialModeActive
        expr: cortex_partial_mode_active == 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "CORTEX operating in partial mode"
```

### Dashboard

Monitor resilience in Grafana:

```
┌────────────────────────────────────────────────────────────────┐
│                    CORTEX Resilience Dashboard                  │
├──────────────────┬──────────────────┬──────────────────────────┤
│ Circuit Breakers │ Retry Statistics │ Partial Mode Status      │
│ ● domain_brain   │ Attempts: 156    │ ◯ Full Functionality     │
│   CLOSED         │ Success: 142     │ ● Partial Mode L1        │
│ ● external_api   │ Rate: 91%        │   Cache fallback active  │
│   HALF_OPEN      │                  │                          │
├──────────────────┴──────────────────┴──────────────────────────┤
│                     Health Check History                        │
│ [██████████████████░░] 90% healthy over last hour              │
└────────────────────────────────────────────────────────────────┘
```

---

## Related Documents

- [Design Principles](2-design-principles.md) - Resilience philosophy
- [System Overview](1-system-overview.md) - Component architecture
- [Troubleshooting](../01-getting-started/3-troubleshooting.md) - Common issues
- [Operations Guide](../04-guides/operations/0-overview.md) - Operational procedures

---

**Resilience is not optional—it's what makes CORTEX production-ready.**
