"""
cortex.intent_router — Public intent routing API for CORTEX.

Exports the WorkflowComplexityRouter and related types for use by
MasterOrchestrator and other orchestrators needing complexity-gated routing.

Authority: WORKFLOW-COMPLEXITY-GATE-001, CORE-035
Canonical source: cortex.orchestrators.core.intent_router.workflow_gate
"""

from cortex.orchestrators.core.intent_router.workflow_gate import (
    WorkflowComplexityRouter,
    Intent,
    RoutingDecision,
    RoutingStrategy,
    ComplexityThreshold,
)
from cortex.orchestrators.core.intent_router import IntentRouter, EnhancedIntentRouter

__all__ = [
    "WorkflowComplexityRouter",
    "Intent",
    "RoutingDecision",
    "RoutingStrategy",
    "ComplexityThreshold",
    "IntentRouter",
    "EnhancedIntentRouter",
]
