"""Optimistic Lock

Author: CORTEX Framework
"""

from dataclasses import dataclass


class ConflictError(Exception):
    """Raised when optimistic lock conflict occurs."""
    pass


@dataclass
class OptimisticLockManager:
    """Manage optimistic locks."""
    lock_timeout_ms: int = 5000



@dataclass
class LockToken:
    """Optimistic lock token."""
    token_id: str
    version: int
    expires_at: str = ""

__all__ = ["OptimisticLockManager", "LockToken"]
