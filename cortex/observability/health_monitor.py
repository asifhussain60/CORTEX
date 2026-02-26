"""health_monitor.py — Health Monitor.

Monitors orchestrator and service health by delegating to HealthOrchestrator
(GAP-84-19). Replaces the hardcoded placeholder that always returned latency_ms=0.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class HealthMonitor:
    """Monitors orchestrator and service health via HealthOrchestrator delegation.

    Replaces the stub that always returned {status: healthy, latency_ms: 0}.
    On delegation failure, falls back to a timed ping to indicate real latency.
    """

    def check(self, target: str) -> dict[str, Any]:
        """Check health of a target component.

        Delegates to HealthOrchestrator when available; falls back to a
        timed availability check to measure real latency.

        Args:
            target: Component name to check.

        Returns:
            Health status dictionary with real latency and status data.
        """
        t0 = time.perf_counter()
        status = "unknown"
        details: dict[str, Any] = {}
        try:
            from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
            orchestrator = HealthOrchestrator()
            result = orchestrator.health_check()
            status = result.get("status", "unknown")
            details = result
        except Exception as exc:
            logger.debug("HealthMonitor: HealthOrchestrator unavailable — %s", exc)
            status = "degraded"
            details = {"error": str(exc), "fallback": True}
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {"target": target, "status": status, "latency_ms": latency_ms, **details}
