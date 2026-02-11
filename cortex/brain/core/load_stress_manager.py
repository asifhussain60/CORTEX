"""
AC-REM-011-07: Load and Stress Testing Manager

Manages load and stress testing validation, throughput monitoring,
latency percentile tracking, and resource stability checks.

CORE-008: Implementation follows TDD principles.
CORE-011: All functions have type hints.
CORE-012: All methods have Google-style docstrings.
"""

import statistics
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Dict, List, Optional, Tuple

import psutil


@dataclass
class LoadTestMetrics:
    """Metrics from a load test execution."""

    total_operations: int = 0
    failed_operations: int = 0
    total_duration_sec: float = 0.0
    latencies_ms: List[float] = field(default_factory=list)
    throughput_ops_sec: float = 0.0
    p50_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    p999_latency_ms: float = 0.0
    memory_used_mb: float = 0.0
    cpu_percent: float = 0.0
    timestamp: float = field(default_factory=time.time)


class LoadStressManager:
    """Manages load and stress testing validation."""

    _instance: Optional['LoadStressManager'] = None
    _lock: RLock = RLock()

    def __init__(self) -> None:
        """Initialize LoadStressManager."""
        self._metrics_history: deque = deque(maxlen=100)
        self._latency_samples: deque = deque(maxlen=10000)
        self._error_count: int = 0
        self._operation_count: int = 0
        self._last_reset: float = time.time()
        self._baseline_memory_mb: float = 0.0
        self._baseline_cpu_percent: float = 0.0
        self._queue_depth: int = 0
        self._cache_hits: int = 0
        self._cache_misses: int = 0

    @classmethod
    def instance(cls) -> 'LoadStressManager':
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def record_operation(self, duration_ms: float, success: bool) -> None:
        """
        Record an operation for load testing metrics.

        Args:
            duration_ms: Operation duration in milliseconds
            success: Whether operation succeeded
        """
        with self._lock:
            self._operation_count += 1
            if not success:
                self._error_count += 1
            self._latency_samples.append(duration_ms)

    def get_throughput_ops_sec(self) -> float:
        """
        Get current throughput in operations per second.

        Returns:
            Throughput in ops/sec
        """
        with self._lock:
            elapsed = time.time() - self._last_reset
            if elapsed <= 0:
                return 0.0
            return self._operation_count / elapsed

    def get_latency_percentile(self, percentile: float) -> float:
        """
        Get latency at specified percentile.

        Args:
            percentile: Percentile (50, 99, 99.9)

        Returns:
            Latency in milliseconds
        """
        with self._lock:
            if not self._latency_samples:
                return 0.0

            sorted_latencies = sorted(list(self._latency_samples))
            index = int(len(sorted_latencies) * (percentile / 100.0))
            index = max(0, min(index, len(sorted_latencies) - 1))

            return float(sorted_latencies[index])

    def get_error_rate(self) -> float:
        """
        Get current error rate as percentage.

        Returns:
            Error rate (0-100%)
        """
        with self._lock:
            if self._operation_count == 0:
                return 0.0
            return (self._error_count / self._operation_count) * 100.0

    def get_resource_metrics(self) -> Dict[str, float]:
        """
        Get current resource usage metrics.

        Returns:
            Dict with memory_mb, cpu_percent
        """
        with self._lock:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent(interval=0.1)

            metrics = {
                "memory_mb": memory_mb,
                "cpu_percent": cpu_percent
            }

            # io_counters not available on all platforms (e.g., macOS)
            try:
                io_counters = process.io_counters()
                metrics["disk_io_reads"] = io_counters.read_count
                metrics["disk_io_writes"] = io_counters.write_count
            except (AttributeError, OSError):
                metrics["disk_io_reads"] = 0
                metrics["disk_io_writes"] = 0

            return metrics

    def set_baseline_resources(self) -> None:
        """Set current resource usage as baseline for comparison."""
        with self._lock:
            metrics = self.get_resource_metrics()
            self._baseline_memory_mb = metrics["memory_mb"]
            self._baseline_cpu_percent = metrics["cpu_percent"]

    def check_memory_stability(self, threshold_percent: float = 20.0) -> Tuple[bool, str]:
        """
        Check if memory usage is stable (no leaks).

        Args:
            threshold_percent: Acceptable increase from baseline

        Returns:
            Tuple of (is_stable, message)
        """
        with self._lock:
            metrics = self.get_resource_metrics()
            current = metrics["memory_mb"]

            if self._baseline_memory_mb == 0:
                return True, "Baseline not set"

            percent_increase = ((current - self._baseline_memory_mb) /
                               self._baseline_memory_mb * 100.0)

            if percent_increase > threshold_percent:
                return False, f"Memory increased {percent_increase:.1f}%"

            return True, f"Memory stable at {current:.1f}MB"

    def check_cpu_stability(self, threshold_percent: float = 20.0) -> Tuple[bool, str]:
        """
        Check if CPU usage is stable (no spikes).

        Args:
            threshold_percent: Acceptable increase from baseline

        Returns:
            Tuple of (is_stable, message)
        """
        with self._lock:
            metrics = self.get_resource_metrics()
            current = metrics["cpu_percent"]

            if self._baseline_cpu_percent == 0:
                return True, "Baseline not set"

            percent_increase = ((current - self._baseline_cpu_percent) /
                               self._baseline_cpu_percent * 100.0) if self._baseline_cpu_percent > 0 else 0

            if percent_increase > threshold_percent:
                return False, f"CPU spiked {percent_increase:.1f}%"

            return True, f"CPU stable at {current:.1f}%"

    def queue_push(self) -> None:
        """Simulate push to request queue."""
        with self._lock:
            self._queue_depth += 1

    def queue_pop(self) -> None:
        """Simulate pop from request queue."""
        with self._lock:
            if self._queue_depth > 0:
                self._queue_depth -= 1

    def get_queue_depth(self) -> int:
        """
        Get current request queue depth.

        Returns:
            Queue depth
        """
        with self._lock:
            return self._queue_depth

    def record_cache_hit(self) -> None:
        """Record cache hit."""
        with self._lock:
            self._cache_hits += 1

    def record_cache_miss(self) -> None:
        """Record cache miss."""
        with self._lock:
            self._cache_misses += 1

    def get_cache_hit_rate(self) -> float:
        """
        Get cache hit rate as percentage.

        Returns:
            Hit rate (0-100%)
        """
        with self._lock:
            total = self._cache_hits + self._cache_misses
            if total == 0:
                return 0.0
            return (self._cache_hits / total) * 100.0

    def simulate_burst_load(self, num_operations: int) -> List[float]:
        """
        Simulate burst load of concurrent operations.

        Args:
            num_operations: Number of operations to simulate

        Returns:
            List of operation durations in ms
        """
        durations = []

        with ThreadPoolExecutor(max_workers=min(num_operations, 100)) as executor:
            futures = []

            for _ in range(num_operations):
                future = executor.submit(self._simulate_operation)
                futures.append(future)

            for future in futures:
                try:
                    duration = future.result(timeout=10)
                    durations.append(duration)
                except Exception:
                    durations.append(0.0)

        return durations

    def _simulate_operation(self) -> float:
        """
        Simulate a single operation.

        Returns:
            Operation duration in ms
        """
        start = time.time()

        # Simulate work
        time.sleep(0.001)  # 1ms base latency

        # Simulate potential jitter
        import random
        if random.random() < 0.1:  # 10% chance of higher latency
            time.sleep(random.uniform(0.001, 0.01))

        duration_ms = (time.time() - start) * 1000
        return duration_ms

    def graceful_degrade_check(self) -> Tuple[bool, str]:
        """
        Check if system should gracefully degrade.

        Returns:
            Tuple of (should_degrade, reason)
        """
        with self._lock:
            # Check memory pressure
            metrics = self.get_resource_metrics()
            if metrics["memory_mb"] > 1000:  # Over 1GB
                return True, "Memory pressure detected"

            # Check CPU
            if metrics["cpu_percent"] > 90:
                return True, "CPU over 90%"

            # Check error rate
            if self.get_error_rate() > 5.0:  # Over 5% errors
                return True, "Error rate elevated"

            return False, "System healthy"

    def get_metrics_snapshot(self) -> LoadTestMetrics:
        """
        Get snapshot of current metrics.

        Returns:
            LoadTestMetrics snapshot
        """
        with self._lock:
            metrics = self.get_resource_metrics()

            return LoadTestMetrics(
                total_operations=self._operation_count,
                failed_operations=self._error_count,
                total_duration_sec=time.time() - self._last_reset,
                latencies_ms=list(self._latency_samples),
                throughput_ops_sec=self.get_throughput_ops_sec(),
                p50_latency_ms=self.get_latency_percentile(50),
                p99_latency_ms=self.get_latency_percentile(99),
                p999_latency_ms=self.get_latency_percentile(99.9),
                memory_used_mb=metrics["memory_mb"],
                cpu_percent=metrics["cpu_percent"]
            )

    def reset_metrics(self) -> None:
        """Reset all metrics for fresh test run."""
        with self._lock:
            self._operation_count = 0
            self._error_count = 0
            self._latency_samples.clear()
            self._last_reset = time.time()
            self._cache_hits = 0
            self._cache_misses = 0


def get_load_stress_manager() -> LoadStressManager:
    """
    Get LoadStressManager singleton.

    Returns:
        LoadStressManager instance
    """
    return LoadStressManager.instance()
