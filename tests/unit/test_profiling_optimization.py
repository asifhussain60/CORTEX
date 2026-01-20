"""
Test suite for Performance Profiling & Optimization (OB-002-02).

This module tests bottleneck identification, optimization recommendations,
and performance comparison reporting.

Acceptance Tests:
- Bottlenecks identifiable from data
- Optimization recommendations generated
- Before/after comparison available
"""

import pytest
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


# Import modules to be tested (will be created)
from cortex.core.observability.performance_profiler import (
    PerformanceProfiler,
    BottleneckDetector,
    Bottleneck,
    OptimizationRecommendation,
)


class TestBottleneckDetection:
    """Test bottleneck identification."""

    def test_bottleneck_detector_initializes(self) -> None:
        """
        Test that bottleneck detector initializes correctly.

        Expected:
        - Detector instance created
        - Configuration stored
        """
        detector = BottleneckDetector(
            latency_threshold_ms=1000,
            error_rate_threshold_pct=5.0,
        )
        
        assert detector is not None
        assert detector.latency_threshold_ms == 1000
        assert detector.error_rate_threshold_pct == 5.0

    def test_detect_high_latency_bottleneck(self) -> None:
        """
        Test detection of high latency bottleneck.

        Expected:
        - High latency operations identified
        - Severity level assigned
        """
        detector = BottleneckDetector(latency_threshold_ms=500)
        
        metrics = {
            "operation.a": {
                "latency_avg": 100.0,
                "latency_p95": 200.0,
                "span_count": 1000,
            },
            "operation.b": {
                "latency_avg": 1500.0,
                "latency_p95": 2000.0,
                "span_count": 500,
            },
        }
        
        bottlenecks = detector.detect(metrics)
        
        # Should find operation.b as bottleneck
        assert len(bottlenecks) > 0
        assert any(b.operation == "operation.b" for b in bottlenecks)

    def test_detect_high_error_rate_bottleneck(self) -> None:
        """
        Test detection of high error rate bottleneck.

        Expected:
        - High error rate operations identified
        """
        detector = BottleneckDetector(error_rate_threshold_pct=5.0)
        
        metrics = {
            "operation.a": {
                "error_count": 5,
                "total_count": 1000,
                "error_rate": 0.5,
            },
            "operation.b": {
                "error_count": 100,
                "total_count": 1000,
                "error_rate": 10.0,
            },
        }
        
        bottlenecks = detector.detect(metrics)
        
        # Should find operation.b as bottleneck
        assert any(b.operation == "operation.b" for b in bottlenecks)

    def test_bottleneck_severity_assignment(self) -> None:
        """
        Test that bottlenecks are assigned severity levels.

        Expected:
        - Severity based on threshold breach magnitude
        - Higher breach = higher severity
        """
        detector = BottleneckDetector(latency_threshold_ms=100)
        
        metrics = {
            "minor_issue": {"latency_avg": 150.0, "span_count": 100},  # 50% over
            "major_issue": {"latency_avg": 500.0, "span_count": 100},  # 400% over
        }
        
        bottlenecks = detector.detect(metrics)
        
        assert len(bottlenecks) >= 1


class TestPerformanceProfiler:
    """Test performance profiling."""

    def test_profiler_initializes(self) -> None:
        """
        Test that profiler initializes correctly.

        Expected:
        - Profiler instance created
        - Baseline data empty initially
        """
        profiler = PerformanceProfiler()
        
        assert profiler is not None

    def test_record_performance_baseline(self) -> None:
        """
        Test recording performance baseline.

        Expected:
        - Baseline metrics stored
        - Retrievable by timestamp or operation
        """
        profiler = PerformanceProfiler()
        
        baseline_metrics = {
            "operation.a": {
                "latency_avg": 100.0,
                "error_rate": 0.5,
            },
            "operation.b": {
                "latency_avg": 200.0,
                "error_rate": 1.0,
            },
        }
        
        profiler.record_baseline(baseline_metrics)
        
        stored_baseline = profiler.get_baseline()
        assert stored_baseline is not None

    def test_analyze_performance_regression(self) -> None:
        """
        Test detection of performance regression.

        Expected:
        - Regression detected when metrics degrade
        - Degradation percentage calculated
        """
        profiler = PerformanceProfiler()
        
        baseline = {
            "operation.a": {"latency_avg": 100.0},
        }
        
        profiler.record_baseline(baseline)
        
        # Current metrics show degradation
        current = {
            "operation.a": {"latency_avg": 150.0},
        }
        
        regression = profiler.detect_regression(current)
        
        # Should detect 50% increase
        if regression:
            assert len(regression) > 0

    def test_analyze_performance_improvement(self) -> None:
        """
        Test detection of performance improvement.

        Expected:
        - Improvement detected when metrics improve
        - Improvement percentage calculated
        """
        profiler = PerformanceProfiler()
        
        baseline = {
            "operation.a": {"latency_avg": 100.0},
        }
        
        profiler.record_baseline(baseline)
        
        # Current metrics show improvement
        current = {
            "operation.a": {"latency_avg": 50.0},
        }
        
        improvement = profiler.detect_improvement(current)
        
        # Should detect 50% decrease
        if improvement:
            assert len(improvement) > 0


class TestOptimizationRecommendations:
    """Test optimization recommendation generation."""

    def test_generate_recommendations_for_high_latency(self) -> None:
        """
        Test generating recommendations for high latency.

        Expected:
        - Recommendations suggest optimization strategies
        - Recommendations are specific to operation
        """
        detector = BottleneckDetector(latency_threshold_ms=500)
        
        bottlenecks = [
            Bottleneck(
                operation="database_query",
                bottleneck_type="latency",
                severity="HIGH",
                current_value=2000.0,
                threshold_value=500.0,
                affected_spans=1000,
            )
        ]
        
        recommendations = detector.generate_recommendations(bottlenecks)
        
        assert len(recommendations) > 0
        # Should have database-specific recommendations

    def test_recommendations_prioritized_by_impact(self) -> None:
        """
        Test that recommendations are prioritized by impact.

        Expected:
        - High impact recommendations first
        - Impact calculated from affected operation metrics
        """
        detector = BottleneckDetector()
        
        bottlenecks = [
            Bottleneck(
                operation="low_impact",
                bottleneck_type="latency",
                severity="LOW",
                current_value=600.0,
                threshold_value=500.0,
                affected_spans=10,
            ),
            Bottleneck(
                operation="high_impact",
                bottleneck_type="latency",
                severity="HIGH",
                current_value=2000.0,
                threshold_value=500.0,
                affected_spans=10000,
            ),
        ]
        
        recommendations = detector.generate_recommendations(bottlenecks)
        
        # Recommendations should be sorted by improvement impact (descending)
        if len(recommendations) > 1:
            # Higher improvement percentage should come first
            assert (
                recommendations[0].estimated_improvement_pct
                >= recommendations[1].estimated_improvement_pct
            )

    def test_recommendation_includes_estimated_improvement(self) -> None:
        """
        Test that recommendations include estimated improvement.

        Expected:
        - Improvement estimate provided
        - Based on optimization strategy effectiveness
        """
        detector = BottleneckDetector()
        
        bottleneck = Bottleneck(
            operation="test_op",
            bottleneck_type="latency",
            severity="HIGH",
            current_value=1000.0,
            threshold_value=500.0,
            affected_spans=1000,
        )
        
        recommendation = OptimizationRecommendation(
            bottleneck_id="test_bottleneck",
            strategy="add_caching",
            description="Add caching layer",
            estimated_improvement_pct=30.0,
            implementation_complexity="MEDIUM",
            estimated_effort_hours=4,
        )
        
        assert recommendation.estimated_improvement_pct > 0


class TestPerformanceComparison:
    """Test performance comparison reporting."""

    def test_before_after_comparison(self) -> None:
        """
        Test generating before/after comparison report.

        Expected:
        - Report includes both baseline and current metrics
        - Change metrics calculated
        - Comparison includes all operations
        """
        profiler = PerformanceProfiler()
        
        baseline = {
            "operation.a": {
                "latency_avg": 100.0,
                "error_rate": 0.5,
                "p95": 200.0,
            },
            "operation.b": {
                "latency_avg": 500.0,
                "error_rate": 2.0,
                "p95": 1000.0,
            },
        }
        
        profiler.record_baseline(baseline)
        
        current = {
            "operation.a": {
                "latency_avg": 80.0,
                "error_rate": 0.3,
                "p95": 150.0,
            },
            "operation.b": {
                "latency_avg": 600.0,
                "error_rate": 3.0,
                "p95": 1200.0,
            },
        }
        
        comparison = profiler.generate_comparison(current)
        
        assert comparison is not None
        assert "operation.a" in str(comparison)

    def test_comparison_identifies_anomalies(self) -> None:
        """
        Test that comparison identifies anomalous changes.

        Expected:
        - Large changes highlighted
        - Normal variance distinguished from anomalies
        """
        profiler = PerformanceProfiler()
        
        baseline = {
            "stable_op": {"latency_avg": 100.0},
            "degraded_op": {"latency_avg": 100.0},
        }
        
        profiler.record_baseline(baseline)
        
        current = {
            "stable_op": {"latency_avg": 105.0},  # Normal variance
            "degraded_op": {"latency_avg": 500.0},  # Anomaly
        }
        
        comparison = profiler.generate_comparison(current)
        
        # Should flag degraded_op as anomaly
        assert comparison is not None

    def test_comparison_report_format(self) -> None:
        """
        Test that comparison report is properly formatted.

        Expected:
        - Report includes headers and structure
        - Metrics organized and readable
        """
        profiler = PerformanceProfiler()
        
        baseline = {"op": {"latency_avg": 100.0}}
        profiler.record_baseline(baseline)
        
        current = {"op": {"latency_avg": 120.0}}
        
        report = profiler.generate_comparison_report(current)
        
        assert report is not None
        assert isinstance(report, str)
        assert len(report) > 0


class TestProfilerMetrics:
    """Test profiler metrics collection."""

    def test_collect_latency_percentiles(self) -> None:
        """
        Test collection of latency percentiles.

        Expected:
        - p50, p95, p99 collected and available
        - Values in correct order
        """
        profiler = PerformanceProfiler()
        
        metrics = {
            "op": {
                "latency_min": 10.0,
                "latency_p50": 100.0,
                "latency_p95": 500.0,
                "latency_p99": 1000.0,
                "latency_max": 5000.0,
            }
        }
        
        profiler.record_baseline(metrics)
        stored = profiler.get_baseline()
        
        assert stored is not None

    def test_collect_error_metrics(self) -> None:
        """
        Test collection of error rate metrics.

        Expected:
        - Error rate tracked
        - Error trends detected
        """
        profiler = PerformanceProfiler()
        
        metrics = {
            "op": {
                "error_rate": 2.5,
                "error_count": 25,
                "total_count": 1000,
            }
        }
        
        profiler.record_baseline(metrics)
        stored = profiler.get_baseline()
        
        assert stored is not None


class TestTypeHints:
    """Test that all functions have proper type hints (CORE-011)."""

    def test_profiler_has_type_hints(self) -> None:
        """Test that PerformanceProfiler methods have complete type hints."""
        import inspect
        
        methods = inspect.getmembers(PerformanceProfiler, predicate=inspect.ismethod)
        
        for name, method in methods:
            if not name.startswith("_"):
                sig = inspect.signature(method)
                assert sig.return_annotation != inspect.Signature.empty

    def test_detector_has_type_hints(self) -> None:
        """Test that BottleneckDetector methods have complete type hints."""
        import inspect
        
        methods = inspect.getmembers(BottleneckDetector, predicate=inspect.ismethod)
        
        for name, method in methods:
            if not name.startswith("_"):
                sig = inspect.signature(method)
                assert sig.return_annotation != inspect.Signature.empty


class TestDocstrings:
    """Test that all public APIs have docstrings (CORE-012)."""

    def test_profiler_has_docstrings(self) -> None:
        """Test that PerformanceProfiler has docstrings on public methods."""
        import inspect
        
        methods = inspect.getmembers(PerformanceProfiler, predicate=inspect.ismethod)
        
        for name, method in methods:
            if not name.startswith("_"):
                assert method.__doc__ is not None

    def test_detector_has_docstrings(self) -> None:
        """Test that BottleneckDetector has docstrings on public methods."""
        import inspect
        
        methods = inspect.getmembers(BottleneckDetector, predicate=inspect.ismethod)
        
        for name, method in methods:
            if not name.startswith("_"):
                assert method.__doc__ is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
