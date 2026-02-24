"""CORTEX Decorators module.

Provides decorator utilities for marking and registering orchestrators,
governance enforcement, and other framework decorators.

Author: CORTEX Framework
# COMPAT: 2026-02-24 (Phase 68-B) — orchestrator_decorator.py moved to cortex.core.common
"""

from cortex.core.common.orchestrator_decorator import (
    clear_orchestrator_registry,
    get_orchestrator_by_domain,
    get_orchestrators_by_domain,
    get_registered_orchestrators,
    is_orchestrator,
    orchestrator,
)

__all__ = [
    "orchestrator",
    "get_registered_orchestrators",
    "get_orchestrator_by_domain",
    "get_orchestrators_by_domain",
    "is_orchestrator",
    "clear_orchestrator_registry",
]
