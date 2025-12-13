"""
Tests for Code Quality Orchestrator.
"""

import pytest
from pathlib import Path
from src.operations.utilities.code_quality_orchestrator import (
    CodeQualityOrchestrator,
    CodeReviewReport,
    ComplexityReport,
    QualityScorecard
)


@pytest.fixture
def orchestrator():
    return CodeQualityOrchestrator()


@pytest.fixture
def sample_code():
    return '''
def simple_function(x):
    return x + 1

def complex_function(a, b, c, d):
    if a > 0:
        if b > 0:
            if c > 0:
                return d
    return 0
'''


class TestCodeReview:
    def test_run_code_review(self, orchestrator, sample_code):
        report = orchestrator.run_code_review(sample_code)
        assert isinstance(report, CodeReviewReport)
        assert len(report.issues) >= 0

    def test_code_review_detects_complexity(self, orchestrator, sample_code):
        report = orchestrator.run_code_review(sample_code)
        assert 'complex_function' in str(report.issues) or report.complexity_warnings > 0


class TestComplexityAnalysis:
    def test_analyze_complexity(self, orchestrator, sample_code):
        report = orchestrator.analyze_complexity(sample_code)
        assert isinstance(report, ComplexityReport)
        assert len(report.functions) > 0

    def test_complexity_scores(self, orchestrator, sample_code):
        report = orchestrator.analyze_complexity(sample_code)
        assert any(f['complexity'] > 1 for f in report.functions)


class TestQualityScorecard:
    def test_generate_scorecard(self, orchestrator, sample_code):
        scorecard = orchestrator.generate_scorecard(sample_code)
        assert isinstance(scorecard, QualityScorecard)
        assert 0 <= scorecard.overall_score <= 100

    def test_scorecard_metrics(self, orchestrator, sample_code):
        scorecard = orchestrator.generate_scorecard(sample_code)
        assert hasattr(scorecard, 'complexity_score')
        assert hasattr(scorecard, 'style_score')
