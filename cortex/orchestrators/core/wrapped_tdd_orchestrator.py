# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: AC-REM-011-03 - WrappedTDDOrchestrator with ConversationProtocol
"""
WrappedTDDOrchestrator - Multi-turn TDD conversation management.

PHASE-REMEDIATION-07: TDD Orchestrator Enhancement
AC-ID: AC-REM-011-03 - Implement WrappedTDDOrchestrator with ConversationProtocol

This orchestrator wraps TDDOrchestrator with ConversationProtocol to provide:
1. Multi-turn conversation support via execute_with_continuation()
2. ContinuationDecision logic (halt, continue, next operation routing)
3. EventRegistry for event-driven callbacks (CompletionEvent, ErrorEvent)
4. Token usage tracking across turns (prompt + completion tokens)
5. Domain-specific next operation suggestions (RED → GREEN → REFACTOR)
6. Full round-trip execution: user input → TDD logic → response

Architecture:
- TDDOrchestrator: Pure TDD logic (phase determination, rules, guidance)
- ConversationProtocol: Turn execution and continuation management
- WrappedTDDOrchestrator: Orchestrates both, manages conversation state

Governance:
  - CORE-008: TDD (tests first)
  - CORE-011: Type hints on ALL functions (params + returns)
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling (no bare except)
  - CORE-019: ALL implementation intents route through TDD-Master
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from cortex.core.result import Ok, Err
from cortex.orchestrators.core.tdd_orchestrator import (
    TDDOrchestrator,
    TDDPhase,
    TDDImplementationGuidance
)
from cortex.brain.core.orchestrator.conversation_protocol import (
    ConversationProtocol,
    RoundContext
)
from cortex.brain.core.orchestrator.continuation_decision import (
    ContinuationDecision,
    ContinuationReason
)
from cortex.brain.core.orchestrator.terminal_events import (
    EventRegistry,
    TerminalEvent,
    PhaseCompletedEvent,
    ErrorOccurredEvent,
    GovernanceViolationEvent,
    TokenLimitEvent,
    MaxTurnsReachedEvent
)


logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES FOR WRAPPED ORCHESTRATOR
# =============================================================================

@dataclass
class TDDTurn:
    """Single turn in TDD conversation."""

    turn_number: int
    user_input: str
    tdd_phase: TDDPhase
    timestamp: datetime
    tdd_guidance: Optional[TDDImplementationGuidance] = None
    response: Optional[Dict[str, Any]] = None
    token_usage: Dict[str, int] = field(default_factory=lambda: {
        "prompt": 0,
        "completion": 0,
        "total": 0
    })
    continuation_reason: Optional[ContinuationReason] = None


@dataclass
class TDDConversationContext:
    """Context maintained across TDD conversation turns."""

    initial_input: str
    initial_context: Dict[str, Any]
    module_path: Optional[str] = None
    domain: Optional[str] = None
    turn_count: int = 0
    total_tokens_used: int = 0
    turn_history: List[TDDTurn] = field(default_factory=list)
    governance_violations: List[str] = field(default_factory=list)
    continuation_reasons: List[ContinuationReason] = field(default_factory=list)

    def add_turn(self, turn: TDDTurn) -> None:
        """Add turn to history.

        Args:
            turn: TDDTurn to record

        AC-REM-011-03: Track turn in conversation context
        """
        self.turn_history.append(turn)
        self.turn_count += 1
        self.total_tokens_used += turn.token_usage.get("total", 0)

    def add_governance_violation(self, violation: str) -> None:
        """Record governance violation.

        Args:
            violation: Violation message

        AC-REM-011-03: Track governance violations
        """
        self.governance_violations.append(violation)

    def add_continuation_reason(self, reason: ContinuationReason) -> None:
        """Record continuation reason.

        Args:
            reason: ContinuationReason

        AC-REM-011-03: Track halt/continue decisions
        """
        self.continuation_reasons.append(reason)


class WrappedTDDOrchestrator:
    """
    Multi-turn TDD orchestrator with ConversationProtocol integration.

    CORE-019: ALL implementation intents route through TDD-Master

    AC-REM-011-03: Orchestrate TDD workflow across multiple turns with
    explicit continuation decisions, event callbacks, and token tracking.
    """

    def __init__(
        self,
        tdd_orchestrator: Optional[TDDOrchestrator] = None,
        conversation_protocol: Optional[ConversationProtocol] = None,
        event_registry: Optional[EventRegistry] = None
    ) -> None:
        """Initialize WrappedTDDOrchestrator.

        Args:
            tdd_orchestrator: TDD orchestrator instance (default: new instance)
            conversation_protocol: Conversation protocol (default: new instance)
            event_registry: Event registry for callbacks (default: new instance)

        AC-REM-011-03: Initialize wrapped orchestrator with required components
        """
        self.tdd_orchestrator = tdd_orchestrator or TDDOrchestrator()
        self.conversation_protocol = conversation_protocol
        self.event_registry = event_registry or EventRegistry()

        self.turn_count: int = 0
        self.total_tokens_used: int = 0
        self.turn_history: List[TDDTurn] = []
        self.conversation_context: Optional[TDDConversationContext] = None

        self.logger = logging.getLogger(__name__)
        self.logger.info("WrappedTDDOrchestrator initialized")

    # =========================================================================
    # SINGLE TURN EXECUTION
    # =========================================================================

    def execute_turn(
        self,
        user_input: str,
        tdd_phase: TDDPhase,
        context: Optional[Dict[str, Any]] = None
    ) -> Union[Ok[List[ContinuationDecision]], Err[str]]:
        """
        Execute single turn of TDD workflow.

        CORE-008: TDD discipline - routes through TDD orchestrator

        Args:
            user_input: User request (e.g., "Write failing test")
            tdd_phase: TDD phase (RED, GREEN, REFACTOR)
            context: Optional execution context

        Returns:
            Result with list of ContinuationDecision objects

        AC-REM-011-03-02: Execute single TDD turn
        """
        try:
            self.turn_count += 1
            turn_timestamp = datetime.now()

            # Extract module path from context if available
            module_path = context.get("module_path", "unknown") if context else "unknown"

            # Route through TDD orchestrator
            tdd_guidance_result = self.tdd_orchestrator.route_implementation_intent(
                user_input,
                module_path,
                context=context
            )

            if tdd_guidance_result.is_err():
                error_msg = tdd_guidance_result.error
                self.logger.error(f"TDD routing failed: {error_msg}")
                return Err(error_msg)

            tdd_guidance = tdd_guidance_result.unwrap()

            # Execute appropriate TDD phase
            phase_result = self._execute_tdd_phase(tdd_phase, module_path, user_input)

            if phase_result.is_err():
                return Err(phase_result.error)

            phase_response = phase_result.unwrap()

            # Record turn
            turn = TDDTurn(
                turn_number=self.turn_count,
                user_input=user_input,
                tdd_phase=tdd_phase,
                timestamp=turn_timestamp,
                tdd_guidance=tdd_guidance,
                response=phase_response,
                token_usage=self._estimate_token_usage(user_input, phase_response)
            )

            self.turn_history.append(turn)
            self.total_tokens_used += turn.token_usage["total"]

            # Create continuation decision
            continuation_reason = self._determine_continuation_reason(tdd_phase)
            next_operation = self._suggest_next_operation(tdd_phase)

            decision = ContinuationDecision(
                should_continue=continuation_reason != ContinuationReason.COMPLETION,
                reason=continuation_reason,
                next_operation=next_operation,
                turn_number=self.turn_count,
                token_usage=turn.token_usage,
                next_parameters={"tdd_phase": tdd_phase.value}
            )

            return Ok([decision])

        except ValueError as e:
            self.logger.error(f"Invalid input: {e}")
            return Err(f"Invalid input: {e}")
        except Exception as e:
            self.logger.error(f"Turn execution failed: {e}")
            return Err(f"Turn execution failed: {e}")

    def _execute_tdd_phase(
        self,
        phase: TDDPhase,
        module_path: str,
        spec: str
    ) -> Union[Ok[Dict[str, Any]], Err[str]]:
        """Execute specific TDD phase.

        Args:
            phase: TDD phase (RED, GREEN, REFACTOR)
            module_path: Module being implemented
            spec: Specification or description

        Returns:
            Result with phase response

        AC-REM-011-03: Execute TDD phase via orchestrator
        """
        try:
            if phase == TDDPhase.RED:
                return self.tdd_orchestrator.execute_red_phase(module_path, spec)
            elif phase == TDDPhase.GREEN:
                return self.tdd_orchestrator.execute_green_phase(module_path, spec)
            elif phase == TDDPhase.REFACTOR:
                return self.tdd_orchestrator.execute_refactor_phase(module_path, spec)
            else:
                return Err(f"Unknown TDD phase: {phase}")
        except Exception as e:
            return Err(f"Phase execution failed: {e}")

    # =========================================================================
    # MULTI-TURN CONTINUATION
    # =========================================================================

    def execute_with_continuation(
        self,
        initial_input: str,
        initial_context: Optional[Dict[str, Any]] = None,
        max_turns: int = 10,
        token_budget: int = 8000
    ) -> Union[Ok[List[ContinuationDecision]], Err[str]]:
        """
        Execute TDD workflow with multi-turn continuation.

        Per CORE-008: Tests BEFORE implementation, with explicit halt decisions.

        Args:
            initial_input: Initial user request
            initial_context: Initial execution context
            max_turns: Maximum turns before halt (safety limit)
            token_budget: Maximum tokens allowed

        Returns:
            Result with list of ContinuationDecision objects from all turns

        AC-REM-011-03-03: Execute multi-turn TDD conversation
        """
        try:
            # Initialize conversation context
            self.conversation_context = TDDConversationContext(
                initial_input=initial_input,
                initial_context=initial_context or {},
                module_path=initial_context.get("module_path") if initial_context else None,
                domain=initial_context.get("domain") if initial_context else None
            )

            decisions: List[ContinuationDecision] = []
            current_input = initial_input
            current_context = initial_context or {}

            # Multi-turn loop
            turn_num = 0
            while turn_num < max_turns:
                turn_num += 1

                # Check token budget
                if self.total_tokens_used >= token_budget:
                    reason = ContinuationReason.TOKEN_LIMIT
                    self.conversation_context.add_continuation_reason(reason)
                    event = TokenLimitEvent(
                        turn_number=turn_num,
                        tokens_used=self.total_tokens_used,
                        token_limit=token_budget,
                        percentage_used=float(self.total_tokens_used) / float(token_budget) * 100.0
                    )
                    self.event_registry.fire_event(event)
                    break

                # Determine TDD phase from input
                phase = self._determine_tdd_phase_from_input(current_input)

                # Execute single turn
                turn_result = self.execute_turn(
                    current_input,
                    phase,
                    context=current_context
                )

                if turn_result.is_err():
                    # Error occurred - fire ErrorEvent and halt
                    error_msg = turn_result.unwrap_err()
                    event = ErrorOccurredEvent(
                        turn_number=turn_num,
                        error_message=error_msg,
                        error_type="execution_error",
                        recoverable=False
                    )
                    self.event_registry.fire_event(event)
                    self.conversation_context.add_continuation_reason(ContinuationReason.ERROR_UNRECOVERABLE)
                    break

                turn_decisions = turn_result.unwrap()
                decisions.extend(turn_decisions)

                # Check continuation
                last_decision = turn_decisions[-1] if turn_decisions else None
                if last_decision:
                    self.conversation_context.add_continuation_reason(last_decision.reason)

                    if not last_decision.should_continue:
                        # Fire completion event
                        event = PhaseCompletedEvent(
                            turn_number=turn_num,
                            operation="tdd_workflow",
                            result=f"TDD workflow completed after {turn_num} turns"
                        )
                        self.event_registry.fire_event(event)
                        break

                    # Prepare for next turn
                    current_input = last_decision.next_operation
                    if last_decision.next_parameters:
                        current_context.update(last_decision.next_parameters)

                # Safety: halt at max turns
                if turn_num >= max_turns:
                    self.conversation_context.add_continuation_reason(ContinuationReason.MAX_ROUNDS_REACHED)
                    break

            return Ok(decisions)

        except Exception as e:
            self.logger.error(f"Continuation execution failed: {e}")
            return Err(f"Continuation execution failed: {e}")

    # =========================================================================
    # CONTEXT MANAGEMENT
    # =========================================================================

    def get_conversation_context(self) -> Optional[TDDConversationContext]:
        """Get current conversation context.

        Returns:
            Current TDDConversationContext or None

        AC-REM-011-03-04: Access conversation state
        """
        return self.conversation_context

    def set_conversation_context(self, context: TDDConversationContext) -> None:
        """Set conversation context.

        Args:
            context: TDDConversationContext to set

        AC-REM-011-03-04: Update conversation state
        """
        self.conversation_context = context

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _determine_tdd_phase_from_input(self, user_input: str) -> TDDPhase:
        """Determine TDD phase from user input.

        Args:
            user_input: User input string

        Returns:
            TDD phase (RED, GREEN, REFACTOR)

        AC-REM-011-03: Determine phase from input
        """
        input_lower = user_input.lower()

        if any(word in input_lower for word in ["test", "red", "failing"]):
            return TDDPhase.RED
        elif any(word in input_lower for word in ["refactor", "improve", "optimize"]):
            return TDDPhase.REFACTOR
        else:
            return TDDPhase.GREEN

    def _determine_continuation_reason(self, phase: TDDPhase) -> ContinuationReason:
        """Determine continuation reason based on TDD phase.

        Args:
            phase: Current TDD phase

        Returns:
            ContinuationReason

        AC-REM-011-03-05: Map TDD phase to continuation decision
        """
        if phase == TDDPhase.REFACTOR:
            # After REFACTOR, typically complete or start new test
            return ContinuationReason.COMPLETION
        else:
            # RED and GREEN continue to next phase
            return ContinuationReason.IMPLICIT_NEXT_OPERATION

    def _suggest_next_operation(self, phase: TDDPhase) -> str:
        """Suggest next operation based on TDD phase.

        Args:
            phase: Current TDD phase

        Returns:
            Suggested next operation

        AC-REM-011-03-08: Route to appropriate next phase
        """
        if phase == TDDPhase.RED:
            return "implement_solution"
        elif phase == TDDPhase.GREEN:
            return "refactor_for_clarity"
        else:  # REFACTOR
            return "run_full_test_suite"

    def _estimate_token_usage(
        self,
        user_input: str,
        response: Dict[str, Any]
    ) -> Dict[str, int]:
        """Estimate token usage for turn.

        Args:
            user_input: User input string
            response: Response dictionary

        Returns:
            Dictionary with prompt, completion, and total tokens

        AC-REM-011-03-07: Track token usage per turn
        """
        # Simple estimation: ~4 chars per token
        prompt_tokens = max(1, len(user_input) // 4)
        response_text = str(response)
        completion_tokens = max(1, len(response_text) // 4)

        return {
            "prompt": prompt_tokens,
            "completion": completion_tokens,
            "total": prompt_tokens + completion_tokens
        }

    def get_turn_history(self) -> List[TDDTurn]:
        """Get turn history.

        Returns:
            List of TDDTurn objects

        AC-REM-011-03: Access turn history
        """
        return self.turn_history

    def get_status(self) -> Dict[str, Any]:
        """Get wrapped orchestrator status.

        Returns:
            Status dictionary

        AC-REM-011-03: Report status
        """
        return {
            "orchestrator": "WrappedTDDOrchestrator",
            "version": "1.0",
            "turn_count": self.turn_count,
            "total_tokens_used": self.total_tokens_used,
            "turn_history_count": len(self.turn_history),
            "conversation_active": self.conversation_context is not None
        }


def get_wrapped_tdd_orchestrator(
    tdd_orchestrator: Optional[TDDOrchestrator] = None,
    conversation_protocol: Optional[ConversationProtocol] = None,
    event_registry: Optional[EventRegistry] = None
) -> WrappedTDDOrchestrator:
    """
    Get singleton instance of WrappedTDDOrchestrator.

    Args:
        tdd_orchestrator: Optional TDD orchestrator instance
        conversation_protocol: Optional conversation protocol
        event_registry: Optional event registry

    Returns:
        WrappedTDDOrchestrator instance

    AC-REM-011-03-10: Access singleton WrappedTDDOrchestrator
    """
    global _wrapped_tdd_orchestrator_instance

    if _wrapped_tdd_orchestrator_instance is None:
        _wrapped_tdd_orchestrator_instance = WrappedTDDOrchestrator(
            tdd_orchestrator=tdd_orchestrator,
            conversation_protocol=conversation_protocol,
            event_registry=event_registry
        )

    return _wrapped_tdd_orchestrator_instance


_wrapped_tdd_orchestrator_instance: Optional[WrappedTDDOrchestrator] = None


__all__ = [
    "WrappedTDDOrchestrator",
    "TDDTurn",
    "TDDConversationContext",
    "get_wrapped_tdd_orchestrator",
]
