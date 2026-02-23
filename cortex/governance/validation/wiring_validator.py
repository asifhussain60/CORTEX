"""COMPAT shim — cortex.governance.validation.wiring_validator → cortex.core.wiring.registry.wiring_validator.

Phase 58-B: zero-import duplicate. Canonical implementation at cortex/core/wiring/registry/wiring_validator.py.
"""
# noqa: F401
from cortex.core.wiring.registry.wiring_validator import WiringValidator, validate_wiring

__all__ = ["WiringValidator", "validate_wiring"]
