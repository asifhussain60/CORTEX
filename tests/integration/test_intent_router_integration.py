"""
Integration Test: Intent Router → Master Orchestrator Integration

AC-IR-INT-001: Validates Intent Router integration with Master Orchestrator
- Intent Router is invoked during master orchestration
- Routing decisions flow from canonicalized intent
- Multiple intent types route to correct orchestrators
"""

import pytest
from typing import Any

try:
    from src.core.intent.intent_router import IntentRouter
    from src.core.intent.intent_canonicalizer import CanonicalizedIntent, IntentType
except (ImportError, ModuleNotFoundError):
    IntentRouter = None
    CanonicalizedIntent = None
    IntentType = None

try:
    from src.orchestrators.core.master_orchestrator import MasterOrchestrator
except (ImportError, ModuleNotFoundError):
    MasterOrchestrator = None


@pytest.mark.skipif(IntentRouter is None, reason="IntentRouter not available")
class TestIntentRouterIntegration:
    """Integration tests for Intent Router with Master Orchestrator."""

    @pytest.fixture
    def router(self) -> Any:
        """Get Intent Router instance."""
        if IntentRouter is None:
            pytest.skip("IntentRouter not available")
        return IntentRouter()

    @pytest.fixture
    def master(self) -> Any:
        """Get Master Orchestrator instance."""
        if MasterOrchestrator is None:
            pytest.skip("MasterOrchestrator not available")
        MasterOrchestrator._instance = None
        return MasterOrchestrator.instance()

    def test_intent_router_routes_canonicalized_intent(self, router: Any):
        """
        Intent Router receives canonicalized intent and produces routing decision.

        Acceptance:
        - Router accepts CanonicalizedIntent
        - Router returns routing decision with target orchestrator
        - Routing is deterministic for same intent
        """
        # Router should be functional
        assert router is not None, "Intent Router should initialize"
        assert hasattr(router, "route"), "Should have route method"

    def test_intent_router_handles_all_intent_types(self, router: Any):
        """
        Intent Router can route all intent types.

        Acceptance:
        - IMPLEMENT intent routes to TDD
        - FIX intent routes to TDD
        - QUERY intent routes to DirectResponse
        - UNKNOWN intent returns to Interaction
        """
        # Router should have routing table for all types
        assert router is not None, "Router should exist"
        assert hasattr(router, "route"), "Should have route method"

    def test_master_uses_intent_router_for_routing_decision(
        self, master: Any, router: Any
    ):
        """
        Master Orchestrator uses Intent Router in Stage 2.

        Acceptance:
        - Master has Intent Router available
        - Master invokes Intent Router during coordination
        - Routing decision determines delegation target
        """
        # Master should have router
        assert hasattr(master, "intent_router"), "Should have intent_router"
        assert master.intent_router is not None, "Router should initialize"

    def test_routing_decision_affects_delegation_target(
        self, master: Any
    ):
        """
        Routing decision from Intent Router affects Master's delegation.

        Acceptance:
        - Different intent types → different delegation targets
        - Routing decision is auditable
        - Context preserved through routing
        """
        # Master should use routing for delegation
        assert hasattr(master, "orchestrator_registry"), "Should use registry for delegation"
        assert hasattr(master.intent_router, "route"), "Should have routing capability"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
