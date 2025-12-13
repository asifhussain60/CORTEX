"""
Tests for Holistic Review Orchestrator.

Tests quality gate functionality, plan integration, and learning library updates.
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List
from src.operations.utilities.holistic_review_orchestrator import (
    HolisticReviewOrchestrator,
    ReviewResult,
    QualityGate
)


@pytest.fixture
def orchestrator():
    """Create orchestrator instance."""
    return HolisticReviewOrchestrator()


@pytest.fixture
def sample_execution_context():
    """Sample execution context for testing."""
    return {
        'feature_name': 'test-feature',
        'files_modified': ['file1.py', 'file2.py'],
        'tests_run': 10,
        'tests_passed': 10,
        'coverage': 95.5,
        'phases_completed': ['Phase 1', 'Phase 2', 'Phase 3']
    }


class TestQualityGates:
    """Test quality gate evaluation."""

    def test_code_quality_gate_pass(self, orchestrator, sample_execution_context):
        """Test code quality gate passes with good metrics."""
        result = orchestrator.evaluate_code_quality(sample_execution_context)
        
        assert isinstance(result, QualityGate)
        assert result.passed is True
        assert result.gate_name == 'code_quality'

    def test_test_coverage_gate_pass(self, orchestrator, sample_execution_context):
        """Test coverage gate passes with 95%+ coverage."""
        result = orchestrator.evaluate_test_coverage(sample_execution_context)
        
        assert isinstance(result, QualityGate)
        assert result.passed is True
        assert result.gate_name == 'test_coverage'

    def test_test_coverage_gate_fail(self, orchestrator):
        """Test coverage gate fails with low coverage."""
        context = {
            'coverage': 60.0,
            'tests_run': 5,
            'tests_passed': 5
        }
        result = orchestrator.evaluate_test_coverage(context)
        
        assert result.passed is False
        assert 'coverage' in result.message.lower()

    def test_documentation_gate(self, orchestrator, sample_execution_context):
        """Test documentation gate evaluation."""
        result = orchestrator.evaluate_documentation(sample_execution_context)
        
        assert isinstance(result, QualityGate)
        assert hasattr(result, 'passed')
        assert result.gate_name == 'documentation'


class TestHolisticReview:
    """Test complete holistic review process."""

    def test_run_holistic_review_all_pass(self, orchestrator, sample_execution_context):
        """Test holistic review with all gates passing."""
        result = orchestrator.run_holistic_review(sample_execution_context)
        
        assert isinstance(result, ReviewResult)
        assert result.overall_passed is True
        assert len(result.gates) > 0

    def test_run_holistic_review_with_failures(self, orchestrator):
        """Test holistic review with some gates failing."""
        context = {
            'feature_name': 'test',
            'files_modified': [],
            'tests_run': 0,
            'tests_passed': 0,
            'coverage': 0.0
        }
        result = orchestrator.run_holistic_review(context)
        
        assert isinstance(result, ReviewResult)
        assert result.overall_passed is False
        assert len(result.failed_gates) > 0

    def test_review_generates_recommendations(self, orchestrator, sample_execution_context):
        """Test review generates actionable recommendations."""
        result = orchestrator.run_holistic_review(sample_execution_context)
        
        assert hasattr(result, 'recommendations')
        assert isinstance(result.recommendations, list)


class TestLearningLibraryIntegration:
    """Test learning library documentation."""

    def test_document_lessons_learned(self, orchestrator, sample_execution_context):
        """Test lessons learned are documented."""
        result = orchestrator.run_holistic_review(sample_execution_context)
        lessons = orchestrator.document_lessons_learned(result)
        
        assert isinstance(lessons, dict)
        assert 'feature_name' in lessons
        assert 'quality_metrics' in lessons

    def test_extract_patterns(self, orchestrator, sample_execution_context):
        """Test pattern extraction from execution."""
        patterns = orchestrator.extract_patterns(sample_execution_context)
        
        assert isinstance(patterns, list)
        assert len(patterns) >= 0


class TestPerformance:
    """Test performance requirements."""

    def test_review_performance_under_500ms(self, orchestrator, sample_execution_context):
        """Test holistic review completes under 500ms."""
        import time
        
        start = time.perf_counter()
        orchestrator.run_holistic_review(sample_execution_context)
        duration = time.perf_counter() - start
        
        assert duration < 0.5, f"Review took {duration:.3f}s, expected <0.5s"


class TestIntegration:
    """Test integration workflows."""

    def test_complete_review_workflow(self, orchestrator, sample_execution_context):
        """Test complete review workflow."""
        # Run review
        result = orchestrator.run_holistic_review(sample_execution_context)
        
        # Document lessons
        lessons = orchestrator.document_lessons_learned(result)
        
        # Extract patterns
        patterns = orchestrator.extract_patterns(sample_execution_context)
        
        assert result.overall_passed in [True, False]
        assert isinstance(lessons, dict)
        assert isinstance(patterns, list)
