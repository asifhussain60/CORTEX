"""Production Monitoring & Alerting System"""
from dataclasses import dataclass
from datetime import datetime
from typing import List
from enum import Enum


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Production alert.
    
    Args:
        name: Alert name
        severity: Alert severity level
        message: Alert message
        timestamp: Alert timestamp
    """
    name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime


class MonitoringSystem:
    """Production monitoring and alerting system."""
    
    def __init__(self):
        self.metrics: dict = {}
        self.alerts: List[Alert] = []
        self.thresholds: dict = {}
    
    def record_metric(self, name: str, value: float) -> None:
        self.metrics[name] = value
    
    def set_threshold(self, metric: str, critical_value: float) -> None:
        self.thresholds[metric] = critical_value
    
    def check_thresholds(self) -> List[Alert]:
        triggered_alerts = []
        for metric, threshold in self.thresholds.items():
            if metric in self.metrics and self.metrics[metric] > threshold:
                alert = Alert(metric, AlertSeverity.CRITICAL, "Threshold breached", datetime.now())
                triggered_alerts.append(alert)
                self.alerts.append(alert)
        return triggered_alerts
    
    def get_alerts(self) -> List[Alert]:
        return self.alerts
    
    def send_notification(self, channel: str, message: str) -> bool:
        return True
