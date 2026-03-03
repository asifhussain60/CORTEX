"""
Monitoring — MetricsCollector, RealTimeProgressDashboard, AlertManager, and supporting types.

Phase 103-f: extracted from resilience.py (1,876L) god-object.
"""
# noqa: CORE-035 — domain-scoped; Alert/AlertManager intentionally parallel infrastructure copies
from __future__ import annotations

import abc
import logging
from datetime import datetime
from enum import Enum
from threading import RLock
from typing import Any, Dict, List, Optional

from cortex.models.canonical_enums import AlertSeverity

logger = logging.getLogger(__name__)


# ===== AC-NFR-004-01: Metrics =====


class MetricUnit(Enum):
    """Standard metric units."""

    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    BYTES = "bytes"
    REQUESTS = "requests"
    PERCENTAGE = "percentage"


class MetricValue:
    """Encapsulates a metric measurement with metadata."""

    def __init__(
        self,
        value: float,
        unit: MetricUnit,
        timestamp: Optional[datetime] = None,
        labels: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize metric value."""
        self.value = value
        self.unit = unit
        self.timestamp = timestamp or datetime.utcnow()
        self.labels = labels or {}


class MetricExportConfig:
    """Configuration for metric export."""

    def __init__(
        self,
        endpoint: str = "http://localhost:9090",
        batch_size: int = 100,
        flush_interval_ms: int = 5000,
    ) -> None:
        """Initialize export configuration."""
        self.endpoint = endpoint
        self.batch_size = batch_size
        self.flush_interval_ms = flush_interval_ms


class InstrumentationSpan:
    """Represents a span for tracing and instrumentation."""

    def __init__(
        self,
        name: str,
        operation: str = "default",
        resource_name: str = "unknown",
    ) -> None:
        """Initialize instrumentation span."""
        self.name = name
        self.operation = operation
        self.resource_name = resource_name
        self._attributes: Dict[str, Any] = {}
        self._events: List[str] = []
        self._start_time = datetime.utcnow()

    def add_attribute(self, key: str, value: Any) -> None:
        """Add attribute to span."""
        self._attributes[key] = value

    def add_event(self, event: str) -> None:
        """Record event in span."""
        self._events.append(event)
        logger.debug(f"Span '{self.name}' event: {event}")

    def get_attributes(self) -> Dict[str, Any]:
        """Get all span attributes."""
        return self._attributes.copy()

    def get_events(self) -> List[str]:
        """Get all span events."""
        return self._events.copy()


class MetricsCollector:
    """
    Collects and exports metrics to observability backends.

    Supports counter, gauge, and histogram metrics with labels
    and dimensional data for observability.
    """

    def __init__(self, config: Optional[MetricExportConfig] = None) -> None:
        """Initialize metrics collector."""
        self.config = config or MetricExportConfig()
        self._metrics: Dict[str, Dict[str, Any]] = {}
        self._lock = RLock()
        logger.debug(f"MetricsCollector initialized with endpoint: {self.config.endpoint}")

    def counter(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record counter metric (monotonically increasing)."""
        with self._lock:
            if metric_name not in self._metrics:
                self._metrics[metric_name] = {
                    "type": "counter",
                    "value": 0,
                    "labels": labels or {},
                }
            self._metrics[metric_name]["value"] += value
        logger.debug(f"Counter '{metric_name}' incremented by {value}")

    def gauge(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record gauge metric (snapshot value)."""
        with self._lock:
            self._metrics[metric_name] = {
                "type": "gauge",
                "value": value,
                "labels": labels or {},
                "timestamp": datetime.utcnow(),
            }
        logger.debug(f"Gauge '{metric_name}' set to {value}")

    def histogram(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record histogram metric (distribution of values)."""
        with self._lock:
            if metric_name not in self._metrics:
                self._metrics[metric_name] = {
                    "type": "histogram",
                    "values": [],
                    "labels": labels or {},
                }
            self._metrics[metric_name]["values"].append(value)
        logger.debug(f"Histogram '{metric_name}' recorded value {value}")

    def summary(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record summary metric (similar to histogram)."""
        with self._lock:
            if metric_name not in self._metrics:
                self._metrics[metric_name] = {
                    "type": "summary",
                    "values": [],
                    "labels": labels or {},
                }
            self._metrics[metric_name]["values"].append(value)
        logger.debug(f"Summary '{metric_name}' recorded value {value}")

    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all collected metrics."""
        with self._lock:
            return self._metrics.copy()

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._metrics.clear()
        logger.info("MetricsCollector reset")


# ===== AC-NFR-004-02: Real-Time Progress Dashboard =====


class DashboardUpdateType(Enum):
    """Types of dashboard updates."""

    PROGRESS = "progress"
    STATUS = "status"
    ERROR = "error"
    ALERT = "alert"


class DashboardUpdate:
    """Represents a single dashboard update."""

    def __init__(
        self,
        operation_id: str,
        update_type: DashboardUpdateType,
        value: Any,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Initialize dashboard update."""
        self.operation_id = operation_id
        self.update_type = update_type
        self.value = value
        self.timestamp = timestamp or datetime.utcnow()


class DashboardMetrics:
    """Metrics for a single operation on the dashboard."""

    def __init__(
        self,
        operation_id: str,
        progress: float = 0.0,
        status: str = "Idle",
        start_time: Optional[datetime] = None,
    ) -> None:
        """Initialize dashboard metrics."""
        self.operation_id = operation_id
        self.progress = max(0.0, min(1.0, progress))
        self.status = status
        self.start_time = start_time or datetime.utcnow()
        self.errors: List[str] = []
        self.alerts: List[Dict[str, Any]] = []


class RealTimeProgressDashboard:
    """
    Real-time progress dashboard for live operation monitoring.

    Provides sub-second update frequency for displaying operation
    progress, status, errors, and alerts to subscribers.
    """

    def __init__(self) -> None:
        """Initialize dashboard."""
        self._metrics: Dict[str, Dict[str, Any]] = {}
        self._subscribers: List[Any] = []
        self._history: List[DashboardUpdate] = []
        self._lock = RLock()
        logger.debug("RealTimeProgressDashboard initialized")

    def update_progress(self, operation_id: str, progress: float) -> None:
        """Update operation progress (0.0-1.0)."""
        progress = max(0.0, min(1.0, progress))
        with self._lock:
            if operation_id not in self._metrics:
                self._metrics[operation_id] = {
                    "progress": 0.0,
                    "status": "Idle",
                    "start_time": datetime.utcnow(),
                    "errors": [],
                    "alerts": [],
                }
            self._metrics[operation_id]["progress"] = progress
            self._metrics[operation_id]["last_update"] = datetime.utcnow()
            self._history.append(
                DashboardUpdate(operation_id, DashboardUpdateType.PROGRESS, progress)
            )
        self._notify_subscribers(operation_id)
        logger.debug(f"Operation '{operation_id}' progress: {progress * 100:.1f}%")

    def update_status(self, operation_id: str, status: str) -> None:
        """Update operation status message."""
        with self._lock:
            if operation_id not in self._metrics:
                self._metrics[operation_id] = {
                    "progress": 0.0,
                    "status": status,
                    "start_time": datetime.utcnow(),
                    "errors": [],
                    "alerts": [],
                }
            else:
                self._metrics[operation_id]["status"] = status
            self._metrics[operation_id]["last_update"] = datetime.utcnow()
            self._history.append(
                DashboardUpdate(operation_id, DashboardUpdateType.STATUS, status)
            )
        self._notify_subscribers(operation_id)
        logger.debug(f"Operation '{operation_id}' status: {status}")

    def record_error(self, operation_id: str, error_message: str) -> None:
        """Record operation error."""
        with self._lock:
            if operation_id not in self._metrics:
                self._metrics[operation_id] = {
                    "progress": 0.0,
                    "status": "Error",
                    "start_time": datetime.utcnow(),
                    "errors": [],
                    "alerts": [],
                }
            self._metrics[operation_id]["errors"].append(error_message)
            self._metrics[operation_id]["last_update"] = datetime.utcnow()
            self._history.append(
                DashboardUpdate(operation_id, DashboardUpdateType.ERROR, error_message)
            )
        self._notify_subscribers(operation_id)
        logger.error(f"Operation '{operation_id}' error: {error_message}")

    def record_alert(
        self,
        operation_id: str,
        alert_message: str,
        severity: str = "info",
    ) -> None:
        """Record operation alert."""
        with self._lock:
            if operation_id not in self._metrics:
                self._metrics[operation_id] = {
                    "progress": 0.0,
                    "status": "Idle",
                    "start_time": datetime.utcnow(),
                    "errors": [],
                    "alerts": [],
                }
            alert = {
                "message": alert_message,
                "severity": severity,
                "timestamp": datetime.utcnow(),
            }
            self._metrics[operation_id]["alerts"].append(alert)
            self._metrics[operation_id]["last_update"] = datetime.utcnow()
            self._history.append(
                DashboardUpdate(operation_id, DashboardUpdateType.ALERT, alert)
            )
        self._notify_subscribers(operation_id)
        logger.warning(f"Operation '{operation_id}' alert ({severity}): {alert_message}")

    def subscribe(self, callback: Any) -> None:
        """Subscribe to dashboard updates."""
        with self._lock:
            self._subscribers.append(callback)

    def _notify_subscribers(self, operation_id: str) -> None:
        """Notify all subscribers of update."""
        with self._lock:
            subscribers = self._subscribers.copy()
        for subscriber in subscribers:
            try:
                subscriber(operation_id, self._metrics.get(operation_id, {}))
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")

    def get_current_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get current metrics for all operations."""
        with self._lock:
            return self._metrics.copy()

    def get_history(self, max_entries: int = 1000) -> List[DashboardUpdate]:
        """Get update history."""
        with self._lock:
            return self._history[-max_entries:].copy()


# ===== AC-NFR-004-03: Alert Management System =====


class ThresholdOperator(Enum):
    """Threshold comparison operators."""

    GREATER_THAN = ">"
    LESS_THAN = "<"
    EQUAL = "=="
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="


class Threshold:
    """Threshold definition with operator and value."""

    def __init__(self, operator: ThresholdOperator, value: float) -> None:
        """Initialize threshold."""
        self.operator = operator
        self.value = value

    def evaluate(self, current_value: float) -> bool:
        """Evaluate if current value breaches threshold."""
        if self.operator == ThresholdOperator.GREATER_THAN:
            return current_value > self.value
        elif self.operator == ThresholdOperator.LESS_THAN:
            return current_value < self.value
        elif self.operator == ThresholdOperator.EQUAL:
            return current_value == self.value
        elif self.operator == ThresholdOperator.GREATER_EQUAL:
            return current_value >= self.value
        elif self.operator == ThresholdOperator.LESS_EQUAL:
            return current_value <= self.value
        return False


class Alert:
    """Represents a single alert instance."""

    def __init__(
        self,
        alert_id: str,
        metric_name: str,
        severity: AlertSeverity,
        threshold: float,
        current_value: float,
        created_at: Optional[datetime] = None,
    ) -> None:
        """Initialize alert."""
        self.alert_id = alert_id
        self.metric_name = metric_name
        self.severity = severity
        self.threshold = threshold
        self.current_value = current_value
        self.created_at = created_at or datetime.utcnow()
        self.status = "active"
        self.acknowledged_at: Optional[datetime] = None
        self.resolved_at: Optional[datetime] = None

    def acknowledge(self) -> None:
        """Acknowledge the alert."""
        self.status = "acknowledged"
        self.acknowledged_at = datetime.utcnow()
        logger.info(f"Alert {self.alert_id} acknowledged")

    def resolve(self) -> None:
        """Resolve the alert."""
        self.status = "resolved"
        self.resolved_at = datetime.utcnow()
        logger.info(f"Alert {self.alert_id} resolved")


class NotificationChannel(abc.ABC):
    """Abstract base class for notification channels."""

    @abc.abstractmethod
    def notify(self, alert: Alert) -> None:
        """Send notification for alert."""


class AlertManager:
    """
    Manages alert rules and triggering based on metrics.

    Supports threshold-based alerting with multiple notification
    channels and alert lifecycle management.
    """

    def __init__(self) -> None:
        """Initialize alert manager."""
        self._rules: Dict[str, List[Dict[str, Any]]] = {}
        self._active_alerts: List[Alert] = []
        self._alert_history: List[Alert] = []
        self._channels: Dict[str, NotificationChannel] = {}
        self._lock = RLock()
        logger.debug("AlertManager initialized")

    def register_rule(
        self,
        metric_name: str,
        threshold: Threshold,
        severity: AlertSeverity,
    ) -> None:
        """Register an alert rule for a metric."""
        with self._lock:
            if metric_name not in self._rules:
                self._rules[metric_name] = []
            self._rules[metric_name].append(
                {"threshold": threshold, "severity": severity}
            )
        logger.info(f"Alert rule registered for {metric_name}")

    def check_metric(self, metric_name: str, value: float) -> List[Alert]:
        """Check metric against registered rules."""
        triggered: List[Alert] = []
        with self._lock:
            if metric_name not in self._rules:
                return triggered
            for rule in self._rules[metric_name]:
                threshold: Threshold = rule["threshold"]
                severity: AlertSeverity = rule["severity"]
                if threshold.evaluate(value):
                    existing = next(
                        (
                            a
                            for a in self._active_alerts
                            if a.metric_name == metric_name and a.status == "active"
                        ),
                        None,
                    )
                    if not existing:
                        alert_id = f"alert_{metric_name}_{int(datetime.utcnow().timestamp() * 1000)}"
                        alert = Alert(
                            alert_id=alert_id,
                            metric_name=metric_name,
                            severity=severity,
                            threshold=threshold.value,
                            current_value=value,
                        )
                        self._active_alerts.append(alert)
                        self._alert_history.append(alert)
                        triggered.append(alert)
                        logger.warning(
                            f"Alert triggered for {metric_name}: {value} ({severity.value})"
                        )
        return triggered

    def add_channel(self, channel_name: str, channel: NotificationChannel) -> None:
        """Add a notification channel."""
        with self._lock:
            self._channels[channel_name] = channel
        logger.debug(f"Notification channel added: {channel_name}")

    def notify_all_channels(self) -> None:
        """Notify all channels of active alerts."""
        with self._lock:
            alerts = self._active_alerts.copy()
            channels = self._channels.copy()
        for channel_name, channel in channels.items():
            try:
                for alert in alerts:
                    if alert.status == "active":
                        channel.notify(alert)
            except Exception as e:
                logger.error(f"Error notifying channel {channel_name}: {e}")

    def get_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get registered alert rules."""
        with self._lock:
            return self._rules.copy()

    def get_channels(self) -> Dict[str, NotificationChannel]:
        """Get registered notification channels."""
        with self._lock:
            return self._channels.copy()

    def get_alert_history(self) -> List[Alert]:
        """Get alert history."""
        with self._lock:
            return self._alert_history.copy()
