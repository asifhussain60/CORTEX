"""
cortex/models/shared/health.py — Canonical HealthCheckResult and HealthStatus.

Phase 114-a GAP-114-01: Single authoritative HealthCheckResult used across CORTEX.
Consolidates 9 separate HealthCheckResult class definitions.

All new code should import from here:
  from cortex.models.shared.health import HealthCheckResult, HealthStatus

Governance: CORE-035 (single canonical), CORE-011 (type hints), CORE-012 (docstrings)
Authority: phase-114-a, SWEEP-114-LAYERING-RESET
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

# Re-export canonical HealthStatus from canonical_enums (single source of truth — CORE-035)
from cortex.models.canonical_enums import HealthStatus


@dataclass
class HealthCheckResult:
    """Canonical result of a health check operation.

    Single source-of-truth HealthCheckResult. Fields are a superset of all
    former HealthCheckResult definitions so existing callers can migrate
    without losing data.

    Attributes:
        orchestrator_name: Name of the component being health-checked.
        status: HealthStatus enum value.
        message: Human-readable status message.
        timestamp: When the health check was performed.
        checks_performed: List of individual checks that were run.
        error: Error message if the check failed, None otherwise.
        recovery_suggestions: List of suggested remediation steps.
        metadata: Arbitrary extra metadata.
        duration_ms: Duration of the health check in milliseconds.
    """

    orchestrator_name: str
    status: HealthStatus
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    checks_performed: List[str] = field(default_factory=list)
    error: Optional[str] = None
    recovery_suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[int] = None

    @property
    def is_healthy(self) -> bool:
        """Return True if status is HEALTHY."""
        return self.status == HealthStatus.HEALTHY

    @property
    def is_degraded(self) -> bool:
        """Return True if status is DEGRADED."""
        return self.status == HealthStatus.DEGRADED

    @classmethod
    def healthy(
        cls,
        name: str,
        message: str = "All checks passed",
        checks: Optional[List[str]] = None,
    ) -> "HealthCheckResult":
        """Create a healthy HealthCheckResult."""
        return cls(
            orchestrator_name=name,
            status=HealthStatus.HEALTHY,
            message=message,
            checks_performed=checks or [],
        )

    @classmethod
    def unhealthy(
        cls,
        name: str,
        message: str,
        error: Optional[str] = None,
    ) -> "HealthCheckResult":
        """Create an unhealthy HealthCheckResult."""
        return cls(
            orchestrator_name=name,
            status=HealthStatus.UNHEALTHY,
            message=message,
            error=error,
        )

    @classmethod
    def degraded(
        cls,
        name: str,
        message: str,
        suggestions: Optional[List[str]] = None,
    ) -> "HealthCheckResult":
        """Create a degraded HealthCheckResult."""
        return cls(
            orchestrator_name=name,
            status=HealthStatus.DEGRADED,
            message=message,
            recovery_suggestions=suggestions or [],
        )


__all__ = ["HealthStatus", "HealthCheckResult"]
