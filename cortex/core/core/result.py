"""
cortex.core.core.result — Re-export shim (Phase 59-b, CORE-035)

All Result, Ok, Err symbols are defined in cortex.core.result (primary).
This module is kept for backward compatibility — do not add new definitions here.

Author: Asif Hussain
"""
# Phase 59-b: Single canonical Result implementation — re-export from cortex.core.result
from cortex.core.result import (  # noqa: F401
    Ok,
    Err,
    Result,
)

# Legacy helper aliases preserved for backward compatibility
ok = Ok
err = Err

__all__ = ["Ok", "Err", "Result", "ok", "err"]
