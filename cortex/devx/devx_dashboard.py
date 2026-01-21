"""DevX Dashboard

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
import threading
import time


class DashboardSection(Enum):
    """Dashboard sections."""
    OVERVIEW = "overview"
    HOT_RELOAD = "hot_reload"
    SCENARIOS = "scenarios"
    INTEGRATIONS = "integrations"
    LOGS = "logs"


@dataclass
class DashboardMetrics:
    """Dashboard metrics."""
    reload_count: int = 0
    reload_success_rate: float = 0.0
    scenario_count: int = 0
    scenario_pass_rate: float = 0.0
    integration_count: int = 0
    integration_health: float = 0.0
    last_update: Optional[datetime] = None
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.last_update is None:
            self.last_update = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "reload_count": self.reload_count,
            "reload_success_rate": self.reload_success_rate,
            "scenario_count": self.scenario_count,
            "scenario_pass_rate": self.scenario_pass_rate,
            "integration_count": self.integration_count,
            "integration_health": self.integration_health,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "custom_metrics": self.custom_metrics,
        }


@dataclass
class LogEntry:
    """Dashboard log entry."""
    level: str
    source: str
    message: str
    timestamp: Optional[datetime] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "level": self.level,
            "source": self.source,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "details": self.details,
        }


class DevXDashboard:
    """Developer experience dashboard."""
    
    def __init__(self, title: str = "CORTEX DevX Dashboard"):
        """Initialize dashboard."""
        self.title = title
        self._hot_reload = None
        self._scenario_library = None
        self._integration_validator = None
        self._metrics = DashboardMetrics()
        self._logs: List[LogEntry] = []
        self._max_logs = 1000
        self._update_callbacks: List[Callable] = []
        self._auto_update = False
        self._update_thread = None
    
    def connect_hot_reload(self, hot_reload: Any) -> "DevXDashboard":
        """Connect hot-reload component."""
        self._hot_reload = hot_reload
        hot_reload.on("after_reload", self._on_reload)
        hot_reload.on("on_error", self._on_reload_error)
        return self
    
    def connect_scenario_library(self, library: Any) -> "DevXDashboard":
        """Connect scenario library."""
        self._scenario_library = library
        library.on_after_run(self._on_scenario_run)
        return self
    
    def connect_integration_validator(self, validator: Any) -> "DevXDashboard":
        """Connect integration validator."""
        self._integration_validator = validator
        return self
    
    def get_metrics(self) -> DashboardMetrics:
        """Get current metrics."""
        self._update_metrics()
        
        # Trigger callbacks
        for callback in self._update_callbacks:
            try:
                callback(self._metrics)
            except Exception:
                pass
        
        return self._metrics
    
    def add_custom_metric(self, key: str, value: Any) -> "DevXDashboard":
        """Add custom metric."""
        self._metrics.custom_metrics[key] = value
        return self
    
    def on_update(self, callback: Callable) -> "DevXDashboard":
        """Register update callback."""
        self._update_callbacks.append(callback)
        return self
    
    def get_logs(self, level: Optional[str] = None, source: Optional[str] = None, 
                 limit: Optional[int] = None) -> List[LogEntry]:
        """Get logs."""
        logs = self._logs
        
        if level:
            logs = [log for log in logs if log.level == level]
        
        if source:
            logs = [log for log in logs if log.source == source]
        
        if limit:
            logs = logs[-limit:]
        
        return logs
    
    def render(self, sections: Optional[List[DashboardSection]] = None) -> str:
        """Render dashboard to text."""
        if sections is None:
            sections = list(DashboardSection)
        
        lines = []
        lines.append("=" * 80)
        lines.append(self.title.center(80))
        lines.append("=" * 80)
        lines.append("")
        
        if DashboardSection.OVERVIEW in sections:
            lines.append("OVERVIEW")
            lines.append("-" * 40)
            metrics = self.get_metrics()
            lines.append(f"Last Update: {metrics.last_update}")
            lines.append(f"Reload Count: {metrics.reload_count} ({metrics.reload_success_rate:.1f}% success)")
            lines.append(f"Scenarios: {metrics.scenario_count} ({metrics.scenario_pass_rate:.1f}% pass rate)")
            lines.append(f"Integrations: {metrics.integration_count} ({metrics.integration_health:.1f}% healthy)")
            lines.append("")
        
        if DashboardSection.HOT_RELOAD in sections:
            lines.append("HOT RELOAD")
            lines.append("-" * 40)
            if self._hot_reload:
                status = "Active" if hasattr(self._hot_reload, 'is_running') and self._hot_reload.is_running else "Inactive"
                lines.append(f"Status: {status}")
                if hasattr(self._hot_reload, 'get_reload_history'):
                    history = self._hot_reload.get_reload_history()
                    lines.append(f"Recent reloads: {len(history)}")
            else:
                lines.append("Not connected")
            lines.append("")
        
        if DashboardSection.SCENARIOS in sections and self._scenario_library:
            lines.append("SCENARIOS")
            lines.append("-" * 40)
            if hasattr(self._scenario_library, 'summary'):
                summary = self._scenario_library.summary()
                lines.append(f"{summary.get('total_scenarios', 0)} scenarios")
                if "pass_rate" in summary:
                    lines.append(f"Pass rate: {summary['pass_rate']:.1f}%")
            lines.append("")
        
        if DashboardSection.INTEGRATIONS in sections and self._integration_validator:
            lines.append("INTEGRATIONS")
            lines.append("-" * 40)
            if hasattr(self._integration_validator, 'summary'):
                summary = self._integration_validator.summary()
                lines.append(f"Integration points: {summary.get('total_integration_points', 0)}")
                if "issues_by_severity" in summary and "warning" in summary["issues_by_severity"]:
                    lines.append(f"Warnings: {summary['issues_by_severity']['warning']}")
            lines.append("")
        
        if DashboardSection.LOGS in sections:
            lines.append("RECENT LOGS")
            lines.append("-" * 40)
            recent = self.get_logs(limit=5)
            for log in recent:
                lines.append(f"[{log.level.upper()}] {log.source}: {log.message}")
            lines.append("")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export dashboard state."""
        return {
            "title": self.title,
            "metrics": self._metrics.to_dict(),
            "logs": [log.to_dict() for log in self._logs],
            "connections": {
                "hot_reload": self._hot_reload is not None,
                "scenario_library": self._scenario_library is not None,
                "integration_validator": self._integration_validator is not None,
            },
        }
    
    def start_auto_update(self, interval: float = 1.0) -> None:
        """Start auto-update."""
        if self._auto_update:
            return
        
        self._auto_update = True
        
        def update_loop():
            while self._auto_update:
                self.get_metrics()
                time.sleep(interval)
        
        self._update_thread = threading.Thread(target=update_loop, daemon=True)
        self._update_thread.start()
    
    def stop_auto_update(self) -> None:
        """Stop auto-update."""
        self._auto_update = False
        if self._update_thread:
            self._update_thread.join(timeout=2.0)
    
    def _log(self, level: str, source: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Add log entry."""
        entry = LogEntry(
            level=level,
            source=source,
            message=message,
            details=details or {},
        )
        self._logs.append(entry)
        
        # Trim logs
        if len(self._logs) > self._max_logs:
            self._logs = self._logs[-self._max_logs:]
    
    def _update_metrics(self) -> None:
        """Update metrics from connected components."""
        # Update from hot-reload
        if self._hot_reload and hasattr(self._hot_reload, 'get_reload_history'):
            history = self._hot_reload.get_reload_history()
            self._metrics.reload_count = len(history)
            if history:
                successes = sum(1 for e in history if e.success)
                self._metrics.reload_success_rate = (successes / len(history)) * 100
        
        # Update from scenario library
        if self._scenario_library and hasattr(self._scenario_library, 'summary'):
            summary = self._scenario_library.summary()
            self._metrics.scenario_count = summary.get("total_scenarios", 0)
            self._metrics.scenario_pass_rate = summary.get("pass_rate", 0.0)
        
        # Update from integration validator
        if self._integration_validator and hasattr(self._integration_validator, 'summary'):
            summary = self._integration_validator.summary()
            self._metrics.integration_count = summary.get("total_integration_points", 0)
            if summary.get("total_validations", 0) > 0:
                valid = summary.get("valid_validations", summary.get("passed_validations", 0))
                self._metrics.integration_health = (valid / summary["total_validations"]) * 100
        
        self._metrics.last_update = datetime.now()
    
    def _on_reload(self, event: Any) -> None:
        """Handle reload event."""
        self._metrics.reload_count += 1
        self._log(
            "info",
            "hot_reload",
            f"Reloaded {event.orchestrator_name} in {event.reload_time_ms:.1f}ms",
        )
    
    def _on_reload_error(self, event: Any) -> None:
        """Handle reload error."""
        self._log(
            "error",
            "hot_reload",
            f"Reload error: {event.error_message}",
        )
    
    def _on_scenario_run(self, scenario: Any, result: Any) -> None:
        """Handle scenario run."""
        self._log(
            "info",
            "scenario_library",
            f"Scenario '{scenario.name}' {result.status.value} in {result.execution_time_ms:.1f}ms",
        )


__all__ = [
    "DashboardSection",
    "DashboardMetrics",
    "LogEntry",
    "DevXDashboard",
]
