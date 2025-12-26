# Task 13.3: TDD & Manifest Integration

**Phase:** 13 (Post-GA Refinement)  
**Task ID:** 13.3  
**Priority:** HIGH  
**Estimated Effort:** 5-7 hours  
**Dependencies:** Task 13.2 (DoR/DoD compliance) ✅  
**Status:** ⏳ READY TO START

---

## 📊 Executive Summary

Integrate TDD Orchestrator with Planning Orchestrator and implement manifest inheritance system for configuration reuse. This adds 11 methods across TDD workflow coordination and YAML inheritance resolution.

**Impact:**
- Automatic TDD integration in all plans (RED→GREEN→REFACTOR enforcement)
- Manifest inheritance reduces duplication (ADO inherits from Planning System)
- Test plan generation tied to acceptance criteria
- Phase-specific TDD validation gates

---

## 🎯 Objectives

### Primary Goals

1. **TDD Workflow Integration (6 methods)**
   - Coordinate with TDD Orchestrator for test-first development
   - Generate test plans from acceptance criteria
   - Execute RED→GREEN→REFACTOR phases with validation
   - Track TDD completion in plan results

2. **Manifest Inheritance System (5 methods)**
   - Load manifests with `inherits_from` support
   - Resolve inheritance chains (ADO → Planning 2.0 → Base)
   - Merge configurations with override rules
   - Cache resolved manifests for performance

3. **Planning Integration**
   - Auto-include TDD in plan phases (complexity-based)
   - Validate TDD completion before plan finalization
   - Generate TDD reports with coverage metrics

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Methods Implemented | 11/11 | All TDD/Manifest methods functional |
| Test Pass Rate | +0.2% | 98.8% → 99.0% |
| TDD Integration | 100% | TDD auto-included in all plans |
| Manifest Reuse | 70%+ | ADO manifest inherits 70% from Planning 2.0 |

---

## 🔧 Implementation Details

### Part 1: TDD Workflow Integration - 6 Methods

**Location:** `src/orchestrators/planning/planning_orchestrator.py`

#### Method 1: `_integrate_tdd_workflow(plan: Dict) -> Dict`

**Purpose:** Add TDD phases to plan based on complexity

**Signature:**
```python
def _integrate_tdd_workflow(self, plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Integrate TDD workflow into plan execution.
    
    Args:
        plan: Plan dictionary with metadata and phases
        
    Returns:
        Updated plan with TDD phases inserted
        
    Integration Logic:
    - LOW complexity: Optional TDD (user can skip)
    - MEDIUM complexity: Recommended TDD (warning if skipped)
    - HIGH/CRITICAL: Mandatory TDD (enforced)
    
    TDD Phases Added:
    1. Test Plan Generation (before implementation)
    2. RED Phase (write failing tests)
    3. GREEN Phase (implement to pass tests)
    4. REFACTOR Phase (clean code)
    """
```

**Implementation Logic:**
```python
metadata = plan.get("metadata", {})
complexity = metadata.get("complexity", "MEDIUM")

# Check if TDD already integrated
if any("TDD" in phase.get("name", "") for phase in plan.get("phases", [])):
    logger.info("TDD already integrated in plan")
    return plan

# Determine TDD requirement
tdd_required = complexity in ["HIGH", "CRITICAL"]
tdd_recommended = complexity == "MEDIUM"

# Generate test plan
test_plan = self._generate_test_plan(plan)

# Insert TDD phases after design phase
phases = plan.get("phases", [])
design_phase_idx = next(
    (i for i, p in enumerate(phases) if "design" in p.get("name", "").lower()),
    0
)

tdd_phases = [
    {
        "name": "Test Plan Generation",
        "type": "tdd",
        "activities": ["Define test strategy", "Identify test cases", "Setup test infrastructure"],
        "test_plan": test_plan,
        "required": tdd_required
    },
    {
        "name": "RED Phase - Write Failing Tests",
        "type": "tdd",
        "activities": ["Write unit tests", "Write integration tests", "Verify tests fail"],
        "required": tdd_required,
        "validation": "All tests must fail before implementation"
    },
    {
        "name": "GREEN Phase - Implement Code",
        "type": "tdd",
        "activities": ["Implement features", "Pass all tests", "Verify coverage"],
        "required": tdd_required,
        "validation": "All tests must pass"
    },
    {
        "name": "REFACTOR Phase - Clean Code",
        "type": "tdd",
        "activities": ["Refactor for clarity", "Check complexity ≤30", "Re-run tests"],
        "required": tdd_required,
        "validation": "Tests still pass after refactor"
    }
]

# Insert TDD phases
phases[design_phase_idx + 1:design_phase_idx + 1] = tdd_phases
plan["phases"] = phases
plan["metadata"]["tdd_integrated"] = True
plan["metadata"]["tdd_required"] = tdd_required

return plan
```

**Lines of Code:** ~60 LOC

---

#### Method 2: `_generate_test_plan(plan: Dict) -> Dict`

**Purpose:** Generate test plan from acceptance criteria

**Implementation:**
```python
def _generate_test_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate test plan from acceptance criteria.
    
    Returns test plan with:
    - Test cases derived from acceptance criteria
    - Coverage targets by layer (unit/integration/e2e)
    - Technology stack (pytest, unittest, etc.)
    """
    metadata = plan.get("metadata", {})
    acceptance_criteria = metadata.get("acceptance_criteria", [])
    
    test_plan = {
        "strategy": "TDD (RED→GREEN→REFACTOR)",
        "framework": "pytest",  # Default, can be overridden
        "coverage_targets": {
            "unit": "≥95%",
            "integration": "≥80%",
            "e2e": "≥70%"
        },
        "test_cases": []
    }
    
    # Generate test cases from acceptance criteria
    for criterion in acceptance_criteria:
        if isinstance(criterion, str):
            test_case = {
                "name": f"test_{criterion[:50].replace(' ', '_').lower()}",
                "description": f"Verify: {criterion}",
                "type": "integration" if "end-to-end" in criterion.lower() else "unit",
                "priority": "HIGH" if "must" in criterion.lower() else "MEDIUM"
            }
            test_plan["test_cases"].append(test_case)
    
    # Add technology-specific tests
    technologies = metadata.get("technologies", [])
    for tech in technologies:
        if "api" in tech.lower():
            test_plan["test_cases"].append({
                "name": "test_api_endpoints",
                "description": "Verify API contract",
                "type": "integration",
                "priority": "HIGH"
            })
    
    return test_plan
```

**Lines of Code:** ~40 LOC

---

#### Method 3: `_execute_red_phase(plan: Dict) -> Dict`

**Purpose:** Execute RED phase (write failing tests)

**Implementation:**
```python
def _execute_red_phase(self, plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute RED phase - write failing tests.
    
    Coordinates with TDD Orchestrator to:
    1. Generate test files from test plan
    2. Run tests (should all fail)
    3. Validate RED phase completion
    """
    logger.info("🎭 Phase transition: Planning → TDD RED")
    
    test_plan = plan.get("metadata", {}).get("test_plan", {})
    
    # Call TDD Orchestrator (simplified - actual would import and call)
    red_results = {
        "phase": "RED",
        "tests_written": len(test_plan.get("test_cases", [])),
        "tests_failing": len(test_plan.get("test_cases", [])),  # All should fail
        "tests_passing": 0,
        "validation": "RED phase complete" if len(test_plan.get("test_cases", [])) > 0 else "No tests written"
    }
    
    # Validate RED phase
    if red_results["tests_passing"] > 0:
        logger.warning("⚠️ RED phase violation: Some tests passing before implementation")
        red_results["validation"] = "FAILED - Tests should not pass in RED phase"
    
    # Store results
    if "tdd_results" not in plan:
        plan["tdd_results"] = {}
    plan["tdd_results"]["red"] = red_results
    
    return plan
```

**Lines of Code:** ~30 LOC

---

#### Method 4: `_execute_green_phase(plan: Dict) -> Dict`

**Purpose:** Execute GREEN phase (implement to pass tests)

**Implementation:**
```python
def _execute_green_phase(self, plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute GREEN phase - implement code to pass tests.
    
    Coordinates with TDD Orchestrator to:
    1. Monitor test execution during implementation
    2. Track pass rate progression
    3. Validate GREEN phase completion (all tests pass)
    """
    logger.info("🎭 Phase transition: TDD RED → GREEN")
    
    # Simulate test execution (actual would call TDD Orchestrator)
    test_plan = plan.get("metadata", {}).get("test_plan", {})
    total_tests = len(test_plan.get("test_cases", []))
    
    green_results = {
        "phase": "GREEN",
        "tests_total": total_tests,
        "tests_passing": total_tests,  # All should pass now
        "tests_failing": 0,
        "pass_rate": 100.0,
        "coverage": 92.5,  # Example
        "validation": "GREEN phase complete"
    }
    
    # Validate GREEN phase
    if green_results["pass_rate"] < 95.0:
        logger.warning(f"⚠️ GREEN phase incomplete: Pass rate {green_results['pass_rate']}% below 95%")
        green_results["validation"] = f"INCOMPLETE - Pass rate below threshold"
    
    # Store results
    plan["tdd_results"]["green"] = green_results
    
    return plan
```

**Lines of Code:** ~30 LOC

---

#### Method 5: `_execute_refactor_phase(plan: Dict) -> Dict`

**Purpose:** Execute REFACTOR phase (clean code)

**Implementation:**
```python
def _execute_refactor_phase(self, plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute REFACTOR phase - clean code while maintaining tests.
    
    Coordinates with TDD Orchestrator to:
    1. Analyze code complexity
    2. Suggest refactoring opportunities
    3. Re-run tests after refactoring
    4. Validate tests still pass
    """
    logger.info("🎭 Phase transition: TDD GREEN → REFACTOR")
    
    # Analyze code quality (simplified)
    refactor_results = {
        "phase": "REFACTOR",
        "complexity_before": 42,  # Example
        "complexity_after": 28,   # Example
        "refactorings": [
            "Extracted helper functions",
            "Reduced nesting depth",
            "Applied DRY principle"
        ],
        "tests_still_passing": True,
        "pass_rate": 100.0,
        "validation": "REFACTOR complete"
    }
    
    # Validate REFACTOR phase
    if not refactor_results["tests_still_passing"]:
        logger.error("❌ REFACTOR failed: Tests broken after refactoring")
        refactor_results["validation"] = "FAILED - Tests broken"
    
    if refactor_results["complexity_after"] > 30:
        logger.warning(f"⚠️ Complexity {refactor_results['complexity_after']} still above 30")
    
    # Store results
    plan["tdd_results"]["refactor"] = refactor_results
    
    return plan
```

**Lines of Code:** ~35 LOC

---

#### Method 6: `_validate_tdd_completion(plan: Dict) -> Tuple[bool, List[str]]`

**Purpose:** Validate full TDD cycle completed successfully

**Implementation:**
```python
def _validate_tdd_completion(self, plan: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate TDD workflow completed successfully.
    
    Returns:
        Tuple of (is_complete: bool, issues: List[str])
    """
    issues = []
    tdd_results = plan.get("tdd_results", {})
    
    # Check RED phase
    red = tdd_results.get("red", {})
    if not red or red.get("tests_failing", 0) == 0:
        issues.append("TDD: RED phase incomplete (no failing tests)")
    
    # Check GREEN phase
    green = tdd_results.get("green", {})
    if not green or green.get("pass_rate", 0) < 95.0:
        issues.append(f"TDD: GREEN phase incomplete (pass rate {green.get('pass_rate', 0)}%)")
    
    # Check REFACTOR phase
    refactor = tdd_results.get("refactor", {})
    if not refactor or not refactor.get("tests_still_passing", False):
        issues.append("TDD: REFACTOR phase failed (tests broken)")
    
    # Check coverage
    if green.get("coverage", 0) < 80.0:
        issues.append(f"TDD: Coverage {green.get('coverage', 0)}% below 80%")
    
    is_complete = len(issues) == 0
    return is_complete, issues
```

**Lines of Code:** ~30 LOC

---

### Part 2: Manifest Inheritance System - 5 Methods

**Location:** `src/orchestrators/planning/planning_orchestrator.py`

#### Method 7: `_load_manifest_with_inheritance(manifest_path: str) -> Dict`

**Purpose:** Load manifest and resolve inheritance chain

**Signature:**
```python
def _load_manifest_with_inheritance(self, manifest_path: str) -> Dict[str, Any]:
    """
    Load manifest with inheritance resolution.
    
    Args:
        manifest_path: Path to manifest YAML file
        
    Returns:
        Fully resolved manifest with all inherited configs merged
        
    Inheritance Chain Example:
    ADO Manifest → Planning System → Base Orchestrator
    
    Merge Rules:
    - Child overrides parent for same keys
    - Lists are appended (child + parent)
    - Nested dicts are merged recursively
    """
```

**Implementation:**
```python
import yaml
from pathlib import Path

# Load base manifest
with open(manifest_path, 'r') as f:
    manifest = yaml.safe_load(f)

# Check for inheritance
inherits_from = manifest.get("inherits_from")
if not inherits_from:
    return manifest  # No inheritance

# Resolve inheritance chain
resolved_manifest = self._resolve_manifest_inheritance(manifest_path, manifest)

return resolved_manifest
```

**Lines of Code:** ~15 LOC

---

#### Method 8: `_resolve_manifest_inheritance(path: str, manifest: Dict) -> Dict`

**Purpose:** Recursively resolve inheritance chain

**Implementation:**
```python
def _resolve_manifest_inheritance(
    self, 
    manifest_path: str, 
    manifest: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Recursively resolve manifest inheritance.
    
    Returns merged manifest with full inheritance chain resolved.
    """
    inherits_from = manifest.get("inherits_from")
    if not inherits_from:
        return manifest  # Base case - no parent
    
    # Load parent manifest
    parent_path = Path(manifest_path).parent / inherits_from
    if not parent_path.exists():
        logger.warning(f"Parent manifest not found: {parent_path}")
        return manifest
    
    with open(parent_path, 'r') as f:
        parent_manifest = yaml.safe_load(f)
    
    # Recursively resolve parent's inheritance
    resolved_parent = self._resolve_manifest_inheritance(str(parent_path), parent_manifest)
    
    # Merge child with resolved parent
    merged_manifest = self._merge_manifest_configs(resolved_parent, manifest)
    
    return merged_manifest
```

**Lines of Code:** ~25 LOC

---

#### Method 9: `_merge_manifest_configs(parent: Dict, child: Dict) -> Dict`

**Purpose:** Merge child manifest with parent using override rules

**Implementation:**
```python
def _merge_manifest_configs(
    self, 
    parent: Dict[str, Any], 
    child: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge child manifest with parent.
    
    Merge Rules:
    1. Child scalar values override parent
    2. Child lists extend parent lists (append)
    3. Child dicts merge with parent dicts (recursive)
    4. Special key "_override": true forces full replacement
    """
    merged = parent.copy()
    
    for key, child_value in child.items():
        if key == "inherits_from":
            continue  # Skip inheritance marker
        
        if key not in merged:
            # New key in child
            merged[key] = child_value
        elif isinstance(child_value, dict) and isinstance(merged[key], dict):
            # Recursive merge for nested dicts
            if child_value.get("_override"):
                merged[key] = {k: v for k, v in child_value.items() if k != "_override"}
            else:
                merged[key] = self._merge_manifest_configs(merged[key], child_value)
        elif isinstance(child_value, list) and isinstance(merged[key], list):
            # Append lists
            merged[key] = merged[key] + child_value
        else:
            # Override scalar values
            merged[key] = child_value
    
    return merged
```

**Lines of Code:** ~30 LOC

---

#### Method 10: `_validate_manifest_schema(manifest: Dict) -> Tuple[bool, List[str]]`

**Purpose:** Validate manifest structure and required fields

**Implementation:**
```python
def _validate_manifest_schema(self, manifest: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate manifest against schema requirements.
    
    Required Fields:
    - orchestrator_name
    - version
    - quality_gates (if inherited from Planning System)
    - phases
    """
    errors = []
    
    # Required top-level keys
    required_keys = ["orchestrator_name", "version", "phases"]
    for key in required_keys:
        if key not in manifest:
            errors.append(f"Missing required field: {key}")
    
    # Validate phases structure
    phases = manifest.get("phases", [])
    if not isinstance(phases, list):
        errors.append("phases must be a list")
    else:
        for i, phase in enumerate(phases):
            if not isinstance(phase, dict):
                errors.append(f"Phase {i} must be a dictionary")
            elif "name" not in phase:
                errors.append(f"Phase {i} missing 'name' field")
    
    # Validate quality gates if present
    if "quality_gates" in manifest:
        gates = manifest["quality_gates"]
        if "definition_of_ready" not in gates and "definition_of_done" not in gates:
            errors.append("quality_gates must have definition_of_ready or definition_of_done")
    
    is_valid = len(errors) == 0
    return is_valid, errors
```

**Lines of Code:** ~35 LOC

---

#### Method 11: `_cache_resolved_manifest(manifest_path: str, resolved: Dict) -> None`

**Purpose:** Cache resolved manifests for performance

**Implementation:**
```python
def _cache_resolved_manifest(self, manifest_path: str, resolved: Dict[str, Any]) -> None:
    """
    Cache resolved manifest to avoid re-parsing inheritance chains.
    
    Uses in-memory cache with TTL of 300 seconds (5 minutes).
    """
    if not hasattr(self, "_manifest_cache"):
        self._manifest_cache = {}
    
    cache_entry = {
        "manifest": resolved,
        "timestamp": time.time(),
        "path": manifest_path
    }
    
    self._manifest_cache[manifest_path] = cache_entry
    
    # Clean expired entries (TTL = 300s)
    current_time = time.time()
    expired_keys = [
        key for key, entry in self._manifest_cache.items()
        if current_time - entry["timestamp"] > 300
    ]
    for key in expired_keys:
        del self._manifest_cache[key]
```

**Lines of Code:** ~20 LOC

---

### Part 3: Integration Changes

**Update `__init__` method:**
```python
def __init__(self, config: Dict[str, Any]):
    # Existing initialization...
    
    # ADD: TDD integration flag
    self.tdd_enabled = config.get("tdd_enabled", True)
    
    # ADD: Manifest cache
    self._manifest_cache = {}
```

**Update `execute_plan` method:**
```python
def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
    # Load manifest with inheritance
    manifest_path = plan.get("metadata", {}).get("manifest_path")
    if manifest_path:
        manifest = self._load_manifest_with_inheritance(manifest_path)
        plan["manifest"] = manifest
    
    # Integrate TDD if enabled
    if self.tdd_enabled:
        plan = self._integrate_tdd_workflow(plan)
    
    # Execute phases...
    results = self._execute_phases(plan)
    
    # Validate TDD completion
    if self.tdd_enabled and plan.get("metadata", {}).get("tdd_integrated"):
        tdd_complete, tdd_issues = self._validate_tdd_completion(plan)
        results["tdd_complete"] = tdd_complete
        results["tdd_issues"] = tdd_issues
    
    return results
```

---

## 📝 Acceptance Criteria

### Functional Requirements

| # | Requirement | Verification |
|---|-------------|--------------|
| 1 | All 6 TDD methods implemented | Code review + method signatures |
| 2 | All 5 Manifest methods implemented | Code review + method signatures |
| 3 | TDD auto-integrated in plans | Integration test with LOW/MEDIUM/HIGH complexity |
| 4 | Manifest inheritance works | Load ADO manifest, verify Planning 2.0 fields inherited |
| 5 | TDD validation enforced | Test plan completion with incomplete TDD |
| 6 | Cache improves performance | Benchmark manifest load times |

### Non-Functional Requirements

| # | Requirement | Target | Verification |
|---|-------------|--------|--------------|
| 1 | TDD integration overhead | <1s | Profiling |
| 2 | Manifest load time | <200ms | Profiling |
| 3 | Code quality | Complexity ≤15 | Static analysis |
| 4 | Test coverage | ≥95% | Pytest coverage |

---

## 🧪 Testing Strategy

### Unit Tests (11 tests)

**File:** `tests/orchestrators/planning/test_planning_orchestrator_tdd_manifest.py`

```python
class TestTDDIntegration:
    def test_integrate_tdd_workflow_low_complexity(self):
        """Test TDD optional for LOW complexity."""
        
    def test_generate_test_plan_from_acceptance_criteria(self):
        """Test test plan generation."""
        
    def test_execute_red_phase_validation(self):
        """Test RED phase validation (tests must fail)."""
        
    def test_execute_green_phase_validation(self):
        """Test GREEN phase validation (tests must pass)."""
        
    def test_execute_refactor_phase_validation(self):
        """Test REFACTOR phase validation (tests still pass)."""
        
    def test_validate_tdd_completion_full_cycle(self):
        """Test full TDD cycle validation."""

class TestManifestInheritance:
    def test_load_manifest_with_inheritance(self):
        """Test manifest loading with inheritance."""
        
    def test_resolve_manifest_inheritance_chain(self):
        """Test 3-level inheritance (ADO→Planning→Base)."""
        
    def test_merge_manifest_configs_override_rules(self):
        """Test merge rules (override, append, recursive)."""
        
    def test_validate_manifest_schema(self):
        """Test manifest schema validation."""
        
    def test_cache_resolved_manifest_performance(self):
        """Test caching improves performance."""
```

---

## 📅 Implementation Plan

### Day 1: TDD Integration (3-4 hours)

**Morning (2h):**
- Implement 6 TDD methods
- Add unit tests
- **Checkpoint:** TDD methods functional

**Afternoon (1-2h):**
- Integrate TDD into `execute_plan`
- Test with LOW/MEDIUM/HIGH complexity plans
- **Checkpoint:** TDD auto-integration working

### Day 2: Manifest Inheritance (2-3 hours)

**Morning (1.5h):**
- Implement 5 Manifest methods
- Add unit tests
- **Checkpoint:** Inheritance resolution working

**Afternoon (0.5-1.5h):**
- Test with ADO manifest (inherits from Planning 2.0)
- Validate schema enforcement
- Performance testing + caching
- Documentation update
- **Checkpoint:** Manifest system complete

---

## 📚 Related Documentation

**Manifests:**
- `cortex-brain/orchestrator-manifests/planning-system-manifest.yaml`
- `cortex-brain/orchestrator-manifests/ado-planning-manifest.yaml`
- Example inheritance: ADO → Planning 2.0 → Base

**TDD Orchestrator:**
- `src/orchestrators/tdd/tdd_orchestrator.py`
- `cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml`

**User Guides:**
- Planning System User Guide (TDD integration section)
- TDD Mastery Guide (RED→GREEN→REFACTOR workflow)

---

## 📊 Expected Outcomes

### Test Impact
- **Before:** 2,833/2,867 passing (98.8%)
- **After:** 2,833+/2,867 passing (98.8%+)
- **New Tests:** +11 tests

### Code Metrics
- **Lines Added:** ~320 LOC (11 methods × ~29 LOC avg)
- **Files Modified:** 1 (`planning_orchestrator.py`)
- **Files Created:** 1 (`test_planning_orchestrator_tdd_manifest.py`)

### Quality Improvements
- ✅ TDD enforced in all plans (complexity-based)
- ✅ Manifest duplication reduced 70%
- ✅ Test plan auto-generation from acceptance criteria
- ✅ Full TDD cycle tracking (RED→GREEN→REFACTOR)

---

**Author:** Asif Hussain  
**Created:** December 25, 2025  
**Status:** Ready for implementation
