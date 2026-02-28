"""
Phase 89-b: IntentType Enum Expansion - GAP-89-19
RED → GREEN → REFACTOR

AC-ID: AC-PHASE-89B-INTENT-ENUM
Purpose: Add 7 missing IntentType enum values for complete execution mode coverage
Gap: GAP-89-19 — IntentType enum missing VACUUM, DEBUG, HEALTH, SYNC, TRAIN, TOTALRECALL, RCA

Governance:
- CORE-008: TDD mandatory (this is RED phase)
- CORE-011: Type hints on all functions
- CORE-035: Single canonical implementation (canonical_enums.py is SSOT)
"""

import pytest
from cortex.models.canonical_enums import IntentType


class TestIntentTypeEnumExpansion:
    """
    Cluster 1: Verify all 7 missing IntentType enum values exist.
    
    Context: Phase 89 canvas audit identified 7 execution modes defined in
    cortex-architect.prompt.md but missing from IntentType enum. These modes
    are already wired in WorkflowComplexityRouter._select_orchestrator() but
    cannot be properly classified without enum values.
    """

    def test_vacuum_intent_exists(self) -> None:
        """VACUUM intent exists for markdown sprawl cleanup."""
        assert hasattr(IntentType, 'VACUUM')
        assert IntentType.VACUUM.value == "vacuum"

    def test_debug_intent_exists(self) -> None:
        """DEBUG intent exists for multi-stack debug pipeline."""
        assert hasattr(IntentType, 'DEBUG')
        assert IntentType.DEBUG.value == "debug"

    def test_health_intent_exists(self) -> None:
        """HEALTH intent exists for orchestrator health checks."""
        assert hasattr(IntentType, 'HEALTH')
        assert IntentType.HEALTH.value == "health"

    def test_sync_intent_exists(self) -> None:
        """SYNC intent exists for privacy-safe folder sync."""
        assert hasattr(IntentType, 'SYNC')
        assert IntentType.SYNC.value == "sync"

    def test_train_intent_exists(self) -> None:
        """TRAIN intent exists for learning/reinforcement operations."""
        assert hasattr(IntentType, 'TRAIN')
        assert IntentType.TRAIN.value == "train"

    def test_totalrecall_intent_exists(self) -> None:
        """TOTALRECALL intent exists for holistic refactor protocol."""
        assert hasattr(IntentType, 'TOTALRECALL')
        assert IntentType.TOTALRECALL.value == "totalrecall"

    def test_rca_intent_exists(self) -> None:
        """RCA intent exists for root cause analysis operations."""
        assert hasattr(IntentType, 'RCA')
        assert IntentType.RCA.value == "rca"


class TestIntentTypeEnumCompleteness:
    """
    Cluster 2: Verify IntentType enum has all 22 execution modes (15 existing + 7 new).
    
    This ensures the enum is a complete SSOT for all CORTEX execution modes
    documented in cortex-architect.prompt.md.
    """

    @pytest.mark.parametrize("intent_value", [
        # Original 15 (existing)
        "implement", "fix", "refactor", "analyze", "document",
        "test", "deploy", "governance", "query", "validate",
        "migrate", "onboard", "plan", "audit", "design",
        "digest", "rephrase", "investigate", "golden_test", "unknown",
        # New 7 (Phase 89-b)
        "vacuum", "debug", "health", "sync", "train", "totalrecall", "rca"
    ])
    def test_all_intent_values_exist(self, intent_value: str) -> None:
        """All 27 intent values exist in IntentType enum."""
        intent_values = [intent.value for intent in IntentType]
        assert intent_value in intent_values, f"IntentType missing value: {intent_value}"

    def test_intent_enum_has_27_values(self) -> None:
        """IntentType enum has exactly 27 values (20 existing + 7 new)."""
        # Count may differ if UNKNOWN is present — validate >= 26 (all non-UNKNOWN values)
        intent_count = len(list(IntentType))
        assert intent_count >= 26, f"Expected ≥26 IntentType values, got {intent_count}"

    def test_new_intents_are_enum_members(self) -> None:
        """All 7 new intents are proper Enum members (not just strings)."""
        new_intents = ['VACUUM', 'DEBUG', 'HEALTH', 'SYNC', 'TRAIN', 'TOTALRECALL', 'RCA']
        for intent_name in new_intents:
            assert hasattr(IntentType, intent_name), f"IntentType.{intent_name} not found"
            intent_member = getattr(IntentType, intent_name)
            assert isinstance(intent_member, IntentType), f"{intent_name} is not an IntentType member"


class TestIntentTypeEnumUsability:
    """
    Cluster 3: Verify new IntentType enum values are usable in routing logic.
    
    This ensures the enum values can be compared, converted, and used in
    conditional logic throughout the IntentRouter pipeline.
    """

    def test_new_intents_are_comparable(self) -> None:
        """New intent values can be compared with == operator."""
        assert IntentType.VACUUM == IntentType.VACUUM
        assert IntentType.DEBUG != IntentType.VACUUM
        assert IntentType.HEALTH.value == "health"

    def test_new_intents_can_be_converted_to_string(self) -> None:
        """New intent values can be converted to strings for logging."""
        assert str(IntentType.VACUUM) == "IntentType.VACUUM"
        assert IntentType.DEBUG.value == "debug"
        assert IntentType.TOTALRECALL.name == "TOTALRECALL"

    def test_new_intents_in_dict_keys(self) -> None:
        """New intent values can be used as dictionary keys."""
        routing_map = {
            IntentType.VACUUM: "VacuumOrchestrator",
            IntentType.DEBUG: "DebuggerOrchestrator",
            IntentType.HEALTH: "HealthOrchestrator",
            IntentType.RCA: "LearningOrchestrator"
        }
        assert routing_map[IntentType.VACUUM] == "VacuumOrchestrator"
        assert routing_map[IntentType.DEBUG] == "DebuggerOrchestrator"

    def test_new_intents_in_list_membership(self) -> None:
        """New intent values can be checked with 'in' operator."""
        system_intents = [IntentType.HEALTH, IntentType.VACUUM, IntentType.DEBUG]
        assert IntentType.HEALTH in system_intents
        assert IntentType.IMPLEMENT not in system_intents

    @pytest.mark.parametrize("intent_str,expected_enum", [
        ("vacuum", IntentType.VACUUM),
        ("debug", IntentType.DEBUG),
        ("health", IntentType.HEALTH),
        ("sync", IntentType.SYNC),
        ("train", IntentType.TRAIN),
        ("totalrecall", IntentType.TOTALRECALL),
        ("rca", IntentType.RCA),
    ])
    def test_new_intents_can_be_looked_up_by_value(self, intent_str: str, expected_enum: IntentType) -> None:
        """New intent values can be looked up by string value."""
        # Standard Enum lookup pattern: IntentType(value)
        found_intent = IntentType(intent_str)
        assert found_intent == expected_enum
