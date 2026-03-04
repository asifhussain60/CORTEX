"""
exec-gateway-impl: MasterGateway Implementation

Provides MasterGateway as the single entry point for all CORTEX operation
execution, enforcing specifications-driven routing per CORE-040.

CORE Rules Applied:
    - CORE-008: TDD (tests before implementation)
    - CORE-011: Type hints mandatory
    - CORE-012: Google-style docstrings
    - CORE-027: Audit trail logging
    - CORE-040: Execution Specification Mandate
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class GatewayError(Exception):  # CORE-035-scoped — domain-specific variant
    """Base exception for MasterGateway errors."""
    pass


class SpecValidationError(GatewayError):
    """Raised when operation spec is invalid."""
    pass


class GovernanceViolationError(GatewayError):
    """Raised when governance preconditions fail."""
    pass


@dataclass
class GatewayResult:
    """Result of gateway operation execution."""
    success: bool
    operation: str
    handler: Optional[str] = None
    execution_time_ms: int = 0
    violations: List[Dict[str, Any]] = field(default_factory=list)
    output: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    audit_entry_id: Optional[str] = None


class MasterGateway:
    """
    Single entry point for all CORTEX operation execution.

    Enforces:
        1. All operations route through MasterGateway.execute()
        2. Specifications loaded and validated before execution
        3. Governance validation before delegation
        4. Structured decision making (JSON only, never markdown)
        5. Centralized audit trail

    CORE-040 Mandate: No direct orchestrator instantiation.
    Always use: MasterGateway.execute(operation_spec)
    """

    def __init__(
        self,
        spec_registry: Optional[Any] = None,
        validator: Optional[Any] = None,
        enforcer: Optional[Any] = None,
        master_orchestrator: Optional[Any] = None,
    ) -> None:
        """
        Initialize MasterGateway.

        Args:
            spec_registry: SpecRegistry instance (lazy-loaded if None)
            validator: GatewayValidator instance (created if None)
            enforcer: GatewayEnforcer instance (optional)
            master_orchestrator: MasterOrchestrator instance for delegation.
                When provided, execute() delegates via
                master_orchestrator.execute_operation(). When None, a lazy
                import of MasterOrchestrator.instance() is attempted at
                execution time.
        """
        self.spec_registry = spec_registry
        self.validator = validator
        self.enforcer = enforcer
        self._master_orchestrator = master_orchestrator
        logger.info("MasterGateway initialized")

    def _get_master_orchestrator(self) -> Optional[Any]:
        """Resolve MasterOrchestrator, injected or lazily imported.

        Returns:
            MasterOrchestrator instance or None if unavailable.
        """
        if self._master_orchestrator is not None:
            return self._master_orchestrator
        try:
            from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
            return MasterOrchestrator.instance()
        except Exception as exc:  # pragma: no cover
            logger.warning("MasterOrchestrator unavailable for gateway delegation: %s", exc)
            return None

    def execute(
        self,
        operation_spec: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> GatewayResult:
        """
        Execute operation via specifications.

        This is the ONLY entry point for operation execution in CORTEX.

        Args:
            operation_spec: Operation specification (Dict/JSON format)
            context: Optional additional context

        Returns:
            GatewayResult with execution outcome (JSON format)

        Raises:
            SpecValidationError: If spec format invalid
            GovernanceViolationError: If governance check fails

        Example:
            >>> gateway = MasterGateway()
            >>> result = gateway.execute({
            ...     "operation": "implement_feature",
            ...     "intent": "IMPLEMENT",
            ...     "context": {"feature_name": "audit_logging"}
            ... })
            >>> assert result.success
        """
        start_time = datetime.now()
        operation_name = operation_spec.get("operation", "unknown")

        try:
            # Spec validation (optional enforcer)
            if self.validator:
                self._validate_spec(operation_spec)

            # Governance check (optional enforcer)
            if self.enforcer:
                self._check_governance(operation_spec)

            # Delegate to MasterOrchestrator
            orchestrator = self._get_master_orchestrator()
            elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            if orchestrator is None:
                logger.error(
                    "MasterGateway: no MasterOrchestrator available for operation '%s'",
                    operation_name,
                )
                return GatewayResult(
                    success=False,
                    operation=operation_name,
                    execution_time_ms=elapsed_ms,
                    error_code="OrchestratorUnavailable",
                    error_message=(
                        "MasterOrchestrator is not available. "
                        "Ensure MasterOrchestrator.instance() is initialised before "
                        "calling MasterGateway.execute()."
                    ),
                )

            parameters: Dict[str, Any] = dict(operation_spec)
            parameters.setdefault("intent", operation_spec.get("intent", "IMPLEMENT"))
            if context:
                parameters.update(context)

            logger.debug("Gateway delegating '%s' to MasterOrchestrator", operation_name)
            mo_result = orchestrator.execute_operation(
                operation_name=operation_name,
                parameters=parameters,
            )

            elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            if mo_result.is_ok():
                output = mo_result.unwrap()
                handler = (
                    output.get("handler", orchestrator.__class__.__name__)
                    if isinstance(output, dict)
                    else orchestrator.__class__.__name__
                )
                return GatewayResult(
                    success=True,
                    operation=operation_name,
                    handler=handler,
                    execution_time_ms=elapsed_ms,
                    violations=[],
                    output=output if isinstance(output, dict) else {"result": output},
                )
            else:
                return GatewayResult(
                    success=False,
                    operation=operation_name,
                    handler=orchestrator.__class__.__name__,
                    execution_time_ms=elapsed_ms,
                    error_code="OrchestratorError",
                    error_message=str(getattr(mo_result, "error", "unknown error")),
                )

        except (SpecValidationError, GovernanceViolationError) as e:
            elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.warning(f"Gateway execution failed: {e}")

            return GatewayResult(
                success=False,
                operation=operation_name,
                execution_time_ms=elapsed_ms,
                error_code=e.__class__.__name__,
                error_message=str(e)
            )

    def _validate_spec(self, spec: Dict[str, Any]) -> None:
        """
        Validate operation specification format.

        Args:
            spec: Operation specification to validate

        Raises:
            SpecValidationError: If spec invalid
        """
        if not isinstance(spec, dict):  # noqa: E501
            raise SpecValidationError("Operation spec must be a dictionary")

        if "operation" not in spec:
            raise SpecValidationError("Operation spec missing 'operation' field")

        logger.debug(f"Spec validation passed: {spec.get('operation')}")

    def _check_governance(self, spec: Dict[str, Any]) -> None:
        """
        Check governance preconditions before execution.

        Args:
            spec: Operation specification

        Raises:
            GovernanceViolationError: If governance check fails
        """
        if callable(self.enforcer):
            self.enforcer(spec)
        elif hasattr(self.enforcer, "check"):
            self.enforcer.check(spec)
        logger.debug("Governance check passed")

    def execute_with_intent(
        self,
        intent: str,
        context: Dict[str, Any]
    ) -> GatewayResult:
        """
        Execute with explicit intent type.

        Convenience method for callers that know intent upfront.

        Args:
            intent: Intent type (e.g., "IMPLEMENT", "FIX", "REFACTOR")
            context: Operation context

        Returns:
            GatewayResult with execution outcome

        Example:
            >>> gateway = MasterGateway()
            >>> result = gateway.execute_with_intent(
            ...     intent="IMPLEMENT",
            ...     context={"feature": "audit_logging"}
            ... )
        """
        spec = {
            "intent": intent,
            "context": context,
            "operation": f"execute_{intent.lower()}"
        }
        return self.execute(spec)


# Singleton instance (Phase 1: optional)
_gateway_instance: Optional[MasterGateway] = None


def get_gateway() -> MasterGateway:
    """
    Get or create singleton MasterGateway instance.

    Returns:
        MasterGateway singleton instance

    Note:
        Phase 1: Optional usage. Phase 3: Mandatory for all operations.
    """
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = MasterGateway()
    return _gateway_instance


__all__ = [
    "MasterGateway",
    "GatewayResult",
    "GatewayError",
    "SpecValidationError",
    "GovernanceViolationError",
    "get_gateway",
]
