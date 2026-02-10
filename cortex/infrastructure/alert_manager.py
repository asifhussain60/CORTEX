"""
Alert Manager for Threshold-Based Alerting

Implements alerting rules based on metric thresholds.

AC-NFR-004-03: Alerts triggered on threshold breach
"""

import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from cortex.models.canonical_enums import AlertSeverity, AlertState

logger = logging.getLogger(__name__)






@dataclass
class Alert:
    """Represents an alert."""
    alert_id: str
    rule_name: str
    message: str
    severity: AlertSeverity
    state: AlertState = AlertState.ACTIVE
    triggered_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    metric_value: Optional[Any] = None
    threshold_value: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "rule_name": self.rule_name,
            "message": self.message,
            "severity": self.severity.name.lower(),
            "state": self.state.value,
            "triggered_at": self.triggered_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "metric_value": self.metric_value,
            "threshold_value": self.threshold_value
        }


@dataclass
class ThresholdRule:
    """Defines a threshold-based alerting rule."""
    rule_id: str
    name: str
    metric_name: str
    threshold_value: Any
    operator: str  # ">", "<", "==", "!=", ">=", "<="
    severity: AlertSeverity
    message_template: str = "Threshold breach: {metric} {op} {threshold}"
    enabled: bool = True
    
    def check(self, metric_value: Any) -> bool:
        """Check if metric violates threshold."""
        if not self.enabled:
            return False
        
        try:
            if self.operator == ">":
                return metric_value > self.threshold_value
            elif self.operator == "<":
                return metric_value < self.threshold_value
            elif self.operator == ">=":
                return metric_value >= self.threshold_value
            elif self.operator == "<=":
                return metric_value <= self.threshold_value
            elif self.operator == "==":
                return metric_value == self.threshold_value
            elif self.operator == "!=":
                return metric_value != self.threshold_value
            else:
                logger.error(f"Unknown operator: {self.operator}")
                return False
        except Exception as e:
            logger.error(f"Error checking threshold: {str(e)}")
            return False
    
    def format_message(self, metric_value: Any) -> str:
        """Format alert message."""
        return self.message_template.format(
            metric=self.metric_name,
            op=self.operator,
            threshold=self.threshold_value,
            value=metric_value
        )


class ThresholdMonitor:
    """Monitors metrics against thresholds."""
    
    def __init__(self):
        self.rules: Dict[str, ThresholdRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
    
    def register_rule(self, rule: ThresholdRule):
        """Register a threshold rule."""
        self.rules[rule.rule_id] = rule
        logger.info(f"Registered threshold rule: {rule.name}")
    
    def check_metric(self, metric_name: str, metric_value: Any) -> List[Alert]:
        """Check metric against relevant rules and return triggered alerts."""
        triggered_alerts: List[Alert] = []
        
        for rule in self.rules.values():
            if rule.metric_name != metric_name:
                continue
            
            if rule.check(metric_value):
                alert = Alert(
                    alert_id=f"alert-{metric_name}-{datetime.utcnow().timestamp()}",
                    rule_name=rule.name,
                    message=rule.format_message(metric_value),
                    severity=rule.severity,
                    metric_value=metric_value,
                    threshold_value=rule.threshold_value
                )
                self.active_alerts[alert.alert_id] = alert
                self.alert_history.append(alert)
                triggered_alerts.append(alert)
                logger.warning(f"Alert triggered: {alert.message}")
        
        return triggered_alerts
    
    def resolve_alert(self, alert_id: str):
        """Resolve an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.state = AlertState.RESOLVED
            alert.resolved_at = datetime.utcnow()
            del self.active_alerts[alert_id]
            logger.info(f"Alert resolved: {alert_id}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: Optional[int] = None) -> List[Alert]:
        """Get alert history."""
        if limit:
            return self.alert_history[-limit:]
        return self.alert_history.copy()
    
    def disable_rule(self, rule_id: str):
        """Disable a rule."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            logger.info(f"Rule disabled: {rule_id}")
    
    def enable_rule(self, rule_id: str):
        """Enable a rule."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            logger.info(f"Rule enabled: {rule_id}")
    
    def clear_history(self):
        """Clear alert history."""
        self.alert_history.clear()


class AlertManager:
    """
    Manages alerting system.
    Coordinates threshold monitoring and alert dispatch.
    """
    
    def __init__(self, monitor: Optional[ThresholdMonitor] = None):
        self.monitor = monitor or ThresholdMonitor()
        self.handlers: List[Callable[[Alert], None]] = []
        self.muted_until: Dict[str, datetime] = {}
    
    def register_alert_handler(self, handler: Callable[[Alert], None]):
        """Register a handler to process alerts."""
        self.handlers.append(handler)
        logger.info(f"Registered alert handler: {handler.__name__}")
    
    def add_rule(self, rule: ThresholdRule):
        """Add a threshold rule."""
        self.monitor.register_rule(rule)
    
    def check_metric(self, metric_name: str, metric_value: Any) -> List[Alert]:
        """Check metric and dispatch alerts."""
        alerts = self.monitor.check_metric(metric_name, metric_value)
        
        for alert in alerts:
            # Check if alert is muted
            if self._is_muted(alert.rule_name):
                logger.info(f"Alert muted: {alert.rule_name}")
                continue
            
            # Dispatch to handlers
            for handler in self.handlers:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"Error dispatching alert: {str(e)}")
        
        return alerts
    
    def mute_rule(self, rule_name: str, until: datetime):
        """Mute alerts for a rule until specified time."""
        self.muted_until[rule_name] = until
        logger.info(f"Muted rule: {rule_name} until {until}")
    
    def unmute_rule(self, rule_name: str):
        """Unmute alerts for a rule."""
        if rule_name in self.muted_until:
            del self.muted_until[rule_name]
            logger.info(f"Unmuted rule: {rule_name}")
    
    def _is_muted(self, rule_name: str) -> bool:
        """Check if rule is muted."""
        if rule_name not in self.muted_until:
            return False
        
        if datetime.utcnow() > self.muted_until[rule_name]:
            del self.muted_until[rule_name]
            return False
        
        return True
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return self.monitor.get_active_alerts()
    
    def resolve_alert(self, alert_id: str):
        """Resolve an alert."""
        self.monitor.resolve_alert(alert_id)
