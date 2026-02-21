"""
Backward-compatibility re-export.

The canonical implementation is now in service_decomposition_orchestrator.py.
This module will be removed in Phase 14 completion.
"""
from cortex.orchestrators.domain.service_decomposition_orchestrator import (
    ServiceDecompositionOrchestrator,
    _NoOpWorkflowEngine,
    _SUPPORTED_INTENTS,
)

# Backward-compat alias — existing code importing LegacyModernizationOrchestrator
# will continue to work until all references are migrated.
LegacyModernizationOrchestrator = ServiceDecompositionOrchestrator

__all__ = [
    "LegacyModernizationOrchestrator",
    "ServiceDecompositionOrchestrator",
]
