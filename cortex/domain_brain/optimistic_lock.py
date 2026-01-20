"""Optimistic Lock

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class OptimisticLockManager:
    """Manage optimistic locks."""
    lock_timeout_ms: int = 5000

__all__ = ["OptimisticLockManager"]
