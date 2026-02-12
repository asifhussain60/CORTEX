"""
CORTEX Wiring System - Git-backed YAML orchestrator configuration.

Authority: cortex-registry/_cortex-master/phases/completed/2025/ (Phase 3)
Rule: CORE-035 (Single Canonical Implementation)

This is the SINGLE SOURCE OF TRUTH for orchestrator wiring.
All orchestrator registration comes from cortex/wiring/specifications/wiring.yaml.

Example:
    >>> from cortex.wiring import bootstrap_cortex, get_cortex
    >>> registry = bootstrap_cortex()  # Initialize system
    >>> orch = registry.get_orchestrator("TDDOrchestrator")
    >>> result = orch.generate_tests(...)

    # Check if wired
    >>> from cortex.wiring import is_wired
    >>> if not is_wired():
    ...     bootstrap_cortex()

    # Get wiring hash for change detection
    >>> from cortex.wiring import get_wiring_hash
    >>> hash_value = get_wiring_hash()
"""

from cortex.wiring.bootstrap import (
    bootstrap_cortex,
    get_cortex,
    get_wiring_hash,
    is_wired,
)
from cortex.wiring.registry import (
    GitBackedRegistry,
    LazyOrchestrator,
    WiringValidator,
    get_registry,
    validate_wiring,
)

__all__ = [
    # Bootstrap functions (primary API)
    "bootstrap_cortex",
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

__version__ = "2.0.0"
__author__ = "Asif Hussain"
