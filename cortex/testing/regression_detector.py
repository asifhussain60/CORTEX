"""
AC_START: AC-PHASE38.0-012
Regression Detector - Stage 3 Implementation

Detects performance regressions by comparing against baseline.
Thresholds: latency +10%, memory +15%, test_time +20%.

Authority: Phase 38.0 Stage 3 - Remediation & Baseline Restoration
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from cortex.testing.baseline_metrics_collector import PerformanceMetrics


class RegressionSeverity(Enum):
    """Severity of detected regression."""
    NONE = "none"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class RegressionResult:
    """Result of regression detection."""
    has_regression: bool
    severity: RegressionSeverity
    regressions: List[str]
    metrics_comparison: Dict[str, Tuple[float, float, float]]  # metric: (baseline, current, % change)
    
    
class RegressionDetector:
    """
    Detects performance regressions against baseline.
    
    AC-PHASE38.0-012: Configurable thresholds for latency, memory, test time.
    """
    
    def __init__(
        self,
        latency_threshold_percent: float = 10.0,
        memory_threshold_percent: float = 15.0,
        test_time_threshold_percent: float = 20.0
    ):
        """
        Initialize regression detector.
        
        Args:
            latency_threshold_percent: Max allowed latency increase (%)
            memory_threshold_percent: Max allowed memory increase (%)
            test_time_threshold_percent: Max allowed test time increase (%)
        """
        self.latency_threshold = latency_threshold_percent
        self.memory_threshold = memory_threshold_percent
        self.test_time_threshold = test_time_threshold_percent
    
    def calculate_percent_change(self, baseline: float, current: float) -> float:
        """
        Calculate percentage change from baseline.
        
        Args:
            baseline: Baseline value
            current: Current value
            
        Returns:
            Percentage change (positive = increase, negative = decrease)
        """
        if baseline == 0:
            return 0.0 if current == 0 else 100.0
        
        return ((current - baseline) / baseline) * 100
    
    def detect(
        self,
        baseline: PerformanceMetrics,
        current: PerformanceMetrics
    ) -> RegressionResult:
        """
        Detect regressions between baseline and current metrics.
        
        Args:
            baseline: Baseline performance metrics
            current: Current performance metrics
            
        Returns:
            RegressionResult with detected issues
        """
        regressions = []
        comparisons = {}
        severity = RegressionSeverity.NONE
        
        # Check latency
        latency_change = self.calculate_percent_change(
            baseline.orchestrator_routing_latency_ms,
            current.orchestrator_routing_latency_ms
        )
        comparisons["latency"] = (
            baseline.orchestrator_routing_latency_ms,
            current.orchestrator_routing_latency_ms,
            latency_change
        )
        
        if latency_change > self.latency_threshold:
            regressions.append(
                f"Latency increased {latency_change:.1f}% "
                f"(threshold: {self.latency_threshold}%)"
            )
            severity = RegressionSeverity.CRITICAL
        
        # Check memory
        memory_change = self.calculate_percent_change(
            baseline.memory_usage_mb_average,
            current.memory_usage_mb_average
        )
        comparisons["memory"] = (
            baseline.memory_usage_mb_average,
            current.memory_usage_mb_average,
            memory_change
        )
        
        if memory_change > self.memory_threshold:
            regressions.append(
                f"Memory increased {memory_change:.1f}% "
                f"(threshold: {self.memory_threshold}%)"
            )
            if severity == RegressionSeverity.NONE:
                severity = RegressionSeverity.WARNING
        
        # Check test execution time (P95)
        test_time_change = self.calculate_percent_change(
            baseline.test_execution_time_p95,
            current.test_execution_time_p95
        )
        comparisons["test_time_p95"] = (
            baseline.test_execution_time_p95,
            current.test_execution_time_p95,
            test_time_change
        )
        
        if test_time_change > self.test_time_threshold:
            regressions.append(
                f"Test time (P95) increased {test_time_change:.1f}% "
                f"(threshold: {self.test_time_threshold}%)"
            )
            if severity == RegressionSeverity.NONE:
                severity = RegressionSeverity.WARNING
        
        return RegressionResult(
            has_regression=len(regressions) > 0,
            severity=severity,
            regressions=regressions,
            metrics_comparison=comparisons
        )


# AC_COMPLETE: AC-PHASE38.0-012 ✅
# Implementation: RegressionDetector fully implemented
# Tests: 5 tests required (see test_regression_detector.py)
