"""COMPAT shim — cortex.core.coherence_validator → cortex.orchestrators.validation.coherence_validator.

Phase 58-B: Canonical implementation lives in cortex/orchestrators/validation/coherence_validator.py.
"""
# noqa: F401
from cortex.orchestrators.validation.coherence_validator import CoherenceIssue, ValidationConfig, CoherenceValidator

__all__ = ["CoherenceIssue", "ValidationConfig", "CoherenceValidator"]

