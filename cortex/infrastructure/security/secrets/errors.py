"""
Custom error classes for secrets management
"""


class SecretsError(Exception):
    """Base class for secrets management errors"""
    pass


class AuthError(SecretsError):
    """Authentication failed (invalid credentials, missing auth)"""
    pass


class ConfigError(SecretsError):
    """Configuration error (invalid provider, missing required config)"""
    pass


class SecretNotFoundError(SecretsError):
    """Secret not found in provider"""
    pass


class PermissionError(SecretsError):
    """Insufficient permissions to access secret"""
    pass


class StorageError(SecretsError):
    """Backend storage error (network, timeout, etc.)"""
    pass
