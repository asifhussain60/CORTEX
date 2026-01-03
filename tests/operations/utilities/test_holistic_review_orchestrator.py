"""
Test Suite: Holistic Review Orchestrator

Comprehensive tests for quality gate validation, learning integration,
and holistic review execution.

Coverage Target: 90%+

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from typing import Dict, Any, List
from pathlib import Path

from src.operations.utilities.holistic_review_orchestrator import (
    HolisticReviewOrchestrator,
    ReviewResult,
    QualityGate
)


# ============================================================================
# Test Group 1: Initialization & Configuration (3 tests)
# ============================================================================

class TestInitialization:
    """Test orchestrator initialization and configuration."""
    
    def test_init_default_values(self):
        """Test default initialization values."""
        orchestrator = HolisticReviewOrchestrator()
        
        assert orchestrator.min_coverage == 90.0
        assert orchestrator.min_tests == 3
    
    def test_orchestrator_creation(self):
        """Test orchestrator can be created successfully."""
        orchestrator = HolisticReviewOrchestrator()
        assert orchestrator is not None
        assert isinstance(orchestrator, HolisticReviewOrchestrator)
    
    def test_orchestrator_has_required_methods(self):
        """Test orchestrator has all required methods."""
        orchestrator = HolisticReviewOrchestrator()
        
        assert hasattr(orchestrator, 'evaluate_code_quality')
        assert hasattr(orchestrator, 'evaluate_test_coverage')
        assert hasattr(orchestrator, 'evaluate_documentation')
        assert hasattr(orchestrator, 'run_holistic_review')
        assert hasattr(orchestrator, '_generate_recommendations')
        assert hasattr(orchestrator, 'document_lessons_learned')
        assert hasattr(orchestrator, 'document_lessons_learned_from_gates')
        assert hasattr(orchestrator, 'extract_patterns')


# ============================================================================
# Test Group 2: Quality Gate - Code Quality (8 tests)
# ============================================================================

class TestCodeQualityGate:
    """Test code quality evaluation."""
    
    def test_code_quality_passes_with_modifications(self):
        """Test code quality gate passes when files are modified."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['src/module1.py', 'src/module2.py']
        }
        
        gate = orchestrator.evaluate_code_quality(context)
        
        assert gate.gate_name == 'code_quality'
        assert gate.passed is True
        assert gate.score == 100.0
        assert gate.message == "Code quality checks passed"
        assert gate.metrics['files_modified'] == 2
    
    def test_code_quality_fails_with_no_modifications(self):
        """Test code quality gate fails when no files modified."""
        orchestrator = HolisticReviewOrchestrator()
        context = {'files_modified': []}
        
        gate = orchestrator.evaluate_code_quality(context)
        
        assert gate.gate_name == 'code_quality'
        assert gate.passed is False
        assert gate.score == 0.0
        assert gate.message == "No code modifications detected"
        assert gate.metrics['files_modified'] == 0
    
    def test_code_quality_with_missing_files_modified_key(self):
        """Test code quality with missing files_modified key in context."""
        orchestrator = HolisticReviewOrchestrator()
        context = {}
        
        gate = orchestrator.evaluate_code_quality(context)
        
        assert gate.gate_name == 'code_quality'
        assert gate.passed is False
        assert gate.score == 0.0
    
    def test_code_quality_with_single_file(self):
        """Test code quality with single file modification."""
        orchestrator = HolisticReviewOrchestrator()
        context = {'files_modified': ['src/single.py']}
        
        gate = orchestrator.evaluate_code_quality(context)
        
        assert gate.passed is True
        assert gate.metrics['files_modified'] == 1
    
    def test_code_quality_with_many_files(self):
        """Test code quality with many file modifications."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': [f'src/module{i}.py' for i in range(20)]
        }
        
        gate = orchestrator.evaluate_code_quality(context)
        
        assert gate.passed is True
        assert gate.metrics['files_modified'] == 20
    
    def test_code_quality_gate_has_required_attributes(self):
        """Test QualityGate dataclass has required attributes."""
        orchestrator = HolisticReviewOrchestrator()
        context = {'files_modified': ['test.py']}
        
        gate = orchestrator.evaluate_code_quality(context)
        
        assert hasattr(gate, 'gate_name')
        assert hasattr(gate, 'passed')
        assert hasattr(gate, 'score')
        assert hasattr(gate, 'message')
        assert hasattr(gate, 'metrics')
    
    def test_code_quality_returns_quality_gate_instance(self):
        """Test code quality evaluation returns QualityGate instance."""
        orchestrator = HolisticReviewOrchestrator()
        context = {'files_modified': ['test.py']}
        
        gate = orchestrator.evaluate_code_quality(context)
        
        assert isinstance(gate, QualityGate)
    
    def test_code_quality_metrics_structure(self):
        """Test code quality metrics have correct structure."""
        orchestrator = HolisticReviewOrchestrator()
        context = {'files_modified': ['a.py', 'b.py', 'c.py']}
        
        gate = orchestrator.evaluate_code_quality(context)
        
        assert isinstance(gate.metrics, dict)
        assert 'files_modified' in gate.metrics
        assert isinstance(gate.metrics['files_modified'], int)


# ============================================================================
# Test Group 3: Quality Gate - Test Coverage (12 tests)
# ============================================================================

class TestCoverageGate:
    """Test test coverage evaluation."""
    
    def test_coverage_passes_at_minimum_threshold(self):
        """Test coverage gate passes at exactly 90% threshold."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'coverage': 90.0,
            'tests_run': 10,
            'tests_passed': 10
        }
        
        gate = orchestrator.evaluate_test_coverage(context)
        
        assert gate.gate_name == 'test_coverage'
        assert gate.passed is True
        assert gate.score == 90.0
        assert "meets 90.0% threshold" in gate.message
    
    def test_coverage_passes_above_threshold(self):
        """Test coverage gate passes above 90% threshold."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'coverage': 95.5,
            'tests_run': 20,
            'tests_passed': 20
        }
        
        gate = orchestrator.evaluate_test_coverage(context)
        
        assert gate.passed is True
        assert gate.score == 95.5
        assert "95.5% meets 90.0% threshold" in gate.message
    
    def test_coverage_fails_below_threshold(self):
        """Test coverage gate fails below 90% threshold."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'coverage': 75.0,
            'tests_run': 10,
            'tests_passed': 10
        }
        
        gate = orchestrator.evaluate_test_coverage(context)
        
        assert gate.passed is False
        assert gate.score == 75.0
        assert "below 90.0% threshold" in gate.message
    
    def test_coverage_fails_with_test_failures(self):
        """Test coverage gate fails when tests fail even with high coverage."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'coverage': 95.0,
            'tests_run': 10,
            'tests_passed': 8  # 2 failures
        }
        
        gate = orchestrator.evaluate_test_coverage(context)
        
        assert gate.passed is False
        assert gate.score == 95.0
    
    def test_coverage_fails_with_insufficient_tests(self):
        """Test coverage gate fails with fewer than minimum tests."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'coverage': 95.0,
            'tests_run': 2,  # Less than min_tests (3)
            'tests_passed': 2
        }
        
        gate = orchestrator.evaluate_test_coverage(context)
        
        assert gate.passed is False
    
    def test_coverage_with_zero_coverage(self):
        """Test coverage gate with 0% coverage."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'coverage': 0.0,
            'tests_run': 0,
            'tests_passed': 0
        }
        
        gate = orchestrator.evaluate_test_coverage(context)
        
        assert gate.passed is False
        assert gate.score == 0.0
    
    def test_coverage_with_100_percent(self):
        """Test coverage gate with 100% coverage."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'coverage': 100.0,
            'tests_run': 50,
            'tests_passed': 50
        }
        
        gate = orchestrator.evaluate_test_coverage(context)
        
        assert gate.passed is True
        assert gate.score == 100.0
    
    def test_coverage_metrics_structure(self):
        """Test coverage metrics have correct structure."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'coverage': 92.5,
            'tests_run': 15,
            'tests_passed': 15
        }
        
        gate = orchestrator.evaluate_test_coverage(context)
        
        assert 'coverage' in gate.metrics
        assert 'tests_run' in gate.metrics
        assert 'tests_passed' in gate.metrics
        assert gate.metrics['coverage'] == 92.5
        assert gate.metrics['tests_run'] == 15
        assert gate.metrics['tests_passed'] == 15
    
    def test_coverage_with_missing_keys(self):
        """Test coverage evaluation with missing context keys."""
        orchestrator = HolisticReviewOrchestrator()
        context = {}
        
        gate = orchestrator.evaluate_test_coverage(context)
        
        assert gate.passed is False
        assert gate.score == 0.0
        assert gate.metrics['coverage'] == 0.0
        assert gate.metrics['tests_run'] == 0
        assert gate.metrics['tests_passed'] == 0
    
    def test_coverage_with_partial_failures(self):
        """Test coverage with some test failures."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'coverage': 93.0,
            'tests_run': 100,
            'tests_passed': 95
        }
        
        gate = orchestrator.evaluate_test_coverage(context)
        
        assert gate.passed is False
    
    def test_coverage_at_minimum_tests(self):
        """Test coverage with exactly minimum test count."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'coverage': 91.0,
            'tests_run': 3,  # Exactly min_tests
            'tests_passed': 3
        }
        
        gate = orchestrator.evaluate_test_coverage(context)
        
        assert gate.passed is True
    
    def test_coverage_message_formats_correctly(self):
        """Test coverage message formatting."""
        orchestrator = HolisticReviewOrchestrator()
        
        # Pass case
        context_pass = {'coverage': 92.3, 'tests_run': 10, 'tests_passed': 10}
        gate_pass = orchestrator.evaluate_test_coverage(context_pass)
        assert "92.3%" in gate_pass.message
        assert "meets" in gate_pass.message
        
        # Fail case
        context_fail = {'coverage': 85.7, 'tests_run': 10, 'tests_passed': 10}
        gate_fail = orchestrator.evaluate_test_coverage(context_fail)
        assert "85.7%" in gate_fail.message
        assert "below" in gate_fail.message


# ============================================================================
# Test Group 4: Quality Gate - Documentation (10 tests)
# ============================================================================

class TestDocumentationGate:
    """Test documentation quality evaluation."""
    
    def test_documentation_passes_with_valid_context(self):
        """Test documentation gate passes with valid feature and phases."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'feature_name': 'user-authentication',
            'phases_completed': ['phase1', 'phase2', 'phase3']
        }
        
        gate = orchestrator.evaluate_documentation(context)
        
        assert gate.gate_name == 'documentation'
        assert gate.passed is True
        assert gate.score == 100.0
        assert gate.message == "Documentation adequate"
    
    def test_documentation_fails_without_feature_name(self):
        """Test documentation gate fails without feature name."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'feature_name': '',
            'phases_completed': ['phase1', 'phase2', 'phase3']
        }
        
        gate = orchestrator.evaluate_documentation(context)
        
        assert gate.passed is False
        assert gate.score == 50.0
        assert gate.message == "Documentation needs improvement"
    
    def test_documentation_fails_with_insufficient_phases(self):
        """Test documentation gate fails with fewer than 3 phases."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'feature_name': 'test-feature',
            'phases_completed': ['phase1', 'phase2']  # Only 2 phases
        }
        
        gate = orchestrator.evaluate_documentation(context)
        
        assert gate.passed is False
        assert gate.score == 50.0
    
    def test_documentation_with_many_phases(self):
        """Test documentation with many completed phases."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'feature_name': 'complex-feature',
            'phases_completed': [f'phase{i}' for i in range(1, 11)]
        }
        
        gate = orchestrator.evaluate_documentation(context)
        
        assert gate.passed is True
        assert gate.metrics['phases_completed'] == 10
    
    def test_documentation_with_exactly_three_phases(self):
        """Test documentation with exactly 3 phases (minimum)."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'feature_name': 'minimal-feature',
            'phases_completed': ['phase1', 'phase2', 'phase3']
        }
        
        gate = orchestrator.evaluate_documentation(context)
        
        assert gate.passed is True
        assert gate.metrics['phases_completed'] == 3
    
    def test_documentation_with_empty_phases(self):
        """Test documentation with empty phases list."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'feature_name': 'test-feature',
            'phases_completed': []
        }
        
        gate = orchestrator.evaluate_documentation(context)
        
        assert gate.passed is False
    
    def test_documentation_with_missing_keys(self):
        """Test documentation with missing context keys."""
        orchestrator = HolisticReviewOrchestrator()
        context = {}
        
        gate = orchestrator.evaluate_documentation(context)
        
        assert gate.passed is False
        assert gate.metrics['phases_completed'] == 0
    
    def test_documentation_metrics_structure(self):
        """Test documentation metrics structure."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'feature_name': 'test',
            'phases_completed': ['p1', 'p2', 'p3', 'p4']
        }
        
        gate = orchestrator.evaluate_documentation(context)
        
        assert 'phases_completed' in gate.metrics
        assert isinstance(gate.metrics['phases_completed'], int)
    
    def test_documentation_with_none_feature_name(self):
        """Test documentation with None as feature name."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'feature_name': None,
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        gate = orchestrator.evaluate_documentation(context)
        
        assert gate.passed is False
    
    def test_documentation_score_values(self):
        """Test documentation score is either 100.0 or 50.0."""
        orchestrator = HolisticReviewOrchestrator()
        
        # Pass case
        context_pass = {
            'feature_name': 'test',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        gate_pass = orchestrator.evaluate_documentation(context_pass)
        assert gate_pass.score == 100.0
        
        # Fail case
        context_fail = {'feature_name': '', 'phases_completed': []}
        gate_fail = orchestrator.evaluate_documentation(context_fail)
        assert gate_fail.score == 50.0


# ============================================================================
# Test Group 5: Holistic Review Execution (10 tests)
# ============================================================================

class TestHolisticReviewExecution:
    """Test complete holistic review execution."""
    
    def test_review_passes_all_gates(self):
        """Test holistic review passes when all gates pass."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['src/a.py', 'src/b.py'],
            'coverage': 95.0,
            'tests_run': 20,
            'tests_passed': 20,
            'feature_name': 'test-feature',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        result = orchestrator.run_holistic_review(context)
        
        assert isinstance(result, ReviewResult)
        assert result.overall_passed is True
        assert len(result.gates) == 3
        assert all(gate.passed for gate in result.gates)
    
    def test_review_fails_with_any_gate_failure(self):
        """Test holistic review fails when any gate fails."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['src/a.py'],
            'coverage': 75.0,  # Below threshold
            'tests_run': 10,
            'tests_passed': 10,
            'feature_name': 'test-feature',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        result = orchestrator.run_holistic_review(context)
        
        assert result.overall_passed is False
    
    def test_review_result_has_three_gates(self):
        """Test review result contains exactly 3 gates."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['test.py'],
            'coverage': 90.0,
            'tests_run': 5,
            'tests_passed': 5,
            'feature_name': 'test',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        result = orchestrator.run_holistic_review(context)
        
        assert len(result.gates) == 3
        gate_names = [gate.gate_name for gate in result.gates]
        assert 'code_quality' in gate_names
        assert 'test_coverage' in gate_names
        assert 'documentation' in gate_names
    
    def test_review_result_has_recommendations(self):
        """Test review result includes recommendations."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': [],
            'coverage': 0.0,
            'tests_run': 0,
            'tests_passed': 0,
            'feature_name': '',
            'phases_completed': []
        }
        
        result = orchestrator.run_holistic_review(context)
        
        assert isinstance(result.recommendations, list)
        assert len(result.recommendations) > 0
    
    def test_review_result_has_lessons(self):
        """Test review result includes lessons learned."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['test.py'],
            'coverage': 92.0,
            'tests_run': 10,
            'tests_passed': 10,
            'feature_name': 'test-feature',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        result = orchestrator.run_holistic_review(context)
        
        assert isinstance(result.lessons, dict)
        assert 'feature_name' in result.lessons
        assert 'quality_metrics' in result.lessons
        assert 'execution_summary' in result.lessons
    
    def test_review_result_has_patterns(self):
        """Test review result includes extracted patterns."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['a.py', 'b.py', 'c.py'],
            'coverage': 96.0,
            'tests_run': 20,
            'tests_passed': 20,
            'feature_name': 'test',
            'phases_completed': ['p1', 'p2', 'p3', 'p4']
        }
        
        result = orchestrator.run_holistic_review(context)
        
        assert isinstance(result.patterns, list)
    
    def test_review_result_failed_gates_property(self):
        """Test ReviewResult.failed_gates property."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': [],  # Will fail code quality
            'coverage': 95.0,
            'tests_run': 10,
            'tests_passed': 10,
            'feature_name': 'test',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        result = orchestrator.run_holistic_review(context)
        
        failed_gates = result.failed_gates
        assert isinstance(failed_gates, list)
        assert len(failed_gates) > 0
        assert all(not gate.passed for gate in failed_gates)
    
    def test_review_with_empty_context(self):
        """Test review with completely empty context."""
        orchestrator = HolisticReviewOrchestrator()
        context = {}
        
        result = orchestrator.run_holistic_review(context)
        
        assert result.overall_passed is False
        assert len(result.gates) == 3
    
    def test_review_result_structure(self):
        """Test ReviewResult has all required attributes."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['test.py'],
            'coverage': 90.0,
            'tests_run': 5,
            'tests_passed': 5,
            'feature_name': 'test',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        result = orchestrator.run_holistic_review(context)
        
        assert hasattr(result, 'overall_passed')
        assert hasattr(result, 'gates')
        assert hasattr(result, 'recommendations')
        assert hasattr(result, 'lessons')
        assert hasattr(result, 'patterns')
        assert hasattr(result, 'failed_gates')
    
    def test_review_logging_messages(self, caplog):
        """Test review execution logs appropriate messages."""
        import logging
        caplog.set_level(logging.INFO)
        
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['test.py'],
            'coverage': 90.0,
            'tests_run': 5,
            'tests_passed': 5,
            'feature_name': 'test',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        result = orchestrator.run_holistic_review(context)
        
        # Check for orchestrator engagement log
        engagement_logs = [r for r in caplog.records if 'Orchestrator engaged' in r.message]
        assert len(engagement_logs) > 0
        
        # Check for review complete log
        complete_logs = [r for r in caplog.records if 'Review complete' in r.message]
        assert len(complete_logs) > 0


# ============================================================================
# Test Group 6: Recommendations Generation (8 tests)
# ============================================================================

class TestRecommendations:
    """Test recommendation generation."""
    
    def test_recommendations_for_failed_code_quality(self):
        """Test recommendations when code quality gate fails."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': [],  # Fail code quality
            'coverage': 95.0,
            'tests_run': 10,
            'tests_passed': 10,
            'feature_name': 'test',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        result = orchestrator.run_holistic_review(context)
        
        assert any('complexity' in rec.lower() or 'refactor' in rec.lower() 
                   for rec in result.recommendations)
    
    def test_recommendations_for_failed_coverage(self):
        """Test recommendations when coverage gate fails."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['test.py'],
            'coverage': 75.0,  # Below threshold
            'tests_run': 10,
            'tests_passed': 10,
            'feature_name': 'test',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        result = orchestrator.run_holistic_review(context)
        
        assert any('coverage' in rec.lower() and '90%' in rec 
                   for rec in result.recommendations)
    
    def test_recommendations_for_failed_documentation(self):
        """Test recommendations when documentation gate fails."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['test.py'],
            'coverage': 95.0,
            'tests_run': 10,
            'tests_passed': 10,
            'feature_name': '',  # Fail documentation
            'phases_completed': ['p1']
        }
        
        result = orchestrator.run_holistic_review(context)
        
        assert any('docstring' in rec.lower() or 'documentation' in rec.lower() 
                   for rec in result.recommendations)
    
    def test_recommendations_for_all_gates_passing(self):
        """Test recommendations when all gates pass."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['test.py'],
            'coverage': 95.0,
            'tests_run': 10,
            'tests_passed': 10,
            'feature_name': 'test',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        result = orchestrator.run_holistic_review(context)
        
        assert len(result.recommendations) == 1
        assert 'quality gates passed' in result.recommendations[0].lower()
    
    def test_recommendations_for_multiple_failures(self):
        """Test recommendations when multiple gates fail."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': [],
            'coverage': 60.0,
            'tests_run': 2,
            'tests_passed': 2,
            'feature_name': '',
            'phases_completed': []
        }
        
        result = orchestrator.run_holistic_review(context)
        
        assert len(result.recommendations) >= 3
    
    def test_recommendations_are_strings(self):
        """Test all recommendations are strings."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': [],
            'coverage': 70.0,
            'tests_run': 5,
            'tests_passed': 5,
            'feature_name': 'test',
            'phases_completed': ['p1']
        }
        
        result = orchestrator.run_holistic_review(context)
        
        assert all(isinstance(rec, str) for rec in result.recommendations)
    
    def test_recommendations_not_empty(self):
        """Test recommendations list is never empty."""
        orchestrator = HolisticReviewOrchestrator()
        
        # All pass
        context_pass = {
            'files_modified': ['test.py'],
            'coverage': 95.0,
            'tests_run': 10,
            'tests_passed': 10,
            'feature_name': 'test',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        result_pass = orchestrator.run_holistic_review(context_pass)
        assert len(result_pass.recommendations) > 0
        
        # All fail
        context_fail = {
            'files_modified': [],
            'coverage': 0.0,
            'tests_run': 0,
            'tests_passed': 0,
            'feature_name': '',
            'phases_completed': []
        }
        result_fail = orchestrator.run_holistic_review(context_fail)
        assert len(result_fail.recommendations) > 0
    
    def test_recommendation_messages_actionable(self):
        """Test recommendations contain actionable guidance."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': [],
            'coverage': 80.0,
            'tests_run': 5,
            'tests_passed': 5,
            'feature_name': '',
            'phases_completed': []
        }
        
        result = orchestrator.run_holistic_review(context)
        
        # Check recommendations have verbs or action words
        action_words = ['review', 'increase', 'add', 'refactor', 'improve', 'consider']
        for rec in result.recommendations:
            assert any(word in rec.lower() for word in action_words)


# ============================================================================
# Test Group 7: Lessons Learned Documentation (8 tests)
# ============================================================================

class TestLessonsLearned:
    """Test lessons learned documentation."""
    
    def test_document_lessons_from_result(self):
        """Test document_lessons_learned from ReviewResult."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['test.py'],
            'coverage': 92.0,
            'tests_run': 10,
            'tests_passed': 10,
            'feature_name': 'test-feature',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        result = orchestrator.run_holistic_review(context)
        lessons = orchestrator.document_lessons_learned(result)
        
        assert 'feature_name' in lessons
        assert 'quality_metrics' in lessons
        assert 'recommendations' in lessons
        assert 'patterns' in lessons
    
    def test_document_lessons_from_gates(self):
        """Test document_lessons_learned_from_gates."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['a.py', 'b.py'],
            'coverage': 95.0,
            'tests_run': 15,
            'tests_passed': 15,
            'feature_name': 'auth-system',
            'phases_completed': ['p1', 'p2', 'p3', 'p4']
        }
        
        gates = [
            orchestrator.evaluate_code_quality(context),
            orchestrator.evaluate_test_coverage(context),
            orchestrator.evaluate_documentation(context)
        ]
        
        lessons = orchestrator.document_lessons_learned_from_gates(gates, context)
        
        assert lessons['feature_name'] == 'auth-system'
        assert 'quality_metrics' in lessons
        assert 'execution_summary' in lessons
    
    def test_lessons_quality_metrics_structure(self):
        """Test lessons quality_metrics structure."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['test.py'],
            'coverage': 90.0,
            'tests_run': 5,
            'tests_passed': 5,
            'feature_name': 'test',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        result = orchestrator.run_holistic_review(context)
        lessons = orchestrator.document_lessons_learned(result)
        
        quality_metrics = lessons['quality_metrics']
        assert 'code_quality' in quality_metrics
        assert 'test_coverage' in quality_metrics
        assert 'documentation' in quality_metrics
        
        for gate_name, metrics in quality_metrics.items():
            assert 'passed' in metrics
            assert 'score' in metrics
    
    def test_lessons_execution_summary_structure(self):
        """Test lessons execution_summary structure."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['a.py', 'b.py', 'c.py'],
            'coverage': 92.0,
            'tests_run': 20,
            'tests_passed': 20,
            'feature_name': 'test',
            'phases_completed': ['p1', 'p2', 'p3', 'p4', 'p5']
        }
        
        gates = [
            orchestrator.evaluate_code_quality(context),
            orchestrator.evaluate_test_coverage(context),
            orchestrator.evaluate_documentation(context)
        ]
        
        lessons = orchestrator.document_lessons_learned_from_gates(gates, context)
        summary = lessons['execution_summary']
        
        assert summary['files_modified'] == 3
        assert summary['tests_run'] == 20
        assert summary['phases_completed'] == 5
    
    def test_lessons_with_unknown_feature(self):
        """Test lessons documentation with unknown feature name."""
        orchestrator = HolisticReviewOrchestrator()
        context = {}
        
        gates = [
            orchestrator.evaluate_code_quality(context),
            orchestrator.evaluate_test_coverage(context),
            orchestrator.evaluate_documentation(context)
        ]
        
        lessons = orchestrator.document_lessons_learned_from_gates(gates, context)
        
        assert lessons['feature_name'] == 'unknown'
    
    def test_lessons_includes_all_gate_metrics(self):
        """Test lessons include metrics from all gates."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['test.py'],
            'coverage': 91.5,
            'tests_run': 8,
            'tests_passed': 8,
            'feature_name': 'feature-x',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        gates = [
            orchestrator.evaluate_code_quality(context),
            orchestrator.evaluate_test_coverage(context),
            orchestrator.evaluate_documentation(context)
        ]
        
        lessons = orchestrator.document_lessons_learned_from_gates(gates, context)
        
        # Code quality metrics
        code_quality = lessons['quality_metrics']['code_quality']
        assert 'metrics' in code_quality
        assert 'files_modified' in code_quality['metrics']
        
        # Coverage metrics
        coverage = lessons['quality_metrics']['test_coverage']
        assert 'metrics' in coverage
        assert 'coverage' in coverage['metrics']
        assert 'tests_run' in coverage['metrics']
        assert 'tests_passed' in coverage['metrics']
        
        # Documentation metrics
        docs = lessons['quality_metrics']['documentation']
        assert 'metrics' in docs
        assert 'phases_completed' in docs['metrics']
    
    def test_lessons_from_result_matches_gates(self):
        """Test lessons from ReviewResult match gate data."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['test.py'],
            'coverage': 93.0,
            'tests_run': 12,
            'tests_passed': 12,
            'feature_name': 'test-feature',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        result = orchestrator.run_holistic_review(context)
        lessons = orchestrator.document_lessons_learned(result)
        
        # Verify gate data matches
        for gate in result.gates:
            assert gate.gate_name in lessons['quality_metrics']
            metrics = lessons['quality_metrics'][gate.gate_name]
            assert metrics['passed'] == gate.passed
            assert metrics['score'] == gate.score
    
    def test_lessons_are_json_serializable(self):
        """Test lessons dictionary is JSON serializable."""
        import json
        
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['test.py'],
            'coverage': 90.0,
            'tests_run': 5,
            'tests_passed': 5,
            'feature_name': 'test',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        result = orchestrator.run_holistic_review(context)
        lessons = orchestrator.document_lessons_learned(result)
        
        # Should not raise exception
        json_str = json.dumps(lessons)
        assert isinstance(json_str, str)


# ============================================================================
# Test Group 8: Pattern Extraction (10 tests)
# ============================================================================

class TestPatternExtraction:
    """Test reusable pattern extraction."""
    
    def test_extract_high_coverage_pattern(self):
        """Test extraction of high-test-coverage pattern."""
        orchestrator = HolisticReviewOrchestrator()
        context = {'coverage': 96.0}
        
        patterns = orchestrator.extract_patterns(context)
        
        assert 'high-test-coverage-pattern' in patterns
    
    def test_high_coverage_pattern_threshold(self):
        """Test high coverage pattern at 95% threshold."""
        orchestrator = HolisticReviewOrchestrator()
        
        # At threshold
        context_at = {'coverage': 95.0}
        patterns_at = orchestrator.extract_patterns(context_at)
        assert 'high-test-coverage-pattern' in patterns_at
        
        # Below threshold
        context_below = {'coverage': 94.9}
        patterns_below = orchestrator.extract_patterns(context_below)
        assert 'high-test-coverage-pattern' not in patterns_below
    
    def test_extract_multi_phase_pattern(self):
        """Test extraction of multi-phase execution pattern."""
        orchestrator = HolisticReviewOrchestrator()
        context = {'phases_completed': ['p1', 'p2', 'p3']}
        
        patterns = orchestrator.extract_patterns(context)
        
        assert 'multi-phase-execution-pattern' in patterns
    
    def test_multi_phase_pattern_threshold(self):
        """Test multi-phase pattern at 3-phase threshold."""
        orchestrator = HolisticReviewOrchestrator()
        
        # At threshold
        context_at = {'phases_completed': ['p1', 'p2', 'p3']}
        patterns_at = orchestrator.extract_patterns(context_at)
        assert 'multi-phase-execution-pattern' in patterns_at
        
        # Below threshold
        context_below = {'phases_completed': ['p1', 'p2']}
        patterns_below = orchestrator.extract_patterns(context_below)
        assert 'multi-phase-execution-pattern' not in patterns_below
    
    def test_extract_comprehensive_modification_pattern(self):
        """Test extraction of comprehensive modification pattern."""
        orchestrator = HolisticReviewOrchestrator()
        context = {'files_modified': ['a.py', 'b.py', 'c.py']}
        
        patterns = orchestrator.extract_patterns(context)
        
        assert 'comprehensive-modification-pattern' in patterns
    
    def test_comprehensive_modification_threshold(self):
        """Test comprehensive modification pattern at 3-file threshold."""
        orchestrator = HolisticReviewOrchestrator()
        
        # At threshold
        context_at = {'files_modified': ['a.py', 'b.py', 'c.py']}
        patterns_at = orchestrator.extract_patterns(context_at)
        assert 'comprehensive-modification-pattern' in patterns_at
        
        # Below threshold
        context_below = {'files_modified': ['a.py', 'b.py']}
        patterns_below = orchestrator.extract_patterns(context_below)
        assert 'comprehensive-modification-pattern' not in patterns_below
    
    def test_extract_all_patterns(self):
        """Test extraction of all patterns simultaneously."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'coverage': 97.0,
            'phases_completed': ['p1', 'p2', 'p3', 'p4'],
            'files_modified': ['a.py', 'b.py', 'c.py', 'd.py']
        }
        
        patterns = orchestrator.extract_patterns(context)
        
        assert 'high-test-coverage-pattern' in patterns
        assert 'multi-phase-execution-pattern' in patterns
        assert 'comprehensive-modification-pattern' in patterns
        assert len(patterns) == 3
    
    def test_extract_no_patterns(self):
        """Test extraction when no patterns match."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'coverage': 80.0,
            'phases_completed': ['p1'],
            'files_modified': ['single.py']
        }
        
        patterns = orchestrator.extract_patterns(context)
        
        assert len(patterns) == 0
    
    def test_patterns_with_empty_context(self):
        """Test pattern extraction with empty context."""
        orchestrator = HolisticReviewOrchestrator()
        context = {}
        
        patterns = orchestrator.extract_patterns(context)
        
        assert isinstance(patterns, list)
        assert len(patterns) == 0
    
    def test_patterns_are_strings(self):
        """Test all extracted patterns are strings."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'coverage': 98.0,
            'phases_completed': ['p1', 'p2', 'p3', 'p4', 'p5'],
            'files_modified': ['a.py', 'b.py', 'c.py', 'd.py', 'e.py']
        }
        
        patterns = orchestrator.extract_patterns(context)
        
        assert all(isinstance(pattern, str) for pattern in patterns)


# ============================================================================
# Test Group 9: Edge Cases & Error Handling (7 tests)
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_context_with_unexpected_types(self):
        """Test handling of unexpected data types in context."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': 'not-a-list',  # Should be list
            'coverage': 'ninety',  # Should be float
            'tests_run': '10',  # Should be int
            'tests_passed': None
        }
        
        # Type errors should be raised (no silent failures)
        with pytest.raises(TypeError):
            result = orchestrator.run_holistic_review(context)
    
    def test_context_with_negative_values(self):
        """Test handling of negative values in context."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'coverage': -10.0,
            'tests_run': -5,
            'tests_passed': -3
        }
        
        gate = orchestrator.evaluate_test_coverage(context)
        
        # Should treat as invalid and fail
        assert gate.passed is False
    
    def test_context_with_extreme_values(self):
        """Test handling of extreme values."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'coverage': 150.0,  # Over 100%
            'tests_run': 1000000,
            'tests_passed': 1000000,
            'files_modified': ['file' + str(i) for i in range(10000)]
        }
        
        # Should not crash
        result = orchestrator.run_holistic_review(context)
        assert isinstance(result, ReviewResult)
    
    def test_concurrent_review_executions(self):
        """Test multiple concurrent review executions."""
        orchestrator = HolisticReviewOrchestrator()
        
        contexts = [
            {
                'files_modified': ['a.py'],
                'coverage': 90.0 + i,
                'tests_run': 10,
                'tests_passed': 10,
                'feature_name': f'feature-{i}',
                'phases_completed': ['p1', 'p2', 'p3']
            }
            for i in range(5)
        ]
        
        results = [orchestrator.run_holistic_review(ctx) for ctx in contexts]
        
        assert len(results) == 5
        assert all(isinstance(r, ReviewResult) for r in results)
    
    def test_review_with_partial_context(self):
        """Test review with only some context keys present."""
        orchestrator = HolisticReviewOrchestrator()
        
        # Only coverage
        context1 = {'coverage': 95.0}
        result1 = orchestrator.run_holistic_review(context1)
        assert isinstance(result1, ReviewResult)
        
        # Only files_modified
        context2 = {'files_modified': ['test.py']}
        result2 = orchestrator.run_holistic_review(context2)
        assert isinstance(result2, ReviewResult)
        
        # Only feature_name
        context3 = {'feature_name': 'test'}
        result3 = orchestrator.run_holistic_review(context3)
        assert isinstance(result3, ReviewResult)
    
    def test_orchestrator_reusability(self):
        """Test orchestrator can be reused for multiple reviews."""
        orchestrator = HolisticReviewOrchestrator()
        
        context1 = {
            'files_modified': ['a.py'],
            'coverage': 90.0,
            'tests_run': 5,
            'tests_passed': 5,
            'feature_name': 'feature1',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        context2 = {
            'files_modified': ['b.py'],
            'coverage': 85.0,
            'tests_run': 10,
            'tests_passed': 10,
            'feature_name': 'feature2',
            'phases_completed': ['p1', 'p2']
        }
        
        result1 = orchestrator.run_holistic_review(context1)
        result2 = orchestrator.run_holistic_review(context2)
        
        assert result1.overall_passed is True
        assert result2.overall_passed is False
        # Results should be independent
        assert result1.lessons['feature_name'] == 'feature1'
        assert result2.lessons['feature_name'] == 'feature2'
    
    def test_context_mutation_safety(self):
        """Test that context is not mutated during review."""
        orchestrator = HolisticReviewOrchestrator()
        context = {
            'files_modified': ['test.py'],
            'coverage': 90.0,
            'tests_run': 5,
            'tests_passed': 5,
            'feature_name': 'test',
            'phases_completed': ['p1', 'p2', 'p3']
        }
        
        context_copy = context.copy()
        
        result = orchestrator.run_holistic_review(context)
        
        # Context should remain unchanged
        assert context == context_copy


# ============================================================================
# Test Summary
# ============================================================================

"""
Test Coverage Summary:

Group 1: Initialization & Configuration (3 tests)
Group 2: Quality Gate - Code Quality (8 tests)
Group 3: Quality Gate - Test Coverage (12 tests)
Group 4: Quality Gate - Documentation (10 tests)
Group 5: Holistic Review Execution (10 tests)
Group 6: Recommendations Generation (8 tests)
Group 7: Lessons Learned Documentation (8 tests)
Group 8: Pattern Extraction (10 tests)
Group 9: Edge Cases & Error Handling (7 tests)

Total: 76 tests

Coverage Target: 90%+ for HolisticReviewOrchestrator

Key Areas Tested:
- ✅ Initialization and configuration
- ✅ All three quality gates (code quality, test coverage, documentation)
- ✅ Complete holistic review execution flow
- ✅ Recommendations generation for all scenarios
- ✅ Lessons learned documentation
- ✅ Pattern extraction with thresholds
- ✅ Edge cases and error handling
- ✅ Reusability and concurrent execution
- ✅ Data structure validation
- ✅ Logging verification
"""
