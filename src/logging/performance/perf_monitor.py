"""
Performance Monitor - Latency and Throughput Tracking.

Features:
- Latency tracking with percentiles (p50, p95, p99)
- Throughput monitoring (ops/sec)
- Resource monitoring (CPU, memory)
- Performance alerts and degradation detection
- Comprehensive reporting
- Benchmarking against targets
"""

import asyncio
import json
import psutil
import statistics
import time
from contextlib import contextmanager, asynccontextmanager
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable


class PerformanceAlert(Exception):
    """Raised when performance degradation is detected."""
    pass


class LatencyTracker:
    """
    Track operation latencies with percentile calculations.
    """
    
    def __init__(self):
        """Initialize latency tracker."""
        self._latencies: List[float] = []
    
    def record(self, latency_ms: float):
        """Record a latency measurement in milliseconds."""
        self._latencies.append(latency_ms)
    
    def count(self) -> int:
        """Get total number of measurements."""
        return len(self._latencies)
    
    def mean(self) -> float:
        """Calculate mean latency."""
        if not self._latencies:
            return 0
        return statistics.mean(self._latencies)
    
    def min(self) -> Optional[float]:
        """Get minimum latency."""
        if not self._latencies:
            return None
        return min(self._latencies)
    
    def max(self) -> Optional[float]:
        """Get maximum latency."""
        if not self._latencies:
            return None
        return max(self._latencies)
    
    def percentile(self, p: int) -> float:
        """
        Calculate percentile.
        
        Args:
            p: Percentile to calculate (0-100)
            
        Returns:
            Percentile value
        """
        if not self._latencies:
            return 0
        
        sorted_latencies = sorted(self._latencies)
        index = int((p / 100) * len(sorted_latencies))
        
        if index >= len(sorted_latencies):
            index = len(sorted_latencies) - 1
        
        return sorted_latencies[index]
    
    def reset(self):
        """Reset all measurements."""
        self._latencies.clear()


class ThroughputMonitor:
    """
    Monitor operation throughput (operations per second).
    """
    
    def __init__(self):
        """Initialize throughput monitor."""
        self._count = 0
        self._timestamped_counts: List[tuple] = []
    
    def increment(self, count: int = 1):
        """Increment operation count."""
        self._count += count
    
    def increment_with_timestamp(self, count: int = 1, timestamp: datetime = None):
        """Increment with timestamp for windowed calculations."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        self._timestamped_counts.append((timestamp, count))
    
    def count(self) -> int:
        """Get total operation count."""
        return self._count
    
    def rate(self, elapsed_seconds: float) -> float:
        """
        Calculate operations per second.
        
        Args:
            elapsed_seconds: Time period in seconds
            
        Returns:
            Operations per second
        """
        if elapsed_seconds == 0:
            return 0
        return self._count / elapsed_seconds
    
    def windowed_rate(self, window_seconds: int = 60) -> float:
        """
        Calculate rate over recent time window.
        
        Args:
            window_seconds: Time window in seconds
            
        Returns:
            Operations per second in window
        """
        cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
        recent_counts = [
            count for timestamp, count in self._timestamped_counts
            if timestamp >= cutoff
        ]
        
        if not recent_counts:
            return 0
        
        return sum(recent_counts) / window_seconds
    
    def reset(self):
        """Reset throughput counters."""
        self._count = 0
        self._timestamped_counts.clear()


class ResourceMonitor:
    """
    Monitor system resource usage (CPU, memory).
    """
    
    def __init__(self):
        """Initialize resource monitor."""
        self._history: List[Dict[str, Any]] = []
        self._process = psutil.Process()
    
    def cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return self._process.cpu_percent()
    
    def memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self._process.memory_info().rss / 1024 / 1024
    
    def memory_percent(self) -> float:
        """Get current memory usage as percentage."""
        return self._process.memory_percent()
    
    def snapshot(self) -> Dict[str, Any]:
        """Capture complete resource snapshot."""
        return {
            "cpu_percent": self.cpu_usage(),
            "memory_mb": self.memory_usage(),
            "memory_percent": self.memory_percent(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def record_snapshot(self):
        """Record resource snapshot to history."""
        self._history.append(self.snapshot())
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get resource usage history."""
        return self._history
    
    def reset(self):
        """Reset resource history."""
        self._history.clear()


class PerformanceMonitor:
    """
    Integrated performance monitoring with latency, throughput, and resources.
    """
    
    def __init__(self):
        """Initialize performance monitor."""
        self.latency = LatencyTracker()
        self.throughput = ThroughputMonitor()
        self.resources = ResourceMonitor()
        
        # Per-operation tracking
        self._operations: Dict[str, LatencyTracker] = {}
        self._thresholds: Dict[str, Dict[str, float]] = {}
        self._alerts: List[Dict[str, Any]] = []
    
    def _get_operation_tracker(self, operation: str) -> LatencyTracker:
        """Get or create tracker for operation."""
        if operation not in self._operations:
            self._operations[operation] = LatencyTracker()
        return self._operations[operation]
    
    @contextmanager
    def measure(self, operation: str):
        """
        Context manager to measure operation latency.
        
        Args:
            operation: Name of operation being measured
            
        Example:
            with monitor.measure("database_query"):
                # operation code
                pass
        """
        start = time.time()
        try:
            yield
        finally:
            elapsed_ms = (time.time() - start) * 1000
            tracker = self._get_operation_tracker(operation)
            tracker.record(elapsed_ms)
            self.throughput.increment()
            self._check_thresholds(operation, elapsed_ms)
    
    @asynccontextmanager
    async def measure_async(self, operation: str):
        """
        Async context manager to measure operation latency.
        
        Args:
            operation: Name of operation being measured
        """
        start = time.time()
        try:
            yield
        finally:
            elapsed_ms = (time.time() - start) * 1000
            tracker = self._get_operation_tracker(operation)
            tracker.record(elapsed_ms)
            self.throughput.increment()
            self._check_thresholds(operation, elapsed_ms)
    
    def track(self, operation: str) -> Callable:
        """
        Decorator to track function performance.
        
        Args:
            operation: Name of operation
            
        Example:
            @monitor.track("process_data")
            def process_data():
                pass
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.measure(operation):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def get_stats(self, operation: str) -> Dict[str, Any]:
        """
        Get statistics for operation.
        
        Args:
            operation: Operation name
            
        Returns:
            Dictionary with latency statistics
        """
        if operation not in self._operations:
            return {
                "count": 0,
                "mean": 0,
                "min": None,
                "max": None,
                "p50": 0,
                "p95": 0,
                "p99": 0
            }
        
        tracker = self._operations[operation]
        return {
            "count": tracker.count(),
            "mean": tracker.mean(),
            "min": tracker.min(),
            "max": tracker.max(),
            "p50": tracker.percentile(50),
            "p95": tracker.percentile(95),
            "p99": tracker.percentile(99)
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all operations."""
        return {
            operation: self.get_stats(operation)
            for operation in self._operations.keys()
        }
    
    def set_threshold(self, operation: str, **thresholds):
        """
        Set performance thresholds for operation.
        
        Args:
            operation: Operation name
            **thresholds: Threshold values (max_latency, min_throughput, etc.)
        """
        self._thresholds[operation] = thresholds
    
    def _check_thresholds(self, operation: str, latency_ms: float):
        """Check if operation exceeded thresholds."""
        if operation not in self._thresholds:
            return
        
        thresholds = self._thresholds[operation]
        
        if "max_latency" in thresholds:
            if latency_ms > thresholds["max_latency"]:
                self._alerts.append({
                    "type": "high_latency",
                    "operation": operation,
                    "latency_ms": latency_ms,
                    "threshold": thresholds["max_latency"],
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # Check throughput threshold
        if "min_throughput" in thresholds:
            tracker = self._operations[operation]
            if tracker.count() >= 10:  # Need enough samples
                # Calculate actual throughput (ops/sec)
                # Rough estimate based on mean latency
                mean_latency_sec = tracker.mean() / 1000
                estimated_throughput = 1 / mean_latency_sec if mean_latency_sec > 0 else 0
                
                if estimated_throughput < thresholds["min_throughput"]:
                    self._alerts.append({
                        "type": "low_throughput",
                        "operation": operation,
                        "throughput": estimated_throughput,
                        "threshold": thresholds["min_throughput"],
                        "timestamp": datetime.utcnow().isoformat()
                    })
    
    def check_resources(self):
        """Check resource usage against thresholds."""
        if "resources" not in self._thresholds:
            return
        
        thresholds = self._thresholds["resources"]
        snapshot = self.resources.snapshot()
        
        if "max_memory_percent" in thresholds:
            if snapshot["memory_percent"] > thresholds["max_memory_percent"]:
                self._alerts.append({
                    "type": "high_memory",
                    "memory_percent": snapshot["memory_percent"],
                    "threshold": thresholds["max_memory_percent"],
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get all performance alerts."""
        return self._alerts
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Returns:
            Report dictionary
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_operations": sum(
                    t.count() for t in self._operations.values()
                ),
                "tracked_operations": len(self._operations),
                "alerts": len(self._alerts)
            },
            "operations": self.get_all_stats(),
            "resources": self.resources.snapshot(),
            "alerts": self._alerts
        }
    
    def export_report(self, file_path: Path, format: str = "json"):
        """
        Export report to file.
        
        Args:
            file_path: Output file path
            format: Export format (json, etc.)
        """
        report = self.generate_report()
        
        if format == "json":
            Path(file_path).write_text(json.dumps(report, indent=2))
    
    def benchmark_against(self, targets: Dict[str, float]) -> Dict[str, Any]:
        """
        Benchmark operations against target latencies.
        
        Args:
            targets: Dictionary mapping operation names to target latencies (ms)
            
        Returns:
            Benchmark results
        """
        results = {}
        
        for operation, target in targets.items():
            stats = self.get_stats(operation)
            results[operation] = {
                "target": target,
                "actual_mean": stats["mean"],
                "meets_target": stats["mean"] <= target if stats["count"] > 0 else None,
                "p95": stats["p95"],
                "p99": stats["p99"]
            }
        
        return results
    
    def reset(self):
        """Reset all performance statistics."""
        self._operations.clear()
        self._alerts.clear()
        self.latency.reset()
        self.throughput.reset()
        self.resources.reset()
