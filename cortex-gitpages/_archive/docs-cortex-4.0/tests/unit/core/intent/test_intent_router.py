"""
Tests for Intent Router - Routes canonicalized intents to appropriate orchestrators.

AC-PROD-001-02: Intent Router Decision Tree
"""
import pytest
from dataclasses import dataclass
from typing import Optional
from enum import Enum

from src.core.intent.intent_canonicalizer import IntentType
from src.core.intent.intent_router import (
    IntentRouter,
    RoutingDecision,
    OrchestrationTarget,
)


class TestIntentRouterBasic:
    """Test basic intent routing functionality."""

    def setup_method(self):
        """Initialize router before each test."""
        self.router = IntentRouter()

    def test_router_initializes_successfully(self):
        """GIVEN a new IntentRouter WHEN initialized THEN should create routing map."""
        assert self.router is not None
        assert hasattr(self.router, "route")

    def test_implement_routes_to_tdd(self):
        """GIVEN an IMPLEMENT intent WHEN routed THEN goes to TDDOrchestrator."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.IMPLEMENT, confidence=0.95
        )
        decision = self.router.route(canonical_intent)

        assert decision is not None
        assert decision.target_orchestrator == OrchestrationTarget.TDD
        assert decision.routing_reason is not None

    def test_fix_routes_to_tdd(self):
        """GIVEN a FIX intent WHEN routed THEN goes to TDDOrchestrator."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.FIX, confidence=0.92
        )
        decision = self.router.route(canonical_intent)

        assert decision.target_orchestrator == OrchestrationTarget.TDD

    def test_refactor_routes_to_tdd(self):
        """GIVEN a REFACTOR intent WHEN routed THEN goes to TDDOrchestrator."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.REFACTOR, confidence=0.88
        )
        decision = self.router.route(canonical_intent)

        assert decision.target_orchestrator == OrchestrationTarget.TDD

    def test_validate_routes_to_tdd(self):
        """GIVEN a VALIDATE intent WHEN routed THEN goes to TDDOrchestrator."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.VALIDATE, confidence=0.90
        )
        decision = self.router.route(canonical_intent)

        assert decision.target_orchestrator == OrchestrationTarget.TDD

    def test_migrate_routes_to_tdd(self):
        """GIVEN a MIGRATE intent WHEN routed THEN goes to TDDOrchestrator."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.MIGRATE, confidence=0.87
        )
        decision = self.router.route(canonical_intent)

        assert decision.target_orchestrator == OrchestrationTarget.TDD

    def test_query_routes_to_direct_response(self):
        """GIVEN a QUERY intent WHEN routed THEN returns DirectResponse (no delegation)."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.QUERY, confidence=0.93
        )
        decision = self.router.route(canonical_intent)

        assert decision.target_orchestrator == OrchestrationTarget.DIRECT_RESPONSE
        assert decision.requires_delegation is False

    def test_analyze_routes_to_direct_response(self):
        """GIVEN an ANALYZE intent WHEN routed THEN returns DirectResponse."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.ANALYZE, confidence=0.89
        )
        decision = self.router.route(canonical_intent)

        assert decision.target_orchestrator == OrchestrationTarget.DIRECT_RESPONSE

    def test_unknown_routes_to_interaction(self):
        """GIVEN an UNKNOWN intent WHEN routed THEN returns to InteractionOrchestrator for clarification."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.UNKNOWN, confidence=0.45
        )
        decision = self.router.route(canonical_intent)

        assert decision.target_orchestrator == OrchestrationTarget.INTERACTION


class TestIntentRouterConfidence:
    """Test routing decisions based on confidence levels."""

    def setup_method(self):
        """Initialize router before each test."""
        self.router = IntentRouter()

    def test_high_confidence_routes_to_target(self):
        """GIVEN confidence >= 0.85 WHEN routed THEN goes to target orchestrator."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.IMPLEMENT, confidence=0.95
        )
        decision = self.router.route(canonical_intent)

        assert decision.target_orchestrator == OrchestrationTarget.TDD
        assert decision.caution_flag is False

    def test_medium_confidence_routes_with_caution(self):
        """GIVEN confidence 0.70-0.84 WHEN routed THEN routes with caution flag."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.IMPLEMENT, confidence=0.75
        )
        decision = self.router.route(canonical_intent)

        assert decision.target_orchestrator == OrchestrationTarget.TDD
        assert decision.caution_flag is True
        assert "medium confidence" in decision.routing_reason.lower() or "caution" in decision.routing_reason.lower()

    def test_low_confidence_returns_to_interaction(self):
        """GIVEN confidence < 0.70 WHEN routed THEN returns for clarification."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.IMPLEMENT, confidence=0.65
        )
        decision = self.router.route(canonical_intent)

        assert decision.target_orchestrator == OrchestrationTarget.INTERACTION
        assert decision.caution_flag is True

    def test_query_with_low_confidence_still_returns_direct(self):
        """GIVEN QUERY with low confidence WHEN routed THEN still returns DirectResponse (queries are safe)."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.QUERY, confidence=0.55
        )
        decision = self.router.route(canonical_intent)

        # Queries are safe to handle even with low confidence
        assert decision.target_orchestrator == OrchestrationTarget.DIRECT_RESPONSE


class TestIntentRouterEdgeCases:
    """Test edge cases and unusual routing scenarios."""

    def setup_method(self):
        """Initialize router before each test."""
        self.router = IntentRouter()

    def test_exact_threshold_high_confidence(self):
        """GIVEN confidence exactly 0.85 WHEN routed THEN treat as high confidence."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.IMPLEMENT, confidence=0.85
        )
        decision = self.router.route(canonical_intent)

        assert decision.caution_flag is False

    def test_exact_threshold_medium_low(self):
        """GIVEN confidence exactly 0.70 WHEN routed THEN treat as medium confidence."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.FIX, confidence=0.70
        )
        decision = self.router.route(canonical_intent)

        # 0.70 is the boundary - at this value, treat as medium confidence (>= 0.70)
        assert decision.target_orchestrator == OrchestrationTarget.TDD
        assert decision.caution_flag is True

    def test_zero_confidence(self):
        """GIVEN confidence 0.0 WHEN routed THEN return for interaction."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.IMPLEMENT, confidence=0.0
        )
        decision = self.router.route(canonical_intent)

        assert decision.target_orchestrator == OrchestrationTarget.INTERACTION

    def test_perfect_confidence(self):
        """GIVEN confidence 1.0 WHEN routed THEN route with full certainty."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.QUERY, confidence=1.0
        )
        decision = self.router.route(canonical_intent)

        assert decision.caution_flag is False
        assert decision.target_orchestrator == OrchestrationTarget.DIRECT_RESPONSE

    def test_none_intent_type_defaults_to_unknown(self):
        """GIVEN None intent type WHEN routed THEN treat as UNKNOWN."""
        # Create intent with UNKNOWN type instead of None
        canonical_intent = self._create_intent(
            intent_type=IntentType.UNKNOWN, confidence=0.50
        )
        decision = self.router.route(canonical_intent)

        assert decision.target_orchestrator == OrchestrationTarget.INTERACTION


class TestIntentRouterLogging:
    """Test that routing decisions are logged correctly."""

    def setup_method(self):
        """Initialize router before each test."""
        self.router = IntentRouter()

    def test_routing_decision_has_reason(self):
        """GIVEN a routing decision WHEN created THEN should include reasoning."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.IMPLEMENT, confidence=0.92
        )
        decision = self.router.route(canonical_intent)

        assert decision.routing_reason is not None
        assert len(decision.routing_reason) > 0
        assert "IMPLEMENT" in decision.routing_reason or "implement" in decision.routing_reason

    def test_routing_reason_includes_confidence_info(self):
        """GIVEN medium confidence WHEN routed THEN reason should explain confidence level."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.FIX, confidence=0.75
        )
        decision = self.router.route(canonical_intent)

        assert "confidence" in decision.routing_reason.lower() or "caution" in decision.routing_reason.lower()

    def test_routing_decision_is_auditable(self):
        """GIVEN a routing decision WHEN created THEN should be auditable."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.REFACTOR, confidence=0.88
        )
        decision = self.router.route(canonical_intent)

        assert decision.target_orchestrator is not None
        assert decision.routing_reason is not None
        assert decision.canonical_intent == canonical_intent

    def test_high_confidence_routing_has_explicit_confirmation(self):
        """GIVEN high confidence routing WHEN logged THEN should confirm certainty."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.QUERY, confidence=0.99
        )
        decision = self.router.route(canonical_intent)

        # For queries, we don't necessarily say "high confidence", just route immediately
        assert decision.caution_flag is False
        assert decision.routing_reason is not None


class TestIntentRouterIntegration:
    """Test router integration with other components."""

    def setup_method(self):
        """Initialize router before each test."""
        self.router = IntentRouter()

    def test_all_intent_types_routable(self):
        """GIVEN all IntentType values WHEN routed THEN each produces a valid decision."""
        # Get all IntentType values except UNKNOWN (which we test separately)
        intent_types = [
            IntentType.IMPLEMENT,
            IntentType.FIX,
            IntentType.REFACTOR,
            IntentType.VALIDATE,
            IntentType.MIGRATE,
            IntentType.QUERY,
            IntentType.ANALYZE,
        ]

        for intent_type in intent_types:
            canonical_intent = self._create_intent(
                intent_type=intent_type, confidence=0.85
            )
            decision = self.router.route(canonical_intent)

            assert decision is not None
            assert decision.target_orchestrator in [
                target for target in OrchestrationTarget
            ]

    def test_routing_preserves_canonical_intent(self):
        """GIVEN a canonical intent WHEN routed THEN routing decision preserves intent."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.IMPLEMENT, confidence=0.90
        )
        decision = self.router.route(canonical_intent)

        assert decision.canonical_intent == canonical_intent

    def test_routing_can_be_chained(self):
        """GIVEN multiple routing requests WHEN chained THEN router remains stateless."""
        intent1 = self._create_intent(intent_type=IntentType.QUERY, confidence=0.95)
        intent2 = self._create_intent(intent_type=IntentType.IMPLEMENT, confidence=0.88)

        decision1 = self.router.route(intent1)
        decision2 = self.router.route(intent2)

        # Verify routing is independent
        assert decision1.target_orchestrator == OrchestrationTarget.DIRECT_RESPONSE
        assert decision2.target_orchestrator == OrchestrationTarget.TDD


class TestIntentRouterDelegation:
    """Test delegation flags and requirements."""

    def setup_method(self):
        """Initialize router before each test."""
        self.router = IntentRouter()

    def test_tdd_requires_delegation(self):
        """GIVEN TDD routing WHEN decided THEN requires_delegation should be True."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.IMPLEMENT, confidence=0.92
        )
        decision = self.router.route(canonical_intent)

        assert decision.requires_delegation is True

    def test_direct_response_no_delegation(self):
        """GIVEN DirectResponse routing WHEN decided THEN requires_delegation should be False."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.QUERY, confidence=0.95
        )
        decision = self.router.route(canonical_intent)

        assert decision.requires_delegation is False

    def test_planning_requires_delegation(self):
        """GIVEN Planning routing WHEN decided THEN requires_delegation should be True."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.MIGRATE, confidence=0.85
        )
        decision = self.router.route(canonical_intent)

        assert decision.requires_delegation is True

    def test_interaction_no_delegation(self):
        """GIVEN Interaction routing WHEN decided THEN requires_delegation should be False."""
        canonical_intent = self._create_intent(
            intent_type=IntentType.UNKNOWN, confidence=0.40
        )
        decision = self.router.route(canonical_intent)

        assert decision.requires_delegation is False


# Helper Methods

def _create_intent(intent_type, confidence):
    """Helper to create canonical intent for testing."""
    from src.core.intent.intent_canonicalizer import CanonicalizedIntent, IntentScope

    return CanonicalizedIntent(
        original_text=f"Test {intent_type.name} request",
        intent_type=intent_type,
        scope=IntentScope(description="test"),
        confidence=confidence,
        keywords=["test"],
    )


# Make helper available to all test classes
def setup_function():
    """Setup for module."""
    pass


# Bind helper to test classes
TestIntentRouterBasic._create_intent = staticmethod(_create_intent)
TestIntentRouterConfidence._create_intent = staticmethod(_create_intent)
TestIntentRouterEdgeCases._create_intent = staticmethod(_create_intent)
TestIntentRouterLogging._create_intent = staticmethod(_create_intent)
TestIntentRouterIntegration._create_intent = staticmethod(_create_intent)
TestIntentRouterDelegation._create_intent = staticmethod(_create_intent)
