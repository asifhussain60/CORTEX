"""Re-export shim for cortex.core.core.result → cortex.core.result.

COMPAT shim — Phase 58 simplification.
All imports should migrate to: from cortex.core.result import Ok, Err, Result
This file will be deleted when cortex/core/core/ is removed in phase-58-e.

# COMPAT — remove after phase-61 cleanup
"""
from cortex.core.result import Err, Ok, Result, _ResultMeta  # noqa: F401

__all__ = ["Ok", "Err", "Result", "_ResultMeta"]
