"""
CORTEX Audit Logger - Alert Manager
Version: 1.0.0
Purpose: Monitoring, metrics collection, and alerting with Grafana integration
"""

import json
import logging
import os
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class Alert:
    """Alert representation"""
    
    def __init__(
        self,
        name: str,
        severity: AlertSeverity,
        message: str,
        metric_name: str,
        current_value: float,
        threshold: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.severity = severity
        self.message = message
        self.metric_name = metric_name
        self.current_value = current_value
        self.threshold = threshold
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.resolved = False
        self.resolved_at: Optional[datetime] = None
        
    def resolve(self) -> None:
        """Mark alert as resolved"""
        self.resolved = True
        self.resolved_at = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "name": self.name,
            "severity": self.severity.value,
            "message": self.message,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }


class Metric:
    """Metric with time-series data"""
    
    def __init__(self, name: str, metric_type: MetricType, description: str = ""):
        self.name = name
        self.type = metric_type
        self.description = description
        self.values = deque(maxlen=10000)  # Keep last 10k datapoints
        self.labels: Dict[str, str] = {}
        self.created_at = datetime.now()
        
    def record(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a metric value"""
        datapoint = {
            "timestamp": datetime.now(),
            "value": value,
            "labels": labels or {}
        }
        self.values.append(datapoint)
        
    def get_latest(self) -> Optional[float]:
        """Get latest metric value"""
        if not self.values:
            return None
        return self.values[-1]["value"]
        
    def get_average(self, window_seconds: int = 60) -> Optional[float]:
        """Get average value over time window"""
        cutoff = datetime.now() - timedelta(seconds=window_seconds)
        values = [
            dp["value"] for dp in self.values
            if dp["timestamp"] > cutoff
        ]
        
        if not values:
            return None
            
        return sum(values) / len(values)
        
    def get_percentile(self, percentile: float, window_seconds: int = 60) -> Optional[float]:
        """Get percentile value over time window"""
        cutoff = datetime.now() - timedelta(seconds=window_seconds)
        values = sorted([
            dp["value"] for dp in self.values
            if dp["timestamp"] > cutoff
        ])
        
        if not values:
            return None
            
        index = int(len(values) * (percentile / 100))
        return values[min(index, len(values) - 1)]
        
    def to_prometheus_format(self) -> str:
        """Export to Prometheus text format"""
        lines = []
        
        # HELP line
        lines.append(f"# HELP {self.name} {self.description}")
        
        # TYPE line
        lines.append(f"# TYPE {self.name} {self.type.value}")
        
        # Metric lines (latest value)
        if self.values:
            latest = self.values[-1]
            label_str = ",".join([f'{k}="{v}"' for k, v in latest["labels"].items()])
            if label_str:
                lines.append(f"{self.name}{{{label_str}}} {latest['value']}")
            else:
                lines.append(f"{self.name} {latest['value']}")
                
        return "\n".join(lines)


class AlertManager:
    """
    Alert management and monitoring system
    
    Features:
    - Log volume metrics
    - Error rate alerts
    - Performance degradation alerts
    - Self-healing success tracking
    - Grafana dashboard integration
    - Prometheus metrics export
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Metrics storage
        self.metrics: Dict[str, Metric] = {}
        
        # Active alerts
        self.active_alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
        
        # Alert rules
        self.alert_rules: List[Dict[str, Any]] = []
        
        # Notification handlers
        self.notification_handlers: List[Callable] = []
        
        # Background monitoring
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_active = False
        self._stop_monitoring = threading.Event()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Initialize default metrics
        self._init_default_metrics()
        
        # Load alert rules from config
        self._load_alert_rules()
        
    def _init_default_metrics(self) -> None:
        """Initialize default metrics"""
        # Log volume metrics
        self.register_metric("audit_log_entries_total", MetricType.COUNTER, "Total audit log entries")
        self.register_metric("audit_log_entries_per_minute", MetricType.GAUGE, "Log entries per minute")
        self.register_metric("audit_log_size_bytes", MetricType.GAUGE, "Total log size in bytes")
        
        # Error metrics
        self.register_metric("audit_errors_total", MetricType.COUNTER, "Total audit logger errors")
        self.register_metric("audit_error_rate_per_minute", MetricType.GAUGE, "Error rate per minute")
        
        # Performance metrics
        self.register_metric("audit_write_latency_ms", MetricType.HISTOGRAM, "Log write latency in ms")
        self.register_metric("audit_write_latency_p50", MetricType.GAUGE, "P50 write latency")
        self.register_metric("audit_write_latency_p95", MetricType.GAUGE, "P95 write latency")
        self.register_metric("audit_write_latency_p99", MetricType.GAUGE, "P99 write latency")
        
        # Buffer metrics
        self.register_metric("audit_buffer_size", MetricType.GAUGE, "Current buffer size")
        self.register_metric("audit_buffer_overflow_total", MetricType.COUNTER, "Buffer overflow count")
        
        # Self-healing metrics
        self.register_metric("audit_self_healing_attempts_total", MetricType.COUNTER, "Self-healing attempts")
        self.register_metric("audit_self_healing_success_total", MetricType.COUNTER, "Successful self-healing")
        self.register_metric("audit_self_healing_success_rate", MetricType.GAUGE, "Self-healing success rate %")
        
        # Degradation metrics
        self.register_metric("audit_degradation_events_total", MetricType.COUNTER, "Degradation events")
        self.register_metric("audit_operational_mode", MetricType.GAUGE, "Current operational mode (0=normal, 1=memory, 2=stderr, 3=reduced, 4=disabled)")
        
    def _load_alert_rules(self) -> None:
        """Load alert rules from configuration"""
        rules = self.config.get("alert_rules", [])
        
        # Default rules if none configured
        if not rules:
            rules = [
                {
                    "name": "high_error_rate",
                    "metric": "audit_error_rate_per_minute",
                    "condition": ">",
                    "threshold": 10,
                    "severity": "warning",
                    "message": "High error rate detected: {current_value}/min (threshold: {threshold}/min)"
                },
                {
                    "name": "critical_error_rate",
                    "metric": "audit_error_rate_per_minute",
                    "condition": ">",
                    "threshold": 50,
                    "severity": "critical",
                    "message": "CRITICAL error rate: {current_value}/min (threshold: {threshold}/min)"
                },
                {
                    "name": "performance_degradation",
                    "metric": "audit_write_latency_p95",
                    "condition": ">",
                    "threshold": 100,
                    "severity": "warning",
                    "message": "Performance degradation: P95 latency {current_value}ms (threshold: {threshold}ms)"
                },
                {
                    "name": "buffer_overflow",
                    "metric": "audit_buffer_overflow_total",
                    "condition": ">",
                    "threshold": 0,
                    "severity": "error",
                    "message": "Buffer overflow detected: {current_value} overflows"
                },
                {
                    "name": "low_self_healing_success",
                    "metric": "audit_self_healing_success_rate",
                    "condition": "<",
                    "threshold": 90,
                    "severity": "warning",
                    "message": "Low self-healing success rate: {current_value}% (threshold: {threshold}%)"
                },
                {
                    "name": "operational_mode_degraded",
                    "metric": "audit_operational_mode",
                    "condition": ">",
                    "threshold": 0,
                    "severity": "warning",
                    "message": "System operating in degraded mode: {current_value}"
                }
            ]
            
        self.alert_rules = rules
        
    def register_metric(self, name: str, metric_type: MetricType, description: str = "") -> None:
        """Register a new metric"""
        with self._lock:
            if name not in self.metrics:
                self.metrics[name] = Metric(name, metric_type, description)
                
    def record_metric(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a metric value"""
        with self._lock:
            if name in self.metrics:
                self.metrics[name].record(value, labels)
            else:
                logger.warning(f"Attempted to record unknown metric: {name}")
                
    def get_metric(self, name: str) -> Optional[Metric]:
        """Get metric by name"""
        return self.metrics.get(name)
        
    def evaluate_alerts(self) -> List[Alert]:
        """Evaluate all alert rules and generate alerts"""
        new_alerts = []
        
        with self._lock:
            for rule in self.alert_rules:
                metric_name = rule["metric"]
                metric = self.metrics.get(metric_name)
                
                if not metric:
                    continue
                    
                current_value = metric.get_latest()
                if current_value is None:
                    continue
                    
                threshold = rule["threshold"]
                condition = rule["condition"]
                
                # Evaluate condition
                triggered = False
                if condition == ">" and current_value > threshold:
                    triggered = True
                elif condition == "<" and current_value < threshold:
                    triggered = True
                elif condition == "==" and current_value == threshold:
                    triggered = True
                elif condition == ">=" and current_value >= threshold:
                    triggered = True
                elif condition == "<=" and current_value <= threshold:
                    triggered = True
                    
                if triggered:
                    # Check if alert already exists
                    existing = next(
                        (a for a in self.active_alerts if a.name == rule["name"]),
                        None
                    )
                    
                    if not existing:
                        # Create new alert
                        severity = AlertSeverity(rule["severity"])
                        message = rule["message"].format(
                            current_value=current_value,
                            threshold=threshold
                        )
                        
                        alert = Alert(
                            name=rule["name"],
                            severity=severity,
                            message=message,
                            metric_name=metric_name,
                            current_value=current_value,
                            threshold=threshold
                        )
                        
                        self.active_alerts.append(alert)
                        new_alerts.append(alert)
                        
                        # Send notifications
                        self._send_notifications(alert)
                        
                else:
                    # Resolve existing alert if condition no longer met
                    existing = next(
                        (a for a in self.active_alerts if a.name == rule["name"]),
                        None
                    )
                    
                    if existing and not existing.resolved:
                        existing.resolve()
                        self.alert_history.append(existing)
                        self.active_alerts.remove(existing)
                        
        return new_alerts
        
    def _send_notifications(self, alert: Alert) -> None:
        """Send alert notifications"""
        for handler in self.notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Notification handler failed: {e}")
                
    def add_notification_handler(self, handler: Callable[[Alert], None]) -> None:
        """Add notification handler"""
        self.notification_handlers.append(handler)
        
    def start_monitoring(self, interval: int = 30) -> None:
        """Start background monitoring thread"""
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info(f"Started monitoring with {interval}s interval")
        
    def stop_monitoring(self) -> None:
        """Stop background monitoring"""
        self.monitoring_active = False
        self._stop_monitoring.set()
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Stopped monitoring")
        
    def _monitoring_loop(self, interval: int) -> None:
        """Background monitoring loop"""
        while self.monitoring_active and not self._stop_monitoring.is_set():
            try:
                self.evaluate_alerts()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                
            self._stop_monitoring.wait(interval)
            
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self.active_alerts)
        
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history"""
        return list(self.alert_history[-limit:])
        
    def export_prometheus_metrics(self) -> str:
        """Export all metrics in Prometheus format"""
        lines = []
        for metric in self.metrics.values():
            lines.append(metric.to_prometheus_format())
        return "\n\n".join(lines)
        
    def export_grafana_dashboard(self, output_path: str) -> None:
        """Export Grafana dashboard JSON"""
        dashboard = {
            "dashboard": {
                "title": "CORTEX Audit Logger Monitoring",
                "tags": ["cortex", "audit-logger"],
                "timezone": "browser",
                "panels": self._generate_grafana_panels(),
                "time": {
                    "from": "now-6h",
                    "to": "now"
                },
                "refresh": "30s"
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(dashboard, f, indent=2)
            
        logger.info(f"Exported Grafana dashboard to: {output_path}")
        
    def _generate_grafana_panels(self) -> List[Dict[str, Any]]:
        """Generate Grafana dashboard panels"""
        panels = [
            {
                "id": 1,
                "title": "Log Volume",
                "type": "graph",
                "targets": [
                    {"expr": "rate(audit_log_entries_total[5m])"}
                ]
            },
            {
                "id": 2,
                "title": "Error Rate",
                "type": "graph",
                "targets": [
                    {"expr": "audit_error_rate_per_minute"}
                ]
            },
            {
                "id": 3,
                "title": "Write Latency (P50, P95, P99)",
                "type": "graph",
                "targets": [
                    {"expr": "audit_write_latency_p50"},
                    {"expr": "audit_write_latency_p95"},
                    {"expr": "audit_write_latency_p99"}
                ]
            },
            {
                "id": 4,
                "title": "Self-Healing Success Rate",
                "type": "gauge",
                "targets": [
                    {"expr": "audit_self_healing_success_rate"}
                ]
            },
            {
                "id": 5,
                "title": "Buffer Utilization",
                "type": "graph",
                "targets": [
                    {"expr": "audit_buffer_size"}
                ]
            },
            {
                "id": 6,
                "title": "Operational Mode",
                "type": "stat",
                "targets": [
                    {"expr": "audit_operational_mode"}
                ]
            }
        ]
        return panels
        
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary with key metrics"""
        return {
            "active_alerts": len(self.active_alerts),
            "total_metrics": len(self.metrics),
            "log_volume_per_minute": self.metrics.get("audit_log_entries_per_minute").get_latest() if "audit_log_entries_per_minute" in self.metrics else 0,
            "error_rate_per_minute": self.metrics.get("audit_error_rate_per_minute").get_latest() if "audit_error_rate_per_minute" in self.metrics else 0,
            "p95_latency_ms": self.metrics.get("audit_write_latency_p95").get_latest() if "audit_write_latency_p95" in self.metrics else 0,
            "self_healing_success_rate": self.metrics.get("audit_self_healing_success_rate").get_latest() if "audit_self_healing_success_rate" in self.metrics else 100,
            "operational_mode": self.metrics.get("audit_operational_mode").get_latest() if "audit_operational_mode" in self.metrics else 0,
            "timestamp": datetime.now().isoformat()
        }


# Global instance
_alert_manager = AlertManager()


def get_alert_manager() -> AlertManager:
    """Get global alert manager instance"""
    return _alert_manager
