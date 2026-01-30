"""Tests for CAP-005: Consensus Builder.

Test-driven implementation of multi-model consensus estimation.
Aggregates PERT, Story Points, and CPM estimates into weighted consensus.

Acceptance Criteria:
- AC-CAP-005-AC01: Three models aggregated with weights (40% PERT, 40% SP, 20% CPM)
- AC-CAP-005-AC02: 80% confidence interval calculated from consensus
- AC-CAP-005-AC03: High-variance detection (>30% spread) triggers warning
- AC-CAP-005-AC04: Model agreement percentage calculated
- AC-CAP-005-AC05: Risk factors identified from estimate variance

Author: Asif Hussain
Date: 2026-01-30
Phase: 17 (Track C: Capacity Planning)
"""

import pytest
from cortex.capacity.multi_model_estimation_engine import (
    MultiModelEstimationEngine,
    EstimationResult,
    SkillLevel,
)


class TestConsensusBuilding:
    """Test consensus building from 3 estimation models.
    
    AC-CAP-005-AC01: Three models aggregated with weights
    """

    def test_consensus_with_close_agreement(self):
        """Test consensus when 3 models agree closely.
        
        PERT: 58h, Story Points: 60h, CPM: 52h
        Weights: 40% PERT, 40% SP, 20% CPM
        Expected: 0.4*58 + 0.4*60 + 0.2*52 = 23.2 + 24 + 10.4 = 57.6h
        """
        engine = MultiModelEstimationEngine()
        
        result = engine.build_consensus(
            pert_hours=58.0,
            story_point_hours=60.0,
            cpm_hours=52.0
        )
        
        assert abs(result.recommended_hours - 57.6) < 0.1, \
            f"Expected ~57.6h consensus, got {result.recommended_hours}h"
        
        # Verify individual estimates stored
        assert result.pert_hours == 58.0
        assert result.story_points == 0  # Not converted yet
        assert result.cpm_hours == 52.0

    def test_consensus_with_identical_estimates(self):
        """Test consensus when all 3 models agree exactly.
        
        PERT: 50h, SP: 50h, CPM: 50h → Consensus: 50h
        """
        engine = MultiModelEstimationEngine()
        
        result = engine.build_consensus(
            pert_hours=50.0,
            story_point_hours=50.0,
            cpm_hours=50.0
        )
        
        assert result.recommended_hours == 50.0
        assert result.model_agreement == 100.0, \
            "Perfect agreement should be 100%"

    def test_consensus_weights_applied_correctly(self):
        """Test that weights are applied correctly: 40-40-20.
        
        PERT: 100h, SP: 50h, CPM: 0h
        Expected: 0.4*100 + 0.4*50 + 0.2*0 = 40 + 20 + 0 = 60h
        """
        engine = MultiModelEstimationEngine()
        
        result = engine.build_consensus(
            pert_hours=100.0,
            story_point_hours=50.0,
            cpm_hours=0.0
        )
        
        assert result.recommended_hours == 60.0


class TestConfidenceIntervals:
    """Test 80% confidence interval calculation.
    
    AC-CAP-005-AC02: 80% confidence intervals from consensus
    """

    def test_confidence_interval_with_variance(self):
        """Test confidence interval calculation with moderate variance.
        
        PERT: 58h, SP: 60h, CPM: 52h
        Consensus: 57.6h
        Spread: ±20% typical for moderate agreement
        """
        engine = MultiModelEstimationEngine()
        
        result = engine.build_consensus(
            pert_hours=58.0,
            story_point_hours=60.0,
            cpm_hours=52.0
        )
        
        # CI should be calculated (specific values depend on variance formula)
        assert result.confidence_interval_low > 0
        assert result.confidence_interval_high > result.confidence_interval_low
        assert result.confidence_interval_low < result.recommended_hours < result.confidence_interval_high

    def test_confidence_interval_with_perfect_agreement(self):
        """Test narrow CI when models agree perfectly.
        
        Perfect agreement → narrow confidence interval
        """
        engine = MultiModelEstimationEngine()
        
        result = engine.build_consensus(
            pert_hours=50.0,
            story_point_hours=50.0,
            cpm_hours=50.0
        )
        
        # CI should be very narrow (all models agree)
        ci_width = result.confidence_interval_high - result.confidence_interval_low
        assert ci_width < 10.0, f"Expected narrow CI with perfect agreement, got width {ci_width}h"


class TestHighVarianceDetection:
    """Test high-variance estimate detection.
    
    AC-CAP-005-AC03: High-variance detection (>30% spread)
    """

    def test_high_variance_flagged_with_large_spread(self):
        """Test that large spread between models triggers warning.
        
        PERT: 40h, SP: 80h, CPM: 50h
        Spread: (80-40)/avg ≈ 67% → HIGH VARIANCE
        """
        engine = MultiModelEstimationEngine()
        
        result = engine.build_consensus(
            pert_hours=40.0,
            story_point_hours=80.0,
            cpm_hours=50.0
        )
        
        # High variance should be flagged in risk factors
        assert len(result.risk_factors) > 0, "Expected risk factors for high variance"
        assert any("variance" in risk.lower() or "spread" in risk.lower() 
                   for risk in result.risk_factors), \
            "Expected 'variance' or 'spread' in risk factors"

    def test_low_variance_no_warning(self):
        """Test that close estimates don't trigger variance warning.
        
        PERT: 55h, SP: 58h, CPM: 56h
        Spread: ~5% → LOW VARIANCE
        """
        engine = MultiModelEstimationEngine()
        
        result = engine.build_consensus(
            pert_hours=55.0,
            story_point_hours=58.0,
            cpm_hours=56.0
        )
        
        # Should have few/no risk factors
        variance_risks = [r for r in result.risk_factors 
                         if "variance" in r.lower() or "spread" in r.lower()]
        assert len(variance_risks) == 0, \
            f"Expected no variance warnings, got: {variance_risks}"


class TestModelAgreement:
    """Test model agreement percentage calculation.
    
    AC-CAP-005-AC04: Model agreement percentage
    """

    def test_model_agreement_perfect(self):
        """Test 100% agreement when models match exactly."""
        engine = MultiModelEstimationEngine()
        
        result = engine.build_consensus(
            pert_hours=50.0,
            story_point_hours=50.0,
            cpm_hours=50.0
        )
        
        assert result.model_agreement == 100.0

    def test_model_agreement_partial(self):
        """Test partial agreement calculation.
        
        PERT: 60h, SP: 60h (agree), CPM: 40h (disagrees)
        Agreement calculation based on coefficient of variation
        """
        engine = MultiModelEstimationEngine()
        
        result = engine.build_consensus(
            pert_hours=60.0,
            story_point_hours=60.0,
            cpm_hours=40.0
        )
        
        # Agreement should be decent (2 out of 3 models close)
        # CV = std_dev / mean * 100, Agreement = 100 - CV
        assert 70.0 <= result.model_agreement <= 90.0, \
            f"Expected 70-90% agreement for partial consensus, got {result.model_agreement}%"

    def test_model_agreement_low(self):
        """Test low agreement when all models differ significantly."""
        engine = MultiModelEstimationEngine()
        
        result = engine.build_consensus(
            pert_hours=30.0,
            story_point_hours=60.0,
            cpm_hours=90.0
        )
        
        # Agreement should be moderate-low with large spread
        # Even with 100% spread, CV formula gives ~59% agreement
        assert result.model_agreement < 70.0, \
            f"Expected <70% agreement with large differences, got {result.model_agreement}%"
        
        # Should definitely have high variance risk factor
        assert len(result.risk_factors) > 0


class TestRiskFactorIdentification:
    """Test risk factor identification from estimate variance.
    
    AC-CAP-005-AC05: Risk factors from variance
    """

    def test_risk_factors_include_high_uncertainty(self):
        """Test that high uncertainty is flagged as risk factor."""
        engine = MultiModelEstimationEngine()
        
        result = engine.build_consensus(
            pert_hours=20.0,
            story_point_hours=80.0,
            cpm_hours=50.0
        )
        
        assert len(result.risk_factors) > 0
        # Should mention uncertainty, variance, or disagreement
        risk_keywords = ["uncertainty", "variance", "spread", "disagreement", "high"]
        assert any(any(keyword in risk.lower() for keyword in risk_keywords) 
                   for risk in result.risk_factors)

    def test_risk_factors_empty_with_low_variance(self):
        """Test minimal risk factors when variance is low."""
        engine = MultiModelEstimationEngine()
        
        result = engine.build_consensus(
            pert_hours=55.0,
            story_point_hours=57.0,
            cpm_hours=56.0
        )
        
        # Should have minimal risk factors
        assert len(result.risk_factors) <= 1, \
            f"Expected ≤1 risk factors with low variance, got {len(result.risk_factors)}"


class TestConsensusEdgeCases:
    """Test edge cases for consensus building."""

    def test_consensus_with_zero_estimates(self):
        """Test consensus when all estimates are zero."""
        engine = MultiModelEstimationEngine()
        
        result = engine.build_consensus(
            pert_hours=0.0,
            story_point_hours=0.0,
            cpm_hours=0.0
        )
        
        assert result.recommended_hours == 0.0

    def test_consensus_with_single_dominant_model(self):
        """Test when one model is much higher than others.
        
        PERT: 10h, SP: 10h, CPM: 100h
        Weighted: 0.4*10 + 0.4*10 + 0.2*100 = 4 + 4 + 20 = 28h
        """
        engine = MultiModelEstimationEngine()
        
        result = engine.build_consensus(
            pert_hours=10.0,
            story_point_hours=10.0,
            cpm_hours=100.0
        )
        
        # CPM's 20% weight should still influence result
        assert result.recommended_hours == 28.0
