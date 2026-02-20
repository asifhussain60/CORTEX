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


class StorageError(SecretsError):
    """Raised when reading/writing to the secrets backend fails."""


# Re-export under the test-expected alias
class PermissionError(SecretsError):  # noqa: A001
    """Raised when the caller lacks permission to access a secret."""
