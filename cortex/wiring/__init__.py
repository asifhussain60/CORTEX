"""
cortex.wiring — Public wiring API for CORTEX bootstrap system.

This package provides the canonical entry points for bootstrapping
the CORTEX orchestrator wiring system.

Authority: CORE-035 (Single Canonical Implementation)
Canonical source: cortex.core.wiring.wiring_bootstrap
"""

from cortex.core.wiring.wiring_bootstrap import (
    bootstrap_cortex,
    get_cortex,
    is_wired,
    get_wiring_hash,
)
from cortex.core.wiring.registry import get_registry, GitBackedRegistry

# Alias for backward compatibility with tests and legacy callers
wiring_bootstrap_cortex = bootstrap_cortex

__all__ = [
    "wiring_bootstrap_cortex",
    "bootstrap_cortex",
    "get_cortex",
    "is_wired",
    "get_wiring_hash",
    "get_registry",
    "GitBackedRegistry",
]
