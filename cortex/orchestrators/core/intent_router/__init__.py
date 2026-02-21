"""Intent Router - Complexity-Gated Workflow Routing."""

from cortex.orchestrators.core.intent_router.workflow_gate import (
    WorkflowComplexityRouter,
    Intent,
    RoutingDecision,
    RoutingStrategy,
    ComplexityThreshold,
)

try:
    from cortex.orchestrators.core.intent_router.router import EnhancedIntentRouter  # type: ignore
    # Alias for backward compat — callers using IntentRouter get the enhanced version
    IntentRouter = EnhancedIntentRouter
except ImportError:
    pass

try:
    from cortex.orchestrators.core.intent_router.routing_enforcement import RoutingEnforcementEngine  # type: ignore
except ImportError:
    class RoutingEnforcementEngine:
        """Stub for backward compatibility."""
        pass

try:
    from cortex.orchestrators.core.intent_router.orchestrator_lookup import OrchestratorLookup  # type: ignore
except ImportError:
    class OrchestratorLookup:
        """Stub for backward compatibility."""
        def __init__(self) -> None:
            self._registry: dict = {}
        def lookup(self, name: str) -> None:
            """Look up an orchestrator by name from the registry."""
            return self._registry.get(name)


def get_registry_intelligence_agent() -> None:
    """Stub for backward compatibility — returns None."""
    return None


__all__ = [
    "WorkflowComplexityRouter",
    "Intent",
    "RoutingDecision",
    "RoutingStrategy",
    "ComplexityThreshold",
    "IntentRouter",
    "EnhancedIntentRouter",
    "OrchestratorLookup",
    "RoutingEnforcementEngine",
    "get_registry_intelligence_agent",
]
