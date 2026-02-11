"""
Routing Enforcement Engine - Tier 0 Blocking for Intent Router

AC-PHASE-8.2-01 / Task ROUTE-005
Enforces routing rules with Tier 0 blocking for violations.

Validation Rules:
  - ROUTING-001: Keywords must map to registered orchestrators
  - ROUTING-002: Confidence must exceed threshold (default: 0.6)
  - ROUTING-003: Fallback orchestrators required for ambiguous requests
  - ROUTING-004: All routing decisions must be auditable

CORE Governance:
  - CORE-008: TDD (tests created first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging

Author: Asif Hussain
Date: 2026-01-30
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from cortex.core.result import Err, Ok, Result
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.orchestrators.registry.orchestrator_lookup import OrchestratorLookup


class RoutingViolation(Enum):
    """Routing rule violation types."""
    ORCHESTRATOR_NOT_FOUND = "ROUTING-001"
    CONFIDENCE_TOO_LOW = "ROUTING-002"
    FALLBACK_MISSING = "ROUTING-003"
    NOT_AUDITABLE = "ROUTING-004"


@dataclass
class RoutingEnforcementResult:
    """Result of routing enforcement validation.

    Attributes:
        passed: Whether validation passed
        violations: List of violations detected
        warnings: List of non-blocking warnings
        details: Additional validation details
    """
    passed: bool
    violations: List[RoutingViolation]
    warnings: List[str]
    details: Dict[str, Any]


class RoutingEnforcementEngine:
    """
    Enforces routing rules with Tier 0 blocking.

    Validates routing decisions against governance rules and blocks
    operations that violate Tier 0 constraints.

    Thread-safe singleton pattern.

    Example:
        engine = RoutingEnforcementEngine.instance()
        result = engine.validate_routing_decision(decision)
        if not result.passed:
            raise RuntimeError(f"Routing blocked: {result.violations}")

    CORE Governance:
      - CORE-008: TDD (tests first)
      - CORE-011: Type hints on all methods
      - CORE-012: Docstrings (Google style)
      - CORE-027: Audit trail for all enforcement actions
    """

    _instance: Optional['RoutingEnforcementEngine'] = None

    # Default configuration
    DEFAULT_CONFIDENCE_THRESHOLD = 0.6
    DEFAULT_DISAMBIGUATION_THRESHOLD = 0.7
    DEFAULT_BLOCKING_ENABLED = True

    def __init__(
        self,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        disambiguation_threshold: float = DEFAULT_DISAMBIGUATION_THRESHOLD,
        blocking_enabled: bool = DEFAULT_BLOCKING_ENABLED
    ) -> None:
        """
        Initialize RoutingEnforcementEngine.

        Args:
            confidence_threshold: Minimum confidence for routing (default: 0.6)
            disambiguation_threshold: Threshold for disambiguation (default: 0.7)
            blocking_enabled: Whether to block violations (default: True)

        Raises:
            RuntimeError: If audit logger cannot be initialized
        """
        self.logger: EnhancedAuditLogger = EnhancedAuditLogger.instance()
        self.orchestrator_lookup: OrchestratorLookup = OrchestratorLookup.instance()

        self.confidence_threshold = confidence_threshold
        self.disambiguation_threshold = disambiguation_threshold
        self.blocking_enabled = blocking_enabled

        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.2-01",
            operation="ROUTING_ENFORCEMENT_INIT",
            success=True,
            details={
                "confidence_threshold": confidence_threshold,
                "disambiguation_threshold": disambiguation_threshold,
                "blocking_enabled": blocking_enabled
            }
        )

    @classmethod
    def instance(cls) -> 'RoutingEnforcementEngine':
        """
        Get singleton instance of RoutingEnforcementEngine.

        Returns:
            RoutingEnforcementEngine: Singleton instance
        """
        if cls._instance is None:
            cls._instance = RoutingEnforcementEngine()
        return cls._instance

    def validate_routing_decision(
        self,
        decision: Any  # RoutingDecision type (avoid circular import)
    ) -> RoutingEnforcementResult:
        """
        Validate a routing decision against all rules.

        Args:
            decision: RoutingDecision with orchestrator and confidence

        Returns:
            RoutingEnforcementResult: Validation result with violations

        Example:
            engine = RoutingEnforcementEngine.instance()
            result = engine.validate_routing_decision(decision)
            if not result.passed:
                print(f"Violations: {result.violations}")
        """
        violations: List[RoutingViolation] = []
        warnings: List[str] = []
        details: Dict[str, Any] = {}

        # ROUTING-001: Orchestrator must exist in registry
        orchestrator_check = self.check_orchestrator_exists(
            decision.target_handler
        )
        if orchestrator_check.is_err():
            violations.append(RoutingViolation.ORCHESTRATOR_NOT_FOUND)
            details["orchestrator_error"] = orchestrator_check.error  # Use .error property

        # ROUTING-002: Confidence must exceed threshold
        confidence_check = self.check_confidence_threshold(
            decision.confidence_score
        )
        if confidence_check.is_err():
            violations.append(RoutingViolation.CONFIDENCE_TOO_LOW)
            details["confidence_error"] = confidence_check.error  # Use .error property

        # ROUTING-003: Fallback orchestrators for low confidence
        if decision.confidence_score < self.disambiguation_threshold:
            fallback_check = self.check_fallback_orchestrators(decision)
            if fallback_check.is_err():
                warnings.append(fallback_check.error)  # Use .error property

        # ROUTING-004: Audit trail required
        if not hasattr(decision, 'reasoning') or not decision.reasoning:
            violations.append(RoutingViolation.NOT_AUDITABLE)
            details["audit_error"] = "Routing decision missing reasoning"

        # Determine if passed
        passed = len(violations) == 0

        # Log enforcement result
        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.2-01",
            operation="ROUTING_ENFORCEMENT_CHECK",
            success=passed,
            details={
                "violations": [v.value for v in violations],
                "warnings": warnings,
                "confidence": decision.confidence_score,
                "target_handler": decision.target_handler
            }
        )

        return RoutingEnforcementResult(
            passed=passed,
            violations=violations,
            warnings=warnings,
            details=details
        )

    def check_orchestrator_exists(self, orchestrator_name: str) -> Result[bool]:
        """
        Check if orchestrator exists in registry (ROUTING-001).

        Args:
            orchestrator_name: Orchestrator class name

        Returns:
            Result[bool]: Ok(True) if exists, Err(message) otherwise

        Example:
            engine = RoutingEnforcementEngine.instance()
            result = engine.check_orchestrator_exists("OnboardingOrchestrator")
            if result.is_err():
                print(f"Error: {result.unwrap_err()}")
        """
        if self.orchestrator_lookup.validate_orchestrator_exists(orchestrator_name):
            return Ok(True)

        return Err(
            f"ROUTING-001 VIOLATION: Orchestrator '{orchestrator_name}' "
            f"not found in registry. Available orchestrators can be listed "
            f"via OrchestratorLookup.instance().list_by_domain()."
        )

    def check_confidence_threshold(self, confidence: float) -> Result[bool]:
        """
        Check if confidence exceeds threshold (ROUTING-002).

        Args:
            confidence: Routing confidence score (0.0-1.0)

        Returns:
            Result[bool]: Ok(True) if passes, Err(message) otherwise

        Example:
            engine = RoutingEnforcementEngine.instance()
            result = engine.check_confidence_threshold(0.75)
            assert result.is_ok()
        """
        if confidence >= self.confidence_threshold:
            return Ok(True)

        return Err(
            f"ROUTING-002 VIOLATION: Confidence {confidence:.2f} below "
            f"threshold {self.confidence_threshold:.2f}. Routing decision "
            f"rejected. Consider adding more keywords to routing config or "
            f"implementing disambiguation UI."
        )

    def check_fallback_orchestrators(self, decision: Any) -> Result[bool]:
        """
        Check if fallback orchestrators exist for ambiguous requests (ROUTING-003).

        Args:
            decision: RoutingDecision with fallback orchestrators

        Returns:
            Result[bool]: Ok(True) if exists, Err(message) as warning

        Example:
            engine = RoutingEnforcementEngine.instance()
            result = engine.check_fallback_orchestrators(decision)
        """
        if not hasattr(decision, 'fallback_orchestrators'):
            return Err(
                "ROUTING-003 WARNING: No fallback orchestrators defined. "
                "Consider adding fallback_orchestrators to routing config "
                "for better handling of ambiguous requests."
            )

        fallbacks = getattr(decision, 'fallback_orchestrators', [])
        if not fallbacks or len(fallbacks) == 0:
            return Err(
                "ROUTING-003 WARNING: Fallback orchestrators list is empty. "
                "Low confidence routing should have 1-3 fallback options."
            )

        return Ok(True)

    def enforce_blocking_rules(self, decision: Any) -> Result[bool]:
        """
        Enforce blocking rules and raise exception if violations found.

        Args:
            decision: RoutingDecision to validate

        Returns:
            Result[bool]: Ok(True) if passed, Err(message) if blocked

        Raises:
            RuntimeError: If blocking enabled and violations found

        Example:
            engine = RoutingEnforcementEngine.instance()
            result = engine.enforce_blocking_rules(decision)
            if result.is_err():
                raise RuntimeError(result.unwrap_err())
        """
        if not self.blocking_enabled:
            return Ok(True)

        validation_result = self.validate_routing_decision(decision)

        if not validation_result.passed:
            error_message = (
                f"Routing BLOCKED by Tier 0 enforcement. "
                f"Violations: {[v.value for v in validation_result.violations]}. "
                f"Details: {validation_result.details}"
            )

            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.2-01",
                operation="ROUTING_BLOCKED",
                success=False,
                details={
                    "violations": [v.value for v in validation_result.violations],
                    "target_handler": decision.target_handler,
                    "confidence": decision.confidence_score
                }
            )

            return Err(error_message)

        return Ok(True)

    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current enforcement configuration.

        Returns:
            Dict with current thresholds and settings

        Example:
            engine = RoutingEnforcementEngine.instance()
            config = engine.get_configuration()
            print(f"Confidence threshold: {config['confidence_threshold']}")
        """
        return {
            "confidence_threshold": self.confidence_threshold,
            "disambiguation_threshold": self.disambiguation_threshold,
            "blocking_enabled": self.blocking_enabled,
            "rules": [
                "ROUTING-001: Orchestrators must exist in registry",
                "ROUTING-002: Confidence must exceed threshold",
                "ROUTING-003: Fallback orchestrators recommended",
                "ROUTING-004: Routing decisions must be auditable"
            ]
        }


# Module-level exports
__all__ = [
    "RoutingEnforcementEngine",
    "RoutingEnforcementResult",
    "RoutingViolation",
]
