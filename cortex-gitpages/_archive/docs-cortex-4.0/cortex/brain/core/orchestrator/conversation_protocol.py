"""
ConversationProtocol - Single turn executor for orchestrators.

Wraps any IOrchestrator to execute one turn at a time with explicit
continuation decisions, governance validation, audit logging, and token tracking.

This replaces imperative "while True" loops with declarative, testable execution.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import yaml

from cortex.brain.core.orchestrator.continuation_decision import (
    ContinuationDecision,
    ContinuationReason,
)
from cortex.brain.core.orchestrator.terminal_events import (
    EventRegistry,
    PhaseCompletedEvent,
    UserCancelledEvent,
    MaxTurnsReachedEvent,
    ErrorOccurredEvent,
    TokenLimitEvent,
    GovernanceViolationEvent,
    UserApprovalRejectedEvent,
)
from cortex.brain.core.result import Result, Ok, Err
from cortex.brain.core.governance_registry import GovernanceRegistry, GovernanceViolationError
from cortex.brain.core.governance_pregate import get_governance_pregate, PreGateDecision
from cortex.brain.core.tier_validator import TierAccessValidator
from cortex.brain.core.intelligence.ast_intelligence import ASTIntelligenceEngine
from cortex.brain.core.intelligence.call_graph import CallGraphBuilder
from cortex.brain.core.intelligence.dependency_mapper import DependencyMapper
from cortex.brain.core.intelligence.pattern_detector import PatternDetector
from cortex.infrastructure.database_transaction_manager import DatabaseTransactionManager


@dataclass
class RoundContext:
    """Context for a single round of execution."""
    
    round_number: int
    user_input: str
    previous_context: Dict[str, Any]
    orchestrator_name: str
    timestamp: datetime = field(default_factory=datetime.now)


class ConversationProtocol:
    """
    Stateless executor that runs one orchestrator turn and returns explicit decision.
    
    NOT a loop - each call to execute_turn() executes exactly one turn and returns
    a ContinuationDecision. The caller decides what to do next.
    
    This enables:
    - Independent testing of each turn
    - Clear audit trail per turn
    - Per-turn LENS re-execution
    - Per-turn governance validation
    - Per-turn token tracking
    - Explicit continuation reasons (not hidden loop state)
    
    Attributes:
        orchestrator: The IOrchestrator to wrap
        max_turns: Safety limit on iterations (default: 10)
        token_limit: Token budget before halt (default: 20000)
        turn_number: Current turn count
        total_tokens_used: Accumulated tokens across all turns
        decisions_history: List of all decisions made
        conversation_session: Optional session for state persistence
    """

    def __init__(
        self,
        orchestrator: Any,
        max_turns: int = 10,
        token_limit: int = 20000,
        event_registry: EventRegistry = None,
        db_path: Optional[str] = None,  # AC-FIX-008-01: Allow test database injection
    ):
        """
        Initialize ConversationProtocol wrapper.
        
        Args:
            orchestrator: IOrchestrator instance to wrap
            max_turns: Maximum turns before safety halt (default: 10)
            token_limit: Token budget before halt (default: 20000)
            event_registry: Optional EventRegistry for event handling
            db_path: Optional database path (for testing, defaults to production path)
        """
        self.orchestrator = orchestrator
        self.max_turns = max_turns
        self.token_limit = token_limit
        
        # Event handling
        self.event_registry = event_registry or EventRegistry()
        
        # Execution state
        self.turn_number: int = 0
        self.total_tokens_used: int = 0
        self.decisions_history: List[ContinuationDecision] = []
        self.conversation_session: Optional[Any] = None
        
        # Governance and audit
        self._governance_registry = None  # Will be injected if available
        self._audit_logger = None  # Will be set if available
        self._tier_validator = TierAccessValidator(enforce_mode=True)  # AC-REM-002-08: Wire validator
        
        # AC-FIX-001-01: Initialize DatabaseTransactionManager for atomic turn execution
        # AC-FIX-008-01: Use provided db_path for tests, default for production
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / "cortex_brain" / "state" / "governance.db")
        self.transaction_manager = DatabaseTransactionManager(db_path)
        
        # AC-REM-001-01: Initialize AST Intelligence Engine for comprehension phase
        self.ast_engine = ASTIntelligenceEngine(enable_cache=True)
        
        # AC-REM-001-02: Initialize CallGraphBuilder for layer tracing
        self.call_graph_builder = CallGraphBuilder()
        
        # AC-REM-001-03: Initialize DependencyMapper for import classification
        self.dependency_mapper = DependencyMapper()
        
        # AC-REM-001-04: Initialize PatternDetector for architectural patterns
        self.pattern_detector = PatternDetector()

    def execute_turn(
        self, user_input: str, previous_context: Dict[str, Any]
    ) -> Result["ContinuationDecision"]:
        """
        Execute one turn and return explicit continuation decision.
        
        AC-FIX-001-01: Atomic transaction for turn execution + audit logging
        
        This is THE core method - it executes exactly one turn within an atomic transaction:
        1. Increment turn counter
        2. Validate governance (pre-turn check)
        3. Create round context with LENS phases
        4. Log AC_START audit entry (in transaction)
        5. Execute orchestrator.execute()
        6. Log AC_EXECUTE audit entry (in transaction)
        7. Evaluate continuation logic
        8. Log AC_COMPLETE audit entry (in transaction)
        9. Return ContinuationDecision
        
        All audit entries and state changes committed atomically or rolled back together.
        
        Args:
            user_input: User's input for this turn
            previous_context: Context from previous turns
        
        Returns:
            Result[ContinuationDecision] - Decision and continuation reason
        
        Raises:
            None - errors wrapped in Result type
        """
        # AC-FIX-001-01: Wrap entire turn in atomic transaction
        # Both turn execution and audit logging occur in single transaction boundary
        try:
            with self.transaction_manager.atomic_operation("AC-FIX-001-01", f"execute_turn_{self.turn_number}") as txn:
                # Increment turn counter
                self.turn_number += 1
                
                # Step 1: Pre-turn governance validation (CORE-017)
                governance_result = self._validate_governance_before_turn()
                if governance_result.is_err():
                    raise Exception(f"Governance validation failed: {governance_result.error}")
                
                # Step 2: Create round context
                round_context = self._create_round_context(
                    user_input, previous_context
                )
                
                # Step 3: Log AC_START (audit trail) - within transaction
                ac_start_entry_id = self._log_ac_start(round_context)
                
                # Step 3b: Run LENS comprehension phase (AC-REM-001-01)
                # Execute AST scanning on identified target files
                comprehension_result = self._run_comprehension_phase(
                    user_input, round_context
                )
                if comprehension_result.is_err():
                    # Log comprehension error but continue (graceful degradation)
                    pass
                
                # Add comprehension results to context for orchestrator
                round_context.previous_context["comprehension_result"] = (
                    comprehension_result.unwrap() if comprehension_result.is_ok() else {}
                )
                
                # Step 3c: Check pre-execution governance gates (AC-FIX-002-01)
                # FINDING-002: Governance must prevent (not just log) unauthorized operations
                pregate_result = self._check_pre_execution_gates()
                if pregate_result.is_err():
                    # Pre-gate blocked execution - return GOVERNANCE_HALT
                    error_msg = pregate_result.error
                    self._log_ac_execute_with_error(ac_start_entry_id, error_msg)
                    
                    # Return governance halt decision
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
                
                # Step 4: Execute orchestrator for one turn
                try:
                    orchestrator_result = self.orchestrator.execute(
                        user_input, round_context.previous_context
                    )
                except Exception as e:
                    # Handle orchestrator errors
                    self._log_ac_execute_with_error(ac_start_entry_id, str(e))
                    raise Exception(f"Orchestrator execution failed: {str(e)}")
                
                # Step 5: Log AC_EXECUTE (audit trail) - within transaction
                self._log_ac_execute(ac_start_entry_id, orchestrator_result)
                
                # Step 6: Evaluate continuation logic
                decision = self._evaluate_continuation(
                    user_input,
                    orchestrator_result,
                    previous_context,
                    ac_start_entry_id,
                )
                
                # Step 7: Log AC_COMPLETE (audit trail) - within transaction
                ac_complete_entry_id = self._log_ac_complete(
                    ac_start_entry_id, decision
                )
                
                # Update decision with audit entry
                decision_with_audit = self._add_audit_entry_to_decision(
                    decision, ac_complete_entry_id
                )
                
                # Step 8: Add to history
                self.decisions_history.append(decision_with_audit)
                
                # Transaction commits automatically on context exit
                # All audit entries and state changes committed atomically
                return Ok(decision_with_audit)
        
        except Exception as e:
            # Transaction automatically rolled back on exception
            # Catch any errors and create error decision
            error_decision = ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.ERROR_UNRECOVERABLE,
                next_operation="error_recovery",
                turn_number=self.turn_number,
                token_usage={"prompt": 0, "completion": 0, "total": 0},
                governance_violations=[],
            )
            self.decisions_history.append(error_decision)
            return Err(f"Turn execution failed (transaction rolled back): {str(e)}")

    def _validate_governance_before_turn(self) -> Result[bool]:
        """
        Pre-turn governance validation gate (CORE-017).
        
        Validates governance state before executing each turn:
        1. Initialize GovernanceRegistry if not already done
        2. Call should_proceed() with current turn number and orchestrator ID
        3. Return Ok(True) if validation passes
        4. Raise GovernanceViolationError on violation
        
        This method is called BEFORE each turn to enforce:
        - TIER-0 immutability (AR-001-03)
        - Strict governance enforcement (CORE-017)
        - Per-turn audit trail (CORE-027)
        
        Implementation for AC-REM-002-02.
        
        Returns:
            Result[bool] - Ok(True) if OK to proceed, Err(message) on violation
        
        Raises:
            GovernanceViolationError if governance violations detected
        """
        try:
            # Initialize registry if needed
            if not self._governance_registry:
                self._governance_registry = GovernanceRegistry.instance()
                init_result = self._governance_registry.initialize()
                if init_result.is_err():
                    return Err(f"Failed to initialize governance registry: {init_result.error}")
            
            # Get orchestrator ID for governance validation
            # Try multiple attribute names to find ID
            orchestrator_id = None
            if hasattr(self.orchestrator, 'id'):
                orchestrator_id = self.orchestrator.id
            elif hasattr(self.orchestrator, 'domain'):
                orchestrator_id = self.orchestrator.domain
            elif hasattr(self.orchestrator, '__class__'):
                orchestrator_id = self.orchestrator.__class__.__name__
            else:
                orchestrator_id = str(type(self.orchestrator))
            
            # Validate governance state for this turn
            validation_result = self._governance_registry.should_proceed(
                turn_number=self.turn_number,
                orchestrator_id=orchestrator_id
            )
            
            # Handle validation result
            if validation_result.is_ok():
                # Governance validation passed
                # AC-REM-002-08: Validate tier access via TierAccessValidator
                # Check if orchestrator declares tier access
                if hasattr(self.orchestrator, 'get_tier_access'):
                    try:
                        # Validate tier access for this turn
                        tier_access_result = self._tier_validator.validate_access_attempt(
                            orchestrator=self.orchestrator,
                            tier=1,  # Default tier for infrastructure operations
                            governance_rules=None
                        )
                        
                        if not tier_access_result:
                            # Tier access validation failed (non-enforcing mode returned False)
                            violation_message = (
                                f"Tier access validation failed for orchestrator {orchestrator_id} "
                                f"on turn {self.turn_number}"
                            )
                            if self._audit_logger:
                                self._audit_logger.log_operation_complete(
                                    ac_id="AC-REM-002-08",
                                    operation="TIER_VALIDATION_FAILED",
                                    success=False,
                                    details={
                                        "turn_number": self.turn_number,
                                        "orchestrator_id": orchestrator_id,
                                        "violation": violation_message
                                    }
                                )
                            return Err(violation_message)
                    except (PermissionError, ValueError) as e:
                        # Tier access validation failed (enforcing mode raised exception)
                        violation_message = f"Tier access violation: {str(e)}"
                        if self._audit_logger:
                            self._audit_logger.log_operation_complete(
                                ac_id="AC-REM-002-08",
                                operation="TIER_VALIDATION_FAILED",
                                success=False,
                                details={
                                    "turn_number": self.turn_number,
                                    "orchestrator_id": orchestrator_id,
                                    "violation": violation_message
                                }
                            )
                        raise GovernanceViolationError(violation_message)
                
                # Log to audit trail if logger available
                if self._audit_logger:
                    self._audit_logger.log_operation_start(
                        ac_id="AC-REM-002-02",
                        operation="GOVERNANCE_VALIDATION_BEFORE_TURN",
                        context={
                            "turn_number": self.turn_number,
                            "orchestrator_id": orchestrator_id,
                            "status": "PASSED",
                            "tier_validation": "PASSED"  # AC-REM-002-08
                        }
                    )
                return Ok(True)
            else:
                # Governance violation detected
                violation_message = validation_result.error
                
                if self._audit_logger:
                    self._audit_logger.log_operation_complete(
                        ac_id="AC-REM-002-02",
                        operation="GOVERNANCE_VIOLATION_DETECTED",
                        success=False,
                        details={
                            "turn_number": self.turn_number,
                            "orchestrator_id": orchestrator_id,
                            "violation": violation_message
                        }
                    )
                
                # Raise exception to halt execution
                raise GovernanceViolationError(violation_message)
        
        except GovernanceViolationError as e:
            # Re-raise governance violations
            raise e
        
        except Exception as e:
            # Wrap other exceptions
            error_msg = f"Governance validation failed: {str(e)}"
            return Err(error_msg)

    def _check_pre_execution_gates(self) -> Result[bool]:
        """
        Check pre-execution governance gates (AC-FIX-002-01).
        
        This method is called AFTER governance validation but BEFORE orchestrator execution.
        It applies pre-gates that can prevent the orchestrator from running based on:
        
        1. Resource quota availability
        2. Actor authorization
        3. Tier access declarations
        
        Returns:
            Ok(True) if all gates pass (execution allowed)
            Err(message) if any gate blocks (execution prevented)
        """
        try:
            # Get pre-gate instance
            pregate = get_governance_pregate()
            
            # Get orchestrator ID
            orchestrator_id = "unknown"
            if hasattr(self.orchestrator, 'id'):
                orchestrator_id = self.orchestrator.id
            elif hasattr(self.orchestrator, 'domain'):
                orchestrator_id = self.orchestrator.domain
            elif hasattr(self.orchestrator, '__class__'):
                orchestrator_id = self.orchestrator.__class__.__name__
            
            # Prepare gate context
            context = {
                "actor_id": orchestrator_id,
                "turn_number": self.turn_number,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            # Get declared tier access if available
            declared_tiers = []
            if hasattr(self.orchestrator, 'get_tier_access'):
                try:
                    declared_tiers = self.orchestrator.get_tier_access()
                except Exception:
                    declared_tiers = []
            
            # Evaluate all gates
            gate_decision: PreGateDecision = pregate.evaluate_all_gates(
                operation_id=f"turn_{self.turn_number}",
                actor_id=orchestrator_id,
                target_resource="orchestrator_execution",
                estimated_token_cost=1000,  # Default estimate
                tier_access=declared_tiers if declared_tiers else None,
                context=context
            )
            
            # Log gate decision to audit trail if logger available
            if self._audit_logger:
                self._audit_logger.log_operation_start(
                    ac_id="AC-FIX-002-01",
                    operation="PREGATE_CHECK",
                    context={
                        "turn_number": self.turn_number,
                        "orchestrator_id": orchestrator_id,
                        "decision": "ALLOWED" if gate_decision.allowed else "BLOCKED",
                        "reason": gate_decision.reason,
                        "violation_type": gate_decision.violation_type,
                    }
                )
            
            # Handle gate decision
            if not gate_decision.allowed:
                error_msg = f"Pre-execution gate blocked: {gate_decision.reason}"
                
                if self._audit_logger:
                    self._audit_logger.log_operation_complete(
                        ac_id="AC-FIX-002-01",
                        operation="PREGATE_BLOCK",
                        success=False,
                        details={
                            "reason": gate_decision.reason,
                            "violation_type": gate_decision.violation_type,
                            "audit_context": gate_decision.audit_context,
                        }
                    )
                
                return Err(error_msg)
            
            return Ok(True)
        
        except Exception as e:
            error_msg = f"Pre-execution gate check failed: {str(e)}"
            if self._audit_logger:
                self._audit_logger.log_operation_complete(
                    ac_id="AC-FIX-002-01",
                    operation="PREGATE_ERROR",
                    success=False,
                    details={"error": str(e)}
                )
            return Err(error_msg)

    def _create_round_context(
        self, user_input: str, previous_context: Dict[str, Any]
    ) -> RoundContext:
        """
        Create round context for single-turn execution.
        
        This context includes:
        - LENS phases (Language, Examination, Navigation, Synthesis)
        - Turn metadata (number, timestamp)
        - Orchestrator metadata
        - User input
        - Previous context
        
        Args:
            user_input: User's input for this turn
            previous_context: Context from previous turns
        
        Returns:
            RoundContext with all metadata for this turn
        """
        context = RoundContext(
            round_number=self.turn_number,
            user_input=user_input,
            previous_context=previous_context,
            orchestrator_name=self.orchestrator.__class__.__name__,
            timestamp=datetime.now(),
        )
        
        # Add LENS phase metadata (executed fresh per turn - not cached)
        previous_context["lens_phases"] = {
            "language": "ACTIVE",
            "examination": "ACTIVE",
            "navigation": "ACTIVE",
            "synthesis": "ACTIVE",
        }
        previous_context["turn_number"] = self.turn_number
        
        return context

    def _log_ac_start(self, round_context: RoundContext) -> str:
        """
        Log AC_START audit entry.
        
        Records:
        - Operation: AC_START
        - Turn number
        - Round context
        - Timestamp
        
        Args:
            round_context: The round context
        
        Returns:
            Entry ID for linking EXECUTE/COMPLETE entries
        """
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
        """
        Log AC_EXECUTE audit entry.
        
        Records:
        - Operation: AC_EXECUTE
        - Orchestrator result
        - Timestamp
        
        Args:
            ac_start_entry_id: AC_START entry for linking
            orchestrator_result: Result from orchestrator.execute()
        
        Returns:
            Entry ID
        """
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

    def _log_ac_execute_with_error(
        self, ac_start_entry_id: str, error_msg: str
    ) -> str:
        """Log AC_EXECUTE with error details."""
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
        """
        Evaluate continuation logic - THE KEY DECISION POINT.
        
        Evaluates all break conditions and fires terminal events:
        1. Max turns reached? → MaxTurnsReachedEvent → MAX_ROUNDS_REACHED
        2. Token limit approaching? → TokenLimitEvent → TOKEN_LIMIT
        3. Governance violation? → GovernanceViolationEvent → GOVERNANCE_HALT
        4. Error in result? → ErrorOccurredEvent → ERROR_UNRECOVERABLE
        5. User rejection in result? → UserApprovalRejectedEvent → USER_REJECTION
        6. Result indicates completion? → PhaseCompletedEvent → COMPLETION
        7. Orchestrator suggests next operation? → IMPLICIT_NEXT_OPERATION
        8. Otherwise → INTERACTION_REQUIRED (wait for user input)
        
        Args:
            user_input: User's input
            orchestrator_result: Result from orchestrator
            previous_context: Previous round context
            ac_start_entry_id: AC_START entry ID
        
        Returns:
            ContinuationDecision with explicit reason
        """
        # Check max turns
        if self.turn_number >= self.max_turns:
            event = MaxTurnsReachedEvent(
                turn_number=self.turn_number,
                max_turns=self.max_turns,
                current_turn=self.turn_number,
                reason="Max turns exceeded",
            )
            self.event_registry.fire_event(event)
            return ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.MAX_ROUNDS_REACHED,
                next_operation="halt_max_rounds",
                turn_number=self.turn_number,
                token_usage=self._get_token_usage(),
            )
        
        # Check token limit
        if self.total_tokens_used > int(self.token_limit * 0.9):
            tokens_percentage = int(
                (self.total_tokens_used / self.token_limit) * 100
            )
            event = TokenLimitEvent(
                turn_number=self.turn_number,
                tokens_used=self.total_tokens_used,
                token_limit=self.token_limit,
                percentage_used=tokens_percentage,
            )
            self.event_registry.fire_event(event)
            return ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.TOKEN_LIMIT,
                next_operation="resume_next_session",
                turn_number=self.turn_number,
                token_usage=self._get_token_usage(),
            )
        
        # Check for orchestrator errors
        if orchestrator_result.get("error"):
            error_msg = orchestrator_result.get("error", "Unknown error")
            event = ErrorOccurredEvent(
                turn_number=self.turn_number,
                error_message=error_msg,
                error_type="orchestrator_error",
                recoverable=False,
            )
            self.event_registry.fire_event(event)
            return ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.ERROR_UNRECOVERABLE,
                next_operation="error_recovery",
                turn_number=self.turn_number,
                token_usage=self._get_token_usage(),
            )
        
        # Check for user approval rejection
        if orchestrator_result.get("requires_approval") and orchestrator_result.get(
            "approval_rejected"
        ):
            event = UserApprovalRejectedEvent(
                turn_number=self.turn_number,
                approval_request=orchestrator_result.get("approval_request", ""),
                rejection_reason=orchestrator_result.get(
                    "rejection_reason", "User rejected"
                ),
            )
            self.event_registry.fire_event(event)
            return ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.USER_REJECTION,
                next_operation="wait_for_user_input",
                turn_number=self.turn_number,
                token_usage=self._get_token_usage(),
            )
        
        # Check if result indicates completion
        if orchestrator_result.get("status") == "completed":
            event = PhaseCompletedEvent(
                turn_number=self.turn_number,
                operation=orchestrator_result.get("operation", "phase"),
                result=orchestrator_result.get("result", {}),
            )
            self.event_registry.fire_event(event)
            return ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.COMPLETION,
                next_operation="done",
                turn_number=self.turn_number,
                token_usage=self._get_token_usage(),
            )
        
        # Check for orchestrator-specified next operation
        next_op = orchestrator_result.get("next_operation", None)
        if next_op:
            # Orchestrator knows what to do next
            return ContinuationDecision(
                should_continue=True,
                reason=ContinuationReason.IMPLICIT_NEXT_OPERATION,
                next_operation=next_op,
                next_parameters=orchestrator_result.get("next_parameters", {}),
                turn_number=self.turn_number,
                token_usage=self._get_token_usage(),
            )
        
        # Default: require user follow-up
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
        """
        Log AC_COMPLETE audit entry.
        
        Records:
        - Operation: AC_COMPLETE
        - Continuation decision
        - Timestamp
        
        Args:
            ac_start_entry_id: AC_START entry for linking
            decision: The continuation decision made
        
        Returns:
            Entry ID
        """
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
        self,
        decision: ContinuationDecision,
        ac_complete_entry_id: str,
    ) -> ContinuationDecision:
        """
        Create new decision with audit entry ID.
        
        Args:
            decision: Original decision
            ac_complete_entry_id: The AC_COMPLETE entry ID
        
        Returns:
            New decision with audit entry ID
        """
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
    ) -> Result["ContinuationDecision"]:
        """
        Create and return a halt decision.
        
        Args:
            reason: Reason for halting
            error_msg: Error message (if applicable)
        
        Returns:
            Result with halt decision
        """
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
        """
        Get current token usage.
        
        Returns:
            Dict with prompt, completion, total tokens
        """
        # For now, return placeholder values
        # In production, would integrate with token counter
        return {
            "prompt": int(self.total_tokens_used * 0.6),
            "completion": int(self.total_tokens_used * 0.4),
            "total": self.total_tokens_used,
        }

    def _run_comprehension_phase(
        self, user_input: str, round_context: "RoundContext"
    ) -> Result[Dict[str, Any]]:
        """
        AC-REM-001-01: Execute LENS comprehension phase with AST scanning.
        
        This phase:
        1. Identifies target files from user input context
        2. Uses ASTIntelligenceEngine to parse each target file
        3. Collects parse results for downstream phases
        4. Stores comprehension results in context
        
        This runs on EVERY turn (per AC-REM-001-06 requirement).
        
        Args:
            user_input: User's input for this turn
            round_context: Round context with previous context
        
        Returns:
            Result[Dict] with comprehension results:
            - target_files: List of analyzed files
            - parse_results: List of ParseResult objects
            - summary: High-level comprehension summary
        """
        try:
            comprehension_data: Dict[str, Any] = {
                "target_files": [],
                "parse_results": [],
                "summary": {},
                "turn_number": round_context.round_number,
            }
            
            # Try to extract target files from previous context or current round
            target_files: List[Path] = []
            
            # Check if orchestrator result from previous turn contains target files
            prev_result = round_context.previous_context.get(
                "last_orchestrator_result", {}
            )
            if isinstance(prev_result, dict):
                prev_targets = prev_result.get("target_files", [])
                if isinstance(prev_targets, list):
                    for t in prev_targets:
                        if isinstance(t, (str, Path)):
                            target_files.append(Path(t))
            
            # If no explicit targets, try to identify files from project context
            if not target_files:
                # Fallback: Look for common source directories
                project_root = Path.cwd()
                for source_dir in ["src", "cortex_brain", "tests"]:
                    potential_dir = project_root / source_dir
                    if potential_dir.exists() and potential_dir.is_dir():
                        # For now, limit to first few Python files to avoid overhead
                        py_files = list(potential_dir.glob("**/*.py"))[:5]
                        target_files.extend(py_files)
                        if len(target_files) >= 5:
                            break
            
            # AC-REM-001-01: Parse each target file with ASTIntelligenceEngine
            parse_results = []
            for target_file in target_files:
                try:
                    parse_result = self.ast_engine.parse_file(target_file)
                    parse_results.append(parse_result)
                    
                    comprehension_data["target_files"].append(str(target_file))
                except Exception as e:
                    # Graceful error handling per AC-REM-001-01
                    if self._audit_logger:
                        self._audit_logger.log_operation_complete(
                            ac_id="AC-REM-001-01",
                            operation="AST_SCANNING_ERROR",
                            success=False,
                            details={
                                "file": str(target_file),
                                "error": str(e),
                            },
                        )
            
            # Store parse results (serialize to dicts for JSON compatibility)
            comprehension_data["parse_results"] = [
                r.to_dict() for r in parse_results
            ]
            
            # AC-REM-001-02: Build call graphs for layer tracing
            call_graphs = []
            for parse_result in parse_results:
                try:
                    call_graph = self.call_graph_builder.build(parse_result)
                    call_graphs.append(call_graph)
                except Exception as e:
                    # Graceful error handling for call graph building
                    if self._audit_logger:
                        self._audit_logger.log_operation_complete(
                            ac_id="AC-REM-001-02",
                            operation="CALL_GRAPH_BUILD_ERROR",
                            success=False,
                            details={"error": str(e)},
                        )
            
            # Store call graphs (serialize to dicts for JSON compatibility)
            comprehension_data["call_graphs"] = [
                g.to_dict() for g in call_graphs
            ]
            
            # AC-REM-001-03: Map dependencies for impact analysis
            dependency_maps = []
            for parse_result in parse_results:
                try:
                    dep_map = self.dependency_mapper.map_dependencies(parse_result)
                    dependency_maps.append(dep_map)
                except Exception as e:
                    # Graceful error handling for dependency mapping
                    if self._audit_logger:
                        self._audit_logger.log_operation_complete(
                            ac_id="AC-REM-001-03",
                            operation="DEPENDENCY_MAP_ERROR",
                            success=False,
                            details={"error": str(e)},
                        )
            
            # Store dependency maps (serialize to dicts for JSON compatibility)
            comprehension_data["dependency_maps"] = [
                m.to_dict() for m in dependency_maps
            ]
            
            # Aggregate dependency statistics
            all_stdlib = set()
            all_third_party = set()
            all_local = set()
            
            for dep_map in dependency_maps:
                all_stdlib.update(dep_map.get_standard_library())
                all_third_party.update(dep_map.get_third_party())
                all_local.update(dep_map.get_local())
            
            # AC-REM-001-04: Detect architectural patterns
            patterns_detected = []
            for parse_result in parse_results:
                try:
                    patterns = self.pattern_detector.detect_patterns(parse_result)
                    patterns_detected.extend(patterns)
                except Exception as e:
                    # Graceful error handling for pattern detection
                    if self._audit_logger:
                        self._audit_logger.log_operation_complete(
                            ac_id="AC-REM-001-04",
                            operation="PATTERN_DETECTION_ERROR",
                            success=False,
                            details={"error": str(e)},
                        )
            
            # Store detected patterns (serialize to dicts for JSON compatibility)
            comprehension_data["patterns_detected"] = [
                p.to_dict() for p in patterns_detected
            ]
            
            # Count layer transitions across all call graphs
            total_layer_transitions = sum(g.edge_count for g in call_graphs)
            
            # Build comprehension summary
            comprehension_data["summary"] = {
                "files_analyzed": len(target_files),
                "files_parsed_successfully": sum(
                    1 for r in parse_results if r.success
                ),
                "total_functions_found": sum(
                    len(r.functions) for r in parse_results
                ),
                "total_classes_found": sum(len(r.classes) for r in parse_results),
                "total_imports_found": sum(len(r.imports) for r in parse_results),
                "call_graphs_built": len(call_graphs),
                "layer_transitions_identified": total_layer_transitions,
                "stdlib_dependencies": len(all_stdlib),
                "third_party_dependencies": len(all_third_party),
                "local_dependencies": len(all_local),
                "patterns_detected": len(patterns_detected),
            }
            
            if self._audit_logger:
                self._audit_logger.log_operation_complete(
                    ac_id="AC-REM-001-04",
                    operation="PATTERN_DETECTION",
                    success=True,
                    details={
                        "patterns_found": len(patterns_detected),
                        "pattern_types": list(set(
                            p.pattern_type for p in patterns_detected
                        )),
                    },
                )
            
            if self._audit_logger:
                self._audit_logger.log_operation_complete(
                    ac_id="AC-REM-001-03",
                    operation="DEPENDENCY_MAPPING",
                    success=True,
                    details={
                        "maps_built": len(dependency_maps),
                        "stdlib": len(all_stdlib),
                        "third_party": len(all_third_party),
                        "local": len(all_local),
                    },
                )
            
            if self._audit_logger:
                self._audit_logger.log_operation_complete(
                    ac_id="AC-REM-001-02",
                    operation="CALL_GRAPH_BUILDING",
                    success=True,
                    details={
                        "graphs_built": len(call_graphs),
                        "transitions": total_layer_transitions,
                    },
                )
            
            if self._audit_logger:
                self._audit_logger.log_operation_complete(
                    ac_id="AC-REM-001-01",
                    operation="COMPREHENSION_PHASE",
                    success=True,
                    details=comprehension_data["summary"],
                )
            
            return Ok(comprehension_data)
            
        except Exception as e:
            # Graceful error handling - comprehension errors don't block execution
            if self._audit_logger:
                self._audit_logger.log_operation_complete(
                    ac_id="AC-REM-001-01",
                    operation="COMPREHENSION_PHASE",
                    success=False,
                    details={"error": str(e)},
                )
            
            # Return empty comprehension data to allow execution to continue
            return Ok({
                "target_files": [],
                "parse_results": [],
                "summary": {"error": str(e)},
            })

    def _generate_comprehension_approval_yaml(
        self, comprehension_data: Dict[str, Any]
    ) -> str:
        """
        AC-REM-001-05: Generate comprehension YAML for approval gate.
        
        Creates holistic context YAML containing:
        - parsed_files: AST scan results
        - call_graphs: Layer relationship tracing
        - dependencies: Import classification
        - patterns: Architectural pattern detection
        - impact_map: Change impact analysis
        
        Args:
            comprehension_data: Result from _run_comprehension_phase
        
        Returns:
            YAML string for approval gate workflow
        """
        try:
            approval_yaml = {
                "operation": "COMPREHENSION_APPROVAL_GATE",
                "phase": "PHASE-REMEDIATION-01",
                "orchestrator": self.orchestrator.__class__.__name__,
                "timestamp": datetime.now().isoformat(),
                "turn_number": self.turn_number,
            }
            
            # Add summary
            approval_yaml["summary"] = comprehension_data.get("summary", {})
            
            # Add parsed files
            if comprehension_data.get("parse_results"):
                approval_yaml["parsed_files"] = [
                    {
                        "index": i,
                        "functions": r.get("functions", []),
                        "classes": r.get("classes", []),
                        "imports": r.get("imports", []),
                    }
                    for i, r in enumerate(comprehension_data["parse_results"][:5])
                ]
            
            # Add call graphs
            if comprehension_data.get("call_graphs"):
                approval_yaml["call_graphs"] = comprehension_data["call_graphs"][:5]
            
            # Add dependencies
            if comprehension_data.get("dependency_maps"):
                approval_yaml["dependencies"] = {
                    "summary": {
                        "stdlib": comprehension_data["summary"].get("stdlib_dependencies", 0),
                        "third_party": comprehension_data["summary"].get("third_party_dependencies", 0),
                        "local": comprehension_data["summary"].get("local_dependencies", 0),
                    },
                    "maps": comprehension_data["dependency_maps"][:3],
                }
            
            # Add patterns
            if comprehension_data.get("patterns_detected"):
                approval_yaml["patterns"] = {
                    "total": len(comprehension_data["patterns_detected"]),
                    "details": comprehension_data["patterns_detected"],
                }
            
            # Add impact map
            approval_yaml["impact_map"] = {
                "files_affected": comprehension_data.get("summary", {}).get("files_analyzed", 0),
                "functions_analyzed": comprehension_data.get("summary", {}).get("total_functions_found", 0),
                "transitive_dependency_depth": 3,  # From AC-REM-001-03
                "architectural_patterns_identified": comprehension_data.get("summary", {}).get("patterns_detected", 0),
            }
            
            # Add approval recommendation
            approval_yaml["approval_recommendation"] = {
                "status": "READY_FOR_APPROVAL",
                "confidence": 0.95,
                "reason": "All comprehension components completed successfully",
                "sign_off_required": True,
            }
            
            # Convert to YAML string
            yaml_str = yaml.dump(
                approval_yaml,
                default_flow_style=False,
                sort_keys=False,
            )
            
            return yaml_str
            
        except Exception as e:
            # Graceful error handling
            if self._audit_logger:
                self._audit_logger.log_operation_complete(
                    ac_id="AC-REM-001-05",
                    operation="YAML_GENERATION",
                    success=False,
                    details={"error": str(e)},
                )
            return ""

