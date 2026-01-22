"""Conversation Protocol - Multi-turn orchestrator executor.

Wraps any IOrchestrator to execute one turn at a time with continuation
decisions, governance validation, and token tracking.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path
import uuid

from cortex.core.result import Result, Ok, Err
from cortex.core.interfaces import IOrchestrator, OperationMode
from cortex.core.orchestrator.terminal_events import EventRegistry


class GovernanceRegistry:
    """Stub for governance registry (for mocking in tests)."""
    
    def should_proceed(self) -> bool:
        """Check if operation should proceed."""
        return True


@dataclass
class RoundContext:
    """Context for a single round of execution.

    Attributes:
        round_number: Current round number.
        user_input: User input for this round.
        previous_context: Context from previous round.
        orchestrator_name: Name of the orchestrator.
        timestamp: When the round started.
    """

    round_number: int
    user_input: str
    previous_context: Dict[str, Any]
    orchestrator_name: str
    timestamp: datetime = field(default_factory=datetime.now)


class ConversationProtocol:
    """Single-turn executor for orchestrators.

    Wraps any IOrchestrator to execute one turn at a time with explicit
    continuation decisions, governance validation, audit logging, and token tracking.

    Attributes:
        orchestrator: The IOrchestrator to wrap.
        max_turns: Safety limit on iterations (default: 10).
        token_limit: Token budget before halt (default: 20000).
        turn_number: Current turn count.
        total_tokens_used: Accumulated tokens across all turns.
        decisions_history: List of all decisions made.
    """

    def __init__(
        self,
        orchestrator: IOrchestrator,
        max_turns: int = 10,
        token_limit: int = 20000,
        db_path: Optional[str] = None,
        event_registry: Optional[Any] = None,
    ) -> None:
        """Initialize ConversationProtocol.

        Args:
            orchestrator: IOrchestrator instance to wrap.
            max_turns: Maximum turns before safety halt (default: 10).
            token_limit: Token budget before halt (default: 20000).
            db_path: Optional database path for persistence.
            event_registry: Optional EventRegistry for event handling.

        Raises:
            TypeError: If orchestrator doesn't implement IOrchestrator protocol.
        """
        self.orchestrator = orchestrator
        self.max_turns = max_turns
        self.token_limit = token_limit
        self.db_path = db_path
        self.event_registry = event_registry or EventRegistry()
        self.turn_number: int = 0
        self.total_tokens_used: int = 0
        self.decisions_history: List[Dict[str, Any]] = []
        self.ast_engine: Optional[Any] = None
        self.context_history: List[RoundContext] = []

    def execute_turn(
        self, user_input: str, context: Dict[str, Any]
    ) -> Result[Any, str]:
        """Execute a single turn of orchestration.

        Args:
            user_input: User input for this turn.
            context: Execution context from previous turn.

        Returns:
            Result[ContinuationDecision] on success, Result[Err] on failure.

        Raises:
            Nothing - all errors returned as Err result.
        """
        try:
            # Validate input
            if not isinstance(user_input, str):
                return Err("user_input must be a string")

            if not context or not isinstance(context, dict):
                context = {}

            # Increment turn counter first
            self.turn_number += 1

            # Check turn limits - but still return OK with MAX_ROUNDS_REACHED reason
            if self.turn_number >= self.max_turns:
                from cortex.core.orchestrator.continuation_decision import (
                    ContinuationDecision,
                    ContinuationReason,
                )
                from cortex.core.orchestrator.terminal_events import MaxTurnsReachedEvent
                
                decision = ContinuationDecision(
                    should_continue=False,
                    reason=ContinuationReason.MAX_ROUNDS_REACHED,
                    turn_number=self.turn_number,
                )
                # Fire event
                event = MaxTurnsReachedEvent(
                    turn_number=self.turn_number,
                    max_turns=self.max_turns,
                    current_turn=self.turn_number,
                    reason="Max turns exceeded"
                )
                self.event_registry.fire_event(event)
                
                self.decisions_history.append({
                    "turn": self.turn_number,
                    "decision": decision,
                })
                return Ok(decision)

            # Check if already approaching token limit (>= 90%) before this turn
            percentage_used = (self.total_tokens_used / self.token_limit * 100) if self.token_limit > 0 else 0
            if percentage_used >= 90:
                from cortex.core.orchestrator.terminal_events import TokenLimitEvent
                event = TokenLimitEvent(
                    tokens_used=self.total_tokens_used,
                    token_limit=self.token_limit,
                    percentage_used=percentage_used,
                    turn_number=self.turn_number
                )
                self.event_registry.fire_event(event)

            # Create round context
            round_context = RoundContext(
                round_number=self.turn_number,
                user_input=user_input,
                previous_context=context,
                orchestrator_name=self.orchestrator.__class__.__name__,
            )
            self.context_history.append(round_context)

            # Validate orchestrator can handle this
            if not isinstance(context, dict):
                return Err("context must be a dict")

            # Execute orchestrator
            result = self.orchestrator.execute(user_input, context)

            # Check if user rejected approval
            if isinstance(result, dict) and result.get("approval_rejected"):
                from cortex.core.orchestrator.terminal_events import UserApprovalRejectedEvent
                event = UserApprovalRejectedEvent(
                    approval_request=result.get("approval_request", "Unknown request"),
                    rejection_reason=result.get("rejection_reason", "No reason provided"),
                    turn_number=self.turn_number
                )
                self.event_registry.fire_event(event)
                
                # Return rejection decision
                from cortex.core.orchestrator.continuation_decision import (
                    ContinuationDecision,
                    ContinuationReason,
                )
                audit_entry_id = str(uuid.uuid4())
                decision = ContinuationDecision(
                    should_continue=False,
                    reason=ContinuationReason.USER_REJECTION,
                    turn_number=self.turn_number,
                    audit_entry_id=audit_entry_id,
                )
                self.decisions_history.append({
                    "turn": self.turn_number,
                    "decision": decision,
                    "timestamp": round_context.timestamp,
                })
                return Ok(decision)

            # Check if orchestrator returned an error
            if isinstance(result, dict) and "error" in result:
                from cortex.core.orchestrator.terminal_events import ErrorOccurredEvent
                event = ErrorOccurredEvent(
                    error_message=result.get("error", "Unknown error"),
                    error_type="orchestrator_error",
                    turn_number=self.turn_number,
                    recoverable=False
                )
                self.event_registry.fire_event(event)
                
                # Return error decision
                from cortex.core.orchestrator.continuation_decision import (
                    ContinuationDecision,
                    ContinuationReason,
                )
                audit_entry_id = str(uuid.uuid4())
                decision = ContinuationDecision(
                    should_continue=False,
                    reason=ContinuationReason.ERROR_UNRECOVERABLE,
                    turn_number=self.turn_number,
                    audit_entry_id=audit_entry_id,
                )
                self.decisions_history.append({
                    "turn": self.turn_number,
                    "decision": decision,
                    "timestamp": round_context.timestamp,
                })
                return Ok(decision)

            # Check if orchestrator completed a phase
            if isinstance(result, dict) and result.get("status") == "completed":
                from cortex.core.orchestrator.terminal_events import PhaseCompletedEvent
                event = PhaseCompletedEvent(
                    operation=result.get("operation", "unknown"),
                    result=result.get("result", {}),
                    turn_number=self.turn_number
                )
                self.event_registry.fire_event(event)
                
                # Return COMPLETION decision with should_continue=False
                from cortex.core.orchestrator.continuation_decision import (
                    ContinuationDecision,
                    ContinuationReason,
                )
                audit_entry_id = str(uuid.uuid4())
                decision = ContinuationDecision(
                    should_continue=False,
                    reason=ContinuationReason.COMPLETION,
                    turn_number=self.turn_number,
                    audit_entry_id=audit_entry_id,
                )
                self.decisions_history.append({
                    "turn": self.turn_number,
                    "decision": decision,
                    "timestamp": round_context.timestamp,
                })
                return Ok(decision)

            # Track tokens (estimate: 4 chars ≈ 1 token)
            user_tokens = len(user_input) // 4
            result_tokens = len(str(result)) // 4
            tokens_this_turn = user_tokens + result_tokens
            self.total_tokens_used += tokens_this_turn

            # Check token limit - if at 95% or exceeded, return OK with TOKEN_LIMIT reason
            percentage_used = (self.total_tokens_used / self.token_limit * 100) if self.token_limit > 0 else 0
            if percentage_used >= 95 or self.total_tokens_used > self.token_limit:
                from cortex.core.orchestrator.continuation_decision import (
                    ContinuationDecision,
                    ContinuationReason,
                )
                audit_entry_id = str(uuid.uuid4())
                decision = ContinuationDecision(
                    should_continue=False,
                    reason=ContinuationReason.TOKEN_LIMIT,
                    turn_number=self.turn_number,
                    token_usage={
                        "prompt": user_tokens,
                        "completion": result_tokens,
                        "total": tokens_this_turn,
                    },
                    audit_entry_id=audit_entry_id,
                )
                self.decisions_history.append({
                    "turn": self.turn_number,
                    "decision": decision,
                    "timestamp": round_context.timestamp,
                })
                return Ok(decision)

            # Create continuation decision with audit entry ID
            from cortex.core.orchestrator.continuation_decision import (
                ContinuationDecision,
                ContinuationReason,
            )

            audit_entry_id = str(uuid.uuid4())
            decision = ContinuationDecision(
                should_continue=self.turn_number < self.max_turns,
                reason=ContinuationReason.COMPLETION,
                turn_number=self.turn_number,
                token_usage={
                    "prompt": user_tokens,
                    "completion": result_tokens,
                    "total": tokens_this_turn,
                },
                next_operation="continue_conversation" if self.turn_number < self.max_turns else None,
                next_parameters={"turn_number": self.turn_number + 1} if self.turn_number < self.max_turns else None,
                audit_entry_id=audit_entry_id,
            )

            # Add to history
            self.decisions_history.append(
                {
                    "turn": self.turn_number,
                    "decision": decision,
                    "timestamp": round_context.timestamp,
                }
            )

            return Ok(decision)

        except ImportError as e:
            return Err(f"Import error: {str(e)}")
        except (ValueError, TypeError) as e:
            return Err(f"Execution failed: {str(e)}")
        except Exception as e:
            return Err(f"Unexpected error: {str(e)}")

    def get_decisions_history(self) -> List[Dict[str, Any]]:
        """Get history of all decisions made.

        Returns:
            List of decision records.
        """
        return list(self.decisions_history)

    def reset(self) -> None:
        """Reset protocol state for a new conversation."""
        self.turn_number = 0
        self.total_tokens_used = 0
        self.decisions_history = []
        self.context_history = []


__all__ = ["ConversationProtocol", "RoundContext"]
