"""CORTEX Bootstrap Module

Orchestrator factory and runtime initialization for CORTEX ecosystem.

Phase 9: Orchestrator Instantiation & Runtime Wiring

This module provides:
- OrchestratorFactory: Main factory for instantiating orchestrators with dependency injection
- CircularDependencyDetector: Kahn's algorithm for cycle detection in orchestrator DAG
- DependencyResolver: Topological sort for correct instantiation order
- Comprehensive error handling and audit trail logging
"""

from cortex.bootstrap.orchestrator_factory import (
    OrchestratorFactory,
    CircularDependencyDetector,
    DependencyResolver,
)

__all__ = [
    "OrchestratorFactory",
    "CircularDependencyDetector",
    "DependencyResolver",
    "create_cortex_runtime",
]
