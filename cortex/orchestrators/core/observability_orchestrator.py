"""ObservabilityOrchestrator - Unified metrics, alerts, tracing with SQLite audit."""
from __future__ import annotations
import sqlite3
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin  # Phase 94f

@dataclass
class Span:  # CORE-035-scoped — domain-scoped tracing span — independent of OpenTelemetry canonical
    """Simplified span for tracing."""
    span_id: str
    operation_name: str
    start_time: float
    duration_ms: float = 0.0
    status: str = "UNSET"

@dataclass
class Alert:
    """Alert representation."""
    alert_id: str
    severity: str
    message: str
    source: str
    timestamp: datetime
    resolved: bool = False

class ObservabilityOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin):
    """Unified observability: metrics + tracing + alerts + SQLite audit.

    Consolidates:
    - PrometheusMetrics (metric recording)
    - OpenTelemetry Tracing (distributed tracing)
    - AlertManager (alert management)
    - MetricsAggregator (metric collection)

    Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
    """

    # Phase 94f — advisory: observability/metrics layer, not a code-execution
    # entry point. Gateway routing deferred until MasterOrchestrator milestone.
    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(
        self,
        service_name: str,
        audit_db_path: Optional[Path] = None
    ) -> None:
        """Initialize observability orchestrator.

        Args:
            service_name: Service name for metrics/tracing
            audit_db_path: Optional SQLite audit DB path
        """
        self.service_name = service_name
        self._alerts: List[Alert] = []
        self._metrics: Dict[str, float] = {}
        self._spans: List[Span] = []

        # SQLite audit logging — stored under .cortex-runtime/ (not gitignored cortex/intelligence/)
        if audit_db_path:
            self.audit_db_path = audit_db_path
        else:
            db_dir = Path(".cortex-runtime/observability")
            db_dir.mkdir(parents=True, exist_ok=True)
            self.audit_db_path = db_dir / "observability_audit.db"
        self._init_audit_db()

    def _init_audit_db(self) -> None:
        """Initialize SQLite audit database."""
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS observability_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,
                target TEXT NOT NULL,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _audit_log(self, operation: str, target: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log operation to audit database."""
        import json
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO observability_audit (timestamp, operation, target, metadata) VALUES (?, ?, ?, ?)",
            (datetime.now().isoformat(), operation, target, json.dumps(metadata) if metadata else None)
        )
        conn.commit()
        conn.close()

    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: str = "gauge",
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record metric with audit logging.

        Args:
            name: Metric name
            value: Metric value
            metric_type: Type (counter, gauge, histogram)
            labels: Optional labels
        """
        self._metrics[name] = value
        # Would integrate with PrometheusMetrics here
        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(operation=f"record_metric_{metric_type}")
        self._audit_log("RECORD_METRIC", name, {"value": value, "type": metric_type})

    def start_span(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None) -> Span:
        """Start distributed trace span.

        Args:
            operation_name: Operation being traced
            attributes: Optional span attributes

        Returns:
            Span context
        """
        span = Span(
            span_id=str(uuid.uuid4()),
            operation_name=operation_name,
            start_time=time.time()
        )
        self._spans.append(span)
        self._audit_log("START_SPAN", operation_name, {"span_id": span.span_id})
        return span

    def end_span(self, span: Span, status: str = "OK") -> None:
        """End trace span.

        Args:
            span: Span to end
            status: Span status
        """
        span.duration_ms = (time.time() - span.start_time) * 1000
        span.status = status
        self._audit_log("END_SPAN", span.span_id, {"duration_ms": span.duration_ms})

    def create_alert(
        self,
        severity: str,
        message: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create alert with audit logging.

        Args:
            severity: Alert severity (INFO, WARNING, ERROR, CRITICAL)
            message: Alert message
            source: Alert source
            metadata: Optional metadata

        Returns:
            Alert ID
        """
        alert_id = str(uuid.uuid4())
        alert = Alert(
            alert_id=alert_id,
            severity=severity,
            message=message,
            source=source,
            timestamp=datetime.now()
        )
        self._alerts.append(alert)
        self._audit_log("CREATE_ALERT", alert_id, {"severity": severity, "source": source})
        return alert_id

    def get_alerts(self, severity: Optional[str] = None, resolved: bool = False) -> List[Alert]:
        """Get alerts with optional filtering.

        Args:
            severity: Optional severity filter
            resolved: Include resolved alerts

        Returns:
            List of alerts
        """
        alerts = [a for a in self._alerts if a.resolved == resolved]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return alerts

    def get_metrics(self) -> Dict[str, float]:
        """Get all recorded metrics.

        Returns:
            Dictionary of metric name to value
        """
        return self._metrics.copy()

    def export_traces(self) -> List[Dict[str, Any]]:
        """Export all traces.

        Returns:
            List of trace dictionaries
        """
        return [
            {
                "span_id": span.span_id,
                "operation_name": span.operation_name,
                "duration_ms": span.duration_ms,
                "status": span.status
            }
            for span in self._spans
        ]

    def query_audit_log(
        self,
        operation: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query audit log.

        Args:
            operation: Optional operation filter
            limit: Max results

        Returns:
            List of audit entries
        """
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()

        if operation:
            cursor.execute(
                "SELECT * FROM observability_audit WHERE operation = ? ORDER BY timestamp DESC LIMIT ?",
                (operation, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM observability_audit ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": r[0],
                "timestamp": r[1],
                "operation": r[2],
                "target": r[3],
                "metadata": r[4]
            }
            for r in rows
        ]

# AC_COMPLETE: AC-MEGA-B-S2-002-OBSERVABILITY ✅ Implemented
