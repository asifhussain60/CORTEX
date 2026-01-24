"""
BRT-026: Monitoring & Alerting

Provides comprehensive monitoring and alerting infrastructure for
resilience patterns and system health.

Test Infrastructure (RED phase - Tests Before Implementation per CORE-008)
"""

import pytest
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable, Set
from enum import Enum
from threading import Lock
import time
from datetime import datetime, timedelta


class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Alert:
    """Alert data structure."""
    alert_id: str
    severity: AlertSeverity
    title: str
    description: str
    source: str
    timestamp_ms: float = field(default_factory=lambda: time.time() * 1000)
    resolved: bool = False
    resolution_time_ms: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Metric:
    """Metric data structure."""
    metric_id: str
    name: str
    metric_type: MetricType
    value: float
    timestamp_ms: float = field(default_factory=lambda: time.time() * 1000)
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""


class MetricsCollector:
    """Collects metrics from various sources."""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self._metrics: Dict[str, Metric] = {}
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._lock = Lock()
    
    def increment_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None) -> bool:
        """Increment a counter metric."""
        with self._lock:
            if len(self._counters) >= self.max_metrics and name not in self._counters:
                return False
            
            self._counters[name] = self._counters.get(name, 0) + value
            return True
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> bool:
        """Set a gauge metric."""
        with self._lock:
            if len(self._gauges) >= self.max_metrics and name not in self._gauges:
                return False
            
            self._gauges[name] = value
            return True
    
    def record_metric(self, metric: Metric) -> bool:
        """Record a metric."""
        with self._lock:
            if len(self._metrics) >= self.max_metrics:
                # Remove oldest metric
                if self._metrics:
                    oldest_key = min(self._metrics.keys(),
                                   key=lambda k: self._metrics[k].timestamp_ms)
                    del self._metrics[oldest_key]
            
            self._metrics[metric.metric_id] = metric
            return True
    
    def get_counter(self, name: str) -> Optional[int]:
        """Get counter value."""
        with self._lock:
            return self._counters.get(name)
    
    def get_gauge(self, name: str) -> Optional[float]:
        """Get gauge value."""
        with self._lock:
            return self._gauges.get(name)
    
    def get_all_metrics(self) -> List[Metric]:
        """Get all recorded metrics."""
        with self._lock:
            return list(self._metrics.values())
    
    def get_metrics_by_type(self, metric_type: MetricType) -> List[Metric]:
        """Get metrics by type."""
        with self._lock:
            return [m for m in self._metrics.values() if m.metric_type == metric_type]


class AlertManager:
    """Manages alerts and notifications."""
    
    def __init__(self, max_alerts: int = 1000):
        self.max_alerts = max_alerts
        self._alerts: Dict[str, Alert] = {}
        self._alert_handlers: List[Callable[[Alert], None]] = []
        self._lock = Lock()
    
    def create_alert(self, alert: Alert) -> bool:
        """Create an alert."""
        with self._lock:
            if len(self._alerts) >= self.max_alerts:
                return False
            
            self._alerts[alert.alert_id] = alert
            
            # Trigger handlers
            for handler in self._alert_handlers:
                try:
                    handler(alert)
                except Exception:
                    pass
            
            return True
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        with self._lock:
            if alert_id not in self._alerts:
                return False
            
            alert = self._alerts[alert_id]
            alert.resolved = True
            alert.resolution_time_ms = time.time() * 1000 - alert.timestamp_ms
            return True
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID."""
        with self._lock:
            return self._alerts.get(alert_id)
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts."""
        with self._lock:
            return [a for a in self._alerts.values() if not a.resolved]
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts by severity."""
        with self._lock:
            return [a for a in self._alerts.values() if a.severity == severity]
    
    def register_handler(self, handler: Callable[[Alert], None]) -> bool:
        """Register an alert handler."""
        with self._lock:
            self._alert_handlers.append(handler)
            return True
    
    def clear_resolved_alerts(self) -> int:
        """Clear resolved alerts."""
        with self._lock:
            before_count = len(self._alerts)
            self._alerts = {k: v for k, v in self._alerts.items() if not v.resolved}
            return before_count - len(self._alerts)


class AlertRule:
    """Rule for triggering alerts."""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        metric_name: str,
        condition: Callable[[float], bool],
        severity: AlertSeverity,
        threshold_cooldown_ms: int = 0
    ):
        self.rule_id = rule_id
        self.name = name
        self.metric_name = metric_name
        self.condition = condition
        self.severity = severity
        self.threshold_cooldown_ms = threshold_cooldown_ms
        self._last_triggered_ms = 0
    
    def should_trigger(self, metric_value: float) -> bool:
        """Check if rule should trigger."""
        now = time.time() * 1000
        
        if now - self._last_triggered_ms < self.threshold_cooldown_ms:
            return False
        
        if self.condition(metric_value):
            self._last_triggered_ms = now
            return True
        
        return False


class AlertingEngine:
    """Engine for evaluating alert rules."""
    
    def __init__(self, metrics_collector: MetricsCollector, alert_manager: AlertManager):
        self.metrics_collector = metrics_collector
        self.alert_manager = alert_manager
        self._rules: Dict[str, AlertRule] = {}
        self._lock = Lock()
    
    def register_rule(self, rule: AlertRule) -> bool:
        """Register an alert rule."""
        with self._lock:
            if rule.rule_id in self._rules:
                return False
            
            self._rules[rule.rule_id] = rule
            return True
    
    def evaluate_rules(self) -> int:
        """Evaluate all rules against current metrics."""
        alerts_triggered = 0
        
        with self._lock:
            rules = list(self._rules.values())
        
        for rule in rules:
            # Get metric value
            counter = self.metrics_collector.get_counter(rule.metric_name)
            gauge = self.metrics_collector.get_gauge(rule.metric_name)
            
            value = counter if counter is not None else gauge
            if value is None:
                continue
            
            if rule.should_trigger(float(value)):
                alert = Alert(
                    alert_id=f"alert_{rule.rule_id}_{int(time.time() * 1000)}",
                    severity=rule.severity,
                    title=rule.name,
                    description=f"Alert rule '{rule.name}' triggered for metric '{rule.metric_name}'",
                    source=rule.metric_name
                )
                
                if self.alert_manager.create_alert(alert):
                    alerts_triggered += 1
        
        return alerts_triggered


class HealthCheck:
    """Health check for a system component."""
    
    def __init__(self, name: str, check_fn: Callable[[], bool], interval_ms: int = 10000):
        self.name = name
        self.check_fn = check_fn
        self.interval_ms = interval_ms
        self.last_check_ms = 0
        self.is_healthy = True
    
    def execute(self) -> bool:
        """Execute health check."""
        now = time.time() * 1000
        
        if now - self.last_check_ms < self.interval_ms:
            return self.is_healthy
        
        try:
            self.is_healthy = self.check_fn()
            self.last_check_ms = now
        except Exception:
            self.is_healthy = False
        
        return self.is_healthy


class HealthCheckManager:
    """Manages health checks."""
    
    def __init__(self):
        self._checks: Dict[str, HealthCheck] = {}
        self._lock = Lock()
    
    def register_check(self, check: HealthCheck) -> bool:
        """Register a health check."""
        with self._lock:
            if check.name in self._checks:
                return False
            
            self._checks[check.name] = check
            return True
    
    def run_all_checks(self) -> Dict[str, bool]:
        """Run all health checks."""
        results = {}
        
        with self._lock:
            checks = list(self._checks.values())
        
        for check in checks:
            results[check.name] = check.execute()
        
        return results
    
    def get_overall_health(self) -> bool:
        """Get overall system health."""
        results = self.run_all_checks()
        return all(results.values()) if results else True
    
    def get_check_status(self, name: str) -> Optional[bool]:
        """Get status of specific check."""
        with self._lock:
            check = self._checks.get(name)
            return check.is_healthy if check else None


class Dashboard:
    """Monitoring dashboard."""
    
    def __init__(
        self,
        metrics_collector: MetricsCollector,
        alert_manager: AlertManager,
        health_check_manager: HealthCheckManager
    ):
        self.metrics_collector = metrics_collector
        self.alert_manager = alert_manager
        self.health_check_manager = health_check_manager
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard."""
        return {
            "timestamp": time.time() * 1000,
            "active_alerts": len(self.alert_manager.get_active_alerts()),
            "critical_alerts": len(self.alert_manager.get_alerts_by_severity(AlertSeverity.CRITICAL)),
            "metrics_count": len(self.metrics_collector.get_all_metrics()),
            "system_healthy": self.health_check_manager.get_overall_health(),
            "alert_breakdown": {
                "critical": len(self.alert_manager.get_alerts_by_severity(AlertSeverity.CRITICAL)),
                "high": len(self.alert_manager.get_alerts_by_severity(AlertSeverity.HIGH)),
                "medium": len(self.alert_manager.get_alerts_by_severity(AlertSeverity.MEDIUM)),
                "low": len(self.alert_manager.get_alerts_by_severity(AlertSeverity.LOW)),
            }
        }


# ============================================================================
# TEST SUITE
# ============================================================================

class TestMetricsCollector:
    """Test MetricsCollector functionality."""
    
    def test_increment_counter(self):
        """Test incrementing counter."""
        collector = MetricsCollector()
        
        assert collector.increment_counter("requests")
        assert collector.get_counter("requests") == 1
    
    def test_increment_counter_multiple_times(self):
        """Test incrementing counter multiple times."""
        collector = MetricsCollector()
        
        collector.increment_counter("requests", 5)
        collector.increment_counter("requests", 3)
        
        assert collector.get_counter("requests") == 8
    
    def test_set_gauge(self):
        """Test setting gauge."""
        collector = MetricsCollector()
        
        assert collector.set_gauge("memory_usage", 85.5)
        assert collector.get_gauge("memory_usage") == 85.5
    
    def test_record_metric(self):
        """Test recording metric."""
        collector = MetricsCollector()
        
        metric = Metric(
            metric_id="m1",
            name="response_time",
            metric_type=MetricType.TIMER,
            value=125.5
        )
        
        assert collector.record_metric(metric)
        assert len(collector.get_all_metrics()) == 1
    
    def test_get_metrics_by_type(self):
        """Test getting metrics by type."""
        collector = MetricsCollector()
        
        metric1 = Metric(
            metric_id="m1",
            name="requests",
            metric_type=MetricType.COUNTER,
            value=100
        )
        metric2 = Metric(
            metric_id="m2",
            name="memory",
            metric_type=MetricType.GAUGE,
            value=85.5
        )
        
        collector.record_metric(metric1)
        collector.record_metric(metric2)
        
        counters = collector.get_metrics_by_type(MetricType.COUNTER)
        assert len(counters) == 1
        assert counters[0].name == "requests"


class TestAlertManager:
    """Test AlertManager functionality."""
    
    def test_create_alert(self):
        """Test creating alert."""
        manager = AlertManager()
        
        alert = Alert(
            alert_id="a1",
            severity=AlertSeverity.HIGH,
            title="High latency",
            description="Response time exceeds threshold",
            source="api"
        )
        
        assert manager.create_alert(alert)
        assert manager.get_alert("a1") is not None
    
    def test_resolve_alert(self):
        """Test resolving alert."""
        manager = AlertManager()
        
        alert = Alert(
            alert_id="a1",
            severity=AlertSeverity.HIGH,
            title="Test",
            description="Test alert",
            source="test"
        )
        
        manager.create_alert(alert)
        assert manager.resolve_alert("a1")
        
        resolved = manager.get_alert("a1")
        assert resolved.resolved is True
    
    def test_get_active_alerts(self):
        """Test getting active alerts."""
        manager = AlertManager()
        
        alert1 = Alert(
            alert_id="a1",
            severity=AlertSeverity.HIGH,
            title="Alert 1",
            description="Test",
            source="test"
        )
        alert2 = Alert(
            alert_id="a2",
            severity=AlertSeverity.MEDIUM,
            title="Alert 2",
            description="Test",
            source="test"
        )
        
        manager.create_alert(alert1)
        manager.create_alert(alert2)
        manager.resolve_alert("a1")
        
        active = manager.get_active_alerts()
        assert len(active) == 1
        assert active[0].alert_id == "a2"
    
    def test_get_alerts_by_severity(self):
        """Test getting alerts by severity."""
        manager = AlertManager()
        
        alert1 = Alert(
            alert_id="a1",
            severity=AlertSeverity.CRITICAL,
            title="Critical",
            description="Test",
            source="test"
        )
        alert2 = Alert(
            alert_id="a2",
            severity=AlertSeverity.HIGH,
            title="High",
            description="Test",
            source="test"
        )
        
        manager.create_alert(alert1)
        manager.create_alert(alert2)
        
        critical = manager.get_alerts_by_severity(AlertSeverity.CRITICAL)
        assert len(critical) == 1
    
    def test_register_handler(self):
        """Test registering alert handler."""
        manager = AlertManager()
        
        handled_alerts = []
        def handler(alert: Alert):
            handled_alerts.append(alert)
        
        manager.register_handler(handler)
        
        alert = Alert(
            alert_id="a1",
            severity=AlertSeverity.HIGH,
            title="Test",
            description="Test",
            source="test"
        )
        manager.create_alert(alert)
        
        assert len(handled_alerts) == 1


class TestAlertRule:
    """Test AlertRule functionality."""
    
    def test_rule_trigger_condition_met(self):
        """Test rule triggers when condition met."""
        rule = AlertRule(
            rule_id="r1",
            name="High error rate",
            metric_name="error_rate",
            condition=lambda x: x > 10,
            severity=AlertSeverity.HIGH
        )
        
        assert rule.should_trigger(15)
    
    def test_rule_no_trigger_condition_not_met(self):
        """Test rule doesn't trigger when condition not met."""
        rule = AlertRule(
            rule_id="r1",
            name="High error rate",
            metric_name="error_rate",
            condition=lambda x: x > 10,
            severity=AlertSeverity.HIGH
        )
        
        assert not rule.should_trigger(5)
    
    def test_rule_cooldown(self):
        """Test rule cooldown."""
        rule = AlertRule(
            rule_id="r1",
            name="High error rate",
            metric_name="error_rate",
            condition=lambda x: x > 10,
            severity=AlertSeverity.HIGH,
            threshold_cooldown_ms=1000
        )
        
        assert rule.should_trigger(15)
        assert not rule.should_trigger(15)  # Still in cooldown


class TestHealthCheck:
    """Test HealthCheck functionality."""
    
    def test_health_check_healthy(self):
        """Test healthy check."""
        def check_fn():
            return True
        
        check = HealthCheck("api", check_fn, interval_ms=0)
        assert check.execute() is True
    
    def test_health_check_unhealthy(self):
        """Test unhealthy check."""
        def check_fn():
            return False
        
        check = HealthCheck("db", check_fn, interval_ms=0)
        assert check.execute() is False
    
    def test_health_check_interval(self):
        """Test health check interval."""
        call_count = 0
        def check_fn():
            nonlocal call_count
            call_count += 1
            return True
        
        check = HealthCheck("service", check_fn, interval_ms=100000)
        check.execute()
        check.execute()
        
        # Should only call once due to interval
        assert call_count == 1


class TestHealthCheckManager:
    """Test HealthCheckManager functionality."""
    
    def test_register_check(self):
        """Test registering health check."""
        manager = HealthCheckManager()
        check = HealthCheck("api", lambda: True, interval_ms=0)
        
        assert manager.register_check(check)
    
    def test_run_all_checks(self):
        """Test running all checks."""
        manager = HealthCheckManager()
        
        check1 = HealthCheck("api", lambda: True, interval_ms=0)
        check2 = HealthCheck("db", lambda: False, interval_ms=0)
        
        manager.register_check(check1)
        manager.register_check(check2)
        
        results = manager.run_all_checks()
        assert results["api"] is True
        assert results["db"] is False
    
    def test_get_overall_health(self):
        """Test getting overall health."""
        manager = HealthCheckManager()
        
        check1 = HealthCheck("api", lambda: True, interval_ms=0)
        check2 = HealthCheck("db", lambda: False, interval_ms=0)
        
        manager.register_check(check1)
        manager.register_check(check2)
        
        assert manager.get_overall_health() is False


class TestAlertingEngine:
    """Test AlertingEngine functionality."""
    
    def test_register_rule(self):
        """Test registering alert rule."""
        collector = MetricsCollector()
        manager = AlertManager()
        engine = AlertingEngine(collector, manager)
        
        rule = AlertRule(
            rule_id="r1",
            name="High errors",
            metric_name="errors",
            condition=lambda x: x > 100,
            severity=AlertSeverity.CRITICAL
        )
        
        assert engine.register_rule(rule)
    
    def test_evaluate_rules(self):
        """Test evaluating rules."""
        collector = MetricsCollector()
        manager = AlertManager()
        engine = AlertingEngine(collector, manager)
        
        collector.increment_counter("errors", 150)
        
        rule = AlertRule(
            rule_id="r1",
            name="High errors",
            metric_name="errors",
            condition=lambda x: x > 100,
            severity=AlertSeverity.CRITICAL
        )
        
        engine.register_rule(rule)
        alerts = engine.evaluate_rules()
        
        assert alerts > 0


class TestDashboard:
    """Test Dashboard functionality."""
    
    def test_get_dashboard_data(self):
        """Test getting dashboard data."""
        collector = MetricsCollector()
        manager = AlertManager()
        health_mgr = HealthCheckManager()
        
        dashboard = Dashboard(collector, manager, health_mgr)
        data = dashboard.get_dashboard_data()
        
        assert "timestamp" in data
        assert "active_alerts" in data
        assert "system_healthy" in data
    
    def test_dashboard_with_alerts(self):
        """Test dashboard with active alerts."""
        collector = MetricsCollector()
        manager = AlertManager()
        health_mgr = HealthCheckManager()
        
        dashboard = Dashboard(collector, manager, health_mgr)
        
        alert = Alert(
            alert_id="a1",
            severity=AlertSeverity.CRITICAL,
            title="Critical",
            description="Test",
            source="test"
        )
        manager.create_alert(alert)
        
        data = dashboard.get_dashboard_data()
        assert data["active_alerts"] == 1
        assert data["critical_alerts"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
