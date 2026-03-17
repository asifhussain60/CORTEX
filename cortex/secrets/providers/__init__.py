"""Compatibility alias package for secrets provider patch targets."""

from cortex.infrastructure.secrets.providers.aws import AWSSecretsProvider
from cortex.infrastructure.secrets.providers.azure import AzureKeyVaultProvider
from cortex.infrastructure.secrets.providers.local import LocalSecretsProvider
from cortex.infrastructure.secrets.providers.vault import VaultProvider

__all__ = [
    "AWSSecretsProvider",
    "AzureKeyVaultProvider",
    "LocalSecretsProvider",
    "VaultProvider",
]
