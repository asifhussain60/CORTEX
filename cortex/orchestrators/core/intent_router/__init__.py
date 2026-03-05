"""Intent Router — package init with correct re-exports.

Re-exports the canonical IntentRouter from intent_router_impl.py
alongside the WorkflowComplexityRouter from workflow_gate.py.

Phase 70 Fix: GAP-70-A1 — resolved IntentRouter identity collapse
where IntentRouter was aliased to WorkflowComplexityRouter.
"""

import logging
import importlib

from cortex.orchestrators.core.intent_router.workflow_gate import (
    WorkflowComplexityRouter,
    Intent,
    RoutingDecision as WorkflowRoutingDecision,
    RoutingStrategy,
    ComplexityThreshold,
)

# Lazy resolution for IntentRouter, IntentType, RoutingDecision.
# intent_router_impl imports from this package (circular), so we defer
# the reverse import until first attribute access (PEP 562).
_LAZY_NAMES = {"IntentRouter", "IntentType", "RoutingDecision", "EnhancedIntentRouter"}
_resolved = False


def _resolve_impl() -> None:
    """One-shot resolution of intent_router_impl exports."""
    global _resolved  # noqa: PLW0603
    if _resolved:
        return
    _resolved = True
    try:
        _mod = importlib.import_module("cortex.orchestrators.core.intent_router_impl")
        globals()["IntentRouter"] = getattr(_mod, "IntentRouter", WorkflowComplexityRouter)
        globals()["IntentType"] = getattr(_mod, "IntentType", None)
        globals()["RoutingDecision"] = getattr(_mod, "RoutingDecision", WorkflowRoutingDecision)
        globals()["EnhancedIntentRouter"] = globals()["IntentRouter"]
    except ImportError:
        logging.getLogger(__name__).error(
            "CRITICAL: cortex.orchestrators.core.intent_router_impl not found — "
            "IntentRouter will be degraded to WorkflowComplexityRouter"
        )
        globals()["IntentRouter"] = WorkflowComplexityRouter
        globals()["RoutingDecision"] = WorkflowRoutingDecision
        globals()["EnhancedIntentRouter"] = WorkflowComplexityRouter
        from enum import Enum
        class _FallbackIntentType(str, Enum):
            UNKNOWN = "UNKNOWN"
        globals()["IntentType"] = _FallbackIntentType


def __getattr__(name: str):
    """PEP 562 lazy attribute resolution for circular-import-safe re-exports."""
    if name in _LAZY_NAMES:
        _resolve_impl()
        if name in globals():
            return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

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
    class RoutingEnforcementEngine:  # type: ignore[no-redef]  # CORE-035-scoped — domain-specific variant
        """Stub for backward compatibility."""
        pass

try:
    from cortex.orchestrators.core.intent_router.orchestrator_lookup import OrchestratorLookup  # type: ignore
except ImportError:
    class OrchestratorLookup:  # CORE-035-scoped — domain-specific variant
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


from cortex.orchestrators.core.intent_router.keyword_registry import IntentKeywordRegistry
from cortex.orchestrators.core.intent_router.lens_analysis_mixin import LensAnalysisMixin
from cortex.orchestrators.core.intent_router.registry_intelligence_mixin import RegistryIntelligenceMixin
from cortex.orchestrators.core.intent_router.routing_core_mixin import RoutingCoreMixin
from cortex.orchestrators.core.intent_router.smart_citations_mixin import SmartCitationsMixin

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
    # Phase 103-b: decomposed mixin modules
    "IntentKeywordRegistry",
    "LensAnalysisMixin",
    "RegistryIntelligenceMixin",
    "RoutingCoreMixin",
    "SmartCitationsMixin",
]
