"""Intent Router - Complexity-Gated Workflow Routing."""

import logging

from cortex.orchestrators.core.intent_router.workflow_gate import (
    WorkflowComplexityRouter,
    Intent,
    RoutingDecision,
    RoutingStrategy,
    ComplexityThreshold,
)

# GAP-57-09: Wire StrategySelector into IntentRouter for routing confidence (Phase 57-f)
try:
    from cortex.intelligence.reasoning.strategy_selector import StrategySelector
    _strategy_selector = StrategySelector()
except ImportError:
    logging.getLogger(__name__).warning(
        "Optional cortex dependency unavailable: "
        "cortex.intelligence.reasoning.strategy_selector — feature degraded"
    )
    StrategySelector = None  # type: ignore[assignment,misc]
    _strategy_selector = None

# IntentRouter: canonical alias to WorkflowComplexityRouter (CORE-035)
IntentRouter = WorkflowComplexityRouter
EnhancedIntentRouter = WorkflowComplexityRouter  # backward-compat alias

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
            """Initialize empty orchestrator registry."""
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
    "StrategySelector",
    "get_registry_intelligence_agent",
]
