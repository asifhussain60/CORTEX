"""
cortex.registry — Registry access layer for CORTEX.

Provides access to the cortex-registry YAML store for governance rules,
orchestrator manifests, and knowledge base entries.

Authority: CORE-035 (Single Canonical Implementation)
"""

from pathlib import Path

# Root of the cortex-registry YAML store
REGISTRY_ROOT = Path(__file__).parent.parent.parent / "cortex-registry"


def get_registry_root() -> Path:
    """Return the path to the cortex-registry YAML store.

    Returns:
        Path to cortex-registry directory.
    """
    return REGISTRY_ROOT


__all__ = [
    "REGISTRY_ROOT",
    "get_registry_root",
]
