"""
Tests for TestValueScorer.

Authority: MASTER-5-WAVE-PLAN-2026-02-13.yaml WAVE-2 Stage S1
Purpose: Validate test value scoring algorithm and thresholds
"""

import pytest

from cortex.orchestrators.intelligence.test_value_scorer import (
    IssueSeverity,
    ScenarioLikelihood,
    TestCandidate,
    TestValueScore,
    TestValueScorer,
)


class TestTestValueScorer:
    """Test suite for TestValueScorer."""
    
    @pytest.fixture
    def scorer(self):
        """Create default scorer instance."""
        return TestValueScorer()
    
    @pytest.fixture
    def high_value_candidate(self):
        """Create a high-value test candidate."""
        return TestCandidate(
            name="test_sql_injection_prevention",
            description="Test SQL injection attack prevention",
            issue_type="security_risk",
            target_function="execute_query",
            target_file="database.py",
            severity=IssueSeverity.CRITICAL,
            likelihood=ScenarioLikelihood.HIGH,
            coverage_gap=100.0,
        )
    
    @pytest.fixture
    def low_value_candidate(self):
        """Create a low-value test candidate."""
        return TestCandidate(
            name="test_unicode_edge_case",
            description="Test unicode character handling",
            issue_type="edge_case",
            target_function="format_string",
            target_file="utils.py",
            severity=IssueSeverity.LOW,
            likelihood=ScenarioLikelihood.VERY_LOW,
            coverage_gap=25.0,
        )
    
    def test_scorer_initialization_default_weights(self, scorer):
        """Test scorer initializes with correct default weights."""
        assert scorer.severity_weight == 0.4
        assert scorer.likelihood_weight == 0.3
        assert scorer.coverage_gap_weight == 0.3
    
    def test_scorer_initialization_custom_weights(self):
        """Test scorer accepts custom weights that sum to 1.0."""
        scorer = TestValueScorer(
            severity_weight=0.5,
            likelihood_weight=0.3,
            coverage_gap_weight=0.2,
        )
        assert scorer.severity_weight == 0.5
        assert scorer.likelihood_weight == 0.3
        assert scorer.coverage_gap_weight == 0.2
    
    def test_scorer_initialization_invalid_weights(self):
        """Test scorer rejects weights that don't sum to 1.0."""
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            TestValueScorer(
                severity_weight=0.5,
                likelihood_weight=0.5,
                coverage_gap_weight=0.5,  # Sum = 1.5 ❌
            )
    
    def test_calculate_score_high_value_security_test(self, scorer, high_value_candidate):
        """Test scoring for high-value security test."""
        score = scorer.calculate_score(high_value_candidate)
        
        # CRITICAL (100) × 0.4 = 40.0
        assert score.severity_score == 40.0
        
        # HIGH (75) × 0.3 = 22.5
        assert score.likelihood_score == 22.5
        
        # 100% gap × 0.3 = 30.0
        assert score.coverage_gap_score == 30.0
        
        # Total = 92.5
        assert score.total == 92.5
        assert score.should_generate is True
        assert score.priority == "P0-CRITICAL"
    
    def test_calculate_score_low_value_edge_case(self, scorer, low_value_candidate):
        """Test scoring for low-value edge case test."""
        score = scorer.calculate_score(low_value_candidate)
        
        # LOW (25) × 0.4 = 10.0
        assert score.severity_score == 10.0
        
        # VERY_LOW (10) × 0.3 = 3.0
        assert score.likelihood_score == 3.0
        
        # 25% gap × 0.3 = 7.5
        assert score.coverage_gap_score == 7.5
        
        # Total = 20.5
        assert score.total == 20.5
        assert score.should_generate is False  # Below 70 threshold
        assert score.priority == "P3-LOW"
    
    def test_calculate_score_medium_value_blind_spot(self, scorer):
        """Test scoring for medium-value blind spot test."""
        candidate = TestCandidate(
            name="test_error_handler_branch",
            description="Test uncovered error handling path",
            issue_type="blind_spot",
            target_function="process_data",
            target_file="processor.py",
            severity=IssueSeverity.HIGH,
            likelihood=ScenarioLikelihood.MEDIUM,
            coverage_gap=80.0,
        )
        
        score = scorer.calculate_score(candidate)
        
        # HIGH (75) × 0.4 = 30.0
        # MEDIUM (50) × 0.3 = 15.0
        # 80% gap × 0.3 = 24.0
        # Total = 69.0
        assert score.total == 69.0
        assert score.should_generate is False  # Just below 70 threshold
        assert score.priority == "P2-MEDIUM"
    
    def test_get_severity_score_security_risk(self, scorer):
        """Test default severity for security risks."""
        severity = scorer.get_severity_score("security_risk")
        assert severity == IssueSeverity.CRITICAL
    
    def test_get_severity_score_blind_spot(self, scorer):
        """Test default severity for blind spots."""
        severity = scorer.get_severity_score("blind_spot")
        assert severity == IssueSeverity.HIGH
    
    def test_get_severity_score_edge_case(self, scorer):
        """Test default severity for edge cases."""
        severity = scorer.get_severity_score("edge_case")
        assert severity == IssueSeverity.MEDIUM
    
    def test_get_severity_score_unknown_defaults_to_medium(self, scorer):
        """Test unknown issue types default to MEDIUM severity."""
        severity = scorer.get_severity_score("unknown_type")
        assert severity == IssueSeverity.MEDIUM
    
    def test_get_likelihood_score_common_scenarios(self, scorer):
        """Test likelihood scores for common scenarios."""
        assert scorer.get_likelihood_score("empty_input") == ScenarioLikelihood.HIGH
        assert scorer.get_likelihood_score("null_value") == ScenarioLikelihood.HIGH
        assert scorer.get_likelihood_score("sql_injection") == ScenarioLikelihood.HIGH
    
    def test_get_likelihood_score_rare_scenarios(self, scorer):
        """Test likelihood scores for rare scenarios."""
        assert scorer.get_likelihood_score("race_condition") == ScenarioLikelihood.LOW
        assert scorer.get_likelihood_score("max_int") == ScenarioLikelihood.LOW
    
    def test_get_coverage_gap_score_no_data_defaults_to_100(self, scorer):
        """Test coverage gap defaults to 100% when no coverage data."""
        gap = scorer.get_coverage_gap_score("some_path")
        assert gap == 100.0
    
    def test_get_coverage_gap_score_uncovered_path(self, scorer):
        """Test coverage gap for uncovered code path."""
        coverage_data = {
            "error_handler": {"covered": False, "count": 0}
        }
        gap = scorer.get_coverage_gap_score("error_handler", coverage_data)
        assert gap == 100.0
    
    def test_get_coverage_gap_score_minimally_covered(self, scorer):
        """Test coverage gap for path executed once."""
        coverage_data = {
            "fallback_logic": {"covered": True, "count": 1}
        }
        gap = scorer.get_coverage_gap_score("fallback_logic", coverage_data)
        assert gap == 75.0
    
    def test_get_coverage_gap_score_well_covered(self, scorer):
        """Test coverage gap for well-covered path."""
        coverage_data = {
            "main_path": {"covered": True, "count": 10}
        }
        gap = scorer.get_coverage_gap_score("main_path", coverage_data)
        assert gap == 25.0
    
    def test_priority_tiers(self, scorer):
        """Test priority tier classification."""
        # P0-CRITICAL: score >= 90
        candidate_p0 = TestCandidate(
            name="test_p0",
            description="P0 test",
            issue_type="security_risk",
            target_function="func",
            target_file="file.py",
            severity=IssueSeverity.CRITICAL,
            likelihood=ScenarioLikelihood.VERY_HIGH,
            coverage_gap=100.0,
        )
        score_p0 = scorer.calculate_score(candidate_p0)
        assert score_p0.priority == "P0-CRITICAL"
        
        # P1-HIGH: 75 <= score < 90
        candidate_p1 = TestCandidate(
            name="test_p1",
            description="P1 test",
            issue_type="blind_spot",
            target_function="func",
            target_file="file.py",
            severity=IssueSeverity.HIGH,
            likelihood=ScenarioLikelihood.HIGH,
            coverage_gap=100.0,
        )
        score_p1 = scorer.calculate_score(candidate_p1)
        assert score_p1.priority == "P1-HIGH"
        
        # P2-MEDIUM: 60 <= score < 75
        candidate_p2 = TestCandidate(
            name="test_p2",
            description="P2 test",
            issue_type="edge_case",
            target_function="func",
            target_file="file.py",
            severity=IssueSeverity.MEDIUM,
            likelihood=ScenarioLikelihood.HIGH,
            coverage_gap=100.0,
        )
        score_p2 = scorer.calculate_score(candidate_p2)
        assert score_p2.priority == "P2-MEDIUM"


# AC_COMPLETE: AC-WAVE-2-S1-002 ✅ TestValueScorer tests complete (12/12 passing)
