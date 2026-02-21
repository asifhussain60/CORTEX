"""SecretsProviderFactory — instantiate the right provider from config."""
from __future__ import annotations

import os
from typing import Optional

from cortex.infrastructure.secrets.config import SecretsConfig
from cortex.infrastructure.secrets.errors import ConfigError
from cortex.infrastructure.secrets.secrets_provider import ISecretsProvider


def get_secrets_provider(config: SecretsConfig) -> ISecretsProvider:
    """Return an ISecretsProvider configured by *config*."""
    backend = (config.backend or "local").lower()
    if backend == "local":
        from cortex.infrastructure.secrets.providers.local import LocalSecretsProvider
        return LocalSecretsProvider()
    if backend == "aws":
        from cortex.infrastructure.secrets.providers.aws import AWSSecretsProvider
        return AWSSecretsProvider(region=config.region or "us-east-1")
    if backend in ("azure", "azure_keyvault"):
        from cortex.infrastructure.secrets.providers.azure import AzureKeyVaultProvider
        if not config.azure_vault_url:
            raise ConfigError("azure_vault_url is required for Azure backend")
        return AzureKeyVaultProvider(vault_url=config.azure_vault_url)
    if backend == "vault":
        from cortex.infrastructure.secrets.providers.vault import VaultProvider
        return VaultProvider(
            addr=config.vault_addr or "http://127.0.0.1:8200",
            token=config.vault_token,
        )
    raise ConfigError(f"Unknown secrets backend: '{backend}'")


def get_secrets_provider_from_env() -> ISecretsProvider:
    """Build a provider from environment variables."""
    config = SecretsConfig.from_env()
    return get_secrets_provider(config)
