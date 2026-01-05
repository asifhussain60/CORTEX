# Phase 2-3 Combined: Orchestrator Interface Fixes

**Date:** January 4, 2026  
**Status:** 🔄 IN PROGRESS

## Problem Analysis

After testing, the actual orchestrator issues are different from initial brittleness reports:

### Actual Issues Found:

1. **planning_v5**: `TypeError: __init__() missing 1 required positional argument: 'config_path'`
   - Constructor requires `config_path` as first positional arg
   - Callers trying to use `state_db` only
   
2. **StateManager missing method**: `log_execution()` method doesn't exist
   - Orchestrators call `self.db.log_execution()` 
   - StateManager delegates to PlanningStateDB.log_execution()
   - Need to add wrapper method

## Root Cause

The orchestrator instantiation pattern expects:
```python
# Current (broken):
orch = PlanningOrchestratorV5(state_db=StateManager(db))

# Required:
orch = PlanningOrchestratorV5(
    config_path="path/to/config.yaml",
    state_db=StateManager(db)
)
```

## Solution Strategy

### Option 1: Make config_path Optional (RECOMMENDED)
- Change `config_path: str` to `config_path: Optional[str] = None`
- Load default config if None
- Maintains backward compatibility

### Option 2: Update All Callers
- Find all instantiation sites
- Add config_path parameter
- More invasive, breaks existing code

**Decision: Option 1** - Less invasive, maintains compatibility

## Implementation Plan

### Step 1: Fix planning_v5 Constructor
File: `src/orchestrators/planning/planning_orchestrator_v5.py`

```python
def __init__(
    self,
    config_path: Optional[str] = None,  # <-- Make optional
    state_db: Optional[PlanningStateDB] = None,
    plan_id: Optional[str] = None,
    template_dir: Optional[str] = None
):
    """Initialize Planning Orchestrator v5."""
    # Load default config if not provided
    if config_path is None:
        config_path = "cortex-brain/config/planning-v5-default.yaml"
    
    # Initialize database if not provided
    if state_db is None:
        db_path = "cortex-brain/database/planning_state.db"
        state_db = PlanningStateDB(db_path=db_path)
    
    super().__init__(config_path, state_db, plan_id, template_dir)
    ...
```

### Step 2: Add StateManager.log_execution() Method
File: `src/orchestrators/state_manager.py`

```python
def log_execution(
    self,
    orchestrator: str,
    phase: str,
    status: str,
    metrics: Dict[str, Any]
) -> None:
    """
    Log execution event to database.
    
    Wrapper around PlanningStateDB.log_execution() for convenience.
    
    Args:
        orchestrator: Orchestrator name
        phase: Phase identifier
        status: Execution status (started/completed/failed)
        metrics: Execution metrics dictionary
    """
    self.db.log_execution(
        orchestrator_id=orchestrator,
        status=status,
        parameters={
            'phase': phase,
            'metrics': metrics
        }
    )
    
    self.logger.info(
        f"Logged execution: {orchestrator}/{phase} - {status}"
    )
```

### Step 3: Apply Same Pattern to Other 5 Orchestrators
- tdd_orchestrator.py
- ado_orchestrator_v2.py
- sanitization_orchestrator.py
- cleanup_orchestrator_v2.py
- vacuum_orchestrator_v2.py

Each needs `config_path` made optional with default fallback.

## Validation Tests

### Test 1: planning_v5 Instantiation
```python
from src.orchestrators.planning.planning_orchestrator_v5 import PlanningOrchestratorV5
from src.orchestrators.state_manager import StateManager
import tempfile

db_path = tempfile.mktemp(suffix='.db')
state_mgr = StateManager(PlanningStateDB(db_path))

# Test without config_path
orch = PlanningOrchestratorV5(state_db=state_mgr)
assert orch is not None

# Test with config_path
orch2 = PlanningOrchestratorV5(
    config_path="cortex-brain/config/planning-v5-default.yaml",
    state_db=state_mgr
)
assert orch2 is not None
```

### Test 2: StateManager.log_execution()
```python
state_mgr.log_execution(
    orchestrator='planning_v5',
    phase='phase-0',
    status='started',
    metrics={'estimated_hours': 2}
)
# Should not raise error
```

### Test 3: All 6 Orchestrators
Run instantiation test for each orchestrator.

## Files to Modify

1. ✅ `src/orchestrators/state_manager.py` - Add log_execution()
2. ✅ `src/orchestrators/planning/planning_orchestrator_v5.py` - Optional config_path
3. ⏳ `src/orchestrators/tdd/tdd_orchestrator.py` - Optional config_path
4. ⏳ `src/orchestrators/ado/ado_orchestrator_v2.py` - Optional config_path  
5. ⏳ `src/orchestrators/sanitization/sanitization_orchestrator.py` - Optional config_path
6. ⏳ `src/orchestrators/cleanup/cleanup_orchestrator_v2.py` - Optional config_path
7. ⏳ `src/orchestrators/vacuum/vacuum_orchestrator_v2.py` - Optional config_path

## Success Criteria

- [x] Identified actual errors (not SyntaxError as reported)
- [ ] StateManager.log_execution() implemented
- [ ] planning_v5 config_path optional
- [ ] All 6 orchestrators instantiate successfully
- [ ] 15 cleanup tests pass
- [ ] 67 vacuum tests ready for Phase 4 (Python compatibility fix)

---
*Generated by C150 Remediation Plan - Phases 2-3*
