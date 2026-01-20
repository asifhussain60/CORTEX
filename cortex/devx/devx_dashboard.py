"""DevX Dashboard

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class DashboardMetrics:
    """Dashboard metrics."""
    active_users: int = 0
    requests_per_minute: float = 0.0
    error_rate: float = 0.0

__all__ = ["DashboardMetrics"]
