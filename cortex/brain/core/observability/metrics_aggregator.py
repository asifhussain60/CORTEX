"""
Metrics aggregation for CORTEX observability.

This module provides metrics collection, aggregation, and statistical computation
for dashboard display and historical analysis.

Attributes:
    DEFAULT_MAX_DATAPOINTS: Maximum historical datapoints to retain (10000)
    DEFAULT_PERCENTILE_BUCKETS: Number of buckets for percentile calculation (100)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
import statistics


@dataclass
class MetricPoint:
    """Single metric data point.
    
    Attributes:
        timestamp: When metric was recorded (seconds since epoch)
        operation: Operation name
        value: Metric value
        metric_type: Type of metric (latency, count, error, etc)
        tags: Additional metadata tags
    """
    timestamp: float
    operation: str
    value: float
    metric_type: str = "latency"
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary with metric data
        """
        return {
            "timestamp": self.timestamp,
            "operation": self.operation,
            "value": self.value,
            "type": self.metric_type,
            "tags": self.tags,
        }


class MetricsAggregator:
    """Aggregates metrics from spans and operations.
    
    Collects span metrics, computes statistics, and provides queryable
    historical data for dashboard and analysis.
    
    Attributes:
        datapoints: List of recorded metric points
        span_latencies: Dictionary of operation -> list of latencies
        error_counts: Dictionary of operation -> error count
        span_counts: Dictionary of operation -> span count
    """
    
    def __init__(self) -> None:
        """Initialize metrics aggregator."""
        self.datapoints: List[MetricPoint] = []
        self.span_latencies: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}
        self.span_counts: Dict[str, int] = {}
        self.total_spans: int = 0
        self.total_errors: int = 0

    def record_span(
        self,
        operation_name: str,
        latency_ms: float,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Record a completed span's metrics.
        
        Args:
            operation_name: Name of the operation
            latency_ms: Latency in milliseconds
            timestamp: When span completed (UTC now if omitted)
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        ts = timestamp.timestamp()
        
        # Record latency
        if operation_name not in self.span_latencies:
            self.span_latencies[operation_name] = []
        
        self.span_latencies[operation_name].append(latency_ms)
        
        # Update counts
        self.span_counts[operation_name] = self.span_counts.get(operation_name, 0) + 1
        self.total_spans += 1
        
        # Record datapoint
        point = MetricPoint(
            timestamp=ts,
            operation=operation_name,
            value=latency_ms,
            metric_type="latency",
        )
        self.datapoints.append(point)

    def record_error(
        self,
        operation_name: str,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Record an error occurrence.
        
        Args:
            operation_name: Name of the operation that errored
            timestamp: When error occurred (UTC now if omitted)
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        ts = timestamp.timestamp()
        
        # Update error counts
        self.error_counts[operation_name] = self.error_counts.get(operation_name, 0) + 1
        self.total_errors += 1
        
        # Record datapoint
        point = MetricPoint(
            timestamp=ts,
            operation=operation_name,
            value=1.0,
            metric_type="error",
        )
        self.datapoints.append(point)

    def get_latency_stats(self, operation_name: str) -> Dict[str, float]:
        """Get latency statistics for an operation.
        
        Args:
            operation_name: Name of operation
            
        Returns:
            Dictionary with min, max, avg, p50, p95, p99
        """
        latencies = self.span_latencies.get(operation_name, [])
        
        if not latencies:
            return {
                "min": 0.0,
                "max": 0.0,
                "avg": 0.0,
                "p50": 0.0,
                "p95": 0.0,
                "p99": 0.0,
                "count": 0,
            }
        
        sorted_latencies = sorted(latencies)
        count = len(sorted_latencies)
        
        return {
            "min": min(latencies),
            "max": max(latencies),
            "avg": statistics.mean(latencies),
            "p50": self._percentile(sorted_latencies, 50),
            "p95": self._percentile(sorted_latencies, 95),
            "p99": self._percentile(sorted_latencies, 99),
            "count": count,
        }

    def get_error_rate(self) -> float:
        """Get overall error rate as percentage.
        
        Returns:
            Error rate (0-100)
        """
        if self.total_spans == 0:
            return 0.0
        
        return (self.total_errors / self.total_spans) * 100.0

    def get_error_rate_by_operation(self, operation_name: str) -> float:
        """Get error rate for specific operation.
        
        Args:
            operation_name: Name of operation
            
        Returns:
            Error rate (0-100)
        """
        span_count = self.span_counts.get(operation_name, 0)
        error_count = self.error_counts.get(operation_name, 0)
        
        if span_count == 0:
            return 0.0
        
        return (error_count / span_count) * 100.0

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all aggregated metrics.
        
        Returns:
            Dictionary with all current metrics
        """
        # Collect stats for all operations
        operations_stats = {}
        for op_name in self.span_counts.keys():
            operations_stats[op_name] = {
                "latency": self.get_latency_stats(op_name),
                "error_rate": self.get_error_rate_by_operation(op_name),
                "span_count": self.span_counts.get(op_name, 0),
                "error_count": self.error_counts.get(op_name, 0),
            }
        
        return {
            "total_spans": self.total_spans,
            "total_errors": self.total_errors,
            "overall_error_rate": self.get_error_rate(),
            "operations": operations_stats,
        }

    @staticmethod
    def _percentile(sorted_data: List[float], percentile: int) -> float:
        """Calculate percentile value.
        
        Args:
            sorted_data: Sorted list of values
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value
        """
        if not sorted_data:
            return 0.0
        
        index = (percentile / 100.0) * (len(sorted_data) - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_data) - 1)
        
        if lower_index == upper_index:
            return sorted_data[lower_index]
        
        # Linear interpolation
        lower_value = sorted_data[lower_index]
        upper_value = sorted_data[upper_index]
        fraction = index - lower_index
        
        return lower_value + (upper_value - lower_value) * fraction

    def get_datapoints_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> List[MetricPoint]:
        """Get datapoints within time range.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of MetricPoint objects within range
        """
        start_ts = start_time.timestamp()
        end_ts = end_time.timestamp()
        
        return [
            point for point in self.datapoints
            if start_ts <= point.timestamp <= end_ts
        ]

    def get_datapoints_by_operation(self, operation_name: str) -> List[MetricPoint]:
        """Get all datapoints for an operation.
        
        Args:
            operation_name: Name of operation
            
        Returns:
            List of MetricPoint objects for operation
        """
        return [
            point for point in self.datapoints
            if point.operation == operation_name
        ]

    def clear_old_datapoints(self, max_age_hours: int = 24) -> None:
        """Remove old datapoints beyond retention policy.
        
        Args:
            max_age_hours: Maximum age in hours (default: 24)
        """
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        cutoff_ts = cutoff_time.timestamp()
        
        self.datapoints = [
            point for point in self.datapoints
            if point.timestamp > cutoff_ts
        ]

    def get_summary(self) -> Dict[str, Any]:
        """Get summary metrics for current state.
        
        Returns:
            Summary dictionary with key metrics
        """
        all_latencies = []
        for latencies in self.span_latencies.values():
            all_latencies.extend(latencies)
        
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "span_count": self.total_spans,
            "error_count": self.total_errors,
            "error_rate": self.get_error_rate(),
            "operation_count": len(self.span_counts),
        }
        
        if all_latencies:
            summary.update({
                "latency_min": min(all_latencies),
                "latency_max": max(all_latencies),
                "latency_avg": statistics.mean(all_latencies),
                "latency_p95": self._percentile(sorted(all_latencies), 95),
                "latency_p99": self._percentile(sorted(all_latencies), 99),
            })
        
        return summary
