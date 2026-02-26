# Modal Design Principles — CORTEX Adoption Analysis

**Date:** 2026-02-26  
**Status:** 🔵 Research Complete — Ready for Implementation Planning  
**Scope:** Architectural principles from Modal (modal.com) applicable to CORTEX without any Modal dependency  
**Source Infrastructure:** `cortex/infrastructure/`, `cortex/core/orchestrator_protocol_mixin.py`

---

## 📋 Summary

Modal (modal.com) is a serverless cloud platform for Python/AI workloads. Its value is **not** the cloud platform
itself — it is the **design principles** embedded in its API that make distributed, resilient, observable Python
functions ergonomic to write. Three of those four principles map directly onto gaps in CORTEX's current
orchestrator layer. All required infrastructure already exists in `cortex/infrastructure/`; it is simply not
composed.

| Principle | CORTEX Status | Impact | Priority |
|---|---|---|---|
| Decorator-driven operation contracts | ❌ Missing | High | P0 |
| Stateless-by-default enforcement | 🟡 Partial | Medium | P1 |
| `.map()` batch primitive on mixin | ❌ Missing | High | P0 |
| Co-location of resource contracts in code | 🟡 Inverse choice (YAML-first) | Low | P2 |

---

## 🎯 Principle 1 — Decorator-Driven Operation Contracts

### What Modal Does

```python
# Modal: all operational behavior declared on the function
@app.function(
    retries=3,
    timeout=300,
    concurrency_limit=10,
    memory=4096,
)
def process_document(doc_id: str) -> dict:
    ...
```

Every concern (retry policy, timeout, concurrency, memory) is declared **where the function is defined**,
not wired separately in caller code or YAML.

### What CORTEX Does Today

The three relevant infrastructure components exist and are fully implemented but are **never composed**:

| Component | File | Status |
|---|---|---|
| `RetryHandler` + `RetryConfig` | `cortex/infrastructure/retry_handler.py` | ✅ Implemented |
| `CircuitBreaker` + `CircuitBreakerConfig` | `cortex/infrastructure/circuit_breaker.py` | ✅ Implemented |
| `TokenBucket` + `RateLimitConfig` | `cortex/infrastructure/rate_limiter.py` | ✅ Implemented |
| `@cross_cutting_enforced` decorator | `cortex/core/orchestrator_protocol_mixin.py` | ✅ Implemented (single concern only) |

Current pattern (scattered, manual wiring per orchestrator):

```python
# In each orchestrator — repeated boilerplate, no standard contract
class MyOrchestrator(OrchestratorProtocolMixin):
    def __init__(self):
        self._retry = RetryHandler(RetryConfig(max_attempts=3))
        self._cb = CircuitBreaker(name="my-orch")

    def execute_operation(self, operation_name, parameters):
        # Manually chain retry → circuit breaker → rate limit
        ...
```

### The Gap

`@cross_cutting_enforced` already proves the decorator pattern works in CORTEX (Phase 59-e). It handles
**one** cross-cutting concern. The missing step is a single `@orchestrator_operation` decorator that
composes all three infrastructure components from one declaration point.

### Target Design

```python
# Proposed: single decorator composing all three existing infrastructure components
@orchestrator_operation(
    retries=3,
    timeout=30.0,
    rate_limit=10,          # requests/sec via TokenBucket
    circuit_breaker=True,   # uses CircuitBreaker defaults
)
def execute_operation(self, operation_name: str, parameters: dict) -> dict:
    return self._do_work(parameters)
```

### Implementation Path

- **File to create:** `cortex/core/orchestrator_operation_decorator.py`
- **Imports:** `RetryHandler`, `CircuitBreaker`, `TokenBucket` — no new infrastructure needed
- **Integrates with:** `@cross_cutting_enforced` (call it internally or merge)
- **Governance:** Add `@orchestrator_operation` to the wiring contract validation in
  `scripts/validate_orchestrator_contracts.py`

---

## 🎯 Principle 2 — Stateless-by-Default Enforcement

### What Modal Does

Modal functions are **stateless by design** — the runtime enforces it. Shared state must be explicitly
declared via typed `modal.Volume` or `modal.Dict`. There is no `self.some_flag` that leaks between
invocations.

### What CORTEX Does Today

Orchestrators carry instance state that makes parallel invocation unsafe:

```python
# cortex/core/orchestrator_protocol_mixin.py
self._cross_cutting_activated = False   # Guard flag — leaks if exception mid-method
self._orch_name: str                    # Fine (constant)
self._activated: bool                   # Risk — mutable per-invocation state
```

The canonical persistent store exists: `cortex/infrastructure/shared_brain_store.py` (SQLite-backed). The
principle says **mutable invocation state should live there**, not in instance variables.

### The Gap

There is no enforcement. An orchestrator can accumulate instance state freely and it will not be caught by
`EnforcementOrchestrator` or `scripts/validate_orchestrator_contracts.py`.

### Target Design

Two complementary changes:

**1. Instance-state audit rule** (static analysis in `EnforcementOrchestrator`):

```python
# Flag any mutable instance variable in an orchestrator that is not:
# - a constant (assigned once in __init__, never mutated)
# - a declared cross-cutting guard (known allowlist)
# - an injected dependency (RetryHandler, CircuitBreaker etc.)
MUTABLE_STATE_ALLOWLIST = {"_cross_cutting_activated", "_orch_name", "_orch_version"}
```

**2. `SharedBrainStore` as the canonical invocation-scoped store:**

```python
# Pattern: push invocation state to the store, not self
from cortex.infrastructure.shared_brain_store import SharedBrainStore

class MyOrchestrator(OrchestratorProtocolMixin):
    def execute_operation(self, operation_name, parameters):
        run_id = parameters.get("run_id")
        store = SharedBrainStore()
        store.set(f"{run_id}.status", "running")
        # ... work ...
        store.set(f"{run_id}.status", "complete")
```

### Implementation Path

- **New governance check:** Add to `EnforcementOrchestrator` — scan for mutable `self.*` that are not in
  the allowlist
- **CORE rule candidate:** CORE-065 "Orchestrator instance state must be read-only after `__init__`"
- **File:** `cortex/governance/` (new rule file following existing pattern)

---

## 🎯 Principle 3 — `.map()` as a First-Class Batch Primitive

### What Modal Does

```python
# Modal: fan-out across items is the primary parallelism primitive
results = list(process_document.map(document_ids))

# Starmap variant for multiple arguments
results = list(process_pair.starmap([(id1, ctx1), (id2, ctx2)]))
```

`.map()` is a method on **every** Modal function automatically. There is no separate concept of "batch mode."

### What CORTEX Does Today

`BulkDigestOrchestrator` re-implements ad hoc batch fan-out internally:

```python
# cortex/orchestrators/support/bulk_digest_orchestrator.py
# Custom loop, custom progress tracking, custom error aggregation — every time
for file_path in file_paths:
    result = self._process_single(file_path)
    results.append(result)
```

`DigestSessionOrchestrator`, `SweepCatalogueOrchestrator`, and others repeat the same pattern independently.
There is no shared primitive.

### The Gap

`OrchestratorProtocolMixin` has 7 interface methods (per wiring contract) but none of them is a batch
operation. Every orchestrator that needs fan-out writes its own loop.

### Target Design

Add `execute_batch` to `OrchestratorProtocolMixin` as the canonical fan-out primitive:

```python
# cortex/core/orchestrator_protocol_mixin.py — proposed addition

def execute_batch(
    self,
    operation_name: str,
    items: list[Any],
    *,
    max_workers: int = 4,
    fail_fast: bool = False,
) -> list[dict[str, Any]]:
    """Fan-out execute_operation across items (Modal .map() equivalent).

    Each item is passed as parameters["item"] to execute_operation.
    Results preserve input order. Errors are collected per-item unless
    fail_fast=True, in which case the first error raises immediately.

    Args:
        operation_name: Operation name forwarded to execute_operation.
        items: Sequence of inputs to process.
        max_workers: ThreadPoolExecutor concurrency cap.
        fail_fast: If True, raise on first item failure.

    Returns:
        List of per-item result dicts, order-preserved.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    results: list[dict[str, Any]] = [{}] * len(items)
    futures = {}

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for idx, item in enumerate(items):
            f = pool.submit(
                self.execute_operation,
                operation_name,
                {"item": item},
            )
            futures[f] = idx

        for future in as_completed(futures):
            idx = futures[future]
            try:
                results[idx] = future.result()
            except Exception as exc:
                if fail_fast:
                    raise
                results[idx] = {"status": "error", "error": str(exc), "item": items[idx]}

    return results
```

**Usage at call site (replaces all ad hoc loops):**

```python
# Before (BulkDigestOrchestrator custom loop):
for path in paths:
    result = self._process_single(path)
    results.append(result)

# After (mixin primitive):
results = self.execute_batch("ingest", paths, max_workers=8)
```

### Implementation Path

- **File:** `cortex/core/orchestrator_protocol_mixin.py` — add `execute_batch()` method
- **Tests:** `tests/core/test_orchestrator_protocol_mixin.py` (CORE-008 TDD first)
- **Refactor:** `BulkDigestOrchestrator`, `DigestSessionOrchestrator`, `SweepCatalogueOrchestrator`
  to delegate to `execute_batch()`
- **AC marker:** Emit `AC_START`/`AC_COMPLETE` inside `execute_batch()` at batch level (not per-item)

---

## 🟡 Principle 4 — Co-location of Resource Contracts in Code

### What Modal Does

There is zero YAML for function behavior. Retry count, timeout, memory, GPU type — all live directly on the
Python function via the `@app.function(...)` decorator. Code and its operational contract are co-located and
version-controlled together.

### What CORTEX Does Today

Resource and concurrency contracts live in `cortex-registry/` YAML:

```
cortex-registry/core/config/system-configuration.yaml
cortex-registry/workflows/templates/
```

This is a **deliberate CORTEX governance choice** (CORE-035 — single canonical source per concern). The
YAML-first approach provides:
- Governance team visibility without reading Python
- Contract changes auditable separately from code changes
- `EnforcementOrchestrator` can validate YAML contracts independently

### The Trade-off

| Dimension | Modal (code-first) | CORTEX (YAML-first) |
|---|---|---|
| Contract/code co-location | ✅ Same file | ❌ Separate files |
| Drift risk | ✅ None (same commit) | 🟡 Contract can lag code |
| Governance visibility | ❌ Must read Python | ✅ YAML-readable by non-devs |
| Cross-orchestrator consistency | ❌ Each function independent | ✅ Enforced by EnforcementOrchestrator |

### Recommendation

**Keep YAML-first** but add a **drift detection check** to `EnforcementOrchestrator`: verify that any
orchestrator decorated with `@orchestrator_operation(timeout=N)` matches its corresponding YAML contract
entry. This gives CORTEX both the co-location ergonomics (Principle 1 decorator) and the YAML governance
auditability.

---

## 🗺️ Implementation Roadmap

| Priority | Action | File(s) | Effort |
|---|---|---|---|
| **P0** | Create `@orchestrator_operation` decorator composing Retry + CircuitBreaker + RateLimiter | `cortex/core/orchestrator_operation_decorator.py` | Medium |
| **P0** | Add `execute_batch()` to `OrchestratorProtocolMixin` | `cortex/core/orchestrator_protocol_mixin.py` | Small |
| **P0** | TDD: tests for both above (CORE-008) | `tests/core/` | Small |
| **P1** | Add mutable instance-state audit to `EnforcementOrchestrator` | `cortex/orchestrators/core/enforcement_orchestrator.py` | Medium |
| **P1** | Refactor `BulkDigestOrchestrator` to use `execute_batch()` | `cortex/orchestrators/support/bulk_digest_orchestrator.py` | Small |
| **P2** | Drift detection: decorator vs YAML contract sync check | `EnforcementOrchestrator` | Large |

---

## 🔗 Related Files

| File | Role |
|---|---|
| `cortex/core/orchestrator_protocol_mixin.py` | Base mixin — `execute_batch()` goes here; `@cross_cutting_enforced` is the existing precedent |
| `cortex/infrastructure/retry_handler.py` | `RetryHandler`, `RetryConfig`, `RetryPolicy` — ready to compose |
| `cortex/infrastructure/circuit_breaker.py` | `CircuitBreaker`, `CircuitBreakerConfig` — ready to compose |
| `cortex/infrastructure/rate_limiter.py` | `TokenBucket`, `RateLimitConfig` — ready to compose |
| `cortex/infrastructure/shared_brain_store.py` | SQLite-backed shared state store — target for Principle 2 |
| `cortex/orchestrators/support/bulk_digest_orchestrator.py` | First refactor candidate for `execute_batch()` |
| `cortex/orchestrators/core/enforcement_orchestrator.py` | Add Principle 2 static analysis checks here |
| `scripts/validate_orchestrator_contracts.py` | Add `@orchestrator_operation` wiring contract check here |

---

*Documented: 2026-02-26 | Source: Architecture analysis session*
