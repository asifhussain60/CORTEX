"""
Performance Monitor - Track and Optimize Audit Logger Performance

Monitors:
- Log write latency
- Buffer utilization
- Compression ratios
- Disk I/O metrics
- Memory usage

Provides:
- Real-time performance metrics
- Anomaly detection
- Performance degradation alerts

Author: Asif Hussain
Created: 2026-01-05
"""

import time
import psutil
from typing import Dict, List, Optional, Deque
from dataclasses import dataclass, field
from collections import deque
from threading import Lock
import statistics


@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    
    # Latency metrics (milliseconds)
    avg_write_latency_ms: float = 0.0
    p50_write_latency_ms: float = 0.0
    p95_write_latency_ms: float = 0.0
    p99_write_latency_ms: float = 0.0
    max_write_latency_ms: float = 0.0
    
    # Throughput metrics
    writes_per_second: float = 0.0
    bytes_per_second: float = 0.0
    
    # Buffer metrics
    buffer_utilization_percent: float = 0.0
    buffer_overflows: int = 0
    
    # Compression metrics
    compression_ratio: float = 0.0
    compressed_bytes_saved: int = 0
    
    # Resource metrics
    memory_usage_mb: float = 0.0
    disk_usage_mb: float = 0.0
    cpu_percent: float = 0.0
    
    # Operational metrics
    total_log_entries: int = 0
    total_bytes_written: int = 0
    uptime_seconds: float = 0.0


@dataclass
class PerformanceSample:
    """Single performance measurement"""
    timestamp: float
    operation: str
    latency_ms: float
    bytes_processed: int = 0
    success: bool = True


class PerformanceMonitor:
    """
    Monitors and tracks audit logger performance metrics.
    
    Maintains a sliding window of performance samples and
    computes real-time statistics.
    """
    
    def __init__(self, window_size: int = 1000, alert_threshold_ms: float = 10.0):
        """
        Initialize the performance monitor.
        
        Args:
            window_size: Number of samples to keep in sliding window
            alert_threshold_ms: Latency threshold for alerts (milliseconds)
        """
        self.window_size = window_size
        self.alert_threshold_ms = alert_threshold_ms
        
        # Sliding window of samples
        self._samples: Deque[PerformanceSample] = deque(maxlen=window_size)
        self._lock = Lock()
        
        # Cumulative counters
        self._total_entries = 0
        self._total_bytes = 0
        self._buffer_overflows = 0
        self._start_time = time.time()
        
        # Alerts
        self._alerts: List[str] = []
    
    def record_operation(self, operation: str, start_time: float, 
                        bytes_processed: int = 0, success: bool = True):
        """
        Record a completed operation.
        
        Args:
            operation: Operation name (e.g., 'write', 'flush', 'compress')
            start_time: Operation start timestamp (from time.time())
            bytes_processed: Number of bytes processed
            success: Whether the operation succeeded
        """
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000  # Convert to milliseconds
        
        sample = PerformanceSample(
            timestamp=end_time,
            operation=operation,
            latency_ms=latency_ms,
            bytes_processed=bytes_processed,
            success=success
        )
        
        with self._lock:
            self._samples.append(sample)
            self._total_entries += 1
            self._total_bytes += bytes_processed
            
            # Check for performance alerts
            if latency_ms > self.alert_threshold_ms:
                alert = f"High latency detected: {operation} took {latency_ms:.2f}ms (threshold: {self.alert_threshold_ms}ms)"
                self._alerts.append(alert)
    
    def record_buffer_overflow(self):
        """Record a buffer overflow event"""
        with self._lock:
            self._buffer_overflows += 1
    
    def get_metrics(self) -> PerformanceMetrics:
        """
        Compute and return current performance metrics.
        
        Returns:
            PerformanceMetrics object with current statistics
        """
        with self._lock:
            if not self._samples:
                return PerformanceMetrics()
            
            # Extract latencies from samples
            latencies = [s.latency_ms for s in self._samples if s.success]
            
            if not latencies:
                return PerformanceMetrics()
            
            # Compute latency percentiles
            sorted_latencies = sorted(latencies)
            n = len(sorted_latencies)
            
            p50_idx = int(n * 0.50)
            p95_idx = int(n * 0.95)
            p99_idx = int(n * 0.99)
            
            # Compute time-based metrics
            uptime = time.time() - self._start_time
            writes_per_sec = self._total_entries / uptime if uptime > 0 else 0
            bytes_per_sec = self._total_bytes / uptime if uptime > 0 else 0
            
            # Get resource metrics
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            cpu_percent = process.cpu_percent(interval=0.1)
            
            return PerformanceMetrics(
                avg_write_latency_ms=statistics.mean(latencies),
                p50_write_latency_ms=sorted_latencies[p50_idx],
                p95_write_latency_ms=sorted_latencies[p95_idx],
                p99_write_latency_ms=sorted_latencies[p99_idx],
                max_write_latency_ms=max(latencies),
                writes_per_second=writes_per_sec,
                bytes_per_second=bytes_per_sec,
                buffer_overflows=self._buffer_overflows,
                memory_usage_mb=memory_mb,
                cpu_percent=cpu_percent,
                total_log_entries=self._total_entries,
                total_bytes_written=self._total_bytes,
                uptime_seconds=uptime
            )
    
    def get_recent_alerts(self, count: int = 10) -> List[str]:
        """
        Get the most recent performance alerts.
        
        Args:
            count: Maximum number of alerts to return
        
        Returns:
            List of alert messages
        """
        with self._lock:
            return self._alerts[-count:]
    
    def clear_alerts(self):
        """Clear all performance alerts"""
        with self._lock:
            self._alerts.clear()
    
    def reset_metrics(self):
        """Reset all performance metrics"""
        with self._lock:
            self._samples.clear()
            self._total_entries = 0
            self._total_bytes = 0
            self._buffer_overflows = 0
            self._start_time = time.time()
            self._alerts.clear()
    
    def get_performance_summary(self) -> Dict:
        """
        Get a human-readable performance summary.
        
        Returns:
            Dictionary with formatted performance data
        """
        metrics = self.get_metrics()
        
        return {
            'latency': {
                'average_ms': f"{metrics.avg_write_latency_ms:.2f}",
                'p50_ms': f"{metrics.p50_write_latency_ms:.2f}",
                'p95_ms': f"{metrics.p95_write_latency_ms:.2f}",
                'p99_ms': f"{metrics.p99_write_latency_ms:.2f}",
                'max_ms': f"{metrics.max_write_latency_ms:.2f}",
                'threshold_ms': f"{self.alert_threshold_ms}",
                'within_sla': metrics.p95_write_latency_ms < self.alert_threshold_ms
            },
            'throughput': {
                'writes_per_second': f"{metrics.writes_per_second:.2f}",
                'bytes_per_second': f"{metrics.bytes_per_second:.2f}",
                'total_entries': metrics.total_log_entries,
                'total_bytes': metrics.total_bytes_written
            },
            'resources': {
                'memory_mb': f"{metrics.memory_usage_mb:.2f}",
                'cpu_percent': f"{metrics.cpu_percent:.2f}",
                'uptime_seconds': f"{metrics.uptime_seconds:.2f}"
            },
            'issues': {
                'buffer_overflows': metrics.buffer_overflows,
                'recent_alerts': self.get_recent_alerts(5)
            }
        }


class PerformanceOptimizer:
    """
    Automatically adjusts audit logger settings based on performance metrics.
    
    Features:
    - Dynamic buffer sizing
    - Adaptive flush intervals
    - Compression policy tuning
    """
    
    def __init__(self, monitor: PerformanceMonitor):
        """
        Initialize the performance optimizer.
        
        Args:
            monitor: PerformanceMonitor instance to watch
        """
        self.monitor = monitor
        
        # Tunable parameters
        self.min_buffer_size = 100
        self.max_buffer_size = 10000
        self.min_flush_interval = 1.0  # seconds
        self.max_flush_interval = 30.0  # seconds
    
    def suggest_buffer_size(self, current_size: int) -> int:
        """
        Suggest an optimal buffer size based on current metrics.
        
        Args:
            current_size: Current buffer size
        
        Returns:
            Suggested buffer size
        """
        metrics = self.monitor.get_metrics()
        
        # If we're seeing buffer overflows, increase size
        if metrics.buffer_overflows > 0:
            suggested = min(int(current_size * 1.5), self.max_buffer_size)
            return suggested
        
        # If utilization is very low and latency is good, can reduce size
        if metrics.buffer_utilization_percent < 20 and metrics.p95_write_latency_ms < 5.0:
            suggested = max(int(current_size * 0.75), self.min_buffer_size)
            return suggested
        
        # Otherwise, keep current size
        return current_size
    
    def suggest_flush_interval(self, current_interval: float) -> float:
        """
        Suggest an optimal flush interval based on current metrics.
        
        Args:
            current_interval: Current flush interval (seconds)
        
        Returns:
            Suggested flush interval (seconds)
        """
        metrics = self.monitor.get_metrics()
        
        # If latency is high, reduce flush interval (flush more often)
        if metrics.p95_write_latency_ms > 10.0:
            suggested = max(current_interval * 0.75, self.min_flush_interval)
            return suggested
        
        # If latency is low and throughput is low, can increase interval
        if metrics.p95_write_latency_ms < 2.0 and metrics.writes_per_second < 10:
            suggested = min(current_interval * 1.25, self.max_flush_interval)
            return suggested
        
        # Otherwise, keep current interval
        return current_interval


# Global singleton instance
_monitor_instance = None


def get_performance_monitor() -> PerformanceMonitor:
    """
    Get the global PerformanceMonitor instance (singleton pattern).
    
    Returns:
        PerformanceMonitor instance
    """
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = PerformanceMonitor()
    return _monitor_instance
