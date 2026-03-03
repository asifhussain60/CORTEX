"""
cortex/models/shared — Canonical shared models package.

Phase 114-a: GAP-114-01 — Shared Model Extraction.
Single canonical definitions for the top duplicate class names.

Import these instead of domain-specific copies:
  from cortex.models.shared.validation import ValidationResult
  from cortex.models.shared.health import HealthCheckResult
  from cortex.models.shared.cache import CacheEntry
  from cortex.models.shared.execution import ExecutionResult

Governance: CORE-035 (single canonical implementation)
Authority: phase-114-a, SWEEP-114-LAYERING-RESET
"""
from cortex.models.shared.validation import ValidationResult
from cortex.models.shared.health import HealthCheckResult, HealthStatus
from cortex.models.shared.cache import CacheEntry
from cortex.models.shared.execution import ExecutionResult

__all__ = [
    "ValidationResult",
    "HealthCheckResult",
    "HealthStatus",
    "CacheEntry",
    "ExecutionResult",
]
