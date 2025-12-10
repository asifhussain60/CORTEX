# TDD Orchestrator Sub-Plan

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** December 10, 2025  
**Status:** 📋 READY FOR IMPLEMENTATION

---

## 📋 Navigation

- **Master Plan:** [orchestration-master-plan.md](../orchestration-master-plan.md)
- **Previous:** [Core Infrastructure Complete](../../reports/phase-1-core-infrastructure-complete.md)
- **Next:** [DevOps Orchestrator Plan](02-devops-orchestrator-plan.md)
- **Workflow YAML:** `src/orchestration_3_0/workflows/tdd_workflow.yaml`

---

## 1️⃣ Existing State (Summarized)

### Current Files Being Consolidated

| File | LOC | Purpose | Key Components |
|------|-----|---------|----------------|
| `src/orchestrators/tdd_implementation_orchestrator.py` | 2,291 | RED→GREEN→REFACTOR workflow | State machine, session tracking, git checkpoints, pattern learning |
| `src/workflows/tdd_workflow_orchestrator.py` | 1,232 | Unified TDD API | Test generation, refactoring intelligence, vision API integration |
| `src/workflows/tdd_workflow_integrator.py` | ~300 | Phase coordination | Test execution, workspace context |
| `src/workflows/tdd_workflow.py` | ~200 | Core workflow logic | Phase transitions, validation |

**Total LOC:** 4,023 lines across 4 files  
**Target LOC:** 2,000 lines (50% reduction through consolidation)

### Current Workflow (High-Level Steps)

1. **User Trigger:** `start tdd`, `run tests`, `@cortex implement TDD`
2. **Session Creation:** Initialize TDD session with feature name, task ID
3. **RED Phase:** Generate failing tests, validate test failures
4. **GREEN Phase:** Implement minimal code to pass tests
5. **REFACTOR Phase:** Clean code, detect duplicates, apply SOLID principles
6. **Git Checkpoint:** Automatic checkpoints at phase boundaries
7. **Pattern Learning:** Store refactoring preferences in Tier 2 knowledge graph
8. **Metrics:** Real-time dashboard updates

### Current Triggers

- **Natural Language:** `"start TDD"`, `"run tests"`, `"RED phase"`, `"implement tests"`
- **CLI Command:** `cortex tdd start`, `cortex tdd phase RED`
- **Copilot Command:** `@cortex start tdd`, `@cortex tdd workflow`

### Current Issues & Pain Points

**Fragmentation:**
- 4 separate files doing overlapping work
- Duplicated session tracking (tdd_implementation has own sessions, tdd_workflow uses Tier 1 sessions)
- No shared state machine across files
- Vision API only in one file, not accessible to others

**Reliability:**
- Workflow completion rate: ~75%
- Phases skipped: ~15% (users can bypass RED validation)
- Manual git checkpoints (sometimes forgotten)
- No recovery from crashes (session state lost)

**Technical Debt:**
- Hard-coded project paths
- No dependency injection (direct imports)
- No multi-tenant support (single-project focus)
- No session persistence (in-memory only)
- Mixed responsibilities (test generation + execution + refactoring in same class)

**Scalability:**
- Cannot run TDD workflows across multiple projects simultaneously
- No RBAC (anyone can trigger any phase)
- No cross-project test reuse

---

## 2️⃣ New Structure

### Target Architecture

```
src/orchestration_3_0/orchestrators/tdd/
├── __init__.py
├── tdd_orchestrator.py              # Main orchestrator (500 LOC)
├── test_generator.py                # Test generation engine (400 LOC)
├── implementation_engine.py         # GREEN phase minimal implementation (300 LOC)
├── refactoring_engine.py            # REFACTOR phase intelligence (400 LOC)
├── phase_validator.py               # DoR/DoD validation for each phase (200 LOC)
└── metrics_collector.py             # Real-time TDD metrics (200 LOC)
```

**Total Target LOC:** 2,000 lines (50% reduction)

### Component Responsibilities

**Main Orchestrator (`tdd_orchestrator.py` - 500 LOC)**
- Extends `BaseOrchestrator`
- State machine integration (RED→GREEN→REFACTOR)
- DI container registration
- Multi-tenant session management
- Git checkpoint coordination
- DoR/DoD validation hooks

**Test Generator (`test_generator.py` - 400 LOC)**
- Edge case analysis
- Error condition generation
- Parametrized test generation
- Domain knowledge integration
- Vision API screenshot parsing
- Test template management
- Dependencies: `FunctionTestGenerator`, `EdgeCaseAnalyzer`, `DomainKnowledgeIntegrator`

**Implementation Engine (`implementation_engine.py` - 300 LOC)**
- Minimal code generation (GREEN phase)
- AST manipulation for code insertion
- Test-to-implementation mapping
- Dependencies: `ast`, `CodeSmellDetector`

**Refactoring Engine (`refactoring_engine.py` - 400 LOC)**
- Code smell detection
- Duplicate code analysis
- SOLID principle validation
- Refactoring suggestions
- Pattern learning integration (Tier 2)
- Dependencies: `RefactoringEngine`, `CodeSmellDetector`, `KnowledgeGraph`

**Phase Validator (`phase_validator.py` - 200 LOC)**
- RED phase DoR: No tests exist, feature scope defined
- RED phase DoD: Tests written, tests fail as expected
- GREEN phase DoR: RED phase complete, tests failing
- GREEN phase DoD: All tests pass, minimal implementation
- REFACTOR phase DoR: GREEN phase complete, tests passing
- REFACTOR phase DoD: Code clean, no smells, tests still passing

**Metrics Collector (`metrics_collector.py` - 200 LOC)**
- Test coverage per layer
- Phase completion times
- Code smell counts
- Refactoring impact metrics
- Dependencies: `TestExecutionManager`, `WorkspaceContextManager`

---

## 3️⃣ State Machine Workflow

### TDD State Machine (7 States)

```yaml
states:
  - INITIALIZED
  - RED_VALIDATING_DOR
  - RED_EXECUTING
  - RED_VALIDATING_DOD
  - GREEN_VALIDATING_DOR
  - GREEN_EXECUTING
  - GREEN_VALIDATING_DOD
  - REFACTOR_VALIDATING_DOR
  - REFACTOR_EXECUTING
  - REFACTOR_VALIDATING_DOD
  - COMPLETED
  - FAILED

transitions:
  - from: INITIALIZED
    to: RED_VALIDATING_DOR
    guard: [feature_scope_defined]
    actions: [create_session, log_start]
  
  - from: RED_VALIDATING_DOR
    to: RED_EXECUTING
    guard: [no_existing_tests, scope_approved]
    actions: [checkpoint_git]
  
  - from: RED_EXECUTING
    to: RED_VALIDATING_DOD
    guard: [tests_generated]
    actions: [run_tests]
  
  - from: RED_VALIDATING_DOD
    to: GREEN_VALIDATING_DOR
    guard: [tests_fail_correctly]
    actions: [checkpoint_git, update_metrics]
  
  - from: GREEN_VALIDATING_DOR
    to: GREEN_EXECUTING
    guard: [tests_still_failing, red_phase_complete]
    actions: [analyze_tests]
  
  - from: GREEN_EXECUTING
    to: GREEN_VALIDATING_DOD
    guard: [implementation_complete]
    actions: [run_tests]
  
  - from: GREEN_VALIDATING_DOD
    to: REFACTOR_VALIDATING_DOR
    guard: [all_tests_pass, minimal_implementation]
    actions: [checkpoint_git, update_metrics]
  
  - from: REFACTOR_VALIDATING_DOR
    to: REFACTOR_EXECUTING
    guard: [tests_passing, green_phase_complete]
    actions: [scan_code_smells]
  
  - from: REFACTOR_EXECUTING
    to: REFACTOR_VALIDATING_DOD
    guard: [refactoring_applied]
    actions: [run_tests]
  
  - from: REFACTOR_VALIDATING_DOD
    to: COMPLETED
    guard: [no_code_smells, tests_still_pass]
    actions: [checkpoint_git, update_metrics, learn_patterns]
```

### Guard Conditions

**RED Phase:**
- `feature_scope_defined()`: Feature name and acceptance criteria provided
- `no_existing_tests()`: No test file exists for this feature
- `scope_approved()`: User confirmed scope
- `tests_generated()`: Test file created with assertions
- `tests_fail_correctly()`: Tests run and fail as expected (not syntax errors)

**GREEN Phase:**
- `tests_still_failing()`: Tests from RED phase still failing
- `red_phase_complete()`: RED DoD passed
- `implementation_complete()`: Implementation code written
- `all_tests_pass()`: 100% test pass rate
- `minimal_implementation()`: No over-engineering (code smell check)

**REFACTOR Phase:**
- `tests_passing()`: All tests green before refactoring
- `green_phase_complete()`: GREEN DoD passed
- `refactoring_applied()`: Code changes made
- `no_code_smells()`: Code smell count reduced
- `tests_still_pass()`: Tests green after refactoring

---

## 4️⃣ DoR/DoD Definitions

### RED Phase

**Definition of Ready (DoR):**
- [ ] Feature name provided
- [ ] Acceptance criteria defined
- [ ] Test file path determined
- [ ] No existing test file for this feature
- [ ] Git working directory clean

**Definition of Done (DoD):**
- [ ] Test file created with meaningful test names
- [ ] At least 3 test cases (happy path, edge case, error case)
- [ ] Tests execute without syntax errors
- [ ] Tests fail for the right reason (assertion failure, not import error)
- [ ] Test coverage plan documented
- [ ] Git checkpoint created

**Validation Metrics:**
- Test count ≥ 3
- Test execution success (no syntax errors)
- Test failure rate = 100% (all must fail)

### GREEN Phase

**Definition of Ready (DoR):**
- [ ] RED phase DoD complete
- [ ] All tests from RED phase failing
- [ ] Implementation file path determined
- [ ] No duplicate implementation exists

**Definition of Done (DoD):**
- [ ] Implementation code written
- [ ] All tests from RED phase now passing
- [ ] Test coverage ≥ 80%
- [ ] No over-engineering (YAGNI principle)
- [ ] No code smells introduced
- [ ] Git checkpoint created

**Validation Metrics:**
- Test pass rate = 100%
- Code coverage ≥ 80%
- Cyclomatic complexity ≤ 10
- Code smell count = 0

### REFACTOR Phase

**Definition of Ready (DoR):**
- [ ] GREEN phase DoD complete
- [ ] All tests passing
- [ ] Code smell scan complete
- [ ] Refactoring opportunities identified

**Definition of Done (DoD):**
- [ ] Code duplicates removed
- [ ] SOLID principles applied
- [ ] Code complexity reduced
- [ ] All tests still passing
- [ ] Code smell count reduced by ≥50%
- [ ] Pattern learning recorded in Tier 2
- [ ] Git checkpoint created

**Validation Metrics:**
- Test pass rate = 100% (must remain green)
- Code smell reduction ≥ 50%
- Cyclomatic complexity reduced
- Duplicate code eliminated

---

## 5️⃣ Multi-Tenant Architecture

### Tenant Isolation

**Tenant Scope:**
- Each tenant has isolated TDD sessions
- Separate git repositories per tenant
- Isolated test execution environments
- Tenant-specific knowledge graphs (pattern learning)

**Project Scope:**
- Multiple projects per tenant
- Cross-project test template reuse
- Shared refactoring patterns within tenant

**User Scope:**
- User-specific TDD preferences
- Personal test templates
- Individual metrics dashboard

### RBAC Model

**Roles:**
- **Developer:** Can start TDD sessions, execute phases
- **Tech Lead:** Can start sessions, execute phases, approve scope, view team metrics
- **Architect:** All permissions + cross-project pattern analysis

**Permissions:**
| Role | Start TDD | Execute Phases | Approve Scope | View Metrics | Cross-Project Analysis |
|------|-----------|----------------|---------------|--------------|------------------------|
| Developer | ✅ | ✅ | ❌ | Own only | ❌ |
| Tech Lead | ✅ | ✅ | ✅ | Team | ❌ |
| Architect | ✅ | ✅ | ✅ | All | ✅ |

---

## 6️⃣ Migration Strategy (TDD: RED→GREEN→REFACTOR→CUTOVER→CLEANUP)

### Phase 1: RED (Create Failing Tests for New Orchestrator)

**Test Files to Create:**
- `tests/orchestration_3_0/orchestrators/tdd/test_tdd_orchestrator.py` (100 tests)
- `tests/orchestration_3_0/orchestrators/tdd/test_test_generator.py` (80 tests)
- `tests/orchestration_3_0/orchestrators/tdd/test_implementation_engine.py` (60 tests)
- `tests/orchestration_3_0/orchestrators/tdd/test_refactoring_engine.py` (80 tests)
- `tests/orchestration_3_0/orchestrators/tdd/test_phase_validator.py` (60 tests)
- `tests/orchestration_3_0/orchestrators/tdd/test_metrics_collector.py` (40 tests)

**Total Tests:** 420 tests

**Test Categories:**
- Unit tests: 300 tests
- Integration tests: 80 tests
- E2E workflow tests: 40 tests

**Validation:**
- All 420 tests must fail initially
- No import errors (modules don't exist yet)
- Clear assertion failures

### Phase 2: GREEN (Implement New Orchestrator)

**Week 1: Core Orchestrator**
- Day 1-2: `tdd_orchestrator.py` (500 LOC)
  - BaseOrchestrator extension
  - State machine integration
  - Session management
- Day 3: `phase_validator.py` (200 LOC)
  - DoR/DoD validation logic
- Day 4-5: Integration tests passing

**Week 2: Supporting Components**
- Day 1-2: `test_generator.py` (400 LOC)
  - Edge case analysis
  - Test generation
- Day 3: `implementation_engine.py` (300 LOC)
  - Minimal code generation
- Day 4: `refactoring_engine.py` (400 LOC)
  - Code smell detection
- Day 5: `metrics_collector.py` (200 LOC)
  - Metrics collection

**Validation:**
- 100% of 420 tests passing
- Code coverage ≥ 85%
- All DoR/DoD gates working

### Phase 3: REFACTOR (Clean New Code)

**Code Quality Improvements:**
- Extract common validation logic
- Consolidate test generation logic
- Optimize AST parsing (cache patterns)
- Improve error messages

**Pattern Learning:**
- Record TDD preferences in Tier 2
- Store common test templates
- Learn refactoring patterns

**Validation:**
- Tests still 100% passing
- Code smell count = 0
- Cyclomatic complexity ≤ 10

### Phase 4: CUTOVER (Switch to New Orchestrator)

**Week 3: Feature Flag Rollout**
- Day 1: Feature flag `ENABLE_TDD_ORCHESTRATOR_4_0 = False`
- Day 2-3: Parallel run (old + new, compare results)
- Day 4: Feature flag = True (50% traffic)
- Day 5: Feature flag = True (100% traffic)

**Rollback Plan:**
- Feature flag toggles back to old orchestrator
- Git checkpoint before cutover
- Session state preserved

**Validation:**
- Compare outputs (old vs new)
- Monitor error rates
- User acceptance testing

### Phase 5: CLEANUP (Archive Old Files)

**Week 4: Archive Legacy**
- Move old files to `cortex-brain/archives/orchestrators-legacy/tdd/`
- Update all imports to new orchestrator
- Remove feature flag
- Update documentation

**Files to Archive:**
- `src/orchestrators/tdd_implementation_orchestrator.py` → `archives/orchestrators-legacy/tdd/`
- `src/workflows/tdd_workflow_orchestrator.py` → `archives/orchestrators-legacy/tdd/`
- `src/workflows/tdd_workflow_integrator.py` → `archives/orchestrators-legacy/tdd/`
- `src/workflows/tdd_workflow.py` → `archives/orchestrators-legacy/tdd/`

**Validation:**
- All imports updated
- No references to old files
- 100% tests passing
- Git history preserved

---

## 7️⃣ Integration Points

### Upstream Dependencies (What This Orchestrator Needs)

**Core Infrastructure (Phase 1):**
- ✅ `StateMachine` - State transitions
- ✅ `DependencyContainer` - Service injection
- ✅ `SessionManager` - Session persistence
- ✅ `BaseOrchestrator` - Base class

**Tier 2 Knowledge Graph:**
- `KnowledgeGraph.store_pattern()` - Learn refactoring patterns
- `KnowledgeGraph.retrieve_patterns()` - Reuse learned patterns

**Git Orchestrator (Phase 1):**
- `GitCheckpointOrchestrator.create_checkpoint()` - Phase boundaries
- `GitCheckpointOrchestrator.rollback()` - Undo failed refactoring

**Test Execution:**
- `TestExecutionManager.run_tests()` - Execute test suite
- `WorkspaceContextManager.get_test_files()` - Locate tests

### Downstream Consumers (What Uses This Orchestrator)

**Planning Orchestrator (Phase 2):**
- Calls TDD Orchestrator for each feature in plan
- Passes feature scope and acceptance criteria

**Execution Orchestrator (Phase 2):**
- Coordinates TDD workflow across multiple features
- Manages parallel TDD sessions

**Documentation Orchestrator (Phase 3):**
- Generates TDD workflow documentation
- Embeds test coverage reports

**Observability Orchestrator (Phase 4):**
- Displays TDD metrics on dashboard
- Tracks TDD adoption across projects

---

## 8️⃣ Metrics & Observability

### Real-Time Metrics

**Session Metrics:**
- Active TDD sessions
- Phase distribution (RED: X%, GREEN: Y%, REFACTOR: Z%)
- Average phase duration
- Session completion rate

**Quality Metrics:**
- Test coverage per layer (unit: X%, integration: Y%, e2e: Z%)
- Code smell count before/after REFACTOR
- Cyclomatic complexity trend
- Duplicate code percentage

**Performance Metrics:**
- Test generation time
- Test execution time
- Refactoring engine time
- End-to-end workflow time

### Dashboard Widgets

**TDD Health Widget:**
- Current phase indicator (RED/GREEN/REFACTOR)
- Test pass rate gauge
- Code coverage progress bar
- Code smell count badge

**TDD Timeline Widget:**
- Phase history (RED → GREEN → REFACTOR)
- Git checkpoints marked
- Duration per phase
- Failure points highlighted

**TDD Leaderboard Widget:**
- Most tests written
- Highest code coverage
- Fastest GREEN phase
- Most refactoring improvements

---

## 9️⃣ Success Criteria

### Functional Success

- [ ] TDD Orchestrator extends BaseOrchestrator
- [ ] State machine enforces RED→GREEN→REFACTOR sequence
- [ ] DoR/DoD validation at phase boundaries
- [ ] Git checkpoints at phase transitions
- [ ] Multi-tenant session isolation
- [ ] 420 unit/integration tests passing (100%)

### Quality Success

- [ ] Code coverage ≥ 85%
- [ ] No code smells
- [ ] Cyclomatic complexity ≤ 10
- [ ] API response time ≤ 200ms
- [ ] Zero test failures

### Business Success

- [ ] Workflow completion rate ≥ 95% (up from 75%)
- [ ] Phase skip rate = 0% (down from 15%)
- [ ] Developer satisfaction score ≥ 4.5/5
- [ ] TDD adoption rate ≥ 80% of features

---

## 🔟 Timeline

**Week 1: Core Infrastructure + Tests**
- Day 1-2: Write 420 failing tests (RED)
- Day 3-4: Implement `tdd_orchestrator.py` + `phase_validator.py` (GREEN)
- Day 5: Refactor, clean code

**Week 2: Components**
- Day 1-2: Implement `test_generator.py` (GREEN)
- Day 3: Implement `implementation_engine.py` (GREEN)
- Day 4: Implement `refactoring_engine.py` (GREEN)
- Day 5: Implement `metrics_collector.py` (GREEN)

**Week 3: Integration + Cutover**
- Day 1-2: Integration testing, bug fixes
- Day 3-4: Feature flag rollout (50% → 100%)
- Day 5: Monitor production, rollback if needed

**Week 4: Cleanup**
- Day 1-2: Archive legacy files
- Day 3-4: Update documentation
- Day 5: Retrospective, lessons learned

**Total:** 4 weeks (20 days)

---

## 🎯 Next Steps

1. ✅ Core infrastructure complete (State Machine, DI, Session Manager, BaseOrchestrator)
2. ⏳ **Start Week 1:** Write 420 failing tests for TDD Orchestrator (RED phase)
3. Implement `tdd_orchestrator.py` (500 LOC)
4. Implement supporting components (1,500 LOC)
5. Cutover with feature flag
6. Archive legacy files

---

## 📞 Contact & Resources

**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX  
**Branch:** `cortex3-orchestration`

**Related Documents:**
- [Orchestration Master Plan](../orchestration-master-plan.md)
- [Core Infrastructure Complete](../../reports/phase-1-core-infrastructure-complete.md)
- [DevOps Orchestrator Plan](02-devops-orchestrator-plan.md)

**Legacy Files:**
- `src/orchestrators/tdd_implementation_orchestrator.py` (2,291 LOC)
- `src/workflows/tdd_workflow_orchestrator.py` (1,232 LOC)
- `src/workflows/tdd_workflow_integrator.py` (~300 LOC)
- `src/workflows/tdd_workflow.py` (~200 LOC)

---

**Status:** ✅ SUB-PLAN COMPLETE - Ready for TDD Orchestrator Implementation (Week 1)
