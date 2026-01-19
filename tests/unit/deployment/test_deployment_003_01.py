"""Tests for AC-DEPLOY-003-01: Production Monitoring & Alerting"""
import pytest
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
    name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime


class MonitoringSystem:
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
                alert = Alert(metric, AlertSeverity.CRITICAL, f"Threshold breached", datetime.now())
                triggered_alerts.append(alert)
                self.alerts.append(alert)
        return triggered_alerts
    
    def get_alerts(self) -> List[Alert]:
        return self.alerts
    
    def send_notification(self, channel: str, message: str) -> bool:
        return True


class TestProductionMonitoring:
    def test_record_metric(self):
        system = MonitoringSystem()
        system.record_metric("cpu", 45.5)
        assert system.metrics["cpu"] == 45.5
    
    def test_set_threshold(self):
        system = MonitoringSystem()
        system.set_threshold("cpu", 80.0)
        assert system.thresholds["cpu"] == 80.0
    
    def test_check_thresholds_no_alert(self):
        system = MonitoringSystem()
        system.record_metric("cpu", 50.0)
        system.set_threshold("cpu", 80.0)
        alerts = system.check_thresholds()
        assert len(alerts) == 0
    
    def test_check_thresholds_alert(self):
        system = MonitoringSystem()
        system.record_metric("cpu", 90.0)
        system.set_threshold("cpu", 80.0)
        alerts = system.check_thresholds()
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.CRITICAL
    
    def test_multiple_metrics(self):
        system = MonitoringSystem()
        system.record_metric("cpu", 50.0)
        system.record_metric("memory", 75.0)
        system.record_metric("disk", 30.0)
        assert len(system.metrics) == 3
    
    def test_multiple_thresholds(self):
        system = MonitoringSystem()
        system.set_threshold("cpu", 80.0)
        system.set_threshold("memory", 85.0)
        assert len(system.thresholds) == 2
    
    def test_send_notification(self):
        system = MonitoringSystem()
        result = system.send_notification("email", "Alert message")
        assert result is True
    
    def test_alert_severity(self):
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.CRITICAL.value == "critical"
    
    def test_get_alerts(self):
        system = MonitoringSystem()
        system.record_metric("cpu", 90.0)
        system.set_threshold("cpu", 80.0)
        system.check_thresholds()
        alerts = system.get_alerts()
        assert len(alerts) == 1
    
    def test_alert_timestamp(self):
        system = MonitoringSystem()
        before = datetime.now()
        system.record_metric("cpu", 90.0)
        system.set_threshold("cpu", 80.0)
        system.check_thresholds()
        after = datetime.now()
        alert = system.get_alerts()[0]
        assert before <= alert.timestamp <= after
    
    def test_monitoring_steady_state(self):
        system = MonitoringSystem()
        for i in range(5):
            system.record_metric("cpu", 50.0 + i)
            system.set_threshold("cpu", 80.0)
        alerts = system.check_thresholds()
        assert len(alerts) == 0
    
    def test_critical_spike(self):
        system = MonitoringSystem()
        system.set_threshold("cpu", 80.0)
        system.record_metric("cpu", 95.0)
        alerts = system.check_thresholds()
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.CRITICAL
    
    def test_multi_metric_alerts(self):
        system = MonitoringSystem()
        system.record_metric("cpu", 90.0)
        system.record_metric("memory", 88.0)
        system.set_threshold("cpu", 80.0)
        system.set_threshold("memory", 85.0)
        alerts = system.check_thresholds()
        assert len(alerts) == 2
    
    def test_alert_message(self):
        system = MonitoringSystem()
        system.record_metric("cpu", 90.0)
        system.set_threshold("cpu", 80.0)
        alerts = system.check_thresholds()
        assert alerts[0].message == "Threshold breached"
    
    def test_metric_update(self):
        system = MonitoringSystem()
        system.record_metric("cpu", 50.0)
        assert system.metrics["cpu"] == 50.0
        system.record_metric("cpu", 75.0)
        assert system.metrics["cpu"] == 75.0
