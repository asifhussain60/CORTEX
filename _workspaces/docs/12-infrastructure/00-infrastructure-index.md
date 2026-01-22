# Infrastructure & Resilience Patterns

> **Summary:** Fault tolerance, circuit breakers, state management, and observability architecture  
> **Authority:** cortex/infrastructure/ | **Last Updated:** 2026-01-22

---

## Overview

CORTEX infrastructure provides enterprise-grade resilience patterns for reliable orchestration under production load, partial failures, and ongoing changes.

**Core Patterns:**
- Circuit breakers for dependency protection
- Bulkhead isolation for resource containment
- Retry with exponential backoff and jitter
- Timeout enforcement at all integration points
- State persistence with crash recovery
- Comprehensive audit trails with hash-chain verification
- Observability with distributed tracing

---

## Architecture

```mermaid
graph TD
  A["User Request"] -->|resilience layer| B["Circuit Breaker<br/>+ Rate Limiter"]
  B -->|isolation| C["Bulkhead<br/>Thread Pool"]
  C -->|orchestration| D["Orchestrator<br/>Instance"]
  D -->|state management| E["State Manager<br/>+ Persistence"]
  E -->|fault tolerance| F["Graceful Degradation<br/>+ Fallback"]
  F -->|observability| G["Enhanced Audit Logger<br/>+ Distributed Trace"]
  
  D -->|resilience| H["Retry Handler<br/>Exponential Backoff"]
  H -->|timeout| I["Timeout Manager<br/>Deadline Enforcement"]
  I -->|recovery| D
  
  E -->|persistence| J["Database<br/>State Store"]
  G -->|audit trail| K["Audit Log DB<br/>Hash Chain"]
  
  style B fill:#ff9800,stroke:#f57c00,color:#fff
  style C fill:#ff9800,stroke:#f57c00,color:#fff
  style E fill:#2196f3,stroke:#1565c0,color:#fff
  style F fill:#4caf50,stroke:#2e7d32,color:#fff
  style G fill:#9c27b0,stroke:#7b1fa2,color:#fff
```

---

## Circuit Breaker Pattern

Prevents cascading failures by stopping requests when dependency is failing.

```mermaid
stateDiagram-v2
  [*] --> CLOSED
  CLOSED -->|failures exceed threshold| OPEN
  OPEN -->|timeout elapsed| HALF_OPEN
  HALF_OPEN -->|test request succeeds| CLOSED
  HALF_OPEN -->|test request fails| OPEN
  HALF_OPEN -->|timeout| OPEN
  
  note right of CLOSED
    Normal operation
    Requests pass through
  end note
  
  note right of OPEN
    Dependency failing
    Requests blocked immediately
  end note
  
  note right of HALF_OPEN
    Testing if dependency recovered
    Limited requests allowed
  end note
```

**Configuration:**
- Failure threshold: 50% of requests in 10-request window
- Timeout: 60 seconds before attempting recovery
- Half-open test requests: 3 before deciding

**Usage:**
```python
from cortex.infrastructure.resilience import CircuitBreaker

breaker = CircuitBreaker(
    name="domain_orchestrator",
    failure_threshold=0.5,
    recovery_timeout=60.0,
    test_requests=3
)

result = breaker.execute(orchestrator.execute, args)
```

---

## State Management

### Crash Recovery

State is persisted to database with checkpoint mechanism:

```python
from cortex.brain.core.state_manager import StateManager

state_mgr = StateManager.instance()

# Save checkpoint before risky operation
checkpoint_id = state_mgr.create_checkpoint("pre_operation")

try:
    result = execute_operation()
    state_mgr.commit_checkpoint(checkpoint_id)
except Exception as e:
    state_mgr.rollback_to_checkpoint(checkpoint_id)
    raise
```

### Concurrency

State manager is thread-safe with optimistic locking:

```python
# Write lock with version check
updated = state_mgr.update_if_version(
    state_key="orchestration_state",
    current_version=42,
    new_value={"status": "completed"},
)

if not updated:
    # Version mismatch - someone else updated
    # Retry or handle conflict
    pass
```

---

## Audit Logging

All operations logged with hash-chain verification:

```mermaid
graph LR
  E1["Event 1<br/>tool_invocation"]
  E2["Event 2<br/>governance_check"]
  E3["Event 3<br/>execution_result"]
  
  E1 -->|hash| H1["Hash<br/>abc123"]
  H1 -->|input to| E2
  E2 -->|hash| H2["Hash<br/>def456"]
  H2 -->|input to| E3
  E3 -->|hash| H3["Hash<br/>ghi789"]
  
  style H1 fill:#2196f3,stroke:#1565c0,color:#fff
  style H2 fill:#2196f3,stroke:#1565c0,color:#fff
  style H3 fill:#2196f3,stroke:#1565c0,color:#fff
```

**Verification:**
```python
from cortex.infrastructure.enhanced_audit_logger import verify_audit_chain

is_valid = verify_audit_chain(
    start_event_id="evt_001",
    end_event_id="evt_099"
)

if not is_valid:
    logger.error("Audit chain broken - potential tampering!")
```

---

## Timeout Enforcement

Deadlines propagated through entire call stack:

```python
from cortex.infrastructure.timeout import TimeoutManager

timeout_mgr = TimeoutManager.instance()

# Set deadline for entire operation
timeout_mgr.set_deadline(deadline=time.time() + 30.0)

try:
    # All sub-operations check deadline
    result = orchestrator.execute()
finally:
    timeout_mgr.clear_deadline()
```

---

## Observability

### Distributed Tracing

All operations traced with correlation IDs:

```python
from cortex.infrastructure.observability import Tracer

tracer = Tracer.instance()
trace_id = tracer.start_span("user_request")

try:
    # Span automatically includes trace_id in all logs
    logger.info(f"Processing request")  # Logs trace_id
    
    result = orchestrator.execute()
    tracer.record_metric("execution_time", elapsed)
except Exception as e:
    tracer.record_error(trace_id, e)
finally:
    tracer.end_span(trace_id)
```

### Metrics

Key metrics collected:
- Request rate (req/sec)
- Response time percentiles (p50, p95, p99)
- Error rate (errors/sec)
- Circuit breaker state transitions
- Tool invocation duration by tool
- Governance rule evaluation time

---

## See Also

- [State Management](../04-architecture/state-management.md)
- [Audit Logging](../04-architecture/audit-logging.md)
- [Observability Guide](15-observability/00-observability-index.md)
- [Source: cortex/infrastructure/](../../../cortex/infrastructure/)

---

**Author:** CORTEX Documentation Engine  
**Generated:** 2026-01-22  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
