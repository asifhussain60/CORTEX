"""
Tests for BaselineMetricsCollector - Phase 38.0 Stage 3
Tests MUST come before implementation (CORE-008 TDD)

AC-PHASE38.0-003: Baseline Performance Metrics Collection
- Captures test execution times
- Measures memory usage
- Records latency metrics
- Stores baseline for regression detection
"""

import pytest
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime


class TestBaselineMetricsCollector:
    """Test suite for baseline metrics collection."""
    
    def test_collector_initializes_with_workspace(self):
        """Test collector initialization."""
        from cortex.phase_38.baseline_metrics_collector import BaselineMetricsCollector
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        collector = BaselineMetricsCollector(workspace_root=workspace)
        
        assert collector.workspace_root == workspace
        assert collector.baselines_dir.exists()
    
    def test_collector_captures_test_execution_metrics(self):
        """Test capturing test suite execution metrics."""
        from cortex.phase_38.baseline_metrics_collector import BaselineMetricsCollector
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        collector = BaselineMetricsCollector(workspace_root=workspace)
        
        metrics = collector.capture_test_metrics()
        
        assert "total_tests" in metrics
        assert "duration_seconds" in metrics
        assert "tests_per_second" in metrics
        assert isinstance(metrics["total_tests"], int)
        assert isinstance(metrics["duration_seconds"], float)
    
    def test_collector_captures_memory_metrics(self):
        """Test capturing memory usage metrics."""
        from cortex.phase_38.baseline_metrics_collector import BaselineMetricsCollector
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        collector = BaselineMetricsCollector(workspace_root=workspace)
        
        metrics = collector.capture_memory_metrics()
        
        assert "rss_mb" in metrics
        assert "vms_mb" in metrics
        assert "percent" in metrics
        assert isinstance(metrics["rss_mb"], (int, float))
        assert isinstance(metrics["vms_mb"], (int, float))
    
    def test_collector_captures_import_latency(self):
        """Test measuring import latency for key modules."""
        from cortex.phase_38.baseline_metrics_collector import BaselineMetricsCollector
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        collector = BaselineMetricsCollector(workspace_root=workspace)
        
        latencies = collector.capture_import_latency()
        
        assert isinstance(latencies, dict)
        assert len(latencies) > 0
        # Should measure key modules
        assert any("cortex" in module for module in latencies.keys())
    
    def test_collector_captures_file_count_metrics(self):
        """Test capturing repository file statistics."""
        from cortex.phase_38.baseline_metrics_collector import BaselineMetricsCollector
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        collector = BaselineMetricsCollector(workspace_root=workspace)
        
        metrics = collector.capture_file_metrics()
        
        assert "total_python_files" in metrics
        assert "total_test_files" in metrics
        assert "lines_of_code" in metrics
        assert isinstance(metrics["total_python_files"], int)
        assert metrics["total_python_files"] > 0
    
    def test_collector_generates_baseline_report(self):
        """Test generation of complete baseline report."""
        from cortex.phase_38.baseline_metrics_collector import BaselineMetricsCollector
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        collector = BaselineMetricsCollector(workspace_root=workspace)
        
        report_path = collector.generate_baseline_report()
        
        assert report_path.exists()
        assert report_path.suffix == ".json"
        assert "pre-phase38" in report_path.name
        
        # Validate JSON structure
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        assert "timestamp" in report
        assert "test_metrics" in report
        assert "memory_metrics" in report
        assert "import_latency" in report
        assert "file_metrics" in report
    
    def test_collector_report_saved_to_baselines_dir(self):
        """Test that baseline report is saved to correct location."""
        from cortex.phase_38.baseline_metrics_collector import BaselineMetricsCollector
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        collector = BaselineMetricsCollector(workspace_root=workspace)
        
        report_path = collector.generate_baseline_report()
        
        assert "cortex-registry" in str(report_path)
        assert "_cortex-master" in str(report_path)
        assert "baselines" in str(report_path)
    
    def test_collector_includes_phase_metadata(self):
        """Test that report includes Phase 38.0 metadata."""
        from cortex.phase_38.baseline_metrics_collector import BaselineMetricsCollector
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        collector = BaselineMetricsCollector(workspace_root=workspace)
        
        report_path = collector.generate_baseline_report()
        
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        assert "phase" in report
        assert "38.0" in report["phase"]


class TestRegressionDetector:
    """Test suite for regression detection."""
    
    def test_detector_loads_baseline(self):
        """Test loading existing baseline report."""
        from cortex.phase_38.baseline_metrics_collector import RegressionDetector
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        detector = RegressionDetector(workspace_root=workspace)
        
        # First generate a baseline
        from cortex.phase_38.baseline_metrics_collector import BaselineMetricsCollector
        collector = BaselineMetricsCollector(workspace_root=workspace)
        baseline_path = collector.generate_baseline_report()
        
        # Now load it
        baseline = detector.load_baseline(baseline_path)
        
        assert baseline is not None
        assert isinstance(baseline, dict)
    
    def test_detector_compares_test_metrics(self):
        """Test comparing test execution metrics."""
        from cortex.phase_38.baseline_metrics_collector import RegressionDetector
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        detector = RegressionDetector(workspace_root=workspace)
        
        baseline = {
            "test_metrics": {
                "total_tests": 100,
                "duration_seconds": 10.0,
                "tests_per_second": 10.0
            }
        }
        
        current = {
            "test_metrics": {
                "total_tests": 100,
                "duration_seconds": 12.0,
                "tests_per_second": 8.33
            }
        }
        
        comparison = detector.compare_metrics(baseline, current)
        
        assert "test_metrics" in comparison
        assert "regression_detected" in comparison
    
    def test_detector_identifies_performance_regression(self):
        """Test identification of performance regressions."""
        from cortex.phase_38.baseline_metrics_collector import RegressionDetector
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        detector = RegressionDetector(workspace_root=workspace)
        
        # Simulate 50% slowdown (regression)
        baseline = {"test_metrics": {"duration_seconds": 10.0}}
        current = {"test_metrics": {"duration_seconds": 15.0}}
        
        comparison = detector.compare_metrics(baseline, current)
        
        # Should detect regression (>20% threshold)
        assert comparison["regression_detected"] is True
    
    def test_detector_allows_minor_variations(self):
        """Test that minor variations don't trigger false positives."""
        from cortex.phase_38.baseline_metrics_collector import RegressionDetector
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        detector = RegressionDetector(workspace_root=workspace)
        
        # Simulate 5% variation (acceptable)
        baseline = {"test_metrics": {"duration_seconds": 10.0}}
        current = {"test_metrics": {"duration_seconds": 10.5}}
        
        comparison = detector.compare_metrics(baseline, current)
        
        # Should NOT detect regression (<20% threshold)
        assert comparison["regression_detected"] is False
    
    def test_detector_generates_comparison_report(self):
        """Test generation of regression comparison report."""
        from cortex.phase_38.baseline_metrics_collector import RegressionDetector
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        detector = RegressionDetector(workspace_root=workspace)
        
        baseline = {
            "timestamp": "2026-02-07T00:00:00",
            "test_metrics": {"duration_seconds": 10.0}
        }
        current = {
            "timestamp": "2026-02-07T12:00:00",
            "test_metrics": {"duration_seconds": 10.5}
        }
        
        report_path = detector.generate_comparison_report(baseline, current)
        
        assert report_path.exists()
        assert report_path.suffix == ".json"
        assert "regression-check" in report_path.name
        
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        assert "baseline_timestamp" in report
        assert "current_timestamp" in report
        assert "comparison" in report
    
    def test_detector_calculates_percentage_change(self):
        """Test calculation of percentage changes."""
        from cortex.phase_38.baseline_metrics_collector import RegressionDetector
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        detector = RegressionDetector(workspace_root=workspace)
        
        baseline_value = 100.0
        current_value = 120.0
        
        pct_change = detector.calculate_percentage_change(baseline_value, current_value)
        
        assert pct_change == 20.0
    
    def test_detector_handles_zero_baseline_values(self):
        """Test handling of zero values in baseline."""
        from cortex.phase_38.baseline_metrics_collector import RegressionDetector
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        detector = RegressionDetector(workspace_root=workspace)
        
        baseline_value = 0.0
        current_value = 10.0
        
        # Should handle gracefully without division by zero
        pct_change = detector.calculate_percentage_change(baseline_value, current_value)
        
        assert pct_change is not None
        assert isinstance(pct_change, (int, float))
