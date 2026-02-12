"""Dashboard API for system observability."""

import random
from datetime import datetime, timezone
from typing import Any, Dict, List

from cortex.models.dashboard_models import (
    ActivityLogEntry,
    DashboardConfig,
    MetricsData,
    SystemHealth,
)


class DashboardAPI:
    """API for dashboard operations and data retrieval."""

    def __init__(self) -> None:
        """Initialize Dashboard API."""
        self.config = DashboardConfig()
        self._activity_log: List[ActivityLogEntry] = self._generate_sample_log()

    def get_health_overview(self) -> SystemHealth:
        """Get system health overview.

        Returns:
            SystemHealth with current system status
        """
        # Simulate health status
        error_rate = random.uniform(0.0, 0.05)
        active_ops = random.randint(5, 50)

        # Determine health based on error rate
        if error_rate < 0.02:
            status = "healthy"
        elif error_rate < 0.05:
            status = "degraded"
        else:
            status = "unhealthy"

        return SystemHealth(
            status=status,
            error_rate=error_rate,
            active_operations=active_ops,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    def get_metrics(self) -> MetricsData:
        """Get performance metrics.

        Returns:
            MetricsData with latency percentiles and throughput
        """
        # Simulate realistic metrics
        p50 = random.uniform(10, 50)
        p95 = p50 + random.uniform(20, 100)
        p99 = p95 + random.uniform(50, 200)

        throughput = random.uniform(100, 1000)
        error_rate = random.uniform(0.0, 0.05)

        return MetricsData(
            p50_latency=p50,
            p95_latency=p95,
            p99_latency=p99,
            throughput=throughput,
            error_rate=error_rate,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    def get_activity_log(self) -> List[ActivityLogEntry]:
        """Get activity log entries.

        Returns:
            List of recent activity log entries (max 50)
        """
        return self._activity_log[-50:]

    def get_available_chart_types(self) -> List[str]:
        """Get available chart types.

        Returns:
            List of supported chart types
        """
        return ["line", "bar", "pie"]

    def get_config(self) -> DashboardConfig:
        """Get dashboard configuration.

        Returns:
            DashboardConfig with current settings
        """
        return self.config

    def get_config_for_viewport(self, viewport: str) -> DashboardConfig:
        """Get dashboard configuration for specific viewport.

        Args:
            viewport: Viewport type ("mobile", "tablet", "desktop")

        Returns:
            DashboardConfig optimized for viewport
        """
        config = DashboardConfig(
            refresh_interval_seconds=5,
            max_log_entries=50 if viewport == "mobile" else 50,
            viewport=viewport
        )
        return config

    def _generate_sample_log(self) -> List[ActivityLogEntry]:
        """Generate sample activity log.

        Returns:
            List of sample activity entries
        """
        log = []
        operation_types = ["api_call", "workflow", "database_query", "batch_process"]
        statuses = ["success", "failure", "in_progress"]

        for i in range(100):
            timestamp = datetime.now(timezone.utc).isoformat()
            entry = ActivityLogEntry(
                operation_type=random.choice(operation_types),
                status=random.choice(statuses),
                duration_ms=random.randint(10, 5000),
                timestamp=timestamp
            )
            log.append(entry)

        return log
