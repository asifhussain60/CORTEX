"""
Tests for TDD Orchestrator Integration with Planning System 3.0

Phase 5: TDD Orchestrator Integration

Tests cover:
- TDD session creation and planning integration
- RED phase validation
- Empty test detection
- Coverage tracking per phase
- Planning orchestrator TDD integration

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from src.operations.modules.orchestration.tdd_orchestrator import (
    TDDOrchestrator, TDDPhase, ValidationResult
)
from src.operations.modules.orchestration.planning.coverage_tracker import (
    CoverageTracker, PhaseCoverageData
)
from src.operations.modules.orchestration.planning_orchestrator import (
    PlanningOrchestrator
)


# ===== Fixtures =====

@pytest.fixture
def temp_project_dir():
    """Create temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def tdd_orchestrator(temp_project_dir):
    """Create TDD orchestrator instance."""
    return TDDOrchestrator(project_root=temp_project_dir)


@pytest.fixture
def planning_orchestrator(temp_project_dir):
    """Create planning orchestrator instance."""
    return PlanningOrchestrator(project_root=temp_project_dir)


@pytest.fixture
def coverage_tracker(temp_project_dir):
    """Create coverage tracker instance."""
    return CoverageTracker(
        session_id="test_session_001",
        coverage_dir=temp_project_dir / ".cortex" / "coverage"
    )


@pytest.fixture
def sample_test_file(temp_project_dir):
    """Create sample test file with failing tests."""
    test_file = temp_project_dir / "test_sample.py"
    test_file.write_text("""
import pytest

def test_addition_fails():
    '''Test that should fail in RED phase.'''
    assert 2 + 2 == 5  # Intentionally wrong

def test_subtraction_fails():
    '''Another failing test.'''
    assert 10 - 3 == 8  # Intentionally wrong
""")
    return test_file


@pytest.fixture
def sample_empty_test_file(temp_project_dir):
    """Create sample test file with empty tests."""
    test_file = temp_project_dir / "test_empty.py"
    test_file.write_text("""
import pytest

def test_empty_with_pass():
    '''Empty test with only pass.'''
    pass

def test_empty_with_docstring():
    '''Only has docstring, no assertions.'''

def test_no_assertions():
    '''Has code but no assertions.'''
    x = 5
    y = 10
    z = x + y
""")
    return test_file


# ===== TDD Orchestrator Tests =====

class TestTDDOrchestratorIntegration:
    """Test TDD orchestrator planning integration."""
    
    def test_integrate_with_planning_creates_session(self, tdd_orchestrator):
        """Test TDD session creation for planning integration."""
        planning_session_id = "plan_abc123"
        
        result = tdd_orchestrator.integrate_with_planning(planning_session_id)
        
        assert 'tdd_session_id' in result
        assert result['tdd_session_id'].startswith('tdd_')
        assert 'enforcement_rules' in result
        assert 'checkpoints' in result
        
        # Verify enforcement rules
        rules = result['enforcement_rules']
        assert rules['red_phase_mandatory'] is True
        assert rules['empty_test_detection'] is True
        assert rules['coverage_threshold'] == 80.0
        assert rules['phase_based_validation'] is True
        
        # Verify checkpoints
        checkpoints = result['checkpoints']
        assert checkpoints['frequency'] == 'per_phase'
        assert checkpoints['auto_validate'] is True
        assert checkpoints['rollback_on_failure'] is True
    
    def test_validate_red_phase_with_failing_tests(self, tdd_orchestrator, sample_test_file):
        """Test RED phase validation with correctly failing tests."""
        result = tdd_orchestrator.validate_red_phase_compliance(sample_test_file)
        
        assert isinstance(result, ValidationResult)
        assert result.compliant is True  # Tests fail as expected
        assert len(result.violations) == 0
        assert 'RED phase valid' in result.recommendation
    
    def test_validate_red_phase_with_passing_tests(self, tdd_orchestrator, temp_project_dir):
        """Test RED phase validation catches passing tests (violation)."""
        test_file = temp_project_dir / "test_passing.py"
        test_file.write_text("""
def test_passing():
    assert 2 + 2 == 4  # Passes without implementation
""")
        
        result = tdd_orchestrator.validate_red_phase_compliance(test_file)
        
        assert isinstance(result, ValidationResult)
        assert result.compliant is False  # RED phase violation
        assert len(result.violations) > 0
        assert 'RED phase violation' in result.violations[0]
    
    def test_validate_red_phase_with_missing_file(self, tdd_orchestrator, temp_project_dir):
        """Test RED phase validation with non-existent file."""
        missing_file = temp_project_dir / "nonexistent_test.py"
        
        result = tdd_orchestrator.validate_red_phase_compliance(missing_file)
        
        assert isinstance(result, ValidationResult)
        assert result.compliant is False
        assert 'not found' in result.violations[0].lower()
    
    def test_detect_empty_tests_with_pass(self, tdd_orchestrator, sample_empty_test_file):
        """Test detection of empty tests with pass statements."""
        empty_tests = tdd_orchestrator.detect_empty_tests(sample_empty_test_file)
        
        assert len(empty_tests) >= 2  # At least pass and docstring-only tests
        
        # Check for pass statement detection
        pass_test = next(t for t in empty_tests if 'pass' in t['name'])
        assert ('pass statement' in pass_test['reason'].lower() or 'assertion' in pass_test['reason'].lower())
        assert pass_test['line'] > 0
    
    def test_detect_empty_tests_with_docstring_only(self, tdd_orchestrator, sample_empty_test_file):
        """Test detection of tests with only docstrings."""
        empty_tests = tdd_orchestrator.detect_empty_tests(sample_empty_test_file)
        
        # Check for docstring-only detection
        docstring_tests = [t for t in empty_tests if 'docstring' in t['reason'].lower()]
        assert len(docstring_tests) >= 1
    
    def test_detect_empty_tests_with_no_assertions(self, tdd_orchestrator, sample_empty_test_file):
        """Test detection of tests without assertions."""
        empty_tests = tdd_orchestrator.detect_empty_tests(sample_empty_test_file)
        
        # Check for no-assertion detection
        no_assert_tests = [t for t in empty_tests if 'assertion' in t['reason'].lower()]
        assert len(no_assert_tests) >= 1
    
    def test_detect_empty_tests_with_missing_file(self, tdd_orchestrator, temp_project_dir):
        """Test empty test detection with non-existent file."""
        missing_file = temp_project_dir / "nonexistent.py"
        
        empty_tests = tdd_orchestrator.detect_empty_tests(missing_file)
        
        assert empty_tests == []  # Returns empty list for missing files


# ===== Coverage Tracker Tests =====

class TestCoverageTracker:
    """Test phase-based coverage tracking."""
    
    def test_coverage_tracker_initialization(self, coverage_tracker):
        """Test coverage tracker initializes correctly."""
        assert coverage_tracker.session_id == "test_session_001"
        assert isinstance(coverage_tracker.coverage_data, dict)
        assert len(coverage_tracker.coverage_data) == 0
    
    def test_record_phase_coverage(self, coverage_tracker):
        """Test recording coverage for a phase."""
        coverage_report = {
            'timestamp': '2025-12-15T10:00:00',
            'totals': {
                'percent_covered': 85.5,
                'covered_lines': 342,
                'num_statements': 400
            },
            'files': {
                'src/module.py': {'coverage': 90.0}
            }
        }
        
        coverage_tracker.record_phase_coverage('Phase 1', coverage_report)
        
        assert 'Phase 1' in coverage_tracker.coverage_data
        phase_data = coverage_tracker.coverage_data['Phase 1']
        assert isinstance(phase_data, PhaseCoverageData)
        assert phase_data.total_coverage == 85.5
        assert phase_data.lines_covered == 342
        assert phase_data.lines_total == 400
    
    def test_get_coverage_trend(self, coverage_tracker):
        """Test retrieving coverage trend across phases."""
        # Record multiple phases
        for i, coverage in enumerate([70.0, 80.0, 85.0]):
            coverage_report = {
                'timestamp': f'2025-12-15T10:{i:02d}:00',
                'totals': {
                    'percent_covered': coverage,
                    'covered_lines': int(coverage * 4),
                    'num_statements': 400
                },
                'files': {}
            }
            coverage_tracker.record_phase_coverage(f'Phase {i+1}', coverage_report)
        
        trend = coverage_tracker.get_coverage_trend()
        
        assert len(trend) == 3
        assert trend[0]['coverage'] == 70.0
        assert trend[1]['coverage'] == 80.0
        assert trend[2]['coverage'] == 85.0
        assert all('timestamp' in item for item in trend)
    
    def test_validate_coverage_threshold_passes(self, coverage_tracker):
        """Test coverage threshold validation (passing)."""
        coverage_report = {
            'timestamp': '2025-12-15T10:00:00',
            'totals': {
                'percent_covered': 85.0,
                'covered_lines': 340,
                'num_statements': 400
            },
            'files': {}
        }
        
        coverage_tracker.record_phase_coverage('Phase 1', coverage_report)
        
        assert coverage_tracker.validate_coverage_threshold(threshold=80.0) is True
        assert coverage_tracker.validate_coverage_threshold(threshold=85.0) is True
    
    def test_validate_coverage_threshold_fails(self, coverage_tracker):
        """Test coverage threshold validation (failing)."""
        coverage_report = {
            'timestamp': '2025-12-15T10:00:00',
            'totals': {
                'percent_covered': 75.0,
                'covered_lines': 300,
                'num_statements': 400
            },
            'files': {}
        }
        
        coverage_tracker.record_phase_coverage('Phase 1', coverage_report)
        
        assert coverage_tracker.validate_coverage_threshold(threshold=80.0) is False
    
    def test_get_phase_coverage(self, coverage_tracker):
        """Test retrieving coverage for specific phase."""
        coverage_report = {
            'timestamp': '2025-12-15T10:00:00',
            'totals': {
                'percent_covered': 85.0,
                'covered_lines': 340,
                'num_statements': 400
            },
            'files': {}
        }
        
        coverage_tracker.record_phase_coverage('Phase 1', coverage_report)
        
        phase_cov = coverage_tracker.get_phase_coverage('Phase 1')
        assert phase_cov is not None
        assert phase_cov.total_coverage == 85.0
        
        missing_cov = coverage_tracker.get_phase_coverage('Phase 999')
        assert missing_cov is None
    
    def test_get_coverage_delta(self, coverage_tracker):
        """Test calculating coverage delta between phases."""
        # Record two phases
        coverage_tracker.record_phase_coverage('Phase 1', {
            'timestamp': '2025-12-15T10:00:00',
            'totals': {'percent_covered': 70.0, 'covered_lines': 280, 'num_statements': 400},
            'files': {}
        })
        
        coverage_tracker.record_phase_coverage('Phase 2', {
            'timestamp': '2025-12-15T11:00:00',
            'totals': {'percent_covered': 85.0, 'covered_lines': 340, 'num_statements': 400},
            'files': {}
        })
        
        delta = coverage_tracker.get_coverage_delta('Phase 1', 'Phase 2')
        
        assert delta is not None
        assert delta['coverage_change'] == 15.0
        assert delta['lines_added'] == 60
    
    def test_get_summary(self, coverage_tracker):
        """Test getting coverage summary."""
        # Record multiple phases
        for i in range(3):
            coverage_tracker.record_phase_coverage(f'Phase {i+1}', {
                'timestamp': f'2025-12-15T1{i}:00:00',
                'totals': {
                    'percent_covered': 70.0 + (i * 5),
                    'covered_lines': 280 + (i * 20),
                    'num_statements': 400
                },
                'files': {}
            })
        
        summary = coverage_tracker.get_summary()
        
        assert summary['session_id'] == "test_session_001"
        assert summary['phases'] == 3
        assert summary['current_coverage'] == 80.0
        assert summary['initial_coverage'] == 70.0
        assert summary['coverage_change'] == 10.0


# ===== Planning Orchestrator TDD Integration Tests =====

class TestPlanningOrchestratorTDDIntegration:
    """Test planning orchestrator TDD integration methods."""
    
    def test_execute_phase_with_tdd_no_test_files(self, planning_orchestrator):
        """Test phase execution without test files."""
        phase = {
            'name': 'Implementation',
            'test_requirements': ['Test feature X']
        }
        
        result = planning_orchestrator.execute_phase_with_tdd(
            phase=phase,
            session_id='session_001'
        )
        
        assert result['status'] == 'success'
        assert result['phase'] == 'Implementation'
        assert result['tdd_cycle_complete'] is True
    
    def test_execute_phase_with_tdd_valid_red_phase(
        self,
        planning_orchestrator,
        sample_test_file
    ):
        """Test phase execution with valid RED phase."""
        phase = {
            'name': 'Implementation',
            'test_requirements': ['Test addition', 'Test subtraction']
        }
        
        result = planning_orchestrator.execute_phase_with_tdd(
            phase=phase,
            session_id='session_001',
            test_files=[sample_test_file],
            source_files=[Path('src/calculator.py')]
        )
        
        assert result['status'] == 'success'
        assert result['red_phase']['validated'] is True
        assert len(result['red_phase']['violations']) == 0
    
    def test_execute_phase_with_tdd_red_violation(
        self,
        planning_orchestrator,
        temp_project_dir
    ):
        """Test phase execution catches RED phase violations."""
        # Create passing test (RED violation)
        test_file = temp_project_dir / "test_violation.py"
        test_file.write_text("""
def test_passes_before_implementation():
    assert True  # Passes without implementation - RED violation
""")
        
        phase = {
            'name': 'Implementation',
            'test_requirements': ['Test feature']
        }
        
        result = planning_orchestrator.execute_phase_with_tdd(
            phase=phase,
            session_id='session_001',
            test_files=[test_file]
        )
        
        assert result['status'] == 'failed'
        assert 'RED phase' in result['reason']
        assert len(result['violations']) > 0
    
    def test_execute_phase_with_tdd_empty_tests(
        self,
        planning_orchestrator,
        sample_empty_test_file
    ):
        """Test phase execution detects empty tests."""
        phase = {
            'name': 'Implementation',
            'test_requirements': ['Test feature']
        }
        
        result = planning_orchestrator.execute_phase_with_tdd(
            phase=phase,
            session_id='session_001',
            test_files=[sample_empty_test_file]
        )
        
        # Should detect empty tests but return warning, not failure
        assert result['status'] in ['warning', 'failed']
        if result['status'] == 'warning':
            assert 'empty' in result['reason'].lower()
    
    def test_validate_phase_completion_with_valid_tests(
        self,
        planning_orchestrator,
        sample_test_file
    ):
        """Test phase completion validation with valid tests."""
        result = planning_orchestrator.validate_phase_completion(
            phase_name='Phase 1',
            session_id='session_001',
            test_files=[sample_test_file]
        )
        
        assert result['valid'] is True
        assert result['test_quality'] == 'validated'
    
    def test_validate_phase_completion_with_empty_tests(
        self,
        planning_orchestrator,
        sample_empty_test_file
    ):
        """Test phase completion validation catches empty tests."""
        result = planning_orchestrator.validate_phase_completion(
            phase_name='Phase 1',
            session_id='session_001',
            test_files=[sample_empty_test_file]
        )
        
        assert result['valid'] is False
        assert result['reason'] == 'empty_tests_detected'
        assert len(result['empty_tests']) > 0
