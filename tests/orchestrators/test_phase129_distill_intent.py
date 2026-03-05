"""
Sub-phase 129-a RED tests — IntentType.DISTILL enum value.

TDD contract (CORE-008): these tests MUST fail before implementation.
Run RED gate:  python3 scripts/run_tests.py file tests/orchestrators/test_phase129_distill_intent.py
Run GREEN gate: same command after adding DISTILL to canonical_enums.py
"""

import pytest
from cortex.models.canonical_enums import IntentType


class TestDistillIntentEnumExists:
    """Tests that IntentType.DISTILL exists in the canonical enum."""

    def test_distill_intent_exists(self):
        """DISTILL must be a valid member of IntentType."""
        assert hasattr(IntentType, "DISTILL"), (
            "IntentType.DISTILL does not exist — add DISTILL = 'distill' to canonical_enums.py"
        )

    def test_distill_intent_value(self):
        """DISTILL enum value must be the string 'distill'."""
        assert IntentType.DISTILL.value == "distill", (
            f"Expected IntentType.DISTILL.value == 'distill', got {IntentType.DISTILL.value!r}"
        )

    def test_distill_intent_is_enum_member(self):
        """IntentType.DISTILL must be reachable as a proper enum member."""
        assert IntentType.DISTILL in list(IntentType), (
            "IntentType.DISTILL is not in list(IntentType) — enum definition is malformed"
        )

    def test_distill_intent_lookup_by_value(self):
        """Must be reversible: IntentType('distill') == IntentType.DISTILL."""
        result = IntentType("distill")
        assert result == IntentType.DISTILL, (
            f"IntentType('distill') returned {result!r} — reverse lookup failed"
        )

    def test_enum_count_incremented(self):
        """Adding DISTILL must bring the total IntentType count to 30."""
        total = len(list(IntentType))
        assert total == 30, (
            f"Expected 30 IntentType members (was 29 + DISTILL), got {total}"
        )
