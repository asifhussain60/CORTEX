"""
Tests for Dashboard Service and Alert Manager

AC-NFR-004-02: Dashboard shows real-time progress
AC-NFR-004-03: Alerts triggered on threshold breach
"""

import pytest
from datetime import datetime, timedelta
from cortex.infrastructure.dashboard_service import (
    DashboardService,
    ProgressAggregator,
    ProgressSnapshot,
    ProgressMetrics,
    DashboardStatus,
)
from cortex.infrastructure.alert_manager import (
    AlertManager,
    ThresholdMonitor,
    ThresholdRule,
    Alert,
    AlertSeverity,
    AlertState,
)


# ============================================================================
# DASHBOARD SERVICE TESTS
# ============================================================================

@pytest.fixture
def progress_aggregator():
    """Create a progress aggregator."""
    return ProgressAggregator()


@pytest.fixture
def dashboard(progress_aggregator):
    """Create a dashboard service."""
    return DashboardService(progress_aggregator)


class TestProgressSnapshot:
    """Test progress snapshot calculations."""
    
    def test_completion_percentage(self):
        """Test completion percentage calculation."""
        snapshot = ProgressSnapshot(
            total_items=100,
            completed_items=50,
            in_progress_items=25,
            failed_items=25
        )
        assert snapshot.completion_percentage == 50.0
    
    def test_completion_percentage_zero(self):
        """Test completion percentage with zero items."""
        snapshot = ProgressSnapshot(
            total_items=0,
            completed_items=0,
            in_progress_items=0,
            failed_items=0
        )
        assert snapshot.completion_percentage == 0.0
    
    def test_success_rate(self):
        """Test success rate calculation."""
        snapshot = ProgressSnapshot(
            total_items=100,
            completed_items=80,
            in_progress_items=10,
            failed_items=10
        )
        assert abs(snapshot.success_rate - 88.89) < 0.1  # 80 / (80 + 10)
    
    def test_snapshot_to_dict(self):
        """Test converting snapshot to dict."""
        snapshot = ProgressSnapshot(
            total_items=100,
            completed_items=50,
            in_progress_items=25,
            failed_items=25
        )
        data = snapshot.to_dict()
        assert data["total_items"] == 100
        assert data["completed_items"] == 50
        assert "completion_percentage" in data


class TestProgressAggregator:
    """Test progress aggregator."""
    
    def test_update_stage_progress(self, progress_aggregator):
        """Test updating stage progress."""
        snapshot = progress_aggregator.update_stage_progress(
            "stage1", 100, 50, 25, 25
        )
        assert snapshot.completed_items == 50
        assert len(progress_aggregator.history) == 1
    
    def test_aggregate_progress_single_stage(self, progress_aggregator):
        """Test aggregating single stage."""
        progress_aggregator.update_stage_progress("stage1", 100, 50, 25, 25)
        aggregate = progress_aggregator.get_aggregate_progress()
        assert aggregate.total_items == 100
        assert aggregate.completed_items == 50
    
    def test_aggregate_progress_multiple_stages(self, progress_aggregator):
        """Test aggregating multiple stages."""
        progress_aggregator.update_stage_progress("stage1", 100, 50, 25, 25)
        progress_aggregator.update_stage_progress("stage2", 50, 30, 10, 10)
        
        aggregate = progress_aggregator.get_aggregate_progress()
        assert aggregate.total_items == 150
        assert aggregate.completed_items == 80
        assert aggregate.in_progress_items == 35
        assert aggregate.failed_items == 35
    
    def test_get_stage_progress(self, progress_aggregator):
        """Test getting specific stage progress."""
        progress_aggregator.update_stage_progress("stage1", 100, 50, 25, 25)
        snapshot = progress_aggregator.get_stage_progress("stage1")
        assert snapshot is not None
        assert snapshot.completed_items == 50
    
    def test_get_nonexistent_stage(self, progress_aggregator):
        """Test getting nonexistent stage."""
        snapshot = progress_aggregator.get_stage_progress("nonexistent")
        assert snapshot is None
    
    def test_get_all_stages(self, progress_aggregator):
        """Test getting all stages."""
        progress_aggregator.update_stage_progress("stage1", 100, 50, 25, 25)
        progress_aggregator.update_stage_progress("stage2", 50, 30, 10, 10)
        
        stages = progress_aggregator.get_all_stages()
        assert len(stages) == 2
        assert "stage1" in stages
        assert "stage2" in stages


class TestDashboardService:
    """Test dashboard service."""
    
    def test_dashboard_starts_stopped(self, dashboard):
        """Test dashboard starts in stopped state."""
        assert dashboard.status == DashboardStatus.STOPPED
    
    def test_dashboard_start(self, dashboard):
        """Test starting dashboard."""
        dashboard.start()
        assert dashboard.status == DashboardStatus.RUNNING
        assert dashboard.metrics.current_status == DashboardStatus.RUNNING
    
    def test_dashboard_pause(self, dashboard):
        """Test pausing dashboard."""
        dashboard.start()
        dashboard.pause()
        assert dashboard.status == DashboardStatus.PAUSED
    
    def test_dashboard_stop(self, dashboard):
        """Test stopping dashboard."""
        dashboard.start()
        dashboard.stop()
        assert dashboard.status == DashboardStatus.STOPPED
    
    def test_update_progress_when_running(self, dashboard):
        """Test updating progress when dashboard is running."""
        dashboard.start()
        dashboard.update_progress("stage1", 100, 50, 25, 25)
        
        aggregate = dashboard.aggregator.get_aggregate_progress()
        assert aggregate.completed_items == 50
    
    def test_update_progress_when_stopped(self, dashboard):
        """Test updating progress when dashboard is stopped."""
        dashboard.update_progress("stage1", 100, 50, 25, 25)
        
        # Should not update
        aggregate = dashboard.aggregator.get_aggregate_progress()
        assert aggregate.completed_items == 0
    
    def test_get_dashboard_data(self, dashboard):
        """Test getting dashboard data."""
        dashboard.start()
        dashboard.update_progress("stage1", 100, 50, 25, 25)
        
        data = dashboard.get_dashboard_data()
        assert "status" in data
        assert data["status"] == "running"
        assert "aggregate_progress" in data
        assert "stages" in data
    
    def test_set_estimated_completion(self, dashboard):
        """Test setting estimated completion time."""
        completion_time = datetime.utcnow() + timedelta(hours=1)
        dashboard.set_estimated_completion(completion_time)
        assert dashboard.metrics.estimated_completion_time == completion_time
    
    def test_get_summary(self, dashboard):
        """Test getting dashboard summary."""
        dashboard.start()
        dashboard.update_progress("stage1", 100, 50, 25, 25)
        
        summary = dashboard.get_summary()
        assert "50/100" in summary
        assert "complete" in summary
        assert "failed" in summary


# ============================================================================
# ALERT MANAGER TESTS
# ============================================================================

@pytest.fixture
def threshold_monitor():
    """Create a threshold monitor."""
    return ThresholdMonitor()


@pytest.fixture
def alert_manager():
    """Create an alert manager."""
    return AlertManager()


class TestThresholdRule:
    """Test threshold rule."""
    
    def test_rule_greater_than(self):
        """Test greater than rule."""
        rule = ThresholdRule(
            rule_id="rule1",
            name="High CPU",
            metric_name="cpu.usage",
            threshold_value=80,
            operator=">",
            severity=AlertSeverity.WARNING
        )
        assert rule.check(85)
        assert not rule.check(75)
    
    def test_rule_less_than(self):
        """Test less than rule."""
        rule = ThresholdRule(
            rule_id="rule1",
            name="Low Memory",
            metric_name="memory.free",
            threshold_value=10,
            operator="<",
            severity=AlertSeverity.ERROR
        )
        assert rule.check(5)
        assert not rule.check(15)
    
    def test_rule_equals(self):
        """Test equals rule."""
        rule = ThresholdRule(
            rule_id="rule1",
            name="Status Check",
            metric_name="status.code",
            threshold_value=0,
            operator="==",
            severity=AlertSeverity.INFO
        )
        assert rule.check(0)
        assert not rule.check(1)
    
    def test_rule_disabled(self):
        """Test disabled rule."""
        rule = ThresholdRule(
            rule_id="rule1",
            name="Disabled Rule",
            metric_name="test.metric",
            threshold_value=50,
            operator=">",
            severity=AlertSeverity.WARNING,
            enabled=False
        )
        assert not rule.check(75)  # Should return False even though 75 > 50
    
    def test_format_message(self):
        """Test message formatting."""
        rule = ThresholdRule(
            rule_id="rule1",
            name="High CPU",
            metric_name="cpu.usage",
            threshold_value=80,
            operator=">",
            severity=AlertSeverity.WARNING,
            message_template="Alert: {metric} {op} {threshold}"
        )
        message = rule.format_message(85)
        assert "cpu.usage" in message
        assert ">" in message
        assert "80" in message


class TestAlert:
    """Test alert."""
    
    def test_alert_creation(self):
        """Test creating alert."""
        alert = Alert(
            alert_id="alert1",
            rule_name="test_rule",
            message="Test alert",
            severity=AlertSeverity.WARNING
        )
        assert alert.state == AlertState.ACTIVE
        assert alert.triggered_at is not None
    
    def test_alert_to_dict(self):
        """Test converting alert to dict."""
        alert = Alert(
            alert_id="alert1",
            rule_name="test_rule",
            message="Test alert",
            severity=AlertSeverity.WARNING,
            metric_value=85,
            threshold_value=80
        )
        data = alert.to_dict()
        assert data["alert_id"] == "alert1"
        assert data["severity"] == "warning"
        assert data["state"] == "active"


class TestThresholdMonitor:
    """Test threshold monitor."""
    
    def test_register_rule(self, threshold_monitor):
        """Test registering rule."""
        rule = ThresholdRule(
            rule_id="rule1",
            name="High CPU",
            metric_name="cpu.usage",
            threshold_value=80,
            operator=">",
            severity=AlertSeverity.WARNING
        )
        threshold_monitor.register_rule(rule)
        assert "rule1" in threshold_monitor.rules
    
    def test_check_metric_triggers_alert(self, threshold_monitor):
        """Test checking metric triggers alert."""
        rule = ThresholdRule(
            rule_id="rule1",
            name="High CPU",
            metric_name="cpu.usage",
            threshold_value=80,
            operator=">",
            severity=AlertSeverity.WARNING
        )
        threshold_monitor.register_rule(rule)
        
        alerts = threshold_monitor.check_metric("cpu.usage", 85)
        assert len(alerts) == 1
        assert alerts[0].rule_name == "High CPU"
    
    def test_check_metric_no_alert(self, threshold_monitor):
        """Test checking metric doesn't trigger alert."""
        rule = ThresholdRule(
            rule_id="rule1",
            name="High CPU",
            metric_name="cpu.usage",
            threshold_value=80,
            operator=">",
            severity=AlertSeverity.WARNING
        )
        threshold_monitor.register_rule(rule)
        
        alerts = threshold_monitor.check_metric("cpu.usage", 75)
        assert len(alerts) == 0
    
    def test_get_active_alerts(self, threshold_monitor):
        """Test getting active alerts."""
        rule = ThresholdRule(
            rule_id="rule1",
            name="High CPU",
            metric_name="cpu.usage",
            threshold_value=80,
            operator=">",
            severity=AlertSeverity.WARNING
        )
        threshold_monitor.register_rule(rule)
        threshold_monitor.check_metric("cpu.usage", 85)
        
        active = threshold_monitor.get_active_alerts()
        assert len(active) == 1
    
    def test_resolve_alert(self, threshold_monitor):
        """Test resolving alert."""
        rule = ThresholdRule(
            rule_id="rule1",
            name="High CPU",
            metric_name="cpu.usage",
            threshold_value=80,
            operator=">",
            severity=AlertSeverity.WARNING
        )
        threshold_monitor.register_rule(rule)
        alerts = threshold_monitor.check_metric("cpu.usage", 85)
        
        assert len(threshold_monitor.get_active_alerts()) == 1
        threshold_monitor.resolve_alert(alerts[0].alert_id)
        assert len(threshold_monitor.get_active_alerts()) == 0
    
    def test_disable_enable_rule(self, threshold_monitor):
        """Test disabling and enabling rules."""
        rule = ThresholdRule(
            rule_id="rule1",
            name="High CPU",
            metric_name="cpu.usage",
            threshold_value=80,
            operator=">",
            severity=AlertSeverity.WARNING
        )
        threshold_monitor.register_rule(rule)
        
        threshold_monitor.disable_rule("rule1")
        alerts = threshold_monitor.check_metric("cpu.usage", 85)
        assert len(alerts) == 0
        
        threshold_monitor.enable_rule("rule1")
        alerts = threshold_monitor.check_metric("cpu.usage", 85)
        assert len(alerts) == 1


class TestAlertManager:
    """Test alert manager."""
    
    def test_add_rule(self, alert_manager):
        """Test adding rule."""
        rule = ThresholdRule(
            rule_id="rule1",
            name="High CPU",
            metric_name="cpu.usage",
            threshold_value=80,
            operator=">",
            severity=AlertSeverity.WARNING
        )
        alert_manager.add_rule(rule)
        assert "rule1" in alert_manager.monitor.rules
    
    def test_register_alert_handler(self, alert_manager):
        """Test registering alert handler."""
        handled_alerts = []
        
        def handler(alert: Alert):
            handled_alerts.append(alert)
        
        alert_manager.register_alert_handler(handler)
        assert len(alert_manager.handlers) == 1
    
    def test_check_metric_with_handler(self, alert_manager):
        """Test checking metric triggers handler."""
        handled_alerts = []
        
        def handler(alert: Alert):
            handled_alerts.append(alert)
        
        alert_manager.register_alert_handler(handler)
        
        rule = ThresholdRule(
            rule_id="rule1",
            name="High CPU",
            metric_name="cpu.usage",
            threshold_value=80,
            operator=">",
            severity=AlertSeverity.WARNING
        )
        alert_manager.add_rule(rule)
        
        alert_manager.check_metric("cpu.usage", 85)
        assert len(handled_alerts) == 1
    
    def test_mute_rule(self, alert_manager):
        """Test muting rule."""
        handled_alerts = []
        
        def handler(alert: Alert):
            handled_alerts.append(alert)
        
        alert_manager.register_alert_handler(handler)
        
        rule = ThresholdRule(
            rule_id="rule1",
            name="High CPU",
            metric_name="cpu.usage",
            threshold_value=80,
            operator=">",
            severity=AlertSeverity.WARNING
        )
        alert_manager.add_rule(rule)
        
        # Mute until future time
        mute_until = datetime.utcnow() + timedelta(hours=1)
        alert_manager.mute_rule("High CPU", mute_until)
        
        alert_manager.check_metric("cpu.usage", 85)
        # Alert should be checked but not dispatched
        assert len(handled_alerts) == 0
    
    def test_unmute_rule(self, alert_manager):
        """Test unmuting rule."""
        handled_alerts = []
        
        def handler(alert: Alert):
            handled_alerts.append(alert)
        
        alert_manager.register_alert_handler(handler)
        
        rule = ThresholdRule(
            rule_id="rule1",
            name="High CPU",
            metric_name="cpu.usage",
            threshold_value=80,
            operator=">",
            severity=AlertSeverity.WARNING
        )
        alert_manager.add_rule(rule)
        
        # Mute then unmute
        mute_until = datetime.utcnow() + timedelta(hours=1)
        alert_manager.mute_rule("High CPU", mute_until)
        alert_manager.unmute_rule("High CPU")
        
        alert_manager.check_metric("cpu.usage", 85)
        assert len(handled_alerts) == 1
    
    def test_get_active_alerts(self, alert_manager):
        """Test getting active alerts."""
        rule = ThresholdRule(
            rule_id="rule1",
            name="High CPU",
            metric_name="cpu.usage",
            threshold_value=80,
            operator=">",
            severity=AlertSeverity.WARNING
        )
        alert_manager.add_rule(rule)
        alert_manager.check_metric("cpu.usage", 85)
        
        active = alert_manager.get_active_alerts()
        assert len(active) == 1
    
    def test_resolve_alert(self, alert_manager):
        """Test resolving alert."""
        rule = ThresholdRule(
            rule_id="rule1",
            name="High CPU",
            metric_name="cpu.usage",
            threshold_value=80,
            operator=">",
            severity=AlertSeverity.WARNING
        )
        alert_manager.add_rule(rule)
        alerts = alert_manager.check_metric("cpu.usage", 85)
        
        alert_manager.resolve_alert(alerts[0].alert_id)
        active = alert_manager.get_active_alerts()
        assert len(active) == 0
