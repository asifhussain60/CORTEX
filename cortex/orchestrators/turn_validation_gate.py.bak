"""Per-Turn Governance Validation Gate.

AC-ID: REMEDIATION-INTENT-004
Enforces per-turn governance validation at TIER 0-3 levels.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ValidationStatus(Enum):
    """Validation result status."""

    PASSED = "PASSED"
    BLOCKED = "BLOCKED"
    ESCALATION_REQUIRED = "ESCALATION_REQUIRED"
    WARNING = "WARNING"


@dataclass
class ValidationResult:
    """Result of turn validation."""

    status: ValidationStatus
    turn_number: int
    message: str = ""
    blocking_violations: List[str] = field(default_factory=list)
    escalation_required_tiers: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation of result.
        """
        return {
            "status": self.status.value,
            "turn_number": self.turn_number,
            "message": self.message,
            "blocking_violations": self.blocking_violations,
            "escalation_required_tiers": self.escalation_required_tiers,
            "timestamp": self.timestamp,
        }


class TurnValidationGate:
    """Per-turn governance validation enforcer."""

    # TIER 0: Immutable, always blocking
    TIER_0_BLOCKING_VIOLATIONS = [
        "DANGEROUS_API_CALL",
        "EVAL_USAGE",
        "EXEC_USAGE",
        "BREAKING_CHANGE",
        "SECURITY_BREACH",
    ]

    # TIER 1: Domain-specific, can escalate
    TIER_1_ESCALATION_RULES = [
        "DOMAIN_SPECIFIC_RULE",
        "PERFORMANCE_RISK",
        "API_CHANGE",
        "DATA_MODEL_CHANGE",
    ]

    # TIER 2: Context-aware, requires approval
    TIER_2_CONTEXT_RULES = [
        "CONVERSATION_PATTERN",
        "USER_PATTERN",
        "HISTORICAL_RISK",
    ]

    # TIER 3: Knowledge-based
    TIER_3_KNOWLEDGE_RULES = [
        "PATTERN_MATCH",
        "BEST_PRACTICE_VIOLATION",
    ]

    def __init__(self) -> None:
        """Initialize the validation gate."""
        self.turn_count = 0
        self.turn_history: List[Dict[str, Any]] = []
        self.validation_rules = self._load_validation_rules()

    def _load_validation_rules(self) -> Dict[str, List[str]]:
        """Load validation rules for each tier.

        Returns:
            Dictionary mapping tiers to rules.
        """
        return {
            "TIER_0": self.TIER_0_BLOCKING_VIOLATIONS,
            "TIER_1": self.TIER_1_ESCALATION_RULES,
            "TIER_2": self.TIER_2_CONTEXT_RULES,
            "TIER_3": self.TIER_3_KNOWLEDGE_RULES,
        }

    def validate(
        self,
        turn_number: int,
        intent_type: str,
        governance_tier: str,
        violation_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Validate a turn against governance rules.

        Args:
            turn_number: Turn number in conversation.
            intent_type: Type of intent (QUERY, IMPLEMENT, FIX, REFACTOR, ANALYZE).
            governance_tier: Governance tier (TIER_0, TIER_1, TIER_2, TIER_3).
            violation_type: Optional specific violation to check.
            context: Optional context for validation.

        Returns:
            ValidationResult with status and details.
        """
        context = context or {}
        self.turn_count += 1

        # TIER 0: Blocking violations
        if governance_tier == "TIER_0":
            if violation_type and violation_type in self.TIER_0_BLOCKING_VIOLATIONS:
                result = ValidationResult(
                    status=ValidationStatus.BLOCKED,
                    turn_number=turn_number,
                    message=f"TIER 0 blocking violation: {violation_type}",
                    blocking_violations=[violation_type],
                )
                self.turn_history.append(result.to_dict())
                return result

        # TIER 1: Escalation required
        if governance_tier == "TIER_1":
            if violation_type and violation_type in self.TIER_1_ESCALATION_RULES:
                result = ValidationResult(
                    status=ValidationStatus.ESCALATION_REQUIRED,
                    turn_number=turn_number,
                    message=f"TIER 1 escalation required: {violation_type}",
                    escalation_required_tiers=["TIER_2"],
                )
                self.turn_history.append(result.to_dict())
                return result

        # TIER 2: Context-aware validation
        if governance_tier == "TIER_2":
            blocking_violations = self._check_tier2_rules(context)
            if blocking_violations:
                result = ValidationResult(
                    status=ValidationStatus.ESCALATION_REQUIRED,
                    turn_number=turn_number,
                    message="TIER 2 context rule triggered escalation",
                    escalation_required_tiers=["TIER_3"],
                )
                self.turn_history.append(result.to_dict())
                return result

        # TIER 3: Knowledge-based validation
        if governance_tier == "TIER_3":
            # TIER 3 has passive rules, always passes
            pass

        # Default: Passed validation
        result = ValidationResult(
            status=ValidationStatus.PASSED,
            turn_number=turn_number,
            message=f"Turn {turn_number} passed {governance_tier} validation",
        )
        self.turn_history.append(result.to_dict())
        return result

    def _check_tier2_rules(self, context: Dict[str, Any]) -> List[str]:
        """Check TIER 2 context rules.

        Args:
            context: Context for validation.

        Returns:
            List of violated rules.
        """
        violations = []

        # Check conversation pattern
        if "previous_turns" in context:
            turns = context["previous_turns"]
            if len(turns) > 3:
                # Many turns might indicate conversation fatigue
                violations.append("CONVERSATION_PATTERN")

        # Check for suspicious patterns
        if context.get("trust_level") == "LOW":
            violations.append("USER_PATTERN")

        return violations

    def reset(self) -> None:
        """Reset validation gate state.

        Used for new sessions/conversations.
        """
        self.turn_count = 0
        self.turn_history = []

    def get_turn_history(self) -> List[Dict[str, Any]]:
        """Get turn history.

        Returns:
            List of validated turns.
        """
        return self.turn_history

    def audit_trail(self) -> str:
        """Generate audit trail summary.

        Returns:
            Formatted audit trail string.
        """
        lines = [f"Turn Validation Audit Trail ({self.turn_count} turns)"]
        for turn_result in self.turn_history:
            lines.append(
                f"  Turn {turn_result['turn_number']}: {turn_result['status']} - {turn_result['message']}"
            )
        return "\n".join(lines)
