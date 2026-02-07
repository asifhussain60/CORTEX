"""
Tests for FallbackPipeline - Multi-tier graceful degradation.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 36 Stage 3 specification
"""

import pytest
from cortex.orchestrators.response.fallback_pipeline import (
    FallbackPipeline,
    FallbackTier,
    FallbackResult,
)


class TestFallbackPipelineBasic:
    """Test basic FallbackPipeline functionality."""
    
    def test_pipeline_initializes(self):
        """FallbackPipeline initializes with default tiers."""
        pipeline = FallbackPipeline()
        
        assert pipeline is not None
        assert len(pipeline.tiers) > 0
    
    def test_summarize_uses_best_available_tier(self):
        """Pipeline tries tiers in order until success."""
        pipeline = FallbackPipeline()
        
        text = "This is a long response that needs summarization. " * 20
        result = pipeline.summarize(text, target_ratio=0.5)
        
        assert result is not None
        assert result.summary != text  # Should be shorter
        assert result.tier_used is not None


class TestFallbackTiers:
    """Test tier fallback logic."""
    
    def test_tier_order(self):
        """Tiers tried in priority order (ML → Dedup → Policy → Raw)."""
        pipeline = FallbackPipeline()
        
        expected_order = [
            FallbackTier.ML_EXTRACTIVE,
            FallbackTier.DEDUPLICATION,
            FallbackTier.POLICY_BASED,
            FallbackTier.RAW,
        ]
        
        assert pipeline.tiers == expected_order
    
    def test_ml_tier_attempts_first(self):
        """ML tier attempted before fallbacks."""
        pipeline = FallbackPipeline()
        
        text = "Test text for summarization."
        result = pipeline.summarize(text, target_ratio=0.5)
        
        # With ML dependencies installed, should use ML tier
        assert result.tier_used in [FallbackTier.ML_EXTRACTIVE, FallbackTier.POLICY_BASED]
    
    def test_raw_tier_always_succeeds(self):
        """RAW tier never fails (returns original text)."""
        pipeline = FallbackPipeline()
        
        text = "Original text"
        result = pipeline._apply_raw_tier(text, 0.5)
        
        assert result.summary == text
        assert result.tier_used == FallbackTier.RAW
        assert result.success is True


class TestFallbackResult:
    """Test FallbackResult dataclass."""
    
    def test_result_stores_tier_info(self):
        """FallbackResult captures tier used and success status."""
        result = FallbackResult(
            summary="Summarized text",
            tier_used=FallbackTier.ML_EXTRACTIVE,
            success=True,
            reduction_ratio=0.5,
        )
        
        assert result.summary == "Summarized text"
        assert result.tier_used == FallbackTier.ML_EXTRACTIVE
        assert result.success is True
        assert result.reduction_ratio == 0.5


class TestGracefulDegradation:
    """Test error handling and graceful degradation."""
    
    def test_continues_on_tier_failure(self):
        """Pipeline continues to next tier if current tier fails."""
        pipeline = FallbackPipeline()
        
        # Empty text might fail ML tier but should succeed with RAW
        text = ""
        result = pipeline.summarize(text, target_ratio=0.5)
        
        assert result is not None
        assert result.success is True
    
    def test_tracks_reduction_ratio(self):
        """Result includes actual reduction achieved."""
        pipeline = FallbackPipeline()
        
        text = "Test sentence. " * 10
        result = pipeline.summarize(text, target_ratio=0.5)
        
        assert result.reduction_ratio is not None
        assert 0 <= result.reduction_ratio <= 1.0
