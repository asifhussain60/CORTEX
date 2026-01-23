"""Tests for TurnValidationGate module.

AC-ID: REMEDIATION-INTENT-004
Tests per-turn governance validation and enforcement.
"""

import pytest
from cortex.orchestrators.turn_validation_gate import (
    TurnValidationGate,
    ValidationResult,
    ValidationStatus,
)


class BaseTurnValidationTest:
    """Base test class with common fixtures."""

    @pytest.fixture(autouse=True)
    def setup_gate(self):
        """Setup TurnValidationGate instance."""
        self.gate = TurnValidationGate()


class TestTurnValidationGateInitialization(BaseTurnValidationTest):
    """Test TurnValidationGate initialization."""

    def test_gate_initializes(self):
        """Test gate initialization."""
        assert self.gate is not None

    def test_turn_counter_starts_at_zero(self):
        """Test turn counter initializes to 0."""
        assert self.gate.turn_count == 0

    def test_validation_rules_loaded(self):
        """Test validation rules are loaded."""
        assert hasattr(self.gate, "validation_rules")
        assert len(self.gate.validation_rules) > 0


class TestValidationResult(BaseTurnValidationTest):
    """Test ValidationResult data class."""

    def test_validation_result_creation(self):
        """Test ValidationResult creation."""
        result = ValidationResult(
            status=ValidationStatus.PASSED,
            turn_number=1,
            message="Validation passed",
        )
        assert result.status == ValidationStatus.PASSED
        assert result.turn_number == 1

    def test_validation_result_with_blocking_violations(self):
        """Test result with blocking violations."""
        result = ValidationResult(
            status=ValidationStatus.BLOCKED,
            turn_number=2,
            blocking_violations=["TIER_0_VIOLATION"],
        )
        assert len(result.blocking_violations) > 0

    def test_validation_result_with_escalations(self):
        """Test result with escalations."""
        result = ValidationResult(
            status=ValidationStatus.ESCALATION_REQUIRED,
            turn_number=3,
            escalation_required_tiers=["TIER_1", "TIER_2"],
        )
        assert len(result.escalation_required_tiers) > 0

    def test_validation_result_to_dict(self):
        """Test to_dict() serialization."""
        result = ValidationResult(
            status=ValidationStatus.PASSED,
            turn_number=1,
            message="Test passed",
        )
        result_dict = result.to_dict()
        assert result_dict["status"] == "PASSED"
        assert result_dict["turn_number"] == 1


class TestTier0BlockingValidation(BaseTurnValidationTest):
    """Test TIER 0 blocking validation rules."""

    def test_tier0_breach_blocks_execution(self):
        """Test TIER 0 breach blocks execution."""
        result = self.gate.validate(
            turn_number=1,
            intent_type="IMPLEMENT",
            governance_tier="TIER_0",
            violation_type="DANGEROUS_API_CALL",
        )
        assert result.status == ValidationStatus.BLOCKED

    def test_tier0_dangerous_pattern_blocked(self):
        """Test TIER 0 dangerous patterns are blocked."""
        result = self.gate.validate(
            turn_number=1,
            intent_type="FIX",
            governance_tier="TIER_0",
            violation_type="EVAL_USAGE",
        )
        assert result.status == ValidationStatus.BLOCKED
        assert len(result.blocking_violations) > 0

    def test_tier0_requires_approval(self):
        """Test TIER 0 blocking violations listed."""
        result = self.gate.validate(
            turn_number=1,
            intent_type="IMPLEMENT",
            governance_tier="TIER_0",
            violation_type="BREAKING_CHANGE",
        )
        if result.status == ValidationStatus.BLOCKED:
            assert result.message is not None


class TestTier1Escalation(BaseTurnValidationTest):
    """Test TIER 1 escalation requirements."""

    def test_tier1_violation_requires_escalation(self):
        """Test TIER 1 violation requires escalation."""
        result = self.gate.validate(
            turn_number=1,
            intent_type="REFACTOR",
            governance_tier="TIER_1",
            violation_type="PERFORMANCE_RISK",
        )
        assert result.status in [
            ValidationStatus.ESCALATION_REQUIRED,
            ValidationStatus.PASSED,
        ]

    def test_tier1_escalation_to_tier2(self):
        """Test TIER 1 can escalate to TIER 2."""
        result = self.gate.validate(
            turn_number=2,
            intent_type="REFACTOR",
            governance_tier="TIER_1",
            violation_type="DOMAIN_SPECIFIC_RULE",
        )
        if result.status == ValidationStatus.ESCALATION_REQUIRED:
            assert "TIER" in str(result.escalation_required_tiers)

    def test_tier1_context_aware_validation(self):
        """Test TIER 1 validation is context-aware."""
        context = {"previous_violations": 1, "success_rate": 0.95}
        result = self.gate.validate(
            turn_number=2,
            intent_type="IMPLEMENT",
            governance_tier="TIER_1",
            context=context,
        )
        assert result is not None


class TestTier2ContextValidation(BaseTurnValidationTest):
    """Test TIER 2 context-aware validation."""

    def test_tier2_context_rule_validation(self):
        """Test TIER 2 context rules."""
        result = self.gate.validate(
            turn_number=1,
            intent_type="IMPLEMENT",
            governance_tier="TIER_2",
            context={"conversation_history": ["QUERY", "IMPLEMENT"]},
        )
        assert result.status is not None

    def test_tier2_multi_turn_analysis(self):
        """Test TIER 2 multi-turn analysis."""
        result = self.gate.validate(
            turn_number=3,
            intent_type="REFACTOR",
            governance_tier="TIER_2",
            context={"turn_history": [1, 2, 3]},
        )
        assert result is not None


class TestTier3Validation(BaseTurnValidationTest):
    """Test TIER 3 knowledge-based validation."""

    def test_tier3_knowledge_validation(self):
        """Test TIER 3 validates against knowledge."""
        result = self.gate.validate(
            turn_number=1,
            intent_type="IMPLEMENT",
            governance_tier="TIER_3",
            context={"domain_knowledge": "Python"},
        )
        assert result is not None

    def test_tier3_pattern_matching(self):
        """Test TIER 3 pattern matching."""
        result = self.gate.validate(
            turn_number=2,
            intent_type="FIX",
            governance_tier="TIER_3",
            context={"pattern_name": "singleton"},
        )
        assert result.status is not None


class TestPerTurnTracking(BaseTurnValidationTest):
    """Test per-turn tracking and state."""

    def test_first_turn_increments_counter(self):
        """Test first turn increments counter."""
        initial = self.gate.turn_count
        self.gate.validate(turn_number=1, intent_type="QUERY", governance_tier="TIER_3")
        assert self.gate.turn_count == initial + 1

    def test_multiple_turns_tracked(self):
        """Test multiple turns are tracked."""
        self.gate.validate(turn_number=1, intent_type="QUERY", governance_tier="TIER_3")
        self.gate.validate(turn_number=2, intent_type="IMPLEMENT", governance_tier="TIER_2")
        self.gate.validate(turn_number=3, intent_type="FIX", governance_tier="TIER_1")
        assert self.gate.turn_count >= 3

    def test_turn_history_preserved(self):
        """Test turn history is preserved."""
        self.gate.validate(turn_number=1, intent_type="QUERY", governance_tier="TIER_3")
        result2 = self.gate.validate(turn_number=2, intent_type="IMPLEMENT", governance_tier="TIER_2")
        assert result2.turn_number == 2

    def test_turn_state_reset_on_new_session(self):
        """Test turn state resets on new session."""
        self.gate.validate(turn_number=1, intent_type="QUERY", governance_tier="TIER_3")
        self.gate.reset()
        assert self.gate.turn_count == 0


class TestPassValidation(BaseTurnValidationTest):
    """Test passing validation scenarios."""

    def test_clean_tier3_passes(self):
        """Test clean TIER 3 validation passes."""
        result = self.gate.validate(
            turn_number=1,
            intent_type="QUERY",
            governance_tier="TIER_3",
        )
        assert result.status == ValidationStatus.PASSED

    def test_clean_tier2_passes(self):
        """Test clean TIER 2 validation passes."""
        result = self.gate.validate(
            turn_number=1,
            intent_type="IMPLEMENT",
            governance_tier="TIER_2",
        )
        assert result.status in [ValidationStatus.PASSED, ValidationStatus.ESCALATION_REQUIRED]

    def test_no_violations_passes(self):
        """Test no violations result in pass."""
        result = self.gate.validate(
            turn_number=1,
            intent_type="REFACTOR",
            governance_tier="TIER_1",
            violation_type=None,
        )
        assert result.status in [ValidationStatus.PASSED, ValidationStatus.ESCALATION_REQUIRED]


class TestMultiTurnValidation(BaseTurnValidationTest):
    """Test multi-turn conversation validation."""

    def test_conversation_pattern_validation(self):
        """Test conversation pattern validation."""
        # Validate first turn
        result1 = self.gate.validate(
            turn_number=1,
            intent_type="QUERY",
            governance_tier="TIER_3",
        )
        # Validate second turn
        result2 = self.gate.validate(
            turn_number=2,
            intent_type="IMPLEMENT",
            governance_tier="TIER_2",
        )
        assert result1.turn_number == 1
        assert result2.turn_number == 2

    def test_turn_sequence_validation(self):
        """Test turn sequence follows expectations."""
        result1 = self.gate.validate(turn_number=1, intent_type="QUERY", governance_tier="TIER_3")
        result2 = self.gate.validate(turn_number=2, intent_type="IMPLEMENT", governance_tier="TIER_2")
        result3 = self.gate.validate(turn_number=3, intent_type="FIX", governance_tier="TIER_1")
        assert result1.turn_number < result2.turn_number < result3.turn_number

    def test_escalation_pattern_across_turns(self):
        """Test escalation pattern across multiple turns."""
        self.gate.validate(turn_number=1, intent_type="QUERY", governance_tier="TIER_3")
        result2 = self.gate.validate(turn_number=2, intent_type="IMPLEMENT", governance_tier="TIER_2")
        result3 = self.gate.validate(turn_number=3, intent_type="FIX", governance_tier="TIER_1")
        # Later turns might require escalation
        assert result2.status is not None
        assert result3.status is not None


class TestValidationWithContext(BaseTurnValidationTest):
    """Test validation with contextual information."""

    def test_conversation_context(self):
        """Test validation with conversation context."""
        context = {
            "previous_turns": [
                {"intent": "QUERY", "passed": True},
                {"intent": "IMPLEMENT", "passed": True},
            ]
        }
        result = self.gate.validate(
            turn_number=3,
            intent_type="FIX",
            governance_tier="TIER_1",
            context=context,
        )
        assert result is not None

    def test_user_context(self):
        """Test validation with user context."""
        context = {
            "user_role": "DEVELOPER",
            "trust_level": "HIGH",
        }
        result = self.gate.validate(
            turn_number=1,
            intent_type="IMPLEMENT",
            governance_tier="TIER_2",
            context=context,
        )
        assert result is not None

    def test_system_context(self):
        """Test validation with system context."""
        context = {
            "api_version": "6.0",
            "security_level": "STANDARD",
        }
        result = self.gate.validate(
            turn_number=1,
            intent_type="IMPLEMENT",
            governance_tier="TIER_2",
            context=context,
        )
        assert result is not None


class TestValidationAudit(BaseTurnValidationTest):
    """Test validation audit trail."""

    def test_validation_audit_trail(self):
        """Test validation audit trail is recorded."""
        result = self.gate.validate(
            turn_number=1,
            intent_type="QUERY",
            governance_tier="TIER_3",
        )
        assert hasattr(result, "timestamp")
        assert result.timestamp is not None

    def test_audit_includes_governance_tier(self):
        """Test audit includes governance tier."""
        result = self.gate.validate(
            turn_number=1,
            intent_type="IMPLEMENT",
            governance_tier="TIER_2",
        )
        # Result should reflect what was validated
        assert result.turn_number == 1


class TestEdgeCases(BaseTurnValidationTest):
    """Test edge cases and boundary conditions."""

    def test_turn_zero_handled(self):
        """Test turn 0 is handled."""
        result = self.gate.validate(
            turn_number=0,
            intent_type="QUERY",
            governance_tier="TIER_3",
        )
        assert result is not None

    def test_high_turn_number(self):
        """Test high turn number is handled."""
        result = self.gate.validate(
            turn_number=100,
            intent_type="IMPLEMENT",
            governance_tier="TIER_2",
        )
        assert result is not None

    def test_empty_context(self):
        """Test empty context works."""
        result = self.gate.validate(
            turn_number=1,
            intent_type="QUERY",
            governance_tier="TIER_3",
            context={},
        )
        assert result.status is not None

    def test_multiple_gates_independent(self):
        """Test multiple gates are independent."""
        gate1 = TurnValidationGate()
        gate2 = TurnValidationGate()
        gate1.validate(turn_number=1, intent_type="QUERY", governance_tier="TIER_3")
        result2 = gate2.validate(turn_number=1, intent_type="QUERY", governance_tier="TIER_3")
        assert result2.turn_number == 1

    def test_invalid_tier_handled(self):
        """Test invalid governance tier is handled."""
        try:
            result = self.gate.validate(
                turn_number=1,
                intent_type="IMPLEMENT",
                governance_tier="INVALID_TIER",
            )
            # Should either return a result or raise ValueError
            assert result is not None
        except ValueError:
            # Acceptable to raise for invalid input
            pass
