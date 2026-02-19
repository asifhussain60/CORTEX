"""
Storage error types.
Authority: Phase 50 Stage 1 - Storage Backend Abstraction
AC-PHASE50-S1-003: Error handling covers all failure modes
"""


class StorageError(Exception):
    """Base exception for all storage-related failures."""
    pass


class NetworkError(StorageError):
    """Raised when remote storage is unreachable or network operation fails."""
    pass


class PermissionError(StorageError):
    """Raised when access is denied to a storage resource."""
    pass


class NotFoundError(StorageError):
    """Raised when a requested path is not found in storage."""
    pass


class ConfigurationError(StorageError):
    """Raised when storage provider configuration is invalid."""
    pass
