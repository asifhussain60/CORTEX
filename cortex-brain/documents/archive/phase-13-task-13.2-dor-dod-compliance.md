# Task 13.2: DoR/DoD Compliance Implementation

**Phase:** 13 (Post-GA Refinement)  
**Task ID:** 13.2  
**Priority:** HIGH  
**Estimated Effort:** 7-8 hours  
**Dependencies:** Task 13.1 (git checkpoint safety net) ✅  
**Status:** ⏳ READY TO START

---

## 📊 Executive Summary

Implement Definition of Ready (DoR) and Definition of Done (DoD) validation frameworks in Planning Orchestrator to ensure quality gates at plan start and completion. This adds 13 methods across validation, checking, and reporting capabilities.

**Impact:**
- Quality gates prevent incomplete/untestable plans from starting
- Completion gates ensure deliverables meet acceptance criteria
- Automated reporting provides actionable feedback for remediation
- Enforces Planning System manifest compliance requirements

---

## 🎯 Objectives

### Primary Goals

1. **DoR Validation Framework (7 methods)**
   - Implement comprehensive pre-flight checks before plan execution
   - Validate requirements clarity, dependencies, testability
   - Generate actionable DoR reports with remediation steps

2. **DoD Validation Framework (6 methods)**
   - Implement completion quality gates
   - Validate code completeness, test coverage, documentation
   - Generate DoD reports with compliance scoring

3. **Planning Integration**
   - Integrate DoR checks into `_validate_plan_structure()`
   - Integrate DoD checks into plan completion phases
   - Add quality gate enforcement with override capability

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Methods Implemented | 13/13 | All DoR/DoD methods functional |
| Test Pass Rate | +0.2% | 98.8% → 99.0% |
| Quality Gates | 100% | DoR/DoD enforced on all plans |
| Report Quality | 10/10 | Actionable feedback with examples |

---

## 🔧 Implementation Details

### Part 1: DoR (Definition of Ready) - 7 Methods

**Location:** `src/orchestrators/planning/planning_orchestrator.py`

#### Method 1: `_validate_definition_of_ready(plan: Dict) -> Tuple[bool, List[str]]`

**Purpose:** Master DoR validation orchestrator

**Signature:**
```python
def _validate_definition_of_ready(self, plan: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates plan meets Definition of Ready criteria.
    
    Args:
        plan: Plan dictionary with metadata, phases, requirements
        
    Returns:
        Tuple of (is_ready: bool, violations: List[str])
        
    DoR Criteria (from Planning System manifest):
    1. Requirements clarity (objectives, acceptance criteria defined)
    2. Dependencies identified (external services, data sources)
    3. Acceptance criteria measurable (testable outcomes)
    4. Technical feasibility assessed (architecture, patterns)
    5. Testability validated (test strategy defined)
    6. Resource availability (tools, environments ready)
    7. Risk assessment (blockers, unknowns documented)
    """
```

**Implementation Logic:**
```python
violations = []

# 1. Check requirements clarity
if not self._check_requirements_clarity(plan):
    violations.append("Requirements clarity: Missing objectives/acceptance criteria")

# 2. Check dependencies
deps_valid, dep_issues = self._check_dependencies_identified(plan)
if not deps_valid:
    violations.extend(dep_issues)

# 3. Check acceptance criteria
if not self._check_acceptance_criteria(plan):
    violations.append("Acceptance criteria: Not measurable/testable")

# 4. Check technical feasibility
feas_valid, feas_issues = self._check_technical_feasibility(plan)
if not feas_valid:
    violations.extend(feas_issues)

# 5. Check testability
if not self._check_testability(plan):
    violations.append("Testability: No test strategy defined")

# 6. Resource availability (simplified - check manifest has tool references)
if "tools" not in plan.get("metadata", {}):
    violations.append("Resource availability: No tools/environments specified")

# 7. Risk assessment (check for risks section)
if "risks" not in plan.get("metadata", {}) and "blockers" not in plan.get("metadata", {}):
    violations.append("Risk assessment: No risks/blockers documented")

is_ready = len(violations) == 0
return is_ready, violations
```

**Lines of Code:** ~40 LOC

---

#### Method 2: `_check_requirements_clarity(plan: Dict) -> bool`

**Purpose:** Validate objectives and acceptance criteria are defined

**Implementation:**
```python
def _check_requirements_clarity(self, plan: Dict[str, Any]) -> bool:
    """Check if requirements are clearly defined."""
    metadata = plan.get("metadata", {})
    
    # Must have objectives
    objectives = metadata.get("objectives", [])
    if not objectives or len(objectives) == 0:
        return False
    
    # Must have acceptance criteria (in phases or metadata)
    has_acceptance_criteria = False
    if "acceptance_criteria" in metadata and len(metadata["acceptance_criteria"]) > 0:
        has_acceptance_criteria = True
    
    # Check phases have success criteria
    phases = plan.get("phases", [])
    if phases and any("success_criteria" in phase for phase in phases):
        has_acceptance_criteria = True
    
    return has_acceptance_criteria
```

**Lines of Code:** ~20 LOC

---

#### Method 3: `_check_dependencies_identified(plan: Dict) -> Tuple[bool, List[str]]`

**Purpose:** Validate external dependencies are documented

**Implementation:**
```python
def _check_dependencies_identified(self, plan: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Check if dependencies are identified."""
    issues = []
    metadata = plan.get("metadata", {})
    
    # Look for dependencies in metadata
    dependencies = metadata.get("dependencies", [])
    
    # For HIGH complexity, must have dependencies documented
    complexity = metadata.get("complexity", "MEDIUM")
    if complexity == "HIGH" and len(dependencies) == 0:
        issues.append("Dependencies: HIGH complexity requires dependency documentation")
    
    # Check for circular dependencies (basic check)
    if len(dependencies) > 1:
        dep_names = [d.get("name", "") for d in dependencies if isinstance(d, dict)]
        if len(dep_names) != len(set(dep_names)):
            issues.append("Dependencies: Duplicate dependencies detected")
    
    return len(issues) == 0, issues
```

**Lines of Code:** ~22 LOC

---

#### Method 4: `_check_acceptance_criteria(plan: Dict) -> bool`

**Purpose:** Validate acceptance criteria are measurable and testable

**Implementation:**
```python
def _check_acceptance_criteria(self, plan: Dict[str, Any]) -> bool:
    """Check if acceptance criteria are measurable."""
    metadata = plan.get("metadata", {})
    criteria = metadata.get("acceptance_criteria", [])
    
    if len(criteria) == 0:
        return False
    
    # Check criteria contain measurable indicators
    measurable_keywords = ["pass rate", "coverage", "performance", "≥", "<=", "%", "time", "count", "response"]
    
    measurable_count = 0
    for criterion in criteria:
        if isinstance(criterion, str):
            if any(keyword in criterion.lower() for keyword in measurable_keywords):
                measurable_count += 1
    
    # At least 50% of criteria should be measurable
    return measurable_count >= len(criteria) * 0.5
```

**Lines of Code:** ~20 LOC

---

#### Method 5: `_check_technical_feasibility(plan: Dict) -> Tuple[bool, List[str]]`

**Purpose:** Assess if technical approach is sound

**Implementation:**
```python
def _check_technical_feasibility(self, plan: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Check technical feasibility."""
    issues = []
    metadata = plan.get("metadata", {})
    
    # Check for architecture/design section
    if "architecture" not in metadata and "design" not in metadata:
        issues.append("Technical feasibility: No architecture/design documented")
    
    # Check for technology stack
    if "technologies" not in metadata and "stack" not in metadata:
        issues.append("Technical feasibility: Technology stack not specified")
    
    # For HIGH complexity, must have proof of concept or existing patterns
    complexity = metadata.get("complexity", "MEDIUM")
    if complexity == "HIGH":
        if "poc" not in metadata and "existing_patterns" not in metadata:
            issues.append("Technical feasibility: HIGH complexity requires POC or pattern references")
    
    return len(issues) == 0, issues
```

**Lines of Code:** ~22 LOC

---

#### Method 6: `_check_testability(plan: Dict) -> bool`

**Purpose:** Validate test strategy is defined

**Implementation:**
```python
def _check_testability(self, plan: Dict[str, Any]) -> bool:
    """Check if plan has testability strategy."""
    metadata = plan.get("metadata", {})
    
    # Look for test strategy in metadata
    has_test_strategy = (
        "test_strategy" in metadata or
        "testing" in metadata or
        "tdd" in metadata
    )
    
    # Check phases mention testing
    phases = plan.get("phases", [])
    has_test_phases = any(
        "test" in phase.get("name", "").lower() or
        "tdd" in phase.get("name", "").lower()
        for phase in phases
    )
    
    return has_test_strategy or has_test_phases
```

**Lines of Code:** ~18 LOC

---

#### Method 7: `_generate_dor_report(plan: Dict, violations: List[str]) -> str`

**Purpose:** Generate actionable DoR compliance report

**Implementation:**
```python
def _generate_dor_report(self, plan: Dict[str, Any], violations: List[str]) -> str:
    """Generate Definition of Ready compliance report."""
    plan_name = plan.get("metadata", {}).get("name", "Unnamed Plan")
    
    if len(violations) == 0:
        return f"✅ DoR COMPLIANT: {plan_name} meets all Definition of Ready criteria"
    
    report = [
        f"❌ DoR VIOLATIONS: {plan_name} has {len(violations)} issue(s)\n",
        "Definition of Ready requires:",
        "1. Requirements clarity (objectives + acceptance criteria)",
        "2. Dependencies identified",
        "3. Acceptance criteria measurable",
        "4. Technical feasibility assessed",
        "5. Testability validated",
        "6. Resource availability confirmed",
        "7. Risk assessment documented\n",
        "VIOLATIONS FOUND:"
    ]
    
    for i, violation in enumerate(violations, 1):
        report.append(f"{i}. {violation}")
    
    report.append("\nREMEDIATION:")
    report.append("- Review Planning System User Guide section 'DoR Requirements'")
    report.append("- Update plan metadata with missing criteria")
    report.append("- Re-run validation after updates")
    
    return "\n".join(report)
```

**Lines of Code:** ~28 LOC

---

### Part 2: DoD (Definition of Done) - 6 Methods

#### Method 8: `_validate_definition_of_done(plan: Dict, results: Dict) -> Tuple[bool, List[str]]`

**Purpose:** Master DoD validation orchestrator

**Signature:**
```python
def _validate_definition_of_done(
    self, 
    plan: Dict[str, Any], 
    results: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Validates plan execution meets Definition of Done criteria.
    
    Args:
        plan: Original plan dictionary
        results: Execution results with test outcomes, coverage, artifacts
        
    Returns:
        Tuple of (is_done: bool, violations: List[str])
        
    DoD Criteria (from Planning System manifest):
    1. Code complete (all phases executed successfully)
    2. Tests passing (≥95% pass rate, TDD complete)
    3. Documentation complete (README, API docs, guides)
    4. Code reviewed (complexity ≤30, no FIXME/TODO)
    5. Performance acceptable (no regressions)
    6. Acceptance criteria met (all requirements satisfied)
    """
```

**Implementation Logic:**
```python
violations = []

# 1. Check code complete
if not self._check_code_complete(results):
    violations.append("Code complete: Not all phases executed successfully")

# 2. Check tests passing
tests_valid, test_issues = self._check_tests_passing(results)
if not tests_valid:
    violations.extend(test_issues)

# 3. Check documentation
if not self._check_documentation_complete(results):
    violations.append("Documentation: Missing required documentation artifacts")

# 4. Check code reviewed
review_valid, review_issues = self._check_code_reviewed(results)
if not review_valid:
    violations.extend(review_issues)

# 5. Performance (check if performance tests exist and passed)
if "performance" in results and not results["performance"].get("passed", True):
    violations.append("Performance: Performance tests failed or regressions detected")

# 6. Acceptance criteria met
acceptance_met = results.get("acceptance_criteria_met", False)
if not acceptance_met:
    violations.append("Acceptance criteria: Not all criteria satisfied")

is_done = len(violations) == 0
return is_done, violations
```

**Lines of Code:** ~35 LOC

---

#### Method 9: `_check_code_complete(results: Dict) -> bool`

**Purpose:** Validate all phases completed successfully

**Implementation:**
```python
def _check_code_complete(self, results: Dict[str, Any]) -> bool:
    """Check if code implementation is complete."""
    # Check phase execution
    phases = results.get("phases", [])
    if not phases:
        return False
    
    # All phases must have status="complete"
    incomplete_phases = [
        p.get("name", "Unknown") 
        for p in phases 
        if p.get("status") != "complete"
    ]
    
    return len(incomplete_phases) == 0
```

**Lines of Code:** ~15 LOC

---

#### Method 10: `_check_tests_passing(results: Dict) -> Tuple[bool, List[str]]`

**Purpose:** Validate test coverage and pass rate

**Implementation:**
```python
def _check_tests_passing(self, results: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Check if tests meet quality thresholds."""
    issues = []
    
    test_results = results.get("test_results", {})
    
    # Check pass rate ≥95%
    pass_rate = test_results.get("pass_rate", 0)
    if pass_rate < 95.0:
        issues.append(f"Tests: Pass rate {pass_rate}% below 95% threshold")
    
    # Check coverage ≥80%
    coverage = test_results.get("coverage", 0)
    if coverage < 80.0:
        issues.append(f"Tests: Coverage {coverage}% below 80% threshold")
    
    # Check TDD phases completed
    tdd_complete = test_results.get("tdd_complete", False)
    if not tdd_complete:
        issues.append("Tests: TDD workflow not completed (RED→GREEN→REFACTOR)")
    
    return len(issues) == 0, issues
```

**Lines of Code:** ~22 LOC

---

#### Method 11: `_check_documentation_complete(results: Dict) -> bool`

**Purpose:** Validate documentation artifacts exist

**Implementation:**
```python
def _check_documentation_complete(self, results: Dict[str, Any]) -> bool:
    """Check if documentation is complete."""
    artifacts = results.get("artifacts", {})
    docs = artifacts.get("documentation", [])
    
    # Minimum required: README or implementation guide
    required_docs = ["README", "guide", "doc"]
    has_required = any(
        any(req in doc.lower() for req in required_docs)
        for doc in docs
    )
    
    return has_required
```

**Lines of Code:** ~14 LOC

---

#### Method 12: `_check_code_reviewed(results: Dict) -> Tuple[bool, List[str]]`

**Purpose:** Validate code quality standards met

**Implementation:**
```python
def _check_code_reviewed(self, results: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Check if code meets review standards."""
    issues = []
    
    quality_metrics = results.get("quality_metrics", {})
    
    # Check complexity ≤30
    max_complexity = quality_metrics.get("max_complexity", 0)
    if max_complexity > 30:
        issues.append(f"Code quality: Complexity {max_complexity} exceeds limit of 30")
    
    # Check for FIXME/TODO
    fixme_count = quality_metrics.get("fixme_count", 0)
    todo_count = quality_metrics.get("todo_count", 0)
    if fixme_count > 0 or todo_count > 0:
        issues.append(f"Code quality: {fixme_count} FIXME + {todo_count} TODO markers found")
    
    return len(issues) == 0, issues
```

**Lines of Code:** ~18 LOC

---

#### Method 13: `_generate_dod_report(plan: Dict, results: Dict, violations: List[str]) -> str`

**Purpose:** Generate actionable DoD compliance report

**Implementation:**
```python
def _generate_dod_report(
    self, 
    plan: Dict[str, Any], 
    results: Dict[str, Any], 
    violations: List[str]
) -> str:
    """Generate Definition of Done compliance report."""
    plan_name = plan.get("metadata", {}).get("name", "Unnamed Plan")
    
    if len(violations) == 0:
        # Success report
        test_results = results.get("test_results", {})
        pass_rate = test_results.get("pass_rate", 0)
        coverage = test_results.get("coverage", 0)
        
        return (
            f"✅ DoD COMPLIANT: {plan_name}\n\n"
            f"Quality Metrics:\n"
            f"- Pass Rate: {pass_rate:.1f}%\n"
            f"- Coverage: {coverage:.1f}%\n"
            f"- Phases: All complete\n"
            f"- Documentation: Present\n"
            f"- Code Quality: Passed review"
        )
    
    report = [
        f"❌ DoD VIOLATIONS: {plan_name} has {len(violations)} issue(s)\n",
        "Definition of Done requires:",
        "1. Code complete (all phases successful)",
        "2. Tests passing (≥95% pass rate, TDD complete)",
        "3. Documentation complete",
        "4. Code reviewed (complexity ≤30, no FIXME/TODO)",
        "5. Performance acceptable",
        "6. Acceptance criteria met\n",
        "VIOLATIONS FOUND:"
    ]
    
    for i, violation in enumerate(violations, 1):
        report.append(f"{i}. {violation}")
    
    report.append("\nREMEDIATION:")
    report.append("- Address violations listed above")
    report.append("- Re-run tests after fixes")
    report.append("- Update documentation if incomplete")
    report.append("- Refactor high-complexity code")
    
    return "\n".join(report)
```

**Lines of Code:** ~45 LOC

---

### Part 3: Integration with Planning Orchestrator

**Changes to `_validate_plan_structure()` method:**

```python
def _validate_plan_structure(self, plan: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate plan structure and DoR compliance."""
    errors = []
    
    # Existing validation logic...
    
    # ADD: DoR validation
    if self.config.get("enforce_dor", True):  # Default enabled
        is_ready, dor_violations = self._validate_definition_of_ready(plan)
        if not is_ready:
            dor_report = self._generate_dor_report(plan, dor_violations)
            logger.warning(f"DoR violations detected:\n{dor_report}")
            errors.extend(dor_violations)
    
    return len(errors) == 0, errors
```

**Changes to plan completion phase:**

```python
def _finalize_plan_execution(self, plan: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
    """Finalize plan and validate DoD compliance."""
    
    # ADD: DoD validation
    if self.config.get("enforce_dod", True):  # Default enabled
        is_done, dod_violations = self._validate_definition_of_done(plan, results)
        dod_report = self._generate_dod_report(plan, results, dod_violations)
        
        if not is_done:
            logger.warning(f"DoD violations detected:\n{dod_report}")
            results["dod_compliant"] = False
            results["dod_violations"] = dod_violations
        else:
            logger.info(f"DoD compliance achieved:\n{dod_report}")
            results["dod_compliant"] = True
    
    return results
```

---

## 📝 Acceptance Criteria

### Functional Requirements

| # | Requirement | Verification |
|---|-------------|--------------|
| 1 | All 7 DoR methods implemented | Code review + method signature validation |
| 2 | All 6 DoD methods implemented | Code review + method signature validation |
| 3 | DoR enforced at plan start | Integration test with incomplete plan |
| 4 | DoD enforced at plan completion | Integration test with failed tests |
| 5 | Reports are actionable | Manual review of violation messages |
| 6 | Override capability exists | Config flag `enforce_dor=False` works |

### Non-Functional Requirements

| # | Requirement | Target | Verification |
|---|-------------|--------|--------------|
| 1 | Performance overhead | <500ms per validation | Profiling |
| 2 | Code quality | Complexity ≤15 per method | Static analysis |
| 3 | Test coverage | ≥95% for new methods | Pytest coverage |
| 4 | Documentation | All methods have docstrings | Code review |

---

## 🧪 Testing Strategy

### Unit Tests (13 tests - one per method)

**File:** `tests/orchestrators/planning/test_planning_orchestrator_dor_dod.py`

```python
class TestDoRValidation:
    def test_validate_definition_of_ready_complete_plan(self):
        """Test DoR passes for complete plan."""
        
    def test_validate_definition_of_ready_missing_objectives(self):
        """Test DoR fails without objectives."""
        
    def test_check_requirements_clarity_valid(self):
        """Test requirements clarity check passes."""
        
    # ... 4 more DoR tests

class TestDoDValidation:
    def test_validate_definition_of_done_complete(self):
        """Test DoD passes for successful execution."""
        
    def test_validate_definition_of_done_failing_tests(self):
        """Test DoD fails with low pass rate."""
        
    # ... 4 more DoD tests
```

### Integration Tests (4 tests)

```python
class TestDoRDoDIntegration:
    def test_plan_blocked_by_dor_violations(self):
        """Test plan start blocked by DoR failures."""
        
    def test_plan_completion_blocked_by_dod_violations(self):
        """Test plan completion blocked by DoD failures."""
        
    def test_dor_override_allows_execution(self):
        """Test enforce_dor=False bypasses checks."""
        
    def test_dod_report_generation_end_to_end(self):
        """Test full DoD report with real execution results."""
```

---

## 📅 Implementation Plan

### Day 1: DoR Implementation (4 hours)

**Morning (2h):**
- Implement 7 DoR methods (`_validate_definition_of_ready` → `_generate_dor_report`)
- Add unit tests for each method
- **Checkpoint:** All DoR methods functional

**Afternoon (2h):**
- Integrate DoR into `_validate_plan_structure()`
- Add config flag `enforce_dor`
- Test with real plan (incomplete plan should be blocked)
- **Checkpoint:** DoR enforcement working

### Day 2: DoD Implementation (3-4 hours)

**Morning (2h):**
- Implement 6 DoD methods (`_validate_definition_of_done` → `_generate_dod_report`)
- Add unit tests for each method
- **Checkpoint:** All DoD methods functional

**Afternoon (1-2h):**
- Integrate DoD into `_finalize_plan_execution()`
- Add config flag `enforce_dod`
- Test with real execution results (failing tests should block completion)
- Write integration tests
- **Checkpoint:** DoD enforcement working

**Documentation (30m):**
- Update Planning System User Guide with DoR/DoD sections
- Add troubleshooting guide for common violations
- Create quick reference card

---

## 📚 Related Documentation

**Planning System Manifest:**
- `cortex-brain/orchestrator-manifests/planning-system-manifest.yaml`
- Section: `quality_gates` → `definition_of_ready` and `definition_of_done`

**User Guide:**
- `cortex-brain/documents/implementation-guides/planning-system-user-guide.md`
- Section: "Quality Gates & Compliance"

**Architecture:**
- Phase 6 Completion Report: Quality gate requirements
- Brain Protection Rules: `PLANNING_QUALITY_ENFORCEMENT`

---

## 🚨 Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| DoR blocks valid plans | HIGH | LOW | Add override flag + granular checks |
| DoD false positives | MEDIUM | MEDIUM | Make thresholds configurable |
| Performance overhead | LOW | LOW | Cache validation results |
| Incomplete test data | MEDIUM | MEDIUM | Provide default values for missing metrics |

---

## 📊 Expected Outcomes

### Test Impact
- **Before:** 2,833/2,867 passing (98.8%)
- **After:** 2,833+/2,867 passing (98.8%+)
- **New Tests:** +17 tests (13 unit + 4 integration)

### Code Metrics
- **Lines Added:** ~320 LOC (13 methods × ~25 LOC avg)
- **Files Modified:** 1 (`planning_orchestrator.py`)
- **Files Created:** 1 (`test_planning_orchestrator_dor_dod.py`)

### Quality Improvements
- ✅ Quality gates enforced at plan start/completion
- ✅ Actionable feedback for non-compliant plans
- ✅ Automated compliance reporting
- ✅ Configurable enforcement (strict/permissive modes)

---

## ✅ Definition of Done (Meta)

This task is complete when:

1. ✅ All 13 methods implemented and functional
2. ✅ 17 tests passing (13 unit + 4 integration)
3. ✅ DoR/DoD enforced in planning workflow
4. ✅ Configuration flags working (override capability)
5. ✅ Reports generate actionable feedback
6. ✅ Documentation updated (user guide + manifest)
7. ✅ Code quality: Complexity ≤15, coverage ≥95%
8. ✅ Completion report published

---

**Author:** Asif Hussain  
**Created:** December 25, 2025  
**Status:** Ready for implementation
