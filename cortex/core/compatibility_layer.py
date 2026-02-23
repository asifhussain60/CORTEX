"""COMPAT shim — cortex.core.compatibility_layer → cortex.core.core.compatibility_layer.

Phase 58: Canonical implementation lives in cortex/core/core/compatibility_layer.py.
This stub is kept for import-path compatibility.
"""
# noqa: F401
from cortex.core.core.compatibility_layer import SchemaVersion, CompatibilityMode, SchemaMapping, FormatProfile, CompatibilityLayer

__all__ = ["SchemaVersion", "CompatibilityMode", "SchemaMapping", "FormatProfile", "CompatibilityLayer"]
