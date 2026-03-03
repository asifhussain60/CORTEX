"""
Shared data models for the enforcement_orchestrator package.

Extracted from enforcement_orchestrator.py (Phase 103-e).
Contains EnforcementLevel, EnforcementResult — imported by all agent modules.

Author: Asif Hussain
AC-ID: AC-P103E-MODELS-001
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class EnforcementLevel(Enum):  # noqa: CORE-035-scoped — domain-specific enforcement level — local orchestrator values
    """Enforcement result severity levels."""
    PASS = "pass"
    WARNING = "warning"
    BLOCKED = "blocked"


@dataclass
class EnforcementResult:
    """
    Result of governance enforcement check.

    Attributes:
        level: Enforcement level (PASS, WARNING, BLOCKED)
        violations: List of Tier 0 violations (block execution)
        warnings: List of Tier 1 warnings (escalate but allow)
        metadata: Additional context (execution time, agent count, etc.)
    """
    level: EnforcementLevel
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_blocked(self) -> bool:
        """Check if execution should be blocked."""
        return self.level == EnforcementLevel.BLOCKED

    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0
