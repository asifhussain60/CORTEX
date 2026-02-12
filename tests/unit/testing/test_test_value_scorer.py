"""
Tests for TestValueScorer - Phase 71 S4.

AC-ID: PHASE-71-S4
Purpose: Verify 5-dimension test quality scoring

Test Coverage:
1. Metric calculation for each dimension
2. Tier assignment based on score
3. Test filtering by tier
4. Summary statistics
5. Edge cases and boundary conditions

Author: Asif Hussain
Date: 2026-02-10
"""

import pytest
from cortex.testing.test_value_scorer import (
    TestValueScorer,
    TestScore,
    TestMetrics,
    ScoreTier,
    get_test_value_scorer,
)


# =============================================================================
# Test: ScoreTier Enum
# =============================================================================

class TestScoreTier:
    """Tests for ScoreTier enum."""
    
    def test_tier_values(self):
        """Tiers should have expected values."""
        assert ScoreTier.ABSOLUTE.value == "ABSOLUTE"
        assert ScoreTier.HIGH.value == "HIGH"
        assert ScoreTier.MEDIUM.value == "MEDIUM"
        assert ScoreTier.LOW.value == "LOW"


# =============================================================================
# Test: TestMetrics
# =============================================================================

class TestMetricsTests:
    """Tests for TestMetrics class."""
    
    def test_metrics_creation(self):
        """TestMetrics should be creatable with required fields."""
        metrics = TestMetrics(
            coverage_percent=85.0,
            edge_cases_covered=7,
            total_edge_cases=10,
            mutations_caught=18,
            total_mutations=20,
        )
        
        assert metrics.coverage_percent == 85.0
        assert metrics.edge_cases_covered == 7
        assert metrics.total_mutations == 20
    
    def test_metrics_coverage_score(self):
        """Coverage score should be 0-1 normalized."""
        # 85% coverage
        metrics = TestMetrics(
            coverage_percent=85.0,
            edge_cases_covered=0,
            total_edge_cases=0,
            mutations_caught=0,
            total_mutations=0,
        )
        
        assert metrics.get_coverage_score() == 0.85
    
    def test_metrics_coverage_score_capped(self):
        """Coverage score should not exceed 1.0."""
        metrics = TestMetrics(
            coverage_percent=150.0,  # Invalid but let's test capping
            edge_cases_covered=0,
            total_edge_cases=0,
            mutations_caught=0,
            total_mutations=0,
        )
        
        assert metrics.get_coverage_score() <= 1.0
    
    def test_metrics_edge_case_score(self):
        """Edge case score should be ratio."""
        metrics = TestMetrics(
            coverage_percent=0,
            edge_cases_covered=7,
            total_edge_cases=10,
            mutations_caught=0,
            total_mutations=0,
        )
        
        assert metrics.get_edge_case_score() == 0.7
    
    def test_metrics_edge_case_score_no_cases(self):
        """Edge case score should be neutral when no cases."""
        metrics = TestMetrics(
            coverage_percent=0,
            edge_cases_covered=0,
            total_edge_cases=0,
            mutations_caught=0,
            total_mutations=0,
        )
        
        assert metrics.get_edge_case_score() == 0.5
    
    def test_metrics_mutation_score(self):
        """Mutation score should be ratio of caught mutations."""
        metrics = TestMetrics(
            coverage_percent=0,
            edge_cases_covered=0,
            total_edge_cases=0,
            mutations_caught=18,
            total_mutations=20,
        )
        
        assert metrics.get_mutation_score() == 0.9
    
    def test_metrics_regression_score(self):
        """Regression score should be average of coverage and edge cases."""
        metrics = TestMetrics(
            coverage_percent=80.0,
            edge_cases_covered=6,
            total_edge_cases=10,
            mutations_caught=0,
            total_mutations=0,
        )
        
        # (0.8 + 0.6) / 2 = 0.7
        assert abs(metrics.get_regression_score() - 0.7) < 0.01
    
    def test_metrics_brittleness_score(self):
        """Brittleness score should penalize flakiness."""
        metrics = TestMetrics(
            coverage_percent=0,
            edge_cases_covered=0,
            total_edge_cases=0,
            mutations_caught=0,
            total_mutations=0,
            flakiness_percent=10.0,  # 10% flaky
        )
        
        # 1.0 - 0.1 = 0.9
        assert metrics.get_brittleness_score() == 0.9
    
    def test_metrics_brittleness_with_false_positives(self):
        """Brittleness score should also penalize false positives."""
        metrics = TestMetrics(
            coverage_percent=0,
            edge_cases_covered=0,
            total_edge_cases=0,
            mutations_caught=0,
            total_mutations=0,
            flakiness_percent=0.0,
            false_positives=5,
        )
        
        # 1.0 - (5 * 0.1) = 0.5
        assert metrics.get_brittleness_score() == 0.5


# =============================================================================
# Test: TestScore
# =============================================================================

class TestScoreTests:
    """Tests for TestScore class."""
    
    def test_test_score_from_metrics_absolute(self):
        """Metrics with high scores should yield ABSOLUTE tier."""
        metrics = TestMetrics(
            coverage_percent=98.0,
            edge_cases_covered=10,
            total_edge_cases=10,
            mutations_caught=20,
            total_mutations=20,
            flakiness_percent=0.0,
        )
        
        score = TestScore.from_metrics("test_perfect", metrics)
        
        assert score.tier == ScoreTier.ABSOLUTE
        assert score.overall_score >= 0.9
    
    def test_test_score_from_metrics_high(self):
        """Metrics with good scores should yield HIGH tier."""
        metrics = TestMetrics(
            coverage_percent=85.0,
            edge_cases_covered=8,
            total_edge_cases=10,
            mutations_caught=18,
            total_mutations=20,
            flakiness_percent=5.0,
        )
        
        score = TestScore.from_metrics("test_good", metrics)
        
        assert score.tier == ScoreTier.HIGH
        assert 0.7 <= score.overall_score < 0.9
    
    def test_test_score_from_metrics_medium(self):
        """Metrics with moderate scores should yield MEDIUM tier."""
        metrics = TestMetrics(
            coverage_percent=60.0,
            edge_cases_covered=4,
            total_edge_cases=10,
            mutations_caught=10,
            total_mutations=20,
            flakiness_percent=10.0,
        )
        
        score = TestScore.from_metrics("test_okay", metrics)
        
        assert score.tier == ScoreTier.MEDIUM
        assert 0.4 <= score.overall_score < 0.7
    
    def test_test_score_from_metrics_low(self):
        """Metrics with poor scores should yield LOW tier."""
        metrics = TestMetrics(
            coverage_percent=20.0,
            edge_cases_covered=1,
            total_edge_cases=10,
            mutations_caught=5,
            total_mutations=20,
            flakiness_percent=30.0,
        )
        
        score = TestScore.from_metrics("test_poor", metrics)
        
        assert score.tier == ScoreTier.LOW
        assert score.overall_score < 0.4
    
    def test_test_score_to_dict(self):
        """TestScore should convert to dictionary."""
        metrics = TestMetrics(
            coverage_percent=85.0,
            edge_cases_covered=8,
            total_edge_cases=10,
            mutations_caught=18,
            total_mutations=20,
        )
        
        score = TestScore.from_metrics("test_example", metrics)
        score_dict = score.to_dict()
        
        assert score_dict["test_name"] == "test_example"
        assert "overall_score" in score_dict
        assert "tier" in score_dict
        assert "dimensions" in score_dict
        assert "coverage" in score_dict["dimensions"]


# =============================================================================
# Test: TestValueScorer
# =============================================================================

class TestTestValueScorer:
    """Tests for TestValueScorer."""
    
    def test_scorer_initialization(self):
        """Scorer should initialize empty."""
        scorer = TestValueScorer()
        
        summary = scorer.get_score_summary()
        assert summary["total_tests"] == 0
    
    def test_score_single_test(self):
        """Scorer should score a single test."""
        scorer = TestValueScorer()
        
        metrics = TestMetrics(
            coverage_percent=85.0,
            edge_cases_covered=8,
            total_edge_cases=10,
            mutations_caught=18,
            total_mutations=20,
        )
        
        score = scorer.score_test("test_example", metrics)
        
        assert score.test_name == "test_example"
        assert score.tier == ScoreTier.HIGH
    
    def test_score_multiple_tests(self):
        """Scorer should track multiple test scores."""
        scorer = TestValueScorer()
        
        # High quality test
        scorer.score_test(
            "test_high",
            TestMetrics(85, 8, 10, 18, 20),
        )
        
        # Low quality test
        scorer.score_test(
            "test_low",
            TestMetrics(20, 1, 10, 5, 20),
        )
        
        summary = scorer.get_score_summary()
        assert summary["total_tests"] == 2
        assert summary["by_tier"]["HIGH"] == 1
        assert summary["by_tier"]["LOW"] == 1
    
    def test_filter_tests_by_tier(self):
        """Scorer should filter tests by tier."""
        scorer = TestValueScorer()
        
        # Create tests with different tiers
        scorer.score_test("test_high", TestMetrics(85, 8, 10, 18, 20))
        scorer.score_test("test_medium", TestMetrics(60, 4, 10, 10, 20))
        scorer.score_test("test_low", TestMetrics(20, 1, 10, 5, 20))
        
        # Filter for HIGH only
        high_tests = scorer.filter_tests(
            ["test_high", "test_medium", "test_low"],
            min_tier="HIGH"
        )
        
        assert high_tests == ["test_high"]
    
    def test_get_high_value_tests(self):
        """Scorer should identify high-value tests."""
        scorer = TestValueScorer()
        
        scorer.score_test("test_absolute", TestMetrics(98, 10, 10, 20, 20))
        scorer.score_test("test_high", TestMetrics(85, 8, 10, 18, 20))
        scorer.score_test("test_medium", TestMetrics(60, 4, 10, 10, 20))
        
        high_value = scorer.get_high_value_tests()
        
        assert len(high_value) == 2
        assert all(s.tier in [ScoreTier.HIGH, ScoreTier.ABSOLUTE] for s in high_value)
    
    def test_get_low_value_tests(self):
        """Scorer should identify low-value tests."""
        scorer = TestValueScorer()
        
        scorer.score_test("test_high", TestMetrics(85, 8, 10, 18, 20))
        scorer.score_test("test_medium", TestMetrics(60, 4, 10, 10, 20))
        scorer.score_test("test_low", TestMetrics(20, 1, 10, 5, 20))
        
        low_value = scorer.get_low_value_tests()
        
        assert len(low_value) == 2
        assert all(s.tier in [ScoreTier.LOW, ScoreTier.MEDIUM] for s in low_value)
    
    def test_score_summary(self):
        """Scorer should provide summary statistics."""
        scorer = TestValueScorer()
        
        scorer.score_test("test_high", TestMetrics(85, 8, 10, 18, 20))
        scorer.score_test("test_medium", TestMetrics(60, 4, 10, 10, 20))
        
        summary = scorer.get_score_summary()
        
        assert summary["total_tests"] == 2
        assert summary["average_score"] > 0
        assert "by_tier" in summary
        assert "high_value_count" in summary
        assert "low_value_count" in summary
    
    def test_dimensions_summary(self):
        """Scorer should provide dimension averages."""
        scorer = TestValueScorer()
        
        scorer.score_test("test_1", TestMetrics(80, 8, 10, 16, 20))
        scorer.score_test("test_2", TestMetrics(90, 9, 10, 18, 20))
        
        dims = scorer.get_dimensions_summary()
        
        assert "coverage" in dims
        assert "edge_cases" in dims
        assert "mutation" in dims
        assert "regression" in dims
        assert "brittleness" in dims
        
        # Coverage should be average of 0.8 and 0.9
        assert abs(dims["coverage"] - 0.85) < 0.01
    
    def test_reset(self):
        """Scorer should reset all scores."""
        scorer = TestValueScorer()
        
        scorer.score_test("test_example", TestMetrics(85, 8, 10, 18, 20))
        assert scorer.get_score_summary()["total_tests"] == 1
        
        scorer.reset()
        assert scorer.get_score_summary()["total_tests"] == 0


# =============================================================================
# Test: Singleton Pattern
# =============================================================================

class TestSingleton:
    """Tests for singleton scorer."""
    
    def test_get_test_value_scorer_singleton(self):
        """get_test_value_scorer should return same instance."""
        # Reset first
        import cortex.testing.test_value_scorer as scorer_module
        scorer_module._scorer_instance = None
        
        scorer1 = get_test_value_scorer()
        scorer2 = get_test_value_scorer()
        
        assert scorer1 is scorer2


# =============================================================================
# Test: Integration
# =============================================================================

class TestIntegration:
    """Integration tests for real-world scenarios."""
    
    def test_quality_pyramid_scenario(self):
        """Test quality pyramid: 10% ABSOLUTE, 30% HIGH, 60% other."""
        scorer = TestValueScorer()
        
        # ABSOLUTE tier tests (high quality)
        for i in range(1):
            scorer.score_test(
                f"test_absolute_{i}",
                TestMetrics(95, 10, 10, 19, 20, flakiness_percent=0)
            )
        
        # HIGH tier tests
        for i in range(3):
            scorer.score_test(
                f"test_high_{i}",
                TestMetrics(80, 8, 10, 16, 20, flakiness_percent=5)
            )
        
        # MEDIUM tier tests
        for i in range(4):
            scorer.score_test(
                f"test_medium_{i}",
                TestMetrics(60, 5, 10, 10, 20, flakiness_percent=10)
            )
        
        # LOW tier tests
        for i in range(2):
            scorer.score_test(
                f"test_low_{i}",
                TestMetrics(30, 2, 10, 5, 20, flakiness_percent=20)
            )
        
        summary = scorer.get_score_summary()
        
        assert summary["total_tests"] == 10
        assert summary["by_tier"]["ABSOLUTE"] == 1
        assert summary["by_tier"]["HIGH"] == 3
        
        # High value tests should be 1 + 3 = 4
        assert summary["high_value_count"] == 4
