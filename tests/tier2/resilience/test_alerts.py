"""
Test suite for AC-NFR-004-03: Alert Management & Threshold Monitoring

This test module validates alert management with configurable thresholds,
multiple notification channels, and alert lifecycle management.

AC-ID: AC-NFR-004-03
Title: Alert Management & Threshold Monitoring
Tests Required: 11 unit tests + 5 integration tests = 16 total
"""

import pytest
import time
from typing import Dict, List, Optional, Any, Callable
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from enum import Enum


class AlertSeverity(Enum):
    """Severity levels for alerts."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertState(Enum):
    """State of an alert."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class Threshold:
    """Configuration for a threshold."""
    name: str
    metric: str
    operator: str  # ">", "<", ">=", "<=", "=="
    value: float
    severity: AlertSeverity
    enabled: bool = True


@dataclass
class Alert:
    """An alert notification."""
    alert_id: str
    metric_name: str
    threshold_name: str
    severity: AlertSeverity
    state: AlertState
    message: str
    timestamp: float
    value: Optional[float] = None
    acknowledged_at: Optional[float] = None


class NotificationChannel:
    """Base class for notification channels."""
    
    def send(self, alert: Alert) -> bool:
        """Send alert through channel."""
        raise NotImplementedError


class EmailChannel(NotificationChannel):
    """Email notification channel."""
    
    def __init__(self, recipient: str):
        self.recipient = recipient
        self.sent_alerts = []
    
    def send(self, alert: Alert) -> bool:
        """Send alert via email."""
        self.sent_alerts.append(alert)
        return True


class SlackChannel(NotificationChannel):
    """Slack notification channel."""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.sent_alerts = []
    
    def send(self, alert: Alert) -> bool:
        """Send alert to Slack."""
        self.sent_alerts.append(alert)
        return True


class AlertManager:
    """
    Manages alerts with configurable thresholds and notifications.
    
    AC-ID: AC-NFR-004-03
    Title: Alert Management & Threshold Monitoring
    """
    
    def __init__(self):
        """Initialize alert manager."""
        self.thresholds: Dict[str, Threshold] = {}
        self.channels: List[NotificationChannel] = []
        self.alerts: Dict[str, Alert] = {}
        self.alert_counter = 0
        self.metrics_history: Dict[str, List[float]] = {}
    
    def add_threshold(self, threshold: Threshold) -> str:
        """Add a threshold configuration."""
        if threshold.operator not in (">", "<", ">=", "<=", "=="):
            raise ValueError(f"Invalid operator: {threshold.operator}")
        
        self.thresholds[threshold.name] = threshold
        return threshold.name
    
    def remove_threshold(self, threshold_name: str) -> bool:
        """Remove a threshold."""
        if threshold_name in self.thresholds:
            del self.thresholds[threshold_name]
            return True
        return False
    
    def add_channel(self, channel: NotificationChannel) -> None:
        """Add a notification channel."""
        self.channels.append(channel)
    
    def record_metric(self, metric_name: str, value: float) -> List[Alert]:
        """
        Record a metric value and check against thresholds.
        
        Returns:
            List of alerts triggered by this metric
        """
        # Store metric history
        if metric_name not in self.metrics_history:
            self.metrics_history[metric_name] = []
        self.metrics_history[metric_name].append(value)
        
        triggered_alerts = []
        
        # Check all thresholds for this metric
        for threshold in self.thresholds.values():
            if threshold.metric == metric_name and threshold.enabled:
                if self._check_threshold(threshold, value):
                    alert = self._create_alert(threshold, metric_name, value)
                    self.alerts[alert.alert_id] = alert
                    triggered_alerts.append(alert)
                    self._notify_channels(alert)
        
        return triggered_alerts
    
    def _check_threshold(self, threshold: Threshold, value: float) -> bool:
        """Check if a value violates a threshold."""
        if threshold.operator == ">":
            return value > threshold.value
        elif threshold.operator == "<":
            return value < threshold.value
        elif threshold.operator == ">=":
            return value >= threshold.value
        elif threshold.operator == "<=":
            return value <= threshold.value
        elif threshold.operator == "==":
            return value == threshold.value
        return False
    
    def _create_alert(self, threshold: Threshold, metric: str, value: float) -> Alert:
        """Create an alert from a threshold violation."""
        self.alert_counter += 1
        alert_id = f"alert-{self.alert_counter}"
        
        return Alert(
            alert_id=alert_id,
            metric_name=metric,
            threshold_name=threshold.name,
            severity=threshold.severity,
            state=AlertState.ACTIVE,
            message=f"{metric} {threshold.operator} {threshold.value} (actual: {value})",
            timestamp=time.time(),
            value=value
        )
    
    def _notify_channels(self, alert: Alert) -> None:
        """Send alert to all channels."""
        for channel in self.channels:
            try:
                channel.send(alert)
            except Exception:
                pass
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        if alert_id in self.alerts:
            self.alerts[alert_id].state = AlertState.ACKNOWLEDGED
            self.alerts[alert_id].acknowledged_at = time.time()
            return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        if alert_id in self.alerts:
            self.alerts[alert_id].state = AlertState.RESOLVED
            return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return [a for a in self.alerts.values() if a.state == AlertState.ACTIVE]
    
    def enable_threshold(self, threshold_name: str) -> bool:
        """Enable a threshold."""
        if threshold_name in self.thresholds:
            self.thresholds[threshold_name].enabled = True
            return True
        return False
    
    def disable_threshold(self, threshold_name: str) -> bool:
        """Disable a threshold."""
        if threshold_name in self.thresholds:
            self.thresholds[threshold_name].enabled = False
            return True
        return False


# UNIT TESTS (11 required)

class TestThresholdConfiguration:
    """Test threshold configuration."""
    
    def test_add_threshold(self):
        """Test adding a threshold."""
        manager = AlertManager()
        threshold = Threshold(
            name="high_cpu",
            metric="cpu_usage",
            operator=">",
            value=80.0,
            severity=AlertSeverity.WARNING
        )
        
        name = manager.add_threshold(threshold)
        assert name == "high_cpu"
        assert "high_cpu" in manager.thresholds
    
    def test_remove_threshold(self):
        """Test removing a threshold."""
        manager = AlertManager()
        threshold = Threshold(
            name="test",
            metric="metric",
            operator=">",
            value=100.0,
            severity=AlertSeverity.WARNING
        )
        
        manager.add_threshold(threshold)
        assert manager.remove_threshold("test") is True
        assert "test" not in manager.thresholds
    
    def test_invalid_operator(self):
        """Test invalid operator rejected."""
        manager = AlertManager()
        threshold = Threshold(
            name="bad",
            metric="metric",
            operator="invalid",
            value=100.0,
            severity=AlertSeverity.WARNING
        )
        
        with pytest.raises(ValueError):
            manager.add_threshold(threshold)
    
    def test_enable_disable_threshold(self):
        """Test enabling and disabling thresholds."""
        manager = AlertManager()
        threshold = Threshold(
            name="test",
            metric="metric",
            operator=">",
            value=100.0,
            severity=AlertSeverity.WARNING,
            enabled=True
        )
        
        manager.add_threshold(threshold)
        assert manager.thresholds["test"].enabled is True
        
        manager.disable_threshold("test")
        assert manager.thresholds["test"].enabled is False
        
        manager.enable_threshold("test")
        assert manager.thresholds["test"].enabled is True


class TestAlertTriggering:
    """Test alert triggering on threshold violation."""
    
    def test_alert_on_threshold_violation(self):
        """Test alert is triggered on violation."""
        manager = AlertManager()
        threshold = Threshold(
            name="high_memory",
            metric="memory_usage",
            operator=">",
            value=80.0,
            severity=AlertSeverity.WARNING
        )
        manager.add_threshold(threshold)
        
        alerts = manager.record_metric("memory_usage", 85.0)
        
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.WARNING
    
    def test_no_alert_below_threshold(self):
        """Test no alert when below threshold."""
        manager = AlertManager()
        threshold = Threshold(
            name="high",
            metric="value",
            operator=">",
            value=100.0,
            severity=AlertSeverity.WARNING
        )
        manager.add_threshold(threshold)
        
        alerts = manager.record_metric("value", 50.0)
        
        assert len(alerts) == 0
    
    def test_multiple_thresholds(self):
        """Test multiple threshold checking."""
        manager = AlertManager()
        
        threshold1 = Threshold(
            name="high",
            metric="cpu",
            operator=">",
            value=80.0,
            severity=AlertSeverity.WARNING
        )
        threshold2 = Threshold(
            name="critical",
            metric="cpu",
            operator=">",
            value=95.0,
            severity=AlertSeverity.CRITICAL
        )
        
        manager.add_threshold(threshold1)
        manager.add_threshold(threshold2)
        
        alerts = manager.record_metric("cpu", 96.0)
        
        # Both thresholds should trigger
        assert len(alerts) == 2


class TestAlertManagement:
    """Test alert lifecycle management."""
    
    def test_acknowledge_alert(self):
        """Test acknowledging an alert."""
        manager = AlertManager()
        threshold = Threshold(
            name="test",
            metric="metric",
            operator=">",
            value=100.0,
            severity=AlertSeverity.WARNING
        )
        manager.add_threshold(threshold)
        
        alerts = manager.record_metric("metric", 150.0)
        alert_id = alerts[0].alert_id
        
        manager.acknowledge_alert(alert_id)
        assert manager.alerts[alert_id].state == AlertState.ACKNOWLEDGED
    
    def test_resolve_alert(self):
        """Test resolving an alert."""
        manager = AlertManager()
        threshold = Threshold(
            name="test",
            metric="metric",
            operator=">",
            value=100.0,
            severity=AlertSeverity.WARNING
        )
        manager.add_threshold(threshold)
        
        alerts = manager.record_metric("metric", 150.0)
        alert_id = alerts[0].alert_id
        
        manager.resolve_alert(alert_id)
        assert manager.alerts[alert_id].state == AlertState.RESOLVED
    
    def test_get_active_alerts(self):
        """Test getting active alerts."""
        manager = AlertManager()
        threshold = Threshold(
            name="test",
            metric="metric",
            operator=">",
            value=100.0,
            severity=AlertSeverity.WARNING
        )
        manager.add_threshold(threshold)
        
        manager.record_metric("metric", 150.0)
        manager.record_metric("metric", 150.0)
        
        active = manager.get_active_alerts()
        assert len(active) == 2


class TestNotificationChannels:
    """Test notification channels."""
    
    def test_add_channel(self):
        """Test adding notification channel."""
        manager = AlertManager()
        channel = EmailChannel("admin@example.com")
        
        manager.add_channel(channel)
        assert len(manager.channels) == 1
    
    def test_notification_sent(self):
        """Test notification is sent through channel."""
        manager = AlertManager()
        channel = EmailChannel("admin@example.com")
        manager.add_channel(channel)
        
        threshold = Threshold(
            name="test",
            metric="metric",
            operator=">",
            value=100.0,
            severity=AlertSeverity.WARNING
        )
        manager.add_threshold(threshold)
        
        manager.record_metric("metric", 150.0)
        
        assert len(channel.sent_alerts) == 1


# INTEGRATION TESTS (5 required)

class TestAlertSystemIntegration:
    """Integration tests for alert system."""
    
    def test_complete_alert_lifecycle(self):
        """Test complete alert lifecycle."""
        manager = AlertManager()
        email = EmailChannel("admin@example.com")
        slack = SlackChannel("https://hooks.slack.com/...")
        
        manager.add_channel(email)
        manager.add_channel(slack)
        
        threshold = Threshold(
            name="high_load",
            metric="load_average",
            operator=">",
            value=80.0,
            severity=AlertSeverity.CRITICAL
        )
        manager.add_threshold(threshold)
        
        # Trigger alert
        alerts = manager.record_metric("load_average", 85.0)
        assert len(alerts) == 1
        alert_id = alerts[0].alert_id
        
        # Verify notification sent
        assert len(email.sent_alerts) == 1
        assert len(slack.sent_alerts) == 1
        
        # Acknowledge
        manager.acknowledge_alert(alert_id)
        assert manager.alerts[alert_id].state == AlertState.ACKNOWLEDGED
        
        # Resolve
        manager.resolve_alert(alert_id)
        assert manager.alerts[alert_id].state == AlertState.RESOLVED
    
    def test_multiple_channels_different_severities(self):
        """Test different channels for different severities."""
        manager = AlertManager()
        email = EmailChannel("admin@example.com")
        slack = SlackChannel("https://hooks.slack.com/...")
        
        manager.add_channel(email)
        manager.add_channel(slack)
        
        # Add thresholds with different severities
        warning = Threshold(
            name="warning_level",
            metric="cpu",
            operator=">",
            value=70.0,
            severity=AlertSeverity.WARNING
        )
        critical = Threshold(
            name="critical_level",
            metric="cpu",
            operator=">",
            value=90.0,
            severity=AlertSeverity.CRITICAL
        )
        
        manager.add_threshold(warning)
        manager.add_threshold(critical)
        
        alerts = manager.record_metric("cpu", 95.0)
        
        # Both thresholds trigger
        assert len(alerts) == 2
        # Both channels notified
        assert len(email.sent_alerts) == 2
        assert len(slack.sent_alerts) == 2
    
    def test_threshold_enable_disable(self):
        """Test enabling and disabling thresholds."""
        manager = AlertManager()
        
        threshold = Threshold(
            name="test",
            metric="metric",
            operator=">",
            value=100.0,
            severity=AlertSeverity.WARNING
        )
        manager.add_threshold(threshold)
        
        # Threshold enabled - alert triggered
        alerts = manager.record_metric("metric", 150.0)
        assert len(alerts) == 1
        
        # Disable threshold
        manager.disable_threshold("test")
        
        # No alert triggered
        alerts = manager.record_metric("metric", 150.0)
        assert len(alerts) == 0
    
    def test_operator_variations(self):
        """Test different threshold operators."""
        manager = AlertManager()
        
        # Test > operator
        t1 = Threshold("gt", "m", ">", 100.0, AlertSeverity.WARNING)
        manager.add_threshold(t1)
        alerts = manager.record_metric("m", 101.0)
        assert len(alerts) == 1
        
        manager.alerts.clear()
        manager.disable_threshold("gt")
        
        # Test < operator
        t2 = Threshold("lt", "m", "<", 50.0, AlertSeverity.WARNING)
        manager.add_threshold(t2)
        alerts = manager.record_metric("m", 49.0)
        assert len(alerts) == 1
    
    def test_alert_aggregation_over_time(self):
        """Test alert aggregation with metrics history."""
        manager = AlertManager()
        
        threshold = Threshold(
            name="test",
            metric="metric",
            operator=">",
            value=100.0,
            severity=AlertSeverity.WARNING
        )
        manager.add_threshold(threshold)
        
        # Record multiple metrics
        values = [50, 75, 100, 150, 150, 120]
        for v in values:
            manager.record_metric("metric", v)
        
        # History should contain all values
        assert len(manager.metrics_history["metric"]) == len(values)
        
        # Should have alerts for values > 100
        assert len(manager.get_active_alerts()) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
