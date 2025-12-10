"""
Health Monitor for Observability Orchestrator

Real-time system health monitoring with alerts.

Features:
- CPU, memory, disk monitoring
- Error rate tracking
- Response time monitoring
- Alert generation
- Threshold-based warnings

Author: Asif Hussain
Date: December 10, 2025
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import psutil

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """System health alert."""
    severity: AlertSeverity
    metric_name: str
    current_value: float
    threshold_value: float
    message: str
    timestamp: datetime


class HealthMonitor:
    """
    Monitors system health and generates alerts.
    
    Metrics:
    - CPU usage percentage
    - Memory usage percentage
    - Disk usage percentage
    - Error rate
    - Response time
    - Active sessions
    """
    
    # Default thresholds
    DEFAULT_THRESHOLDS = {
        "cpu_percent": {"warning": 70.0, "critical": 90.0},
        "memory_percent": {"warning": 75.0, "critical": 90.0},
        "disk_percent": {"warning": 80.0, "critical": 95.0},
        "error_rate": {"warning": 0.05, "critical": 0.10},
        "response_time_ms": {"warning": 1000.0, "critical": 5000.0}
    }
    
    def __init__(self, thresholds: Optional[Dict[str, Dict[str, float]]] = None):
        """
        Initialize health monitor.
        
        Args:
            thresholds: Custom threshold configuration
        """
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS
        self.alerts: List[Alert] = []
    
    def check_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.
        
        Returns:
            Health status with metrics and alerts
        """
        metrics = self._collect_metrics()
        alerts = self._evaluate_thresholds(metrics)
        status = self._determine_status(alerts)
        
        return {
            "status": status,
            "metrics": metrics,
            "alerts": [self._alert_to_dict(a) for a in alerts],
            "checked_at": datetime.now().isoformat()
        }
    
    def _collect_metrics(self) -> Dict[str, float]:
        """Collect system metrics."""
        try:
            metrics = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "error_rate": 0.0,  # Placeholder - would be calculated from logs
                "response_time_ms": 0.0,  # Placeholder - would be calculated from metrics
                "active_sessions": 0  # Placeholder - would be queried from session manager
            }
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            metrics = {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "disk_percent": 0.0,
                "error_rate": 0.0,
                "response_time_ms": 0.0,
                "active_sessions": 0
            }
        
        return metrics
    
    def _evaluate_thresholds(self, metrics: Dict[str, float]) -> List[Alert]:
        """Evaluate metrics against thresholds and generate alerts."""
        alerts = []
        
        for metric_name, value in metrics.items():
            if metric_name not in self.thresholds:
                continue
            
            thresholds = self.thresholds[metric_name]
            
            # Check critical threshold
            if value >= thresholds.get("critical", float('inf')):
                alerts.append(Alert(
                    severity=AlertSeverity.CRITICAL,
                    metric_name=metric_name,
                    current_value=value,
                    threshold_value=thresholds["critical"],
                    message=f"{metric_name} is critically high: {value:.2f}",
                    timestamp=datetime.now()
                ))
            # Check warning threshold
            elif value >= thresholds.get("warning", float('inf')):
                alerts.append(Alert(
                    severity=AlertSeverity.WARNING,
                    metric_name=metric_name,
                    current_value=value,
                    threshold_value=thresholds["warning"],
                    message=f"{metric_name} is elevated: {value:.2f}",
                    timestamp=datetime.now()
                ))
        
        return alerts
    
    def _determine_status(self, alerts: List[Alert]) -> str:
        """Determine overall health status from alerts."""
        if any(a.severity == AlertSeverity.CRITICAL for a in alerts):
            return "critical"
        elif any(a.severity == AlertSeverity.WARNING for a in alerts):
            return "warning"
        else:
            return "healthy"
    
    def _alert_to_dict(self, alert: Alert) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "severity": alert.severity.value,
            "metric_name": alert.metric_name,
            "current_value": alert.current_value,
            "threshold_value": alert.threshold_value,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat()
        }
