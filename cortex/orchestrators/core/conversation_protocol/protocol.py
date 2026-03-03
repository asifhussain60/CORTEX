"""
ConversationProtocol — stateless single-turn executor.

Phase 103-h: extracted from conversation_protocol.py (1,539L) god-object.
Heavy governance and comprehension logic delegated to mixins.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.core.result import Err, Ok, Result
from cortex.core.tier_validator import TierAccessValidator
from cortex.infrastructure.database_transaction_manager import DatabaseTransactionManager
from cortex.intelligence.ast_intelligence import ASTIntelligenceEngine
from cortex.intelligence.call_graph import CallGraphBuilder
from cortex.intelligence.dependency_mapper import DependencyMapper
from cortex.intelligence.pattern_detector import PatternDetector
from cortex.orchestrators.core.continuation_decision import (
    ContinuationDecision,
    ContinuationReason,
)
from cortex.orchestrators.core.terminal_events import (
    ErrorOccurredEvent,
    EventRegistry,
    MaxTurnsReachedEvent,
    PhaseCompletedEvent,
    TokenLimitEvent,
    UserApprovalRejectedEvent,
)
from cortex.orchestrators.workflow.exec_gateway_impl import GovernanceViolationError

from cortex.orchestrators.core.conversation_protocol.models import (
    RequestComplexityClassifier,
    RoundContext,
)
from cortex.orchestrators.core.conversation_protocol.governance_mixin import GovernanceMixin
from cortex.orchestrators.core.conversation_protocol.comprehension_mixin import ComprehensionMixin

logger = logging.getLogger(__name__)


class ConversationProtocol(GovernanceMixin, ComprehensionMixin):
    """
    Stateless executor that runs one orchestrator turn and returns explicit decision.

    NOT a loop — each call to execute_turn() executes exactly one turn and returns
    a ContinuationDecision. The caller decides what to do next.
    """

    def __init__(
        self,
        orchestrator: Any,
        max_turns: int = 10,
        token_limit: int = 20000,
        event_registry: Optional[EventRegistry] = None,
        db_path: Optional[str] = None,
        adaptive_turn_limit: bool = True,
        memoization_enabled: bool = True,
    ) -> None:
        self.orchestrator = orchestrator
        self.max_turns = max_turns
        self.token_limit = token_limit
        self.adaptive_turn_limit = adaptive_turn_limit
        self.event_registry = event_registry or EventRegistry()

        # Execution state
        self.turn_number: int = 0
        self.total_tokens_used: int = 0
        self.decisions_history: List[ContinuationDecision] = []
        self.conversation_session: Optional[Any] = None

        # AC-FUTURE-006: memoization
        self.turn_result_cache: Dict[str, Any] = {}
        self.turn_cache_hits: int = 0
        self.turn_cache_misses: int = 0
        self.memoization_enabled: bool = memoization_enabled

        # Governance + audit
        self._governance_registry = None
        self._audit_logger = None
        self._tier_validator = TierAccessValidator(enforce_mode=True)

        # AC-FIX-001-01: DatabaseTransactionManager
        if db_path is None:
            db_path = str(
                Path(__file__).parents[4]
                / ".cortex-runtime"
                / "state"
                / "governance.db"
            )
        self.transaction_manager = DatabaseTransactionManager(db_path)

        # LENS engines (AC-REM-001-xx)
        self.ast_engine = ASTIntelligenceEngine(enable_cache=True)
        self.call_graph_builder = CallGraphBuilder()
        self.dependency_mapper = DependencyMapper()
        self.pattern_detector = PatternDetector()

    # =========================================================================
    # AC-FUTURE-004: Adaptive turn limit
    # =========================================================================

    def calculate_adaptive_turn_limit(self, user_request: str) -> int:
        """Return recommended max_turns based on request complexity."""
        if not self.adaptive_turn_limit:
            return self.max_turns
        _, recommended_turns = RequestComplexityClassifier.classify(user_request)
        if self._audit_logger:
            self._audit_logger.log_operation_complete(
                ac_id="AC-FUTURE-004",
                operation="ADAPTIVE_TURN_LIMIT_CALCULATED",
                success=True,
                details={"recommended_turns": recommended_turns, "user_request": user_request[:100]},
            )
        return recommended_turns

    # =========================================================================
    # AC-FUTURE-006: Memoization
    # =========================================================================

    def _compute_turn_hash(self, round_context: RoundContext) -> str:
        key_data = {
            "user_input": round_context.user_input,
            "orchestrator": round_context.orchestrator_name,
            "round": round_context.round_number,
            "turn": self.turn_number,
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True, default=str).encode()).hexdigest()

    def _get_cached_result(self, turn_hash: str) -> Optional[Dict[str, Any]]:
        if not self.memoization_enabled:
            return None
        if turn_hash in self.turn_result_cache:
            self.turn_cache_hits += 1
            return self.turn_result_cache[turn_hash]
        self.turn_cache_misses += 1
        return None

    def _cache_result(self, turn_hash: str, result: Dict[str, Any]) -> None:
        if not self.memoization_enabled or not result:
            return
        if len(self.turn_result_cache) >= 1000:
            for key in list(self.turn_result_cache.keys())[:100]:
                del self.turn_result_cache[key]
        self.turn_result_cache[turn_hash] = result

    def get_memoization_stats(self) -> Dict[str, Any]:
        total = self.turn_cache_hits + self.turn_cache_misses
        hit_rate = (self.turn_cache_hits / total * 100) if total > 0 else 0.0
        return {
            "cache_enabled": self.memoization_enabled,
            "cache_size": len(self.turn_result_cache),
            "hits": self.turn_cache_hits,
            "misses": self.turn_cache_misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "total_turns": total,
        }

    # =========================================================================
    # Core turn execution
    # =========================================================================

    def execute_turn(self, round_context: RoundContext) -> Result[Dict[str, Any]]:
        """
        Execute one turn and return explicit continuation decision.

        AC-FIX-001-01: Atomic transaction for turn execution + audit logging.
        """
        user_input = round_context.user_input
        previous_context = round_context.previous_context

        try:
            with self.transaction_manager.atomic_operation(
                "AC-FIX-001-01", f"execute_turn_{self.turn_number}"
            ):
                self.turn_number += 1

                # Step 1: Pre-turn governance
                gov_result = self._validate_governance_before_turn()
                if gov_result.is_err():
                    raise Exception(f"Governance validation failed: {gov_result.error}")

                # Step 2: Create round context
                round_context = self._create_round_context(user_input, previous_context)

                # Step 3: Log AC_START
                ac_start_entry_id = self._log_ac_start(round_context)

                # Step 3b: LENS comprehension
                comprehension_result = self._run_comprehension_phase(user_input, round_context)
                round_context.previous_context["comprehension_result"] = (
                    comprehension_result.unwrap() if comprehension_result.is_ok() else {}
                )

                # Step 3c: Pre-execution gates
                pregate_result = self._check_pre_execution_gates()
                if pregate_result.is_err():
                    error_msg = pregate_result.error
                    self._log_ac_execute_with_error(ac_start_entry_id, error_msg)
                    halt_decision = ContinuationDecision(
                        reason=ContinuationReason.GOVERNANCE_HALT,
                        can_continue=False,
                        turn_number=self.turn_number,
                        explanation=f"Pre-execution governance gate blocked: {error_msg}",
                        next_operation=None,
                        governance_violations=[error_msg],
                    )
                    self.decisions_history.append(halt_decision)
                    return Ok(halt_decision)

                # Step 4: Execute orchestrator
                try:
                    orchestrator_result = self.orchestrator.execute(
                        user_input, round_context.previous_context
                    )
                except Exception as exc:
                    self._log_ac_execute_with_error(ac_start_entry_id, str(exc))
                    raise Exception(f"Orchestrator execution failed: {exc}")

                # Step 5: Log AC_EXECUTE
                self._log_ac_execute(ac_start_entry_id, orchestrator_result)

                # Step 6: Evaluate continuation
                decision = self._evaluate_continuation(
                    user_input, orchestrator_result, previous_context, ac_start_entry_id
                )

                # Step 7: Log AC_COMPLETE
                ac_complete_entry_id = self._log_ac_complete(ac_start_entry_id, decision)

                # Step 8: Update decision with audit entry
                decision_with_audit = self._add_audit_entry_to_decision(
                    decision, ac_complete_entry_id
                )

                self.decisions_history.append(decision_with_audit)
                return Ok(decision_with_audit)

        except Exception as exc:
            error_decision = ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.ERROR_UNRECOVERABLE,
                next_operation="error_recovery",
                turn_number=self.turn_number,
                token_usage={"prompt": 0, "completion": 0, "total": 0},
                governance_violations=[],
            )
            self.decisions_history.append(error_decision)
            return Err(f"Turn execution failed (transaction rolled back): {exc}")

    # =========================================================================
    # Internal helpers
    # =========================================================================

    def _create_round_context(
        self, user_input: str, previous_context: Dict[str, Any]
    ) -> RoundContext:
        context = RoundContext(
            round_number=self.turn_number,
            user_input=user_input,
            previous_context=previous_context,
            orchestrator_name=self.orchestrator.__class__.__name__,
            timestamp=datetime.now(),
        )
        previous_context["lens_phases"] = {
            "language": "ACTIVE",
            "examination": "ACTIVE",
            "navigation": "ACTIVE",
            "synthesis": "ACTIVE",
        }
        previous_context["turn_number"] = self.turn_number
        return context

    def _log_ac_start(self, round_context: RoundContext) -> str:
        entry_id = f"ac-start-turn-{self.turn_number}"
        if self._audit_logger:
            self._audit_logger.log_entry(
                operation="AC_START",
                ac_id=f"OC-001-02-turn-{self.turn_number}",
                details={
                    "turn_number": self.turn_number,
                    "orchestrator": round_context.orchestrator_name,
                    "user_input_length": len(round_context.user_input),
                },
            )
        return entry_id

    def _log_ac_execute(
        self, ac_start_entry_id: str, orchestrator_result: Dict[str, Any]
    ) -> str:
        entry_id = f"ac-execute-turn-{self.turn_number}"
        if self._audit_logger:
            self._audit_logger.log_entry(
                operation="AC_EXECUTE",
                ac_id=f"OC-001-02-turn-{self.turn_number}",
                details={
                    "parent_entry": ac_start_entry_id,
                    "result_keys": list(orchestrator_result.keys()),
                },
                previous_entry_id=ac_start_entry_id,
            )
        return entry_id

    def _log_ac_execute_with_error(self, ac_start_entry_id: str, error_msg: str) -> str:
        entry_id = f"ac-execute-error-turn-{self.turn_number}"
        if self._audit_logger:
            self._audit_logger.log_entry(
                operation="AC_EXECUTE_ERROR",
                ac_id=f"OC-001-02-turn-{self.turn_number}",
                details={"parent_entry": ac_start_entry_id, "error": error_msg},
                previous_entry_id=ac_start_entry_id,
            )
        return entry_id

    def _evaluate_continuation(
        self,
        user_input: str,
        orchestrator_result: Dict[str, Any],
        previous_context: Dict[str, Any],
        ac_start_entry_id: str,
    ) -> ContinuationDecision:
        """Evaluate all break conditions and return explicit ContinuationDecision."""
        # Max turns
        if self.turn_number >= self.max_turns:
            self.event_registry.fire_event(
                MaxTurnsReachedEvent(
                    turn_number=self.turn_number,
                    max_turns=self.max_turns,
                    current_turn=self.turn_number,
                    reason="Max turns exceeded",
                )
            )
            return ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.MAX_ROUNDS_REACHED,
                next_operation="halt_max_rounds",
                turn_number=self.turn_number,
                token_usage=self._get_token_usage(),
            )

        # Token limit
        if self.total_tokens_used > int(self.token_limit * 0.9):
            self.event_registry.fire_event(
                TokenLimitEvent(
                    turn_number=self.turn_number,
                    tokens_used=self.total_tokens_used,
                    token_limit=self.token_limit,
                    percentage_used=int((self.total_tokens_used / self.token_limit) * 100),
                )
            )
            return ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.TOKEN_LIMIT,
                next_operation="resume_next_session",
                turn_number=self.turn_number,
                token_usage=self._get_token_usage(),
            )

        # Error
        if orchestrator_result.get("error"):
            self.event_registry.fire_event(
                ErrorOccurredEvent(
                    turn_number=self.turn_number,
                    error_message=orchestrator_result.get("error", "Unknown error"),
                    error_type="orchestrator_error",
                    recoverable=False,
                )
            )
            return ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.ERROR_UNRECOVERABLE,
                next_operation="error_recovery",
                turn_number=self.turn_number,
                token_usage=self._get_token_usage(),
            )

        # User rejection
        if orchestrator_result.get("requires_approval") and orchestrator_result.get("approval_rejected"):
            self.event_registry.fire_event(
                UserApprovalRejectedEvent(
                    turn_number=self.turn_number,
                    approval_request=orchestrator_result.get("approval_request", ""),
                    rejection_reason=orchestrator_result.get("rejection_reason", "User rejected"),
                )
            )
            return ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.USER_REJECTION,
                next_operation="wait_for_user_input",
                turn_number=self.turn_number,
                token_usage=self._get_token_usage(),
            )

        # Completion
        if orchestrator_result.get("status") == "completed":
            self.event_registry.fire_event(
                PhaseCompletedEvent(
                    turn_number=self.turn_number,
                    operation=orchestrator_result.get("operation", "phase"),
                    result=orchestrator_result.get("result", {}),
                )
            )
            return ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.COMPLETION,
                next_operation="done",
                turn_number=self.turn_number,
                token_usage=self._get_token_usage(),
            )

        # Implicit next operation
        next_op = orchestrator_result.get("next_operation")
        if next_op:
            return ContinuationDecision(
                should_continue=True,
                reason=ContinuationReason.IMPLICIT_NEXT_OPERATION,
                next_operation=next_op,
                next_parameters=orchestrator_result.get("next_parameters", {}),
                turn_number=self.turn_number,
                token_usage=self._get_token_usage(),
            )

        # Default: wait for user
        return ContinuationDecision(
            should_continue=False,
            reason=ContinuationReason.INTERACTION_REQUIRED,
            next_operation="wait_for_user_input",
            turn_number=self.turn_number,
            token_usage=self._get_token_usage(),
        )

    def _log_ac_complete(
        self, ac_start_entry_id: str, decision: ContinuationDecision
    ) -> str:
        entry_id = f"ac-complete-turn-{self.turn_number}"
        if self._audit_logger:
            self._audit_logger.log_entry(
                operation="AC_COMPLETE",
                ac_id=f"OC-001-02-turn-{self.turn_number}",
                details={
                    "parent_entry": ac_start_entry_id,
                    "decision": {
                        "should_continue": decision.should_continue,
                        "reason": decision.reason.value,
                        "next_operation": decision.next_operation,
                    },
                },
                previous_entry_id=ac_start_entry_id,
            )
        return entry_id

    def _add_audit_entry_to_decision(
        self, decision: ContinuationDecision, ac_complete_entry_id: str
    ) -> ContinuationDecision:
        return ContinuationDecision(
            should_continue=decision.should_continue,
            reason=decision.reason,
            next_operation=decision.next_operation,
            next_parameters=decision.next_parameters,
            turn_number=decision.turn_number,
            token_usage=decision.token_usage,
            audit_entry_id=ac_complete_entry_id,
            governance_violations=decision.governance_violations,
        )

    def _create_halt_decision(
        self, reason: ContinuationReason, error_msg: str = ""
    ) -> Result[ContinuationDecision]:
        decision = ContinuationDecision(
            should_continue=False,
            reason=reason,
            next_operation="halt",
            turn_number=self.turn_number,
            token_usage=self._get_token_usage(),
        )
        self.decisions_history.append(decision)
        return Ok(decision)

    def _get_token_usage(self) -> Dict[str, int]:
        return {
            "prompt": int(self.total_tokens_used * 0.6),
            "completion": int(self.total_tokens_used * 0.4),
            "total": self.total_tokens_used,
        }
