"""Stage 2.5 Gate - Pipeline gate for stage 2.5 processing.

Gate validator for stage 2.5 of the pipeline.

Author: CORTEX Framework
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, List
from enum import Enum


class GateDecision(Enum):
    """Gate decision outcomes."""
    ALLOW = "allow"
    REJECT = "reject"
    REVIEW = "review"
    ESCALATE = "escalate"


@dataclass
class ContinuationDecision:
    """Decision about whether to continue execution.
    
    Attributes:
        continue_execution: Whether to continue execution.
        reason: Reason for the decision.
        confirmation_context: Optional confirmation context with challenges.
    """
    continue_execution: bool
    reason: str
    confirmation_context: Optional["ConfirmationContext"] = None


@dataclass
class GateCheckResult:
    """Result of a gate check.

    Attributes:
        check_name: Name of the check.
        passed: Whether check passed.
        details: Details about the check.
        severity: Severity if failed.
    """

    check_name: str
    passed: bool
    details: str = ""
    severity: str = "medium"


@dataclass
class ConfirmationContext:
    """Context for confirmation decisions.

    Attributes:
        context_id: Unique context identifier.
        request_context: Request context data.
        verification_details: Verification details.
        confirmed: Whether confirmed.
        challenges: List of challenges associated with this context.
        user_intent: Optional user intent string.
        affected_files: Optional list of affected files.
        alternatives: Optional list of alternatives.
    """

    context_id: str
    request_context: Dict[str, Any]
    verification_details: Dict[str, Any] = None
    confirmed: bool = False
    challenges: List[Dict[str, Any]] = None
    user_intent: Optional[str] = None
    affected_files: Optional[List[str]] = None
    alternatives: Optional[List[Dict[str, Any]]] = None

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.verification_details is None:
            self.verification_details = {}
        if self.challenges is None:
            self.challenges = []
        if self.alternatives is None:
            self.alternatives = []
        if self.affected_files is None:
            self.affected_files = []


class Stage25Gate:
    """Gate for stage 2.5 processing."""

    def __init__(self) -> None:
        """Initialize stage 2.5 gate."""
        self.checks: List[GateCheckResult] = []
        self.decision = GateDecision.ALLOW
        self.engine = None  # Complexity assessment engine
        self.gate = None  # Approval gate logic

    def evaluate(
        self,
        operation_id: str,
        lens_confidence: float,
        signals: Any,
        challenges: Optional[List[Dict[str, Any]]] = None,
        user_intent: Optional[str] = None,
        affected_files: Optional[List[str]] = None,
        alternatives: Optional[List[Dict[str, Any]]] = None,
    ) -> ContinuationDecision:
        """Evaluate gate with challenge integration.

        Args:
            operation_id: Operation identifier.
            lens_confidence: Lens confidence score.
            signals: Complexity signals.
            challenges: Optional list of challenges.
            user_intent: Optional user intent description.
            affected_files: Optional list of affected files.
            alternatives: Optional list of alternatives.

        Returns:
            ContinuationDecision with attached challenges if applicable.
        """
        if challenges is None:
            challenges = []
        if alternatives is None:
            alternatives = []
        if affected_files is None:
            affected_files = []

        # Use engine and gate if available (for testing with mocks)
        if self.engine and self.gate:
            assessment = self.engine.assess_complexity(signals)
            approval_decision = self.gate.evaluate_approval(assessment, operation_id)
            
            # Create confirmation context if not auto-approved
            confirmation_context = None
            if not approval_decision.approved:
                confirmation_context = ConfirmationContext(
                    context_id=f"{operation_id}_confirmation",
                    request_context={"operation_id": operation_id},
                    challenges=challenges,
                    user_intent=user_intent,
                    affected_files=affected_files,
                    alternatives=alternatives
                )
            elif challenges:
                # Even for auto-approved, attach challenges if they exist
                confirmation_context = ConfirmationContext(
                    context_id=f"{operation_id}_confirmation",
                    request_context={"operation_id": operation_id},
                    challenges=challenges,
                    user_intent=user_intent,
                    affected_files=affected_files,
                    alternatives=alternatives,
                    confirmed=True
                )
            
            return ContinuationDecision(
                continue_execution=approval_decision.approved,
                reason=approval_decision.reason,
                confirmation_context=confirmation_context
            )
        
        # Default behavior without engine/gate
        return ContinuationDecision(
            continue_execution=True,
            reason="Auto-approved - default behavior"
        )

    def validate(self, context: Dict[str, Any]) -> GateDecision:
        """Validate against stage 2.5 requirements.

        Args:
            context: Context to validate.

        Returns:
            GateDecision.
        """
        self.checks = []

        # Check required fields
        required_fields = ["intent", "context", "execution_mode"]
        for field in required_fields:
            if field in context:
                self.checks.append(
                    GateCheckResult(
                        check_name=f"required_field_{field}",
                        passed=True,
                        details=f"Field '{field}' present",
                    )
                )
            else:
                self.checks.append(
                    GateCheckResult(
                        check_name=f"required_field_{field}",
                        passed=False,
                        details=f"Field '{field}' missing",
                        severity="high",
                    )
                )

        # Determine decision
        failed_critical = [c for c in self.checks if not c.passed and c.severity == "high"]
        if failed_critical:
            self.decision = GateDecision.ESCALATE
        elif any(not c.passed for c in self.checks):
            self.decision = GateDecision.REVIEW
        else:
            self.decision = GateDecision.ALLOW

        return self.decision

    def get_failed_checks(self) -> List[GateCheckResult]:
        """Get failed checks.

        Returns:
            List of failed GateCheckResult.
        """
        return [c for c in self.checks if not c.passed]

    def is_passed(self) -> bool:
        """Check if all validations passed.

        Returns:
            True if all checks passed.
        """
        return all(c.passed for c in self.checks)


# Alias for backward compatibility
Stage2_5Gate = Stage25Gate


class ConversationProtocolIntegration:
    """Integration layer for conversation protocol with stage 2.5 gate.

    Bridges conversation protocol and stage 2.5 gate processing.
    """

    def __init__(self) -> None:
        """Initialize conversation protocol integration."""
        self.gate = Stage25Gate()
        self.conversation_state: Dict[str, Any] = {}
        self.protocol_version = "1.0"

    def initialize_from_protocol(self, protocol_data: Dict[str, Any]) -> bool:
        """Initialize from conversation protocol data.

        Args:
            protocol_data: Protocol data dictionary.

        Returns:
            True if initialization successful, False otherwise.
        """
        try:
            self.conversation_state = protocol_data.copy()
            decision = self.gate.validate(protocol_data)
            return decision == GateDecision.ALLOW
        except Exception:
            return False

    def get_integration_context(self) -> Dict[str, Any]:
        """Get current integration context.

        Returns:
            Context dictionary.
        """
        return {
            "protocol_version": self.protocol_version,
            "gate_decision": self.gate.decision.value,
            "conversation_state": self.conversation_state.copy(),
            "checks": [
                {
                    "name": c.check_name,
                    "passed": c.passed,
                    "details": c.details,
                }
                for c in self.gate.checks
            ],
        }

    def apply_protocol_transformation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply conversation protocol transformations.

        Args:
            data: Data to transform.

        Returns:
            Transformed data.
        """
        transformed = data.copy()
        transformed["_protocol_version"] = self.protocol_version
        transformed["_gate_validated"] = self.gate.is_passed()
        return transformed


__all__ = [
    "Stage25Gate",
    "Stage2_5Gate",
    "ConversationProtocolIntegration",
    "GateDecision",
    "GateCheckResult",
    "ConfirmationContext",
    "ContinuationDecision",
]
