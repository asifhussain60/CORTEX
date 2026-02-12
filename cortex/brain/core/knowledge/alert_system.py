"""Alert system for anomaly notifications and governance registry integration.

This module provides alerting capabilities for detected anomalies, including
notification routing, severity-based escalation, and governance registry integration.

CORE Governance:
- CORE-004: Tier structure (Tier1 service)
- CORE-011: Type hints (100% mypy --strict)
- CORE-012: Documentation (100% docstrings)
- CORE-013: Specific exceptions
- CORE-028: Portable paths

Integration Points:
- ChangeDetectionService: Anomaly source
- Governance Registry: Rule storage and enforcement
- Notification System: Alert dispatch
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from cortex.brain.core.knowledge.change_detection import (
    AnomalyDetection,
    AnomalyType,
    SeverityLevel,
)
from cortex.models.canonical_enums import AlertPriority

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Supported notification channels."""

    EMAIL = "email"
    """Send alert via email."""

    SLACK = "slack"
    """Send alert via Slack."""

    LOG = "log"
    """Log to system logger."""

    WEBHOOK = "webhook"
    """Send alert via webhook."""

    AUDIT_TRAIL = "audit_trail"
    """Record in audit trail."""

    GOVERNANCE_REGISTRY = "governance_registry"
    """Record in governance registry."""




@dataclass
class AlertRule:
    """Rule defining when and how to alert for anomalies.

    Attributes:
        name: Unique rule identifier.
        anomaly_type: Type of anomaly to match.
        severity: Minimum severity to trigger alert.
        channels: Notification channels to use.
        priority: Alert priority.
        enabled: Whether rule is active.
        cooldown_seconds: Minimum time between alerts for same anomaly.
    """

    name: str
    anomaly_type: AnomalyType
    severity: SeverityLevel
    channels: List[NotificationChannel] = field(default_factory=list)
    priority: AlertPriority = AlertPriority.MEDIUM
    enabled: bool = True
    cooldown_seconds: int = 300

    def matches(self, anomaly: AnomalyDetection) -> bool:
        """Check if anomaly matches this rule.

        Args:
            anomaly: Anomaly to check.

        Returns:
            True if anomaly matches rule conditions.
        """
        if not self.enabled:
            return False

        if anomaly.anomaly_type != self.anomaly_type:
            return False

        # Check severity level
        severity_order = [SeverityLevel.INFO, SeverityLevel.WARNING, SeverityLevel.CRITICAL]
        anomaly_idx = severity_order.index(anomaly.severity)
        rule_idx = severity_order.index(self.severity)

        return anomaly_idx >= rule_idx


@dataclass
class Alert:
    """Alert instance for a detected anomaly.

    Attributes:
        alert_id: Unique identifier for this alert.
        anomaly: The underlying anomaly.
        rule: The rule that triggered this alert.
        severity: Alert severity level.
        priority: Alert priority.
        timestamp: When alert was created.
        channels: Channels to notify.
        status: Current alert status.
        notified_channels: Channels successfully notified.
    """

    alert_id: str
    anomaly: AnomalyDetection
    rule: AlertRule
    severity: AlertPriority
    timestamp: datetime = field(default_factory=datetime.utcnow)
    channels: List[NotificationChannel] = field(default_factory=list)
    status: str = "pending"
    notified_channels: Set[NotificationChannel] = field(default_factory=set)

    def mark_notified(self, channel: NotificationChannel) -> None:
        """Mark that a channel has been notified.

        Args:
            channel: The channel that was notified.
        """
        self.notified_channels.add(channel)


@dataclass
class AlertMetrics:
    """Metrics for alert system performance.

    Attributes:
        total_alerts: Total alerts generated.
        alerts_by_severity: Count by priority.
        alerts_by_type: Count by anomaly type.
        channels_used: Set of channels used.
        last_alert_time: When last alert was sent.
    """

    total_alerts: int = 0
    alerts_by_severity: Dict[AlertPriority, int] = field(default_factory=dict)
    alerts_by_type: Dict[AnomalyType, int] = field(default_factory=dict)
    channels_used: Set[NotificationChannel] = field(default_factory=set)
    last_alert_time: Optional[datetime] = None

    def record_alert(self, alert: Alert) -> None:
        """Record metrics for an alert.

        Args:
            alert: The alert to record.
        """
        self.total_alerts += 1
        self.alerts_by_severity[alert.severity] = (
            self.alerts_by_severity.get(alert.severity, 0) + 1
        )
        self.alerts_by_type[alert.anomaly.anomaly_type] = (
            self.alerts_by_type.get(alert.anomaly.anomaly_type, 0) + 1
        )
        self.channels_used.update(alert.channels)
        self.last_alert_time = datetime.utcnow()


class NotificationChannel_Handler(ABC):
    """Base class for notification channel implementations."""

    @abstractmethod
    def notify(self, alert: Alert) -> bool:
        """Send notification through channel.

        Args:
            alert: Alert to send.

        Returns:
            True if notification sent successfully.
        """


class LogNotificationHandler(NotificationChannel_Handler):
    """Handler for logging notifications."""

    def notify(self, alert: Alert) -> bool:
        """Log alert to system logger.

        Args:
            alert: Alert to log.

        Returns:
            True (always succeeds).
        """
        level = {
            AlertPriority.LOW: logging.INFO,
            AlertPriority.MEDIUM: logging.WARNING,
            AlertPriority.HIGH: logging.ERROR,
            AlertPriority.CRITICAL: logging.CRITICAL,
        }.get(alert.severity, logging.WARNING)

        logger.log(
            level,
            f"ALERT [{alert.alert_id}] {alert.rule.name}: "
            f"{alert.anomaly.anomaly_type.value} - {alert.anomaly.reasoning}",
        )

        return True


class AuditTrailNotificationHandler(NotificationChannel_Handler):
    """Handler for audit trail recording."""

    def notify(self, alert: Alert) -> bool:
        """Record alert in audit trail.

        Args:
            alert: Alert to record.

        Returns:
            True if recorded successfully.
        """
        # In production, would write to actual audit trail
        logger.info(
            f"Audit trail entry: Alert {alert.alert_id} recorded for {alert.anomaly.anomaly_type.value}"
        )
        return True


class GovernanceRegistryNotificationHandler(NotificationChannel_Handler):
    """Handler for governance registry integration."""

    def notify(self, alert: Alert) -> bool:
        """Record alert in governance registry.

        Args:
            alert: Alert to record.

        Returns:
            True if recorded successfully.
        """
        # In production, would write to governance registry
        logger.info(
            f"Governance registry entry: Alert {alert.alert_id} "
            f"({alert.rule.name}) priority={alert.severity.name}"
        )
        return True


class AlertSystem:
    """Central alert system for anomaly notifications.

    Manages alert rules, dispatches alerts, and tracks metrics.
    """

    def __init__(self) -> None:
        """Initialize alert system."""
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: List[Alert] = []
        self.metrics = AlertMetrics()
        self.handlers: Dict[NotificationChannel, NotificationChannel_Handler] = {
            NotificationChannel.LOG: LogNotificationHandler(),
            NotificationChannel.AUDIT_TRAIL: AuditTrailNotificationHandler(),
            NotificationChannel.GOVERNANCE_REGISTRY: GovernanceRegistryNotificationHandler(),
        }
        self.alert_cooldowns: Dict[str, datetime] = {}
        self._alert_counter = 0

    def add_rule(self, rule: AlertRule) -> None:
        """Add an alert rule.

        Args:
            rule: Rule to add.

        Raises:
            ValueError: If rule name already exists.
        """
        if rule.name in self.rules:
            raise ValueError(f"Rule with name '{rule.name}' already exists")

        self.rules[rule.name] = rule
        logger.info(f"Alert rule added: {rule.name}")

    def remove_rule(self, rule_name: str) -> bool:
        """Remove an alert rule.

        Args:
            rule_name: Name of rule to remove.

        Returns:
            True if rule was removed, False if not found.
        """
        if rule_name in self.rules:
            del self.rules[rule_name]
            logger.info(f"Alert rule removed: {rule_name}")
            return True
        return False

    def enable_rule(self, rule_name: str) -> bool:
        """Enable an alert rule.

        Args:
            rule_name: Name of rule to enable.

        Returns:
            True if rule was enabled.
        """
        if rule_name in self.rules:
            self.rules[rule_name].enabled = True
            return True
        return False

    def disable_rule(self, rule_name: str) -> bool:
        """Disable an alert rule.

        Args:
            rule_name: Name of rule to disable.

        Returns:
            True if rule was disabled.
        """
        if rule_name in self.rules:
            self.rules[rule_name].enabled = False
            return True
        return False

    def process_anomaly(self, anomaly: AnomalyDetection) -> List[Alert]:
        """Process an anomaly and generate alerts.

        Args:
            anomaly: Anomaly to process.

        Returns:
            List of alerts generated.
        """
        alerts: List[Alert] = []

        # Check all rules
        for rule in self.rules.values():
            if not rule.matches(anomaly):
                continue

            # Check cooldown
            rule_key = f"{rule.name}_{anomaly.anomaly_type.value}"
            now = datetime.utcnow()

            if rule_key in self.alert_cooldowns:
                last_alert = self.alert_cooldowns[rule_key]
                if (now - last_alert).total_seconds() < rule.cooldown_seconds:
                    continue

            # Create alert
            self._alert_counter += 1
            alert_id = f"ALERT-{self._alert_counter:06d}"

            # Map severity to priority
            priority_map = {
                SeverityLevel.INFO: AlertPriority.LOW,
                SeverityLevel.WARNING: AlertPriority.MEDIUM,
                SeverityLevel.CRITICAL: AlertPriority.CRITICAL,
            }
            priority = priority_map.get(anomaly.severity, AlertPriority.MEDIUM)

            alert = Alert(
                alert_id=alert_id,
                anomaly=anomaly,
                rule=rule,
                severity=priority,
                channels=rule.channels,
            )

            # Dispatch alert
            self._dispatch_alert(alert)

            alerts.append(alert)
            self.alerts.append(alert)
            self.metrics.record_alert(alert)
            self.alert_cooldowns[rule_key] = now

            logger.info(f"Alert generated: {alert_id} for {rule.name}")

        return alerts

    def _dispatch_alert(self, alert: Alert) -> None:
        """Dispatch alert to configured channels.

        Args:
            alert: Alert to dispatch.
        """
        for channel in alert.channels:
            handler = self.handlers.get(channel)
            if handler:
                try:
                    if handler.notify(alert):
                        alert.mark_notified(channel)
                except Exception as e:
                    logger.error(f"Failed to notify {channel.value}: {e}")

        alert.status = "sent"

    def get_alerts_by_rule(self, rule_name: str) -> List[Alert]:
        """Get all alerts for a specific rule.

        Args:
            rule_name: Name of rule to filter by.

        Returns:
            List of alerts matching rule.
        """
        return [a for a in self.alerts if a.rule.name == rule_name]

    def get_alerts_by_severity(self, severity: AlertPriority) -> List[Alert]:
        """Get alerts by priority level.

        Args:
            severity: Priority level to filter by.

        Returns:
            List of alerts matching priority.
        """
        return [a for a in self.alerts if a.severity == severity]

    def get_alerts_by_anomaly_type(self, anomaly_type: AnomalyType) -> List[Alert]:
        """Get alerts by anomaly type.

        Args:
            anomaly_type: Anomaly type to filter by.

        Returns:
            List of alerts matching type.
        """
        return [a for a in self.alerts if a.anomaly.anomaly_type == anomaly_type]

    def get_recent_alerts(self, limit: int = 10) -> List[Alert]:
        """Get most recent alerts.

        Args:
            limit: Maximum number of alerts to return.

        Returns:
            List of recent alerts, newest first.
        """
        return sorted(self.alerts, key=lambda a: a.timestamp, reverse=True)[:limit]

    def get_metrics(self) -> AlertMetrics:
        """Get alert system metrics.

        Returns:
            Current system metrics.
        """
        return self.metrics

    def clear_alerts(self, older_than_hours: int = 24) -> int:
        """Clear old alerts.

        Args:
            older_than_hours: Remove alerts older than this many hours.

        Returns:
            Number of alerts cleared.
        """
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)
        initial_count = len(self.alerts)
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff]
        removed = initial_count - len(self.alerts)

        logger.info(f"Cleared {removed} alerts older than {older_than_hours} hours")
        return removed


def create_default_alert_rules() -> List[AlertRule]:
    """Create default alert rules.

    Returns:
        List of default alert rules.
    """
    return [
        AlertRule(
            name="critical_schema_drift",
            anomaly_type=AnomalyType.SCHEMA_DRIFT,
            severity=SeverityLevel.CRITICAL,
            channels=[
                NotificationChannel.LOG,
                NotificationChannel.GOVERNANCE_REGISTRY,
            ],
            priority=AlertPriority.CRITICAL,
            cooldown_seconds=600,
        ),
        AlertRule(
            name="critical_coverage_gap",
            anomaly_type=AnomalyType.COVERAGE_GAP,
            severity=SeverityLevel.CRITICAL,
            channels=[
                NotificationChannel.LOG,
                NotificationChannel.AUDIT_TRAIL,
                NotificationChannel.GOVERNANCE_REGISTRY,
            ],
            priority=AlertPriority.CRITICAL,
            cooldown_seconds=600,
        ),
        AlertRule(
            name="warning_staleness",
            anomaly_type=AnomalyType.STALENESS,
            severity=SeverityLevel.WARNING,
            channels=[NotificationChannel.LOG, NotificationChannel.AUDIT_TRAIL],
            priority=AlertPriority.MEDIUM,
            cooldown_seconds=3600,
        ),
        AlertRule(
            name="warning_semantic_shift",
            anomaly_type=AnomalyType.SEMANTIC_SHIFT,
            severity=SeverityLevel.WARNING,
            channels=[NotificationChannel.LOG],
            priority=AlertPriority.MEDIUM,
            cooldown_seconds=1800,
        ),
        AlertRule(
            name="warning_volume_anomaly",
            anomaly_type=AnomalyType.VOLUME_ANOMALY,
            severity=SeverityLevel.WARNING,
            channels=[NotificationChannel.LOG, NotificationChannel.AUDIT_TRAIL],
            priority=AlertPriority.MEDIUM,
            cooldown_seconds=1800,
        ),
    ]


class AlertSystemFactory:
    """Factory for creating configured alert systems."""

    @staticmethod
    def create_with_defaults() -> AlertSystem:
        """Create alert system with default rules.

        Returns:
            Configured AlertSystem instance.
        """
        system = AlertSystem()
        for rule in create_default_alert_rules():
            system.add_rule(rule)
        return system
