"""
Canonical ValidationResult — cortex.models.validation_result (GAP-80-04).

Single authoritative definition of ValidationResult used across CORTEX.
Consolidates 22 separate ValidationResult class definitions scattered
across cortex/tools/, cortex/core/, cortex/governance/, cortex/orchestrators/,
cortex/infrastructure/, and cortex/templates/.

CORE-011: type hints  CORE-012: docstrings  CORE-035: single canonical definition
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ValidationResult:
    """Canonical validation result for CORTEX governance and compliance checks.

    Single source-of-truth ValidationResult. Fields are a superset of all
    former ValidationResult definitions so existing callers can migrate
    without losing data.

    Attributes:
        passed: True if validation passed, False if any violations were found.
        violations: List of violation strings (CORE rule IDs, error messages, etc.).
        warnings: Non-blocking warnings raised during validation.
        score: Optional numeric validation score (0.0–1.0).
        metadata: Arbitrary metadata for extra validation context.
        details: Detailed validation report dict.
    """

    passed: bool
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Alias for ``passed`` — convenience property for callers using is_valid."""
        return self.passed

    @property
    def valid(self) -> bool:
        """Alias for ``passed`` — convenience property for callers using valid."""
        return self.passed

    @classmethod
    def ok(cls, warnings: Optional[List[str]] = None, **kwargs: Any) -> "ValidationResult":
        """Create a passing ValidationResult.

        Args:
            warnings: Optional list of non-blocking warnings.
            **kwargs: Additional fields to set on the result.

        Returns:
            ValidationResult with passed=True.
        """
        return cls(passed=True, warnings=warnings or [], **kwargs)

    @classmethod
    def fail(cls, violations: List[str], **kwargs: Any) -> "ValidationResult":
        """Create a failing ValidationResult.

        Args:
            violations: List of violation descriptions.
            **kwargs: Additional fields to set on the result.

        Returns:
            ValidationResult with passed=False.
        """
        return cls(passed=False, violations=violations, **kwargs)
