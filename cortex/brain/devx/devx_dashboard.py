"""
ODX-002-02: DevX Dashboard

Development dashboard for orchestrator monitoring and feedback.
Provides real-time metrics and interactive development tools.

AC-ID: ODX-002-02
Phase: PHASE-18-ORCHESTRATOR-DEVX
TDD Status: GREEN phase

Features:
- Real-time metrics display
- Hot-reload status
- Scenario execution tracking
- Integration health monitoring
"""

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)


class DashboardSection(Enum):
    """Dashboard display sections."""
    OVERVIEW = "overview"
    HOT_RELOAD = "hot_reload"
    SCENARIOS = "scenarios"
    INTEGRATIONS = "integrations"
    METRICS = "metrics"
    LOGS = "logs"


@dataclass
class DashboardMetrics:
    """Metrics tracked by the dashboard.

    Attributes:
        reload_count: Number of hot reloads
        reload_success_rate: Success rate of reloads
        scenario_count: Total scenarios
        scenario_pass_rate: Scenario pass rate
        integration_count: Number of integration points
        integration_health: Integration health percentage
        last_update: When metrics were last updated
        custom_metrics: User-defined metrics
    """
    reload_count: int = 0
    reload_success_rate: float = 0.0
    scenario_count: int = 0
    scenario_pass_rate: float = 0.0
    integration_count: int = 0
    integration_health: float = 0.0
    last_update: datetime = field(default_factory=datetime.utcnow)
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "reload_count": self.reload_count,
            "reload_success_rate": self.reload_success_rate,
            "scenario_count": self.scenario_count,
            "scenario_pass_rate": self.scenario_pass_rate,
            "integration_count": self.integration_count,
            "integration_health": self.integration_health,
            "last_update": self.last_update.isoformat(),
            "custom_metrics": self.custom_metrics,
        }


@dataclass
class LogEntry:
    """A log entry for the dashboard.

    Attributes:
        timestamp: When log was created
        level: Log level (info, warning, error)
        source: Source component
        message: Log message
        details: Additional details
    """
    timestamp: datetime = field(default_factory=datetime.utcnow)
    level: str = "info"
    source: str = ""
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "source": self.source,
            "message": self.message,
            "details": self.details,
        }


class DevXDashboard:
    """Development dashboard for orchestrator feedback.

    Provides a unified view of:
    - Hot-reload status and history
    - Scenario execution results
    - Integration health
    - Real-time metrics

    Example:
        dashboard = DevXDashboard()

        # Connect to hot-reload
        hot_reload = HotReloadOrchestrator(...)
        dashboard.connect_hot_reload(hot_reload)

        # Connect scenario library
        library = ScenarioLibrary(...)
        dashboard.connect_scenario_library(library)

        # Get current metrics
        metrics = dashboard.get_metrics()

        # Render dashboard (for CLI display)
        print(dashboard.render())
    """

    def __init__(self, title: str = "CORTEX DevX Dashboard"):
        """Initialize dashboard.

        Args:
            title: Dashboard title
        """
        self.title = title

        # Connected components
        self._hot_reload = None
        self._scenario_library = None
        self._integration_validator = None

        # Metrics
        self._metrics = DashboardMetrics()

        # Logs
        self._logs: List[LogEntry] = []
        self._max_logs = 1000

        # Update callbacks
        self._update_callbacks: List[Callable[[DashboardMetrics], None]] = []

        # Auto-update
        self._auto_update = False
        self._update_thread: Optional[threading.Thread] = None
        self._update_interval = 1.0  # seconds

    def connect_hot_reload(self, hot_reload: Any) -> "DevXDashboard":
        """Connect to a HotReloadOrchestrator for monitoring.

        Args:
            hot_reload: HotReloadOrchestrator instance

        Returns:
            Self for method chaining
        """
        self._hot_reload = hot_reload

        # Register callbacks
        if hasattr(hot_reload, "on"):
            hot_reload.on("after_reload", self._on_reload)
            hot_reload.on("on_error", self._on_reload_error)

        self._log("info", "hot_reload", "Hot reload connected")
        return self

    def connect_scenario_library(self, library: Any) -> "DevXDashboard":
        """Connect to a ScenarioLibrary for monitoring.

        Args:
            library: ScenarioLibrary instance

        Returns:
            Self for method chaining
        """
        self._scenario_library = library

        # Register callbacks
        if hasattr(library, "on_after_run"):
            library.on_after_run(self._on_scenario_run)

        self._log("info", "scenario_library", "Scenario library connected")
        return self

    def connect_integration_validator(self, validator: Any) -> "DevXDashboard":
        """Connect to an IntegrationValidator for monitoring.

        Args:
            validator: IntegrationValidator instance

        Returns:
            Self for method chaining
        """
        self._integration_validator = validator
        self._log("info", "integration_validator", "Integration validator connected")
        return self

    def _on_reload(self, event: Any):
        """Handle reload event from hot-reload."""
        self._metrics.reload_count += 1

        if hasattr(event, "success") and event.success:
            # Update success rate
            total = self._metrics.reload_count
            successes = int(self._metrics.reload_success_rate * (total - 1) / 100) + 1
            self._metrics.reload_success_rate = (successes / total) * 100

            self._log(
                "info",
                "hot_reload",
                f"Reload successful: {getattr(event, 'orchestrator_name', 'unknown')}",
                {"reload_time_ms": getattr(event, "reload_time_ms", 0)},
            )

        self._update_metrics()

    def _on_reload_error(self, event: Any):
        """Handle reload error from hot-reload."""
        self._log(
            "error",
            "hot_reload",
            f"Reload failed: {getattr(event, 'error_message', 'unknown error')}",
        )
        self._update_metrics()

    def _on_scenario_run(self, scenario: Any, result: Any):
        """Handle scenario run completion."""
        status = getattr(result, "status", None)
        status_str = status.value if hasattr(status, "value") else str(status)

        self._log(
            "info" if status_str == "passed" else "warning",
            "scenarios",
            f"Scenario '{getattr(scenario, 'name', 'unknown')}': {status_str}",
            {"execution_time_ms": getattr(result, "execution_time_ms", 0)},
        )
        self._update_metrics()

    def _log(
        self,
        level: str,
        source: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Add a log entry.

        Args:
            level: Log level
            source: Source component
            message: Log message
            details: Additional details
        """
        entry = LogEntry(
            level=level,
            source=source,
            message=message,
            details=details or {},
        )

        self._logs.append(entry)

        # Trim if needed
        if len(self._logs) > self._max_logs:
            self._logs = self._logs[-self._max_logs:]

    def _update_metrics(self):
        """Update all metrics from connected components."""
        # Update from hot-reload
        if self._hot_reload:
            history = getattr(self._hot_reload, "get_reload_history", lambda: [])()
            if history:
                successes = sum(1 for e in history if getattr(e, "success", False))
                self._metrics.reload_count = len(history)
                self._metrics.reload_success_rate = (successes / len(history)) * 100 if history else 0

        # Update from scenario library
        if self._scenario_library:
            summary = getattr(self._scenario_library, "summary", lambda: {})()
            self._metrics.scenario_count = summary.get("total_scenarios", 0)
            self._metrics.scenario_pass_rate = summary.get("pass_rate", 0)

        # Update from integration validator
        if self._integration_validator:
            summary = getattr(self._integration_validator, "summary", lambda: {})()
            self._metrics.integration_count = summary.get("total_integration_points", 0)

            valid = summary.get("valid_validations", 0)
            total = summary.get("total_validations", 0)
            self._metrics.integration_health = (valid / total * 100) if total > 0 else 0

        self._metrics.last_update = datetime.utcnow()

        # Trigger callbacks
        for callback in self._update_callbacks:
            try:
                callback(self._metrics)
            except Exception:
                pass

    def _auto_update_loop(self):
        """Auto-update loop running in background."""
        while self._auto_update:
            self._update_metrics()
            time.sleep(self._update_interval)

    def start_auto_update(self, interval: float = 1.0) -> "DevXDashboard":
        """Start auto-updating metrics.

        Args:
            interval: Update interval in seconds

        Returns:
            Self for method chaining
        """
        self._update_interval = interval
        self._auto_update = True
        self._update_thread = threading.Thread(target=self._auto_update_loop, daemon=True)
        self._update_thread.start()
        return self

    def stop_auto_update(self) -> "DevXDashboard":
        """Stop auto-updating metrics.

        Returns:
            Self for method chaining
        """
        self._auto_update = False
        if self._update_thread:
            self._update_thread.join(timeout=2.0)
            self._update_thread = None
        return self

    def on_update(self, callback: Callable[[DashboardMetrics], None]) -> "DevXDashboard":
        """Register callback for metric updates.

        Args:
            callback: Function called with updated metrics

        Returns:
            Self for method chaining
        """
        self._update_callbacks.append(callback)
        return self

    def get_metrics(self) -> DashboardMetrics:
        """Get current metrics.

        Returns:
            Current DashboardMetrics
        """
        self._update_metrics()
        return self._metrics

    def get_logs(
        self,
        level: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100,
    ) -> List[LogEntry]:
        """Get log entries with optional filtering.

        Args:
            level: Filter by level
            source: Filter by source
            limit: Maximum entries to return

        Returns:
            List of LogEntries
        """
        logs = self._logs

        if level:
            logs = [l for l in logs if l.level == level]

        if source:
            logs = [l for l in logs if l.source == source]

        return logs[-limit:]

    def add_custom_metric(self, name: str, value: Any) -> "DevXDashboard":
        """Add a custom metric.

        Args:
            name: Metric name
            value: Metric value

        Returns:
            Self for method chaining
        """
        self._metrics.custom_metrics[name] = value
        return self

    def render(
        self,
        sections: Optional[List[DashboardSection]] = None,
        width: int = 80,
    ) -> str:
        """Render dashboard to text for CLI display.

        Args:
            sections: Sections to render (default: all)
            width: Display width

        Returns:
            Rendered dashboard string
        """
        if sections is None:
            sections = list(DashboardSection)

        self._update_metrics()
        lines = []

        # Title
        lines.append("=" * width)
        lines.append(self.title.center(width))
        lines.append(f"Last Update: {self._metrics.last_update.strftime('%Y-%m-%d %H:%M:%S')}".center(width))
        lines.append("=" * width)
        lines.append("")

        # Sections
        if DashboardSection.OVERVIEW in sections:
            lines.extend(self._render_overview(width))

        if DashboardSection.HOT_RELOAD in sections:
            lines.extend(self._render_hot_reload(width))

        if DashboardSection.SCENARIOS in sections:
            lines.extend(self._render_scenarios(width))

        if DashboardSection.INTEGRATIONS in sections:
            lines.extend(self._render_integrations(width))

        if DashboardSection.METRICS in sections:
            lines.extend(self._render_metrics(width))

        if DashboardSection.LOGS in sections:
            lines.extend(self._render_logs(width))

        return "\n".join(lines)

    def _render_overview(self, width: int) -> List[str]:
        """Render overview section."""
        lines = [
            "📊 OVERVIEW",
            "-" * width,
        ]

        # Status indicators
        hr_status = "🟢 Active" if self._hot_reload and getattr(self._hot_reload, "is_running", False) else "⚪ Inactive"
        sl_status = f"📝 {self._metrics.scenario_count} scenarios" if self._scenario_library else "⚪ Not connected"
        iv_status = f"🔗 {self._metrics.integration_count} points" if self._integration_validator else "⚪ Not connected"

        lines.append(f"  Hot Reload:    {hr_status}")
        lines.append(f"  Scenarios:     {sl_status}")
        lines.append(f"  Integrations:  {iv_status}")
        lines.append("")

        return lines

    def _render_hot_reload(self, width: int) -> List[str]:
        """Render hot reload section."""
        lines = [
            "🔄 HOT RELOAD",
            "-" * width,
        ]

        lines.append(f"  Total Reloads:  {self._metrics.reload_count}")
        lines.append(f"  Success Rate:   {self._metrics.reload_success_rate:.1f}%")

        # Recent reloads
        if self._hot_reload:
            history = getattr(self._hot_reload, "get_reload_history", lambda: [])()[-5:]
            if history:
                lines.append("  Recent:")
                for event in reversed(history):
                    status = "✅" if getattr(event, "success", False) else "❌"
                    name = getattr(event, "orchestrator_name", "unknown")
                    time_ms = getattr(event, "reload_time_ms", 0)
                    lines.append(f"    {status} {name} ({time_ms:.0f}ms)")

        lines.append("")
        return lines

    def _render_scenarios(self, width: int) -> List[str]:
        """Render scenarios section."""
        lines = [
            "🧪 SCENARIOS",
            "-" * width,
        ]

        lines.append(f"  Total:      {self._metrics.scenario_count}")
        lines.append(f"  Pass Rate:  {self._metrics.scenario_pass_rate:.1f}%")

        # By category
        if self._scenario_library:
            summary = getattr(self._scenario_library, "summary", lambda: {})()
            by_cat = summary.get("by_category", {})
            if by_cat:
                lines.append("  By Category:")
                for cat, count in by_cat.items():
                    lines.append(f"    {cat}: {count}")

        lines.append("")
        return lines

    def _render_integrations(self, width: int) -> List[str]:
        """Render integrations section."""
        lines = [
            "🔗 INTEGRATIONS",
            "-" * width,
        ]

        lines.append(f"  Total Points:  {self._metrics.integration_count}")
        lines.append(f"  Health:        {self._metrics.integration_health:.1f}%")

        # Issues
        if self._integration_validator:
            summary = getattr(self._integration_validator, "summary", lambda: {})()
            issues = summary.get("issues_by_severity", {})
            if issues:
                lines.append("  Issues:")
                for sev, count in issues.items():
                    icon = {"critical": "🔴", "error": "🟠", "warning": "🟡", "info": "🔵"}.get(sev, "⚪")
                    lines.append(f"    {icon} {sev}: {count}")

        lines.append("")
        return lines

    def _render_metrics(self, width: int) -> List[str]:
        """Render custom metrics section."""
        lines = [
            "📈 CUSTOM METRICS",
            "-" * width,
        ]

        if self._metrics.custom_metrics:
            for name, value in self._metrics.custom_metrics.items():
                lines.append(f"  {name}: {value}")
        else:
            lines.append("  No custom metrics defined")

        lines.append("")
        return lines

    def _render_logs(self, width: int) -> List[str]:
        """Render logs section."""
        lines = [
            "📋 RECENT LOGS",
            "-" * width,
        ]

        recent_logs = self._logs[-10:]
        if recent_logs:
            for log in reversed(recent_logs):
                icon = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}.get(log.level, "•")
                time_str = log.timestamp.strftime("%H:%M:%S")
                lines.append(f"  {icon} [{time_str}] {log.source}: {log.message}")
        else:
            lines.append("  No logs")

        lines.append("")
        return lines

    def to_dict(self) -> Dict[str, Any]:
        """Export dashboard state to dictionary.

        Returns:
            Dashboard state dictionary
        """
        return {
            "title": self.title,
            "metrics": self._metrics.to_dict(),
            "logs": [l.to_dict() for l in self._logs[-100:]],
            "connections": {
                "hot_reload": self._hot_reload is not None,
                "scenario_library": self._scenario_library is not None,
                "integration_validator": self._integration_validator is not None,
            },
        }
