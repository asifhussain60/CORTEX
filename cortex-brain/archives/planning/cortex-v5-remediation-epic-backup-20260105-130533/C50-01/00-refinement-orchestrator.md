# 🎯 Sub-Plan 01: Refinement Orchestrator Implementation

**Plan ID:** C50-01-refinement-orchestrator  
**Parent Epic:** CORTEX-5.0 Gap Remediation (C50)  
**Order:** 01  
**Created:** January 4, 2026  
**Priority:** 🎯 HIGH (Core Orchestrator)  
**Duration:** 1 week  
**Status:** 🔓 READY  
**Type:** Feature Implementation

---

## 📊 Progress Tracker

**Overall Progress:** `░░░░░░░░░░` **0%** 🔓 READY

| Phase | Task | Status | Duration |
|-------|------|--------|----------|
| 1 | Design refinement workflow & manifest | 🔓 Ready | 1d |
| 2 | Implement RefinementOrchestrator class | 🔓 Ready | 2d |
| 3 | Add TDD enforcement & validation | 🔓 Ready | 1d |
| 4 | Create unit tests (80%+ coverage) | 🔓 Ready | 1.5d |
| 5 | Integration & Master Orchestrator routing | 🔓 Ready | 0.5d |

---

## 🎯 Objective

**Mission:** Implement Refinement Orchestrator as a guided workflow for code improvement, refactoring, and technical debt reduction with TDD enforcement and automated validation.

**Problem:**
- CORTEX has `refinement-manifest.yaml` but no Python orchestrator implementation
- Users manually execute refinement workflows without automation
- No systematic approach to code improvement and refactoring
- Technical debt accumulates without structured remediation

**Solution:**
- Implement `RefinementOrchestrator` class with 7-phase workflow
- Integrate with Master Orchestrator routing (`refine`, `improve`, `optimize`)
- Enforce TDD (RED→GREEN→REFACTOR) for all code changes
- Automated metrics collection and validation

---

## ✅ Acceptance Criteria (DoD)

### Must Have
- [ ] **RefinementOrchestrator** class implemented
  - [ ] Inherits from `BaseOrchestratorV4_1`
  - [ ] 7-phase workflow (Analysis → Implementation → Validation)
  - [ ] State management via `PlanningStateDB`
  - [ ] Phase transitions with validation gates
  - [ ] TDD enforcement (RED→GREEN→REFACTOR mandatory)

- [ ] **Manifest Configuration**
  - [ ] `refinement-orchestrator-manifest.yaml` updated
  - [ ] Phase definitions with acceptance criteria
  - [ ] Tool integrations (AST scanner, complexity metrics)
  - [ ] Rollback strategy and checkpoint rules

- [ ] **Master Orchestrator Integration**
  - [ ] Pattern matching: `^(refine|improve|optimize)`
  - [ ] Router registration in `pattern_router.py`
  - [ ] Entry in `cortex-operations.yaml`

- [ ] **Unit Tests**
  - [ ] 80%+ code coverage
  - [ ] Mock filesystem and database operations
  - [ ] Test each phase independently
  - [ ] Test TDD enforcement
  - [ ] Test rollback scenarios

### Should Have
- [ ] **Metrics & Reporting**
  - [ ] Complexity reduction metrics
  - [ ] Code quality improvements (LOC, cyclomatic complexity)
  - [ ] Test coverage delta
  - [ ] Refactoring impact report

- [ ] **Documentation**
  - [ ] Inline code documentation
  - [ ] User-facing behavior guide
  - [ ] Example refinement workflows

### Nice to Have (Future)
- [ ] AI-powered refactoring suggestions
- [ ] Automated anti-pattern detection
- [ ] Visual dependency graph updates

---

## 🏗️ Implementation Plan

### Phase 1: Design Refinement Workflow & Manifest (1 day)

**Objective:** Define 7-phase workflow and update manifest

**Workflow Design:**
```
Phase 1: CODE ANALYSIS
  → AST scanning, complexity metrics, pattern detection
  → Output: Code health report

Phase 2: ISSUE IDENTIFICATION
  → Anti-patterns, technical debt, optimization opportunities
  → Output: Prioritized issue list

Phase 3: IMPACT ASSESSMENT  
  → Risk scoring, dependency analysis, effort estimation
  → Output: Impact matrix

Phase 4: REFACTORING PLAN
  → Prioritized improvement tasks with rollback strategy
  → Output: Detailed refactoring plan

Phase 5: IMPLEMENTATION (TDD ENFORCED)
  → RED: Write failing tests
  → GREEN: Implement changes
  → REFACTOR: Clean up code
  → Output: Refactored code + tests

Phase 6: VALIDATION
  → Test coverage verification (≥80%)
  → Performance benchmarks
  → Integration tests
  → Output: Validation report

Phase 7: DOCUMENTATION
  → Update architecture docs
  → Add improvement notes
  → Generate completion report
  → Output: Updated documentation
```

**Manifest Updates:**
- Update `cortex-brain/manifests/orchestrators/refinement-manifest.yaml`
- Add phase definitions with validation criteria
- Define tool integrations (pytest, coverage, AST analyzers)
- Add rollback checkpoints

**Deliverables:**
- [ ] Updated `refinement-manifest.yaml`
- [ ] Workflow diagram (Mermaid)
- [ ] Phase acceptance criteria document

---

### Phase 2: Implement RefinementOrchestrator Class (2 days)

**File:** `src/orchestrators/refinement_orchestrator.py` (~600-800 LOC)

**Class Structure:**
```python
from src.orchestrators.base.base_orchestrator_v4_1 import (
    BaseOrchestratorV4_1,
    PhaseStatus,
    PhaseResult,
    OrchestratorResult
)

class RefinementOrchestrator(BaseOrchestratorV4_1):
    \"\"\"
    Refinement Orchestrator - Guided code improvement workflow.
    
    Workflow (7 phases):
        1. CODE ANALYSIS - Scan codebase for issues
        2. ISSUE IDENTIFICATION - Prioritize technical debt
        3. IMPACT ASSESSMENT - Risk and effort estimation
        4. REFACTORING PLAN - Create improvement roadmap
        5. IMPLEMENTATION - TDD-enforced refactoring
        6. VALIDATION - Test coverage and performance
        7. DOCUMENTATION - Update architecture docs
    \"\"\"
    
    def __init__(self, config_path: str, state_db, plan_id):
        super().__init__(config_path, state_db, plan_id)
        
        # Load refinement-specific config
        self.analysis_tools = self.config.get('analysis_tools', {})
        self.validation_rules = self.config.get('validation', {})
        self.tdd_enforcement = self.config.get('tdd_enforcement', True)
    
    def _phase_1_code_analysis(self) -> PhaseResult:
        \"\"\"Phase 1: Analyze codebase for improvement opportunities.\"\"\"
        pass
    
    def _phase_2_issue_identification(self) -> PhaseResult:
        \"\"\"Phase 2: Identify and prioritize issues.\"\"\"
        pass
    
    def _phase_3_impact_assessment(self) -> PhaseResult:
        \"\"\"Phase 3: Assess risk and effort for each issue.\"\"\"
        pass
    
    def _phase_4_refactoring_plan(self) -> PhaseResult:
        \"\"\"Phase 4: Create detailed refactoring plan.\"\"\"
        pass
    
    def _phase_5_implementation(self) -> PhaseResult:
        \"\"\"Phase 5: Implement changes with TDD enforcement.\"\"\"
        # TDD Cycle: RED → GREEN → REFACTOR
        pass
    
    def _phase_6_validation(self) -> PhaseResult:
        \"\"\"Phase 6: Validate improvements meet criteria.\"\"\"
        pass
    
    def _phase_7_documentation(self) -> PhaseResult:
        \"\"\"Phase 7: Update documentation and generate report.\"\"\"
        pass
```

**Key Methods:**
- `_analyze_complexity()` - Calculate cyclomatic complexity
- `_detect_anti_patterns()` - Find code smells
- `_assess_risk()` - Score impact of changes
- `_enforce_tdd()` - Validate RED→GREEN→REFACTOR cycle
- `_run_validation_suite()` - Execute tests and benchmarks

**Deliverables:**
- [ ] `refinement_orchestrator.py` implemented
- [ ] All 7 phases functional
- [ ] TDD enforcement integrated
- [ ] State management via `PlanningStateDB`

---

### Phase 3: Add TDD Enforcement & Validation (1 day)

**TDD Enforcement:**
```python
def _enforce_tdd_cycle(self, target_files: List[Path]) -> bool:
    \"\"\"
    Enforce RED→GREEN→REFACTOR cycle.
    
    Steps:
    1. RED: Verify failing tests exist
    2. GREEN: Verify tests pass after implementation
    3. REFACTOR: Verify code quality improved
    \"\"\"
    # Step 1: RED - Run tests (should fail)
    red_result = self._run_tests(target_files)
    if not red_result.has_failures:
        raise TDDViolation("RED phase: No failing tests found")
    
    # Step 2: GREEN - Implement changes, run tests (should pass)
    self._implement_changes(target_files)
    green_result = self._run_tests(target_files)
    if green_result.has_failures:
        raise TDDViolation("GREEN phase: Tests still failing")
    
    # Step 3: REFACTOR - Clean up, verify quality
    self._refactor_code(target_files)
    refactor_result = self._run_quality_checks(target_files)
    if not refactor_result.meets_standards:
        raise TDDViolation("REFACTOR phase: Quality standards not met")
    
    return True
```

**Validation Gates:**
- Test coverage ≥ 80%
- No pylint errors
- Complexity metrics improved
- No regression in performance

**Deliverables:**
- [ ] `_enforce_tdd_cycle()` method
- [ ] Validation gate checks
- [ ] Rollback on validation failure

---

### Phase 4: Create Unit Tests (1.5 days)

**File:** `tests/test_refinement_orchestrator.py` (~400-500 LOC)

**Test Suites:**
```python
class TestRefinementOrchestrator(unittest.TestCase):
    def setUp(self):
        # Create test orchestrator with mock DB
        pass
    
    def test_phase_1_code_analysis(self):
        # Test code analysis phase
        pass
    
    def test_phase_5_tdd_enforcement(self):
        # Test TDD cycle enforcement
        pass
    
    def test_validation_gate_failure(self):
        # Test rollback on validation failure
        pass
    
    def test_integration_with_master_orchestrator(self):
        # Test routing from master orchestrator
        pass
```

**Coverage Target:** 80%+

**Deliverables:**
- [ ] Unit tests for all phases
- [ ] Integration tests
- [ ] Mock database and filesystem
- [ ] Coverage report ≥80%

---

### Phase 5: Integration & Master Orchestrator Routing (0.5 days)

**Router Registration:**
```python
# src/orchestrators/pattern_router.py

ORCHESTRATOR_PATTERNS = [
    # ... existing patterns ...
    {
        "pattern": r"^(refine|improve|optimize)",
        "orchestrator": "refinement",
        "priority": 40,
        "mode": "guided"
    }
]
```

**Operations Registry:**
```yaml
# cortex-operations.yaml

refinement:
  name: "Code Refinement"
  orchestrator_class: "RefinementOrchestrator"
  config_path: "cortex-brain/manifests/orchestrators/refinement-manifest.yaml"
  triggers:
    - "refine"
    - "improve code"
    - "optimize"
  execution_method: "orchestrator"
```

**Deliverables:**
- [ ] Router pattern registered
- [ ] Operations registry updated
- [ ] End-to-end test with user command

---

## 📊 Success Metrics

**Implementation:**
- ✅ RefinementOrchestrator class: ~600-800 LOC
- ✅ Unit tests: ≥80% coverage
- ✅ All 7 phases functional
- ✅ TDD enforcement working

**Integration:**
- ✅ Master Orchestrator routing: Pattern match success
- ✅ User command `refine [target]` works end-to-end
- ✅ State persistence via `PlanningStateDB`

**Quality:**
- ✅ No pylint errors
- ✅ All unit tests pass
- ✅ Integration tests pass
- ✅ Documentation complete

---

## 🔄 Dependencies

**Upstream (Must Be Complete):**
- ✅ C50-00C: Test Coverage Sprint (80%+ infrastructure coverage)

**Downstream (Unlocks):**
- C50-08: Orchestrator Migrations (needs Refinement + Debug orchestrators)

**Parallel (Can Run Concurrently):**
- C50-02: Debug Orchestrator
- C50-03: Knowledge Library Phase -1
- C50-04: AST Scanning Integration
- C50-05: Context Middleware Enhancement

---

## 🎭 Execution Notes

**TDD Mandate:** ALL code changes MUST follow RED→GREEN→REFACTOR cycle

**Rollback Strategy:**
- Git checkpoint before Phase 5 (Implementation)
- State checkpoints after each phase
- Automatic rollback on validation failure

**Brain Protection (SKULL):**
- HOLISTIC_DISCOVERY: Search for existing refinement code before creating
- GIT_ISOLATION: Refinement orchestrator stays in CORTEX repo
- TDD_ENFORCEMENT: Mandatory for all implementation phases

---

## 📚 References

**Existing Infrastructure:**
- `cortex-brain/manifests/orchestrators/refinement-manifest.yaml` (manifest to update)
- `src/orchestrators/base/base_orchestrator_v4_1.py` (base class)
- `src/database/planning_state_db.py` (state management)
- `src/orchestrators/pattern_router.py` (routing)

**Similar Orchestrators:**
- Vacuum Orchestrator v2 (7-phase workflow example)
- Investigation Orchestrator (analysis phase patterns)

---

**Plan Status:** 🔓 READY  
**Created:** January 4, 2026  
**Ready to Execute:** Yes (all dependencies met)
