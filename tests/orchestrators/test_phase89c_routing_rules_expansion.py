"""
Phase 89-c: Routing Rules Expansion - GAP-89-20
RED → GREEN → REFACTOR

AC-ID: AC-PHASE-89C-ROUTING-RULES
Purpose: Expand _build_routing_rules() to cover all 27 IntentType values
Gap: GAP-89-20 — _build_routing_rules() only has rules for 5 of 27 intents

Governance:
- CORE-008: TDD mandatory (this is RED phase)
- CORE-011: Type hints on all functions
- CORE-064: Sweep completeness contract (all intents must have rules)
"""

import pytest
from typing import Dict, Tuple, Optional

from cortex.models.canonical_enums import IntentType
from cortex.orchestrators.core.intent_router_impl import IntentRouter


class TestRoutingRulesCompleteness:
    """
    Cluster 1: Verify _build_routing_rules() returns rules for all 27 IntentType values.
    
    Context: Current implementation only has routing rules for 5 intents (IMPLEMENT,
    FIX, REFACTOR, DOCUMENT, PLAN). Need to add rules for the remaining 22 intents
    to ensure IntentRouter can route all execution modes.
    """

    @pytest.fixture
    def intent_router(self) -> IntentRouter:
        """Create IntentRouter instance for testing."""
        return IntentRouter()

    @pytest.mark.parametrize("intent", [
        IntentType.IMPLEMENT,
        IntentType.FIX,
        IntentType.REFACTOR,
        IntentType.ANALYZE,
        IntentType.DOCUMENT,
        IntentType.TEST,
        IntentType.DEPLOY,
        IntentType.GOVERNANCE,
        IntentType.QUERY,
        IntentType.VALIDATE,
        IntentType.MIGRATE,
        IntentType.ONBOARD,
        IntentType.PLAN,
        IntentType.AUDIT,
        IntentType.DESIGN,
        IntentType.DIGEST,
        IntentType.REPHRASE,
        IntentType.INVESTIGATE,
        IntentType.GOLDEN_TEST,
        IntentType.VACUUM,
        IntentType.DEBUG,
        IntentType.HEALTH,
        IntentType.SYNC,
        IntentType.TRAIN,
        IntentType.TOTALRECALL,
        IntentType.RCA,
    ])
    def test_routing_rules_has_default_handler_for_intent(
        self, intent_router: IntentRouter, intent: IntentType
    ) -> None:
        """All intents (except UNKNOWN) have at least a default routing rule."""
        rules = intent_router._build_routing_rules()
        
        # Check for (intent, None) — the default handler key
        default_key = (intent, None)
        assert default_key in rules, (
            f"No default routing rule for {intent.name}. "
            f"Expected key ({intent}, None) in routing rules."
        )
        
        # Verify handler is a non-empty string
        handler = rules[default_key]
        assert isinstance(handler, str), f"Handler for {intent.name} is not a string: {handler}"
        assert len(handler) > 0, f"Handler for {intent.name} is empty"

    def test_routing_rules_has_at_least_26_default_rules(
        self, intent_router: IntentRouter
    ) -> None:
        """Routing rules contain at least 26 default handlers (one per non-UNKNOWN intent)."""
        rules = intent_router._build_routing_rules()
        
        # Count (IntentType.*, None) entries — these are default handlers
        default_rules = [key for key in rules.keys() if key[1] is None]
        
        assert len(default_rules) >= 26, (
            f"Expected ≥26 default routing rules, found {len(default_rules)}. "
            f"Missing rules for some IntentType values."
        )

    def test_unknown_intent_has_no_routing_rule(
        self, intent_router: IntentRouter
    ) -> None:
        """UNKNOWN intent deliberately has no routing rule (handled by fallback)."""
        rules = intent_router._build_routing_rules()
        
        # UNKNOWN should NOT have a routing rule — it's a fallback case
        unknown_keys = [key for key in rules.keys() if key[0] == IntentType.UNKNOWN]
        assert len(unknown_keys) == 0, (
            f"UNKNOWN intent should not have routing rules (fallback only). "
            f"Found rules: {unknown_keys}"
        )


class TestRoutingRulesStructure:
    """
    Cluster 2: Verify routing rules dictionary structure and types.
    
    Ensures the returned rules dictionary has the correct key/value types
    and follows the (IntentType, Optional[str]) → str pattern.
    """

    @pytest.fixture
    def intent_router(self) -> IntentRouter:
        """Create IntentRouter instance for testing."""
        return IntentRouter()

    def test_routing_rules_returns_dict(
        self, intent_router: IntentRouter
    ) -> None:
        """_build_routing_rules() returns a dictionary."""
        rules = intent_router._build_routing_rules()
        assert isinstance(rules, dict), f"Expected dict, got {type(rules)}"

    def test_routing_rules_keys_are_tuples(
        self, intent_router: IntentRouter
    ) -> None:
        """All routing rule keys are (IntentType, Optional[str]) tuples."""
        rules = intent_router._build_routing_rules()
        
        for key in rules.keys():
            assert isinstance(key, tuple), f"Key is not tuple: {key}"
            assert len(key) == 2, f"Key tuple length != 2: {key}"
            assert isinstance(key[0], IntentType), f"First element not IntentType: {key[0]}"
            assert key[1] is None or isinstance(key[1], str), (
                f"Second element not None or str: {key[1]}"
            )

    def test_routing_rules_values_are_strings(
        self, intent_router: IntentRouter
    ) -> None:
        """All routing rule values are non-empty strings (orchestrator names)."""
        rules = intent_router._build_routing_rules()
        
        for key, value in rules.items():
            assert isinstance(value, str), f"Value for {key} is not str: {value}"
            assert len(value) > 0, f"Value for {key} is empty string"

    def test_routing_rules_is_not_empty(
        self, intent_router: IntentRouter
    ) -> None:
        """Routing rules dictionary is not empty."""
        rules = intent_router._build_routing_rules()
        assert len(rules) > 0, "Routing rules dictionary is empty"


class TestSpecificOrchestratorMappings:
    """
    Cluster 3: Verify specific intent→orchestrator mappings for key execution modes.
    
    Ensures critical intents are mapped to their canonical orchestrators from
    Phase 89-a canvas audit (WorkflowComplexityRouter._select_orchestrator).
    """

    @pytest.fixture
    def intent_router(self) -> IntentRouter:
        """Create IntentRouter instance for testing."""
        return IntentRouter()

    @pytest.mark.parametrize("intent,expected_orchestrator", [
        (IntentType.VACUUM, "VacuumOrchestrator"),
        (IntentType.DEBUG, "DebuggerOrchestrator"),
        (IntentType.HEALTH, "HealthOrchestrator"),
        (IntentType.ONBOARD, "OnboardOrchestrator"),
        (IntentType.AUDIT, "AuditOrchestrator"),
        (IntentType.VALIDATE, "ValidationOrchestrator"),
        (IntentType.TEST, "TDDOrchestrator"),
        (IntentType.GOVERNANCE, "EnforcementOrchestrator"),
        (IntentType.ANALYZE, "IntelligenceOrchestrator"),
        (IntentType.RCA, "LearningOrchestrator"),
    ])
    def test_critical_intents_map_to_canonical_orchestrators(
        self, intent_router: IntentRouter, intent: IntentType, expected_orchestrator: str
    ) -> None:
        """Critical intents map to their canonical orchestrators."""
        rules = intent_router._build_routing_rules()
        default_key = (intent, None)
        
        assert default_key in rules, f"No default rule for {intent.name}"
        actual_orchestrator = rules[default_key]
        
        assert actual_orchestrator == expected_orchestrator, (
            f"{intent.name} maps to {actual_orchestrator}, expected {expected_orchestrator}"
        )
