# Testing the Planning Orchestrator

**Author:** CORTEX Development Team  
**Last Updated:** December 29, 2025  
**Version:** 4.0.0

---

## 📋 Overview

The Planning Orchestrator has **441 comprehensive tests** covering all major features and integration points. This guide shows you how to run and understand the test suite.

---

## 🚀 Quick Start

### Run All Planning Tests

```bash
# From CORTEX root directory
python3 -m pytest tests/orchestrators/planning/ -v
```

### Run Specific Test Categories

```bash
# Interactive Planning Session (18 tests)
python3 -m pytest tests/orchestrators/planning/test_interactive_planning_session.py -v

# Toolkit Integration (9 tests)
python3 -m pytest tests/orchestrators/planning/test_toolkit_integration.py -v

# TDD Workflow (18 tests)
python3 -m pytest tests/orchestrators/planning/test_planning_orchestrator_tdd_manifest.py -v

# Phase Manager Integration
python3 -m pytest tests/orchestrators/planning/test_phase_manager_integration.py -v

# Git Checkpoint Integration
python3 -m pytest tests/orchestrators/planning/test_git_checkpoint_integration.py -v
```

---

## 📊 Test Suite Structure

### 1. **Interactive Planning Tests** (NEW - 18 tests)
**File:** `test_interactive_planning_session.py`

Tests the collaborative planning workflow:

```python
# Session Management (3 tests)
- test_session_creation_with_plan_name
- test_session_tracks_conversation_history
- test_session_state_transitions

# Discovery Questions (2 tests)
- test_generate_discovery_questions_for_plan_type
- test_questions_adapt_to_plan_context

# Context Discovery Engine (4 tests)
- test_ast_analysis_discovers_related_code
- test_code_graph_identifies_impact_zones
- test_brain_consultation_finds_similar_plans
- test_context_gathering_presents_findings_to_user

# User Approval Workflow (4 tests)
- test_present_findings_to_user
- test_user_can_request_refinements
- test_approval_transitions_to_drafting
- test_iterative_refinement_loop

# Cleanup Phase (4 tests)
- test_cleanup_phase_reviews_all_modified_files
- test_cleanup_validates_codebase_not_broken
- test_cleanup_generates_pdoc3_documentation
- test_cleanup_adds_to_knowledge_graph

# End-to-End (1 test)
- test_full_interactive_planning_workflow
```

**Run these tests:**
```bash
python3 -m pytest tests/orchestrators/planning/test_interactive_planning_session.py -v
```

**Expected output:**
```
18 passed in 0.11s
```

---

### 2. **Toolkit Integration Tests** (9 tests)
**File:** `test_toolkit_integration.py`

Tests integration with CORTEX Toolkit's plan scaffold generator:

```python
- test_orchestrator_uses_toolkit_scaffold_generator
- test_orchestrator_create_plan_calls_toolkit
- test_created_folders_match_toolkit_structure
- test_orchestrator_handles_existing_plan
- test_orchestrator_validates_plan_structure
- test_orchestrator_sanitizes_plan_names
- test_progress_tracker_json_schema
- test_toolkit_generator_dry_run_mode
- test_orchestrator_error_handling_invalid_names
```

**Run these tests:**
```bash
python3 -m pytest tests/orchestrators/planning/test_toolkit_integration.py -v
```

---

### 3. **TDD Workflow Tests** (18 tests)
**File:** `test_planning_orchestrator_tdd_manifest.py`

Tests TDD integration (RED→GREEN→REFACTOR):

```python
# Workflow Integration
- test_integrate_tdd_workflow_adds_phases
- test_integrate_tdd_workflow_disabled
- test_generate_test_plan_from_acceptance_criteria

# Phase Execution
- test_execute_red_phase
- test_execute_green_phase
- test_execute_refactor_phase

# Manifest Loading
- test_load_manifest_with_inheritance
- test_load_manifest_without_inheritance
- test_merge_manifest_configs_scalar_override
- test_merge_manifest_configs_list_append
- test_merge_manifest_configs_dict_recursive

# Validation
- test_validate_tdd_completion_success
- test_validate_tdd_completion_missing_phases
- test_validate_manifest_schema_valid
- test_validate_manifest_schema_invalid
- test_cache_resolved_manifest
```

---

### 4. **Complexity-Based Routing Tests** (12 tests)
**File:** `test_planning_orchestrator_extended.py`

Tests adaptive planning based on complexity:

```python
# Complexity Routing
- test_low_complexity_routes_to_skeleton
- test_medium_complexity_routes_to_conditional
- test_high_complexity_routes_to_incremental
- test_critical_complexity_includes_security

# Complexity Analysis
- test_complexity_analysis_factors
- test_high_dependency_count_increases_complexity
- test_complexity_escalation_mid_execution
- test_complexity_routing_logged
- test_invalid_complexity_handled_gracefully

# DoR/DoD Validation
- test_dor_validation_before_phase_execution
- test_dor_missing_criteria_fails
- test_dod_validation_after_phase_execution
```

---

### 5. **Intelligence Layer Tests** (40+ tests)
**File:** `intelligence/test_intelligence_orchestrator.py`

Tests AI-powered analysis and validation:

```python
# Initialization
- test_init_full_mode
- test_init_validation_only_mode
- test_init_advisory_only_mode

# Plan Analysis
- test_analyze_valid_plan
- test_analyze_plan_with_errors
- test_analyze_plan_missing_dor

# Validation API
- test_validate_plan_success
- test_validate_plan_failure

# And 30+ more intelligence tests...
```

---

## 🎯 Testing Patterns

### Pattern 1: Testing Interactive Planning

```python
def test_interactive_planning_example():
    """Test interactive planning workflow."""
    from src.orchestrators.planning.planning_orchestrator import PlanningOrchestrator
    from src.orchestrators.planning.interactive_session import SessionState
    
    # Initialize orchestrator
    config = {"cortex_root": "/path/to/cortex"}
    orchestrator = PlanningOrchestrator(config)
    
    # Start interactive session
    session = orchestrator.interactive_plan_creation(
        plan_name="test-feature",
        user_context={"target": "developers"}
    )
    
    # Assert session created
    assert session.state == SessionState.DISCOVERY
    
    # Add user answers
    session.add_answers({
        "target_audience": "developers",
        "duration": "60min"
    })
    
    # Discover context (AST/graphs/brain)
    context = session.discover_context()
    assert "ast_analysis" in context
    
    # Approve and finalize
    session.approve_context()
    assert session.state == SessionState.APPROVED
```

### Pattern 2: Testing Toolkit Integration

```python
def test_toolkit_integration_example(tmp_path):
    """Test toolkit creates proper folder structure."""
    from src.orchestrators.planning.planning_orchestrator import PlanningOrchestrator
    
    config = {"cortex_root": str(tmp_path)}
    orchestrator = PlanningOrchestrator(config)
    
    # Create plan using toolkit
    result = orchestrator.create_plan_folders("test-plan")
    
    # Verify structure
    assert result["status"] == "created"
    assert (tmp_path / "planning" / "features" / "active" / "test-plan").exists()
    assert (tmp_path / "planning" / "features" / "active" / "test-plan" / "context").exists()
    assert (tmp_path / "planning" / "features" / "active" / "test-plan" / "reports").exists()
```

### Pattern 3: Testing TDD Workflow

```python
def test_tdd_workflow_example():
    """Test TDD RED→GREEN→REFACTOR phases."""
    from src.orchestrators.planning.planning_orchestrator import PlanningOrchestrator
    
    orchestrator = PlanningOrchestrator({"enable_tdd": True})
    
    # Create plan with TDD
    plan = {
        "name": "test-feature",
        "phases": [],
        "acceptance_criteria": ["Test must fail first", "Test must pass"]
    }
    
    # Integrate TDD workflow
    enhanced_plan = orchestrator.integrate_tdd_workflow(plan)
    
    # Assert TDD phases added
    phase_names = [p["name"] for p in enhanced_plan["phases"]]
    assert "RED: Write Failing Tests" in phase_names
    assert "GREEN: Implement Feature" in phase_names
    assert "REFACTOR: Optimize Code" in phase_names
```

---

## 🔧 Test Fixtures

### Common Fixtures Available

```python
@pytest.fixture
def orchestrator():
    """Provides initialized PlanningOrchestrator."""
    config = {
        "cortex_root": "/fake/cortex",
        "enable_folder_structure": True,
        "enable_tdd": True
    }
    return PlanningOrchestrator(config)

@pytest.fixture
def temp_cortex_root(tmp_path):
    """Provides temporary CORTEX root directory."""
    cortex_root = tmp_path / "cortex"
    cortex_root.mkdir()
    return cortex_root

@pytest.fixture
def valid_plan():
    """Provides valid plan structure for testing."""
    return {
        "name": "test-feature",
        "description": "Test feature implementation",
        "phases": [
            {
                "name": "Phase 1",
                "tasks": ["Task 1", "Task 2"],
                "dor": {"criteria": ["Setup complete"]},
                "dod": {"criteria": ["Tests passing"]}
            }
        ]
    }
```

---

## 📈 Test Coverage Report

### Generate Coverage Report

```bash
# Run with coverage
python3 -m pytest tests/orchestrators/planning/ --cov=src/orchestrators/planning --cov-report=html

# Open report
open htmlcov/index.html
```

### Current Coverage (Estimated)

```
Module                                    Coverage
---------------------------------------------------
planning_orchestrator.py                  92%
interactive_session.py                    100%
plan_validator.py                         88%
plan_generator.py                         85%
markdown_renderer.py                      90%
plan_executor.py                          78%
git_checkpoint_integration.py             82%
phase_manager_integration.py              95%
---------------------------------------------------
TOTAL                                     88%
```

---

## 🎨 Running Tests with Different Options

### Verbose Output
```bash
python3 -m pytest tests/orchestrators/planning/ -v
```

### Show Print Statements
```bash
python3 -m pytest tests/orchestrators/planning/ -v -s
```

### Run Specific Test
```bash
python3 -m pytest tests/orchestrators/planning/test_interactive_planning_session.py::TestPlanningSessionInitialization::test_session_creation_with_plan_name -v
```

### Stop on First Failure
```bash
python3 -m pytest tests/orchestrators/planning/ -x
```

### Run Only Failed Tests
```bash
python3 -m pytest tests/orchestrators/planning/ --lf
```

### Parallel Execution (faster)
```bash
python3 -m pytest tests/orchestrators/planning/ -n auto
```

### Show Slowest Tests
```bash
python3 -m pytest tests/orchestrators/planning/ --durations=10
```

---

## 🐛 Debugging Failed Tests

### Show Full Traceback
```bash
python3 -m pytest tests/orchestrators/planning/test_interactive_planning_session.py --tb=long
```

### Enter Debugger on Failure
```bash
python3 -m pytest tests/orchestrators/planning/ --pdb
```

### Show Local Variables
```bash
python3 -m pytest tests/orchestrators/planning/ -v --showlocals
```

---

## ✅ Test Quality Checklist

When writing new tests for Planning Orchestrator:

- [ ] **Isolation**: Tests don't depend on external state
- [ ] **Temp Directories**: Use `tmp_path` fixture for file operations
- [ ] **Mocking**: Mock external dependencies (toolkit, git, brain)
- [ ] **Assertions**: Clear, specific assertions with good error messages
- [ ] **Documentation**: Docstrings explain what's being tested
- [ ] **Edge Cases**: Test error conditions, not just happy path
- [ ] **TDD**: Write test first (RED), implement (GREEN), refactor
- [ ] **Coverage**: Aim for >80% coverage on new code

---

## 🎯 Test Categories Summary

| Category | File(s) | Test Count | Status |
|----------|---------|------------|--------|
| Interactive Planning | `test_interactive_planning_session.py` | 18 | ✅ 100% passing |
| Toolkit Integration | `test_toolkit_integration.py` | 9 | ✅ 100% passing |
| TDD Workflow | `test_planning_orchestrator_tdd_manifest.py` | 18 | ✅ Passing |
| Complexity Routing | `test_planning_orchestrator_extended.py` | 12 | ✅ Passing |
| Intelligence Layer | `intelligence/test_*.py` | 40+ | ✅ Passing |
| Phase Manager | `test_phase_manager_integration.py` | 15+ | ✅ Passing |
| Git Checkpoints | `test_git_checkpoint_integration.py` | 12+ | ✅ Passing |
| DoR/DoD Validation | `test_planning_orchestrator_dor_dod.py` | 10+ | ✅ Passing |
| Learning Library | `test_learning_library_enforcement.py` | 8+ | ✅ Passing |
| **TOTAL** | **Multiple files** | **441+** | **✅ Passing** |

---

## 🚀 Next Steps

### To Add New Tests

1. **Choose appropriate test file** (or create new one)
2. **Follow TDD**: Write RED test first
3. **Use fixtures**: Leverage existing fixtures
4. **Run test**: Verify it fails (RED)
5. **Implement feature**: Make test pass (GREEN)
6. **Refactor**: Clean up code
7. **Verify**: Run full test suite

### To Test New Feature

```bash
# Example: Testing new interactive planning feature
cd /Users/asifhussain/PROJECTS/CORTEX

# 1. Create test file
touch tests/orchestrators/planning/test_my_new_feature.py

# 2. Write RED tests
# (edit file with TDD tests)

# 3. Run to confirm RED
python3 -m pytest tests/orchestrators/planning/test_my_new_feature.py -v

# 4. Implement feature
# (edit source files)

# 5. Run to confirm GREEN
python3 -m pytest tests/orchestrators/planning/test_my_new_feature.py -v

# 6. Run full suite
python3 -m pytest tests/orchestrators/planning/ -v
```

---

## 📚 Additional Resources

- **Test Examples**: See `tests/orchestrators/planning/` for comprehensive examples
- **Fixtures Guide**: Check `conftest.py` for available fixtures
- **TDD Methodology**: See `.github/prompts/tdd-orchestrator.prompt.md`
- **CORTEX Testing Standards**: See `cortex-brain/admin/testing-guidelines.yaml`

---

**Status:** ✅ Comprehensive test suite with 441+ tests covering all Planning Orchestrator features

**Last Test Run:** December 29, 2025 - All core tests passing
