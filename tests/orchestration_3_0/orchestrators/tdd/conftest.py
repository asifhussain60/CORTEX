"""
Shared fixtures and test utilities for TDD Orchestrator tests
Uses efficient testing strategies: factories, mocks, parameterization
"""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
from typing import Dict, Any, List
import tempfile
import os

# Test data constants
TEST_FEATURE_SCOPE = {
    "feature_name": "User Authentication",
    "acceptance_criteria": [
        "Users can log in with email/password",
        "Password must be hashed",
        "Failed login attempts logged"
    ],
    "test_file_path": "tests/test_auth.py",
    "implementation_file_path": "src/auth.py"
}

TEST_RED_PHASE_OUTPUT = {
    "tests_generated": True,
    "test_count": 5,
    "test_file": "tests/test_auth.py",
    "tests_fail": True,
    "failure_reasons": ["NotImplementedError", "Function not found"]
}

TEST_GREEN_PHASE_OUTPUT = {
    "implementation_complete": True,
    "tests_pass": True,
    "test_pass_rate": 1.0,
    "coverage": 0.85
}

TEST_REFACTOR_PHASE_OUTPUT = {
    "code_smells_before": 5,
    "code_smells_after": 0,
    "refactoring_applied": True,
    "tests_still_pass": True
}


@pytest.fixture
def mock_test_generator():
    """Mock test generator for RED phase."""
    generator = Mock()
    generator.generate_tests.return_value = {
        "success": True,
        "test_file": "tests/test_feature.py",
        "test_count": 5,
        "tests": [
            "def test_happy_path(): ...",
            "def test_edge_case(): ...",
            "def test_error_handling(): ..."
        ]
    }
    generator.analyze_edge_cases.return_value = ["null input", "empty string", "max value"]
    return generator


@pytest.fixture
def mock_implementation_engine():
    """Mock implementation engine for GREEN phase."""
    engine = Mock()
    engine.generate_minimal_implementation.return_value = {
        "success": True,
        "implementation": "def feature(): return True",
        "complexity": 5,
        "over_engineering_detected": False
    }
    engine.run_tests.return_value = {
        "success": True,
        "pass_rate": 1.0,
        "passed": 5,
        "failed": 0,
        "coverage": 0.85
    }
    return engine


@pytest.fixture
def mock_refactoring_engine():
    """Mock refactoring engine for REFACTOR phase."""
    engine = Mock()
    engine.detect_code_smells.return_value = {
        "smells": [],
        "smell_count": 0,
        "complexity": 5
    }
    engine.apply_refactoring.return_value = {
        "refactored": True,
        "changes_applied": ["extracted function", "removed duplicate"],
        "tests_pass": True
    }
    return engine


@pytest.fixture
def mock_phase_validator():
    """Mock phase validator for DoR/DoD validation."""
    from orchestration_3_0.orchestrators.tdd.phase_validator import ValidationResult
    
    validator = Mock()
    validator.validate_red_dor.return_value = ValidationResult(
        passed=True, errors=[], warnings=[], phase="RED", validation_type="DoR"
    )
    validator.validate_red_dod.return_value = ValidationResult(
        passed=True, errors=[], warnings=[], phase="RED", validation_type="DoD"
    )
    validator.validate_green_dor.return_value = ValidationResult(
        passed=True, errors=[], warnings=[], phase="GREEN", validation_type="DoR"
    )
    validator.validate_green_dod.return_value = ValidationResult(
        passed=True, errors=[], warnings=[], phase="GREEN", validation_type="DoD"
    )
    validator.validate_refactor_dor.return_value = ValidationResult(
        passed=True, errors=[], warnings=[], phase="REFACTOR", validation_type="DoR"
    )
    validator.validate_refactor_dod.return_value = ValidationResult(
        passed=True, errors=[], warnings=[], phase="REFACTOR", validation_type="DoD"
    )
    return validator


@pytest.fixture
def mock_metrics_collector():
    """Mock metrics collector."""
    collector = Mock()
    collector.collect_phase_metrics.return_value = {
        "phase": "RED",
        "duration_seconds": 10.5,
        "test_count": 5,
        "coverage": 0.0
    }
    collector.collect_session_metrics.return_value = {
        "total_duration": 45.0,
        "phases_completed": ["RED", "GREEN", "REFACTOR"],
        "final_coverage": 0.85
    }
    return collector


@pytest.fixture
def mock_git_orchestrator():
    """Mock Git orchestrator for checkpoints."""
    git = Mock()
    git.create_checkpoint.return_value = {
        "checkpoint_id": "checkpoint-123",
        "commit_hash": "abc123",
        "branch": "feature/auth"
    }
    git.rollback.return_value = {"success": True, "restored_commit": "abc123"}
    return git


@pytest.fixture
def tdd_orchestrator_factory(
    basic_fsm,
    fresh_session_manager,
    fresh_container,
    mock_test_generator,
    mock_implementation_engine,
    mock_refactoring_engine,
    mock_phase_validator,
    mock_metrics_collector,
    mock_git_orchestrator
):
    """Factory for creating TDD orchestrator instances with mocked dependencies."""
    def _create(config: Dict[str, Any] = None):
        # Import here to avoid circular dependency
        from orchestration_3_0.orchestrators.tdd.tdd_orchestrator import TDDOrchestrator
        from orchestration_3_0.orchestrators.tdd.test_generator import TestGenerator
        from orchestration_3_0.orchestrators.tdd.implementation_engine import ImplementationEngine
        from orchestration_3_0.orchestrators.tdd.refactoring_engine import RefactoringEngine
        from orchestration_3_0.orchestrators.tdd.phase_validator import PhaseValidator
        from orchestration_3_0.orchestrators.tdd.metrics_collector import MetricsCollector
        
        # Register mock services with proper types (container expects Type[T], not strings)
        # Use service_name parameter for string-based lookup
        fresh_container.services['test_generator'] = mock_test_generator
        fresh_container.services['implementation_engine'] = mock_implementation_engine
        fresh_container.services['refactoring_engine'] = mock_refactoring_engine
        fresh_container.services['phase_validator'] = mock_phase_validator
        fresh_container.services['metrics_collector'] = mock_metrics_collector
        fresh_container.services['git_orchestrator'] = mock_git_orchestrator
        
        # TDDOrchestrator signature: state_machine, session_manager, container (no config param)
        return TDDOrchestrator(basic_fsm, fresh_session_manager, fresh_container)
    
    return _create


@pytest.fixture
def sample_tdd_context():
    """Sample TDD workflow context."""
    from types import SimpleNamespace
    return SimpleNamespace(
        tenant_id="tenant-001",
        project_id="project-001",
        user_id="user-001",
        inputs=TEST_FEATURE_SCOPE
    )


# Parameterized test data for validation tests
VALIDATION_TEST_CASES = [
    # (phase, dor_status, expected_pass, expected_errors)
    ("RED", "valid", True, []),
    ("RED", "no_feature_name", False, ["Feature name required"]),
    ("RED", "existing_tests", False, ["Tests already exist"]),
    ("GREEN", "valid", True, []),
    ("GREEN", "tests_not_failing", False, ["Tests must be failing"]),
    ("GREEN", "no_red_phase", False, ["RED phase not complete"]),
    ("REFACTOR", "valid", True, []),
    ("REFACTOR", "tests_not_passing", False, ["Tests must be passing"]),
    ("REFACTOR", "no_green_phase", False, ["GREEN phase not complete"]),
]

# Parameterized test data for phase execution
PHASE_EXECUTION_TEST_CASES = [
    # (phase, should_succeed, expected_output_keys)
    ("RED", True, ["tests_generated", "test_count", "tests_fail"]),
    ("GREEN", True, ["implementation_complete", "tests_pass", "coverage"]),
    ("REFACTOR", True, ["code_smells_after", "refactoring_applied", "tests_still_pass"]),
]

# Parameterized test data for multi-tenant isolation
TENANT_ISOLATION_TEST_CASES = [
    ("tenant-1", "project-1", "user-1"),
    ("tenant-2", "project-2", "user-2"),
    ("tenant-3", "project-3", "user-3"),
]

# Parameterized test data for error scenarios
ERROR_SCENARIO_TEST_CASES = [
    ("test_generation_failure", "RED", "Test generator crashed"),
    ("implementation_timeout", "GREEN", "Implementation timeout"),
    ("refactoring_breaks_tests", "REFACTOR", "Tests failed after refactoring"),
    ("git_checkpoint_failure", "RED", "Git checkpoint failed"),
]
