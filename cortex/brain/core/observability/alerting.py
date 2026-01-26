"""
Alert management and notification system for CORTEX observability.

Provides rule-based alerting, severity levels, notification routing, and
alert deduplication for production monitoring.

Attributes:
    DEFAULT_ALERT_RETENTION: Alert history retention days (7)
    DEFAULT_DEDUP_WINDOW: Alert deduplication window seconds (300)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable, Set
from datetime import datetime, timedelta
from enum import Enum
import logging
from cortex.models.canonical_enums import AlertSeverity




@dataclass
class AlertCondition:
    """Condition for alert evaluation.
    
    Attributes:
        name: Condition name
        func: Callable that evaluates metrics
    """
    name: str
    func: Callable[[Dict[str, Any]], bool]


@dataclass
class AlertRule:
    """Alert rule definition.
    
    Attributes:
        name: Unique rule name
        description: Rule description
        severity: Alert severity level
        condition: Function evaluating if alert should trigger
        enabled: Whether rule is active
        tags: Metadata tags
    """
    name: str
    description: str
    severity: AlertSeverity
    condition: Callable[[Dict[str, Any]], bool]
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate rule after initialization.
        
        Raises:
            ValueError: If name is empty
        """
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty")

    def evaluate(self, metrics: Dict[str, Any]) -> bool:
        """Evaluate rule condition against metrics.
        
        Args:
            metrics: Metrics dictionary
            
        Returns:
            True if condition met, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            return self.condition(metrics)
        except Exception as e:
            logging.warning(f"Error evaluating rule {self.name}: {e}")
            return False


@dataclass
class AlertNotification:
    """Alert notification.
    
    Attributes:
        rule_name: Name of rule that triggered
        severity: Alert severity
        timestamp: When alert fired
        message: Alert message
        metrics: Related metrics data
    """
    rule_name: str
    severity: AlertSeverity
    timestamp: datetime
    message: str
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary with alert data
        """
        return {
            "rule_name": self.rule_name,
            "severity": self.severity.name,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "metrics": self.metrics,
        }


class AlertManager:
    """Manages alert rules and notifications.
    
    Handles rule registration, metric evaluation, alert firing,
    deduplication, and notification routing.
    
    Attributes:
        rules: Dictionary of registered alert rules
        channels: Dictionary of notification channels
        active_alerts: Currently active alerts
        alert_history: Historical alert records
    """
    
    def __init__(
        self,
        dedup_window_seconds: int = 300,
        retention_days: int = 7,
    ) -> None:
        """Initialize alert manager.
        
        Args:
            dedup_window_seconds: Deduplication window in seconds
            retention_days: Alert retention in days
        """
        self.rules: Dict[str, AlertRule] = {}
        self.channels: Dict[str, Any] = {}
        self.active_alerts: Set[str] = set()
        self.alert_history: List[AlertNotification] = []
        
        self.dedup_window_seconds = dedup_window_seconds
        self.retention_days = retention_days
        
        self._last_alert_time: Dict[str, datetime] = {}
        self._logger: logging.Logger = logging.getLogger(__name__)

    def register_rule(self, rule: AlertRule) -> None:
        """Register an alert rule.
        
        Args:
            rule: AlertRule instance
        """
        self.rules[rule.name] = rule
        self._logger.info(f"Registered alert rule: {rule.name}")

    def deregister_rule(self, rule_name: str) -> None:
        """Deregister an alert rule.
        
        Args:
            rule_name: Name of rule to remove
        """
        if rule_name in self.rules:
            del self.rules[rule_name]
            self._logger.info(f"Deregistered alert rule: {rule_name}")

    def get_rule(self, rule_name: str) -> Optional[AlertRule]:
        """Get a registered rule by name.
        
        Args:
            rule_name: Name of rule
            
        Returns:
            AlertRule or None if not found
        """
        return self.rules.get(rule_name)

    def get_rules(self) -> List[AlertRule]:
        """Get all registered rules.
        
        Returns:
            List of AlertRule instances
        """
        return list(self.rules.values())

    def register_notification_channel(self, channel_type: str, channel: Any) -> None:
        """Register a notification channel.
        
        Args:
            channel_type: Type of channel (email, slack, etc)
            channel: Channel instance
        """
        self.channels[channel_type] = channel
        self._logger.info(f"Registered notification channel: {channel_type}")

    def get_notification_channels(self) -> Dict[str, Any]:
        """Get all registered notification channels.
        
        Returns:
            Dictionary of channels
        """
        return self.channels.copy()

    def evaluate_metrics(self, metrics: Dict[str, Any]) -> List[AlertNotification]:
        """Evaluate all rules against metrics.
        
        Args:
            metrics: Metrics dictionary
            
        Returns:
            List of AlertNotification objects for triggered rules
        """
        alerts = []
        now = datetime.utcnow()
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            # Check if rule triggers
            if rule.evaluate(metrics):
                # Check deduplication
                last_alert = self._last_alert_time.get(rule.name)
                if last_alert and (now - last_alert).total_seconds() < self.dedup_window_seconds:
                    continue
                
                # Create alert notification
                alert = AlertNotification(
                    rule_name=rule.name,
                    severity=rule.severity,
                    timestamp=now,
                    message=rule.description,
                    metrics=metrics.copy(),
                )
                
                alerts.append(alert)
                self._last_alert_time[rule.name] = now
                self.active_alerts.add(rule.name)
                self.alert_history.append(alert)
            else:
                # Rule no longer triggers
                if rule.name in self.active_alerts:
                    self.active_alerts.discard(rule.name)
        
        return alerts

    def send_alerts(self, alerts: List[AlertNotification]) -> None:
        """Send alerts to notification channels.
        
        Args:
            alerts: List of AlertNotification objects
        """
        for alert in alerts:
            for channel in self.channels.values():
                # Check if channel should receive this alert
                min_severity = getattr(channel, "min_severity", AlertSeverity.INFO)
                if alert.severity.value >= min_severity.value:
                    try:
                        channel.send(alert)
                    except Exception as e:
                        self._logger.error(f"Failed to send alert via channel: {e}")

    def get_alert_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        rule_name: Optional[str] = None,
    ) -> List[AlertNotification]:
        """Get alert history.
        
        Args:
            start_time: Start of time range (optional)
            end_time: End of time range (optional)
            rule_name: Filter by rule name (optional)
            
        Returns:
            List of AlertNotification objects
        """
        results = self.alert_history
        
        if start_time:
            results = [a for a in results if a.timestamp >= start_time]
        
        if end_time:
            results = [a for a in results if a.timestamp <= end_time]
        
        if rule_name:
            results = [a for a in results if a.rule_name == rule_name]
        
        return results

    def clear_old_alerts(self) -> None:
        """Clear alerts older than retention policy."""
        cutoff_time = datetime.utcnow() - timedelta(days=self.retention_days)
        self.alert_history = [
            a for a in self.alert_history
            if a.timestamp > cutoff_time
        ]

    def get_active_alerts(self) -> List[str]:
        """Get currently active alert rule names.
        
        Returns:
            List of active rule names
        """
        return list(self.active_alerts)

    def get_stats(self) -> Dict[str, Any]:
        """Get alert statistics.
        
        Returns:
            Dictionary with alert statistics
        """
        total_alerts = len(self.alert_history)
        active_count = len(self.active_alerts)
        
        # Count by severity
        severity_counts = {
            "INFO": len([a for a in self.alert_history if a.severity == AlertSeverity.INFO]),
            "WARNING": len([a for a in self.alert_history if a.severity == AlertSeverity.WARNING]),
            "CRITICAL": len([a for a in self.alert_history if a.severity == AlertSeverity.CRITICAL]),
        }
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_count,
            "severity_counts": severity_counts,
            "registered_rules": len(self.rules),
            "registered_channels": len(self.channels),
        }
