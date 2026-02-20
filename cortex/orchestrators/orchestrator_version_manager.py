"""
orchestrator_version_manager — re-export shim.

The canonical implementation lives in
``cortex.orchestrators.version_manager`` so that tests patching
``cortex.orchestrators.version_manager.requests`` intercept the
module-level ``requests`` reference correctly.

Authority: CORE-035 (single canonical implementation)
"""
from cortex.orchestrators.version_manager import VersionManager  # noqa: F401

__all__ = ["VersionManager"]
