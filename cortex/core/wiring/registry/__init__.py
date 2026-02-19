"""
Wiring Registry - Git-backed orchestrator registry.

Authority: cortex-registry/planning/phases/completed/2025/ (Phase 3)
"""

from cortex.core.wiring.registry.git_backed_registry import (
    GitBackedRegistry,
    get_registry,
    reset_registry,
)
from cortex.core.wiring.registry.lazy_orchestrator import LazyOrchestrator
from cortex.core.wiring.registry.wiring_validator import WiringValidator, validate_wiring

__all__ = [
    "GitBackedRegistry",
    "get_registry",
    "reset_registry",
    "LazyOrchestrator",
    "WiringValidator",
    "validate_wiring",
]
