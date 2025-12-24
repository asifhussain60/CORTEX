# CORTEX Event Schema Definitions

**Purpose:** Define standard event schemas for observer pattern communication

**Version:** 1.0.0 | **Updated:** December 09, 2025

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## Overview

CORTEX uses an **observer pattern** for event-driven learning. Orchestrators emit events to observers (like `LearningObserver`) which automatically capture patterns into Tier 2 (Knowledge Graph).

This document defines the canonical event schemas for all orchestrator events.

---

## Event Types

| Event Type | Emitted By | Purpose |
|------------|-----------|---------|
| `phase_completion` | Planning Orchestrator | Capture planning decisions and strategy patterns |
| `tdd_cycle_completion` | TDD Workflow Orchestrator | Capture RED→GREEN→REFACTOR patterns |
| `debug_session_completion` | Debug Workflow Orchestrator | Capture RCA patterns and bug resolutions |

---

## 1. phase_completion

**Emitted:** When a planning phase is completed (analysis, design, implementation, testing)

**Observer Method:** `on_phase_completion(event)`

**Schema:**

```python
{
    "phase_name": str,          # Required: "analysis", "design", "implementation", "testing"
    "duration_seconds": float,  # Required: Phase duration
    "decisions": List[str],     # Required: Key decisions made
    "artifacts": List[str],     # Required: Files/docs generated
    "complexity": str,          # Required: "low", "medium", "high"
    "confidence": float,        # Required: 0.0-1.0
    "started_at": str,          # Required: ISO timestamp
    "completed_at": str,        # Required: ISO timestamp
    "feature_name": str,        # Optional: Feature being planned
    "phase_id": str,            # Optional: UUID for phase tracking
    "metadata": Dict[str, Any]  # Optional: Custom fields
}
```

**Example:**

```python
{
    "phase_name": "design",
    "duration_seconds": 3600,
    "decisions": [
        "Use observer pattern for event-driven learning",
        "Flatten RCA metadata for query compatibility",
        "Session-based debugging with UUID tracking"
    ],
    "artifacts": [
        "debug_workflow_orchestrator.py",
        "test_debug_workflow_orchestrator.py"
    ],
    "complexity": "medium",
    "confidence": 0.95,
    "started_at": "2025-12-09T10:00:00",
    "completed_at": "2025-12-09T11:00:00",
    "feature_name": "Phase 5.2: Debug orchestrator observer integration",
    "phase_id": "phase-5.2.1-design"
}
```

**Captured Patterns:**

- Planning strategies
- Decision rationale
- Artifact relationships
- Complexity assessment

---

## 2. tdd_cycle_completion

**Emitted:** When a TDD cycle completes (RED→GREEN→REFACTOR)

**Observer Method:** `on_tdd_cycle_completion(event)`

**Schema:**

```python
{
    "cycle_number": int,           # Required: Sequential cycle number
    "red_phase_duration": float,   # Required: RED phase seconds
    "green_phase_duration": float, # Required: GREEN phase seconds
    "refactor_phase_duration": float, # Required: REFACTOR phase seconds
    "tests_written": int,          # Required: Number of tests created
    "tests_passed": int,           # Required: Final passing test count
    "tests_failed_initially": int, # Required: RED phase failures
    "refactorings_applied": List[str], # Required: Refactoring types
    "complexity_reduced": bool,    # Required: Did refactor reduce complexity?
    "started_at": str,             # Required: ISO timestamp
    "completed_at": str,           # Required: ISO timestamp
    "feature_name": str,           # Optional: Feature being developed
    "cycle_id": str,               # Optional: UUID for cycle tracking
    "coverage_before": float,      # Optional: Pre-refactor coverage %
    "coverage_after": float,       # Optional: Post-refactor coverage %
    "metadata": Dict[str, Any]     # Optional: Custom fields
}
```

**Example:**

```python
{
    "cycle_number": 3,
    "red_phase_duration": 600,
    "green_phase_duration": 900,
    "refactor_phase_duration": 450,
    "tests_written": 11,
    "tests_passed": 11,
    "tests_failed_initially": 11,
    "refactorings_applied": [
        "Extract method: _notify_observers",
        "Flatten metadata structure",
        "Add session lifecycle tracking"
    ],
    "complexity_reduced": True,
    "started_at": "2025-12-09T08:00:00",
    "completed_at": "2025-12-09T08:32:30",
    "feature_name": "Debug workflow orchestrator",
    "cycle_id": "tdd-cycle-5.2.1-003",
    "coverage_before": 0.0,
    "coverage_after": 1.0
}
```

**Captured Patterns:**

- TDD efficiency metrics
- Refactoring strategies
- Test design patterns
- Coverage improvement

---

## 3. debug_session_completion

**Emitted:** When a debug session completes with RCA (Root Cause Analysis)

**Observer Method:** `on_debug_session_completion(event)`

**Schema:**

```python
{
    "session_id": str,             # Required: UUID for session tracking
    "symptom": str,                # Required: Bug symptom description
    "root_cause": str,             # Required: Identified root cause
    "fix_applied": str,            # Required: Solution implemented
    "prevention": str,             # Required: How to prevent recurrence
    "recurrence_risk": str,        # Required: "low", "medium", "high"
    "affected_features": List[str], # Required: Features impacted by bug
    "target": str,                 # Required: Module/file where bug existed
    "duration_seconds": float,     # Required: Debug session duration
    "started_at": str,             # Required: ISO timestamp
    "completed_at": str,           # Required: ISO timestamp
    "tests_added": int,            # Optional: Tests added to prevent recurrence
    "metadata": Dict[str, Any]     # Optional: Custom fields
}
```

**Example:**

```python
{
    "session_id": "dbg-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "symptom": "Application crashes on login with null pointer exception",
    "root_cause": "Session validation accessed session object before null check",
    "fix_applied": "Added null check before session.get_user() call in auth_middleware.py:45",
    "prevention": "Add unit tests for null session scenarios; Add session null checks to code review checklist",
    "recurrence_risk": "low",
    "affected_features": ["authentication", "sessions", "user_login"],
    "target": "src/auth/auth_middleware.py",
    "duration_seconds": 1800,
    "started_at": "2025-12-09T14:00:00",
    "completed_at": "2025-12-09T14:30:00",
    "tests_added": 3
}
```

**Captured Patterns:**

- Bug resolution patterns
- RCA methodologies
- Prevention strategies
- Recurrence risk assessment

---

## Metadata Structure

### Flattened vs Nested

**CORTEX uses FLATTENED metadata** for query compatibility:

✅ **Correct (Flattened):**

```python
{
    "metadata": {
        "symptom": "Login crash",
        "root_cause": "Null pointer",
        "recurrence_risk": "low"
    }
}
```

❌ **Incorrect (Nested):**

```python
{
    "metadata": {
        "rca": {
            "symptom": "Login crash",
            "root_cause": "Null pointer",
            "recurrence_risk": "low"
        }
    }
}
```

**Reason:** Phase 5.1.6 RCA query methods expect top-level metadata fields for efficient SQLite queries.

---

## Observer Implementation

### Required Methods

All observers MUST implement methods for each event type they handle:

```python
class CustomObserver:
    def on_phase_completion(self, event: Dict[str, Any]) -> None:
        """Handle planning phase completion."""
        pass
    
    def on_tdd_cycle_completion(self, event: Dict[str, Any]) -> None:
        """Handle TDD cycle completion."""
        pass
    
    def on_debug_session_completion(self, event: Dict[str, Any]) -> None:
        """Handle debug session completion."""
        pass
```

### Error Isolation

Observers MUST NOT propagate exceptions to orchestrators:

```python
def _notify_observers(self, event: Dict[str, Any]) -> None:
    """Notify all observers with error isolation."""
    for observer in self.observers:
        try:
            if hasattr(observer, 'on_debug_session_completion'):
                observer.on_debug_session_completion(event)
            else:
                logger.warning(f"Observer missing handler method")
        except Exception as e:
            logger.error(f"Observer notification failed: {e}")
            # DON'T propagate - orchestrator continues
```

---

## Schema Validation (Optional)

For strict validation, use JSON Schema:

```python
DEBUG_SESSION_SCHEMA = {
    "type": "object",
    "required": [
        "session_id", "symptom", "root_cause", "fix_applied",
        "prevention", "recurrence_risk", "affected_features",
        "target", "duration_seconds", "started_at", "completed_at"
    ],
    "properties": {
        "session_id": {"type": "string", "pattern": "^dbg-[0-9a-f-]{36}$"},
        "symptom": {"type": "string", "minLength": 10},
        "root_cause": {"type": "string", "minLength": 10},
        "fix_applied": {"type": "string", "minLength": 10},
        "prevention": {"type": "string", "minLength": 10},
        "recurrence_risk": {"type": "string", "enum": ["low", "medium", "high"]},
        "affected_features": {"type": "array", "items": {"type": "string"}},
        "target": {"type": "string"},
        "duration_seconds": {"type": "number", "minimum": 0},
        "started_at": {"type": "string", "format": "date-time"},
        "completed_at": {"type": "string", "format": "date-time"}
    }
}
```

**Usage:**

```python
from jsonschema import validate

validate(instance=event, schema=DEBUG_SESSION_SCHEMA)
```

---

## Performance Requirements

**All event emissions MUST complete in <50ms:**

- Event payload construction: <10ms
- Observer notification: <40ms total (all observers)
- Tier 2 storage: Handled asynchronously by observer

**Current Performance (Phase 5.2.1):**

- Debug event emission: 6-10ms (500x under target)
- Planning event emission: 5-8ms
- TDD event emission: 8-12ms

---

## Testing Requirements

### Unit Tests

Each orchestrator MUST have tests for:

1. ✅ **Event Emission:** Verify event is emitted with correct structure
2. ✅ **Observer Notification:** Verify all subscribed observers receive event
3. ✅ **Error Isolation:** Verify observer exceptions don't crash orchestrator
4. ✅ **Performance:** Verify <50ms emission time
5. ✅ **Payload Completeness:** Verify all required fields present

### Integration Tests

Each observer integration MUST have tests for:

1. ✅ **Pattern Storage:** Verify Tier 2 stores pattern correctly
2. ✅ **Query Compatibility:** Verify stored patterns are queryable
3. ✅ **Metadata Structure:** Verify flattened metadata structure
4. ✅ **Concurrent Events:** Verify multiple events handled correctly

---

## Migration Guide

### From Nested to Flattened Metadata

**Old Code (v5.1.5 and earlier):**

```python
pattern = {
    "metadata": {
        "rca": {
            "symptom": event["symptom"],
            "root_cause": event["root_cause"]
        }
    }
}
```

**New Code (v5.2.1+):**

```python
pattern = {
    "metadata": {
        "symptom": event.get("symptom"),
        "root_cause": event.get("root_cause"),
        "recurrence_risk": event.get("recurrence_risk", "medium")
    }
}
```

**Query Updates:**

Old queries expecting `metadata.rca.*` will fail. Update to:

```python
# OLD
cursor.execute("SELECT * FROM patterns WHERE json_extract(metadata, '$.rca.symptom') = ?", (symptom,))

# NEW
cursor.execute("SELECT * FROM patterns WHERE json_extract(metadata, '$.symptom') = ?", (symptom,))
```

---

## Related Documentation

- **Observer Pattern Implementation:** `src/orchestrators/learning_observer.py`
- **Debug Orchestrator:** `src/orchestrators/debug_workflow_orchestrator.py`
- **Planning Orchestrator:** `src/workflows/planning_orchestrator.py`
- **TDD Orchestrator:** `src/workflows/tdd_workflow_orchestrator.py`
- **RCA Query Methods:** `src/tier2/knowledge_graph.py` (Lines 2400-2700)
- **Phase 5.1.6 Completion:** `cortex-brain/documents/reports/TDD-MASTERY-PHASE-5.1.6-COMPLETION.md`
- **Phase 5.2.1 Completion:** `cortex-brain/documents/reports/TDD-MASTERY-PHASE-5.2.1-COMPLETION.md`

---

## Changelog

### v1.0.0 (December 09, 2025)

- Initial schema definitions for 3 event types
- Documented flattened metadata structure
- Added performance requirements (<50ms)
- Included JSON Schema validation examples
- Added migration guide from nested to flattened structure

---

**End of Event Schema Definitions**
