"""
DEPRECATED: LENSOrchestrator moved to cortex.lens

This module has been relocated as part of LENS consolidation (2026-02-02).

OLD LOCATION: cortex.orchestrators.support.lens_orchestrator
NEW LOCATION: cortex.lens.orchestrator

MIGRATION:
  OLD: from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
  NEW: from cortex.lens import LENSOrchestrator

This stub will be removed in next sprint. Update your imports now.

Authority: CORE-035 (Consolidation), ARCH-006 (No backward compatibility)
"""

import warnings


def __getattr__(name):
    """Deprecation handler for old imports."""
    warnings.warn(
        f"Importing {name} from cortex.orchestrators.support.lens_orchestrator is deprecated. "
        f"Use 'from cortex.lens import {name}' instead. "
        "This stub will be removed in next sprint.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Forward to new location
    if name == "LENSOrchestrator":
        from cortex.lens import LENSOrchestrator
        return LENSOrchestrator
    elif name == "LENSContext":
        from cortex.lens.orchestrator import LENSContext
        return LENSContext
    else:
        raise AttributeError(f"module 'cortex.orchestrators.support.lens_orchestrator' has no attribute '{name}'")
