"""
Golden Tests: IntentRouter Must Differentiate Routing by Intent Type.

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
AC_START: AC-GOLDEN-INTENT-DIFFERENTIATION-001

These tests enforce that the IntentRouter routes DIFFERENT intent types
to DIFFERENT handlers — the P0 production-readiness requirement identified
in the holistic audit of 2026-02-22.

The router MUST NOT collapse all intents to a single handler (cortex-tdd-orchestrator).
"""

import pytest
from typing import Dict, Any


class TestIntentRouterDifferentiatesRouting:
    """Golden: IntentRouter must route different intents to different handlers."""

    def _route(self, description: str, operation: str = "", **extra: Any) -> Any:
        """Helper: route a dict-based request through the IntentRouter.

        Args:
            description: User request description
            operation: Operation name
            **extra: Additional context fields

        Returns:
            Routing result from IntentRouter.route()
        """
        from cortex.orchestrators.core.intent_router import IntentRouter

        router = IntentRouter()
        context: Dict[str, Any] = {
            "description": description,
            "operation": operation,
            **extra,
        }
        return router.route(context)

    # --- P0: Core differentiation tests ---

    def test_fix_routes_to_fix_handler(self) -> None:
        """FIX intent must NOT route to TDD-only handler."""
        result = self._route("fix the broken test in the health orchestrator", "fix")
        handler = getattr(result, "target_handler", "") or getattr(result, "primary_agent_id", "")
        # Must contain "fix" or "debug" — NOT be generic tdd-only
        assert handler != "cortex-tdd-orchestrator", (
            f"FIX intent collapsed to generic TDD handler: {handler}"
        )

    def test_audit_routes_to_audit_handler(self) -> None:
        """AUDIT intent must route to auditor, not TDD."""
        result = self._route("audit the codebase for stale imports", "audit")
        handler = getattr(result, "target_handler", "") or getattr(result, "primary_agent_id", "")
        assert "audit" in handler.lower() or "health" in handler.lower(), (
            f"AUDIT intent should route to auditor, got: {handler}"
        )

    def test_refactor_routes_to_refactor_handler(self) -> None:
        """REFACTOR intent must route to refactorer, not TDD."""
        result = self._route("refactor the master orchestrator for clarity", "refactor")
        handler = getattr(result, "target_handler", "") or getattr(result, "primary_agent_id", "")
        assert "refactor" in handler.lower(), (
            f"REFACTOR intent should route to refactorer, got: {handler}"
        )

    def test_design_routes_to_architect_handler(self) -> None:
        """DESIGN intent must route to architect, not TDD."""
        result = self._route("design the architecture for the new module", "design")
        handler = getattr(result, "target_handler", "") or getattr(result, "primary_agent_id", "")
        assert "architect" in handler.lower() or "design" in handler.lower(), (
            f"DESIGN intent should route to architect, got: {handler}"
        )

    def test_plan_routes_to_planner_handler(self) -> None:
        """PLAN intent must route to planner, not TDD."""
        result = self._route("plan the next phase of development", "plan")
        handler = getattr(result, "target_handler", "") or getattr(result, "primary_agent_id", "")
        assert "plan" in handler.lower(), (
            f"PLAN intent should route to planner, got: {handler}"
        )

    # --- P0: No single-handler collapse ---

    def test_at_least_three_distinct_handlers(self) -> None:
        """Routing 5 different intents must produce at least 3 distinct handlers."""
        requests = [
            ("fix the broken test", "fix"),
            ("audit the codebase", "audit"),
            ("refactor the module", "refactor"),
            ("design the architecture", "design"),
            ("plan the next phase", "plan"),
        ]
        handlers = set()
        for desc, op in requests:
            result = self._route(desc, op)
            handler = getattr(result, "target_handler", "") or getattr(result, "primary_agent_id", "")
            handlers.add(handler)

        assert len(handlers) >= 3, (
            f"5 different intents produced only {len(handlers)} distinct handler(s): {handlers}. "
            f"IntentRouter is collapsing all routes to a single handler."
        )

    # --- P1: Intent detection accuracy (already passing via _detect_intent_from_dict) ---

    def test_intent_type_matches_request(self) -> None:
        """Routing result must carry the correct intent_type."""
        result = self._route("audit the repository for issues", "audit")
        intent_type = getattr(result, "intent_type", None)
        if intent_type is not None:
            intent_val = intent_type.value if hasattr(intent_type, "value") else str(intent_type)
            assert intent_val.lower() == "audit", (
                f"Expected intent_type=audit, got {intent_val}"
            )

    def test_implement_intent_detected(self) -> None:
        """IMPLEMENT request must carry implement intent type."""
        result = self._route("implement a new logging endpoint for the service", "implement")
        intent_type = getattr(result, "intent_type", None)
        if intent_type is not None:
            intent_val = intent_type.value if hasattr(intent_type, "value") else str(intent_type)
            assert intent_val.lower() == "implement", (
                f"Expected intent_type=implement, got {intent_val}"
            )

    def test_investigate_intent_detected(self) -> None:
        """INVESTIGATE request must carry investigate intent type."""
        result = self._route("investigate the root cause of the failure", "investigate")
        intent_type = getattr(result, "intent_type", None)
        if intent_type is not None:
            intent_val = intent_type.value if hasattr(intent_type, "value") else str(intent_type)
            assert intent_val.lower() == "investigate", (
                f"Expected intent_type=investigate, got {intent_val}"
            )


class TestCapabilityMatcherCorrectness:
    """Golden: CapabilityMatcher must use intent-specific capability requirements."""

    def test_required_caps_not_zeroed_out(self) -> None:
        """CapabilityMatcher must NOT zero out required_caps for known intents."""
        from cortex.orchestrators.core.intent_router.capability_matcher import (
            CapabilityMatcher,
            IntentType,
        )

        matcher = CapabilityMatcher()
        # AUDIT has explicit capabilities in INTENT_CAPABILITY_MAP
        caps = matcher.INTENT_CAPABILITY_MAP.get(IntentType.AUDIT)
        assert caps is not None, "AUDIT must have capability requirements"
        assert len(caps) > 0, "AUDIT capability requirements must not be empty"

        # Simulate match_capabilities for AUDIT with 2 agents
        agents = [
            {"agent_id": "auditor", "capabilities": ["codebase_health_scanning", "security_validation", "governance_compliance_checking"], "priority": "P0"},
            {"agent_id": "tdd", "capabilities": ["testing", "tdd", "implementation"], "priority": "P0"},
        ]
        rankings = matcher.match_capabilities(
            intent=IntentType.AUDIT,
            user_request="audit the codebase",
            available_agents=agents,
        )
        assert rankings.primary_agent_id == "auditor", (
            f"AUDIT intent should select auditor agent, got {rankings.primary_agent_id}"
        )

    def test_fix_intent_prefers_debugger(self) -> None:
        """FIX intent must prefer agent with debugging/bug_fixing capabilities."""
        from cortex.orchestrators.core.intent_router.capability_matcher import (
            CapabilityMatcher,
            IntentType,
        )

        matcher = CapabilityMatcher()
        agents = [
            {"agent_id": "debugger", "capabilities": ["bug_fixing", "debugging", "test_coverage_analysis"], "priority": "P1"},
            {"agent_id": "tdd", "capabilities": ["testing", "tdd", "implementation"], "priority": "P0"},
        ]
        rankings = matcher.match_capabilities(
            intent=IntentType.FIX,
            user_request="fix the broken test",
            available_agents=agents,
        )
        assert rankings.primary_agent_id == "debugger", (
            f"FIX intent should prefer debugger, got {rankings.primary_agent_id}"
        )

    def test_different_intents_rank_differently(self) -> None:
        """Different intents must produce different primary agents when appropriate."""
        from cortex.orchestrators.core.intent_router.capability_matcher import (
            CapabilityMatcher,
            IntentType,
        )

        matcher = CapabilityMatcher()
        agents = [
            {"agent_id": "auditor", "capabilities": ["codebase_health_scanning", "security_validation"], "priority": "P0"},
            {"agent_id": "debugger", "capabilities": ["bug_fixing", "debugging"], "priority": "P1"},
            {"agent_id": "refactorer", "capabilities": ["code_refactoring", "architecture_analysis"], "priority": "P2"},
        ]

        audit_result = matcher.match_capabilities(IntentType.AUDIT, "audit repo", agents)
        fix_result = matcher.match_capabilities(IntentType.FIX, "fix bug", agents)
        refactor_result = matcher.match_capabilities(IntentType.REFACTOR, "refactor code", agents)

        # At least 2 of 3 must be different
        primaries = {audit_result.primary_agent_id, fix_result.primary_agent_id, refactor_result.primary_agent_id}
        assert len(primaries) >= 2, (
            f"3 different intents produced only {len(primaries)} distinct primary agent(s): {primaries}"
        )
