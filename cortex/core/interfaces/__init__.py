"""Core Interfaces Package - Central location for core interface definitions.

Re-exports interfaces from parent module via i_orchestrator submodule.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

# Lazy imports to avoid circular dependency
def __getattr__(name):
    """Lazy load interfaces to avoid circular imports."""
    if name == "IOrchestrator":
        from ..interfaces import IOrchestrator
        return IOrchestrator
    elif name == "OrchestratorBase":
        from ..interfaces import OrchestratorBase
        return OrchestratorBase
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["IOrchestrator", "OrchestratorBase"]
