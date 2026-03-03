"""
cortex/models/shared/execution.py — Canonical ExecutionResult.

Phase 114-a GAP-114-01: Single authoritative ExecutionResult used across CORTEX.
Consolidates 6 separate ExecutionResult class definitions.

All new code should import from here:
  from cortex.models.shared.execution import ExecutionResult

Governance: CORE-035 (single canonical), CORE-011 (type hints), CORE-012 (docstrings)
Authority: phase-114-a, SWEEP-114-LAYERING-RESET
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionResult:
    """Canonical result of an orchestrator execution.

    Single source-of-truth ExecutionResult. Fields are a superset of all
    former ExecutionResult definitions so existing callers can migrate
    without losing data.

    Attributes:
        success: True if execution completed without errors.
        stage: Lifecycle stage where the result was produced.
        duration_ms: Execution duration in milliseconds.
        output: Execution output payload.
        error: Error message if execution failed, None otherwise.
        metadata: Arbitrary extra metadata.
        violations: Governance violations detected during execution.
    """

    success: bool
    stage: str = "execute"
    duration_ms: int = 0
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    violations: List[str] = field(default_factory=list)

    @property
    def failed(self) -> bool:
        """Return True if execution failed."""
        return not self.success

    @property
    def has_violations(self) -> bool:
        """Return True if governance violations were detected."""
        return bool(self.violations)

    @classmethod
    def ok(
        cls,
        stage: str = "execute",
        output: Optional[Dict[str, Any]] = None,
        duration_ms: int = 0,
    ) -> "ExecutionResult":
        """Create a successful ExecutionResult."""
        return cls(success=True, stage=stage, output=output or {}, duration_ms=duration_ms)

    @classmethod
    def failure(
        cls,
        error: str,
        stage: str = "execute",
        violations: Optional[List[str]] = None,
    ) -> "ExecutionResult":
        """Create a failed ExecutionResult."""
        return cls(
            success=False,
            stage=stage,
            error=error,
            violations=violations or [],
        )


__all__ = ["ExecutionResult"]
