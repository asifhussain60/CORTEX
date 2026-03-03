"""
GovernanceMixin — pre-turn and pre-execution governance gates.

Phase 103-h: extracted from conversation_protocol.py (1,539L) god-object.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

from cortex.core.result import Err, Ok, Result
from cortex.orchestrators.workflow.exec_gateway_impl import GovernanceViolationError

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class GovernanceMixin:
    """Mixin providing pre-turn and pre-execution governance validation."""

    # Provided by ConversationProtocol.__init__:
    # self.orchestrator, self.turn_number, self._governance_registry,
    # self._audit_logger, self._tier_validator

    def _validate_governance_before_turn(self) -> Result[bool]:
        """
        Pre-turn governance validation gate (CORE-017).

        Returns:
            Result[bool] — Ok(True) if OK to proceed, Err(message) on violation.
        """
        try:
            from cortex.orchestrators.core.governance_registry import GovernanceRegistry

            if not self._governance_registry:
                self._governance_registry = GovernanceRegistry.instance()
                init_result = self._governance_registry.initialize()
                if init_result.is_err():
                    return Err(f"Failed to initialize governance registry: {init_result.error}")

            orchestrator_id = self._get_orchestrator_id()

            validation_result = self._governance_registry.should_proceed(
                turn_number=self.turn_number,
                orchestrator_id=orchestrator_id,
            )

            if validation_result.is_ok():
                # Tier access check
                if hasattr(self.orchestrator, "get_tier_access"):
                    try:
                        tier_access_result = self._tier_validator.validate_access_attempt(
                            orchestrator=self.orchestrator,
                            tier=1,
                            governance_rules=None,
                        )
                        if not tier_access_result:
                            violation_message = (
                                f"Tier access validation failed for orchestrator "
                                f"{orchestrator_id} on turn {self.turn_number}"
                            )
                            return Err(violation_message)
                    except (PermissionError, ValueError) as exc:
                        violation_message = f"Tier access violation: {exc}"
                        raise GovernanceViolationError(violation_message)

                if self._audit_logger:
                    self._audit_logger.log_operation_start(
                        ac_id="AC-REM-002-02",
                        operation="GOVERNANCE_VALIDATION_BEFORE_TURN",
                        context={
                            "turn_number": self.turn_number,
                            "orchestrator_id": orchestrator_id,
                            "status": "PASSED",
                            "tier_validation": "PASSED",
                        },
                    )
                return Ok(True)
            else:
                violation_message = validation_result.error
                if self._audit_logger:
                    self._audit_logger.log_operation_complete(
                        ac_id="AC-REM-002-02",
                        operation="GOVERNANCE_VIOLATION_DETECTED",
                        success=False,
                        details={
                            "turn_number": self.turn_number,
                            "orchestrator_id": orchestrator_id,
                            "violation": violation_message,
                        },
                    )
                raise GovernanceViolationError(violation_message)

        except GovernanceViolationError:
            raise
        except Exception as exc:
            return Err(f"Governance validation failed: {exc}")

    def _check_pre_execution_gates(self) -> Result[bool]:
        """
        Check pre-execution governance gates (AC-FIX-002-01).

        Returns:
            Ok(True) if all gates pass, Err(message) if any gate blocks.
        """
        try:
            from cortex.core.governance_pregate import get_governance_pregate

            pregate = get_governance_pregate()
            orchestrator_id = self._get_orchestrator_id()

            context = {
                "actor_id": orchestrator_id,
                "turn_number": self.turn_number,
                "timestamp": datetime.utcnow().isoformat(),
            }

            declared_tiers: Any = []
            if hasattr(self.orchestrator, "get_tier_access"):
                try:
                    declared_tiers = self.orchestrator.get_tier_access()
                except Exception:
                    declared_tiers = []

            gate_decision = pregate.evaluate_all_gates(
                operation_id=f"turn_{self.turn_number}",
                actor_id=orchestrator_id,
                target_resource="orchestrator_execution",
                estimated_token_cost=1000,
                tier_access=declared_tiers if declared_tiers else None,
                context=context,
            )

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
                    },
                )

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
                        },
                    )
                return Err(error_msg)

            return Ok(True)

        except Exception as exc:
            error_msg = f"Pre-execution gate check failed: {exc}"
            if self._audit_logger:
                self._audit_logger.log_operation_complete(
                    ac_id="AC-FIX-002-01",
                    operation="PREGATE_ERROR",
                    success=False,
                    details={"error": str(exc)},
                )
            return Err(error_msg)

    def _get_orchestrator_id(self) -> str:
        """Resolve orchestrator ID from multiple attribute sources."""
        if hasattr(self.orchestrator, "id"):
            return self.orchestrator.id
        if hasattr(self.orchestrator, "domain"):
            return self.orchestrator.domain
        if hasattr(self.orchestrator, "__class__"):
            return self.orchestrator.__class__.__name__
        return str(type(self.orchestrator))
