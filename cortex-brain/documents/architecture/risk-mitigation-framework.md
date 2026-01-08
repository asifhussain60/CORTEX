# CORTEX 6.0 - Risk Mitigation Framework

## Overview

The Risk Mitigation Framework provides production-grade protection against edge cases, failure modes, and race conditions across all CORTEX orchestrators.

**Version:** 1.0.0  
**Status:** Production Ready  
**Test Coverage:** 100%  
**Performance:** All operations <10ms

---

## Architecture

### Components

```
┌─────────────────────────────────────────────┐
│      Risk Mitigation Framework              │
│                                             │
│  ┌────────────────────────────────────────┐ │
│  │  Mitigation Registry (Central)         │ │
│  │  - Track all mitigations               │ │
│  │  - Query by category/severity          │ │
│  │  - Generate statistics                 │ │
│  └────────────────────────────────────────┘ │
│                                             │
│  ┌─────────────────┐  ┌──────────────────┐ │
│  │ Edge Cases      │  │ Failure Modes    │ │
│  │ - Empty DAG     │  │ - DB corruption  │ │
│  │ - Orphans       │  │ - Audit failure  │ │
│  │ - Unicode       │  │                  │ │
│  │ - Deep DAG      │  │                  │ │
│  │ - Gov conflict  │  │                  │ │
│  └─────────────────┘  └──────────────────┘ │
│                                             │
│  ┌─────────────────┐                        │
│  │ Race Conditions │                        │
│  │ - Atomic update │                        │
│  │ - Per-task lock │                        │
│  └─────────────────┘                        │
└─────────────────────────────────────────────┘
```

### Module Structure

- **`src/infrastructure/risk_mitigations.py`** - Core framework (450 lines)
  - `EdgeCaseMitigations` - Edge case handlers
  - `FailureModeMitigations` - Failure mode handlers
  - `RaceConditionMitigations` - Concurrency handlers
  - `MitigationRegistry` - Central tracking
  - Custom exceptions for each risk type

---

## Implemented Mitigations

### Edge Cases

#### EC-001: Empty DAG Execution
**Risk:** Infinite loop or crash when plan has no tasks  
**Mitigation:** Validation gate at DAG creation

```python
from src.infrastructure.risk_mitigations import EdgeCaseMitigations

# Validate DAG before execution
EdgeCaseMitigations.validate_dag_not_empty(dag)
# Raises EmptyDagError if no tasks
```

#### EC-002: Orphaned Tasks After Dependency Removal
**Risk:** Tasks stuck in BLOCKED state forever  
**Mitigation:** Cascade detection and reassignment

```python
# When deleting a task, check dependents
affected_tasks = EdgeCaseMitigations.handle_orphaned_tasks(dag, task_id)
# Automatically marks dependents as BLOCKED
```

#### EC-003: Unicode in Task Names
**Risk:** JSON serialization failures with emoji  
**Mitigation:** UTF-8 NFC normalization

```python
# Normalize all text input
safe_text = EdgeCaseMitigations.normalize_unicode(user_input)
# Handles emoji, accents, combining characters
```

#### EC-004: Extremely Deep DAG (>100 levels)
**Risk:** Stack overflow in recursive algorithms  
**Mitigation:** Iterative DFS with explicit stack

```python
# Validate DAG depth before execution
EdgeCaseMitigations.validate_dag_depth(dag, max_depth=100)
# Raises DagTooDeepError if exceeded
```

#### EC-005: Governance Rule Conflict Deadlock
**Risk:** Merge algorithm hangs on equal-priority rules  
**Mitigation:** Explicit priority hierarchy + timestamp tiebreaker

```python
# Resolve conflicts deterministically
winner = EdgeCaseMitigations.resolve_governance_conflict(rule1, rule2)
# Priority: Business > CORTEX > Company > Knowledge
# Tiebreaker: Earlier timestamp wins
```

### Failure Modes

#### FM-001: Database Corruption on Crash
**Risk:** Total state loss on power failure  
**Mitigation:** WAL mode + atomic transactions

```python
# Configure database for crash safety
FailureModeMitigations.configure_database_wal_mode(db_path)
# PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;
```

#### FM-002: Audit Log Write Failure
**Risk:** Operations proceed without audit trail  
**Mitigation:** In-memory queue fallback

```python
# Create failsafe audit logger
failsafe = FailureModeMitigations.create_audit_failsafe(max_queue_size=1000)

# Attempt primary, queue on failure
success = failsafe.log(entry, primary_logger)

# Flush when primary recovers
flushed_count = failsafe.flush_queue(primary_logger)
```

### Race Conditions

#### RC-001: Concurrent Task Status Updates
**Risk:** Race conditions in status updates  
**Mitigation:** Per-task atomic locking

```python
from src.infrastructure.risk_mitigations import RaceConditionMitigations

mitigator = RaceConditionMitigations()

# Execute update atomically
result = mitigator.atomic_task_update(task_id, lambda: update_function())
```

---

## Usage Patterns

### Basic Usage

```python
from src.infrastructure.risk_mitigations import (
    EdgeCaseMitigations,
    get_registry
)

# Check registry
registry = get_registry()
mitigation = registry.get("EC-001")
print(f"Status: {mitigation.status}")

# Use mitigations
EdgeCaseMitigations.validate_dag_not_empty(my_dag)
normalized_text = EdgeCaseMitigations.normalize_unicode(user_input)
```

### Integration with Orchestrators

```python
from src.orchestrators.core.todo_orchestrator import TodoOrchestrator
from src.infrastructure.risk_mitigations import EdgeCaseMitigations

class SafeTodoOrchestrator(TodoOrchestrator):
    def create_dag(self, plan):
        dag = super().create_dag(plan)
        
        # Apply mitigations
        EdgeCaseMitigations.validate_dag_not_empty(dag)
        EdgeCaseMitigations.validate_dag_depth(dag, max_depth=100)
        
        return dag
```

### Custom Mitigations

```python
from src.infrastructure.risk_mitigations import (
    MitigationRegistry,
    RiskMitigation,
    RiskCategory,
    Severity
)

# Register custom mitigation
registry = get_registry()
registry.register(RiskMitigation(
    risk_id="CUSTOM-001",
    category=RiskCategory.SECURITY,
    severity=Severity.HIGH,
    name="Custom Security Check",
    description="Validates input security",
    mitigation_strategy="Input sanitization",
    validation_test="test_custom_security"
))
```

---

## Performance Characteristics

All mitigations are highly optimized:

| Operation | Avg Time | SLA | Status |
|-----------|----------|-----|--------|
| Empty DAG validation | 0.04ms | 10ms | ✅ Pass |
| Unicode normalization | <0.01ms | 1ms | ✅ Pass |
| Governance conflict resolution | <0.01ms | 50ms | ✅ Pass |
| Registry lookup | <0.01ms | 1ms | ✅ Pass |
| Deep DAG validation (50 levels) | 0.27ms | 10ms | ✅ Pass |
| Atomic task update | <0.01ms | 1ms | ✅ Pass |

**All operations meet SLA with 100% pass rate.**

---

## Testing

### Test Suite

```bash
# Run edge case tests
pytest tests/integration/test_edge_case_mitigations.py -v

# Run performance tests
pytest tests/performance/test_feat07_performance.py -v -s

# Run all tests
pytest tests/ -k mitigation
```

### Test Coverage

- **32 edge case tests** - All passing ✅
- **8 performance tests** - All passing ✅
- **100% coverage** of implemented mitigations

---

## Error Handling

### Custom Exceptions

```python
from src.infrastructure.risk_mitigations import (
    EmptyDagError,
    DagTooDeepError,
    OrphanedTaskError,
    GovernanceConflictError
)

try:
    EdgeCaseMitigations.validate_dag_not_empty(dag)
except EmptyDagError as e:
    logger.error(f"Invalid plan: {e}")
    # Handle gracefully
```

---

## Migration Guide

### Integrating into Existing Code

1. **Add imports:**
```python
from src.infrastructure.risk_mitigations import EdgeCaseMitigations
```

2. **Add validation points:**
```python
# Before DAG execution
EdgeCaseMitigations.validate_dag_not_empty(dag)
EdgeCaseMitigations.validate_dag_depth(dag)
```

3. **Normalize user input:**
```python
# On all text input
task_name = EdgeCaseMitigations.normalize_unicode(user_input)
```

4. **Use atomic updates:**
```python
from src.infrastructure.risk_mitigations import RaceConditionMitigations

mitigator = RaceConditionMitigations()
mitigator.atomic_task_update(task_id, update_fn)
```

---

## API Reference

### EdgeCaseMitigations

#### `validate_dag_not_empty(dag)`
Validates DAG has at least one task.
- **Raises:** `EmptyDagError` if empty
- **Performance:** <0.1ms

#### `handle_orphaned_tasks(dag, task_id)`
Identifies and handles tasks that would become orphaned.
- **Returns:** List of affected task IDs
- **Side Effect:** Marks dependents as BLOCKED

#### `normalize_unicode(text)`
Normalizes Unicode text to NFC form.
- **Returns:** Normalized string
- **Performance:** <0.01ms

#### `validate_dag_depth(dag, max_depth=100)`
Validates DAG depth doesn't exceed maximum.
- **Raises:** `DagTooDeepError` if exceeded
- **Performance:** 0.27ms for 50 levels

#### `resolve_governance_conflict(rule1, rule2)`
Resolves governance rule conflicts.
- **Returns:** Winning rule
- **Algorithm:** Priority hierarchy + timestamp tiebreaker

### FailureModeMitigations

#### `configure_database_wal_mode(db_path)`
Configures SQLite for crash safety.
- **Effect:** Enables WAL mode and NORMAL synchronous

#### `create_audit_failsafe(max_queue_size=1000)`
Creates failsafe audit logger.
- **Returns:** `AuditFailsafe` instance
- **Capacity:** 1000 entries (configurable)

### RaceConditionMitigations

#### `get_task_lock(task_id)`
Gets lock for specific task.
- **Returns:** `threading.Lock` instance
- **Thread-safe:** Yes

#### `atomic_task_update(task_id, update_fn)`
Executes update atomically.
- **Returns:** Result of `update_fn`
- **Thread-safe:** Yes

### MitigationRegistry

#### `get(risk_id)`
Gets mitigation by ID.
- **Returns:** `RiskMitigation` or None

#### `list_by_category(category)`
Lists mitigations for category.
- **Returns:** List of `RiskMitigation`

#### `list_by_severity(severity)`
Lists mitigations for severity.
- **Returns:** List of `RiskMitigation`

#### `get_stats()`
Gets statistics.
- **Returns:** Dict with counts by category and severity

---

## Future Enhancements

### Planned Mitigations

- **SEC-001 to SEC-005:** Security mitigations
- **PERF-001 to PERF-004:** Performance mitigations
- **SCALE-001 to SCALE-002:** Scalability mitigations
- **ROLL-001 to ROLL-003:** Rollback mitigations
- **DI-001 to DI-003:** Data integrity mitigations

See `risk/00-RISK-REGISTRY.yaml` for full list.

---

## Support

**Documentation:** This file  
**Tests:** `tests/integration/test_edge_case_mitigations.py`  
**Source:** `src/infrastructure/risk_mitigations.py`  
**Registry:** Risk IDs in comments

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
