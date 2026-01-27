"""
Performance Metrics Collector - Tracks execution performance metrics.

This module provides performance metric collection and computation for
latency, error rates, and success metrics.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot."""
    p50_latency: float
    p95_latency: float
    p99_latency: float
    error_rate: float
    success_rate: float
    success_percentage: float
    total_operations: int


class PerformanceMetricsCollector:
    """
    Collects and aggregates performance metrics.
    
    Tracks latency percentiles, error rates, and success metrics
    for analysis and optimization.
    """

    def __init__(self) -> None:
        """Initialize the performance metrics collector."""
        self.metrics_history: List[PerformanceMetrics] = []
        self.latencies: List[float] = []
        self.successes: int = 0
        self.errors: int = 0

    def record_latency(self, latency: float) -> None:
        """
        Record a latency measurement.
        
        Args:
            latency: Latency value in seconds.
        """
        self.latencies.append(latency)

    def record_success(self) -> None:
        """Record a successful operation."""
        self.successes += 1

    def record_error(self) -> None:
        """Record a failed operation."""
        self.errors += 1

    def compute_metrics(self) -> PerformanceMetrics:
        """
        Compute current performance metrics.
        
        Returns:
            PerformanceMetrics object with current values.
        """
        if not self.latencies:
            p50 = p95 = p99 = 0.0
        else:
            sorted_latencies = sorted(self.latencies)
            n = len(sorted_latencies)
            p50 = sorted_latencies[int(n * 0.50)]
            p95 = sorted_latencies[int(n * 0.95)]
            p99 = sorted_latencies[int(n * 0.99)]

        total_ops = self.successes + self.errors
        success_rate = self.successes / total_ops if total_ops > 0 else 0.0
        error_rate = self.errors / total_ops if total_ops > 0 else 0.0
        success_percentage = success_rate * 100.0

        metrics = PerformanceMetrics(
            p50_latency=p50,
            p95_latency=p95,
            p99_latency=p99,
            error_rate=error_rate,
            success_rate=success_rate,
            success_percentage=success_percentage,
            total_operations=total_ops,
        )
        
        self.metrics_history.append(metrics)
        return metrics

    def reset(self) -> None:
        """Reset all metrics."""
        self.latencies.clear()
        self.successes = 0
        self.errors = 0
        self.metrics_history.clear()
