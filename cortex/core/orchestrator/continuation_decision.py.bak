"""Continuation Decision - Manages turn-by-turn conversation continuation logic.

Determines whether a conversation should continue or terminate based on
completion state, tokens, and other criteria.

Production-ready implementation with:
- ContinuationReason enum for decision types
- ContinuationDecision frozen dataclass
- Token tracking and governance violation handling
- Audit trail integration

Author: Asif Hussain
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from cortex.models.canonical_enums import ContinuationReason




@dataclass(frozen=True)
class ContinuationDecision:
    """Continuation decision for a conversation turn.

    Frozen dataclass to ensure immutability.
    
    Attributes:
        should_continue: Whether to continue the conversation.
        reason: The reason for the decision (ContinuationReason enum).
        next_operation: The next operation to execute (if any).
        turn_number: The turn number for this decision.
        token_usage: Dictionary with prompt, completion, and total tokens.
        next_parameters: Parameters for the next operation.
        audit_entry_id: ID for audit trail entry.
        governance_violations: List of governance violations encountered.
    """

    should_continue: bool
    reason: ContinuationReason
    next_operation: Optional[str] = None
    turn_number: int = 0
    token_usage: Dict[str, int] = field(default_factory=lambda: {"prompt": 0, "completion": 0, "total": 0})
    next_parameters: Optional[Dict[str, Any]] = None
    audit_entry_id: Optional[str] = None
    governance_violations: List[str] = field(default_factory=list)

    @property
    def is_halt_by_governance(self) -> bool:
        """Check if halt was due to governance violation.
        
        Returns:
            True if governance violation caused halt, False otherwise.
        """
        return (
            self.reason == ContinuationReason.GOVERNANCE_HALT
            or len(self.governance_violations) > 0
        )
    
    @property
    def is_user_action_required(self) -> bool:
        """Check if user action is required to continue.
        
        Returns:
            True if user interaction needed, False otherwise.
        """
        return self.reason == ContinuationReason.INTERACTION_REQUIRED
    
    @property
    def is_safe_to_resume(self) -> bool:
        """Check if it's safe to resume operation later.
        
        Returns:
            True if safe to resume, False if error or halt.
        """
        safe_reasons = {
            ContinuationReason.TOKEN_LIMIT,
            ContinuationReason.COMPLETION,
            ContinuationReason.INTERACTION_REQUIRED,
        }
        return self.reason in safe_reasons
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary representation of decision.
        """
        return {
            "should_continue": self.should_continue,
            "reason": self.reason.name,
            "next_operation": self.next_operation,
            "turn_number": self.turn_number,
            "token_usage": self.token_usage.copy(),
            "next_parameters": self.next_parameters.copy() if self.next_parameters else {},
            "audit_entry_id": self.audit_entry_id,
            "governance_violations": self.governance_violations.copy(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContinuationDecision":
        """Create ContinuationDecision from dictionary.
        
        Args:
            data: Dictionary with decision data
        
        Returns:
            ContinuationDecision instance
        """
        reason = data.get("reason", "COMPLETION")
        if isinstance(reason, str):
            reason = ContinuationReason.from_string(reason)
        
        return cls(
            should_continue=data.get("should_continue", False),
            reason=reason,
            next_operation=data.get("next_operation"),
            turn_number=data.get("turn_number", 0),
            token_usage=data.get("token_usage", {"prompt": 0, "completion": 0, "total": 0}),
            next_parameters=data.get("next_parameters"),
            audit_entry_id=data.get("audit_entry_id"),
            governance_violations=data.get("governance_violations", []),
        )


__all__ = [
    "ContinuationDecision",
    "ContinuationReason",
]

