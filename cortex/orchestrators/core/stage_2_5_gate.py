"""Stage 2.5 Gate - Pipeline gate for stage 2.5 processing.

Gate validator for stage 2.5 of the pipeline.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, List
from enum import Enum
from cortex.core.orchestrator.continuation_decision import ContinuationDecision


class GateDecision(Enum):
    """Gate decision outcomes."""

    ALLOW = "allow"
    REJECT = "reject"
    REVIEW = "review"
    ESCALATE = "escalate"


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
    """

    context_id: str
    request_context: Dict[str, Any]
    verification_details: Dict[str, Any] = None
    confirmed: bool = False

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.verification_details is None:
            self.verification_details = {}


class Stage25Gate:
    """Gate for stage 2.5 processing."""

    def __init__(self) -> None:
        """Initialize stage 2.5 gate."""
        self.checks: List[GateCheckResult] = []
        self.decision = GateDecision.ALLOW

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
