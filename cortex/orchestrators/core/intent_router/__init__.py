"""Intent Router — package init with correct re-exports.

Re-exports the canonical IntentRouter from intent_router_impl.py
alongside the WorkflowComplexityRouter from workflow_gate.py.

Phase 70 Fix: GAP-70-A1 — resolved IntentRouter identity collapse
where IntentRouter was aliased to WorkflowComplexityRouter.
"""

import logging

from cortex.orchestrators.core.intent_router.workflow_gate import (
    WorkflowComplexityRouter,
    Intent,
    RoutingDecision as WorkflowRoutingDecision,
    RoutingStrategy,
    ComplexityThreshold,
)

# Import the REAL IntentRouter from the renamed implementation file
try:
    from ..intent_router_impl import (
        IntentRouter,
        IntentType,
        RoutingDecision,
    )
except ImportError:
    # Fallback: if intent_router_impl doesn't exist, use WorkflowComplexityRouter.
    # CORE-035: ensure RoutingDecision and IntentType are always exported so that
    # callers (e.g. health_check_service) don't fail with NameError/ImportError.
    logging.getLogger(__name__).error(
        "CRITICAL: cortex.orchestrators.core.intent_router_impl not found — "
        "IntentRouter will be degraded to WorkflowComplexityRouter"
    )
    IntentRouter = WorkflowComplexityRouter  # type: ignore[assignment,misc]
    # Re-export WorkflowRoutingDecision as RoutingDecision so the name is always available
    RoutingDecision = WorkflowRoutingDecision  # type: ignore[assignment,misc]
    # Provide a minimal IntentType enum stub so imports never fail
    from enum import Enum
    class IntentType(str, Enum):  # type: ignore[no-redef]
        """Fallback IntentType when intent_router_impl is unavailable."""
        UNKNOWN = "UNKNOWN"

# EnhancedIntentRouter is the same as IntentRouter (backward compat)
EnhancedIntentRouter = IntentRouter  # type: ignore[assignment,misc]

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

try:
    from cortex.orchestrators.core.intent_router.routing_enforcement import RoutingEnforcementEngine  # type: ignore
except ImportError:
    class RoutingEnforcementEngine:  # type: ignore[no-redef]
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
    "IntentType",
    "EnhancedIntentRouter",
    "OrchestratorLookup",
    "RoutingEnforcementEngine",
    "StrategySelector",
    "get_registry_intelligence_agent",
]
