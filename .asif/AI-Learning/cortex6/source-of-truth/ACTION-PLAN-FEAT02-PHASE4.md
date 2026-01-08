# 🚨 CRITICAL: Immediate Action Plan

**Generated:** 2026-01-08T06:00:00Z  
**Priority:** P0_CRITICAL  
**Estimated Duration:** 6-8 hours  
**Status:** READY FOR EXECUTION

---

## 🎯 Problem Statement

**CRITICAL GAP IDENTIFIED:** feat02 Phase 4 (Self-Management Capability) is incomplete.

**Impact:**
- ❌ HANDOFF TRIGGER not activated
- ❌ CORTEX cannot manage its own work
- ❌ feat03/feat04 work done by GitHub Copilot (should be CORTEX)
- ❌ Plan integrity compromised

**Root Cause:** Premature progression to feat03/feat04 before feat02 handoff complete.

---

## 📋 Required Actions

### 🔴 STEP 1: STOP Current Work

**Action:** Immediately pause feat04 work

**Commands:**
```bash
# Mark current position
echo "PAUSED feat04 Phase 1 Task 1.2" > .cortex-pause

# Document reason
git commit -m "feat04: PAUSE - backtracking to complete feat02 Phase 4 handoff"
```

**Duration:** 5 minutes

---

### 🔴 STEP 2: BACKTRACK to feat02 Phase 4

**Action:** Update tracker to reflect correct position

**File:** `.asif/AI-Learning/cortex6/source-of-truth/todo/00-TODO-CONTINUITY-TRACKER.yaml`

**Changes:**
```yaml
current_position:
  feature: "feat02-todo-orchestrator"  # WAS: "feat04-core-orchestration"
  phase: 4
  task: "2.4.2"  # Next task after 2.4.1 (YAML to TODOs)
  status: "NOT_STARTED"
  tdd_phase: "N/A"
  last_completed: "task-2.4.1-yaml-to-todos"
  completed_count: 58  # Keep same
  backtrack_reason: "Complete handoff trigger before continuing"
  backtrack_timestamp: "2026-01-08T06:00:00Z"
```

**Also update:**
```yaml
feat02_todo_orchestrator:
  status: IN_PROGRESS  # WAS: "COMPLETED" (incorrect)
  phases:
    - phase_id: 4
      status: IN_PROGRESS  # WAS: "NOT_STARTED"
      progress: 20  # 1/5 tasks complete
```

**Duration:** 10 minutes

---

### 🔴 STEP 3: Complete task-2.4.2 (Lifecycle Management)

**Task Definition:**
- **ID:** task-2.4.2
- **Name:** Implement CORTEX TODO lifecycle management
- **Priority:** P0_CRITICAL
- **Estimated:** 90 minutes
- **TDD Required:** true

**Implementation Steps:**

1. **RED: Write failing test**
   ```bash
   # Create test file
   touch tests/integration/test_todo_lifecycle.py
   ```

   **Test Content:**
   ```python
   def test_cortex_creates_todo_from_yaml():
       """Test CORTEX can create TODO from YAML plan"""
       
   def test_cortex_updates_todo_status():
       """Test CORTEX can update TODO status as work progresses"""
       
   def test_cortex_queries_ready_todos():
       """Test CORTEX can identify ready-to-execute TODOs"""
   ```

   **Run:** `pytest tests/integration/test_todo_lifecycle.py -v`  
   **Expected:** 3 failures (RED)

2. **GREEN: Implement minimal code**
   
   **File:** `src/orchestrators/master/todo_manager.py`
   
   Add methods:
   - `create_todo_from_plan(plan_yaml_path)`
   - `update_todo_progress(todo_id, status)`
   - `get_ready_todos()`

3. **REFACTOR: Clean up**
   
   Run: `pytest tests/integration/test_todo_lifecycle.py -v`  
   Expected: 3 passes (GREEN)

**Validation:**
- ✅ Tests pass
- ✅ Audit logged: `correlation_id="FEAT02-P4-T2.4.2"`

**Duration:** 90 minutes

---

### 🔴 STEP 4: Complete task-2.4.3 (Error Recovery)

**Task Definition:**
- **ID:** task-2.4.3
- **Name:** Implement error recovery with rollback
- **Priority:** P0_CRITICAL
- **Estimated:** 90 minutes
- **TDD Required:** true

**Implementation Steps:**

1. **RED: Write failing test**
   
   Add to `tests/integration/test_todo_lifecycle.py`:
   ```python
   def test_cortex_recovers_from_todo_failure():
       """Test CORTEX can recover from TODO execution failure"""
       
   def test_cortex_rolls_back_on_error():
       """Test CORTEX rolls back state on unrecoverable error"""
   ```

2. **GREEN: Implement**
   
   Add to `todo_manager.py`:
   - `handle_todo_error(todo_id, error)`
   - `rollback_to_checkpoint(checkpoint_id)`

3. **REFACTOR**

**Validation:**
- ✅ Tests pass
- ✅ Audit logged: `correlation_id="FEAT02-P4-T2.4.3"`

**Duration:** 90 minutes

---

### 🔴 STEP 5: Complete task-2.4.4 (Integration Test)

**Task Definition:**
- **ID:** task-2.4.4
- **Name:** End-to-end CORTEX self-management test
- **Priority:** P0_CRITICAL
- **Estimated:** 120 minutes

**Implementation:**

**File:** `tests/integration/test_cortex_self_management.py`

```python
def test_cortex_manages_own_todos():
    """
    Full integration test:
    1. Load YAML plan
    2. Create TODOs
    3. Execute DAG order
    4. Handle errors
    5. Complete successfully
    """
    
def test_cortex_audit_trail():
    """Verify complete audit trail for self-managed work"""
    
def test_cortex_rollback_capability():
    """Test CORTEX can rollback on failure"""
```

**Run:** `pytest tests/integration/test_cortex_self_management.py -v`

**Expected:** 3 tests passing

**Duration:** 120 minutes

---

### 🔴 STEP 6: Complete task-2.4.5 (Handoff Validation)

**Task Definition:**
- **ID:** task-2.4.5
- **Name:** Handoff validation and documentation
- **Priority:** P0_CRITICAL
- **Estimated:** 60 minutes

**Steps:**

1. **Run full test suite:**
   ```bash
   pytest tests/ -v
   ```
   Expected: All tests pass

2. **Validate integration:**
   ```bash
   pytest tests/integration/test_cortex_self_management.py -v
   pytest tests/integration/test_todo_lifecycle.py -v
   pytest tests/integration/test_governance_todo_integration.py -v
   ```
   Expected: All pass

3. **Update tracker:**
   ```yaml
   current_executor: "CORTEX TODO Manager"  # WAS: "GitHub Copilot"
   handoff_completed: true
   handoff_timestamp: "2026-01-08T12:00:00Z"
   ```

4. **Log handoff:**
   ```python
   logger.info(
       category=AuditCategory.EXECUTION,
       component="handoff",
       operation="executor_transition",
       message="Handoff from GitHub Copilot to CORTEX TODO Manager",
       context={
           "from": "GitHub Copilot",
           "to": "CORTEX TODO Manager",
           "phase": "feat02-phase4-complete",
           "validation": "test_cortex_self_management.py PASSED"
       },
       correlation_id="FEAT02-HANDOFF"
   )
   ```

5. **Document handoff:**
   
   **File:** `.asif/AI-Learning/cortex6/source-of-truth/HANDOFF-VALIDATION.md`
   
   Content:
   - Handoff criteria checklist
   - Test results
   - Audit log confirmation
   - Next steps

**Duration:** 60 minutes

---

## 📊 Total Timeline

| Step | Task | Duration | Cumulative |
|------|------|----------|------------|
| 1 | STOP feat04 | 5 min | 5 min |
| 2 | BACKTRACK tracker | 10 min | 15 min |
| 3 | task-2.4.2 (Lifecycle) | 90 min | 105 min |
| 4 | task-2.4.3 (Error recovery) | 90 min | 195 min |
| 5 | task-2.4.4 (Integration test) | 120 min | 315 min |
| 6 | task-2.4.5 (Handoff validation) | 60 min | 375 min |
| **TOTAL** | | **6.25 hours** | |

---

## ✅ Success Criteria

Before resuming feat04, ALL of these must be true:

- ✅ task-2.4.2 COMPLETED (lifecycle management)
- ✅ task-2.4.3 COMPLETED (error recovery)
- ✅ task-2.4.4 COMPLETED (integration test passing)
- ✅ task-2.4.5 COMPLETED (handoff validated)
- ✅ Tracker updated: `current_executor = "CORTEX TODO Manager"`
- ✅ Audit log entry: `FEAT02-HANDOFF` logged
- ✅ Integration tests pass: `pytest tests/integration/test_cortex_self_management.py -v`
- ✅ HANDOFF-VALIDATION.md created and reviewed

---

## 🚀 After Handoff Complete

### Resume feat04 (with CORTEX in control)

1. **Update tracker:**
   ```yaml
   current_position:
     feature: "feat04-core-orchestration"
     phase: 1
     task: "1.3"  # Resume from YAML-first enforcement
     status: "NOT_STARTED"
     executor: "CORTEX TODO Manager"  # Now CORTEX executes
   ```

2. **Continue work:**
   - Task 1.3: YAML-first enforcement (leverage CORE-018 rule)
   - Task 1.4: Orchestrator lifecycle management
   - Phase 2-4: TODO-Governance integration, Silent execution, Integration

3. **Validate autonomy:**
   - CORTEX creates its own TODOs
   - CORTEX executes DAG-based workflows
   - CORTEX updates tracker automatically
   - GitHub Copilot becomes advisory (not executor)

---

## 📋 Checklist

**Before Starting:**
- [ ] Read holistic review report (`HOLISTIC-REVIEW-2026-01-08.md`)
- [ ] Understand critical gap (feat02 Phase 4 incomplete)
- [ ] Review feat02 Phase 4 task definitions
- [ ] Confirm TDD enforcement enabled

**During Execution:**
- [ ] Follow RED-GREEN-REFACTOR for tasks 2.4.2, 2.4.3
- [ ] Log ALL operations with correlation IDs (FEAT02-P4-*)
- [ ] Update tracker after each task completion
- [ ] Run tests after each GREEN phase
- [ ] Commit checkpoints every 2 tasks

**After Completion:**
- [ ] All 5 Phase 4 tasks marked COMPLETED
- [ ] Integration tests pass (test_cortex_self_management.py)
- [ ] Handoff logged to audit trail
- [ ] HANDOFF-VALIDATION.md created
- [ ] Tracker updated: current_executor = "CORTEX TODO Manager"
- [ ] CONTINUATION-PROMPT.md updated with handoff status

---

## 🎯 Command Reference

**Run integration tests:**
```bash
pytest tests/integration/test_cortex_self_management.py -v
pytest tests/integration/test_todo_lifecycle.py -v
pytest tests/integration/test_governance_todo_integration.py -v
```

**Check audit logs:**
```bash
grep "FEAT02-P4" cortex-brain/audit-logs/*.jsonl
grep "HANDOFF" cortex-brain/audit-logs/*.jsonl
```

**Update tracker:**
```bash
# Edit tracker YAML
vim .asif/AI-Learning/cortex6/source-of-truth/todo/00-TODO-CONTINUITY-TRACKER.yaml

# Run update script
python3 .asif/AI-Learning/cortex6/source-of-truth/update_continuation_prompt.py
```

**Commit checkpoint:**
```bash
git add .
git commit -m "feat02-phase4: task-2.4.X complete - [description]"
```

---

**Ready to Execute:** YES  
**Priority:** P0_CRITICAL  
**Blocker:** YES (blocks feat04-feat08 progression)  
**Estimated Duration:** 6-8 hours  
**Start Immediately:** RECOMMENDED

---

**Report Generated By:** GitHub Copilot Holistic Review System  
**Action Plan ID:** ACTION-PLAN-FEAT02-PHASE4  
**Status:** READY FOR EXECUTION
