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
class VersionedDomain:
    """Versioned domain entity."""
    domain_id: str
    version: int
    data: dict = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}



@dataclass
class LockToken:
    """Optimistic lock token."""
    token_id: str
    version: int
    expires_at: str = ""

__all__ = ["OptimisticLockManager", "LockToken"]
