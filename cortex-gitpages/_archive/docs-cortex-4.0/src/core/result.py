"""
Result Module - Compatibility Layer

This module provides backward compatibility for code importing from src.core.result.
The actual implementation is in cortex.brain.core.result.

This allows old imports like:
    from src.core.result import Ok, Err, Result
    
To continue working while we migrate the codebase to use:
    from cortex.brain.core.result import Ok, Err, Result
"""

# Re-export from the actual location
from cortex.brain.core.result import Ok, Err, ok, err, Result

__all__ = ["Ok", "Err", "ok", "err", "Result"]
