# CORTEX Learning System - Event Infrastructure

**Version:** 1.0.0 (Phase 1 Complete)  
**Author:** Asif Hussain  
**Status:** Production Ready

## Overview

Event-driven learning system that captures milestone events from CORTEX orchestrators and agents to generate educational documentation.

### Architecture

- **Event-Driven:** No orchestrator coupling, fire-and-forget pattern
- **Milestone-Based:** Only significant events captured (not continuous)
- **Thread-Safe:** Concurrent event capture with locking
- **High-Performance:** <10ms overhead per event

### Components

```
src/learning/
├── __init__.py              # Module exports
├── event_collector.py       # Event capture and storage (97% coverage)
├── event_taxonomy.py        # 52 event types across 3 tiers (95% coverage)
└── README.md               # This file
```

## Quick Start

### Capturing Events

```python
from src.learning.event_collector import get_global_collector
from src.learning.event_taxonomy import LearningEvent, EventType

# Emit event (fire-and-forget, <10ms)
event = LearningEvent(
    event_type=EventType.PLAN_APPROVED,
    component="PlanningOrchestrator",
    metadata={"plan_id": "feature-xyz", "phases": 4}
)
get_global_collector().capture_event(event)
```

### Retrieving Events

```python
collector = get_global_collector()

# Get all milestone events
milestones = collector.get_milestone_events()

# Filter by category
planning_events = collector.get_events_by_category(EventCategory.MILESTONES)

# Filter by component
ado_events = collector.get_events_by_component("ADOUtility")

# Performance statistics
stats = collector.get_performance_stats()
print(f"Avg overhead: {stats['avg_capture_time_ms']}ms")
```

## Event Taxonomy

### Tier 1: Must-Have Events (19 events, Phase 1-4)

**Planning & Execution (6 events)**
- `PLAN_CREATED`, `PLAN_APPROVED`, `PLAN_ABANDONED`
- `PHASE_STARTED`, `PHASE_COMPLETED`, `CHECKPOINT_COMMITTED`

**ADO Work Management (4 events)**
- `ADO_STORY_CREATED`, `ADO_FEATURE_CREATED`
- `ADO_WORK_ITEM_COMPLETED`, `ADO_ACCEPTANCE_CRITERIA_VALIDATED`

**Workflow Routing (3 events)**
- `WORKFLOW_STARTED`, `OPERATION_ROUTED`, `WORKFLOW_COMPLETED`

**Planning Strategy (6 events)**
- `PLANNING_REQUEST`, `PLAN_STRATEGY_SELECTED`, `PLAN_VALIDATED`
- `INTERACTIVE_PLANNING_STARTED`, `CLARIFICATION_REQUESTED`, `REQUIREMENTS_FINALIZED`

### Tier 2-3: Should-Have Events (33 events, Phase 5-7)

Architectural patterns, code quality, design decisions, debugging patterns, productivity patterns, operational learnings, user onboarding, intent routing.

## Integration Points

### Orchestrators (Phase 1.5-1.7)
- **PlanningOrchestrator:** `approve_plan()` → PLAN_APPROVED
- **PlanExecutionOrchestrator:** `_execute_phase()` → PHASE_STARTED, PHASE_COMPLETED
- **GitCheckpointOrchestrator:** `create_checkpoint()` → CHECKPOINT_COMMITTED

### Utilities (Phase 1.8-1.9)
- **ADOUtility:** `create_work_item()` → ADO_STORY_CREATED / ADO_FEATURE_CREATED
- **ADOUtility:** `update_work_item()` → ADO_WORK_ITEM_COMPLETED
- **UnifiedEntryPointOrchestrator:** `execute_*()` → WORKFLOW_STARTED, WORKFLOW_COMPLETED

### Agents (Phase 1.10-1.11)
- **WorkPlanner:** `execute()` → PLANNING_REQUEST, PLAN_VALIDATED
- **InteractivePlanner:** `execute()` → INTERACTIVE_PLANNING_STARTED

## Integration Pattern

All integrations follow this pattern:

```python
# Import with graceful degradation
try:
    from src.learning.event_collector import get_global_collector
    from src.learning.event_taxonomy import LearningEvent, EventType
except ImportError:
    get_global_collector = None
    LearningEvent = None
    EventType = None

# Emit event with exception safety
if get_global_collector and LearningEvent and EventType:
    try:
        event = LearningEvent(
            event_type=EventType.PLAN_APPROVED,
            component="MyComponent",
            metadata={"key": "value"}
        )
        get_global_collector().capture_event(event)
    except Exception as e:
        logger.debug(f"Learning event capture failed: {e}")
```

**Key Principles:**
1. **No Blocking:** Fire-and-forget pattern
2. **Graceful Degradation:** Import errors handled
3. **Exception Safety:** Event failures don't break workflow
4. **Performance:** <10ms overhead validated

## Performance Characteristics

- **Event Capture:** <10ms per event (validated)
- **Milestone Filtering:** <10ms for 100 events
- **Thread Safety:** Lock-based, no deadlocks
- **Memory:** In-memory storage (Phase 1), database persistence (Phase 2)

## Testing

```bash
# Run all tests
pytest tests/learning/test_event_collector.py -v

# With coverage
pytest tests/learning/test_event_collector.py --cov=src/learning --cov-report=term-missing

# Performance tests only
pytest tests/learning/test_event_collector.py::TestPerformance -v
```

**Test Coverage:**
- 33 comprehensive tests
- 96% code coverage (218/227 statements)
- All tests pass in <0.2s

## Future Phases

### Phase 2: Document Generation (Weeks 2-3)
- Template-based markdown generation
- 15 learning categories
- Resource database integration

### Phase 3: Docsify UI (Week 4)
- Learning dashboard launcher
- Full-text search
- Sidebar navigation

### Phase 4: MVP Testing (Week 5)
- End-to-end validation
- Performance tuning
- Documentation polish

### Phase 5-7: Should-Have Events (Weeks 6-11)
- Architectural learning (15 events)
- System operations (18 events)
- Complete feature set

## Troubleshooting

**Import Errors:**
```python
# Check if learning system available
from src.learning import __version__
print(f"Learning system version: {__version__}")
```

**Performance Issues:**
```python
# Check performance stats
collector = get_global_collector()
stats = collector.get_performance_stats()
print(f"Overhead target met: {stats['overhead_target_met']}")
print(f"Average capture time: {stats['avg_capture_time_ms']}ms")
```

**Event Not Captured:**
- Verify EventType is in must-have tier (filter_must_have_only=True in Phase 1)
- Check component name matches expected value
- Ensure collector is enabled: `collector.enabled`

## API Reference

See inline documentation in:
- `src/learning/event_collector.py` - LearningEventCollector class
- `src/learning/event_taxonomy.py` - EventType, EventCategory, LearningEvent

## License

Source-Available (Use Allowed, No Contributions)  
Copyright © 2024-2025 Asif Hussain. All rights reserved.
