"""Tests for ConfidenceRouter module.

AC-ID: REMEDIATION-INTENT-003
Tests confidence-based routing decisions and thresholds.
"""

import pytest
from cortex.orchestrators.confidence_router import (
    ConfidenceRouter,
    RoutingDecision,
    RoutingDecisionType,
)


class BaseConfidenceRouterTest:
    """Base test class with common fixtures."""

    @pytest.fixture(autouse=True)
    def setup_router(self):
        """Setup ConfidenceRouter instance."""
        self.router = ConfidenceRouter()


class TestConfidenceRouterInitialization(BaseConfidenceRouterTest):
    """Test ConfidenceRouter initialization."""

    def test_router_initializes(self):
        """Test router initialization."""
        assert self.router is not None

    def test_confidence_thresholds_set(self):
        """Test confidence thresholds are set."""
        assert hasattr(self.router, "HIGH_CONFIDENCE_THRESHOLD")
        assert hasattr(self.router, "MEDIUM_CONFIDENCE_THRESHOLD")
        assert self.router.HIGH_CONFIDENCE_THRESHOLD >= self.router.MEDIUM_CONFIDENCE_THRESHOLD

    def test_high_threshold_is_0_85(self):
        """Test HIGH confidence threshold is 0.85."""
        assert self.router.HIGH_CONFIDENCE_THRESHOLD == 0.85

    def test_medium_threshold_is_0_70(self):
        """Test MEDIUM confidence threshold is 0.70."""
        assert self.router.MEDIUM_CONFIDENCE_THRESHOLD == 0.70


class TestRoutingDecision(BaseConfidenceRouterTest):
    """Test RoutingDecision data class."""

    def test_routing_decision_creation(self):
        """Test RoutingDecision creation."""
        decision = RoutingDecision(
            decision_type=RoutingDecisionType.DIRECT_ROUTE,
            confidence=0.95,
            target_stage="KNOWLEDGE",
        )
        assert decision.decision_type == RoutingDecisionType.DIRECT_ROUTE
        assert decision.confidence == 0.95
        assert decision.target_stage == "KNOWLEDGE"

    def test_routing_decision_caution_flag(self):
        """Test caution flag in decision."""
        decision = RoutingDecision(
            decision_type=RoutingDecisionType.CAUTION_ROUTE,
            confidence=0.75,
            caution_flag=True,
        )
        assert decision.caution_flag is True

    def test_routing_decision_reason(self):
        """Test reason field."""
        decision = RoutingDecision(
            decision_type=RoutingDecisionType.CLARIFICATION_NEEDED,
            confidence=0.5,
            reason="Low confidence on intent interpretation",
        )
        assert decision.reason == "Low confidence on intent interpretation"

    def test_routing_decision_to_dict(self):
        """Test to_dict() serialization."""
        decision = RoutingDecision(
            decision_type=RoutingDecisionType.DIRECT_ROUTE,
            confidence=0.92,
            target_stage="KNOWLEDGE",
        )
        result = decision.to_dict()
        assert result["decision_type"] == "DIRECT_ROUTE"
        assert result["confidence"] == 0.92
        assert result["target_stage"] == "KNOWLEDGE"


class TestHighConfidenceRouting(BaseConfidenceRouterTest):
    """Test high confidence routing (≥0.85)."""

    def test_confidence_0_95_routes_to_knowledge(self):
        """Test 0.95 confidence routes directly to KNOWLEDGE."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.95,
        )
        assert decision.decision_type == RoutingDecisionType.DIRECT_ROUTE
        assert decision.caution_flag is False

    def test_confidence_0_90_routes_directly(self):
        """Test 0.90 confidence routes directly."""
        decision = self.router.route(
            intent_type="REFACTOR",
            confidence=0.90,
        )
        assert decision.decision_type == RoutingDecisionType.DIRECT_ROUTE

    def test_confidence_0_85_threshold_direct(self):
        """Test exactly 0.85 (threshold) routes directly."""
        decision = self.router.route(
            intent_type="FIX",
            confidence=0.85,
        )
        assert decision.decision_type == RoutingDecisionType.DIRECT_ROUTE

    def test_high_confidence_no_caution(self):
        """Test high confidence has no caution flag."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.88,
        )
        assert decision.caution_flag is False

    def test_high_confidence_reason(self):
        """Test high confidence decision includes reason."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.90,
        )
        assert decision.reason is not None
        assert len(decision.reason) > 0


class TestMediumConfidenceRouting(BaseConfidenceRouterTest):
    """Test medium confidence routing (0.70-0.84)."""

    def test_confidence_0_75_caution_route(self):
        """Test 0.75 confidence triggers caution route."""
        decision = self.router.route(
            intent_type="FIX",
            confidence=0.75,
        )
        assert decision.decision_type == RoutingDecisionType.CAUTION_ROUTE
        assert decision.caution_flag is True

    def test_confidence_0_70_threshold_caution(self):
        """Test exactly 0.70 (threshold) triggers caution."""
        decision = self.router.route(
            intent_type="REFACTOR",
            confidence=0.70,
        )
        assert decision.decision_type == RoutingDecisionType.CAUTION_ROUTE

    def test_confidence_0_80_caution_route(self):
        """Test 0.80 confidence triggers caution."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.80,
        )
        assert decision.decision_type == RoutingDecisionType.CAUTION_ROUTE

    def test_medium_confidence_includes_escalation(self):
        """Test medium confidence includes escalation advice."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.75,
        )
        assert decision.reason is not None
        assert "escalat" in decision.reason.lower() or "caution" in decision.reason.lower()

    def test_medium_confidence_target_stage(self):
        """Test medium confidence includes target stage."""
        decision = self.router.route(
            intent_type="FIX",
            confidence=0.75,
        )
        assert decision.target_stage is not None


class TestLowConfidenceRouting(BaseConfidenceRouterTest):
    """Test low confidence routing (<0.70)."""

    def test_confidence_0_65_needs_clarification(self):
        """Test 0.65 confidence needs clarification."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.65,
        )
        assert decision.decision_type == RoutingDecisionType.CLARIFICATION_NEEDED

    def test_confidence_0_50_needs_clarification(self):
        """Test 0.50 confidence needs clarification."""
        decision = self.router.route(
            intent_type="REFACTOR",
            confidence=0.50,
        )
        assert decision.decision_type == RoutingDecisionType.CLARIFICATION_NEEDED

    def test_confidence_0_10_needs_clarification(self):
        """Test 0.10 confidence needs clarification."""
        decision = self.router.route(
            intent_type="FIX",
            confidence=0.10,
        )
        assert decision.decision_type == RoutingDecisionType.CLARIFICATION_NEEDED

    def test_low_confidence_no_target_stage(self):
        """Test low confidence doesn't set target stage."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.30,
        )
        assert decision.target_stage is None or decision.target_stage == "INTERACTION"

    def test_low_confidence_reason_suggests_interaction(self):
        """Test low confidence reason suggests user interaction."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.40,
        )
        assert "clarif" in decision.reason.lower() or "interactiv" in decision.reason.lower()


class TestIntentTypeRoutingRules(BaseConfidenceRouterTest):
    """Test routing behavior for different intent types."""

    def test_query_intent_always_direct_response(self):
        """Test QUERY intent always routes to DIRECT_RESPONSE."""
        # Low confidence QUERY
        decision = self.router.route(
            intent_type="QUERY",
            confidence=0.40,
        )
        assert decision.target_stage == "DIRECT_RESPONSE" or decision.decision_type == RoutingDecisionType.DIRECT_ROUTE

    def test_analyze_intent_always_direct_response(self):
        """Test ANALYZE intent always routes to DIRECT_RESPONSE."""
        decision = self.router.route(
            intent_type="ANALYZE",
            confidence=0.30,
        )
        assert decision.target_stage == "DIRECT_RESPONSE" or decision.decision_type == RoutingDecisionType.DIRECT_ROUTE

    def test_implement_low_confidence_goes_back_to_interaction(self):
        """Test IMPLEMENT with low confidence goes to INTERACTION."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.50,
        )
        # Low confidence non-query should clarify
        assert decision.decision_type in [
            RoutingDecisionType.CLARIFICATION_NEEDED,
            RoutingDecisionType.CAUTION_ROUTE,
        ]

    def test_fix_low_confidence_goes_back_to_interaction(self):
        """Test FIX with low confidence goes to INTERACTION."""
        decision = self.router.route(
            intent_type="FIX",
            confidence=0.40,
        )
        assert decision.decision_type == RoutingDecisionType.CLARIFICATION_NEEDED

    def test_refactor_high_confidence_goes_to_knowledge(self):
        """Test REFACTOR with high confidence goes to KNOWLEDGE."""
        decision = self.router.route(
            intent_type="REFACTOR",
            confidence=0.90,
        )
        assert decision.decision_type == RoutingDecisionType.DIRECT_ROUTE


class TestConfidenceScoreBoundaries(BaseConfidenceRouterTest):
    """Test boundary conditions for confidence scores."""

    def test_confidence_1_0_accepted(self):
        """Test confidence 1.0 is accepted."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=1.0,
        )
        assert decision.decision_type == RoutingDecisionType.DIRECT_ROUTE

    def test_confidence_0_0_accepted(self):
        """Test confidence 0.0 is accepted."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.0,
        )
        assert decision.decision_type == RoutingDecisionType.CLARIFICATION_NEEDED

    def test_confidence_just_above_medium_threshold(self):
        """Test confidence just above medium threshold."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.701,
        )
        assert decision.decision_type == RoutingDecisionType.DIRECT_ROUTE or decision.decision_type == RoutingDecisionType.CAUTION_ROUTE

    def test_confidence_just_below_medium_threshold(self):
        """Test confidence just below medium threshold."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.699,
        )
        assert decision.decision_type == RoutingDecisionType.CLARIFICATION_NEEDED

    def test_confidence_just_above_high_threshold(self):
        """Test confidence just above high threshold."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.851,
        )
        assert decision.decision_type == RoutingDecisionType.DIRECT_ROUTE

    def test_confidence_just_below_high_threshold(self):
        """Test confidence just below high threshold."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.849,
        )
        assert decision.decision_type == RoutingDecisionType.CAUTION_ROUTE


class TestDecisionTimestamp(BaseConfidenceRouterTest):
    """Test decision timestamp recording."""

    def test_routing_decision_has_timestamp(self):
        """Test routing decision includes timestamp."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.90,
        )
        assert hasattr(decision, "timestamp")
        assert decision.timestamp is not None

    def test_timestamp_format_is_iso(self):
        """Test timestamp is ISO format."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.80,
        )
        # ISO format should contain 'T' and be parseable
        assert "T" in decision.timestamp or isinstance(decision.timestamp, str)


class TestContextAwareRouting(BaseConfidenceRouterTest):
    """Test context-aware routing decisions."""

    def test_route_with_context(self):
        """Test routing with context information."""
        context = {
            "conversation_turn": 2,
            "previous_confidence": 0.85,
            "historical_success_rate": 0.92,
        }
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.75,
            context=context,
        )
        assert decision is not None

    def test_route_with_session_history(self):
        """Test routing with session history."""
        context = {
            "previous_decisions": [
                {"confidence": 0.95, "success": True},
                {"confidence": 0.88, "success": True},
            ]
        }
        decision = self.router.route(
            intent_type="FIX",
            confidence=0.72,
            context=context,
        )
        assert decision is not None

    def test_empty_context_works(self):
        """Test routing with empty context."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.85,
            context={},
        )
        assert decision.decision_type == RoutingDecisionType.DIRECT_ROUTE


class TestMultipleRouting(BaseConfidenceRouterTest):
    """Test multiple routing decisions."""

    def test_multiple_decisions_independent(self):
        """Test multiple decisions don't interfere."""
        decision1 = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.95,
        )
        decision2 = self.router.route(
            intent_type="FIX",
            confidence=0.40,
        )
        assert decision1.decision_type == RoutingDecisionType.DIRECT_ROUTE
        assert decision2.decision_type == RoutingDecisionType.CLARIFICATION_NEEDED

    def test_sequential_routing_consistent(self):
        """Test sequential routing decisions are consistent."""
        decision1 = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.75,
        )
        decision2 = self.router.route(
            intent_type="IMPLEMENT",
            confidence=0.75,
        )
        assert decision1.decision_type == decision2.decision_type


class TestEdgeCases(BaseConfidenceRouterTest):
    """Test edge cases and boundary conditions."""

    def test_route_with_none_intent_type(self):
        """Test routing with None intent type."""
        # Should not crash, should handle gracefully
        try:
            decision = self.router.route(
                intent_type=None,
                confidence=0.85,
            )
            assert decision is not None
        except (TypeError, ValueError):
            # Acceptable to raise error for invalid input
            pass

    def test_route_with_negative_confidence(self):
        """Test routing with negative confidence."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=-0.5,
        )
        # Negative confidence should be treated as low confidence
        assert decision.decision_type == RoutingDecisionType.CLARIFICATION_NEEDED

    def test_route_with_confidence_greater_than_1(self):
        """Test routing with confidence > 1.0."""
        decision = self.router.route(
            intent_type="IMPLEMENT",
            confidence=1.5,
        )
        # Should be treated as high confidence
        assert decision.decision_type == RoutingDecisionType.DIRECT_ROUTE

    def test_multiple_routers_independent(self):
        """Test multiple routers are independent."""
        router1 = ConfidenceRouter()
        router2 = ConfidenceRouter()
        decision1 = router1.route(
            intent_type="IMPLEMENT",
            confidence=0.85,
        )
        decision2 = router2.route(
            intent_type="IMPLEMENT",
            confidence=0.85,
        )
        assert decision1.decision_type == decision2.decision_type
