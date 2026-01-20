"""Detection and Recovery - Detect and recover from hallucination events.

Provides detection of hallucination patterns and recovery mechanisms.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class HallucinationPattern(Enum):
    """Types of hallucination patterns."""

    FACTUAL_ERROR = "factual_error"
    LOGICAL_CONTRADICTION = "logical_contradiction"
    CONTEXT_DRIFT = "context_drift"
    CONFABULATION = "confabulation"
    INCONSISTENCY = "inconsistency"


@dataclass
class HallucinationEvent:
    """A detected hallucination event.

    Attributes:
        pattern: Type of hallucination.
        severity: Severity level (0-100).
        description: Event description.
        context: Related context.
        recovery_applied: Whether recovery was applied.
    """

    pattern: HallucinationPattern
    severity: int
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    recovery_applied: bool = False


class HallucinationDetector:
    """Detects hallucination patterns."""

    def __init__(self) -> None:
        """Initialize detector."""
        self.events: List[HallucinationEvent] = []
        self.thresholds = {
            HallucinationPattern.FACTUAL_ERROR: 70,
            HallucinationPattern.LOGICAL_CONTRADICTION: 80,
            HallucinationPattern.CONTEXT_DRIFT: 60,
            HallucinationPattern.CONFABULATION: 75,
            HallucinationPattern.INCONSISTENCY: 65,
        }

    def detect(
        self,
        pattern: HallucinationPattern,
        severity: int,
        description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> HallucinationEvent:
        """Detect a hallucination event.

        Args:
            pattern: Type of hallucination.
            severity: Severity level.
            description: Description.
            context: Related context.

        Returns:
            HallucinationEvent.
        """
        event = HallucinationEvent(
            pattern=pattern,
            severity=severity,
            description=description,
            context=context or {},
        )
        self.events.append(event)
        return event

    def is_critical(self, event: HallucinationEvent) -> bool:
        """Check if event is critical.

        Args:
            event: Event to check.

        Returns:
            True if critical, False otherwise.
        """
        threshold = self.thresholds.get(event.pattern, 50)
        return event.severity >= threshold

    def get_events(self, pattern: Optional[HallucinationPattern] = None) -> List[HallucinationEvent]:
        """Get detected events.

        Args:
            pattern: Optional filter by pattern.

        Returns:
            List of events.
        """
        if pattern:
            return [e for e in self.events if e.pattern == pattern]
        return self.events.copy()

    def clear_events(self) -> None:
        """Clear event history."""
        self.events.clear()


class HallucinationRecovery:
    """Recovers from hallucination events."""

    def __init__(self) -> None:
        """Initialize recovery."""
        self.recovery_actions: Dict[HallucinationPattern, list] = {}

    def register_recovery(self, pattern: HallucinationPattern, action: callable) -> None:
        """Register recovery action.

        Args:
            pattern: Hallucination pattern.
            action: Recovery action callable.
        """
        if pattern not in self.recovery_actions:
            self.recovery_actions[pattern] = []
        self.recovery_actions[pattern].append(action)

    def recover(self, event: HallucinationEvent) -> bool:
        """Apply recovery for an event.

        Args:
            event: Event to recover from.

        Returns:
            True if recovery successful, False otherwise.
        """
        actions = self.recovery_actions.get(event.pattern, [])

        for action in actions:
            try:
                result = action(event)
                if result:
                    event.recovery_applied = True
                    return True
            except Exception:
                pass

        return False

    def get_recovery_status(self, pattern: HallucinationPattern) -> int:
        """Get number of recovery actions for pattern.

        Args:
            pattern: Hallucination pattern.

        Returns:
            Number of registered actions.
        """
        return len(self.recovery_actions.get(pattern, []))




@dataclass
class CorruptionDetectionResult:
    """Result of corruption detection."""
    is_corrupted: bool
    corruption_type: Optional[str] = None
    confidence: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

__all__ = [
    "HallucinationDetector",
    "HallucinationRecovery",
    "HallucinationEvent",
    "HallucinationPattern",
    "CorruptionIndicator",
]

# Aliases and stubs for test compatibility
class CorruptionIndicator(Enum):
    """Types of corruption indicators."""
    INVALID_STATE = "invalid_state"
    INCONSISTENT_DATA = "inconsistent_data"
    MISSING_REFERENCE = "missing_reference"
