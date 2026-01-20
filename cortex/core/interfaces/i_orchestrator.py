"""IOrchestrator Interface - Core orchestrator interface definition.

Provides lazy-loaded access to IOrchestrator and OrchestratorBase.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

def __getattr__(name):
    """Lazy load from parent interfaces module."""
    if name in ("IOrchestrator", "OrchestratorBase"):
        # Import on demand to avoid circular imports
        import sys
        parent = sys.modules.get("cortex.core.interfaces")
        if parent and hasattr(parent, name):
            return getattr(parent, name)
        # Fall back to loading from parent module directly
        from .. import interfaces as parent_mod
        return getattr(parent_mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["IOrchestrator", "OrchestratorBase"]
