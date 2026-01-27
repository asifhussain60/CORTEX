"""Phase Events - Events for phase completion and lifecycle.

Events for tracking phase transitions and completions.

Author: CORTEX Framework
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum


class PhaseType(Enum):
    """Types of phases."""

    DISCOVERY = "discovery"
    ANALYSIS = "analysis"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    COMPLETION = "completion"


@dataclass
class PhaseCompletedEvent:
    """Event when a phase completes.

    Attributes:
        phase_id: Phase identifier.
        phase_type: Type of phase.
        duration_ms: Phase duration.
        status: Completion status (success/failure).
        timestamp: When phase completed.
        metadata: Additional metadata.
    """

    phase_id: str
    phase_type: PhaseType
    duration_ms: int
    status: str = "success"
    timestamp: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class PhaseEventHandler:
    """Handles phase lifecycle events."""

    def __init__(self) -> None:
        """Initialize event handler."""
        self.events: list = []

    def emit_phase_completed(
        self,
        phase_id: str,
        phase_type: PhaseType,
        duration_ms: int,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PhaseCompletedEvent:
        """Emit a phase completed event.

        Args:
            phase_id: Phase ID.
            phase_type: Phase type.
            duration_ms: Duration in milliseconds.
            status: Completion status.
            metadata: Optional metadata.

        Returns:
            PhaseCompletedEvent.
        """
        event = PhaseCompletedEvent(
            phase_id=phase_id,
            phase_type=phase_type,
            duration_ms=duration_ms,
            status=status,
            metadata=metadata or {},
        )
        self.events.append(event)
        return event

    def get_events(self, phase_type: Optional[PhaseType] = None) -> list:
        """Get events.

        Args:
            phase_type: Optional filter by phase type.

        Returns:
            List of events.
        """
        if phase_type:
            return [e for e in self.events if e.phase_type == phase_type]
        return self.events.copy()


__all__ = ["PhaseCompletedEvent", "PhaseEventHandler", "PhaseType"]
