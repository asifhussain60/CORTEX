# 🛡️ TDD Orchestrator v2 Migration Plan

**Plan ID:** tdd-v2-migration  
**Feature:** Convert TDD Orchestrator from GUIDED to AUTONOMOUS (Phase 6.5)  
**Created:** January 3, 2026  
**Based On:** Phase 6.4 GUIDED Orchestrators Assessment (Decision Score: 8.85/10)  
**Complexity:** TIER 3 (ORCHESTRATOR MIGRATION)  
**Duration:** 4 days  
**Status:** ✅ APPROVED (January 2, 2026)

---

## 📊 Visual Progress Tracker

**Overall Progress:** `░░░░░░░░░░░░░░░░░░░░` **0%** 📋 NOT STARTED

| Day | Focus | Progress | Status |
|-----|-------|----------|--------|
| 1 | Core TDDOrchestratorV2 + TestRunnerAbstraction | `░░░░░░░░░░` | 📋 Not Started |
| 2 | RED Phase Automation | `░░░░░░░░░░` | 📋 Not Started |
| 3 | GREEN Phase Automation | `░░░░░░░░░░` | 📋 Not Started |
| 4 | REFACTOR Phase + Integration | `░░░░░░░░░░` | 📋 Not Started |

---

## 🎯 Response Template Reference

**Orchestrator Type:** 🛡️ AUTONOMOUS (target state)  
**Template:** `response-templates-v4.yaml:863` (autonomous_execution_progress)  
**Current State:** 📋 GUIDED (tdd-orchestrator-v4-manifest.yaml)  
**Migration Goal:** Convert to AUTONOMOUS with BaseOrchestrator v4.1

---

## 🤖 Copilot Instructions

```yaml
copilot_instructions:
  # Response template
  response_template: "autonomous_execution_progress"
  template_reference: "response-templates-v4.yaml:863"
  
  # SKULL enforcement
  tdd_enforcement: true
  tdd_cycle_required: "RED→GREEN→REFACTOR"
  
  # REFACTOR requirements
  final_refactor_required: true
  refactor_scope: "whole_file_cleanup"
  
  # Testing
  test_coverage_required: 100
  test_framework: "pytest"
```

---

## 📋 Executive Summary

### Decision Rationale (From Phase 6.4 Assessment)

**Decision Score:** 8.85/10 → ✅ **AUTONOMOUS MIGRATION APPROVED**

**Scoring Breakdown:**
1. **Workflow Complexity:** 10/10 - Complex RED→GREEN→REFACTOR cycle requires transactional state
2. **User Interaction:** 6/10 - Primarily automated with optional intervention points
3. **Reusable Components:** 9/10 - TestRunnerAbstraction benefits Debug/Sanitization/Refinement
4. **Integration Dependencies:** 10/10 - Master Orchestrator, Git Checkpoint, State DB integration
5. **State Management:** 10/10 - Multi-phase state machine with rollback/checkpointing

**Key Strengths:**
- Complex state machine ideal for autonomous implementation
- Clear phase boundaries (RED → GREEN → REFACTOR)
- High reusability (TestRunnerAbstraction, test execution patterns)
- Strong Master Orchestrator integration potential
- Transactional state enables rollback on failure

**Priority:** 🔴 **HIGH** - Week 1 of 3-week migration roadmap

---

## 🏗️ Architecture Overview

### Current State (GUIDED)
```
User: "start tdd for auth module"
  ↓
CORTEX reads tdd-orchestrator-v4-manifest.yaml
  ↓
CORTEX executes TDD workflow instructions
  ↓
Manual step-by-step guidance (RED → GREEN → REFACTOR)
```

### Target State (AUTONOMOUS)
```
User: "start tdd for auth module"
  ↓
GitHub Copilot → run_in_terminal
  ↓
scripts/cortex-cli.py tdd_orchestrator_v2 "start tdd for auth module"
  ↓
TDDOrchestratorV2 (Python class, extends BaseOrchestrator v4.1)
  ↓
Autonomous execution: RED → GREEN → REFACTOR
  ↓
State DB persistence, Git checkpointing, Master Orchestrator coordination
```

---

## 📦 Key Components

### 1. TDDOrchestratorV2 (Core)
**File:** `src/orchestrators/tdd/tdd_orchestrator_v2.py`  
**Extends:** `BaseOrchestrator v4.1`  
**Lines:** ~800 (estimated)

**Responsibilities:**
- RED phase: Execute tests, detect failures, record baseline
- GREEN phase: Verify test pass, create checkpoint
- REFACTOR phase: Code quality checks, atomic rollback
- State persistence via Planning State DB
- Git checkpoint integration
- Master Orchestrator coordination

### 2. TestRunnerAbstraction (Reusable)
**File:** `src/orchestrators/tdd/test_runner_abstraction.py`  
**Lines:** ~400 (estimated)

**Responsibilities:**
- Unified interface for pytest, unittest, nose
- Test discovery and execution
- Coverage tracking
- Failure parsing and categorization
- Performance metrics

**Reusability:**
- Debug Orchestrator v2 (test execution for bug verification)
- Sanitization Orchestrator v2 (test suite validation)
- Refinement Orchestrator (regression testing)

### 3. State Machine
**Phases:**
1. **INIT:** Parse user request, identify test scope
2. **RED:** Execute tests, expect failures, record baseline
3. **GREEN:** Implement minimal code, verify test pass
4. **REFACTOR:** Quality checks, optimization, maintain green state
5. **CHECKPOINT:** Git commit, state persistence
6. **COMPLETE:** Summary report, continuation prompt

**Transitions:**
- RED → GREEN: All target tests failing as expected
- GREEN → REFACTOR: All tests passing
- REFACTOR → CHECKPOINT: Quality checks pass, tests still green
- REFACTOR → GREEN: Quality check failed, rollback, retry
- Any → ABORT: Unrecoverable error, rollback to last checkpoint

---

## 🎯 Success Criteria

### Functional Requirements
- ✅ RED→GREEN→REFACTOR cycle fully automated
- ✅ Test framework abstraction (pytest/unittest/nose support)
- ✅ Automatic test discovery from user request
- ✅ Failure detection and categorization
- ✅ Atomic rollback on REFACTOR failure
- ✅ Git checkpoint creation on GREEN/REFACTOR success
- ✅ State persistence across sessions
- ✅ Master Orchestrator routing integration

### Non-Functional Requirements
- ✅ Test execution < 5 seconds (performance benchmark)
- ✅ 100% test coverage for TDDOrchestratorV2
- ✅ TestRunnerAbstraction reusable by 3+ orchestrators
- ✅ State DB schema compatible with BaseOrchestrator v4.1
- ✅ MCP registration in `mcp-server.yaml`
- ✅ CLI bridge invocation tested

### Quality Requirements
- ✅ Zero orphaned test files after execution
- ✅ Comprehensive error handling (network, file I/O, test framework)
- ✅ Rollback completeness (no partial state)
- ✅ Continuation prompt generation for multi-session work
- ✅ SKULL rules enforced (TDD_ENFORCEMENT, HOLISTIC_DISCOVERY, REFACTOR_CLEANUP)

---

## 📅 4-Day Implementation Plan

### Day 1: Core TDDOrchestratorV2 + TestRunnerAbstraction (8 hours)

**Morning (4h): Scaffolding**
- [ ] Create `src/orchestrators/tdd/` directory structure
- [ ] Implement `TDDOrchestratorV2` class extending `BaseOrchestrator v4.1`
- [ ] Define phase enum (`RED`, `GREEN`, `REFACTOR`, `CHECKPOINT`, `COMPLETE`)
- [ ] Implement `execute()` method with state machine dispatcher
- [ ] Connect to Planning State DB

**Afternoon (4h): TestRunnerAbstraction**
- [ ] Create `TestRunnerAbstraction` base class
- [ ] Implement `PytestAdapter` (primary framework)
- [ ] Implement `UnittestAdapter` (secondary framework)
- [ ] Test discovery logic (file patterns, naming conventions)
- [ ] Basic test execution (run, capture output, parse results)

**Deliverables:**
- `tdd_orchestrator_v2.py` (scaffolding, ~200 lines)
- `test_runner_abstraction.py` (base + 2 adapters, ~300 lines)
- Unit tests for adapters (50+ tests)

**Exit Criteria:**
- TDDOrchestratorV2 instantiates successfully
- TestRunnerAbstraction can execute pytest/unittest tests
- State DB connection established

---

### Day 2: RED Phase Automation (8 hours)

**Morning (4h): Test Failure Detection**
- [ ] Implement `execute_red_phase()` method
- [ ] Test discovery from user request (e.g., "test auth module" → `tests/test_auth.py`)
- [ ] Execute tests, capture failures
- [ ] Categorize failure types (assertion, exception, timeout, syntax error)
- [ ] Record baseline state (which tests should fail)

**Afternoon (4h): State Persistence & Validation**
- [ ] Persist RED phase state to Planning State DB
- [ ] Validate expected failures (user-defined vs actual)
- [ ] Handle edge cases (no tests found, all tests passing unexpectedly)
- [ ] Implement RED → GREEN transition logic
- [ ] Error handling and rollback

**Deliverables:**
- `execute_red_phase()` implementation (~150 lines)
- RED phase state schema in State DB
- Unit tests for RED phase (30+ tests)
- Edge case handling (no tests, unexpected pass)

**Exit Criteria:**
- RED phase executes tests and detects failures
- Failure baseline recorded in State DB
- Transition to GREEN phase triggered correctly

---

### Day 3: GREEN Phase Automation (8 hours)

**Morning (4h): Test Pass Verification**
- [ ] Implement `execute_green_phase()` method
- [ ] Re-execute tests from RED phase
- [ ] Verify all previously-failing tests now pass
- [ ] Detect new failures (regressions)
- [ ] Calculate code coverage (via pytest-cov)

**Afternoon (4h): Checkpoint Creation**
- [ ] Git checkpoint creation on GREEN success
- [ ] State DB update with GREEN phase results
- [ ] Coverage report generation
- [ ] Implement GREEN → REFACTOR transition
- [ ] Handle partial success (some tests still failing)

**Deliverables:**
- `execute_green_phase()` implementation (~150 lines)
- Git checkpoint integration
- Coverage tracking
- Unit tests for GREEN phase (30+ tests)

**Exit Criteria:**
- GREEN phase verifies test pass
- Git checkpoint created on success
- Coverage metrics recorded
- Transition to REFACTOR phase triggered

---

### Day 4: REFACTOR Phase + Integration (8 hours)

**Morning (4h): REFACTOR Phase**
- [ ] Implement `execute_refactor_phase()` method
- [ ] Code quality checks (pylint, mypy, complexity analysis)
- [ ] Re-run tests to ensure green state maintained
- [ ] Atomic rollback on quality check failure
- [ ] Git checkpoint on REFACTOR success

**Afternoon (4h): Master Orchestrator Integration**
- [ ] Register TDDOrchestratorV2 in `mcp-server.yaml`
- [ ] Update Master Orchestrator routing config
- [ ] Test CLI bridge invocation: `python3 scripts/cortex-cli.py tdd_orchestrator_v2 "test auth"`
- [ ] Create continuation prompt template
- [ ] 100% test coverage validation
- [ ] Integration tests (end-to-end RED→GREEN→REFACTOR)

**Deliverables:**
- `execute_refactor_phase()` implementation (~150 lines)
- MCP server registration
- Master Orchestrator routing
- CLI bridge integration tests
- Continuation prompt template
- Complete test suite (100% coverage)

**Exit Criteria:**
- REFACTOR phase enforces quality checks
- Atomic rollback functional
- CLI bridge invocation works end-to-end
- Master Orchestrator routes TDD commands
- 100% test coverage achieved

---

## 🔗 Integration Points

### 1. BaseOrchestrator v4.1
**Connection:** TDDOrchestratorV2 extends BaseOrchestrator v4.1  
**Inherited:**
- `execute_phase()` method (state machine dispatcher)
- Pattern router integration
- State manager connection
- Execution engine coordination
- Error handling framework

### 2. Planning State DB
**Connection:** TDD state persistence  
**Schema:**
```sql
CREATE TABLE tdd_sessions (
  session_id TEXT PRIMARY KEY,
  orchestrator_id TEXT,
  phase TEXT,  -- RED, GREEN, REFACTOR, CHECKPOINT, COMPLETE
  test_scope TEXT,  -- e.g., "tests/test_auth.py"
  baseline_failures TEXT,  -- JSON array of expected failures
  current_state TEXT,  -- JSON object with phase-specific data
  git_checkpoint TEXT,  -- Last checkpoint commit hash
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### 3. Master Orchestrator
**Connection:** Command routing  
**Routing Rules:**
- `start tdd [scope]` → `tdd_orchestrator_v2`
- `run tests [scope]` → `tdd_orchestrator_v2`
- `continue tdd` → `tdd_orchestrator_v2` (with session context)

### 4. Git Checkpoint Orchestrator
**Connection:** Checkpoint creation  
**Protocol:**
- GREEN phase success → Create checkpoint with message "TDD: GREEN phase - tests passing"
- REFACTOR phase success → Create checkpoint with message "TDD: REFACTOR phase - code quality improved"

### 5. MCP Server
**Registration:** `cortex-brain/config/mcp-server.yaml`
```yaml
tdd_orchestrator_v2:
  class: "TDDOrchestratorV2"
  module: "src.orchestrators.tdd.tdd_orchestrator_v2"
  config: "cortex-brain/manifests/orchestrators/tdd-orchestrator-v2.yaml"
  type: "autonomous"
  description: "Test-Driven Development orchestrator with RED-GREEN-REFACTOR automation"
```

---

## 🧪 Testing Strategy

### Unit Tests (Target: 100% coverage)
**File:** `tests/orchestrators/tdd/test_tdd_orchestrator_v2.py`

**Test Categories:**
1. **Initialization Tests** (10 tests)
   - Orchestrator instantiation
   - State DB connection
   - TestRunnerAbstraction initialization

2. **RED Phase Tests** (15 tests)
   - Test discovery (various patterns)
   - Failure detection (assertion, exception, timeout)
   - Baseline recording
   - Edge cases (no tests, unexpected pass)

3. **GREEN Phase Tests** (15 tests)
   - Test pass verification
   - Regression detection
   - Coverage tracking
   - Git checkpoint creation

4. **REFACTOR Phase Tests** (15 tests)
   - Quality checks (pylint, mypy)
   - Atomic rollback
   - Green state maintenance
   - Git checkpoint on success

5. **State Machine Tests** (10 tests)
   - Phase transitions (RED→GREEN, GREEN→REFACTOR)
   - Rollback scenarios
   - Error recovery
   - Session persistence

6. **Integration Tests** (15 tests)
   - End-to-end RED→GREEN→REFACTOR workflow
   - Master Orchestrator routing
   - CLI bridge invocation
   - Multi-session continuation

**Total:** 80+ unit tests

### TestRunnerAbstraction Tests
**File:** `tests/orchestrators/tdd/test_test_runner_abstraction.py`

**Test Categories:**
1. **Pytest Adapter Tests** (20 tests)
2. **Unittest Adapter Tests** (20 tests)
3. **Test Discovery Tests** (10 tests)
4. **Coverage Tracking Tests** (5 tests)
5. **Error Handling Tests** (10 tests)

**Total:** 65+ unit tests

---

## 📊 Reusability Impact

### TestRunnerAbstraction Benefits

**Orchestrators That Will Use It:**
1. **Debug Orchestrator v2** (Phase 6.6)
   - Test execution for bug verification
   - Regression testing after fix

2. **Sanitization Orchestrator v2** (Phase 6.7)
   - Test suite validation post-sanitization
   - Ensure sanitized code still passes tests

3. **Refinement Orchestrator** (Phase 6.8)
   - Regression testing after refactoring
   - Performance benchmarking

**Estimated Reuse:**
- 400 lines of TestRunnerAbstraction code
- 65 unit tests
- Saves ~2 days of development across 3 orchestrators

---

## 🛡️ SKULL Rules Compliance

### TDD_ENFORCEMENT
- ✅ RED→GREEN→REFACTOR cycle mandatory
- ✅ Tests must fail before implementation (RED phase validation)
- ✅ Tests must pass before refactoring (GREEN phase gate)
- ✅ Atomic rollback enforced on REFACTOR failure

### HOLISTIC_DISCOVERY
- ✅ Test file discovery before creation (prevent duplication)
- ✅ Search for existing test patterns
- ✅ Reuse TestRunnerAbstraction across orchestrators

### REFACTOR_CLEANUP
- ✅ REFACTOR phase removes unused imports, dead code
- ✅ Quality checks enforce code standards
- ✅ Whole-file cleanup on completion

### GIT_ISOLATION
- ✅ TDD commits isolated to feature branch
- ✅ Checkpoint messages clearly labeled "TDD: [phase]"

### AUTONOMOUS_EXECUTION_PROTECTION
- ✅ TDDOrchestratorV2 invoked via CLI bridge only
- ✅ CORTEX cannot execute Python directly
- ✅ Enforced by MCP architecture

---

## 📈 Success Metrics

### Performance Benchmarks
- **Test Execution:** < 5 seconds (95th percentile)
- **Phase Transition:** < 500ms overhead
- **State DB Write:** < 100ms
- **Git Checkpoint:** < 2 seconds

### Quality Metrics
- **Test Coverage:** 100% (TDDOrchestratorV2 + TestRunnerAbstraction)
- **Code Quality:** Pylint score > 9.0, Mypy strict mode pass
- **Reusability:** TestRunnerAbstraction used by 3+ orchestrators

### Adoption Metrics
- **CLI Bridge Invocation:** Successful on first attempt
- **Master Orchestrator Routing:** 100% accuracy
- **Error Rate:** < 1% (unrecoverable errors)

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All unit tests passing (100% coverage)
- [ ] Integration tests passing (end-to-end workflow)
- [ ] MCP server registration complete
- [ ] Master Orchestrator routing configured
- [ ] CLI bridge invocation tested

### Deployment
- [ ] Commit TDDOrchestratorV2 implementation
- [ ] Commit TestRunnerAbstraction
- [ ] Update MCP server config
- [ ] Update Master Orchestrator routing
- [ ] Create migration completion report

### Post-Deployment
- [ ] Test CLI bridge: `python3 scripts/cortex-cli.py tdd_orchestrator_v2 "test auth"`
- [ ] Verify Master Orchestrator routing
- [ ] Test continuation prompt workflow
- [ ] Update Phase 6.5 progress in master plan
- [ ] Begin Phase 6.6 (Debug Orchestrator v2)

---

## 🔄 Continuation Protocol

### Multi-Session Support
**User:** "continue tdd"

**CORTEX Action:**
1. Detect continuation pattern
2. Query Tier 1 for last TDD session
3. Load session state from Planning State DB
4. Resume at last completed phase + 1
5. Display progress: "Resuming TDD session [session_id], Phase [X], [N] tests"

**Context Injected:**
```json
{
  "session_id": "tdd-session-20260103-143000",
  "orchestrator": "tdd_orchestrator_v2",
  "current_phase": "GREEN",
  "test_scope": "tests/test_auth.py",
  "baseline_failures": ["test_login_invalid_password", "test_login_missing_username"],
  "last_checkpoint": "abc123def",
  "continuation_detected": true
}
```

---

## 📝 Documentation Requirements

### User-Facing Documentation
1. **TDD v2 Usage Guide** (`docs/orchestrators/tdd-orchestrator-v2.md`)
   - Command patterns
   - RED→GREEN→REFACTOR workflow explanation
   - Continuation workflow
   - Troubleshooting

2. **CLI Bridge Examples** (`.github/prompts/CORTEX.prompt.md`)
   - Add TDD v2 invocation examples
   - Update Intent Router table

### Developer Documentation
1. **TestRunnerAbstraction API** (`src/orchestrators/tdd/README.md`)
   - Interface documentation
   - Adapter implementation guide
   - Reusability examples

2. **State Schema Documentation** (`cortex-brain/database/schemas/tdd-state-schema.md`)
   - Table structure
   - State transitions
   - Query patterns

---

## ⚠️ Risks & Mitigation

### Risk 1: Test Framework Compatibility
**Description:** pytest/unittest behavior differences cause adapter issues  
**Probability:** MEDIUM  
**Impact:** MEDIUM  
**Mitigation:** 
- Comprehensive adapter testing (65+ tests)
- Fallback to pytest as primary framework
- Document framework-specific limitations

### Risk 2: State Machine Complexity
**Description:** Phase transitions have edge cases causing incorrect state  
**Probability:** MEDIUM  
**Impact:** HIGH  
**Mitigation:**
- State machine tests (10+ transition tests)
- Atomic rollback on any error
- State DB audit trail for debugging

### Risk 3: Performance (Test Execution)
**Description:** Large test suites exceed 5-second benchmark  
**Probability:** LOW  
**Impact:** MEDIUM  
**Mitigation:**
- Parallel test execution (pytest -n auto)
- Selective test execution (only changed files)
- Performance profiling during Day 3

### Risk 4: Git Checkpoint Conflicts
**Description:** Concurrent TDD sessions create merge conflicts  
**Probability:** LOW  
**Impact:** LOW  
**Mitigation:**
- Session isolation (separate branches)
- Checkpoint naming convention (session ID in commit message)
- Conflict detection and user notification

---

## 📅 Next Steps After Completion

### Immediate (Day 5)
1. **Create Migration Completion Report**
   - Document lessons learned
   - Performance metrics
   - Reusability validation

2. **Update Master Plan Progress**
   - Mark Phase 6.5 complete
   - Update progress tracker (53% → 60%)

3. **Begin Phase 6.6 Planning**
   - Generate Debug Orchestrator v2 migration plan
   - Leverage TestRunnerAbstraction patterns

### Short-Term (Week 2)
- **Phase 6.6:** Debug Orchestrator v2 Migration (3 days)
- TestRunnerAbstraction reuse validation

### Long-Term (Week 3+)
- **Phase 6.7:** Sanitization Orchestrator v2 Migration (2 days)
- **Phase 6.8:** Refinement Enhancements (4 hours)
- Phase 7: System Integration (2 days)

---

## ✅ Approval Record

**Decision Date:** January 2, 2026  
**Decision Score:** 8.85/10  
**Decision:** ✅ AUTONOMOUS MIGRATION APPROVED  
**Authority:** Phase 6.4 GUIDED Orchestrators Assessment  
**Priority:** 🔴 HIGH (Week 1 of migration roadmap)

**Stakeholder Sign-Off:**
- [x] Assessment complete (Phase 6.4)
- [x] Decision matrix applied (8.85/10 > 7.0 threshold)
- [x] Strategic recommendations documented
- [x] Resource allocation approved (4 days, Week 1)

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
