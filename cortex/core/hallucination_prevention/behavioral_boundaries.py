"""behavioral_boundaries.py - Behavioral boundary protection.

Prevents locked phase modification, AC deletion, and governance bypass.
Enforces boundaries that protect system integrity and governance compliance.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime


class ViolationType(Enum):
    """Types of boundary violations."""
    LOCKED_PHASE_MODIFICATION = "locked_phase_modification"
    AC_DELETION = "ac_deletion"
    GOVERNANCE_BYPASS = "governance_bypass"
    PERMISSION_VIOLATION = "permission_violation"
    STATE_VIOLATION = "state_violation"


@dataclass
class BoundaryViolation:
    """Represents a boundary rule violation."""
    violation_type: ViolationType
    entity_id: str
    action: str
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: Dict[str, Any] = field(default_factory=dict)


class BehavioralBoundaryRules:
    """Enforces behavioral boundaries to protect system integrity."""

    def __init__(self):
        """Initialize behavioral boundary rules."""
        self.violations: List[BoundaryViolation] = []
        self.protected_phases: set = set()
        self.protected_acs: set = set()

    def lock_phase(self, phase_id: str) -> None:
        """Lock a phase from modification.

        Args:
            phase_id: Phase identifier.
        """
        self.protected_phases.add(phase_id)

    def unlock_phase(self, phase_id: str) -> None:
        """Unlock a phase for modification.

        Args:
            phase_id: Phase identifier.
        """
        self.protected_phases.discard(phase_id)

    def protect_ac(self, ac_id: str) -> None:
        """Protect an AC from deletion.

        Args:
            ac_id: AC identifier.
        """
        self.protected_acs.add(ac_id)

    def unprotect_ac(self, ac_id: str) -> None:
        """Unprotect an AC from deletion.

        Args:
            ac_id: AC identifier.
        """
        self.protected_acs.discard(ac_id)

    def check_phase_modification(self, phase_id: str, action: str) -> bool:
        """Check if phase modification is allowed.

        Args:
            phase_id: Phase identifier.
            action: Action to perform (MODIFY, DELETE, etc.).

        Returns:
            True if modification is allowed.

        Raises:
            BoundaryViolation: If modification is not allowed.
        """
        if phase_id in self.protected_phases and action in ["MODIFY", "DELETE"]:
            violation = BoundaryViolation(
                violation_type=ViolationType.LOCKED_PHASE_MODIFICATION,
                entity_id=phase_id,
                action=action,
                reason=f"Phase {phase_id} is locked",
            )
            self.violations.append(violation)
            raise Exception(f"Boundary violation: {violation.reason}")
        return True

    def check_ac_deletion(self, ac_id: str) -> bool:
        """Check if AC deletion is allowed.

        Args:
            ac_id: AC identifier.

        Returns:
            True if deletion is allowed.

        Raises:
            BoundaryViolation: If deletion is not allowed.
        """
        if ac_id in self.protected_acs:
            violation = BoundaryViolation(
                violation_type=ViolationType.AC_DELETION,
                entity_id=ac_id,
                action="DELETE",
                reason=f"AC {ac_id} is protected",
            )
            self.violations.append(violation)
            raise Exception(f"Boundary violation: {violation.reason}")
        return True

    def get_violations(self) -> List[BoundaryViolation]:
        """Get all recorded violations.

        Returns:
            List of boundary violations.
        """
        return self.violations.copy()

    def clear_violations(self) -> None:
        """Clear violation history."""
        self.violations.clear()

