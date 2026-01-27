"""
Strategy Selector - Recommends execution strategies based on metrics.

This module analyzes performance metrics and recommends optimal
execution strategies.
"""

from cortex.execution.adaptive_execution_engine import ExecutionStrategy
from cortex.execution.performance_metrics import PerformanceMetrics


class StrategySelector:
    """
    Selects optimal execution strategy based on performance metrics.
    
    Uses performance characteristics to recommend sequential, parallel,
    or async execution strategies.
    """

    def __init__(self) -> None:
        """Initialize the strategy selector."""
        self.default_strategy = ExecutionStrategy.SEQUENTIAL

    def recommend(self, metrics: PerformanceMetrics) -> ExecutionStrategy:
        """
        Recommend an execution strategy based on metrics.
        
        Args:
            metrics: PerformanceMetrics object with current performance data.
            
        Returns:
            ExecutionStrategy recommendation.
        """
        # High error rate -> Sequential (more reliable)
        if metrics.error_rate > 0.2:
            return ExecutionStrategy.SEQUENTIAL

        # Very low error rate -> Parallel (safe to parallelize)
        if metrics.error_rate < 0.05 and metrics.p95_latency > 5.0:
            return ExecutionStrategy.PARALLEL

        # Long operations -> Async (avoid blocking)
        if metrics.p50_latency > 8.0:
            return ExecutionStrategy.ASYNC

        # Moderate conditions -> Default
        if metrics.error_rate < 0.1 and metrics.p95_latency > 3.0:
            return ExecutionStrategy.PARALLEL

        return ExecutionStrategy.SEQUENTIAL

    def is_safe_to_parallelize(self, metrics: PerformanceMetrics) -> bool:
        """
        Check if it's safe to parallelize based on error rates.
        
        Args:
            metrics: Performance metrics to evaluate.
            
        Returns:
            True if parallelization is recommended, False otherwise.
        """
        return metrics.error_rate < 0.1 and metrics.success_percentage > 85.0

    def is_suitable_for_async(self, metrics: PerformanceMetrics) -> bool:
        """
        Check if async execution is suitable.
        
        Args:
            metrics: Performance metrics to evaluate.
            
        Returns:
            True if async is recommended, False otherwise.
        """
        return metrics.p50_latency > 5.0 and metrics.error_rate < 0.2
