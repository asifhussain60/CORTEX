# [Orchestrator Name] Sub-Plan Template

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** December 10, 2025  
**Status:** 📋 TEMPLATE

---

## 📋 Navigation

- **Master Plan:** [orchestration-master-plan.md](../orchestration-master-plan.md)
- **Previous:** [Link to previous orchestrator plan]
- **Next:** [Link to next orchestrator plan]
- **Workflow YAML:** `src/orchestration_3_0/workflows/[orchestrator-name]_workflow.yaml`

---

## 1️⃣ Existing State (Summarized)

### 🔎 Phase-Specific Context

**Scope:** {PHASE_SCOPE_SUMMARY}

**Files Modified in This Phase:**

{PHASE_FILES_WITH_NARRATIVE}

**Dependencies for This Phase:**

{PHASE_DEPENDENCIES_NARRATIVE}

**Architectural Considerations:**

{PHASE_ARCH_CONSIDERATIONS}

### Current Files Being Consolidated

| File | LOC | Purpose | Key Components |
|------|-----|---------|----------------|
| `path/to/file1.py` | X,XXX | Brief description | Component1, Component2 |
| `path/to/file2.py` | X,XXX | Brief description | Component3, Component4 |

**Total LOC:** X,XXX lines across Y files

### Current Workflow (High-Level Steps)

1. **User Trigger:** How users invoke today (command/CLI/API)
2. **Initialization:** What gets set up
3. **Phase 1:** First major step
4. **Phase 2:** Second major step
5. **Phase N:** Final step
6. **Completion:** Output/result

### Current Triggers

- **Natural Language:** `"trigger phrase"`, `"alternative phrase"`
- **CLI Command:** `cortex [command]`
- **API Endpoint:** `/api/[endpoint]`
- **Copilot Command:** `@cortex [command]`

### Current Issues & Pain Points

**Fragmentation:**
- Y separate files doing similar work
- Duplicated code across files (X% overlap)
- No shared state management

**Reliability:**
- Workflow completion rate: X%
- Phases skipped: Y%
- Error recovery: Manual intervention required

**Technical Debt:**
- Hard-coded paths and configurations
- No dependency injection
- No state persistence (lost progress on crash)
- No multi-tenant support

**Scalability:**
- Single-project focus
- No RBAC
- No cross-project dependencies

---

## 2️⃣ New Structure

### Target Architecture

```
src/orchestration_3_0/orchestrators/[orchestrator-name]/
├── __init__.py
├── [orchestrator-name]_orchestrator.py    # Main orchestrator (XXX LOC)
├── component1.py                          # Specific component
├── component2.py                          # Specific component
└── component3.py                          # Specific component
```

### Component Responsibilities

**Main Orchestrator (`[orchestrator-name]_orchestrator.py` - XXX LOC)**
- State machine integration
- Workflow coordination
- DI container registration
- Multi-tenant isolation
- Session management

**Component 1 (`component1.py` - XXX LOC)**
- Specific responsibility 1
- Input: [Input type]
- Output: [Output type]
- Dependencies: [List dependencies]

**Component 2 (`component2.py` - XXX LOC)**
- Specific responsibility 2
- Input: [Input type]
- Output: [Output type]
- Dependencies: [List dependencies]

### API Contracts (Public Interfaces)

```python
# Main orchestrator interface
class [OrchestratorName]Orchestrator(BaseOrchestrator):
    def execute(
        self, 
        tenant_id: str, 
        project_id: str, 
        user_id: str, 
        **kwargs
    ) -> OrchestratorResult:
        """Execute workflow with multi-tenant isolation."""
        pass
    
    def validate_dor(self, context: WorkflowContext) -> ValidationResult:
        """Validate Definition of Ready."""
        pass
    
    def validate_dod(self, context: WorkflowContext) -> ValidationResult:
        """Validate Definition of Done."""
        pass
```

### State Machine Integration

**FSM States:**
1. `INITIALIZED` - Orchestrator ready
2. `VALIDATING_DOR` - Checking prerequisites
3. `EXECUTING_PHASE_1` - First phase
4. `EXECUTING_PHASE_N` - Subsequent phases
5. `VALIDATING_DOD` - Checking completion criteria
6. `COMPLETED` - Workflow finished
7. `FAILED` - Error state

**Transitions:**
- `INITIALIZED → VALIDATING_DOR` (on execute)
- `VALIDATING_DOR → EXECUTING_PHASE_1` (DoR passed)
- `VALIDATING_DOR → FAILED` (DoR failed)
- `EXECUTING_PHASE_N → VALIDATING_DOD` (phases complete)
- `VALIDATING_DOD → COMPLETED` (DoD passed)
- `VALIDATING_DOD → FAILED` (DoD failed)

**Guard Conditions:**
- DoR gates: [List prerequisites]
- DoD gates: [List completion criteria]

### YAML Workflow Definition

**File:** `src/orchestration_3_0/workflows/[orchestrator-name]_workflow.yaml`

```yaml
workflow:
  name: "[Orchestrator Name] Workflow"
  version: "1.0.0"
  orchestrator: "[OrchestratorName]Orchestrator"
  
  phases:
    - id: "dor_validation"
      name: "Validate Definition of Ready"
      gates:
        - prerequisite_1
        - prerequisite_2
    
    - id: "phase_1"
      name: "Phase 1 Name"
      tasks:
        - task_1
        - task_2
    
    - id: "dod_validation"
      name: "Validate Definition of Done"
      gates:
        - completion_criterion_1
        - completion_criterion_2
```

---

## 3️⃣ Migration Strategy (5 Phases with TDD)

⚠️ **CRITICAL REQUIREMENT:** At the end of EVERY phase, you MUST update the **Master Planner Visual Tracker** in the master plan document before proceeding. Record completion status, metrics, and overall progress.

**Master Tracker Update Template:**
```markdown
### 📊 Master Planner Visual Tracker - [Sub-Plan Name]

**Started:** YYYY-MM-DD HH:MM:SS [Timezone]
**Last Updated:** YYYY-MM-DD HH:MM:SS [Timezone]
**Tokens Used:** [X,XXX] tokens

| Phase | Status | Duration | Files Modified | Tests | Tokens |
|-------|--------|----------|----------------|-------|--------|
| Phase 1: RED | ✅ COMPLETE | 2h 15m | 8 files | 45 tests | 3,200 |
| Phase 2: GREEN | 🔄 IN PROGRESS | 3h 45m ⏳ | 12 files | 45 pass | 5,300 |
| Phase 3: REFACTOR | ⏸️ PENDING | - | - | - | - |

**Overall Progress:** 40% complete (2/5 phases)
```

### Phase 1: RED (Tests First) - Week X, Day 1-2

**Objective:** Write comprehensive failing tests

**Integration Tests (XX tests):**
- [ ] Test end-to-end workflow (user trigger → completion)
- [ ] Test DoR validation (pass/fail scenarios)
- [ ] Test DoD validation (pass/fail scenarios)
- [ ] Test error handling and rollback
- [ ] Test multi-tenant isolation
- [ ] Test session persistence and recovery

**Unit Tests (XXX tests):**
- [ ] Test main orchestrator initialization
- [ ] Test each component in isolation
- [ ] Test state machine transitions
- [ ] Test DI container bindings
- [ ] Test RBAC enforcement

**Expected Result:** All tests RED (failing)

**Deliverable:** Test suite in `tests/orchestration_3_0/orchestrators/[orchestrator-name]/`

**🎯 CHECKPOINT:** Update Master Planner Visual Tracker with Phase 1 completion:
- Record status: ✅ Phase 1 RED - COMPLETE
- Add metrics: duration, tests created, tokens used
- Update overall progress percentage
- **Do NOT proceed to Phase 2 until master tracker is updated**

---

### Phase 2: GREEN (Core Implementation) - Week X, Day 3-5

**Objective:** Implement minimum viable orchestrator

**Implementation Tasks:**
- [ ] Create orchestrator folder structure
- [ ] Implement main orchestrator class (inherits BaseOrchestrator)
- [ ] Implement each component
- [ ] Register state machine states/transitions
- [ ] Register DI container bindings
- [ ] Create YAML workflow definition
- [ ] Implement session manager integration

**Expected Result:** All tests GREEN (passing)

**Deliverable:** Working orchestrator in `src/orchestration_3_0/orchestrators/[orchestrator-name]/`

**🎯 CHECKPOINT:** Update Master Planner Visual Tracker with Phase 2 completion:
- Record status: ✅ Phase 2 GREEN - COMPLETE
- Add metrics: duration, files created, tests passing, tokens used
- Update overall progress percentage
- **Do NOT proceed to Phase 3 until master tracker is updated**

---

### Phase 3: REFACTOR (Parallel Operation) - Week X, Day 6-7

**Objective:** Run old and new orchestrators in parallel, validate equivalence

**Parallel Testing:**
- [ ] Configure feature flag for A/B testing
- [ ] Run both orchestrators on sample workflows
- [ ] Compare outputs for equivalence
- [ ] Performance benchmarking (old vs new)
- [ ] Load testing (100 concurrent workflows)

**Equivalence Validation:**
- [ ] Output format matches old orchestrator
- [ ] All edge cases handled identically
- [ ] Error messages consistent
- [ ] Performance within 10% of old orchestrator

**Expected Result:** New orchestrator behavior matches old orchestrator 100%

**Deliverable:** Equivalence report in `cortex-brain/documents/reports/[orchestrator-name]-equivalence-report.md`

**🎯 CHECKPOINT:** Update Master Planner Visual Tracker with Phase 3 completion:
- Record status: ✅ Phase 3 REFACTOR - COMPLETE
- Add metrics: duration, equivalence %, performance delta, tokens used
- Update overall progress percentage
- **Do NOT proceed to Phase 4 until master tracker is updated**

---

### Phase 4: CUTOVER (Switch to New) - Week X+1, Day 1-3

**Objective:** Make new orchestrator production-default

**Cutover Tasks:**
- [ ] Update `cortex-operations.yaml` to route to new orchestrator
- [ ] Archive old orchestrator files to `cortex-brain/archives/orchestrators-legacy/[orchestrator-name]/`
- [ ] Create rollback script in `scripts/rollback/rollback_[orchestrator-name].py`
- [ ] Enable production monitoring (error rates, latency)
- [ ] Announce cutover to users (30-day grace period begins)

**Grace Period Monitoring (30 days):**
- [ ] Day 1-7: Monitor error rate (<0.1% target)
- [ ] Day 7-14: Collect user feedback
- [ ] Day 14-21: Address any issues
- [ ] Day 21-30: Final validation

**Expected Result:** Production stable, error rate <0.1%

**Deliverable:** Production monitoring dashboard

**🎯 CHECKPOINT:** Update Master Planner Visual Tracker with Phase 4 completion:
- Record status: ✅ Phase 4 CUTOVER - COMPLETE
- Add metrics: duration, cutover time, production error rate, tokens used
- Update overall progress percentage
- **Do NOT proceed to Phase 5 until master tracker is updated**

---

### Phase 5: CLEANUP (Remove Old) - Week X+5

**Objective:** Permanently delete old orchestrator

**Cleanup Tasks:**
- [ ] Grace period expired (30 days)
- [ ] No rollback requests
- [ ] Error rate stable (<0.1%)
- [ ] Delete archived orchestrator files
- [ ] Delete rollback scripts
- [ ] Update documentation (remove old orchestrator references)

**Expected Result:** Legacy code permanently removed

**Deliverable:** Cleanup report in `cortex-brain/documents/reports/[orchestrator-name]-cleanup-report.md`

**🎯 FINAL CHECKPOINT:** Update Master Planner Visual Tracker with Phase 5 completion:
- Record status: ✅ Phase 5 CLEANUP - COMPLETE ✨
- Add metrics: total duration, total tokens used, final file count
- Mark overall progress: 100% COMPLETE 🎉
- **ALL PHASES COMPLETE - Update master plan with final summary**

---

## 4️⃣ Test Coverage Requirements

### Unit Tests (XXX tests - 100% coverage)

| Component | Tests | Coverage Target | Purpose |
|-----------|-------|-----------------|---------|
| Main Orchestrator | XX | 100% | All public methods |
| Component 1 | XX | 100% | Isolated component logic |
| Component 2 | XX | 100% | Isolated component logic |
| Component 3 | XX | 100% | Isolated component logic |
| State Machine Integration | XX | 100% | All state transitions |
| DI Container Bindings | XX | 100% | All dependencies resolved |

### Integration Tests (XX tests - 95% coverage)

| Scenario | Tests | Purpose |
|----------|-------|---------|
| End-to-End Workflow | XX | Full user journey |
| DoR Validation | XX | Gate enforcement |
| DoD Validation | XX | Completion criteria |
| Error Handling | XX | Rollback and recovery |
| Multi-Tenant Isolation | XX | Tenant data separation |
| Session Persistence | XX | Crash recovery |

### Migration Tests (XX tests - 100% legacy behavior)

| Legacy Behavior | Tests | Purpose |
|-----------------|-------|---------|
| Legacy Workflow 1 | XX | Preserve original behavior |
| Legacy Workflow 2 | XX | Preserve original behavior |
| Legacy Edge Case 1 | XX | Handle corner cases |
| Legacy Edge Case 2 | XX | Handle corner cases |

### Performance Tests (X tests)

| Scenario | Target | Purpose |
|----------|--------|---------|
| Single Workflow | <Xs | Latency benchmark |
| 100 Concurrent Workflows | <XXs | Throughput benchmark |
| Large Input (10k items) | <XXs | Scalability benchmark |
| Memory Usage | <XXX MB | Resource efficiency |

### Total Test Count

**Total:** XXX unit + XX integration + XX migration + X performance = **XXX tests**

---

## 5️⃣ Wiring Validation Checklist

**Before cutover, ALL items MUST be checked:**

- [ ] **State Machine Transitions Registered**
  - All FSM states defined in `state_machine.py`
  - All transitions with guard conditions
  - Recovery states for error handling

- [ ] **DI Container Bindings Configured**
  - Main orchestrator registered
  - All components registered
  - Dependencies auto-wired
  - Lifecycle management (singleton/transient)

- [ ] **cortex-operations.yaml Updated**
  - Natural language triggers added
  - CLI commands mapped
  - API endpoints configured
  - Execution method specified (`copilot_chat` or `cli_wrapper`)

- [ ] **YAML Workflow Definition Created**
  - File created in `src/orchestration_3_0/workflows/`
  - JSON Schema validated
  - Phases and tasks defined
  - DoR/DoD gates specified

- [ ] **Session Manager Integration Complete**
  - Session creation on workflow start
  - Checkpoint creation after each phase
  - Recovery from interruption tested
  - Session history tracked

- [ ] **Multi-Tenant Isolation Verified**
  - Tenant ID required for all operations
  - Project ID scoped correctly
  - User ID for RBAC enforcement
  - Cross-tenant data leakage prevented

- [ ] **RBAC Permissions Configured**
  - Role definitions created
  - Permission matrix defined
  - Authorization checks at entry points
  - Audit trail for access attempts

- [ ] **Logging and Monitoring Instrumented**
  - Structured logging (JSON format)
  - Performance metrics tracked
  - Error tracking integrated
  - Dashboards configured

- [ ] **Error Handling and Rollback Tested**
  - Exception handling at all levels
  - Graceful degradation
  - Rollback scripts functional
  - User-friendly error messages

- [ ] **Documentation Generated**
  - API documentation (method signatures)
  - Workflow documentation (Mermaid diagrams)
  - User guide (how to invoke)
  - Troubleshooting guide

---

## 6️⃣ Complete Removal Strategy

### Archive Location

```
cortex-brain/archives/orchestrators-legacy/[orchestrator-name]/
├── [file1].py
├── [file2].py
└── README.md  # Context about archived files
```

### Grace Period Timeline

| Week | Activities | Validation |
|------|------------|------------|
| **Week 1-2** | Archive old files | Files moved to archive/ |
| **Week 2** | Update all imports | No import errors |
| **Week 2-4** | Run full test suite (2,300+ tests) | All tests pass |
| **Week 3-4** | Production monitoring | Error rate <0.1% |
| **Week 4** | User feedback collection | No blockers reported |
| **Week 5** | Final validation checks | System stable |

### Rollback Script

**File:** `scripts/rollback/rollback_[orchestrator-name].py`

```python
"""
Rollback script for [Orchestrator Name]
Restores archived orchestrator if issues found during grace period.
"""

def rollback():
    # Restore archived files
    # Revert cortex-operations.yaml changes
    # Update imports
    # Restart services
    pass
```

### Deletion Checklist

- ✅ **Week 1-2:** Archive to `cortex-brain/archives/orchestrators-legacy/`
- ✅ **Week 2:** Update all imports to new orchestrator
- ✅ **Week 2-4:** Run full test suite (2,300+ tests)
- ✅ **Week 3-4:** Monitor production (error rate <0.1%)
- ✅ **Week 4:** User feedback collection
- ✅ **Grace period end:** Final validation checks
- ❌ **Permanent deletion:** Remove from archive, delete rollback scripts

### Safety Mechanisms

- **Rollback Available:** During entire grace period (30 days)
- **Emergency Recovery:** Restore from archive if critical issues
- **Production Monitoring:** Real-time error tracking
- **User Communication:** Email notification before deletion
- **Phased Approach:** One orchestrator at a time (not batch deletion)

---

## 📊 Summary

**Current State:**
- Y files with X,XXX total LOC
- Fragmented, hard-coded, single-project

**New State:**
- 1 unified orchestrator with XXX LOC
- State machine-based, DI container, multi-tenant

**Migration Effort:**
- X weeks (5 phases)
- XXX tests (unit + integration + migration + performance)
- 30-day grace period
- 100% backward compatibility

**Success Criteria:**
- ✅ All tests pass (XXX tests)
- ✅ Production error rate <0.1%
- ✅ Performance within 10% of old orchestrator
- ✅ User feedback positive (no blockers)
- ✅ 30-day grace period completed without rollback

---

## 📞 Contact & Resources

**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX  
**Branch:** `cortex3-orchestration`

**Related Documents:**
- [Master Plan](../orchestration-master-plan.md)
- [State Machine Design](../../architecture/state-machine-design.md)
- [DI Container Design](../../architecture/di-container-design.md)
- [Multi-Tenant Architecture](../../architecture/multi-tenant-architecture.md)

---

**Next Step:** Review this sub-plan, approve approach, begin Phase 1 (RED).
