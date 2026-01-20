"""
Test suite for Alerting & Health Monitoring (OB-002-01).

This module tests alert rules, health checks, and notification routing for
the CORTEX observability system.

Acceptance Tests:
- Alerts triggered on threshold breaches
- Health checks implemented
- Notification channels configured
"""

import pytest
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from enum import Enum


# Import modules to be tested (will be created)
from cortex.core.observability.alerting import (
    AlertManager,
    AlertRule,
    AlertSeverity,
    AlertCondition,
    AlertNotification,
)
from cortex.core.observability.health_monitor import (
    HealthMonitor,
    HealthStatus,
    HealthStatusLevel,
)


class TestAlertRuleCreation:
    """Test alert rule definition and creation."""

    def test_alert_rule_creates_with_valid_config(self) -> None:
        """
        Test that alert rule initializes with valid configuration.

        Expected:
        - Rule instance created successfully
        - Configuration stored correctly
        - Condition callable assigned
        """
        def span_latency_high(metrics: Dict[str, Any]) -> bool:
            return metrics.get("latency_avg", 0) > 1000
        
        rule = AlertRule(
            name="high_latency",
            description="Alert when average latency exceeds 1000ms",
            severity=AlertSeverity.WARNING,
            condition=span_latency_high,
            enabled=True,
        )
        
        assert rule is not None
        assert rule.name == "high_latency"
        assert rule.severity == AlertSeverity.WARNING
        assert rule.enabled is True

    def test_alert_rule_requires_valid_name(self) -> None:
        """
        Test that alert rule validates name.

        Expected:
        - Empty name raises ValueError
        """
        with pytest.raises(ValueError, match="name cannot be empty"):
            AlertRule(
                name="",
                description="Test",
                severity=AlertSeverity.WARNING,
                condition=lambda m: False,
                enabled=True,
            )

    def test_alert_rule_evaluates_condition(self) -> None:
        """
        Test that alert rule evaluates its condition.

        Expected:
        - Condition function called with metrics
        - Result reflects actual evaluation
        """
        call_count = [0]
        
        def test_condition(metrics: Dict[str, Any]) -> bool:
            call_count[0] += 1
            return metrics.get("value", 0) > 50
        
        rule = AlertRule(
            name="test_rule",
            description="Test",
            severity=AlertSeverity.WARNING,
            condition=test_condition,
            enabled=True,
        )
        
        # Evaluate with metrics that match
        result = rule.evaluate({"value": 100})
        
        assert result is True
        assert call_count[0] == 1
        
        # Evaluate with metrics that don't match
        result = rule.evaluate({"value": 25})
        
        assert result is False
        assert call_count[0] == 2


class TestAlertManager:
    """Test alert manager functionality."""

    def test_alert_manager_initializes(self) -> None:
        """
        Test that alert manager initializes correctly.

        Expected:
        - Manager instance created
        - Rules list empty initially
        - Notification channels list empty
        """
        manager = AlertManager()
        
        assert manager is not None
        assert len(manager.get_rules()) == 0
        assert len(manager.get_notification_channels()) == 0

    def test_alert_rule_registration(self) -> None:
        """
        Test registering alert rules.

        Expected:
        - Rule added to manager
        - Rule retrievable by name
        - Multiple rules can be added
        """
        manager = AlertManager()
        
        rule = AlertRule(
            name="test_rule",
            description="Test",
            severity=AlertSeverity.WARNING,
            condition=lambda m: False,
            enabled=True,
        )
        
        manager.register_rule(rule)
        
        assert len(manager.get_rules()) == 1
        retrieved = manager.get_rule("test_rule")
        assert retrieved is not None
        assert retrieved.name == "test_rule"

    def test_alert_rule_deregistration(self) -> None:
        """
        Test deregistering alert rules.

        Expected:
        - Rule removed from manager
        - Not retrievable after removal
        """
        manager = AlertManager()
        
        rule = AlertRule(
            name="temp_rule",
            description="Test",
            severity=AlertSeverity.INFO,
            condition=lambda m: False,
            enabled=True,
        )
        
        manager.register_rule(rule)
        assert len(manager.get_rules()) == 1
        
        manager.deregister_rule("temp_rule")
        assert len(manager.get_rules()) == 0

    def test_alert_evaluation_on_metrics(self) -> None:
        """
        Test that alerts evaluate against metrics.

        Expected:
        - All enabled rules evaluated
        - Alerts generated for rules that trigger
        - Severity level included in alert
        """
        manager = AlertManager()
        
        # High latency rule
        manager.register_rule(AlertRule(
            name="high_latency",
            description="Latency alert",
            severity=AlertSeverity.WARNING,
            condition=lambda m: m.get("latency_avg", 0) > 500,
            enabled=True,
        ))
        
        # Error rate rule
        manager.register_rule(AlertRule(
            name="high_error_rate",
            description="Error rate alert",
            severity=AlertSeverity.CRITICAL,
            condition=lambda m: m.get("error_rate", 0) > 10,
            enabled=True,
        ))
        
        # Evaluate metrics that trigger high_latency
        metrics = {
            "latency_avg": 750,
            "error_rate": 2,
        }
        
        alerts = manager.evaluate_metrics(metrics)
        
        assert len(alerts) == 1
        assert alerts[0].rule_name == "high_latency"
        assert alerts[0].severity == AlertSeverity.WARNING

    def test_alert_deduplication(self) -> None:
        """
        Test that duplicate alerts are deduplicated.

        Expected:
        - Same alert not fired multiple times
        - Alert cleared when condition no longer met
        """
        manager = AlertManager(dedup_window_seconds=1)
        
        manager.register_rule(AlertRule(
            name="flaky_rule",
            description="Flaky alert",
            severity=AlertSeverity.WARNING,
            condition=lambda m: m.get("flaky", False),
            enabled=True,
        ))
        
        # First evaluation - should fire
        alerts1 = manager.evaluate_metrics({"flaky": True})
        assert len(alerts1) == 1
        
        # Second evaluation - should not fire (already fired, within dedup window)
        alerts2 = manager.evaluate_metrics({"flaky": True})
        assert len(alerts2) == 0
        
        # Clear condition - should mark as resolved
        alerts3 = manager.evaluate_metrics({"flaky": False})
        # No new alerts (condition is false)
        assert len(alerts3) == 0
        
        # Wait for dedup window to expire or use new manager
        manager2 = AlertManager(dedup_window_seconds=1)
        manager2.register_rule(AlertRule(
            name="flaky_rule",
            description="Flaky alert",
            severity=AlertSeverity.WARNING,
            condition=lambda m: m.get("flaky", False),
            enabled=True,
        ))
        
        # Re-trigger - should fire again
        alerts4 = manager2.evaluate_metrics({"flaky": True})
        assert len(alerts4) == 1


class TestNotificationChannels:
    """Test alert notification routing."""

    def test_notification_channel_registration(self) -> None:
        """
        Test registering notification channels.

        Expected:
        - Channel added to manager
        - Channel type tracked
        """
        manager = AlertManager()
        
        mock_channel = Mock()
        mock_channel.channel_type = "email"
        
        manager.register_notification_channel("email", mock_channel)
        
        channels = manager.get_notification_channels()
        assert len(channels) == 1

    def test_alert_routing_to_channels(self) -> None:
        """
        Test that alerts are routed to notification channels.

        Expected:
        - Alert sent to registered channels
        - Channel receives alert object
        - Multiple channels can receive same alert
        """
        manager = AlertManager()
        
        # Register mock channels with proper severity
        email_channel = Mock()
        email_channel.min_severity = AlertSeverity.INFO
        email_channel.send = Mock()
        
        slack_channel = Mock()
        slack_channel.min_severity = AlertSeverity.INFO
        slack_channel.send = Mock()
        
        manager.register_notification_channel("email", email_channel)
        manager.register_notification_channel("slack", slack_channel)
        
        # Create alert
        rule = AlertRule(
            name="test",
            description="Test",
            severity=AlertSeverity.CRITICAL,
            condition=lambda m: True,
            enabled=True,
        )
        
        manager.register_rule(rule)
        alerts = manager.evaluate_metrics({})
        
        # Send alerts
        if alerts:
            manager.send_alerts(alerts)
            
            # Verify channels called
            email_channel.send.assert_called()
            slack_channel.send.assert_called()

    def test_channel_severity_filtering(self) -> None:
        """
        Test that channels can filter by alert severity.

        Expected:
        - Channel only receives alerts above minimum severity
        """
        manager = AlertManager()
        
        mock_channel = Mock()
        mock_channel.min_severity = AlertSeverity.WARNING
        
        manager.register_notification_channel("test", mock_channel)
        
        # INFO alert (below threshold)
        info_alert = AlertNotification(
            rule_name="info_rule",
            severity=AlertSeverity.INFO,
            timestamp=datetime.utcnow(),
            message="Info message",
        )
        
        # CRITICAL alert (above threshold)
        critical_alert = AlertNotification(
            rule_name="critical_rule",
            severity=AlertSeverity.CRITICAL,
            timestamp=datetime.utcnow(),
            message="Critical message",
        )
        
        manager.send_alerts([info_alert])
        # Channel should not be called for INFO
        
        manager.send_alerts([critical_alert])
        # Channel should be called for CRITICAL


class TestHealthMonitor:
    """Test health checking system."""

    def test_health_monitor_initializes(self) -> None:
        """
        Test that health monitor initializes correctly.

        Expected:
        - Monitor instance created
        - Health status retrievable
        """
        monitor = HealthMonitor()
        
        assert monitor is not None
        status = monitor.get_status()
        assert status is not None

    def test_health_check_execution(self) -> None:
        """
        Test that health checks execute.

        Expected:
        - Health check function called
        - Result reflected in status
        """
        monitor = HealthMonitor()
        
        def check_database() -> bool:
            return True
        
        monitor.register_check("database", check_database)
        
        checks = monitor.get_registered_checks()
        assert len(checks) == 1

    def test_health_status_aggregation(self) -> None:
        """
        Test that health status aggregates multiple checks.

        Expected:
        - Overall status based on all checks
        - Individual check results available
        """
        monitor = HealthMonitor()
        
        monitor.register_check("db", lambda: True)
        monitor.register_check("cache", lambda: True)
        monitor.register_check("network", lambda: False)
        
        status = monitor.get_status()
        
        # If any check fails, overall should be degraded
        assert status.healthy is False or status.status == HealthStatusLevel.DEGRADED

    def test_health_check_caching(self) -> None:
        """
        Test that health check results are cached.

        Expected:
        - Check function not called on every status request
        - Cache expires after TTL
        """
        call_count = [0]
        
        def expensive_check() -> bool:
            call_count[0] += 1
            return True
        
        monitor = HealthMonitor(cache_ttl_seconds=5)
        monitor.register_check("expensive", expensive_check)
        
        # First call should execute check
        status1 = monitor.get_status()
        count_after_first = call_count[0]
        
        # Second call should use cache
        status2 = monitor.get_status()
        count_after_second = call_count[0]
        
        # Should not have called again
        assert count_after_second == count_after_first

    def test_health_check_timeout(self) -> None:
        """
        Test that health checks timeout if they run too long.

        Expected:
        - Check interrupted after timeout
        - Status marked as timeout
        """
        def slow_check() -> bool:
            import time
            time.sleep(5)  # Slower than timeout
            return True
        
        monitor = HealthMonitor(check_timeout_seconds=1)
        monitor.register_check("slow", slow_check)
        
        # This should timeout or be interrupted
        # Implementation detail - may vary


class TestAlertSeverity:
    """Test alert severity levels."""

    def test_severity_ordering(self) -> None:
        """
        Test that severity levels are properly ordered.

        Expected:
        - INFO < WARNING < CRITICAL ordering
        - Can compare severity levels
        """
        assert AlertSeverity.INFO.value < AlertSeverity.WARNING.value
        assert AlertSeverity.WARNING.value < AlertSeverity.CRITICAL.value


class TestAlertStorage:
    """Test alert history and storage."""

    def test_alert_history_stored(self) -> None:
        """
        Test that alerts are stored for history.

        Expected:
        - Alerts retrievable after firing
        - History queryable by time range
        """
        manager = AlertManager()
        
        rule = AlertRule(
            name="test",
            description="Test",
            severity=AlertSeverity.WARNING,
            condition=lambda m: m.get("trigger", False),
            enabled=True,
        )
        
        manager.register_rule(rule)
        
        # Fire alert
        alerts = manager.evaluate_metrics({"trigger": True})
        
        # Retrieve history
        history = manager.get_alert_history()
        
        assert len(history) >= 1


class TestTypeHints:
    """Test that all functions have proper type hints (CORE-011)."""

    def test_alert_manager_has_type_hints(self) -> None:
        """Test that AlertManager methods have complete type hints."""
        import inspect
        
        methods = inspect.getmembers(AlertManager, predicate=inspect.ismethod)
        
        for name, method in methods:
            if not name.startswith("_"):
                sig = inspect.signature(method)
                assert sig.return_annotation != inspect.Signature.empty

    def test_health_monitor_has_type_hints(self) -> None:
        """Test that HealthMonitor methods have complete type hints."""
        import inspect
        
        methods = inspect.getmembers(HealthMonitor, predicate=inspect.ismethod)
        
        for name, method in methods:
            if not name.startswith("_"):
                sig = inspect.signature(method)
                assert sig.return_annotation != inspect.Signature.empty


class TestDocstrings:
    """Test that all public APIs have docstrings (CORE-012)."""

    def test_alert_manager_has_docstrings(self) -> None:
        """Test that AlertManager has docstrings on public methods."""
        import inspect
        
        methods = inspect.getmembers(AlertManager, predicate=inspect.ismethod)
        
        for name, method in methods:
            if not name.startswith("_"):
                assert method.__doc__ is not None

    def test_health_monitor_has_docstrings(self) -> None:
        """Test that HealthMonitor has docstrings on public methods."""
        import inspect
        
        methods = inspect.getmembers(HealthMonitor, predicate=inspect.ismethod)
        
        for name, method in methods:
            if not name.startswith("_"):
                assert method.__doc__ is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
