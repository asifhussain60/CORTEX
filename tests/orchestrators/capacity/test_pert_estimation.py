"""Tests for CAP-002: PERT Estimation.

Test-driven implementation of PERT (Program Evaluation and Review Technique) estimation.
Formula: Expected = (Optimistic + 4*MostLikely + Pessimistic) / 6

Acceptance Criteria:
- AC-CAP-002-AC01: PERT formula calculates expected hours correctly
- AC-CAP-002-AC02: Standard deviation calculated from 3-point estimate
- AC-CAP-002-AC03: 80% confidence intervals generated
- AC-CAP-002-AC04: Invalid inputs raise ValueError

Author: Asif Hussain
Date: 2026-01-30
Phase: 17 (Track C: Capacity Planning)
"""

import pytest
from cortex.capacity.multi_model_estimation_engine import (
    PERTEstimator,
    EstimationResult,
)


class TestPERTFormula:
    """Test PERT 3-point estimation formula.
    
    AC-CAP-002-AC01: PERT formula calculates expected hours correctly
    """

    def test_pert_formula_basic(self):
        """Test PERT formula with simple inputs.
        
        Formula: (O + 4*ML + P) / 6
        Example: (8 + 4*12 + 20) / 6 = 76/6 = 12.67
        """
        optimistic = 8.0
        likely = 12.0
        pessimistic = 20.0
        
        expected, std_dev = PERTEstimator.estimate(optimistic, likely, pessimistic)
        
        # Expected hours: (8 + 4*12 + 20) / 6 = 12.67
        assert abs(expected - 12.67) < 0.01, f"Expected ~12.67, got {expected}"
        
        # Standard deviation: (20 - 8) / 6 = 2.0
        assert abs(std_dev - 2.0) < 0.01, f"Expected std_dev ~2.0, got {std_dev}"

    def test_pert_formula_identical_values(self):
        """Test PERT when all 3 values are identical (no uncertainty).
        
        AC-CAP-002-AC01: Edge case - zero variance
        """
        value = 10.0
        
        expected, std_dev = PERTEstimator.estimate(value, value, value)
        
        assert expected == value, f"Expected {value}, got {expected}"
        assert std_dev == 0.0, f"Expected std_dev 0.0, got {std_dev}"

    def test_pert_formula_large_spread(self):
        """Test PERT with large uncertainty spread.
        
        AC-CAP-002-AC01: Wide range case
        """
        optimistic = 5.0
        likely = 15.0
        pessimistic = 50.0
        
        expected, std_dev = PERTEstimator.estimate(optimistic, likely, pessimistic)
        
        # Expected: (5 + 4*15 + 50) / 6 = 115/6 = 19.17
        assert abs(expected - 19.17) < 0.01
        
        # Std dev: (50 - 5) / 6 = 7.5
        assert abs(std_dev - 7.5) < 0.01


class TestPERTValidation:
    """Test PERT input validation.
    
    AC-CAP-002-AC04: Invalid inputs raise ValueError
    """

    def test_pert_rejects_optimistic_greater_than_likely(self):
        """Test PERT rejects optimistic > likely."""
        with pytest.raises(ValueError, match="optimistic <= likely <= pessimistic"):
            PERTEstimator.estimate(
                optimistic=15.0,
                likely=10.0,  # Lower than optimistic!
                pessimistic=20.0
            )

    def test_pert_rejects_likely_greater_than_pessimistic(self):
        """Test PERT rejects likely > pessimistic."""
        with pytest.raises(ValueError, match="optimistic <= likely <= pessimistic"):
            PERTEstimator.estimate(
                optimistic=5.0,
                likely=25.0,  # Higher than pessimistic!
                pessimistic=20.0
            )

    def test_pert_rejects_negative_values(self):
        """Test PERT rejects negative hours."""
        with pytest.raises(ValueError):
            PERTEstimator.estimate(
                optimistic=-5.0,
                likely=10.0,
                pessimistic=20.0
            )


class TestPERTConfidenceIntervals:
    """Test 80% confidence interval calculation.
    
    AC-CAP-002-AC03: 80% confidence intervals generated
    """

    def test_confidence_interval_80_percent(self):
        """Test 80% confidence interval calculation.
        
        For 80% confidence, z-score ≈ 1.28
        CI = Expected ± 1.28 * StdDev
        """
        expected = 12.67
        std_dev = 2.0
        
        low, high = PERTEstimator.get_confidence_interval(expected, std_dev, confidence=0.80)
        
        # CI_80% = 12.67 ± 1.28*2.0 = 12.67 ± 2.56
        # Low: 10.11, High: 15.23
        assert abs(low - 10.11) < 0.01, f"Expected low ~10.11, got {low}"
        assert abs(high - 15.23) < 0.01, f"Expected high ~15.23, got {high}"

    def test_confidence_interval_zero_variance(self):
        """Test confidence interval with zero variance (certainty).
        
        AC-CAP-002-AC03: Edge case - zero uncertainty
        """
        expected = 10.0
        std_dev = 0.0
        
        low, high = PERTEstimator.get_confidence_interval(expected, std_dev, confidence=0.80)
        
        assert low == expected, f"Expected low {expected}, got {low}"
        assert high == expected, f"Expected high {expected}, got {high}"

    def test_confidence_interval_95_percent(self):
        """Test 95% confidence interval (wider than 80%).
        
        For 95% confidence, z-score ≈ 1.96
        """
        expected = 12.67
        std_dev = 2.0
        
        low, high = PERTEstimator.get_confidence_interval(expected, std_dev, confidence=0.95)
        
        # CI_95% = 12.67 ± 1.96*2.0 = 12.67 ± 3.92
        # Low: 8.75, High: 16.59
        assert abs(low - 8.75) < 0.01
        assert abs(high - 16.59) < 0.01


class TestPERTStandardDeviation:
    """Test standard deviation calculation.
    
    AC-CAP-002-AC02: Standard deviation calculated from 3-point estimate
    """

    def test_standard_deviation_calculation(self):
        """Test standard deviation formula: (P - O) / 6."""
        optimistic = 10.0
        pessimistic = 40.0
        likely = 25.0
        
        _, std_dev = PERTEstimator.estimate(optimistic, likely, pessimistic)
        
        # Std dev: (40 - 10) / 6 = 5.0
        assert abs(std_dev - 5.0) < 0.01

    def test_standard_deviation_reflects_uncertainty(self):
        """Test that wider spread produces larger std dev."""
        # Narrow spread
        _, std_dev_narrow = PERTEstimator.estimate(10.0, 12.0, 14.0)
        
        # Wide spread
        _, std_dev_wide = PERTEstimator.estimate(10.0, 15.0, 30.0)
        
        assert std_dev_wide > std_dev_narrow, \
            "Wider spread should produce larger standard deviation"
