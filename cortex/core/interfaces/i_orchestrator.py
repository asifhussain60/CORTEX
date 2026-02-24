"""COMPAT shim — i_orchestrator merged into cortex.core.interfaces (Phase 60)."""
from cortex.core.interfaces import IOrchestrator, OperationMode  # noqa: F401

__all__ = ["IOrchestrator", "OperationMode"]
