"""Secrets provider errors."""
from __future__ import annotations


class SecretsError(Exception):
    """Base class for all secrets errors."""


class SecretNotFoundError(SecretsError):
    """Raised when a requested secret does not exist."""


class AuthError(SecretsError):
    """Raised when authentication to the secrets backend fails."""


class ConfigError(SecretsError):
    """Raised when the secrets configuration is invalid."""


class SecretsStorageError(SecretsError):
    """Raised when reading/writing to the secrets backend fails.

    Renamed from StorageError → SecretsStorageError (Phase 101)
    to resolve CORE-035 duplicate with cortex.infrastructure.storage.errors.StorageError.
    """


class SecretsPermissionError(SecretsError):  # noqa: A001
    """Raised when the caller lacks permission to access a secret.

    Renamed from PermissionError → SecretsPermissionError (Phase 101)
    to resolve CORE-035 duplicate with cortex.infrastructure.storage.errors.PermissionError.
    """


# Phase 101: Backward-compat aliases (CORE-035 resolution)
StorageError = SecretsStorageError
PermissionError = SecretsPermissionError  # noqa: A001
