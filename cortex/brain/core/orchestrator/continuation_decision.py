"""
ContinuationDecision and ContinuationReason enum for orchestrator multi-turn execution.

ContinuationDecision explicitly specifies whether an orchestrator should continue
to another turn, and provides context about why the decision was made.

This replaces fragile implicit loop conditions with declarative, auditable decisions.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from cortex.models.canonical_enums import ContinuationReason


@dataclass(frozen=True)
class ContinuationDecision:
    """
    Explicit decision about whether orchestrator should continue after a turn.

    This dataclass replaces implicit loop conditions with declarative, auditable
    decisions that can be tested, logged, and reasoned about.

    Attributes:
        should_continue: bool - Continue to next turn or stop
        reason: ContinuationReason - Why the decision was made
        next_operation: str - What operation to do next (if continuing)
        turn_number: int - Which turn produced this decision
        token_usage: Dict[str, int] - Token usage for this turn
            - "prompt": tokens in prompt
            - "completion": tokens in response
            - "total": sum of prompt + completion
        next_parameters: Dict[str, Any] - Parameters for next operation (optional)
        audit_entry_id: str - Link to AC_COMPLETE audit entry (optional)
        governance_violations: List[str] - Governance rule violations detected (optional)
    """

    should_continue: bool
    reason: ContinuationReason
    next_operation: str
    turn_number: int
    token_usage: Dict[str, int]
    next_parameters: Dict[str, Any] = field(default_factory=dict)
    audit_entry_id: Optional[str] = None
    governance_violations: List[str] = field(default_factory=list)

    @property
    def is_halt_by_governance(self) -> bool:
        """
        Property: Is the decision to halt due to governance violation?

        Returns:
            True if reason is GOVERNANCE_HALT, False otherwise
        """
        return self.reason == ContinuationReason.GOVERNANCE_HALT

    @property
    def is_user_action_required(self) -> bool:
        """
        Property: Does the decision require user action to continue?

        Returns:
            True if reason is INTERACTION_REQUIRED or USER_REJECTION, False otherwise
        """
        return self.reason in (
            ContinuationReason.INTERACTION_REQUIRED,
            ContinuationReason.USER_REJECTION,
        )

    @property
    def is_safe_to_resume(self) -> bool:
        """
        Property: Can the workflow safely resume from this decision?

        Safe to resume: TOKEN_LIMIT, INTERACTION_REQUIRED, COMPLETION
        NOT safe: ERROR_UNRECOVERABLE, GOVERNANCE_HALT, MAX_ROUNDS_REACHED

        Returns:
            True if workflow can be resumed, False otherwise
        """
        safe_reasons = {
            ContinuationReason.TOKEN_LIMIT,
            ContinuationReason.INTERACTION_REQUIRED,
            ContinuationReason.COMPLETION,
        }
        return self.reason in safe_reasons

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ContinuationDecision to dictionary for JSON serialization.

        Returns:
            Dictionary representation suitable for JSON encoding
        """
        return {
            "should_continue": self.should_continue,
            "reason": self.reason.value,
            "next_operation": self.next_operation,
            "turn_number": self.turn_number,
            "token_usage": self.token_usage,
            "next_parameters": self.next_parameters,
            "audit_entry_id": self.audit_entry_id,
            "governance_violations": self.governance_violations,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContinuationDecision":
        """
        Create ContinuationDecision from dictionary (JSON deserialization).

        Args:
            data: Dictionary with ContinuationDecision fields

        Returns:
            ContinuationDecision instance

        Raises:
            KeyError: If required fields missing
            ValueError: If reason string invalid
        """
        # Convert reason string to enum if needed
        reason = data.get("reason")
        if isinstance(reason, str):
            reason = ContinuationReason.from_string(reason)

        return cls(
            should_continue=data["should_continue"],
            reason=reason,
            next_operation=data["next_operation"],
            turn_number=data["turn_number"],
            token_usage=data["token_usage"],
            next_parameters=data.get("next_parameters", {}),
            audit_entry_id=data.get("audit_entry_id"),
            governance_violations=data.get("governance_violations", []),
        )
