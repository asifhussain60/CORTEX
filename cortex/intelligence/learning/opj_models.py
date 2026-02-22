"""
OPJModels — shared dataclasses for the Operational Pattern Journal.

AC-ID: AC-OPJ-PHASE52-MODELS
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings), CORE-028 (snake_case)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class OPJOutcome(Enum):
    """Outcome of an orchestrator operation recorded in the OPJ."""

    SUCCESS = "success"
    FAILURE = "failure"


class OPJValidationError(ValueError):
    """Raised when an OPJEntry field fails validation."""


@dataclass
class OPJEntry:
    """
    A single Operational Pattern Journal entry.

    Required for both success and failure outcomes:
        entry_id, orchestrator, operation, outcome, confidence, timestamp

    Success-specific (optional):
        resolution, context, pattern_reuse_count

    Failure-specific (optional):
        error, attempted_fix, root_cause, avoid_in_future
    """

    entry_id: str
    orchestrator: str
    operation: str
    outcome: OPJOutcome
    confidence: float

    # Success fields
    resolution: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    pattern_reuse_count: int = 0

    # Failure fields
    error: Optional[str] = None
    attempted_fix: Optional[str] = None
    root_cause: Optional[str] = None
    avoid_in_future: Optional[str] = None

    # Auto-set
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    _ENTRY_ID_RE = re.compile(r"^OPJ-[A-Z0-9_]+-\d{14}$")

    def __post_init__(self) -> None:
        """Validate entry_id format and confidence range."""
        if not self._ENTRY_ID_RE.match(self.entry_id):
            raise OPJValidationError(
                f"entry_id '{self.entry_id}' must match OPJ-{{ORCHESTRATOR}}-{{TIMESTAMP}}. "
                "Example: OPJ-MYORCH-20260222120000"
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise OPJValidationError(
                f"confidence must be between 0.0 and 1.0, got {self.confidence}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serialise entry to a plain dict (YAML-safe)."""
        return {
            "entry_id": self.entry_id,
            "orchestrator": self.orchestrator,
            "operation": self.operation,
            "outcome": self.outcome.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "resolution": self.resolution,
            "context": self.context,
            "pattern_reuse_count": self.pattern_reuse_count,
            "error": self.error,
            "attempted_fix": self.attempted_fix,
            "root_cause": self.root_cause,
            "avoid_in_future": self.avoid_in_future,
        }
