"""COMPAT shim — cortex.core.bootstrap.orchestrator_factory → cortex.core.wiring.orchestrator_factory.

Phase 58-B: zero-import duplicate. Canonical implementation at cortex/core/wiring/orchestrator_factory.py.
"""
# noqa: F401
from cortex.core.wiring.orchestrator_factory import OrchestrationSpec, OrchestrationContext, WiringSpecification, OrchestratorFactory, OrchestrationBootstrap, initialize_orchestration, get_orchestrator, get_event_bus

__all__ = ["OrchestrationSpec", "OrchestrationContext", "WiringSpecification", "OrchestratorFactory", "OrchestrationBootstrap", "initialize_orchestration", "get_orchestrator", "get_event_bus"]
