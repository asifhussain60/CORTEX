"""Continuation Decision - Manages turn-by-turn conversation continuation logic.

Determines whether a conversation should continue or terminate based on
completion state, tokens, and other criteria.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class ContinuationDecision(Enum):
    """Turn continuation decision types."""

    CONTINUE = "continue"
    COMPLETE = "complete"
    PAUSE = "pause"
    ERROR = "error"
    ESCALATE = "escalate"


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


def decide_continuation(context: ContinuationContext) -> ContinuationDecision:
    """Decide whether to continue a conversation.

    Args:
        context: Continuation context.

    Returns:
        ContinuationDecision indicating next action.
    """
    # Check for errors
    if context.error_message:
        return ContinuationDecision.ERROR

    # Check if work is complete
    if not context.has_more_work or context.completion_percentage >= 100:
        return ContinuationDecision.COMPLETE

    # Check token limits
    if context.tokens_remaining < 100:  # Minimum for next turn
        return ContinuationDecision.PAUSE

    # Check turn limits
    if context.turn_number > 20:  # Max 20 turns
        return ContinuationDecision.COMPLETE



    # Normal continuation
    return ContinuationDecision.CONTINUE


# Aliases for backward compatibility
ContinuationReason = ContinuationDecision

__all__ = [
    "ContinuationDecision",
    "ContinuationContext",
    "ContinuationReason",
    "decide_continuation",
]

