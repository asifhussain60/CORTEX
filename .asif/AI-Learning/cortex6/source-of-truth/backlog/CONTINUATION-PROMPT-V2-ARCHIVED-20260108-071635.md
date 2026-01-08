# 🛡️🧠 CORTEX 6.0 - AUTONOMOUS CONTINUATION PROMPT v2.0

**Current Position:** feat04-core-orchestration Phase 2 Task 2.1 COMPLETED ✅  
**Completed:** 61/150 tasks (40%)  
**Next Task:** 2.2 (Governance Merger-TODO Integration)  
**Version:** 2.0.0 (Fully Autonomous)

---

## ⚡ QUICK START - ZERO AMBIGUITY MODE

**When you say "continue"**, I will:
1. Read the "IMMEDIATE NEXT TASK" section below
2. Execute it autonomously (TDD: RED→GREEN→REFACTOR)
3. Update tracker + this file
4. Commit changes
5. Move to next task

**No questions. No waiting. Pure execution.** 🚀

---

## 🎯 Current State

- **Feature:** feat04-core-orchestration (Core Orchestration Layer)
- **Phase:** 2 - TODO-Governance Integration (42% complete)
- **Completed Tasks:** 1/3 in phase 2
- **Overall Progress:** 61/150 tasks (40%)
- **Last Completed:** Task 2.1 - Master Orchestrator-TODO Integration ✅
- **Test Results:** 4/4 passing (100%)
- **Last Commit:** `d26139fa0` - feat04-p2-t2.1

---

## 🚀 EXECUTION QUEUE - ORDERED TASK LIST

### ⏩ IMMEDIATE NEXT TASK

**Task 2.2: Connect Governance Merger to TODO Generation**

**ID:** feat04-p2-t2.2  
**Status:** NOT_STARTED  
**Estimated:** 30 minutes  
**TDD Required:** ✅ Yes

#### 📋 What to Build

Connect the 4-tier Governance system (feat03) to TODO generation so that governance rule violations automatically create TODO items.

**Core Functionality:**
1. `MasterOrchestrator.connect_governance(merger: GovernanceMerger)` - Register governance
2. Governance rules drive TODO creation (e.g., "YAML_FIRST" violation → TODO: "Create YAML plan first")
3. Validate governance rules before execution
4. Log governance checks to audit trail

#### 🧪 Test Plan (RED Phase)

**File:** `tests/unit/test_master_orchestrator_governance.py`

```python
# Test 1: Governance registration
def test_master_registers_governance_merger():
    """Verify MasterOrchestrator can register GovernanceMerger"""
    
# Test 2: Governance rules trigger TODOs
def test_governance_violation_creates_todo():
    """When governance rule violated, TODO item created"""
    
# Test 3: Governance validation
def test_governance_rules_validated_before_execution():
    """Governance rules checked before orchestrator execution"""
    
# Test 4: Audit logging
def test_governance_operations_logged():
    """All governance operations appear in audit log"""
```

#### 💻 Implementation Plan (GREEN Phase)

**File 1:** `src/orchestrators/core/master_orchestrator.py`

Add methods:
```python
def connect_governance(self, merger: GovernanceMerger) -> None:
    """Register GovernanceMerger for rule validation"""
    
def _validate_governance_rules(self, context: Dict[str, Any]) -> List[str]:
    """Validate governance rules, return violations"""
    
def _governance_violation_to_todo(self, violation: str) -> Dict[str, Any]:
    """Convert governance violation to TODO item"""
```

**File 2:** Reference `src/orchestrators/core/governance_merger.py` (already exists from feat03)

#### 📂 Files to Create/Modify

- ✅ **Exists:** `src/orchestrators/core/governance_merger.py` (from feat03)
- ✅ **Exists:** `src/orchestrators/core/master_orchestrator.py` (modify)
- 🆕 **Create:** `tests/unit/test_master_orchestrator_governance.py`

#### ✅ Exit Criteria

- [ ] 4 tests written BEFORE implementation (RED phase)
- [ ] All 4 tests passing (GREEN phase)
- [ ] Governance violations trigger TODO creation
- [ ] Audit logging includes governance operations
- [ ] Code refactored, docstrings added (REFACTOR phase)
- [ ] Tracker status updated to COMPLETED
- [ ] Git commit created: `feat04-p2-t2.2: Governance-TODO integration`

#### 🔗 Dependencies

- ✅ feat03-governance (COMPLETED)
- ✅ Task 2.1 - Master Orchestrator-TODO Integration (COMPLETED)

---

### 📝 Task 2.3: Implement Unified Execution Pipeline

**ID:** feat04-p2-t2.3  
**Status:** NOT_STARTED  
**Estimated:** 45 minutes  
**TDD Required:** ✅ Yes

#### 📋 What to Build

Create a unified execution pipeline that integrates TODO Orchestrator, Governance Merger, and Master Orchestrator into a single cohesive flow.

**Core Functionality:**
1. `MasterOrchestrator.execute_pipeline(request)` - Main entry point
2. Flow: Request → Governance Check → TODO Generation → Execution
3. Handle governance violations gracefully
4. Provide unified status/progress reporting

#### 🧪 Test Plan (RED Phase)

**File:** `tests/integration/test_unified_pipeline.py`

```python
# Test 1: Full pipeline flow
def test_full_pipeline_executes_end_to_end():
    """Verify request flows through governance → TODO → execution"""
    
# Test 2: Governance violation handling
def test_pipeline_handles_governance_violations():
    """When governance violated, pipeline stops gracefully"""
    
# Test 3: TODO generation integration
def test_pipeline_generates_todos_from_governance():
    """Governance rules generate appropriate TODO items"""
    
# Test 4: Status reporting
def test_pipeline_reports_unified_status():
    """Pipeline provides coherent progress updates"""
```

#### 💻 Implementation Plan (GREEN Phase)

**File:** `src/orchestrators/core/master_orchestrator.py`

Add methods:
```python
def execute_pipeline(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Execute unified pipeline: governance → TODO → execution"""
    
def _pipeline_phase_governance(self, request: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Phase 1: Governance validation"""
    
def _pipeline_phase_todo(self, violations: List[str]) -> List[Dict[str, Any]]:
    """Phase 2: TODO generation from violations"""
    
def _pipeline_phase_execute(self, todos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Phase 3: Execute TODOs"""
```

#### 📂 Files to Create/Modify

- ✅ **Exists:** `src/orchestrators/core/master_orchestrator.py` (modify)
- 🆕 **Create:** `tests/integration/test_unified_pipeline.py`

#### ✅ Exit Criteria

- [ ] 4 integration tests written BEFORE implementation (RED phase)
- [ ] All 4 tests passing (GREEN phase)
- [ ] Pipeline integrates governance + TODO + execution
- [ ] Errors handled gracefully at each phase
- [ ] Audit logging for entire pipeline flow
- [ ] Code refactored (REFACTOR phase)
- [ ] Tracker updated to COMPLETED
- [ ] Git commit: `feat04-p2-t2.3: Unified execution pipeline`

#### 🔗 Dependencies

- ✅ Task 2.1 - Master Orchestrator-TODO Integration (COMPLETED)
- 🔄 Task 2.2 - Governance Merger-TODO Integration (IN QUEUE)

---

### 🔕 Task 3.1: Implement Silent Execution Middleware

**ID:** feat04-p3-t3.1  
**Status:** NOT_STARTED  
**Estimated:** 30 minutes  
**TDD Required:** ✅ Yes

#### 📋 What to Build

Create middleware that suppresses verbose output during orchestrator execution, showing only essential progress updates (phase boundaries only).

**Core Functionality:**
1. `SilentExecutionMiddleware` class
2. Suppress task-level narration ("Now I'll...", "Perfect!", etc.)
3. Show only phase start/end updates
4. Configurable verbosity levels (SILENT, ESSENTIAL, VERBOSE)

#### 🧪 Test Plan (RED Phase)

**File:** `tests/unit/test_silent_execution.py`

```python
# Test 1: Output suppression
def test_suppresses_verbose_output():
    """Verify task narration is suppressed in SILENT mode"""
    
# Test 2: Essential updates preserved
def test_preserves_essential_updates():
    """Phase boundary updates still shown"""
    
# Test 3: Verbosity levels
def test_verbosity_levels():
    """SILENT < ESSENTIAL < VERBOSE levels work correctly"""
    
# Test 4: Integration with orchestrator
def test_integrates_with_master_orchestrator():
    """Middleware works with MasterOrchestrator"""
```

#### 💻 Implementation Plan (GREEN Phase)

**File:** `src/orchestrators/middleware/silent_execution.py`

```python
class VerbosityLevel(Enum):
    SILENT = "silent"           # Phase boundaries only
    ESSENTIAL = "essential"      # + Critical errors
    VERBOSE = "verbose"          # Everything (default)

class SilentExecutionMiddleware:
    def __init__(self, level: VerbosityLevel = VerbosityLevel.SILENT):
        ...
        
    def should_suppress(self, message_type: str) -> bool:
        """Determine if message should be suppressed"""
        
    def filter_output(self, message: str, message_type: str) -> Optional[str]:
        """Filter message based on verbosity level"""
```

#### 📂 Files to Create/Modify

- 🆕 **Create:** `src/orchestrators/middleware/silent_execution.py`
- 🆕 **Create:** `tests/unit/test_silent_execution.py`

#### ✅ Exit Criteria

- [ ] 4 tests written BEFORE implementation (RED phase)
- [ ] All 4 tests passing (GREEN phase)
- [ ] SILENT mode suppresses task narration
- [ ] Phase boundaries still displayed
- [ ] Integrates with MasterOrchestrator
- [ ] Audit logging unaffected (always full detail)
- [ ] Code refactored (REFACTOR phase)
- [ ] Tracker updated to COMPLETED
- [ ] Git commit: `feat04-p3-t3.1: Silent execution middleware`

---

### ⏱️ Task 3.2: Implement Progress Update Throttling

**ID:** feat04-p3-t3.2  
**Status:** NOT_STARTED  
**Estimated:** 20 minutes  
**TDD Required:** ✅ Yes

#### 📋 What to Build

Throttle progress updates to prevent flooding users with rapid-fire status messages. Limit to max 1 update per configurable interval (e.g., 5 seconds).

**Core Functionality:**
1. `ProgressThrottler` class with time-based throttling
2. Configurable interval (default: 5 seconds)
3. Queue updates and emit throttled
4. Always emit final update (no throttling on completion)

#### 🧪 Test Plan (RED Phase)

**File:** `tests/unit/test_progress_throttler.py`

```python
# Test 1: Throttling behavior
def test_throttles_rapid_updates():
    """Rapid updates get throttled to max rate"""
    
# Test 2: Final update always emitted
def test_final_update_always_emitted():
    """Completion message not throttled"""
    
# Test 3: Configurable interval
def test_configurable_throttle_interval():
    """Throttle interval can be configured"""
    
# Test 4: Integration
def test_integrates_with_orchestrator():
    """Throttler works with MasterOrchestrator"""
```

#### 💻 Implementation Plan (GREEN Phase)

**File:** `src/orchestrators/middleware/progress_throttler.py`

```python
class ProgressThrottler:
    def __init__(self, interval_seconds: float = 5.0):
        self.interval = interval_seconds
        self.last_emit_time = 0
        
    def should_emit(self, is_final: bool = False) -> bool:
        """Determine if update should be emitted"""
        
    def emit(self, message: str, is_final: bool = False) -> None:
        """Emit progress update (respecting throttle)"""
```

#### 📂 Files to Create/Modify

- 🆕 **Create:** `src/orchestrators/middleware/progress_throttler.py`
- 🆕 **Create:** `tests/unit/test_progress_throttler.py`

#### ✅ Exit Criteria

- [ ] 4 tests written BEFORE implementation (RED phase)
- [ ] All 4 tests passing (GREEN phase)
- [ ] Updates throttled to max rate
- [ ] Final updates never throttled
- [ ] Configurable interval works
- [ ] Integrates with MasterOrchestrator
- [ ] Code refactored (REFACTOR phase)
- [ ] Tracker updated to COMPLETED
- [ ] Git commit: `feat04-p3-t3.2: Progress update throttling`

---

### 🎯 Task 3.3: Implement Phase-Boundary-Only Updates

**ID:** feat04-p3-t3.3  
**Status:** NOT_STARTED  
**Estimated:** 25 minutes  
**TDD Required:** ✅ Yes

#### 📋 What to Build

Create reporter that ONLY emits updates at phase boundaries (start/end), completely suppressing mid-phase task updates.

**Core Functionality:**
1. `PhaseBoundaryReporter` class
2. Detect phase start/end events
3. Suppress all mid-phase updates
4. Emit concise phase summaries

#### 🧪 Test Plan (RED Phase)

**File:** `tests/unit/test_phase_boundary_reporter.py`

```python
# Test 1: Phase boundary detection
def test_detects_phase_boundaries():
    """Correctly identifies phase start/end"""
    
# Test 2: Mid-phase suppression
def test_suppresses_mid_phase_updates():
    """Task updates within phase suppressed"""
    
# Test 3: Phase summary
def test_emits_phase_summary():
    """Phase end includes summary of completed tasks"""
    
# Test 4: Integration
def test_integrates_with_master_orchestrator():
    """Reporter works with MasterOrchestrator"""
```

#### 💻 Implementation Plan (GREEN Phase)

**File:** `src/orchestrators/middleware/phase_boundary_reporter.py`

```python
class PhaseEvent(Enum):
    START = "start"
    END = "end"
    
class PhaseBoundaryReporter:
    def __init__(self):
        self.current_phase = None
        self.phase_tasks = []
        
    def is_boundary(self, event_type: str) -> bool:
        """Check if event is a phase boundary"""
        
    def report_phase_start(self, phase_name: str) -> str:
        """Generate phase start message"""
        
    def report_phase_end(self, phase_name: str, tasks_completed: int) -> str:
        """Generate phase end summary"""
```

#### 📂 Files to Create/Modify

- 🆕 **Create:** `src/orchestrators/middleware/phase_boundary_reporter.py`
- 🆕 **Create:** `tests/unit/test_phase_boundary_reporter.py`

#### ✅ Exit Criteria

- [ ] 4 tests written BEFORE implementation (RED phase)
- [ ] All 4 tests passing (GREEN phase)
- [ ] Phase boundaries detected correctly
- [ ] Mid-phase updates suppressed
- [ ] Phase summaries concise and informative
- [ ] Integrates with MasterOrchestrator
- [ ] Code refactored (REFACTOR phase)
- [ ] Tracker updated to COMPLETED
- [ ] Git commit: `feat04-p3-t3.3: Phase-boundary-only updates`

---

### 🧪 Task 4.1: End-to-End Orchestration Test

**ID:** feat04-p4-t4.1  
**Status:** NOT_STARTED  
**Estimated:** 45 minutes  
**TDD Required:** ✅ Yes

#### 📋 What to Build

Comprehensive end-to-end integration test that validates the entire orchestration stack: Master Orchestrator → Governance → TODO → Lifecycle → Silent Execution.

**Core Functionality:**
1. Full orchestration flow test
2. Real governance rules applied
3. Real TODO items generated
4. Real lifecycle state transitions
5. Silent execution mode active

#### 🧪 Test Plan (RED Phase)

**File:** `tests/integration/test_e2e_orchestration.py`

```python
# Test 1: Complete orchestration flow
def test_complete_orchestration_flow():
    """Full request → governance → TODO → execution → completion"""
    
# Test 2: Error handling
def test_orchestration_handles_errors_gracefully():
    """Errors at any stage handled properly"""
    
# Test 3: Lifecycle transitions
def test_orchestration_lifecycle_transitions():
    """Lifecycle states transition correctly throughout flow"""
    
# Test 4: Silent mode integration
def test_orchestration_respects_silent_mode():
    """Silent execution mode suppresses verbose output"""
    
# Test 5: Audit trail completeness
def test_orchestration_audit_trail_complete():
    """All operations logged to audit trail"""
```

#### 💻 Implementation Plan (GREEN Phase)

**File:** `tests/integration/test_e2e_orchestration.py`

Comprehensive integration test that:
1. Sets up full orchestration stack
2. Submits realistic requests
3. Validates governance checks
4. Confirms TODO generation
5. Verifies lifecycle transitions
6. Checks audit log completeness
7. Validates silent execution behavior

#### 📂 Files to Create/Modify

- 🆕 **Create:** `tests/integration/test_e2e_orchestration.py`
- ✅ **Reference:** All orchestrator components (no modifications)

#### ✅ Exit Criteria

- [ ] 5 integration tests written (RED phase)
- [ ] All 5 tests passing (GREEN phase)
- [ ] Full orchestration flow validated
- [ ] Error handling confirmed
- [ ] Lifecycle transitions correct
- [ ] Silent mode working
- [ ] Audit trail complete
- [ ] Code refactored (REFACTOR phase)
- [ ] Tracker updated to COMPLETED
- [ ] Git commit: `feat04-p4-t4.1: E2E orchestration test`

---

### 📊 Task 4.2: Audit Log Validation

**ID:** feat04-p4-t4.2  
**Status:** NOT_STARTED  
**Estimated:** 30 minutes  
**TDD Required:** ✅ Yes

#### 📋 What to Build

Validate that ALL orchestrator operations are properly logged to the audit trail with correct structure, levels, and correlation IDs.

**Core Functionality:**
1. Audit log completeness checker
2. Validate log structure (level, category, component, operation, correlation_id)
3. Check correlation ID consistency
4. Verify no missing operations

#### 🧪 Test Plan (RED Phase)

**File:** `tests/integration/test_audit_validation.py`

```python
# Test 1: All operations logged
def test_all_orchestrator_operations_logged():
    """Every orchestrator operation has audit log entry"""
    
# Test 2: Log structure validation
def test_audit_log_structure_valid():
    """All log entries have required fields"""
    
# Test 3: Correlation ID consistency
def test_correlation_ids_consistent():
    """Related operations share correlation IDs"""
    
# Test 4: No missing operations
def test_no_missing_audit_entries():
    """Audit trail has no gaps"""
```

#### 💻 Implementation Plan (GREEN Phase)

**File:** `tests/integration/test_audit_validation.py`

Create comprehensive audit validation:
1. Execute known orchestrator operations
2. Parse audit logs
3. Validate presence of all expected entries
4. Check structure compliance
5. Verify correlation ID usage
6. Identify any gaps

#### 📂 Files to Create/Modify

- 🆕 **Create:** `tests/integration/test_audit_validation.py`
- ✅ **Reference:** `cortex-brain/audit-logs/*.jsonl` (read-only)

#### ✅ Exit Criteria

- [ ] 4 validation tests written (RED phase)
- [ ] All 4 tests passing (GREEN phase)
- [ ] All orchestrator operations logged
- [ ] Log structure validated
- [ ] Correlation IDs consistent
- [ ] No missing audit entries
- [ ] Code refactored (REFACTOR phase)
- [ ] Tracker updated to COMPLETED
- [ ] Git commit: `feat04-p4-t4.2: Audit log validation`

---

## ⚡ AUTONOMOUS EXECUTION PROTOCOL

### When User Says "continue"

**I will execute the following sequence AUTOMATICALLY:**

1. ✅ **Load Context** - Read "IMMEDIATE NEXT TASK" section
2. ✅ **TDD RED Phase** - Write failing tests FIRST
3. ✅ **TDD GREEN Phase** - Implement to pass tests
4. ✅ **TDD REFACTOR Phase** - Clean up code, add docstrings
5. ✅ **Run Tests** - Verify all tests passing
6. ✅ **Update Tracker** - Mark task COMPLETED in `00-TODO-CONTINUITY-TRACKER.yaml`
7. ✅ **Update This File** - Move "IMMEDIATE NEXT TASK" to next task
8. ✅ **Git Commit** - Format: `feat04-p{phase}-t{task}: {task_name}`
9. ✅ **Report Completion** - Concise summary (3-5 lines max)
10. ✅ **Continue** - Immediately start next task OR stop if queue empty

### No Questions Mode

**I will NOT ask:**
- ❌ "Should I implement X?" (YES, it's in the task)
- ❌ "Which file should I modify?" (Listed in task)
- ❌ "Do you want TDD?" (YES, always for code tasks)
- ❌ "Should I commit?" (YES, always after task completion)

**I will ONLY stop if:**
- ✅ You say "stop" or "pause"
- ✅ Queue is empty (all tasks complete)
- ✅ Critical error occurs (then report and wait)

### Accessibility Compliance (SKULL Rules)

**Output Format:**
- ✅ Phase start: "## 🛡️🧠 CORTEX - Phase X: {name}"
- ✅ Task completion: "✅ Task X.Y complete (N tests passing)"
- ✅ Phase end: "## 🎉 Phase X Complete - {M/N tasks}"
- ❌ NO task narration ("Now I'll...", "Perfect!", etc.)
- ❌ NO verbose transformation details
- ❌ NO intermediate status (unless error)

**Update Frequency:**
- Phase boundaries ONLY (start/end)
- Task completion (one-line summary)
- Overall progress (every 5 tasks)

---

## 📊 Progress Tracking

### feat04-core-orchestration Status

| Phase | Tasks | Completed | Status |
|-------|-------|-----------|--------|
| Phase 1: Master Orchestrator Enhancement | 4 | 4 | ✅ COMPLETE |
| Phase 2: TODO-Governance Integration | 3 | 1 | 🔄 IN PROGRESS (33%) |
| Phase 3: Silent Execution Mode | 3 | 0 | ⏳ NOT STARTED |
| Phase 4: Integration Testing | 2 | 0 | ⏳ NOT STARTED |
| **Total** | **12** | **5** | **42%** |

### Overall CORTEX 6.0 Build

- **Total Features:** 8 (feat01-feat08)
- **Completed Features:** 3 (feat01, feat02, feat03)
- **Current Feature:** feat04 (42% complete)
- **Total Tasks:** ~150
- **Completed Tasks:** 61
- **Overall Progress:** 40%

---

## 🔗 Dependencies & Context

### Completed Dependencies (Available for Use)

- ✅ **feat01-foundation** - Base infrastructure complete
- ✅ **feat02-todo-orchestrator** - TODO system complete (51/51 tests passing)
- ✅ **feat03-governance** - 4-tier governance complete (41/41 tests passing)
- ✅ **feat04-phase1** - Master Orchestrator Enhancement complete (85/86 tests passing)

### Key Files Reference

| Component | File Path | Status |
|-----------|-----------|--------|
| Master Orchestrator | `src/orchestrators/core/master_orchestrator.py` | ✅ Exists (modify) |
| Governance Merger | `src/orchestrators/core/governance_merger.py` | ✅ Exists (feat03) |
| TODO Orchestrator | `src/orchestrators/todo_orchestrator.py` | ✅ Exists (feat02) |
| Lifecycle Manager | `src/orchestrators/middleware/orchestrator_lifecycle.py` | ✅ Exists (phase1) |
| YAML-First Enforcer | `src/orchestrators/middleware/yaml_first_enforcement.py` | ✅ Exists (phase1) |
| Audit Logger | `src/orchestrators/audit_logger.py` | ✅ Exists (foundation) |
| State Manager | `src/orchestrators/state_manager.py` | ✅ Exists (foundation) |

---

## 🛡️ Brain Protection (SKULL Rules)

### Active Rules for feat04

- ✅ **TDD_ENFORCEMENT** - All code tasks require RED→GREEN→REFACTOR
- ✅ **HOLISTIC_DISCOVERY** - Search before create (prevent duplication)
- ✅ **PLANNING_ISOLATION** - This is EXECUTION, not planning
- ✅ **CONCISE_DEFAULT** - Phase-boundary updates only
- ✅ **NO_NARRATION** - Suppress "Now I'll...", "Perfect!" commentary
- ✅ **PROGRESS_FREQUENCY** - Update at phase boundaries only

---

## 🎯 Success Criteria

### Per-Task Success
- [ ] Tests written BEFORE implementation (RED)
- [ ] All tests passing (GREEN)
- [ ] Code refactored with docstrings (REFACTOR)
- [ ] Audit logging present
- [ ] Tracker updated
- [ ] Git commit created

### Per-Phase Success
- [ ] All phase tasks complete
- [ ] Integration tests passing
- [ ] Audit trail validated
- [ ] Phase summary committed

### Feature Complete (feat04)
- [ ] All 12 tasks complete
- [ ] All 4 phases complete
- [ ] E2E orchestration working
- [ ] Silent execution mode functional
- [ ] Audit logs validated
- [ ] Ready for feat05

---

## 🚀 Ready to Execute

**Current Mode:** Autonomous v2.0 (Zero Ambiguity)  
**Waiting for:** User to say "continue"  
**Will Execute:** Task 2.2 immediately, then 2.3, 3.1, 3.2, 3.3, 4.1, 4.2  
**Estimated Total Time:** 3-4 hours for remaining 7 tasks  
**Questions:** None (fully autonomous)

---

**Last Updated:** 2026-01-08T07:30:00Z  
**Version:** 2.0.0 (Fully Autonomous)  
**Author:** Asif Hussain + GitHub Copilot
