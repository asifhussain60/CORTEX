"""
Metrics dashboard for CORTEX observability.

Provides HTTP-based metrics dashboard for real-time visualization of CORTEX
runtime metrics, including span latencies, error rates, and historical trends.

Attributes:
    DEFAULT_HOST: Default host for dashboard server (127.0.0.1)
    DEFAULT_PORT: Default port for dashboard server (8080)
    DEFAULT_REFRESH_INTERVAL: Default refresh interval in seconds (5)
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.brain.core.observability.metrics_aggregator import (
    MetricPoint,
    MetricsAggregator,
)

# Import audit logger if available
try:
    from cortex.brain.core.governance.audit_logger import get_audit_logger
    _audit_logger = get_audit_logger()
except (ImportError, Exception):
    _audit_logger = None


@dataclass
class DashboardConfig:
    """Configuration for metrics dashboard.

    Attributes:
        host: Hostname or IP for dashboard server
        port: Port number for dashboard server
        enabled: Whether dashboard is enabled
        title: Dashboard title
        refresh_interval_seconds: WebSocket update interval in seconds
    """
    host: str = "127.0.0.1"
    port: int = 8080
    enabled: bool = True
    title: str = "CORTEX Metrics Dashboard"
    refresh_interval_seconds: int = 5

    def __post_init__(self) -> None:
        """Validate configuration after initialization.

        Raises:
            ValueError: If port is invalid
        """
        if not (1 <= self.port <= 65535):
            raise ValueError("port must be between 1 and 65535")


class MetricsDashboard:
    """Metrics dashboard for CORTEX runtime visualization.

    Provides HTTP API and WebSocket streaming for real-time metrics display,
    historical data queries, and metrics analysis.

    Attributes:
        host: Hostname for dashboard server
        port: Port for dashboard server
        enabled: Whether dashboard is enabled
        title: Dashboard title
        metrics_aggregator: MetricsAggregator instance
    """

    def __init__(self, config: DashboardConfig) -> None:
        """Initialize metrics dashboard.

        Args:
            config: DashboardConfig instance

        Raises:
            TypeError: If config is not DashboardConfig
        """
        if not isinstance(config, DashboardConfig):
            raise TypeError("config must be DashboardConfig instance")

        self.host: str = config.host
        self.port: int = config.port
        self.enabled: bool = config.enabled
        self.title: str = config.title
        self.refresh_interval_seconds: int = config.refresh_interval_seconds

        self.metrics_aggregator: MetricsAggregator = MetricsAggregator()
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._connected_clients: List[Any] = []

    def get_metrics_data(self) -> Dict[str, Any]:
        """Get current metrics data for dashboard display.

        Returns:
            Dictionary with timestamp and current metrics
        """
        summary = self.metrics_aggregator.get_summary()

        # Aggregate all operations' latency stats
        all_latencies = []
        for latencies in self.metrics_aggregator.span_latencies.values():
            all_latencies.extend(latencies)

        latency_stats = {}
        if all_latencies:
            latency_stats = {
                "min": min(all_latencies),
                "max": max(all_latencies),
                "avg": sum(all_latencies) / len(all_latencies),
                "p95": self.metrics_aggregator._percentile(sorted(all_latencies), 95),
                "p99": self.metrics_aggregator._percentile(sorted(all_latencies), 99),
            }

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "span_count": self.metrics_aggregator.total_spans,
                "error_count": self.metrics_aggregator.total_errors,
                "error_rate": self.metrics_aggregator.get_error_rate(),
                "operation_count": len(self.metrics_aggregator.span_counts),
                "latency_stats": latency_stats,
            },
        }

    def query_metrics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        operation_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Query historical metrics data.

        Args:
            start_time: Start of time range (omit for all time)
            end_time: End of time range (omit for now)
            operation_name: Filter by operation name (omit for all)

        Returns:
            List of metric datapoints
        """
        results = self.metrics_aggregator.datapoints

        # Filter by time range
        if start_time and end_time:
            results = self.metrics_aggregator.get_datapoints_by_time_range(
                start_time, end_time
            )

        # Filter by operation
        if operation_name:
            results = [p for p in results if p.operation == operation_name]

        return [p.to_dict() for p in results]

    def query_metrics_aggregated(
        self,
        bucket_size_seconds: int = 3600,
        operation_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Query aggregated metrics by time bucket.

        Args:
            bucket_size_seconds: Size of time bucket (default: 1 hour)
            operation_name: Filter by operation (omit for all)

        Returns:
            List of aggregated metric buckets
        """
        from datetime import datetime

        if not self.metrics_aggregator.datapoints:
            return []

        # Find time range
        min_ts = min(p.timestamp for p in self.metrics_aggregator.datapoints)
        max_ts = max(p.timestamp for p in self.metrics_aggregator.datapoints)

        results = []
        current_ts = min_ts

        while current_ts < max_ts:
            bucket_end = current_ts + bucket_size_seconds

            # Get datapoints in this bucket
            bucket_points = [
                p for p in self.metrics_aggregator.datapoints
                if current_ts <= p.timestamp < bucket_end
            ]

            if operation_name:
                bucket_points = [p for p in bucket_points if p.operation == operation_name]

            if bucket_points:
                # Compute aggregates
                values = [p.value for p in bucket_points if p.metric_type == "latency"]

                bucket_data = {
                    "start_time": datetime.fromtimestamp(current_ts).isoformat(),
                    "end_time": datetime.fromtimestamp(bucket_end).isoformat(),
                    "count": len(bucket_points),
                }

                if values:
                    bucket_data.update({
                        "min": min(values),
                        "max": max(values),
                        "avg": sum(values) / len(values),
                    })

                results.append(bucket_data)

            current_ts = bucket_end

        return results

    def get_dashboard_html(self) -> str:
        """Get dashboard HTML for web browser.

        Returns:
            HTML string for dashboard UI
        """
        metrics = self.get_metrics_data()

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{self.title}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; margin-bottom: 30px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #2563eb; margin: 10px 0; }}
        .metric-label {{ font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }}
        .latency-stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 10px; }}
        .stat-item {{ font-size: 12px; }}
        .stat-label {{ color: #999; }}
        .stat-value {{ font-weight: bold; color: #333; }}
        .auto-refresh {{ color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{self.title}</h1>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Spans</div>
                <div class="metric-value">{metrics['metrics']['span_count']}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Error Rate</div>
                <div class="metric-value">{metrics['metrics']['error_rate']:.1f}%</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Operations</div>
                <div class="metric-value">{metrics['metrics']['operation_count']}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Latency Stats (ms)</div>
                <div class="latency-stats">
                    <div class="stat-item">
                        <div class="stat-label">Min</div>
                        <div class="stat-value">{metrics['metrics']['latency_stats'].get('min', 0):.1f}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Avg</div>
                        <div class="stat-value">{metrics['metrics']['latency_stats'].get('avg', 0):.1f}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Max</div>
                        <div class="stat-value">{metrics['metrics']['latency_stats'].get('max', 0):.1f}</div>
                    </div>
                </div>
            </div>
        </div>

        <p class="auto-refresh">Last updated: {metrics['timestamp']} (auto-refresh every {self.refresh_interval_seconds}s)</p>
    </div>

    <script>
        // Auto-refresh metrics
        setInterval(() => {{
            location.reload();
        }}, {self.refresh_interval_seconds * 1000});
    </script>
</body>
</html>"""

        return html

    def get_metrics_json(self) -> str:
        """Get metrics as JSON string.

        Returns:
            JSON string with metrics data
        """
        metrics = self.get_metrics_data()
        return json.dumps(metrics, indent=2)

    def broadcast_metrics_update(self) -> None:
        """Broadcast metrics update to connected WebSocket clients.

        In production, this would send to all connected clients via WebSocket.
        """
        metrics = self.get_metrics_data()

        self._logger.debug(f"Broadcasting metrics: {metrics}")

    def add_connected_client(self, client: Any) -> None:
        """Register a connected WebSocket client.

        Args:
            client: WebSocket client connection
        """
        if client not in self._connected_clients:
            self._connected_clients.append(client)

    def remove_connected_client(self, client: Any) -> None:
        """Unregister a WebSocket client.

        Args:
            client: WebSocket client connection
        """
        if client in self._connected_clients:
            self._connected_clients.remove(client)

    def get_config_dict(self) -> Dict[str, Any]:
        """Get dashboard configuration as dictionary.

        Returns:
            Configuration dictionary
        """
        return {
            "host": self.host,
            "port": self.port,
            "enabled": self.enabled,
            "title": self.title,
            "refresh_interval_seconds": self.refresh_interval_seconds,
        }
