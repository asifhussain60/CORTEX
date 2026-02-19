"""
Performance Profiling & Optimization Module (OB-002-02).

This module provides performance analysis, bottleneck detection, and
optimization recommendations for CORTEX runtime operations.

Key Components:
- BottleneckDetector: Identifies high-latency and high-error operations
- PerformanceProfiler: Tracks baseline and current performance metrics
- Optimization engine: Generates actionable recommendations
"""

import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class BottleneckType(str, Enum):
    """Types of performance bottlenecks."""

    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"


from cortex.models.canonical_enums import SeverityLevel


class ComplexityLevel(str, Enum):
    """Implementation complexity levels."""

    SIMPLE = "SIMPLE"
    MEDIUM = "MEDIUM"
    COMPLEX = "COMPLEX"


@dataclass
class Bottleneck:
    """
    Represents a detected performance bottleneck.

    Attributes:
        operation: Name of the operation
        bottleneck_type: Type of bottleneck (latency, error_rate, etc)
        severity: Severity level of the bottleneck
        current_value: Current metric value
        threshold_value: Threshold that was breached
        affected_spans: Number of spans affected
    """

    operation: str
    bottleneck_type: str
    severity: str
    current_value: float
    threshold_value: float
    affected_spans: int


@dataclass
class OptimizationRecommendation:
    """
    Represents an optimization recommendation.

    Attributes:
        bottleneck_id: ID of the bottleneck being addressed
        strategy: Optimization strategy (e.g., caching, batching)
        description: Human-readable description
        estimated_improvement_pct: Estimated improvement percentage
        implementation_complexity: Complexity level
        estimated_effort_hours: Estimated effort in hours
    """

    bottleneck_id: str
    strategy: str
    description: str
    estimated_improvement_pct: float
    implementation_complexity: str
    estimated_effort_hours: float


@dataclass
class PerformanceSnapshot:
    """
    Represents a snapshot of performance metrics at a point in time.

    Attributes:
        timestamp: When the snapshot was taken
        metrics: Dictionary of operation metrics
    """

    timestamp: datetime
    metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)


class BottleneckDetector:
    """
    Detects performance bottlenecks in runtime metrics.

    This detector identifies operations that exceed latency or error rate
    thresholds and generates optimization recommendations.
    """

    def __init__(
        self,
        latency_threshold_ms: float = 1000.0,
        error_rate_threshold_pct: float = 5.0,
        throughput_threshold_ops_per_sec: float = 100.0,
    ) -> None:
        """
        Initialize the bottleneck detector.

        Args:
            latency_threshold_ms: Latency threshold in milliseconds
            error_rate_threshold_pct: Error rate threshold as percentage
            throughput_threshold_ops_per_sec: Throughput threshold in ops/sec
        """
        self.latency_threshold_ms = latency_threshold_ms
        self.error_rate_threshold_pct = error_rate_threshold_pct
        self.throughput_threshold_ops_per_sec = throughput_threshold_ops_per_sec
        self._bottleneck_history: List[Bottleneck] = []

    def detect(self, metrics: Dict[str, Dict[str, float]]) -> List[Bottleneck]:
        """
        Detect bottlenecks in the provided metrics.

        Analyzes latency, error rate, and throughput metrics to identify
        operations exceeding configured thresholds.

        Args:
            metrics: Dictionary mapping operation names to metric dictionaries

        Returns:
            List of detected bottlenecks, sorted by severity
        """
        bottlenecks: List[Bottleneck] = []

        for operation, operation_metrics in metrics.items():
            # Check latency threshold
            if "latency_avg" in operation_metrics:
                latency = operation_metrics["latency_avg"]
                if latency > self.latency_threshold_ms:
                    severity = self._calculate_severity_latency(latency)
                    bottlenecks.append(
                        Bottleneck(
                            operation=operation,
                            bottleneck_type=BottleneckType.LATENCY.value,
                            severity=severity,
                            current_value=latency,
                            threshold_value=self.latency_threshold_ms,
                            affected_spans=int(
                                operation_metrics.get("span_count", 0)
                            ),
                        )
                    )

            # Check error rate threshold
            if "error_rate" in operation_metrics:
                error_rate = operation_metrics["error_rate"]
                if error_rate > self.error_rate_threshold_pct:
                    severity = self._calculate_severity_error_rate(error_rate)
                    bottlenecks.append(
                        Bottleneck(
                            operation=operation,
                            bottleneck_type=BottleneckType.ERROR_RATE.value,
                            severity=severity,
                            current_value=error_rate,
                            threshold_value=self.error_rate_threshold_pct,
                            affected_spans=int(
                                operation_metrics.get("total_count", 0)
                            ),
                        )
                    )

        # Store history
        self._bottleneck_history.extend(bottlenecks)

        return self._prioritize_bottlenecks(bottlenecks)

    def _calculate_severity_latency(self, latency: float) -> str:
        """
        Calculate severity based on latency breach magnitude.

        Args:
            latency: Current latency value in milliseconds

        Returns:
            Severity level string
        """
        breach_ratio = latency / self.latency_threshold_ms

        if breach_ratio > 10:
            return SeverityLevel.CRITICAL.value
        elif breach_ratio > 5:
            return SeverityLevel.HIGH.value
        elif breach_ratio > 2:
            return SeverityLevel.MEDIUM.value
        else:
            return SeverityLevel.LOW.value

    def _calculate_severity_error_rate(self, error_rate: float) -> str:
        """
        Calculate severity based on error rate breach magnitude.

        Args:
            error_rate: Error rate as percentage

        Returns:
            Severity level string
        """
        breach_ratio = error_rate / self.error_rate_threshold_pct

        if breach_ratio > 20:
            return SeverityLevel.CRITICAL.value
        elif breach_ratio > 10:
            return SeverityLevel.HIGH.value
        elif breach_ratio > 3:
            return SeverityLevel.MEDIUM.value
        else:
            return SeverityLevel.LOW.value

    def _prioritize_bottlenecks(
        self, bottlenecks: List[Bottleneck]
    ) -> List[Bottleneck]:
        """
        Sort bottlenecks by priority (severity and impact).

        Args:
            bottlenecks: List of detected bottlenecks

        Returns:
            Sorted bottleneck list with critical issues first
        """
        severity_order = {
            SeverityLevel.CRITICAL.value: 0,
            SeverityLevel.HIGH.value: 1,
            SeverityLevel.MEDIUM.value: 2,
            SeverityLevel.LOW.value: 3,
        }

        return sorted(
            bottlenecks,
            key=lambda b: (
                severity_order.get(b.severity, 99),
                -b.affected_spans,
            ),
        )

    def generate_recommendations(
        self, bottlenecks: List[Bottleneck]
    ) -> List[OptimizationRecommendation]:
        """
        Generate optimization recommendations for bottlenecks.

        Args:
            bottlenecks: List of bottlenecks to address

        Returns:
            List of recommendations sorted by impact
        """
        recommendations: List[OptimizationRecommendation] = []

        for idx, bottleneck in enumerate(bottlenecks):
            if bottleneck.bottleneck_type == BottleneckType.LATENCY.value:
                # Determine strategy based on latency magnitude
                if bottleneck.current_value > 5000:
                    strategy = "async_processing"
                    description = "Convert to async/background processing"
                    improvement = 50.0
                    complexity = ComplexityLevel.MEDIUM.value
                    effort = 8.0
                elif bottleneck.current_value > 2000:
                    strategy = "add_caching"
                    description = "Implement caching layer for frequent operations"
                    improvement = 40.0
                    complexity = ComplexityLevel.MEDIUM.value
                    effort = 4.0
                elif bottleneck.current_value > 1000:
                    strategy = "optimize_queries"
                    description = "Optimize database queries and indexes"
                    improvement = 30.0
                    complexity = ComplexityLevel.MEDIUM.value
                    effort = 6.0
                else:
                    strategy = "profile_identify"
                    description = "Profile to identify specific bottleneck"
                    improvement = 20.0
                    complexity = ComplexityLevel.SIMPLE.value
                    effort = 2.0

            elif (
                bottleneck.bottleneck_type == BottleneckType.ERROR_RATE.value
            ):
                if bottleneck.current_value > 20:
                    strategy = "circuit_breaker"
                    description = "Implement circuit breaker pattern"
                    improvement = 60.0
                    complexity = ComplexityLevel.MEDIUM.value
                    effort = 6.0
                elif bottleneck.current_value > 10:
                    strategy = "retry_backoff"
                    description = "Implement retry with exponential backoff"
                    improvement = 40.0
                    complexity = ComplexityLevel.SIMPLE.value
                    effort = 3.0
                else:
                    strategy = "error_logging"
                    description = "Enhance error logging and monitoring"
                    improvement = 15.0
                    complexity = ComplexityLevel.SIMPLE.value
                    effort = 2.0
            else:
                continue

            recommendation = OptimizationRecommendation(
                bottleneck_id=f"bottleneck_{idx}",
                strategy=strategy,
                description=description,
                estimated_improvement_pct=improvement,
                implementation_complexity=complexity,
                estimated_effort_hours=effort,
            )
            recommendations.append(recommendation)

        return sorted(
            recommendations,
            key=lambda r: -r.estimated_improvement_pct,
        )

    def get_history(self) -> List[Bottleneck]:
        """
        Get historical bottleneck detections.

        Returns:
            List of all detected bottlenecks
        """
        return self._bottleneck_history.copy()

    def clear_history(self) -> None:
        """Clear bottleneck history."""
        self._bottleneck_history.clear()


class PerformanceProfiler:
    """
    Tracks and analyzes performance metrics over time.

    This profiler maintains baselines, detects regressions and improvements,
    and generates performance comparison reports.
    """

    def __init__(self) -> None:
        """Initialize the performance profiler."""
        self._baseline: Optional[PerformanceSnapshot] = None
        self._snapshots: List[PerformanceSnapshot] = []
        self._detector = BottleneckDetector()

    def record_baseline(self, metrics: Dict[str, Dict[str, float]]) -> None:
        """
        Record baseline performance metrics.

        Args:
            metrics: Dictionary of operation metrics to use as baseline
        """
        self._baseline = PerformanceSnapshot(
            timestamp=datetime.now(),
            metrics=metrics.copy(),
        )

    def get_baseline(self) -> Optional[PerformanceSnapshot]:
        """
        Get the current baseline snapshot.

        Returns:
            Baseline snapshot or None if not set
        """
        return self._baseline

    def record_snapshot(self, metrics: Dict[str, Dict[str, float]]) -> None:
        """
        Record a performance snapshot.

        Args:
            metrics: Current performance metrics
        """
        snapshot = PerformanceSnapshot(
            timestamp=datetime.now(),
            metrics=metrics.copy(),
        )
        self._snapshots.append(snapshot)

    def detect_regression(
        self, current_metrics: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Detect performance regression compared to baseline.

        Args:
            current_metrics: Current performance metrics

        Returns:
            Dictionary mapping operations to regression percentages
        """
        if not self._baseline:
            return {}

        regressions = {}

        for operation, current in current_metrics.items():
            if operation not in self._baseline.metrics:
                continue

            baseline = self._baseline.metrics[operation]

            if "latency_avg" in current and "latency_avg" in baseline:
                baseline_latency = baseline["latency_avg"]
                current_latency = current["latency_avg"]

                if current_latency > baseline_latency:
                    regression_pct = (
                        (current_latency - baseline_latency)
                        / baseline_latency
                        * 100
                    )
                    regressions[operation] = regression_pct

        return regressions

    def detect_improvement(
        self, current_metrics: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Detect performance improvement compared to baseline.

        Args:
            current_metrics: Current performance metrics

        Returns:
            Dictionary mapping operations to improvement percentages
        """
        if not self._baseline:
            return {}

        improvements = {}

        for operation, current in current_metrics.items():
            if operation not in self._baseline.metrics:
                continue

            baseline = self._baseline.metrics[operation]

            if "latency_avg" in current and "latency_avg" in baseline:
                baseline_latency = baseline["latency_avg"]
                current_latency = current["latency_avg"]

                if current_latency < baseline_latency:
                    improvement_pct = (
                        (baseline_latency - current_latency)
                        / baseline_latency
                        * 100
                    )
                    improvements[operation] = improvement_pct

        return improvements

    def generate_comparison(
        self, current_metrics: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Generate performance comparison between baseline and current.

        Args:
            current_metrics: Current performance metrics

        Returns:
            Comparison dictionary with changes and anomalies
        """
        if not self._baseline:
            return {}

        comparison = {
            "timestamp": datetime.now().isoformat(),
            "baseline_timestamp": self._baseline.timestamp.isoformat(),
            "regressions": self.detect_regression(current_metrics),
            "improvements": self.detect_improvement(current_metrics),
            "operations": {},
        }

        # Detailed operation comparison
        for operation in set(
            list(self._baseline.metrics.keys())
            + list(current_metrics.keys())
        ):
            operation_data = {
                "baseline": self._baseline.metrics.get(operation, {}),
                "current": current_metrics.get(operation, {}),
            }
            comparison["operations"][operation] = operation_data

        return comparison

    def generate_comparison_report(
        self, current_metrics: Dict[str, Dict[str, float]]
    ) -> str:
        """
        Generate a formatted performance comparison report.

        Args:
            current_metrics: Current performance metrics

        Returns:
            Formatted report string
        """
        if not self._baseline:
            return "No baseline recorded"

        lines = [
            "Performance Comparison Report",
            "=" * 80,
            "",
            f"Baseline: {self._baseline.timestamp.isoformat()}",
            f"Current:  {datetime.now().isoformat()}",
            "",
        ]

        regressions = self.detect_regression(current_metrics)
        improvements = self.detect_improvement(current_metrics)

        if regressions:
            lines.append("Performance Regressions:")
            lines.append("-" * 40)
            for op, pct in sorted(
                regressions.items(), key=lambda x: -x[1]
            ):
                lines.append(f"  {op}: {pct:+.1f}%")
            lines.append("")

        if improvements:
            lines.append("Performance Improvements:")
            lines.append("-" * 40)
            for op, pct in sorted(
                improvements.items(), key=lambda x: -x[1]
            ):
                lines.append(f"  {op}: {pct:+.1f}%")
            lines.append("")

        # Identify anomalies (changes > 50%)
        anomalies = {
            k: v
            for k, v in {**regressions, **improvements}.items()
            if abs(v) > 50
        }

        if anomalies:
            lines.append("Anomalies Detected (change > 50%):")
            lines.append("-" * 40)
            for op, pct in anomalies.items():
                lines.append(f"  {op}: {pct:+.1f}%")
            lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)

    def get_bottleneck_detector(self) -> BottleneckDetector:
        """
        Get the bottleneck detector instance.

        Returns:
            BottleneckDetector instance
        """
        return self._detector
