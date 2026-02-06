"""
Unit tests for response optimization metrics.

Tests performance monitoring for response optimization pipeline:
- SemanticDeduplicator metrics
- ResponseQualityScorer metrics
- RoleVerbosityProfiles metrics
- End-to-end optimization tracking

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34 specification
"""

import pytest
from typing import Dict, Any

from cortex.orchestrators.response.response_optimization_metrics import (
    ResponseOptimizationMetrics,
    OptimizationStage,
    OptimizationMetric,
)


class TestResponseOptimizationMetrics:
    """Test response optimization metrics tracking."""
    
    @pytest.fixture
    def metrics(self) -> ResponseOptimizationMetrics:
        """Create metrics instance."""
        return ResponseOptimizationMetrics()
    
    def test_record_deduplication(self, metrics):
        """Test recording deduplication metrics."""
        metrics.record_optimization(
            stage=OptimizationStage.SEMANTIC_DEDUPLICATION,
            input_tokens=1000,
            output_tokens=850,
            duration_ms=120.5
        )
        
        stats = metrics.get_stage_stats(OptimizationStage.SEMANTIC_DEDUPLICATION)
        
        assert stats["total_operations"] == 1
        assert stats["avg_reduction_pct"] == pytest.approx(15.0, abs=0.1)
        assert stats["avg_duration_ms"] == pytest.approx(120.5, abs=0.1)
    
    def test_record_quality_scoring(self, metrics):
        """Test recording quality scoring metrics."""
        metrics.record_optimization(
            stage=OptimizationStage.QUALITY_SCORING,
            input_tokens=850,
            output_tokens=850,  # No reduction
            duration_ms=45.2
        )
        
        stats = metrics.get_stage_stats(OptimizationStage.QUALITY_SCORING)
        
        assert stats["total_operations"] == 1
        assert stats["avg_reduction_pct"] == 0.0
        assert stats["avg_duration_ms"] == pytest.approx(45.2, abs=0.1)
    
    def test_record_role_profile(self, metrics):
        """Test recording role profile application."""
        metrics.record_optimization(
            stage=OptimizationStage.ROLE_PROFILE,
            input_tokens=850,
            output_tokens=510,  # 40% reduction
            duration_ms=30.8
        )
        
        stats = metrics.get_stage_stats(OptimizationStage.ROLE_PROFILE)
        
        assert stats["total_operations"] == 1
        assert stats["avg_reduction_pct"] == pytest.approx(40.0, abs=0.1)
    
    def test_end_to_end_pipeline(self, metrics):
        """Test full optimization pipeline tracking."""
        # Stage 1: Deduplication
        metrics.record_optimization(
            OptimizationStage.SEMANTIC_DEDUPLICATION,
            input_tokens=1000,
            output_tokens=850,
            duration_ms=120.0
        )
        
        # Stage 2: Quality scoring (no reduction)
        metrics.record_optimization(
            OptimizationStage.QUALITY_SCORING,
            input_tokens=850,
            output_tokens=850,
            duration_ms=45.0
        )
        
        # Stage 3: Role profile
        metrics.record_optimization(
            OptimizationStage.ROLE_PROFILE,
            input_tokens=850,
            output_tokens=510,
            duration_ms=30.0
        )
        
        summary = metrics.get_pipeline_summary()
        
        assert summary["total_stages"] == 3
        assert summary["overall_reduction_pct"] == pytest.approx(49.0, abs=0.1)
        assert summary["total_duration_ms"] == pytest.approx(195.0, abs=0.1)
    
    def test_overhead_within_target(self, metrics):
        """Test that overhead stays under 50ms target."""
        # Simulate typical optimization
        metrics.record_optimization(
            OptimizationStage.SEMANTIC_DEDUPLICATION,
            input_tokens=500,
            output_tokens=450,
            duration_ms=20.0
        )
        
        metrics.record_optimization(
            OptimizationStage.QUALITY_SCORING,
            input_tokens=450,
            output_tokens=450,
            duration_ms=15.0
        )
        
        metrics.record_optimization(
            OptimizationStage.ROLE_PROFILE,
            input_tokens=450,
            output_tokens=400,
            duration_ms=10.0
        )
        
        summary = metrics.get_pipeline_summary()
        
        # Total should be under 50ms
        assert summary["total_duration_ms"] < 50.0
    
    def test_multiple_operations_averaging(self, metrics):
        """Test averaging across multiple operations."""
        # Record 3 operations
        for _ in range(3):
            metrics.record_optimization(
                OptimizationStage.SEMANTIC_DEDUPLICATION,
                input_tokens=1000,
                output_tokens=850,
                duration_ms=100.0
            )
        
        stats = metrics.get_stage_stats(OptimizationStage.SEMANTIC_DEDUPLICATION)
        
        assert stats["total_operations"] == 3
        assert stats["avg_reduction_pct"] == pytest.approx(15.0, abs=0.1)
        assert stats["avg_duration_ms"] == pytest.approx(100.0, abs=0.1)
    
    def test_zero_operations_stats(self, metrics):
        """Test stats when no operations recorded."""
        stats = metrics.get_stage_stats(OptimizationStage.SEMANTIC_DEDUPLICATION)
        
        assert stats["total_operations"] == 0
        assert stats["avg_reduction_pct"] == 0.0
        assert stats["avg_duration_ms"] == 0.0


class TestOptimizationStage:
    """Test OptimizationStage enum."""
    
    def test_all_stages_defined(self):
        """Test that all 3 stages are defined."""
        stages = list(OptimizationStage)
        assert len(stages) == 3
        assert OptimizationStage.SEMANTIC_DEDUPLICATION in stages
        assert OptimizationStage.QUALITY_SCORING in stages
        assert OptimizationStage.ROLE_PROFILE in stages


class TestOptimizationMetric:
    """Test OptimizationMetric dataclass."""
    
    def test_metric_creation(self):
        """Test OptimizationMetric instantiation."""
        metric = OptimizationMetric(
            stage=OptimizationStage.SEMANTIC_DEDUPLICATION,
            input_tokens=1000,
            output_tokens=850,
            duration_ms=120.5
        )
        
        assert metric.stage == OptimizationStage.SEMANTIC_DEDUPLICATION
        assert metric.input_tokens == 1000
        assert metric.output_tokens == 850
        assert metric.duration_ms == pytest.approx(120.5, abs=0.1)
    
    def test_metric_reduction_calculation(self):
        """Test reduction percentage calculation."""
        metric = OptimizationMetric(
            stage=OptimizationStage.SEMANTIC_DEDUPLICATION,
            input_tokens=1000,
            output_tokens=750,
            duration_ms=100.0
        )
        
        reduction = metric.calculate_reduction_pct()
        assert reduction == pytest.approx(25.0, abs=0.1)
