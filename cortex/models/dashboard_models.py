"""Dashboard data models."""

from typing import Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class SystemHealth:
    """System health overview."""

    status: str  # "healthy", "degraded", "unhealthy"
    error_rate: float  # 0.0-1.0
    active_operations: int
    timestamp: Optional[str] = None


@dataclass
class MetricsData:
    """Performance metrics data."""

    p50_latency: float  # milliseconds
    p95_latency: float  # milliseconds
    p99_latency: float  # milliseconds
    throughput: float  # operations per second
    error_rate: float  # 0.0-1.0
    timestamp: Optional[str] = None


@dataclass
class ActivityLogEntry:
    """Activity log entry."""

    operation_type: str
    status: str  # "success", "failure", "in_progress"
    duration_ms: int
    timestamp: str


@dataclass
class DashboardConfig:
    """Dashboard configuration."""

    refresh_interval_seconds: int = 5
    max_log_entries: int = 50
    enable_real_time: bool = False
    viewport: str = "desktop"
