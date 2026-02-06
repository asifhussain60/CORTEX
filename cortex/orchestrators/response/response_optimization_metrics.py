"""
Performance monitoring for response optimization pipeline.

Tracks metrics across optimization stages:
- Semantic deduplication
- Quality scoring
- Role profile application

Target: <50ms total overhead per response.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34 specification
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any
from collections import defaultdict


class OptimizationStage(Enum):
    """Optimization pipeline stages."""
    
    SEMANTIC_DEDUPLICATION = "SEMANTIC_DEDUPLICATION"
    QUALITY_SCORING = "QUALITY_SCORING"
    ROLE_PROFILE = "ROLE_PROFILE"


@dataclass
class OptimizationMetric:
    """
    Single optimization operation metric.
    
    Attributes:
        stage: Pipeline stage
        input_tokens: Token count before optimization
        output_tokens: Token count after optimization
        duration_ms: Processing time in milliseconds
    """
    
    stage: OptimizationStage
    input_tokens: int
    output_tokens: int
    duration_ms: float
    
    def calculate_reduction_pct(self) -> float:
        """
        Calculate token reduction percentage.
        
        Returns:
            Reduction percentage (0.0-100.0)
        """
        if self.input_tokens == 0:
            return 0.0
        reduction = self.input_tokens - self.output_tokens
        return (reduction / self.input_tokens) * 100.0


class ResponseOptimizationMetrics:
    """
    Tracks performance metrics for response optimization pipeline.
    
    Monitors:
    - Token reduction per stage
    - Processing duration per stage
    - End-to-end pipeline performance
    - Overhead vs benefit analysis
    
    Target: <50ms total overhead
    
    Example:
        >>> metrics = ResponseOptimizationMetrics()
        >>> metrics.record_optimization(
        ...     OptimizationStage.SEMANTIC_DEDUPLICATION,
        ...     input_tokens=1000,
        ...     output_tokens=850,
        ...     duration_ms=120.0
        ... )
        >>> stats = metrics.get_stage_stats(OptimizationStage.SEMANTIC_DEDUPLICATION)
    """
    
    def __init__(self):
        """Initialize metrics tracking."""
        self._metrics: Dict[OptimizationStage, List[OptimizationMetric]] = defaultdict(list)
    
    def record_optimization(
        self,
        stage: OptimizationStage,
        input_tokens: int,
        output_tokens: int,
        duration_ms: float
    ) -> None:
        """
        Record optimization operation.
        
        Args:
            stage: Pipeline stage
            input_tokens: Tokens before optimization
            output_tokens: Tokens after optimization
            duration_ms: Processing time
        """
        metric = OptimizationMetric(
            stage=stage,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms
        )
        self._metrics[stage].append(metric)
    
    def get_stage_stats(self, stage: OptimizationStage) -> Dict[str, Any]:
        """
        Get statistics for a specific stage.
        
        Args:
            stage: Pipeline stage
            
        Returns:
            Dictionary with:
            - total_operations: Number of operations
            - avg_reduction_pct: Average token reduction
            - avg_duration_ms: Average processing time
            - total_tokens_saved: Total tokens saved
        """
        metrics = self._metrics.get(stage, [])
        
        if not metrics:
            return {
                "total_operations": 0,
                "avg_reduction_pct": 0.0,
                "avg_duration_ms": 0.0,
                "total_tokens_saved": 0
            }
        
        # Calculate averages
        total_reduction_pct = sum(m.calculate_reduction_pct() for m in metrics)
        total_duration = sum(m.duration_ms for m in metrics)
        total_tokens_saved = sum(m.input_tokens - m.output_tokens for m in metrics)
        
        return {
            "total_operations": len(metrics),
            "avg_reduction_pct": total_reduction_pct / len(metrics),
            "avg_duration_ms": total_duration / len(metrics),
            "total_tokens_saved": total_tokens_saved
        }
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """
        Get summary of entire optimization pipeline.
        
        Returns:
            Dictionary with:
            - total_stages: Number of stages with metrics
            - overall_reduction_pct: End-to-end token reduction
            - total_duration_ms: Total processing time
            - stages: Per-stage breakdown
        """
        # Get all recorded metrics in order
        all_metrics: List[OptimizationMetric] = []
        for stage in OptimizationStage:
            all_metrics.extend(self._metrics.get(stage, []))
        
        if not all_metrics:
            return {
                "total_stages": 0,
                "overall_reduction_pct": 0.0,
                "total_duration_ms": 0.0,
                "stages": {}
            }
        
        # Calculate overall reduction (first input -> last output)
        # For simplicity, use first metric's input and last metric's output
        first_input = all_metrics[0].input_tokens
        last_output = all_metrics[-1].output_tokens
        
        if first_input > 0:
            overall_reduction = ((first_input - last_output) / first_input) * 100.0
        else:
            overall_reduction = 0.0
        
        # Total duration
        total_duration = sum(m.duration_ms for m in all_metrics)
        
        # Per-stage stats
        stage_stats = {}
        for stage in OptimizationStage:
            if self._metrics.get(stage):
                stage_stats[stage.value] = self.get_stage_stats(stage)
        
        return {
            "total_stages": len(stage_stats),
            "overall_reduction_pct": overall_reduction,
            "total_duration_ms": total_duration,
            "stages": stage_stats
        }
    
    def reset(self) -> None:
        """Reset all metrics."""
        self._metrics.clear()
    
    def get_overhead_analysis(self) -> Dict[str, Any]:
        """
        Analyze overhead vs benefit.
        
        Returns:
            Dictionary with:
            - avg_overhead_ms: Average processing time
            - avg_tokens_saved: Average tokens saved
            - efficiency_ratio: Tokens saved per ms
            - meets_target: Whether overhead < 50ms
        """
        summary = self.get_pipeline_summary()
        
        if summary["total_stages"] == 0:
            return {
                "avg_overhead_ms": 0.0,
                "avg_tokens_saved": 0,
                "efficiency_ratio": 0.0,
                "meets_target": True
            }
        
        avg_overhead = summary["total_duration_ms"]
        
        # Calculate average tokens saved across all stages
        total_saved = sum(
            stats["total_tokens_saved"]
            for stats in summary["stages"].values()
        )
        
        # Efficiency: tokens saved per millisecond
        efficiency = total_saved / avg_overhead if avg_overhead > 0 else 0.0
        
        return {
            "avg_overhead_ms": avg_overhead,
            "avg_tokens_saved": total_saved,
            "efficiency_ratio": efficiency,
            "meets_target": avg_overhead < 50.0
        }
