"""Unit tests for alert system.

Tests alert rules, alert generation, and notification dispatch.
"""

import pytest
from datetime import datetime, timedelta

from cortex.brain.core.knowledge.alert_system import (
    NotificationChannel,
    AlertPriority,
    AlertRule,
    Alert,
    AlertMetrics,
    AlertSystem,
    create_default_alert_rules,
    AlertSystemFactory,
)
from cortex.brain.core.knowledge.change_detection import (
    AnomalyDetection,
    AnomalyScore,
    AnomalyType,
    SeverityLevel,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_anomalies() -> dict:
    """Sample anomalies for testing."""
    return {
        "critical_schema": AnomalyDetection(
            anomaly_type=AnomalyType.SCHEMA_DRIFT,
            severity=SeverityLevel.CRITICAL,
            score=AnomalyScore(value=0.9, confidence=0.95, reasoning="Critical drift"),
            affected_entries=["entry1"],
        ),
        "warning_coverage": AnomalyDetection(
            anomaly_type=AnomalyType.COVERAGE_GAP,
            severity=SeverityLevel.WARNING,
            score=AnomalyScore(value=0.6, confidence=0.8, reasoning="Coverage gap"),
            affected_entries=["domain1"],
        ),
        "info_stale": AnomalyDetection(
            anomaly_type=AnomalyType.STALENESS,
            severity=SeverityLevel.INFO,
            score=AnomalyScore(value=0.3, confidence=0.7, reasoning="Some staleness"),
            affected_entries=["entry3"],
        ),
    }


@pytest.fixture
def alert_rule():
    """Sample alert rule."""
    return AlertRule(
        name="test_rule",
        anomaly_type=AnomalyType.SCHEMA_DRIFT,
        severity=SeverityLevel.CRITICAL,
        channels=[NotificationChannel.LOG],
        priority=AlertPriority.HIGH,
    )


@pytest.fixture
def alert_system():
    """Create alert system for testing."""
    return AlertSystem()


# ============================================================================
# AlertRule Tests
# ============================================================================


class TestAlertRule:
    """Tests for alert rules."""

    def test_rule_creation(self) -> None:
        """Test creating an alert rule."""
        rule = AlertRule(
            name="test_rule",
            anomaly_type=AnomalyType.SCHEMA_DRIFT,
            severity=SeverityLevel.CRITICAL,
            channels=[NotificationChannel.LOG],
        )

        assert rule.name == "test_rule"
        assert rule.enabled is True

    def test_rule_disabled(self) -> None:
        """Test disabled rule."""
        rule = AlertRule(
            name="disabled_rule",
            anomaly_type=AnomalyType.SCHEMA_DRIFT,
            severity=SeverityLevel.CRITICAL,
            enabled=False,
        )

        assert rule.enabled is False

    def test_rule_matches_exact(self, alert_rule: AlertRule, sample_anomalies: dict) -> None:
        """Test rule matching with exact match."""
        anomaly = sample_anomalies["critical_schema"]
        assert alert_rule.matches(anomaly)

    def test_rule_no_match_wrong_type(self, alert_rule: AlertRule, sample_anomalies: dict) -> None:
        """Test rule not matching wrong anomaly type."""
        anomaly = sample_anomalies["warning_coverage"]
        assert not alert_rule.matches(anomaly)

    def test_rule_no_match_insufficient_severity(self, sample_anomalies: dict) -> None:
        """Test rule not matching due to insufficient severity."""
        rule = AlertRule(
            name="critical_rule",
            anomaly_type=AnomalyType.STALENESS,
            severity=SeverityLevel.CRITICAL,
        )

        anomaly = sample_anomalies["info_stale"]
        assert not rule.matches(anomaly)

    def test_rule_match_higher_severity(self, alert_rule: AlertRule) -> None:
        """Test rule matching anomaly with higher severity."""
        anomaly = AnomalyDetection(
            anomaly_type=AnomalyType.SCHEMA_DRIFT,
            severity=SeverityLevel.CRITICAL,
            score=AnomalyScore(value=1.0, confidence=1.0, reasoning="Very critical"),
            affected_entries=["entry1", "entry2"],
        )

        assert alert_rule.matches(anomaly)


# ============================================================================
# Alert Tests
# ============================================================================


class TestAlert:
    """Tests for alert instances."""

    def test_alert_creation(self, alert_rule: AlertRule, sample_anomalies: dict) -> None:
        """Test creating an alert."""
        alert = Alert(
            alert_id="ALERT-001",
            anomaly=sample_anomalies["critical_schema"],
            rule=alert_rule,
            severity=AlertPriority.CRITICAL,
            channels=[NotificationChannel.LOG],
        )

        assert alert.alert_id == "ALERT-001"
        assert alert.status == "pending"

    def test_alert_mark_notified(self, alert_rule: AlertRule, sample_anomalies: dict) -> None:
        """Test marking alert as notified."""
        alert = Alert(
            alert_id="ALERT-001",
            anomaly=sample_anomalies["critical_schema"],
            rule=alert_rule,
            severity=AlertPriority.CRITICAL,
        )

        assert NotificationChannel.LOG not in alert.notified_channels

        alert.mark_notified(NotificationChannel.LOG)

        assert NotificationChannel.LOG in alert.notified_channels


# ============================================================================
# AlertMetrics Tests
# ============================================================================


class TestAlertMetrics:
    """Tests for alert metrics."""

    def test_metrics_initialization(self) -> None:
        """Test creating alert metrics."""
        metrics = AlertMetrics()

        assert metrics.total_alerts == 0
        assert len(metrics.alerts_by_severity) == 0

    def test_record_alert(self, alert_rule: AlertRule, sample_anomalies: dict) -> None:
        """Test recording alert metrics."""
        metrics = AlertMetrics()

        alert = Alert(
            alert_id="ALERT-001",
            anomaly=sample_anomalies["critical_schema"],
            rule=alert_rule,
            severity=AlertPriority.CRITICAL,
        )

        metrics.record_alert(alert)

        assert metrics.total_alerts == 1
        assert metrics.alerts_by_severity[AlertPriority.CRITICAL] == 1

    def test_record_multiple_alerts(self, alert_rule: AlertRule, sample_anomalies: dict) -> None:
        """Test recording multiple alerts."""
        metrics = AlertMetrics()

        for i, (key, anomaly) in enumerate(sample_anomalies.items()):
            alert = Alert(
                alert_id=f"ALERT-{i:03d}",
                anomaly=anomaly,
                rule=alert_rule,
                severity=AlertPriority.MEDIUM,
            )
            metrics.record_alert(alert)

        assert metrics.total_alerts == 3


# ============================================================================
# AlertSystem Tests
# ============================================================================


class TestAlertSystem:
    """Tests for alert system."""

    def test_system_initialization(self, alert_system: AlertSystem) -> None:
        """Test alert system initialization."""
        assert len(alert_system.rules) == 0
        assert len(alert_system.alerts) == 0

    def test_add_rule(self, alert_system: AlertSystem, alert_rule: AlertRule) -> None:
        """Test adding a rule."""
        alert_system.add_rule(alert_rule)

        assert "test_rule" in alert_system.rules

    def test_add_duplicate_rule_raises(self, alert_system: AlertSystem, alert_rule: AlertRule) -> None:
        """Test that duplicate rule name raises error."""
        alert_system.add_rule(alert_rule)

        with pytest.raises(ValueError):
            alert_system.add_rule(alert_rule)

    def test_remove_rule(self, alert_system: AlertSystem, alert_rule: AlertRule) -> None:
        """Test removing a rule."""
        alert_system.add_rule(alert_rule)
        removed = alert_system.remove_rule("test_rule")

        assert removed is True
        assert "test_rule" not in alert_system.rules

    def test_remove_nonexistent_rule(self, alert_system: AlertSystem) -> None:
        """Test removing non-existent rule."""
        removed = alert_system.remove_rule("nonexistent")

        assert removed is False

    def test_enable_rule(self, alert_system: AlertSystem, alert_rule: AlertRule) -> None:
        """Test enabling a rule."""
        alert_rule.enabled = False
        alert_system.add_rule(alert_rule)

        alert_system.enable_rule("test_rule")

        assert alert_system.rules["test_rule"].enabled is True

    def test_disable_rule(self, alert_system: AlertSystem, alert_rule: AlertRule) -> None:
        """Test disabling a rule."""
        alert_system.add_rule(alert_rule)

        alert_system.disable_rule("test_rule")

        assert alert_system.rules["test_rule"].enabled is False

    def test_process_anomaly_matching_rule(self, alert_system: AlertSystem, alert_rule: AlertRule, sample_anomalies: dict) -> None:
        """Test processing anomaly that matches rule."""
        alert_system.add_rule(alert_rule)

        alerts = alert_system.process_anomaly(sample_anomalies["critical_schema"])

        assert len(alerts) == 1
        assert alerts[0].rule.name == "test_rule"

    def test_process_anomaly_no_matching_rule(self, alert_system: AlertSystem, alert_rule: AlertRule, sample_anomalies: dict) -> None:
        """Test processing anomaly with no matching rule."""
        alert_system.add_rule(alert_rule)

        alerts = alert_system.process_anomaly(sample_anomalies["warning_coverage"])

        assert len(alerts) == 0

    def test_process_anomaly_disabled_rule(self, alert_system: AlertSystem, alert_rule: AlertRule, sample_anomalies: dict) -> None:
        """Test that disabled rule doesn't match."""
        alert_rule.enabled = False
        alert_system.add_rule(alert_rule)

        alerts = alert_system.process_anomaly(sample_anomalies["critical_schema"])

        assert len(alerts) == 0

    def test_alert_cooldown(self, alert_system: AlertSystem, alert_rule: AlertRule, sample_anomalies: dict) -> None:
        """Test alert cooldown prevents duplicate alerts."""
        alert_rule.cooldown_seconds = 1
        alert_system.add_rule(alert_rule)

        # First alert should be processed
        alerts1 = alert_system.process_anomaly(sample_anomalies["critical_schema"])
        assert len(alerts1) == 1

        # Second immediate alert should be suppressed by cooldown
        alerts2 = alert_system.process_anomaly(sample_anomalies["critical_schema"])
        assert len(alerts2) == 0

    def test_get_alerts_by_rule(self, alert_system: AlertSystem, alert_rule: AlertRule, sample_anomalies: dict) -> None:
        """Test retrieving alerts by rule name."""
        alert_system.add_rule(alert_rule)

        alert_system.process_anomaly(sample_anomalies["critical_schema"])
        alerts = alert_system.get_alerts_by_rule("test_rule")

        assert len(alerts) == 1

    def test_get_alerts_by_severity(self, alert_system: AlertSystem, alert_rule: AlertRule, sample_anomalies: dict) -> None:
        """Test retrieving alerts by severity."""
        alert_system.add_rule(alert_rule)

        alert_system.process_anomaly(sample_anomalies["critical_schema"])
        alerts = alert_system.get_alerts_by_severity(AlertPriority.CRITICAL)

        assert len(alerts) == 1

    def test_get_alerts_by_anomaly_type(self, alert_system: AlertSystem, alert_rule: AlertRule, sample_anomalies: dict) -> None:
        """Test retrieving alerts by anomaly type."""
        alert_system.add_rule(alert_rule)

        alert_system.process_anomaly(sample_anomalies["critical_schema"])
        alerts = alert_system.get_alerts_by_anomaly_type(AnomalyType.SCHEMA_DRIFT)

        assert len(alerts) == 1

    def test_get_recent_alerts(self, alert_system: AlertSystem) -> None:
        """Test retrieving recent alerts."""
        rule = AlertRule(
            name="rule1",
            anomaly_type=AnomalyType.SCHEMA_DRIFT,
            severity=SeverityLevel.CRITICAL,
        )
        alert_system.add_rule(rule)

        anomaly = AnomalyDetection(
            anomaly_type=AnomalyType.SCHEMA_DRIFT,
            severity=SeverityLevel.CRITICAL,
            score=AnomalyScore(value=0.9, confidence=0.95, reasoning="Test"),
            affected_entries=[],
        )

        # Create multiple alerts
        for i in range(5):
            alert_system.process_anomaly(anomaly)

        recent = alert_system.get_recent_alerts(limit=3)
        assert len(recent) <= 3

    def test_get_metrics(self, alert_system: AlertSystem, alert_rule: AlertRule, sample_anomalies: dict) -> None:
        """Test retrieving system metrics."""
        alert_system.add_rule(alert_rule)
        alert_system.process_anomaly(sample_anomalies["critical_schema"])

        metrics = alert_system.get_metrics()

        assert metrics.total_alerts == 1

    def test_clear_alerts(self, alert_system: AlertSystem, alert_rule: AlertRule, sample_anomalies: dict) -> None:
        """Test clearing old alerts."""
        alert_system.add_rule(alert_rule)
        alert_system.process_anomaly(sample_anomalies["critical_schema"])

        # Create old alert manually
        old_alert = Alert(
            alert_id="OLD-001",
            anomaly=sample_anomalies["critical_schema"],
            rule=alert_rule,
            severity=AlertPriority.CRITICAL,
            timestamp=datetime.utcnow() - timedelta(days=2),
        )
        alert_system.alerts.append(old_alert)

        cleared = alert_system.clear_alerts(older_than_hours=24)

        assert cleared >= 1


# ============================================================================
# Default Rules Tests
# ============================================================================


class TestDefaultRules:
    """Tests for default alert rules."""

    def test_create_default_rules(self) -> None:
        """Test creating default rules."""
        rules = create_default_alert_rules()

        assert len(rules) >= 5
        assert all(isinstance(r, AlertRule) for r in rules)

    def test_default_rules_enabled(self) -> None:
        """Test that default rules are enabled."""
        rules = create_default_alert_rules()

        assert all(r.enabled for r in rules)

    def test_default_rules_have_channels(self) -> None:
        """Test that default rules have notification channels."""
        rules = create_default_alert_rules()

        assert all(len(r.channels) > 0 for r in rules)

    def test_default_rules_coverage(self) -> None:
        """Test that default rules cover all anomaly types."""
        rules = create_default_alert_rules()
        anomaly_types = {r.anomaly_type for r in rules}

        assert AnomalyType.SCHEMA_DRIFT in anomaly_types
        assert AnomalyType.COVERAGE_GAP in anomaly_types


# ============================================================================
# Factory Tests
# ============================================================================


class TestAlertSystemFactory:
    """Tests for alert system factory."""

    def test_create_with_defaults(self) -> None:
        """Test creating system with default rules."""
        system = AlertSystemFactory.create_with_defaults()

        assert len(system.rules) >= 5
        assert all(r.enabled for r in system.rules.values())

    def test_default_system_ready_to_use(self, sample_anomalies: dict) -> None:
        """Test that default system can immediately process anomalies."""
        system = AlertSystemFactory.create_with_defaults()

        alerts = system.process_anomaly(sample_anomalies["critical_schema"])

        assert isinstance(alerts, list)


# ============================================================================
# Integration Tests
# ============================================================================


class TestAlertIntegration:
    """Integration tests for alert system."""

    def test_end_to_end_alerting(self) -> None:
        """Test end-to-end alerting workflow."""
        system = AlertSystemFactory.create_with_defaults()

        anomaly = AnomalyDetection(
            anomaly_type=AnomalyType.SCHEMA_DRIFT,
            severity=SeverityLevel.CRITICAL,
            score=AnomalyScore(value=0.95, confidence=0.99, reasoning="Critical drift"),
            affected_entries=["entry1", "entry2"],
        )

        alerts = system.process_anomaly(anomaly)
        metrics = system.get_metrics()

        assert len(alerts) > 0
        assert metrics.total_alerts > 0

    def test_multiple_rule_matching(self) -> None:
        """Test anomaly matching multiple rules."""
        system = AlertSystem()

        rule1 = AlertRule(
            name="rule1",
            anomaly_type=AnomalyType.SCHEMA_DRIFT,
            severity=SeverityLevel.WARNING,
            channels=[NotificationChannel.LOG],
        )

        rule2 = AlertRule(
            name="rule2",
            anomaly_type=AnomalyType.SCHEMA_DRIFT,
            severity=SeverityLevel.INFO,
            channels=[NotificationChannel.AUDIT_TRAIL],
        )

        system.add_rule(rule1)
        system.add_rule(rule2)

        anomaly = AnomalyDetection(
            anomaly_type=AnomalyType.SCHEMA_DRIFT,
            severity=SeverityLevel.CRITICAL,
            score=AnomalyScore(value=0.9, confidence=0.95, reasoning="Critical"),
            affected_entries=["entry1"],
        )

        alerts = system.process_anomaly(anomaly)

        # Should match both rules
        assert len(alerts) >= 2
