"""
CORTEX Wiring System - Git-backed YAML orchestrator configuration.

Authority: cortex-registry/planning/phases/completed/2025/ (Phase 3)
Rule: CORE-035 (Single Canonical Implementation)

This is the SINGLE SOURCE OF TRUTH for orchestrator wiring.
All orchestrator registration comes from cortex/core/wiring/specifications/wiring.yaml.

Example:
    >>> from cortex.core.wiring import bootstrap_cortex, get_cortex
    >>> registry = bootstrap_cortex()  # Initialize system
    >>> orch = registry.get_orchestrator("TDDOrchestrator")
    >>> result = orch.generate_tests(...)

    # Check if wired
    >>> from cortex.core.wiring import is_wired
    >>> if not is_wired():
    ...     bootstrap_cortex()

    # Get wiring hash for change detection
    >>> from cortex.core.wiring import get_wiring_hash
    >>> hash_value = get_wiring_hash()
"""

from cortex.core.wiring.wiring_bootstrap import (
    bootstrap_cortex,
    get_cortex,
    get_wiring_hash,
    is_wired,
)

# Alias for backward compatibility (tests import wiring_bootstrap_cortex)
wiring_bootstrap_cortex = bootstrap_cortex
from cortex.core.wiring.registry import (
    GitBackedRegistry,
    LazyOrchestrator,
    WiringValidator,
    get_registry,
    validate_wiring,
)

__all__ = [
    # Bootstrap functions (primary API)
    "bootstrap_cortex",
    "wiring_bootstrap_cortex",  # alias for bootstrap_cortex
    "get_cortex",
    "is_wired",
    "get_wiring_hash",

    # Registry classes (advanced usage)
    "GitBackedRegistry",
    "LazyOrchestrator",
    "WiringValidator",
    "get_registry",
    "validate_wiring",
]

