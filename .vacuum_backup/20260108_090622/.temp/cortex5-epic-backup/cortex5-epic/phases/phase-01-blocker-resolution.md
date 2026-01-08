# Phase 1: Critical Blocker Resolution

**Phase ID:** P001  
**Epic:** cortex5-epic-v3  
**Duration:** 1 day (10 hours)  
**Status:** 🔴 READY TO START  
**Priority:** P0_CRITICAL  
**Dependencies:** Phase 0 (Complete)  
**Blocks:** All remaining phases (2-13)

---

## 🎯 Phase Objective

Resolve 3 critical blockers preventing safe execution of Phases 2-13:
1. **Missing rollback script** - Phase 0 migration unsafe without recovery
2. **Orchestrator instantiation failures** - 6 orchestrators cannot load
3. **StateManager race condition** - Concurrent writes corrupt state

**Why Critical:** These blockers prevent ANY phase execution. Must be resolved before Phase 2 can begin.

---

## 📋 Requirements (from epic-requirements-todo.yaml)

### Requirement P00B-R001: Create Rollback Script
**Duration:** 2 hours  
**Deliverable:** `scripts/rollback-cortex-5.5-migration.ps1`

**Acceptance Criteria:**
- [ ] Script creates backup before Phase 0 migration
- [ ] Script can restore from backup on failure
- [ ] Validation confirms clean rollback state
- [ ] Test: Simulate failed migration → successful rollback

**Implementation:**
```powershell
# Features required:
# 1. Git branch reset to pre-migration state
# 2. File system restoration from backup
# 3. Database state rollback (if applicable)
# 4. Validation that rollback successful
# 5. Report generation (what was rolled back, why)
```

---

### Requirement P00B-R002: Fix planning_v5 Syntax Error
**Duration:** 0.5 hours  
**File:** `src/orchestrators/planning/planning_orchestrator_v5.py` (line 718)

**Issue:** f-string contains backslash (invalid Python syntax)

**Fix:**
```python
# Before (line 718):
f"path\to\file"  # Invalid: backslash in f-string

# After:
f"path/to/file"  # OR
"path\\to\\file"  # OR
raw_string = r"path\to\file"
```

**Validation:**
```bash
python3 -c "import src.orchestrators.planning.planning_orchestrator_v5"
# Should not raise SyntaxError
```

---

### Requirement P00B-R003: Add state_db Parameter
**Duration:** 1 hour  
**Files:**
- `src/orchestrators/ado/ado_orchestrator_v2.py`
- `src/orchestrators/cleanup/cleanup_orchestrator_v2.py`

**Issue:** Missing required `state_db` parameter in `__init__`

**Fix:**
```python
# Current:
def __init__(self, config_path: str):
    self.config_path = config_path

# Required:
def __init__(self, config_path: str, state_db: PlanningStateDB):
    self.config_path = config_path
    self.state_db = state_db
```

**Validation:**
```python
from src.orchestrators.ado.ado_orchestrator_v2 import AdoOrchestratorV2
from src.state.planning_state_db import PlanningStateDB

state_db = PlanningStateDB("cortex-brain/state/planning.db")
orchestrator = AdoOrchestratorV2("cortex.config.json", state_db)
# Should instantiate without error
```

---

### Requirement P00B-R004: Accept config_path Parameter
**Duration:** 1 hour  
**Files:**
- `src/orchestrators/tdd/tdd_orchestrator.py`
- `src/orchestrators/sanitization/sanitization_orchestrator.py`

**Issue:** Orchestrators don't accept `config_path` parameter

**Fix:**
```python
# Current:
def __init__(self, ...):
    # No config_path

# Required:
def __init__(self, config_path: str, ...):
    self.config_path = Path(config_path)
    self.config = self._load_config()
```

---

### Requirement P00B-R005: Implement log_execution() Method
**Duration:** 0.5 hours  
**File:** `src/orchestrators/state_manager.py`

**Issue:** `StateManager.log_execution()` method missing

**Implementation:**
```python
def log_execution(
    self, 
    orchestrator_id: str, 
    execution_data: Dict[str, Any]
) -> None:
    """Log orchestrator execution to audit trail."""
    self.audit.info(
        AuditCategory.EXECUTION,
        orchestrator_id,
        "execute",
        f"Orchestrator {orchestrator_id} executed",
        context=execution_data
    )
```

---

### Requirement P00B-R006: Create Integration Test Suite
**Duration:** 2 hours  
**Deliverable:** `tests/integration/test_all_orchestrators_instantiate.py`

**Test Coverage:**
```python
def test_all_orchestrators_instantiate():
    """Verify all 6 problematic orchestrators can instantiate."""
    orchestrators = [
        'planning_v5',
        'tdd_orchestrator',
        'ado_orchestrator_v2',
        'sanitization',
        'cleanup_v2',
        'vacuum_v2'
    ]
    
    for orch_id in orchestrators:
        orchestrator = registry.instantiate(orch_id)
        assert orchestrator is not None
```

---

### Requirement P00B-R007: Fix StateManager Race Condition
**Duration:** 4 hours  
**File:** `src/orchestrators/state_manager.py`

**Issue:** JSON file persistence without locking → concurrent write corruption

**Solution:** Implement file locking using `fcntl` (Unix) or `FileLock` library

**Implementation:**
```python
import fcntl  # Unix
from pathlib import Path

class StateManager:
    def _write_state(self, data: Dict[str, Any]) -> None:
        """Thread-safe state write with file locking."""
        with open(self.state_file, 'w') as f:
            # Acquire exclusive lock
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(data, f, indent=2)
            finally:
                # Release lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

**Stress Test:**
```python
def test_concurrent_writes():
    """Test StateManager handles 10 concurrent writes."""
    from concurrent.futures import ThreadPoolExecutor
    
    state_manager = StateManager("test.db")
    
    def write_state(i):
        state_manager.update({"counter": i})
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(write_state, range(100))
    
    # Verify state not corrupted
    assert state_manager.get("counter") == 99
```

**Performance Target:** <5ms lock overhead

---

## ✅ Success Criteria

**Phase 1 is complete when:**
1. ✅ Rollback script exists and tested
2. ✅ All 6 orchestrators instantiate successfully
3. ✅ StateManager thread-safe (passes stress test)
4. ✅ Integration test suite passes in CI/CD
5. ✅ Zero instantiation failures
6. ✅ Governance audit shows orchestrator errors fixed

---

## 🔄 Execution Workflow

### Step 1: Create Rollback Script (2 hours)
```bash
# Create script
code scripts/rollback-cortex-5.5-migration.ps1

# Test rollback
./scripts/rollback-cortex-5.5-migration.ps1 --dry-run
```

### Step 2: Fix Syntax Errors (0.5 hours)
```bash
# Fix planning_v5
code src/orchestrators/planning/planning_orchestrator_v5.py

# Validate
python3 -m py_compile src/orchestrators/planning/planning_orchestrator_v5.py
```

### Step 3: Fix Instantiation Issues (2 hours)
```bash
# Fix __init__ signatures
code src/orchestrators/ado/ado_orchestrator_v2.py
code src/orchestrators/cleanup/cleanup_orchestrator_v2.py
code src/orchestrators/tdd/tdd_orchestrator.py
code src/orchestrators/sanitization/sanitization_orchestrator.py

# Add missing method
code src/orchestrators/state_manager.py
```

### Step 4: Create Integration Tests (2 hours)
```bash
# Create test suite
code tests/integration/test_all_orchestrators_instantiate.py

# Run tests
pytest tests/integration/test_all_orchestrators_instantiate.py -v
```

### Step 5: Fix StateManager Race Condition (4 hours)
```bash
# Implement file locking
code src/orchestrators/state_manager.py

# Run stress test
pytest tests/test_state_manager_concurrent.py -v
```

### Step 6: Validation (Final Check)
```bash
# Re-run governance audit
python3 -m src.orchestrators.middleware.python_best_practices_validator \
  --target src/orchestrators/ \
  --output cortex-brain/tier1/tracking/governance-audit-post-phase1.json

# Compare before/after
diff \
  cortex-brain/tier1/tracking/governance-audit.json \
  cortex-brain/tier1/tracking/governance-audit-post-phase1.json
```

---

## 📊 Progress Tracking

**Update epic-requirements-todo.yaml after each task:**
```yaml
phase_p00b_blockers:
  requirements:
    - id: "P00B-R001"
      status: "complete"  # Update after rollback script done
    - id: "P00B-R002"
      status: "complete"  # Update after syntax fix
    # etc.
```

---

## 🎯 Deliverables

1. ✅ `scripts/rollback-cortex-5.5-migration.ps1`
2. ✅ Fixed `src/orchestrators/planning/planning_orchestrator_v5.py` (line 718)
3. ✅ Updated `src/orchestrators/ado/ado_orchestrator_v2.py` (__init__)
4. ✅ Updated `src/orchestrators/cleanup/cleanup_orchestrator_v2.py` (__init__)
5. ✅ Updated `src/orchestrators/tdd/tdd_orchestrator.py` (__init__)
6. ✅ Updated `src/orchestrators/sanitization/sanitization_orchestrator.py` (__init__)
7. ✅ Implemented `StateManager.log_execution()` method
8. ✅ Created `tests/integration/test_all_orchestrators_instantiate.py`
9. ✅ Thread-safe StateManager with file locking
10. ✅ Governance audit report (post-Phase 1)

---

## ⚠️ Risks & Mitigations

**Risk 1:** Rollback script fails to restore state  
**Mitigation:** Test rollback on non-production branch first

**Risk 2:** StateManager locking degrades performance  
**Mitigation:** Benchmark lock overhead, target <5ms

**Risk 3:** Fixing __init__ signatures breaks existing code  
**Mitigation:** Run full test suite after each fix

---

## 🚀 Next Phase

**Phase 2: Knowledge Extension Layer (2 weeks)**
- Depends on Phase 1 complete
- Builds company knowledge folder structure
- Implements CompanyKnowledgeProvider

**Blocked until Phase 1 complete.**

---

**Phase Status:** 🔴 READY TO START  
**Estimated Completion:** 1 day from start  
**Phase Owner:** CORTEX Engineering Team
