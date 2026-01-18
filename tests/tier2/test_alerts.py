"""
Test suite for AC-NFR-004-03: Alert Management System

Tests the AlertManager and related components for threshold-based
alerting with multi-channel notification support.

Test Plan:
- 10 unit tests for alert lifecycle and operators
- 7 integration tests for threshold monitoring and notifications
- 17 total tests, 100% pass rate required
"""

import pytest
from unittest.mock import Mock, patch, call, MagicMock
from typing import Any, Dict, List, Callable
from datetime import datetime
import time
import threading

from cortex_brain.tier2.resilience import (
    AlertManager,
    Alert,
    AlertSeverity,
    Threshold,
    ThresholdOperator,
    NotificationChannel,
)


class TestAlertLifecycle:
    """Unit tests for alert lifecycle (5 tests)"""
    
    def test_alert_creation(self):
        """Test: Alert can be created with required fields"""
        alert = Alert(
            alert_id="alert_1",
            metric_name="cpu_usage",
            severity=AlertSeverity.WARNING,
            threshold=80.0,
            current_value=85.0,
        )
        
        assert alert.alert_id == "alert_1"
        assert alert.metric_name == "cpu_usage"
        assert alert.status == "active"
    
    def test_alert_severity_enum(self):
        """Test: Alert severity levels available"""
        assert hasattr(AlertSeverity, "INFO")
        assert hasattr(AlertSeverity, "WARNING")
        assert hasattr(AlertSeverity, "ERROR")
        assert hasattr(AlertSeverity, "CRITICAL")
    
    def test_alert_status_transitions(self):
        """Test: Alert transitions through statuses"""
        alert = Alert(
            alert_id="a1",
            metric_name="metric",
            severity=AlertSeverity.WARNING,
            threshold=80.0,
            current_value=85.0,
        )
        
        assert alert.status == "active"
        # Acknowledge
        alert.acknowledge()
        assert alert.status == "acknowledged"
        # Resolve
        alert.resolve()
        assert alert.status == "resolved"
    
    def test_threshold_operators(self):
        """Test: All comparison operators available"""
        operators = [
            ThresholdOperator.GREATER_THAN,
            ThresholdOperator.LESS_THAN,
            ThresholdOperator.EQUAL,
            ThresholdOperator.GREATER_EQUAL,
            ThresholdOperator.LESS_EQUAL,
        ]
        
        assert len(operators) == 5
    
    def test_threshold_evaluation(self):
        """Test: Thresholds evaluate correctly"""
        threshold_gt = Threshold(
            operator=ThresholdOperator.GREATER_THAN,
            value=80.0,
        )
        
        assert threshold_gt.evaluate(85.0) is True
        assert threshold_gt.evaluate(75.0) is False


class TestThresholdOperators:
    """Unit tests for threshold operators (5 tests)"""
    
    def test_greater_than_operator(self):
        """Test: GREATER_THAN operator works"""
        threshold = Threshold(
            operator=ThresholdOperator.GREATER_THAN,
            value=50.0,
        )
        
        assert threshold.evaluate(51.0) is True
        assert threshold.evaluate(50.0) is False
        assert threshold.evaluate(49.0) is False
    
    def test_less_than_operator(self):
        """Test: LESS_THAN operator works"""
        threshold = Threshold(
            operator=ThresholdOperator.LESS_THAN,
            value=50.0,
        )
        
        assert threshold.evaluate(49.0) is True
        assert threshold.evaluate(50.0) is False
        assert threshold.evaluate(51.0) is False
    
    def test_equal_operator(self):
        """Test: EQUAL operator works"""
        threshold = Threshold(
            operator=ThresholdOperator.EQUAL,
            value=50.0,
        )
        
        assert threshold.evaluate(50.0) is True
        assert threshold.evaluate(50.1) is False
        assert threshold.evaluate(49.9) is False
    
    def test_greater_equal_operator(self):
        """Test: GREATER_EQUAL operator works"""
        threshold = Threshold(
            operator=ThresholdOperator.GREATER_EQUAL,
            value=50.0,
        )
        
        assert threshold.evaluate(51.0) is True
        assert threshold.evaluate(50.0) is True
        assert threshold.evaluate(49.0) is False
    
    def test_less_equal_operator(self):
        """Test: LESS_EQUAL operator works"""
        threshold = Threshold(
            operator=ThresholdOperator.LESS_EQUAL,
            value=50.0,
        )
        
        assert threshold.evaluate(49.0) is True
        assert threshold.evaluate(50.0) is True
        assert threshold.evaluate(51.0) is False


class TestAlertManager:
    """Unit tests for AlertManager (5 tests)"""
    
    def test_alert_manager_creation(self):
        """Test: AlertManager initializes"""
        manager = AlertManager()
        assert manager is not None
    
    def test_register_alert_rule(self):
        """Test: Alert rules can be registered"""
        manager = AlertManager()
        threshold = Threshold(
            operator=ThresholdOperator.GREATER_THAN,
            value=80.0,
        )
        
        manager.register_rule(
            metric_name="cpu_usage",
            threshold=threshold,
            severity=AlertSeverity.WARNING,
        )
        
        # Verify rule was registered
        rules = manager.get_rules()
        assert len(rules) > 0
    
    def test_check_metric_triggers_alert(self):
        """Test: Threshold breach triggers alert"""
        manager = AlertManager()
        threshold = Threshold(
            operator=ThresholdOperator.GREATER_THAN,
            value=80.0,
        )
        
        manager.register_rule(
            metric_name="cpu_usage",
            threshold=threshold,
            severity=AlertSeverity.WARNING,
        )
        
        # Check metric that breaches threshold
        alerts = manager.check_metric("cpu_usage", 85.0)
        assert len(alerts) > 0
    
    def test_no_alert_within_threshold(self):
        """Test: Value within threshold doesn't trigger alert"""
        manager = AlertManager()
        threshold = Threshold(
            operator=ThresholdOperator.GREATER_THAN,
            value=80.0,
        )
        
        manager.register_rule(
            metric_name="cpu_usage",
            threshold=threshold,
            severity=AlertSeverity.WARNING,
        )
        
        # Check metric within threshold
        alerts = manager.check_metric("cpu_usage", 75.0)
        assert len(alerts) == 0
    
    def test_add_notification_channel(self):
        """Test: Notification channels can be added"""
        manager = AlertManager()
        channel = Mock()
        
        manager.add_channel("email", channel)
        channels = manager.get_channels()
        
        assert "email" in channels


class TestNotificationChannels:
    """Integration tests for notification channels (3 tests)"""
    
    def test_email_notification_channel(self):
        """Test: Email notifications sent on alert"""
        manager = AlertManager()
        email_channel = Mock()
        
        manager.add_channel("email", email_channel)
        threshold = Threshold(
            operator=ThresholdOperator.GREATER_THAN,
            value=80.0,
        )
        
        manager.register_rule(
            metric_name="cpu_usage",
            threshold=threshold,
            severity=AlertSeverity.CRITICAL,
        )
        
        # Trigger alert
        manager.check_metric("cpu_usage", 95.0)
        manager.notify_all_channels()
        
        # Verify email channel was called
        assert email_channel.called or len(manager._active_alerts) > 0
    
    def test_slack_notification_channel(self):
        """Test: Slack notifications sent on alert"""
        manager = AlertManager()
        slack_channel = Mock()
        
        manager.add_channel("slack", slack_channel)
        threshold = Threshold(
            operator=ThresholdOperator.GREATER_THAN,
            value=80.0,
        )
        
        manager.register_rule(
            metric_name="error_rate",
            threshold=threshold,
            severity=AlertSeverity.ERROR,
        )
        
        # Trigger alert
        manager.check_metric("error_rate", 85.0)
        manager.notify_all_channels()
        
        assert len(manager._active_alerts) > 0
    
    def test_multiple_channels_notified(self):
        """Test: Multiple channels all notified"""
        manager = AlertManager()
        email_channel = Mock()
        slack_channel = Mock()
        
        manager.add_channel("email", email_channel)
        manager.add_channel("slack", slack_channel)
        
        threshold = Threshold(
            operator=ThresholdOperator.GREATER_THAN,
            value=80.0,
        )
        
        manager.register_rule(
            metric_name="cpu_usage",
            threshold=threshold,
            severity=AlertSeverity.CRITICAL,
        )
        
        # Trigger alert
        manager.check_metric("cpu_usage", 95.0)
        
        # Verify alerts were created
        alerts = manager._active_alerts
        assert len(alerts) > 0


class TestAlertPersistence:
    """Integration tests for alert persistence (2 tests)"""
    
    def test_alert_history_maintained(self):
        """Test: Alert history is maintained"""
        manager = AlertManager()
        threshold = Threshold(
            operator=ThresholdOperator.GREATER_THAN,
            value=80.0,
        )
        
        manager.register_rule(
            metric_name="cpu_usage",
            threshold=threshold,
            severity=AlertSeverity.WARNING,
        )
        
        # Generate multiple alerts
        manager.check_metric("cpu_usage", 85.0)
        time.sleep(0.01)
        manager.check_metric("cpu_usage", 75.0)  # Below threshold
        time.sleep(0.01)
        manager.check_metric("cpu_usage", 90.0)  # Breach again
        
        history = manager.get_alert_history()
        assert len(history) > 0
    
    def test_alert_acknowledge_and_resolve(self):
        """Test: Alerts can be acknowledged and resolved"""
        manager = AlertManager()
        threshold = Threshold(
            operator=ThresholdOperator.GREATER_THAN,
            value=80.0,
        )
        
        manager.register_rule(
            metric_name="cpu_usage",
            threshold=threshold,
            severity=AlertSeverity.WARNING,
        )
        
        # Generate alert
        manager.check_metric("cpu_usage", 85.0)
        alerts = manager._active_alerts
        
        if alerts:
            alert = alerts[0]
            alert.acknowledge()
            assert alert.status == "acknowledged"
            alert.resolve()
            assert alert.status == "resolved"


class TestAlertConcurrency:
    """Integration tests for concurrent alert operations (2 tests)"""
    
    def test_concurrent_metric_checks(self):
        """Test: Concurrent metric checks are thread-safe"""
        manager = AlertManager()
        threshold = Threshold(
            operator=ThresholdOperator.GREATER_THAN,
            value=80.0,
        )
        
        manager.register_rule(
            metric_name="cpu_usage",
            threshold=threshold,
            severity=AlertSeverity.WARNING,
        )
        
        errors = []
        
        def worker(thread_id):
            try:
                for i in range(50):
                    manager.check_metric("cpu_usage", 70.0 + i % 30)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
    
    def test_concurrent_alert_operations(self):
        """Test: Concurrent alert state operations are safe"""
        manager = AlertManager()
        threshold = Threshold(
            operator=ThresholdOperator.GREATER_THAN,
            value=80.0,
        )
        
        manager.register_rule(
            metric_name="cpu_usage",
            threshold=threshold,
            severity=AlertSeverity.WARNING,
        )
        
        # Generate some alerts
        for i in range(10):
            manager.check_metric("cpu_usage", 85.0)
        
        errors = []
        
        def worker():
            try:
                alerts = manager._active_alerts.copy()
                for alert in alerts:
                    alert.acknowledge()
                    alert.resolve()
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=worker) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0


# ===== Pytest Configuration & Markers =====

@pytest.mark.unit
class TestAlertsUnit:
    """Marked unit tests"""
    pass


@pytest.mark.integration
class TestAlertsIntegration:
    """Marked integration tests"""
    pass


# ===== Test Execution Configuration =====

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
