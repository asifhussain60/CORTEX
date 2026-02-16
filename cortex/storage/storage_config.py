"""
Storage configuration.
Authority: Phase 50 Stage 1 - Storage Backend Abstraction
AC-PHASE50-S1-001: StorageConfig dataclass for all backends
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class StorageConfig:
    """
    Configuration for knowledge storage providers.

    Attributes:
        backend: Storage backend type ("local", "s3", "azure")
        endpoint: Remote storage endpoint URL (optional)
        credentials: Backend-specific credentials dict (optional)
        cache_ttl_seconds: Cache time-to-live in seconds (default: 3600)
        cache_enabled: Enable L1 in-memory caching (default: True)
    """

    backend: str  # "local", "s3", "azure"
    endpoint: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    cache_ttl_seconds: int = 3600
    cache_enabled: bool = True

    def __post_init__(self):
        """Validate backend value."""
        valid_backends = {"local", "s3", "azure"}
        if self.backend not in valid_backends:
            raise ValueError(f"Invalid backend: {self.backend}. Must be one of {valid_backends}")
