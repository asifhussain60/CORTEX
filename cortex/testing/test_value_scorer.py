"""
Test Value Scorer - Phase 71 S4.

AC-ID: PHASE-71-S4
Purpose: Score test quality using 5-dimension scoring

The TestValueScorer measures test quality across 5 dimensions:
1. Coverage (25%) - How much code is executed
2. Edge Cases (25%) - Boundary condition coverage
3. Mutation Score (20%) - How many mutations would fail
4. Regression Detection (15%) - Can it catch introduced bugs
5. Brittleness (15%) - How stable is the test (false positives)

Usage:
    scorer = TestValueScorer()
    
    # Score a test
    score = scorer.score_test(
        test_function=test_my_feature,
        test_metrics={
            "coverage_percent": 95,
            "edge_cases_covered": 7,
            "total_edge_cases": 10,
            "mutations_caught": 18,
            "total_mutations": 20,
        }
    )
    
    # Get tier
    if score.tier == "HIGH":
        print("Excellent test quality!")
    
    # Extract high-value tests for learning
    high_value_tests = scorer.filter_tests(
        tests=[test1, test2, test3],
        min_tier="HIGH"
    )

Integration:
- TDDOrchestrator uses TestValueScorer to rank tests
- Learning loop prioritizes high-value tests
- Test suites can be optimized by removing low-value tests

Scoring Tiers:
- ABSOLUTE (0.9-1.0): Perfect test quality
- HIGH (0.7-0.9): Excellent, capture learnings
- MEDIUM (0.4-0.7): Acceptable, use selectively
- LOW (0-0.4): Poor quality, consider removing

Author: Asif Hussain
Date: 2026-02-10
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ScoreTier(Enum):
    """Test quality tiers based on score."""
    
    ABSOLUTE = "ABSOLUTE"  # 0.9-1.0: Perfect quality
    HIGH = "HIGH"  # 0.7-0.9: Excellent quality
    MEDIUM = "MEDIUM"  # 0.4-0.7: Acceptable quality
    LOW = "LOW"  # 0-0.4: Poor quality


@dataclass
class TestMetrics:
    """Metrics from test execution."""
    
    coverage_percent: float  # 0-100: Code coverage percentage
    edge_cases_covered: int  # Number of edge cases covered
    total_edge_cases: int  # Total edge cases in code
    mutations_caught: int  # Number of mutations caught
    total_mutations: int  # Total mutations injected
    false_positives: int = 0  # False positive assertions
    execution_time_ms: float = 0.0  # Execution time
    flakiness_percent: float = 0.0  # How often it fails unexpectedly
    
    def get_coverage_score(self) -> float:
        """Calculate coverage dimension (0-1)."""
        return min(1.0, self.coverage_percent / 100.0)
    
    def get_edge_case_score(self) -> float:
        """Calculate edge case dimension (0-1)."""
        if self.total_edge_cases == 0:
            return 0.5  # Neutral if no edge cases
        return min(1.0, self.edge_cases_covered / self.total_edge_cases)
    
    def get_mutation_score(self) -> float:
        """Calculate mutation dimension (0-1)."""
        if self.total_mutations == 0:
            return 0.5  # Neutral if no mutations
        return min(1.0, self.mutations_caught / self.total_mutations)
    
    def get_regression_score(self) -> float:
        """Calculate regression detection dimension (0-1)."""
        # High coverage + edge cases = high regression detection
        coverage = self.get_coverage_score()
        edge_cases = self.get_edge_case_score()
        return (coverage + edge_cases) / 2.0
    
    def get_brittleness_score(self) -> float:
        """Calculate brittleness dimension (0-1)."""
        # Lower flakiness = lower brittleness = higher score
        flakiness_ratio = self.flakiness_percent / 100.0
        stability = 1.0 - flakiness_ratio
        # Also factor in false positives
        false_positive_penalty = min(0.5, self.false_positives * 0.1)
        return max(0.0, stability - false_positive_penalty)


@dataclass
class TestScore:
    """Complete test quality score."""
    
    test_name: str
    overall_score: float  # 0-1
    tier: ScoreTier
    
    # Dimension scores
    coverage_score: float
    edge_case_score: float
    mutation_score: float
    regression_score: float
    brittleness_score: float
    
    # Weights (hardcoded per requirements)
    _weights: Dict[str, float] = field(default_factory=lambda: {
        "coverage": 0.25,
        "edge_cases": 0.25,
        "mutation": 0.20,
        "regression": 0.15,
        "brittleness": 0.15,
    })
    
    @classmethod
    def from_metrics(cls, test_name: str, metrics: TestMetrics) -> "TestScore":
        """Create TestScore from metrics."""
        # Calculate dimension scores
        coverage = metrics.get_coverage_score()
        edge_cases = metrics.get_edge_case_score()
        mutation = metrics.get_mutation_score()
        regression = metrics.get_regression_score()
        brittleness = metrics.get_brittleness_score()
        
        # Weighted average (5 dimensions)
        weights = {
            "coverage": 0.25,
            "edge_cases": 0.25,
            "mutation": 0.20,
            "regression": 0.15,
            "brittleness": 0.15,
        }
        
        overall = (
            coverage * weights["coverage"] +
            edge_cases * weights["edge_cases"] +
            mutation * weights["mutation"] +
            regression * weights["regression"] +
            brittleness * weights["brittleness"]
        )
        
        # Determine tier
        if overall >= 0.9:
            tier = ScoreTier.ABSOLUTE
        elif overall >= 0.7:
            tier = ScoreTier.HIGH
        elif overall >= 0.4:
            tier = ScoreTier.MEDIUM
        else:
            tier = ScoreTier.LOW
        
        return cls(
            test_name=test_name,
            overall_score=overall,
            tier=tier,
            coverage_score=coverage,
            edge_case_score=edge_cases,
            mutation_score=mutation,
            regression_score=regression,
            brittleness_score=brittleness,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_name": self.test_name,
            "overall_score": round(self.overall_score, 3),
            "tier": self.tier.value,
            "dimensions": {
                "coverage": round(self.coverage_score, 3),
                "edge_cases": round(self.edge_case_score, 3),
                "mutation": round(self.mutation_score, 3),
                "regression": round(self.regression_score, 3),
                "brittleness": round(self.brittleness_score, 3),
            }
        }


class TestValueScorer:
    """
    Score test quality using 5-dimension framework.
    
    AC-ID: PHASE-71-S4
    """
    
    def __init__(self) -> None:
        """Initialize scorer."""
        self._scores: List[TestScore] = []
        self._metrics_cache: Dict[str, TestMetrics] = {}
    
    def score_test(
        self,
        test_name: str,
        metrics: TestMetrics,
    ) -> TestScore:
        """
        Score a single test.
        
        Args:
            test_name: Name of the test
            metrics: TestMetrics from execution
            
        Returns:
            TestScore with overall and dimension scores
        """
        # Create score
        score = TestScore.from_metrics(test_name, metrics)
        
        # Cache metrics
        self._metrics_cache[test_name] = metrics
        
        # Store score
        self._scores.append(score)
        
        logger.info(
            f"Scored test '{test_name}': {score.tier.value} "
            f"({score.overall_score:.1%})"
        )
        
        return score
    
    def filter_tests(
        self,
        test_names: List[str],
        min_tier: str = "MEDIUM",
    ) -> List[str]:
        """
        Filter tests by quality tier.
        
        Args:
            test_names: Names of tests to filter
            min_tier: Minimum tier (LOW, MEDIUM, HIGH, ABSOLUTE)
            
        Returns:
            Filtered test names meeting minimum tier
        """
        min_tier_enum = ScoreTier[min_tier]
        
        # Tier hierarchy
        tier_order = {
            ScoreTier.LOW: 0,
            ScoreTier.MEDIUM: 1,
            ScoreTier.HIGH: 2,
            ScoreTier.ABSOLUTE: 3,
        }
        
        min_order = tier_order[min_tier_enum]
        
        filtered = []
        for test_name in test_names:
            # Find score for this test
            score = next(
                (s for s in self._scores if s.test_name == test_name),
                None
            )
            
            if score and tier_order[score.tier] >= min_order:
                filtered.append(test_name)
        
        logger.info(
            f"Filtered {len(filtered)}/{len(test_names)} tests "
            f"with tier >= {min_tier}"
        )
        
        return filtered
    
    def get_high_value_tests(self) -> List[TestScore]:
        """
        Get all tests with HIGH or ABSOLUTE tier.
        
        Returns:
            List of high-value test scores
        """
        return [
            s for s in self._scores
            if s.tier in [ScoreTier.HIGH, ScoreTier.ABSOLUTE]
        ]
    
    def get_low_value_tests(self) -> List[TestScore]:
        """
        Get all tests with LOW or MEDIUM tier.
        
        Returns:
            List of low-value test scores
        """
        return [
            s for s in self._scores
            if s.tier in [ScoreTier.LOW, ScoreTier.MEDIUM]
        ]
    
    def get_score_summary(self) -> Dict[str, Any]:
        """
        Get summary of all scored tests.
        
        Returns:
            Summary dictionary with tier distribution
        """
        if not self._scores:
            return {
                "total_tests": 0,
                "average_score": 0.0,
                "by_tier": {},
            }
        
        # Count by tier
        by_tier = {tier.value: 0 for tier in ScoreTier}
        for score in self._scores:
            by_tier[score.tier.value] += 1
        
        # Calculate average
        avg_score = sum(s.overall_score for s in self._scores) / len(self._scores)
        
        return {
            "total_tests": len(self._scores),
            "average_score": round(avg_score, 3),
            "by_tier": by_tier,
            "high_value_count": len(self.get_high_value_tests()),
            "low_value_count": len(self.get_low_value_tests()),
        }
    
    def get_dimensions_summary(self) -> Dict[str, float]:
        """
        Get average scores by dimension.
        
        Returns:
            Dictionary with average dimension scores
        """
        if not self._scores:
            return {}
        
        dimensions = {
            "coverage": [],
            "edge_cases": [],
            "mutation": [],
            "regression": [],
            "brittleness": [],
        }
        
        for score in self._scores:
            dimensions["coverage"].append(score.coverage_score)
            dimensions["edge_cases"].append(score.edge_case_score)
            dimensions["mutation"].append(score.mutation_score)
            dimensions["regression"].append(score.regression_score)
            dimensions["brittleness"].append(score.brittleness_score)
        
        return {
            dim: round(sum(scores) / len(scores), 3)
            for dim, scores in dimensions.items()
        }
    
    def reset(self) -> None:
        """Reset all scores."""
        self._scores.clear()
        self._metrics_cache.clear()


# Global scorer instance (singleton)
_scorer_instance: Optional[TestValueScorer] = None


def get_test_value_scorer() -> TestValueScorer:
    """
    Get global TestValueScorer instance.
    
    Returns:
        TestValueScorer singleton
    """
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = TestValueScorer()
    return _scorer_instance


__all__ = [
    "TestValueScorer",
    "TestScore",
    "TestMetrics",
    "ScoreTier",
    "get_test_value_scorer",
]
