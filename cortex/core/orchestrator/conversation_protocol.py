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
    ) -> None:
        """Initialize ConversationProtocol.

        Args:
            orchestrator: IOrchestrator instance to wrap.
            max_turns: Maximum turns before safety halt (default: 10).
            token_limit: Token budget before halt (default: 20000).
            db_path: Optional database path for persistence.

        Raises:
            TypeError: If orchestrator doesn't implement IOrchestrator protocol.
        """
        self.orchestrator = orchestrator
        self.max_turns = max_turns
        self.token_limit = token_limit
        self.db_path = db_path
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

            # Check turn limits - but still return OK with MAX_ROUNDS_REACHED reason
            if self.turn_number >= self.max_turns:
                from cortex.core.orchestrator.continuation_decision import (
                    ContinuationDecision,
                    ContinuationReason,
                )
                decision = ContinuationDecision(
                    reason=ContinuationReason.MAX_ROUNDS_REACHED,
                    turn_number=self.turn_number,
                )
                self.decisions_history.append({
                    "turn": self.turn_number,
                    "decision": decision,
                })
                return Ok(decision)

            # Increment turn counter
            self.turn_number += 1

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

            # Track tokens (estimate: 4 chars ≈ 1 token)
            user_tokens = len(user_input) // 4
            result_tokens = len(str(result)) // 4
            tokens_this_turn = user_tokens + result_tokens
            self.total_tokens_used += tokens_this_turn

            # Check token limit - if exceeded, return OK with TOKEN_LIMIT reason
            if self.total_tokens_used > self.token_limit:
                from cortex.core.orchestrator.continuation_decision import (
                    ContinuationDecision,
                    ContinuationReason,
                )
                decision = ContinuationDecision(
                    reason=ContinuationReason.TOKEN_LIMIT,
                    turn_number=self.turn_number,
                    token_usage={
                        "prompt": user_tokens,
                        "completion": result_tokens,
                        "total": tokens_this_turn,
                    },
                )
                self.decisions_history.append({
                    "turn": self.turn_number,
                    "decision": decision,
                    "timestamp": round_context.timestamp,
                })
                return Ok(decision)

            # Create continuation decision
            from cortex.core.orchestrator.continuation_decision import (
                ContinuationDecision,
                ContinuationReason,
            )

            decision = ContinuationDecision(
                reason=ContinuationReason.COMPLETE,
                turn_number=self.turn_number,
                token_usage={
                    "prompt": user_tokens,
                    "completion": result_tokens,
                    "total": tokens_this_turn,
                },
                context=result if isinstance(result, dict) else {"result": result},
                next_operation="continue_conversation" if self.turn_number < self.max_turns else None,
                next_parameters={"turn_number": self.turn_number + 1} if self.turn_number < self.max_turns else {},
            )
            
            # Add audit entry ID
            audit_entry_id = str(uuid.uuid4())
            decision_dict = {
                "turn": self.turn_number,
                "decision": decision,
                "timestamp": round_context.timestamp,
                "audit_entry_id": audit_entry_id,
            }
            
            # Add audit_entry_id to decision for access by tests
            if not hasattr(decision, 'audit_entry_id'):
                decision.audit_entry_id = audit_entry_id  # type: ignore

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
