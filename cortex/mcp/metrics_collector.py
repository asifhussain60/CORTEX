"""
CORTEX MCP Server Prometheus Metrics.

Provides Prometheus-compatible metrics for monitoring CORTEX:
- Request count and duration
- Orchestrator invocations
- Wiring system health
- Error rates

CORE-011: All functions have type hints.
CORE-012: All public APIs have Google-style docstrings.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class MetricsCollector:
    """
    Prometheus-compatible metrics collector for CORTEX.

    Tracks:
    - cortex_requests_total: Total requests processed
    - cortex_request_duration_seconds: Request duration histogram
    - cortex_orchestrator_invocations: Orchestrator call counts
    - cortex_wiring_health: Wiring system status
    - cortex_errors_total: Total errors
    """

    requests_total: int = 0
    errors_total: int = 0
    request_durations: Dict[str, list] = field(default_factory=lambda: defaultdict(list))
    orchestrator_invocations: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    wiring_version: str = "unknown"
    last_request_time: float = 0.0

    def record_request(self, method: str, duration_seconds: float, success: bool) -> None:
        """
        Record a request metric.

        Args:
            method: MCP method name.
            duration_seconds: Request duration in seconds.
            success: Whether request succeeded.
        """
        self.requests_total += 1
        if not success:
            self.errors_total += 1

        self.request_durations[method].append(duration_seconds)
        self.last_request_time = time.time()

        # Keep only last 100 durations per method to save memory
        if len(self.request_durations[method]) > 100:
            self.request_durations[method] = self.request_durations[method][-100:]

    def record_orchestrator_invocation(self, orchestrator_name: str) -> None:
        """
        Record orchestrator invocation.

        Args:
            orchestrator_name: Name of invoked orchestrator.
        """
        self.orchestrator_invocations[orchestrator_name] += 1

    def get_prometheus_metrics(self) -> str:
        """
        Get metrics in Prometheus text format.

        Returns:
            Metrics string in Prometheus format.
        """
        metrics = []

        # Header
        metrics.append("# HELP cortex_requests_total Total requests processed by CORTEX MCP Server")
        metrics.append("# TYPE cortex_requests_total counter")
        metrics.append(f"cortex_requests_total {self.requests_total}")

        metrics.append("")
        metrics.append("# HELP cortex_errors_total Total errors in CORTEX MCP Server")
        metrics.append("# TYPE cortex_errors_total counter")
        metrics.append(f"cortex_errors_total {self.errors_total}")

        metrics.append("")
        metrics.append("# HELP cortex_request_duration_seconds Request duration in seconds")
        metrics.append("# TYPE cortex_request_duration_seconds summary")

        # Calculate request duration stats
        for method, durations in self.request_durations.items():
            if durations:
                avg_duration = sum(durations) / len(durations)
                max_duration = max(durations)
                min_duration = min(durations)

                metrics.append(f'cortex_request_duration_seconds{{method="{method}",quantile="0.5"}} {sorted(durations)[len(durations)//2]}')
                metrics.append(f'cortex_request_duration_seconds{{method="{method}",quantile="0.95"}} {sorted(durations)[int(len(durations)*0.95)]}')
                metrics.append(f'cortex_request_duration_seconds{{method="{method}",quantile="0.99"}} {sorted(durations)[int(len(durations)*0.99)]}')
                metrics.append(f'cortex_request_duration_seconds_sum{{method="{method}"}} {sum(durations)}')
                metrics.append(f'cortex_request_duration_seconds_count{{method="{method}"}} {len(durations)}')

        metrics.append("")
        metrics.append("# HELP cortex_orchestrator_invocations Total orchestrator invocations")
        metrics.append("# TYPE cortex_orchestrator_invocations counter")
        for orchestrator, count in self.orchestrator_invocations.items():
            metrics.append(f'cortex_orchestrator_invocations{{orchestrator="{orchestrator}"}} {count}')

        metrics.append("")
        metrics.append("# HELP cortex_wiring_health Wiring system health (1=healthy, 0=unhealthy)")
        metrics.append("# TYPE cortex_wiring_health gauge")
        metrics.append('cortex_wiring_health{version="unknown"} 1')

        return "\n".join(metrics) + "\n"


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """
    Get or create global metrics collector instance.

    Returns:
        Global MetricsCollector instance.
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
