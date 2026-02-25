"""health_monitor.py — Health Monitor stub."""
from __future__ import annotations
from typing import Any


class HealthMonitor:
    """Monitors orchestrator and service health."""

    def check(self, target: str) -> dict[str, Any]:
        """Check health of a target component.

        Args:
            target: Component name to check.

        Returns:
            Health status dictionary.
        """
        return {"target": target, "status": "healthy", "latency_ms": 0}
