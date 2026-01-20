"""
Tests for ContinuationDecision dataclass and ContinuationReason enum.

Tests validate:
- ContinuationDecision structure with all required fields
- ContinuationReason enum values
- Immutability (frozen dataclass)
- JSON serialization/deserialization
- Property methods for convenience access
"""

import json
import pytest
from datetime import datetime
from typing import Dict, Any

from cortex.core.orchestrator.continuation_decision import (
    ContinuationDecision,
    ContinuationReason,
)


class TestContinuationDecision:
    """Test ContinuationDecision dataclass structure and functionality."""

    def test_continuation_decision_creation_with_minimal_fields(self):
        """Test creating ContinuationDecision with minimal required fields."""
        decision = ContinuationDecision(
            should_continue=False,
            reason=ContinuationReason.COMPLETION,
            next_operation="done",
            turn_number=1,
            token_usage={"prompt": 100, "completion": 50, "total": 150},
        )
        
        assert decision.should_continue is False
        assert decision.reason == ContinuationReason.COMPLETION
        assert decision.next_operation == "done"
        assert decision.turn_number == 1
        assert decision.token_usage["total"] == 150

    def test_continuation_decision_all_fields(self):
        """Test ContinuationDecision with all optional fields."""
        decision = ContinuationDecision(
            should_continue=True,
            reason=ContinuationReason.IMPLICIT_NEXT_OPERATION,
            next_operation="refine_result",
            next_parameters={"iteration": 2, "focus": "accuracy"},
            turn_number=2,
            token_usage={"prompt": 200, "completion": 100, "total": 300},
            audit_entry_id="audit-123",
            governance_violations=["CORE-013"],
        )
        
        assert decision.should_continue is True
        assert decision.next_parameters["iteration"] == 2
        assert decision.audit_entry_id == "audit-123"
        assert "CORE-013" in decision.governance_violations

    def test_continuation_decision_is_immutable(self):
        """Test that ContinuationDecision is frozen (immutable)."""
        decision = ContinuationDecision(
            should_continue=False,
            reason=ContinuationReason.COMPLETION,
            next_operation="done",
            turn_number=1,
            token_usage={"prompt": 100, "completion": 50, "total": 150},
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            decision.should_continue = True

    def test_continuation_decision_has_required_fields(self):
        """Test all required fields are present in ContinuationDecision."""
        decision = ContinuationDecision(
            should_continue=True,
            reason=ContinuationReason.USER_PROVIDED_FOLLOWUP,
            next_operation="process_input",
            turn_number=1,
            token_usage={"prompt": 150, "completion": 75, "total": 225},
        )
        
        # Verify all required fields exist and have correct types
        assert isinstance(decision.should_continue, bool)
        assert isinstance(decision.reason, ContinuationReason)
        assert isinstance(decision.next_operation, str)
        assert isinstance(decision.turn_number, int)
        assert isinstance(decision.token_usage, dict)

    def test_continuation_decision_property_is_halt_by_governance(self):
        """Test is_halt_by_governance property."""
        halt_decision = ContinuationDecision(
            should_continue=False,
            reason=ContinuationReason.GOVERNANCE_HALT,
            next_operation="stop",
            turn_number=1,
            token_usage={"prompt": 100, "completion": 50, "total": 150},
        )
        
        completion_decision = ContinuationDecision(
            should_continue=False,
            reason=ContinuationReason.COMPLETION,
            next_operation="done",
            turn_number=1,
            token_usage={"prompt": 100, "completion": 50, "total": 150},
        )
        
        assert halt_decision.is_halt_by_governance is True
        assert completion_decision.is_halt_by_governance is False

    def test_continuation_decision_property_is_user_action_required(self):
        """Test is_user_action_required property."""
        interaction_required = ContinuationDecision(
            should_continue=False,
            reason=ContinuationReason.INTERACTION_REQUIRED,
            next_operation="wait_for_user",
            turn_number=2,
            token_usage={"prompt": 200, "completion": 100, "total": 300},
        )
        
        completion = ContinuationDecision(
            should_continue=False,
            reason=ContinuationReason.COMPLETION,
            next_operation="done",
            turn_number=1,
            token_usage={"prompt": 100, "completion": 50, "total": 150},
        )
        
        assert interaction_required.is_user_action_required is True
        assert completion.is_user_action_required is False

    def test_continuation_decision_property_is_safe_to_resume(self):
        """Test is_safe_to_resume property."""
        # Safe to resume: token limit or interaction required
        token_limit_decision = ContinuationDecision(
            should_continue=False,
            reason=ContinuationReason.TOKEN_LIMIT,
            next_operation="resume_later",
            turn_number=5,
            token_usage={"prompt": 1900, "completion": 900, "total": 2800},
        )
        
        # Not safe to resume: error or governance halt
        error_decision = ContinuationDecision(
            should_continue=False,
            reason=ContinuationReason.ERROR_UNRECOVERABLE,
            next_operation="stop",
            turn_number=3,
            token_usage={"prompt": 300, "completion": 150, "total": 450},
        )
        
        # Safe to resume: completion with follow-up
        completion_decision = ContinuationDecision(
            should_continue=False,
            reason=ContinuationReason.COMPLETION,
            next_operation="done",
            turn_number=1,
            token_usage={"prompt": 100, "completion": 50, "total": 150},
        )
        
        assert token_limit_decision.is_safe_to_resume is True
        assert error_decision.is_safe_to_resume is False
        assert completion_decision.is_safe_to_resume is True

    def test_continuation_decision_json_serialization(self):
        """Test JSON serialization of ContinuationDecision."""
        decision = ContinuationDecision(
            should_continue=True,
            reason=ContinuationReason.AUTO_REFINEMENT_LOOP,
            next_operation="refine",
            next_parameters={"attempt": 2},
            turn_number=2,
            token_usage={"prompt": 200, "completion": 100, "total": 300},
            audit_entry_id="audit-456",
        )
        
        # Serialize to JSON
        json_str = json.dumps(decision.to_dict())
        
        # Should not raise
        assert json_str is not None
        assert "CONTINUATION_AUTO_REFINEMENT_LOOP" in json_str or "AUTO_REFINEMENT_LOOP" in json_str

    def test_continuation_decision_json_deserialization(self):
        """Test JSON deserialization of ContinuationDecision."""
        original_dict = {
            "should_continue": False,
            "reason": "COMPLETION",
            "next_operation": "done",
            "turn_number": 1,
            "token_usage": {"prompt": 100, "completion": 50, "total": 150},
            "audit_entry_id": "audit-789",
            "governance_violations": [],
        }
        
        # Convert to actual dataclass
        decision = ContinuationDecision.from_dict(original_dict)
        
        assert decision.should_continue is False
        assert decision.reason == ContinuationReason.COMPLETION
        assert decision.turn_number == 1

    def test_continuation_decision_to_dict(self):
        """Test to_dict() method."""
        decision = ContinuationDecision(
            should_continue=False,
            reason=ContinuationReason.COMPLETION,
            next_operation="done",
            turn_number=1,
            token_usage={"prompt": 100, "completion": 50, "total": 150},
        )
        
        decision_dict = decision.to_dict()
        
        assert decision_dict["should_continue"] is False
        assert decision_dict["turn_number"] == 1
        assert decision_dict["token_usage"]["total"] == 150


class TestContinuationReason:
    """Test ContinuationReason enum."""

    def test_continuation_reason_has_all_required_values(self):
        """Test ContinuationReason enum has all expected values."""
        required_reasons = [
            ContinuationReason.IMPLICIT_NEXT_OPERATION,
            ContinuationReason.USER_PROVIDED_FOLLOWUP,
            ContinuationReason.AUTO_REFINEMENT_LOOP,
            ContinuationReason.COMPLETION,
            ContinuationReason.USER_REJECTION,
            ContinuationReason.TOKEN_LIMIT,
            ContinuationReason.GOVERNANCE_HALT,
            ContinuationReason.MAX_ROUNDS_REACHED,
            ContinuationReason.ERROR_UNRECOVERABLE,
            ContinuationReason.INTERACTION_REQUIRED,
        ]
        
        # All should be accessible
        for reason in required_reasons:
            assert reason is not None

    def test_continuation_reason_enum_is_comparable(self):
        """Test ContinuationReason enum values are comparable."""
        reason1 = ContinuationReason.COMPLETION
        reason2 = ContinuationReason.COMPLETION
        reason3 = ContinuationReason.ERROR_UNRECOVERABLE
        
        assert reason1 == reason2
        assert reason1 != reason3

    def test_continuation_reason_enum_string_conversion(self):
        """Test ContinuationReason can be converted to string."""
        reason = ContinuationReason.TOKEN_LIMIT
        
        # Should have a string representation
        reason_str = str(reason)
        assert reason_str is not None
        assert len(reason_str) > 0

    def test_continuation_reason_from_string(self):
        """Test creating ContinuationReason from string."""
        reason = ContinuationReason.from_string("COMPLETION")
        
        assert reason == ContinuationReason.COMPLETION

    def test_continuation_reason_from_string_case_insensitive(self):
        """Test ContinuationReason.from_string() is case insensitive."""
        reason_upper = ContinuationReason.from_string("COMPLETION")
        reason_lower = ContinuationReason.from_string("completion")
        
        assert reason_upper == reason_lower


class TestSerializationDeserialization:
    """Test serialization and deserialization round-trips."""

    def test_full_round_trip_serialization(self):
        """Test serialize → deserialize maintains data integrity."""
        original = ContinuationDecision(
            should_continue=True,
            reason=ContinuationReason.USER_PROVIDED_FOLLOWUP,
            next_operation="process_user_input",
            next_parameters={"input_type": "text", "priority": "high"},
            turn_number=3,
            token_usage={"prompt": 450, "completion": 200, "total": 650},
            audit_entry_id="audit-001-turn-3",
            governance_violations=["CORE-013", "CORE-027"],
        )
        
        # Serialize
        dict_form = original.to_dict()
        
        # Deserialize
        restored = ContinuationDecision.from_dict(dict_form)
        
        # Verify all fields match
        assert restored.should_continue == original.should_continue
        assert restored.reason == original.reason
        assert restored.next_operation == original.next_operation
        assert restored.next_parameters == original.next_parameters
        assert restored.turn_number == original.turn_number
        assert restored.token_usage == original.token_usage
        assert restored.audit_entry_id == original.audit_entry_id
        assert restored.governance_violations == original.governance_violations

    def test_minimal_round_trip_serialization(self):
        """Test serialize → deserialize with minimal fields."""
        original = ContinuationDecision(
            should_continue=False,
            reason=ContinuationReason.COMPLETION,
            next_operation="done",
            turn_number=1,
            token_usage={"prompt": 100, "completion": 50, "total": 150},
        )
        
        dict_form = original.to_dict()
        restored = ContinuationDecision.from_dict(dict_form)
        
        assert restored.should_continue == original.should_continue
        assert restored.reason == original.reason
        assert restored.next_operation == original.next_operation
