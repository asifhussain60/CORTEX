"""
TDD Test Suite: Deployment Metrics & Analytics

Tests for deployment metrics tracking, health monitoring, alerting,
and integration with existing health reports.

RED Phase: All tests should fail initially
GREEN Phase: Implement deployment_metrics.py to pass tests
REFACTOR Phase: Optimize and clean up implementation

Author: Asif Hussain
Version: 1.0.0
"""

import pytest
import tempfile
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Import will fail initially (RED phase) - implement in GREEN phase
try:
    from src.deployment.deployment_metrics import (
        DeploymentMetricsCollector,
        DeploymentMetric,
        MetricType,
        AlertLevel,
        DeploymentAlert,
        generate_metrics_report,
        check_health_thresholds
    )
except ImportError:
    # RED phase - module doesn't exist yet
    DeploymentMetricsCollector = None
    DeploymentMetric = None
    MetricType = None
    AlertLevel = None
    DeploymentAlert = None
    generate_metrics_report = None
    check_health_thresholds = None


@pytest.fixture
def temp_cortex_root():
    """Create temporary CORTEX root for testing."""
    temp_dir = tempfile.mkdtemp()
    cortex_root = Path(temp_dir)
    
    # Create expected directory structure
    (cortex_root / "cortex-brain" / "metrics" / "deployments").mkdir(parents=True)
    (cortex_root / "cortex-brain" / "health-reports").mkdir(parents=True)
    
    yield cortex_root
    
    # Cleanup
    shutil.rmtree(temp_dir)


# Test Class 1: Initialization and Configuration
class TestDeploymentMetricsInitialization:
    """Test metrics collector initialization."""
    
    def test_collector_initialization(self, temp_cortex_root):
        """Test metrics collector initializes correctly."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        assert collector is not None
        assert collector.cortex_root == temp_cortex_root
        assert collector.metrics_dir == temp_cortex_root / "cortex-brain" / "metrics" / "deployments"
        assert collector.metrics_dir.exists()
    
    def test_metrics_directory_creation(self, temp_cortex_root):
        """Test metrics directory is created if missing."""
        metrics_dir = temp_cortex_root / "cortex-brain" / "metrics" / "deployments"
        metrics_dir.rmdir()  # Remove directory
        
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        assert collector.metrics_dir.exists()


# Test Class 2: Metric Recording
class TestMetricRecording:
    """Test recording deployment metrics."""
    
    def test_record_deployment_duration(self, temp_cortex_root):
        """Test recording deployment duration."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        metric = collector.record_metric(
            metric_type=MetricType.DEPLOYMENT_DURATION,
            value=180.5,  # 3 minutes
            deployment_id="deploy-123",
            metadata={"phase": "full"}
        )
        
        assert metric is not None
        assert metric.metric_type == MetricType.DEPLOYMENT_DURATION
        assert metric.value == 180.5
        assert metric.deployment_id == "deploy-123"
    
    def test_record_phase_duration(self, temp_cortex_root):
        """Test recording individual phase duration."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        metric = collector.record_metric(
            metric_type=MetricType.PHASE_DURATION,
            value=45.2,
            deployment_id="deploy-123",
            metadata={"phase": "BUILD"}
        )
        
        assert metric.metric_type == MetricType.PHASE_DURATION
        assert metric.metadata["phase"] == "BUILD"
    
    def test_record_gate_results(self, temp_cortex_root):
        """Test recording gate validation results."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        metric = collector.record_metric(
            metric_type=MetricType.GATE_PASS_RATE,
            value=0.85,  # 85% pass rate
            deployment_id="deploy-123",
            metadata={"total_gates": 20, "passed": 17, "failed": 3}
        )
        
        assert metric.metric_type == MetricType.GATE_PASS_RATE
        assert metric.value == 0.85
    
    def test_record_rollback_event(self, temp_cortex_root):
        """Test recording rollback events."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        metric = collector.record_metric(
            metric_type=MetricType.ROLLBACK_COUNT,
            value=1,
            deployment_id="deploy-123",
            metadata={"reason": "gate_failure", "snapshot_id": "snap-456"}
        )
        
        assert metric.metric_type == MetricType.ROLLBACK_COUNT
        assert metric.metadata["reason"] == "gate_failure"
    
    def test_record_deployment_success(self, temp_cortex_root):
        """Test recording deployment outcome."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        metric = collector.record_metric(
            metric_type=MetricType.DEPLOYMENT_SUCCESS,
            value=1,  # Success
            deployment_id="deploy-123"
        )
        
        assert metric.metric_type == MetricType.DEPLOYMENT_SUCCESS
        assert metric.value == 1


# Test Class 3: Metric Persistence
class TestMetricPersistence:
    """Test metrics are persisted to disk."""
    
    def test_metrics_saved_to_file(self, temp_cortex_root):
        """Test metrics are saved to JSONL file."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        collector.record_metric(
            metric_type=MetricType.DEPLOYMENT_DURATION,
            value=120.0,
            deployment_id="deploy-123"
        )
        
        # Check metrics file exists
        metrics_file = collector.metrics_dir / "deployment-metrics.jsonl"
        assert metrics_file.exists()
        
        # Verify content
        with open(metrics_file, 'r') as f:
            line = f.readline()
            data = json.loads(line)
        
        assert data['metric_type'] == MetricType.DEPLOYMENT_DURATION.value
        assert data['value'] == 120.0
    
    def test_multiple_metrics_appended(self, temp_cortex_root):
        """Test multiple metrics are appended to file."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 100.0, "deploy-1")
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 150.0, "deploy-2")
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 200.0, "deploy-3")
        
        metrics_file = collector.metrics_dir / "deployment-metrics.jsonl"
        
        with open(metrics_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 3


# Test Class 4: Metric Querying
class TestMetricQuerying:
    """Test querying and filtering metrics."""
    
    def test_get_metrics_by_type(self, temp_cortex_root):
        """Test filtering metrics by type."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 100.0, "deploy-1")
        collector.record_metric(MetricType.GATE_PASS_RATE, 0.9, "deploy-1")
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 150.0, "deploy-2")
        
        duration_metrics = collector.get_metrics(metric_type=MetricType.DEPLOYMENT_DURATION)
        
        assert len(duration_metrics) == 2
        assert all(m.metric_type == MetricType.DEPLOYMENT_DURATION for m in duration_metrics)
    
    def test_get_metrics_by_deployment_id(self, temp_cortex_root):
        """Test filtering metrics by deployment ID."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 100.0, "deploy-1")
        collector.record_metric(MetricType.GATE_PASS_RATE, 0.9, "deploy-1")
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 150.0, "deploy-2")
        
        deploy1_metrics = collector.get_metrics(deployment_id="deploy-1")
        
        assert len(deploy1_metrics) == 2
        assert all(m.deployment_id == "deploy-1" for m in deploy1_metrics)
    
    def test_get_metrics_by_time_range(self, temp_cortex_root):
        """Test filtering metrics by time range."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        now = datetime.now()
        
        # Create metrics with different timestamps
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 100.0, "deploy-1")
        
        # Get metrics from last hour
        start_time = now - timedelta(hours=1)
        recent_metrics = collector.get_metrics(start_time=start_time)
        
        assert len(recent_metrics) >= 1


# Test Class 5: Aggregated Statistics
class TestAggregatedStatistics:
    """Test aggregated statistics calculation."""
    
    def test_calculate_average_duration(self, temp_cortex_root):
        """Test calculating average deployment duration."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 100.0, "deploy-1")
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 150.0, "deploy-2")
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 200.0, "deploy-3")
        
        avg_duration = collector.get_average_duration()
        
        assert avg_duration == 150.0
    
    def test_calculate_success_rate(self, temp_cortex_root):
        """Test calculating deployment success rate."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        collector.record_metric(MetricType.DEPLOYMENT_SUCCESS, 1, "deploy-1")  # Success
        collector.record_metric(MetricType.DEPLOYMENT_SUCCESS, 1, "deploy-2")  # Success
        collector.record_metric(MetricType.DEPLOYMENT_SUCCESS, 0, "deploy-3")  # Failure
        collector.record_metric(MetricType.DEPLOYMENT_SUCCESS, 1, "deploy-4")  # Success
        
        success_rate = collector.get_success_rate()
        
        assert success_rate == 0.75  # 3 out of 4
    
    def test_calculate_rollback_frequency(self, temp_cortex_root):
        """Test calculating rollback frequency."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        collector.record_metric(MetricType.ROLLBACK_COUNT, 1, "deploy-1")
        collector.record_metric(MetricType.ROLLBACK_COUNT, 0, "deploy-2")
        collector.record_metric(MetricType.ROLLBACK_COUNT, 1, "deploy-3")
        
        rollback_count = collector.get_rollback_count(days=7)
        
        assert rollback_count == 2
    
    def test_calculate_gate_statistics(self, temp_cortex_root):
        """Test calculating gate pass rate statistics."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        collector.record_metric(MetricType.GATE_PASS_RATE, 0.8, "deploy-1")
        collector.record_metric(MetricType.GATE_PASS_RATE, 0.9, "deploy-2")
        collector.record_metric(MetricType.GATE_PASS_RATE, 0.85, "deploy-3")
        
        avg_pass_rate = collector.get_average_gate_pass_rate()
        
        assert abs(avg_pass_rate - 0.85) < 0.01  # Average of 0.8, 0.9, 0.85


# Test Class 6: Health Threshold Checking
class TestHealthThresholds:
    """Test health threshold checking and alerting."""
    
    def test_alert_on_long_duration(self, temp_cortex_root):
        """Test alert when deployment duration exceeds threshold."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 360.0, "deploy-1")  # 6 minutes > 5 min threshold
        
        alerts = collector.check_health_thresholds()
        
        assert len(alerts) > 0
        assert any(a.alert_level == AlertLevel.WARNING for a in alerts)
        assert any("duration" in a.message.lower() for a in alerts)
    
    def test_alert_on_high_rollback_frequency(self, temp_cortex_root):
        """Test alert when rollback frequency is high."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        # Record 3 rollbacks in short time (exceeds 2/week threshold)
        for i in range(3):
            collector.record_metric(MetricType.ROLLBACK_COUNT, 1, f"deploy-{i}")
        
        alerts = collector.check_health_thresholds()
        
        assert len(alerts) > 0
        assert any("rollback" in a.message.lower() for a in alerts)
    
    def test_alert_on_low_gate_pass_rate(self, temp_cortex_root):
        """Test alert when gate pass rate is consistently low."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        # Record low gate pass rates
        collector.record_metric(MetricType.GATE_PASS_RATE, 0.6, "deploy-1")
        collector.record_metric(MetricType.GATE_PASS_RATE, 0.65, "deploy-2")
        collector.record_metric(MetricType.GATE_PASS_RATE, 0.7, "deploy-3")
        
        alerts = collector.check_health_thresholds()
        
        assert len(alerts) > 0
        assert any("gate" in a.message.lower() for a in alerts)
    
    def test_no_alerts_when_healthy(self, temp_cortex_root):
        """Test no alerts when metrics are healthy."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 120.0, "deploy-1")  # 2 min (good)
        collector.record_metric(MetricType.GATE_PASS_RATE, 0.95, "deploy-1")  # 95% (good)
        collector.record_metric(MetricType.DEPLOYMENT_SUCCESS, 1, "deploy-1")  # Success
        
        alerts = collector.check_health_thresholds()
        
        assert len(alerts) == 0


# Test Class 7: Alert Generation
class TestAlertGeneration:
    """Test alert object generation."""
    
    def test_create_warning_alert(self, temp_cortex_root):
        """Test creating warning-level alert."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        alert = collector.create_alert(
            alert_level=AlertLevel.WARNING,
            message="Deployment duration exceeded threshold",
            metric_type=MetricType.DEPLOYMENT_DURATION,
            current_value=360.0,
            threshold_value=300.0
        )
        
        assert alert.alert_level == AlertLevel.WARNING
        assert "duration" in alert.message.lower()
        assert alert.current_value == 360.0
    
    def test_create_critical_alert(self, temp_cortex_root):
        """Test creating critical-level alert."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        alert = collector.create_alert(
            alert_level=AlertLevel.CRITICAL,
            message="Multiple consecutive deployment failures",
            metric_type=MetricType.DEPLOYMENT_SUCCESS
        )
        
        assert alert.alert_level == AlertLevel.CRITICAL


# Test Class 8: Report Generation
class TestReportGeneration:
    """Test metrics report generation."""
    
    def test_generate_metrics_report(self, temp_cortex_root):
        """Test generating comprehensive metrics report."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        # Add some metrics
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 120.0, "deploy-1")
        collector.record_metric(MetricType.GATE_PASS_RATE, 0.9, "deploy-1")
        collector.record_metric(MetricType.DEPLOYMENT_SUCCESS, 1, "deploy-1")
        
        report = collector.generate_report(days=7)
        
        assert report is not None
        assert "total_deployments" in report
        assert "average_duration" in report
        assert "success_rate" in report
        assert "rollback_count" in report
    
    def test_report_includes_alerts(self, temp_cortex_root):
        """Test report includes active alerts."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        # Add metric that triggers alert
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 400.0, "deploy-1")
        
        report = collector.generate_report(days=7)
        
        assert "alerts" in report
        assert len(report["alerts"]) > 0
    
    def test_save_report_to_disk(self, temp_cortex_root):
        """Test saving report to disk."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 120.0, "deploy-1")
        
        report_path = collector.save_report(days=7)
        
        assert report_path is not None
        assert report_path.exists()
        assert report_path.suffix == ".json"


# Test Class 9: Health Report Integration
class TestHealthReportIntegration:
    """Test integration with existing health reports."""
    
    def test_export_to_health_report_format(self, temp_cortex_root):
        """Test exporting metrics in health report format."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 120.0, "deploy-1")
        collector.record_metric(MetricType.DEPLOYMENT_SUCCESS, 1, "deploy-1")
        
        health_data = collector.export_for_health_report()
        
        assert health_data is not None
        assert "deployment_metrics" in health_data
        assert "health_score" in health_data
    
    def test_calculate_health_score(self, temp_cortex_root):
        """Test calculating deployment health score."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        # Good metrics
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 120.0, "deploy-1")
        collector.record_metric(MetricType.GATE_PASS_RATE, 0.95, "deploy-1")
        collector.record_metric(MetricType.DEPLOYMENT_SUCCESS, 1, "deploy-1")
        
        health_score = collector.calculate_health_score()
        
        assert 0.0 <= health_score <= 100.0
        assert health_score > 80.0  # Good metrics should score high


# Test Class 10: Trend Analysis
class TestTrendAnalysis:
    """Test trend analysis functionality."""
    
    def test_detect_duration_trend(self, temp_cortex_root):
        """Test detecting deployment duration trend."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        # Increasing duration trend
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 100.0, "deploy-1")
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 150.0, "deploy-2")
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 200.0, "deploy-3")
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 250.0, "deploy-4")
        
        trend = collector.analyze_trend(MetricType.DEPLOYMENT_DURATION, days=7)
        
        assert trend is not None
        assert trend["direction"] == "increasing"
    
    def test_detect_stable_trend(self, temp_cortex_root):
        """Test detecting stable metrics."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        # Stable gate pass rates
        for i in range(5):
            collector.record_metric(MetricType.GATE_PASS_RATE, 0.9, f"deploy-{i}")
        
        trend = collector.analyze_trend(MetricType.GATE_PASS_RATE, days=7)
        
        assert trend["direction"] == "stable"


# Test Class 11: End-to-End Metrics Workflow
class TestEndToEndMetricsWorkflow:
    """Test complete metrics collection and reporting workflow."""
    
    def test_full_deployment_metrics_lifecycle(self, temp_cortex_root):
        """Test full deployment with metrics collection."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        deployment_id = "deploy-123"
        
        # Record deployment start
        start_time = datetime.now()
        
        # Record phase durations
        collector.record_metric(MetricType.PHASE_DURATION, 30.0, deployment_id, {"phase": "PRE_FLIGHT"})
        collector.record_metric(MetricType.PHASE_DURATION, 45.0, deployment_id, {"phase": "BUILD"})
        collector.record_metric(MetricType.PHASE_DURATION, 60.0, deployment_id, {"phase": "DEPLOY"})
        
        # Record gate results
        collector.record_metric(MetricType.GATE_PASS_RATE, 0.95, deployment_id, {"total": 20, "passed": 19})
        
        # Record deployment success
        total_duration = 135.0
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, total_duration, deployment_id)
        collector.record_metric(MetricType.DEPLOYMENT_SUCCESS, 1, deployment_id)
        
        # Generate report
        report = collector.generate_report(days=1)
        
        assert report["total_deployments"] >= 1
        assert report["average_duration"] == total_duration
        assert report["success_rate"] == 1.0
    
    def test_failed_deployment_with_rollback(self, temp_cortex_root):
        """Test failed deployment with rollback metrics."""
        collector = DeploymentMetricsCollector(cortex_root=temp_cortex_root)
        
        deployment_id = "deploy-456"
        
        # Record phases up to failure
        collector.record_metric(MetricType.PHASE_DURATION, 30.0, deployment_id, {"phase": "PRE_FLIGHT"})
        collector.record_metric(MetricType.PHASE_DURATION, 45.0, deployment_id, {"phase": "BUILD"})
        
        # Gate failure
        collector.record_metric(MetricType.GATE_PASS_RATE, 0.6, deployment_id, {"total": 20, "passed": 12})
        
        # Rollback triggered
        collector.record_metric(MetricType.ROLLBACK_COUNT, 1, deployment_id, {"reason": "gate_failure"})
        
        # Deployment failed
        collector.record_metric(MetricType.DEPLOYMENT_DURATION, 80.0, deployment_id)
        collector.record_metric(MetricType.DEPLOYMENT_SUCCESS, 0, deployment_id)
        
        # Check alerts triggered
        alerts = collector.check_health_thresholds()
        
        assert len(alerts) > 0
        # Should alert on low gate pass rate
        assert any("gate" in a.message.lower() for a in alerts)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
