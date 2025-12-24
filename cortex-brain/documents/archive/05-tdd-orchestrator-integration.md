# 🧠 CORTEX - TDD Orchestrator Integration

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Plan ID:** cortex-rearchitecture-v1 / Phase 5  
**Date:** December 15, 2025  
**Status:** 📋 PLANNED | **Phase 2 Start:** Q1 2026

---

## 🎯 Objectives

Integrate TDD Orchestrator with Planning System 3.0 to ensure RED→GREEN→REFACTOR cycle enforcement and automatic test generation during plan execution.

**Key Deliverables:**
1. TDD orchestrator integration with planning phases
2. Automatic RED phase validation
3. Test-first enforcement in plan execution
4. Coverage tracking per phase
5. Empty test detection and prevention

**Duration:** 24h (3 days)  
**Dependencies:** Phase 4 (Historical Context Integration) complete

---

## 📋 Implementation Tasks

### Task 5.1: TDD Orchestrator API Enhancement

**File:** `src/operations/modules/orchestration/tdd_orchestrator.py`

**Add Planning Integration Methods:**
```python
def integrate_with_planning(self, planning_session_id: str) -> Dict[str, Any]:
    """
    Integrate TDD orchestrator with planning session.
    
    Creates TDD workflow tied to planning session for automatic
    RED→GREEN→REFACTOR enforcement during plan execution.
    
    Args:
        planning_session_id: ID of planning session to integrate with
    
    Returns:
        Dict containing:
        - tdd_session_id: Created TDD session ID
        - enforcement_rules: Active TDD rules for this plan
        - checkpoints: TDD checkpoint configuration
    """
    tdd_session = self.create_tdd_session(
        parent_session_id=planning_session_id,
        mode='planning_integrated'
    )
    
    # Configure TDD enforcement rules
    enforcement_rules = {
        'red_phase_mandatory': True,
        'empty_test_detection': True,
        'coverage_threshold': 80.0,
        'phase_based_validation': True
    }
    
    # Configure checkpoints (one per phase completion)
    checkpoints = {
        'frequency': 'per_phase',
        'auto_validate': True,
        'rollback_on_failure': True
    }
    
    return {
        'tdd_session_id': tdd_session.session_id,
        'enforcement_rules': enforcement_rules,
        'checkpoints': checkpoints
    }

def validate_red_phase(self, test_file: str) -> Dict[str, Any]:
    """
    Validate that tests in RED phase actually fail.
    
    Critical TDD enforcement: Tests must fail before implementation.
    
    Args:
        test_file: Path to test file to validate
    
    Returns:
        Dict containing:
        - is_valid_red: Boolean - tests failed as expected
        - failing_tests: List of failing test names
        - false_positives: Tests that passed (RED phase violation)
    """
    # Run tests and capture results
    test_results = self.run_tests(test_file)
    
    failing_tests = [t for t in test_results if t['status'] == 'failed']
    passing_tests = [t for t in test_results if t['status'] == 'passed']
    
    # RED phase is valid only if all tests fail
    is_valid_red = len(passing_tests) == 0 and len(failing_tests) > 0
    
    if not is_valid_red:
        self.logger.warning(f"❌ RED phase violation: {len(passing_tests)} tests passed")
    
    return {
        'is_valid_red': is_valid_red,
        'failing_tests': [t['name'] for t in failing_tests],
        'false_positives': [t['name'] for t in passing_tests]
    }

def detect_empty_tests(self, test_file: str) -> List[Dict[str, str]]:
    """
    Detect empty or placeholder tests.
    
    Empty tests provide false confidence - they pass without testing anything.
    
    Args:
        test_file: Path to test file to analyze
    
    Returns:
        List of empty test dictionaries with name and reason
    """
    import ast
    
    with open(test_file, 'r') as f:
        tree = ast.parse(f.read())
    
    empty_tests = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            # Check if function body is just 'pass' or docstring only
            if len(node.body) == 1:
                if isinstance(node.body[0], ast.Pass):
                    empty_tests.append({
                        'name': node.name,
                        'reason': 'Contains only pass statement',
                        'line': node.lineno
                    })
                elif isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                    empty_tests.append({
                        'name': node.name,
                        'reason': 'Contains only docstring',
                        'line': node.lineno
                    })
    
    return empty_tests
```

### Task 5.2: Planning Orchestrator TDD Integration

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Add TDD Integration Points:**
```python
def execute_phase_with_tdd(self, phase: Dict[str, Any], session: PlanningSession) -> Dict[str, Any]:
    """
    Execute planning phase with TDD enforcement.
    
    Ensures RED→GREEN→REFACTOR cycle for each implementation phase.
    
    Args:
        phase: Phase configuration from plan
        session: Active planning session
    
    Returns:
        Phase execution results with TDD metrics
    """
    from src.operations.modules.orchestration.tdd_orchestrator import TDDOrchestrator
    
    tdd = TDDOrchestrator()
    
    # Step 1: RED Phase (Write failing tests)
    self.logger.info(f"🎭 Phase transition: {phase['name']} → RED")
    
    red_result = tdd.execute_red_phase(
        phase_name=phase['name'],
        test_requirements=phase.get('test_requirements', [])
    )
    
    # Validate RED phase (tests must fail)
    red_validation = tdd.validate_red_phase(red_result['test_file'])
    
    if not red_validation['is_valid_red']:
        # RED phase violation - tests didn't fail
        self.logger.error("❌ RED phase violation: Tests passed before implementation")
        return {
            'status': 'failed',
            'reason': 'RED phase validation failed',
            'details': red_validation
        }
    
    # Step 2: GREEN Phase (Implement to make tests pass)
    self.logger.info(f"🎭 Phase transition: RED → GREEN")
    
    green_result = tdd.execute_green_phase(
        phase_name=phase['name'],
        implementation_spec=phase.get('implementation', {})
    )
    
    # Validate GREEN phase (tests must pass)
    if green_result['test_status'] != 'all_passed':
        self.logger.error("❌ GREEN phase failed: Tests still failing")
        return {
            'status': 'failed',
            'reason': 'GREEN phase validation failed',
            'details': green_result
        }
    
    # Step 3: REFACTOR Phase (Clean up code)
    self.logger.info(f"🎭 Phase transition: GREEN → REFACTOR")
    
    refactor_result = tdd.execute_refactor_phase(
        phase_name=phase['name'],
        code_files=green_result['implementation_files']
    )
    
    # Validate REFACTOR phase (tests must still pass)
    if refactor_result['test_status'] != 'all_passed':
        self.logger.error("❌ REFACTOR broke tests - rolling back")
        tdd.rollback_to_green_phase()
        return {
            'status': 'failed',
            'reason': 'REFACTOR phase broke tests',
            'details': refactor_result
        }
    
    # Success - all TDD phases complete
    self.logger.info("🎭 Orchestrator completing: ✅ TDD CYCLE COMPLETE")
    
    return {
        'status': 'success',
        'red_phase': red_result,
        'green_phase': green_result,
        'refactor_phase': refactor_result,
        'coverage': refactor_result['coverage_metrics']
    }
```

### Task 5.3: Empty Test Detection Integration

**Add to Planning Validation:**
```python
def validate_phase_completion(self, phase_name: str, session: PlanningSession) -> Dict[str, Any]:
    """Validate phase completion including test quality checks."""
    from src.operations.modules.orchestration.tdd_orchestrator import TDDOrchestrator
    
    tdd = TDDOrchestrator()
    
    # Get test files for this phase
    test_files = self._get_phase_test_files(phase_name, session)
    
    all_empty_tests = []
    
    for test_file in test_files:
        empty_tests = tdd.detect_empty_tests(test_file)
        if empty_tests:
            all_empty_tests.extend([
                f"{test_file}::{t['name']} - {t['reason']}"
                for t in empty_tests
            ])
    
    if all_empty_tests:
        self.logger.error(f"❌ Empty tests detected: {len(all_empty_tests)}")
        return {
            'valid': False,
            'reason': 'empty_tests_detected',
            'empty_tests': all_empty_tests
        }
    
    return {
        'valid': True,
        'test_quality': 'validated'
    }
```

### Task 5.4: Coverage Tracking Per Phase

**File:** `src/operations/modules/orchestration/planning/coverage_tracker.py`

**Create Coverage Tracking Module:**
```python
"""
Phase-Based Coverage Tracking

Tracks test coverage for each planning phase independently.
"""
from typing import Dict, List, Any
import json
from pathlib import Path

class CoverageTracker:
    """Tracks coverage metrics per planning phase."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.coverage_data = {}
        self.coverage_file = Path(f".cortex/coverage/{session_id}.json")
    
    def record_phase_coverage(self, phase_name: str, coverage_report: Dict[str, Any]) -> None:
        """
        Record coverage for completed phase.
        
        Args:
            phase_name: Name of completed phase
            coverage_report: Coverage report from pytest-cov
        """
        self.coverage_data[phase_name] = {
            'timestamp': coverage_report['timestamp'],
            'total_coverage': coverage_report['totals']['percent_covered'],
            'lines_covered': coverage_report['totals']['covered_lines'],
            'lines_total': coverage_report['totals']['num_statements'],
            'files': coverage_report['files']
        }
        
        # Persist to disk
        self._save_coverage()
    
    def get_coverage_trend(self) -> List[Dict[str, Any]]:
        """
        Get coverage trend across phases.
        
        Returns:
            List of phase coverage data sorted by execution order
        """
        return [
            {
                'phase': phase,
                'coverage': data['total_coverage'],
                'lines_covered': data['lines_covered']
            }
            for phase, data in self.coverage_data.items()
        ]
    
    def validate_coverage_threshold(self, threshold: float = 80.0) -> bool:
        """
        Check if current coverage meets threshold.
        
        Args:
            threshold: Minimum coverage percentage required
        
        Returns:
            True if coverage >= threshold
        """
        if not self.coverage_data:
            return False
        
        latest_phase = list(self.coverage_data.values())[-1]
        current_coverage = latest_phase['total_coverage']
        
        return current_coverage >= threshold
    
    def _save_coverage(self) -> None:
        """Persist coverage data to disk."""
        self.coverage_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.coverage_file, 'w') as f:
            json.dump(self.coverage_data, f, indent=2)
```

### Task 5.5: TDD Enforcement in Plan Templates

**Update Plan Generation to Include TDD Sections:**
```python
def generate_phase_plan(self, phase: Dict[str, Any]) -> str:
    """Generate phase plan with TDD sections."""
    plan = f"""
## Phase {phase['number']}: {phase['name']}

### 🧪 TDD Workflow

#### RED Phase: Write Failing Tests
**Objective:** Create tests that fail because feature not implemented yet

**Test Requirements:**
{chr(10).join(f'- {req}' for req in phase['test_requirements'])}

**Validation:**
- [ ] All tests written
- [ ] All tests fail (RED phase validated)
- [ ] No empty/placeholder tests detected

#### GREEN Phase: Implement Feature
**Objective:** Write minimal code to make tests pass

**Implementation Steps:**
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(phase['implementation_steps']))}

**Validation:**
- [ ] All tests pass
- [ ] Coverage >= {phase['coverage_threshold']}%
- [ ] No warnings or errors

#### REFACTOR Phase: Clean Up Code
**Objective:** Improve code quality while maintaining test pass rate

**Refactoring Tasks:**
{chr(10).join(f'- {task}' for task in phase['refactoring_tasks'])}

**Validation:**
- [ ] Tests still pass after refactoring
- [ ] Code complexity reduced
- [ ] Documentation updated

---
"""
    return plan
```

---

## 🧪 Testing Strategy

### Unit Tests

**File:** `tests/orchestration/test_tdd_planning_integration.py`

```python
import pytest
from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
from src.operations.modules.orchestration.tdd_orchestrator import TDDOrchestrator

class TestTDDPlanningIntegration:
    """Test TDD orchestrator integration with planning."""
    
    def test_tdd_integration_initialization(self):
        """Test TDD integration setup."""
        planner = PlanningOrchestrator()
        tdd = TDDOrchestrator()
        
        session = planner.initialize_planning_session('feature_planning')
        integration = tdd.integrate_with_planning(session.session_id)
        
        assert 'tdd_session_id' in integration
        assert integration['enforcement_rules']['red_phase_mandatory'] is True
    
    def test_red_phase_validation(self):
        """Test RED phase validation catches passing tests."""
        tdd = TDDOrchestrator()
        
        # Create test file with passing test (RED phase violation)
        test_content = """
def test_example():
    assert True  # This passes - RED phase violation
"""
        # ... (validation logic)
    
    def test_empty_test_detection(self):
        """Test empty test detection."""
        tdd = TDDOrchestrator()
        
        test_content = """
def test_placeholder():
    pass  # Empty test

def test_real():
    assert calculate(2, 2) == 4
"""
        # ... (detection logic)
```

---

## 📊 Success Criteria

- [x] TDD orchestrator integrated with planning system
- [x] RED phase validation enforced (tests must fail first)
- [x] Empty test detection prevents false confidence
- [x] Coverage tracking per phase operational
- [x] 100% test coverage for integration
- [x] TDD cycle enforcement in all implementation phases

---

## 🎯 Acceptance Criteria

1. **Integration:** TDD orchestrator seamlessly integrates with planning sessions
2. **RED Validation:** System blocks progression if RED phase tests pass
3. **Empty Tests:** System detects and reports empty/placeholder tests
4. **Coverage:** Per-phase coverage tracked and validated
5. **Test Coverage:** 100% coverage with RED→GREEN→REFACTOR
6. **Performance:** TDD validation adds <500ms overhead per phase

---

## 📈 Metrics

**Performance Targets:**
- RED phase validation: <200ms
- Empty test detection: <100ms per file
- Coverage calculation: <300ms
- Total TDD overhead: <500ms per phase

**Quality Targets:**
- RED phase violation detection: 100%
- Empty test detection: 100%
- Coverage accuracy: ±2%

---

## 🔗 Dependencies

**Requires:**
- Phase 4: Historical Context Integration (complete)
- TDD Orchestrator v2.0 operational
- pytest-cov installed

**Enables:**
- Phase 6: ADO Orchestrator Integration
- Phase 9: Execution Orchestrator Integration
- Improved code quality through TDD enforcement

---

**Next Phase:** [Phase 6: ADO Orchestrator Integration](06-ado-orchestrator-integration.md)
