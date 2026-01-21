"""Continuation Decision - Manages turn-by-turn conversation continuation logic.

Determines whether a conversation should continue or terminate based on
completion state, tokens, and other criteria.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class ContinuationReason(Enum):
    """Turn continuation decision types."""

    CONTINUE = "continue"
    COMPLETE = "complete"
    PAUSE = "pause"
    ERROR = "error"
    ESCALATE = "escalate"
    MAX_ROUNDS_REACHED = "max_rounds_reached"


@dataclass
class ContinuationContext:
    """Context for continuation decision.

    Attributes:
        turn_number: Current turn number.
        tokens_used: Tokens used in current turn.
        tokens_remaining: Tokens remaining in conversation.
        has_more_work: Whether there's more work to do.
        completion_percentage: Estimated completion percentage (0-100).
        error_message: Error message if any.
    """

    turn_number: int
    tokens_used: int
    tokens_remaining: int
    has_more_work: bool = True
    completion_percentage: int = 0
    error_message: Optional[str] = None


@dataclass
class ContinuationDecision:
    """Continuation decision for a conversation turn.

    Attributes:
        reason: The reason for the decision (ContinuationReason enum).
        turn_number: The turn number for this decision.
        token_usage: Dictionary with prompt, completion, and total tokens.
        context: Additional context data from this turn.
        next_operation: The next operation to execute (if any).
        next_parameters: Parameters for the next operation.
        governance_violation: Any governance violation encountered.
    """

    reason: ContinuationReason
    turn_number: int = 0
    token_usage: Dict[str, int] = field(default_factory=lambda: {"prompt": 0, "completion": 0, "total": 0})
    context: Dict[str, Any] = field(default_factory=dict)
    next_operation: Optional[str] = None
    next_parameters: Dict[str, Any] = field(default_factory=dict)
    governance_violation: Optional[str] = None


def decide_continuation(context: ContinuationContext) -> ContinuationReason:
    """Decide whether to continue a conversation.

    Args:
        context: Continuation context.

    Returns:
        ContinuationReason indicating next action.
    """
    # Check for errors
    if context.error_message:
        return ContinuationReason.ERROR

    # Check if work is complete
    if not context.has_more_work or context.completion_percentage >= 100:
        return ContinuationReason.COMPLETE

    # Check token limits
    if context.tokens_remaining < 100:  # Minimum for next turn
        return ContinuationReason.PAUSE

    # Check turn limits
    if context.turn_number > 20:  # Max 20 turns
        return ContinuationReason.COMPLETE

    # Normal continuation
    return ContinuationReason.CONTINUE


__all__ = [
    "ContinuationDecision",
    "ContinuationContext",
    "ContinuationReason",
    "decide_continuation",
]

