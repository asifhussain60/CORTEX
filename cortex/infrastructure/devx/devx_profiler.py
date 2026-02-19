"""DevX Profiler for performance measurement."""

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class ProfileResult:
    """Profile result for an operation."""

    operation: str
    execution_time_ms: float = 0.0
    memory_used_mb: float = 0.0
    timestamp: str = ""
    measurements: List[Dict[str, Any]] = field(default_factory=lambda: [])

    def __post_init__(self) -> None:
        """Initialize timestamp."""
        self.timestamp = datetime.now(timezone.utc).isoformat()


class DevxProfiler:
    """Performance profiling tools."""

    def __init__(self) -> None:
        """Initialize profiler."""
        self.results: Dict[str, ProfileResult] = {}
        self.active_measurements: Dict[str, float] = {}

    @contextmanager
    def measure(self, operation: str) -> Any:
        """Context manager for measuring execution time.

        Args:
            operation: Operation name

        Yields:
            Measurement context
        """
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # Convert to ms
            self.active_measurements[operation] = execution_time

            if operation not in self.results:
                self.results[operation] = ProfileResult(operation=operation)

            self.results[operation].execution_time_ms = execution_time
            self.results[operation].measurements.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "execution_time_ms": execution_time
            })

    def get_results(self) -> Dict[str, ProfileResult]:
        """Get profiling results.

        Returns:
            Dictionary of results
        """
        return self.results

    def get_profile_result(self, operation: str) -> ProfileResult:
        """Get profile result for operation.

        Args:
            operation: Operation name

        Returns:
            ProfileResult
        """
        if operation not in self.results:
            self.results[operation] = ProfileResult(operation=operation)
        return self.results[operation]

    def find_bottlenecks(self, threshold_ms: float = 100.0) -> List[str]:
        """Find operations exceeding threshold.

        Args:
            threshold_ms: Threshold in milliseconds

        Returns:
            List of bottleneck operations
        """
        bottlenecks: List[str] = []
        for operation, result in self.results.items():
            if result.execution_time_ms > threshold_ms:
                bottlenecks.append(str(operation))
        return bottlenecks

    def generate_report(self) -> str:
        """Generate profiling report.

        Returns:
            Report string
        """
        total_time = sum(r.execution_time_ms for r in self.results.values())
        avg_time = total_time / len(self.results) if self.results else 0.0

        report_dict: Dict[str, Any] = {
            "total_operations": len(self.results),
            "total_time_ms": total_time,
            "average_time_ms": avg_time,
            "slowest_operation": max(
                self.results.items(),
                key=lambda x: x[1].execution_time_ms,
                default=(None, ProfileResult(operation=""))
            )[0],
            "results": {
                op: {
                    "execution_time_ms": result.execution_time_ms,
                    "measurements_count": len(result.measurements)
                }
                for op, result in self.results.items()
            }
        }
        return str(report_dict)
