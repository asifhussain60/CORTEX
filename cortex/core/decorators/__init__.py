"""CORTEX Decorators module.

Provides decorator utilities for marking and registering orchestrators,
governance enforcement, and other framework decorators.

Author: CORTEX Framework
"""

from cortex.core.decorators.orchestrator_decorator import (
    orchestrator,
    get_registered_orchestrators,
    get_orchestrator_by_domain,
    get_orchestrators_by_domain,
    is_orchestrator,
    clear_orchestrator_registry,
)

__all__ = [
    "orchestrator",
    "get_registered_orchestrators",
    "get_orchestrator_by_domain",
    "get_orchestrators_by_domain",
    "is_orchestrator",
    "clear_orchestrator_registry",
]
