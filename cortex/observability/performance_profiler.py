"""performance_profiler.py — Performance Profiler for CORTEX observability.

Canonical location: cortex/observability/performance_profiler.py
Migrated from cortex/core/observability/ (Phase 68 flatten — subdir count gate).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class PerformanceLevel(str, Enum):
    """Performance level classification."""

    EXCELLENT = "excellent"
    GOOD = "good"
    DEGRADED = "degraded"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Single performance measurement."""

    label: str
    elapsed_seconds: float
    level: PerformanceLevel = PerformanceLevel.GOOD

    @property
    def elapsed_ms(self) -> float:
        """Elapsed time in milliseconds."""
        return self.elapsed_seconds * 1000.0


@dataclass
class Bottleneck:
    """Detected performance bottleneck."""

    label: str
    elapsed_seconds: float
    threshold_seconds: float
    severity: PerformanceLevel = PerformanceLevel.DEGRADED


@dataclass
class OptimizationRecommendation:
    """Recommendation for performance optimisation."""

    bottleneck: Bottleneck
    recommendation: str
    expected_improvement_pct: float = 0.0


@dataclass
class PerformanceStats:
    """Aggregated profiling statistics."""

    metrics: List[PerformanceMetric] = field(default_factory=list)
    bottlenecks: List[Bottleneck] = field(default_factory=list)
    recommendations: List[OptimizationRecommendation] = field(default_factory=list)

    @property
    def total_elapsed_seconds(self) -> float:
        """Sum of all measured elapsed times."""
        return sum(m.elapsed_seconds for m in self.metrics)

    @property
    def average_elapsed_seconds(self) -> float:
        """Average elapsed time across all metrics."""
        if not self.metrics:
            return 0.0
        return self.total_elapsed_seconds / len(self.metrics)


class PerformanceProfiler:
    """Profiles execution time of orchestrator operations."""

    # Thresholds in seconds
    _THRESHOLDS: Dict[str, float] = {
        "core": 0.2,
        "domain": 0.5,
        "support": 1.0,
        "default": 1.0,
    }

    def __init__(self) -> None:
        """Initialise profiler."""
        self._timings: Dict[str, float] = {}
        self._metrics: List[PerformanceMetric] = []

    def start(self, label: str) -> None:
        """Start timing a labelled operation.

        Args:
            label: Operation label.
        """
        self._timings[label] = time.monotonic()

    def stop(self, label: str) -> float:
        """Stop timing and return elapsed seconds.

        Args:
            label: Operation label.

        Returns:
            Elapsed time in seconds.
        """
        start = self._timings.pop(label, time.monotonic())
        elapsed = time.monotonic() - start
        level = self._classify(elapsed)
        self._metrics.append(PerformanceMetric(label=label, elapsed_seconds=elapsed, level=level))
        return elapsed

    def report(self) -> Dict[str, Any]:
        """Return profiling report."""
        return {
            "active_timers": list(self._timings.keys()),
            "completed_metrics": len(self._metrics),
            "total_elapsed_seconds": sum(m.elapsed_seconds for m in self._metrics),
        }

    def get_stats(self) -> PerformanceStats:
        """Return aggregated PerformanceStats."""
        bottlenecks = self._detect_bottlenecks()
        recommendations = [
            OptimizationRecommendation(
                bottleneck=b,
                recommendation=f"Optimise '{b.label}' — exceeds threshold by "
                f"{(b.elapsed_seconds - b.threshold_seconds) * 1000:.0f}ms",
            )
            for b in bottlenecks
        ]
        return PerformanceStats(
            metrics=list(self._metrics),
            bottlenecks=bottlenecks,
            recommendations=recommendations,
        )

    # ── Private helpers ──────────────────────────────────────────────────────

    def _classify(self, elapsed: float) -> PerformanceLevel:
        """Classify elapsed time into a PerformanceLevel."""
        if elapsed < 0.1:
            return PerformanceLevel.EXCELLENT
        if elapsed < 0.5:
            return PerformanceLevel.GOOD
        if elapsed < 1.0:
            return PerformanceLevel.DEGRADED
        return PerformanceLevel.CRITICAL

    def _detect_bottlenecks(self) -> List[Bottleneck]:
        """Detect metrics that exceed their domain threshold."""
        bottlenecks: List[Bottleneck] = []
        for m in self._metrics:
            threshold = self._THRESHOLDS.get("default", 1.0)
            if m.elapsed_seconds > threshold:
                bottlenecks.append(
                    Bottleneck(
                        label=m.label,
                        elapsed_seconds=m.elapsed_seconds,
                        threshold_seconds=threshold,
                        severity=m.level,
                    )
                )
        return bottlenecks


# ── Module-level singleton ────────────────────────────────────────────────────

_profiler_instance: Optional[PerformanceProfiler] = None


def get_performance_profiler() -> PerformanceProfiler:
    """Return the module-level PerformanceProfiler singleton.

    Returns:
        Shared PerformanceProfiler instance.
    """
    global _profiler_instance
    if _profiler_instance is None:
        _profiler_instance = PerformanceProfiler()
    return _profiler_instance
