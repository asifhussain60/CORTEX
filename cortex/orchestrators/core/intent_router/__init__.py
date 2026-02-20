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

__all__ = [
    "WorkflowComplexityRouter",
    "Intent",
    "RoutingDecision",
    "RoutingStrategy",
    "ComplexityThreshold",
    "IntentRouter",
    "EnhancedIntentRouter",
]
