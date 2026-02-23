"""COMPAT shim — cortex.core.registry.status_update_hook → cortex.infrastructure.automation.status_update_hook.

Phase 58-B: zero-import duplicate. Canonical implementation at cortex/infrastructure/automation/status_update_hook.py.
"""
# noqa: F401
from cortex.infrastructure.automation.status_update_hook import StatusUpdateHook

__all__ = ["StatusUpdateHook"]
