"""Autonomous Plan Executor - Continuation Detection.

Detects continuation patterns ("proceed", "continue", "yes", "approve")
and enables autonomous multi-phase execution without interruption.

Authority: Phase 35 R1 + cortex-architect.prompt.md lines 540-570
"""

import re
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class Phase(BaseModel):
    """Phase representation for continuation detection."""

    id: str
    name: str
    status: str
    priority: str
    execution_order: Optional[int] = None
    file: str


class AutonomousPlanExecutor:
    """Detects continuation patterns and loads next phase for autonomous execution.

    Usage:
        executor = AutonomousPlanExecutor()
        if executor.detect_continuation(user_input):
            next_phase = executor.load_next_phase()
            if next_phase and executor.should_skip_dor():
                # Skip DoR/Challenge, execute immediately
                ...
    """

    # Continuation patterns (case-insensitive)
    CONTINUATION_PATTERNS = [
        r"\b(continue|proceed|yes|approve)\b",
        r"\bphase[-\s]?\d+\b",  # "phase 3", "phase-3"
        r"\bautonomous(?:ly)?\b",
        r"\bbypass\s+challenge\b",
        r"\bskip\s+dor\b",
    ]

    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize executor with registry path.

        Args:
            registry_path: Path to _cortex-master/index.yaml
                          Defaults to cortex-registry/_cortex-master/index.yaml
        """
        if registry_path is None:
            # Default to cortex-registry/_cortex-master/index.yaml
            registry_path = (
                Path(__file__).parent.parent.parent.parent
                / "cortex-registry"
                / "_cortex-master"
                / "index.yaml"
            )
        self.registry_path = registry_path
        self._autonomous_mode = False
        self._last_input: Optional[str] = None

    def detect_continuation(self, user_input: str) -> bool:
        """Detect if user input indicates continuation intent.

        Args:
            user_input: Raw user input string

        Returns:
            True if continuation detected, False otherwise

        Examples:
            >>> executor = AutonomousPlanExecutor()
            >>> executor.detect_continuation("proceed")
            True
            >>> executor.detect_continuation("continue with phase 3")
            True
            >>> executor.detect_continuation("what is the next step?")
            False
        """
        self._last_input = user_input
        normalized = user_input.lower().strip()

        # Check each pattern
        for pattern in self.CONTINUATION_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                self._autonomous_mode = True
                return True

        return False

    def load_next_phase(self) -> Optional[Phase]:
        """Load next phase from registry (in-progress or planned).

        Returns:
            Next Phase to execute, or None if no phases available

        Priority:
            1. IN_PROGRESS phases (resume)
            2. PLANNED phases (by execution_order, then priority)
        """
        if not self.registry_path.exists():
            return None

        try:
            with open(self.registry_path, "r") as f:
                registry = yaml.safe_load(f)
        except Exception:
            return None

        active_phases = registry.get("active_phases", [])
        if not active_phases:
            return None

        # Priority 1: Find in-progress phases
        in_progress = [
            p for p in active_phases if p.get("status") in ["in-progress", "active"]
        ]
        if in_progress:
            # Sort by execution_order (nulls last), then by priority
            in_progress.sort(
                key=lambda p: (
                    p.get("execution_order") is None,
                    p.get("execution_order", 999),
                    p.get("priority", "P9"),
                )
            )
            return Phase(**in_progress[0])

        # Priority 2: Find planned phases
        planned = [p for p in active_phases if p.get("status") == "planned"]
        if planned:
            planned.sort(
                key=lambda p: (
                    p.get("execution_order") is None,
                    p.get("execution_order", 999),
                    p.get("priority", "P9"),
                )
            )
            return Phase(**planned[0])

        return None

    def should_skip_dor(self) -> bool:
        """Determine if DoR/Challenge should be skipped.

        Returns:
            True if in autonomous mode (skip DoR/Challenge)
            False otherwise (show DoR/Challenge)
        """
        return self._autonomous_mode

    def is_autonomous_mode(self) -> bool:
        """Check if executor is in autonomous mode.

        Returns:
            True if autonomous mode active
        """
        return self._autonomous_mode

    def reset(self) -> None:
        """Reset autonomous mode state."""
        self._autonomous_mode = False
        self._last_input = None

    def get_continuation_reason(self) -> str:
        """Get human-readable reason for continuation detection.

        Returns:
            Reason string (e.g., "User said 'proceed'")
        """
        if not self._last_input:
            return "Unknown"

        normalized = self._last_input.lower().strip()

        # Check specific patterns
        if re.search(r"\b(proceed)\b", normalized):
            return "User said 'proceed'"
        if re.search(r"\b(continue)\b", normalized):
            return "User said 'continue'"
        if re.search(r"\b(yes|approve)\b", normalized):
            return "User approved"
        if re.search(r"\bphase[-\s]?\d+\b", normalized):
            match = re.search(r"\bphase[-\s]?(\d+)\b", normalized)
            if match:
                return f"User requested phase {match.group(1)}"
        if re.search(r"\bautonomous(?:ly)?\b", normalized):
            return "User requested autonomous execution"
        if re.search(r"\bbypass\s+challenge\b", normalized):
            return "User bypassed challenge"

        return "Continuation detected"
