# Phase 3: Plan Lifecycle Management

**Phase ID:** 03  
**Plan:** cortex-rearchitecture-v1  
**Status:** IN PROGRESS  
**Estimated Time:** 16h (2 days)

---

## 🎯 Objectives

Implement automated plan lifecycle management with state machine validation, folder transitions (temp → active → completed), DoR approval workflows, and progress persistence.

### Success Criteria
✅ State machine enforces valid lifecycle transitions  
✅ DoR approval gate before temp → active  
✅ Automated folder movement (temp/active/completed)  
✅ Progress tracker persists state across sessions  
✅ Integration with PlanningOrchestrator, TempPlanManager  
✅ All tests passing (100%)

---

## 📋 Tasks

### Task 3.1: RED - Create Lifecycle Tests (2h)
**Objective:** Write failing tests for plan lifecycle state machine

**Tests to Create:**
1. `test_plan_lifecycle_manager.py`
   - `test_state_machine_initialization` - FSM starts in TEMP state
   - `test_temp_to_active_requires_approval` - DoR gate enforcement
   - `test_active_to_completed_transition` - Valid completion flow
   - `test_invalid_transitions_rejected` - Skip prevention (temp → completed)
   - `test_folder_movement_on_transition` - Physical file moves
   - `test_progress_persistence` - State survives restarts
   
2. `test_dor_approval_workflow.py`
   - `test_dor_checklist_validation` - Required criteria present
   - `test_user_approval_required` - Interactive gate
   - `test_auto_approve_for_tier_1_2` - Lightweight bypass
   - `test_approval_rejection_returns_to_temp` - Failure handling

**Expected State:** All tests failing (RED phase)

---

### Task 3.2: GREEN - Implement PlanLifecycleManager (6h)
**Objective:** Create lifecycle manager with state machine

**Components:**

1. **PlanLifecycleManager** (`src/planning/plan_lifecycle_manager.py`)
   ```python
   class PlanLifecycleManager:
       """Manages plan lifecycle with state machine validation."""
       
       def __init__(self, project_root: Path):
           self.fsm = self._create_lifecycle_fsm()
           self.project_root = project_root
           
       def transition_to(self, plan_id: str, to_state: PlanState) -> bool:
           """Attempt state transition with validation."""
           
       def request_dor_approval(self, plan_id: str) -> ApprovalResult:
           """Interactive DoR approval workflow."""
           
       def move_plan_folder(self, plan_id: str, from_status: str, to_status: str):
           """Physical folder movement on state change."""
           
       def persist_state(self, plan_id: str, state: PlanState):
           """Save state to progress-tracker.json."""
           
       def restore_state(self, plan_id: str) -> Optional[PlanState]:
           """Load state from progress-tracker.json."""
   ```

2. **PlanState Enum**
   ```python
   class PlanState(Enum):
       TEMP = "temp"              # Unapproved, in temp-plans/
       AWAITING_APPROVAL = "awaiting_approval"  # DoR review pending
       ACTIVE = "active"          # Approved, in active/
       IN_PROGRESS = "in_progress"  # Execution started
       COMPLETED = "completed"    # Done, in completed/
       ARCHIVED = "archived"      # Historical, in archived/
   ```

3. **State Machine Configuration**
   - Valid transitions:
     - TEMP → AWAITING_APPROVAL (request approval)
     - AWAITING_APPROVAL → ACTIVE (approval granted)
     - AWAITING_APPROVAL → TEMP (approval rejected)
     - ACTIVE → IN_PROGRESS (execution started)
     - IN_PROGRESS → COMPLETED (all phases done)
     - COMPLETED → ARCHIVED (after 180 days)
   - Guard conditions:
     - TEMP → AWAITING_APPROVAL: DoR checklist complete
     - AWAITING_APPROVAL → ACTIVE: User approval + tier validation
     - IN_PROGRESS → COMPLETED: All phases 100% + tests passing

**Expected State:** 14/14 tests passing (GREEN phase)

---

### Task 3.3: DoR Approval Workflow (3h)
**Objective:** Interactive approval gate with checklist

**Features:**
1. **DoR Checklist:**
   - ✅ Problem statement clear
   - ✅ Success criteria defined
   - ✅ Phases breakdown logical
   - ✅ Estimated time reasonable
   - ✅ Dependencies identified
   - ✅ Risks assessed

2. **Approval Workflow:**
   ```python
   def request_dor_approval(self, plan_id: str) -> ApprovalResult:
       """
       Interactive approval workflow:
       1. Display DoR checklist with status
       2. Show plan summary (user request, approach, phases)
       3. Prompt: "Approve this plan? (y/n/edit)"
       4. On approval: Transition AWAITING_APPROVAL → ACTIVE
       5. On rejection: Provide feedback, return to TEMP
       6. On edit: Update plan, re-validate DoR
       """
   ```

3. **Auto-Approve Rules:**
   - Tier 1-2 (INSTANT/LIGHTWEIGHT): Auto-approve if DoR complete
   - Tier 3-4 (DOCUMENTED/COMPLEX): Always require explicit approval

---

### Task 3.4: Folder Movement Integration (2h)
**Objective:** Sync state transitions with folder structure

**Integration Points:**
1. **TempPlanManager.approve_temporary_plan()**
   - Call `lifecycle_manager.transition_to(plan_id, PlanState.ACTIVE)`
   - Trigger folder move: temp-plans/{id} → active/{id}

2. **TempPlanManager.complete_plan()**
   - Call `lifecycle_manager.transition_to(plan_id, PlanState.COMPLETED)`
   - Trigger folder move: active/{id} → completed/{id}

3. **PlanningOrchestrator.save_plan()**
   - Respect current lifecycle state
   - Create in correct folder based on state

---

### Task 3.5: Progress Persistence (2h)
**Objective:** State survives restarts and interruptions

**Implementation:**
1. **Extend progress-tracker.json:**
   ```json
   {
     "plan_id": "cortex-rearchitecture-v1",
     "lifecycle_state": "in_progress",
     "lifecycle_history": [
       {"from": "temp", "to": "awaiting_approval", "timestamp": "2025-12-15T10:00:00"},
       {"from": "awaiting_approval", "to": "active", "timestamp": "2025-12-15T10:05:00", "approved_by": "user"},
       {"from": "active", "to": "in_progress", "timestamp": "2025-12-15T10:10:00"}
     ],
     "approval_metadata": {
       "dor_checklist_complete": true,
       "approved_by": "user",
       "approval_timestamp": "2025-12-15T10:05:00"
     }
   }
   ```

2. **Recovery Methods:**
   ```python
   def restore_from_checkpoint(self, plan_id: str) -> PlanLifecycleManager:
       """Load lifecycle state from progress tracker."""
       
   def create_checkpoint(self, plan_id: str):
       """Save current state to progress tracker."""
   ```

---

### Task 3.6: Orchestrator Integration (2h)
**Objective:** Wire lifecycle manager into existing orchestrators

**Changes:**

1. **PlanningOrchestrator:**
   ```python
   def __init__(self, ...):
       self.lifecycle_manager = PlanLifecycleManager(self.project_root)
       
   def create_plan(self, ...):
       # Create plan in TEMP state
       plan_id = self._generate_plan_id()
       self.lifecycle_manager.transition_to(plan_id, PlanState.TEMP)
   ```

2. **TempPlanManager:**
   ```python
   def __init__(self, ...):
       self.lifecycle_manager = PlanLifecycleManager(self.project_root)
       
   def approve_temporary_plan(self, plan_id: str):
       # Request DoR approval
       result = self.lifecycle_manager.request_dor_approval(plan_id)
       if result.approved:
           self.lifecycle_manager.transition_to(plan_id, PlanState.ACTIVE)
   ```

---

### Task 3.7: Integration Testing (1h)
**Objective:** End-to-end lifecycle validation

**Test Scenarios:**
1. Complete lifecycle: temp → awaiting_approval → active → in_progress → completed
2. Rejection handling: awaiting_approval → temp (with feedback)
3. State persistence across restarts
4. Invalid transition prevention
5. Folder structure consistency

---

## 📐 Architecture

```
src/planning/
├── plan_lifecycle_manager.py      # Main lifecycle manager (350 LOC)
└── plan_states.py                 # State definitions (50 LOC)

tests/
├── test_plan_lifecycle_manager.py # Core lifecycle tests (14 tests)
└── test_dor_approval_workflow.py  # Approval workflow tests (6 tests)
```

---

## 🔗 Dependencies

**Existing Components:**
- `src/orchestration_3_0/core/state_machine.py` - FSM engine
- `src/operations/modules/orchestration/temporary_plan_manager.py` - Temp plan handling
- `src/operations/modules/orchestration/planning_orchestrator.py` - Plan creation
- `src/workflows/plan_folder_manager.py` - Folder operations

**New Dependencies:**
- None (uses existing state machine infrastructure)

---

## 🎯 Acceptance Criteria

**DoR (Definition of Ready):**
✅ Phase 2 (Semantic Folder Organization) complete  
✅ State machine architecture understood  
✅ TempPlanManager and PlanningOrchestrator integration points identified

**DoD (Definition of Done):**
✅ All 20 tests passing (100%)  
✅ DoR approval workflow functional  
✅ State persists in progress-tracker.json  
✅ Folder movements automated  
✅ Integration with orchestrators complete  
✅ Code coverage > 90%  
✅ Documentation updated  

---

## 📊 Metrics Tracking

**Estimated Time:** 16h (2 days)  
**Actual Time:** TBD  
**Token Savings:** 0 (architectural foundation)

---

## 🚀 Execution Strategy

**TDD Cycle:**
1. RED (2h): Write 20 failing tests
2. GREEN (10h): Implement PlanLifecycleManager + DoR workflow + integrations
3. REFACTOR (2h): Code cleanup, optimization
4. VALIDATE (2h): Integration testing, documentation

**Parallel Work:**
- Tasks 3.1-3.2 sequential (TDD)
- Tasks 3.3-3.6 can be developed in parallel after 3.2 complete

---

**Next Phase:** 04 - Historical Context Integration
