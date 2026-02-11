"""
Factory for creating secrets providers
"""

import os
from typing import Optional

from cortex.secrets.config import SecretsConfig
from cortex.secrets.errors import ConfigError
from cortex.secrets.provider import ISecretsProvider
from cortex.secrets.providers.local import LocalSecretsProvider


def get_secrets_provider(config: SecretsConfig) -> ISecretsProvider:
    """
    Factory function to create secrets provider based on configuration.

    Args:
        config: SecretsConfig with provider_type and settings

    Returns:
        Instance of appropriate ISecretsProvider

    Raises:
        ConfigError: If provider_type unknown
    """

    if config.provider_type == "local":
        return LocalSecretsProvider(config)

    elif config.provider_type == "aws":
        from cortex.secrets.providers.aws import AWSSecretsProvider
        return AWSSecretsProvider(config)

    elif config.provider_type == "azure":
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        return AzureKeyVaultProvider(config)

    elif config.provider_type == "vault":
        from cortex.secrets.providers.vault import VaultProvider
        return VaultProvider(config)

    else:
        raise ConfigError(f"Unknown provider_type: {config.provider_type}")


def get_secrets_provider_from_env() -> ISecretsProvider:
    """
    Create secrets provider from environment variables.

    Environment variables:
        SECRETS_PROVIDER: Provider type (aws|azure|vault|local, default: local)
        AWS_SECRETS_REGION: AWS region (for AWS provider)
        AZURE_KEYVAULT_URL: Azure Key Vault URL
        VAULT_ADDR: Vault server address

    Returns:
        Instance of appropriate ISecretsProvider
    """

    provider_type = os.getenv("SECRETS_PROVIDER", "local")

    config_kwargs = {"provider_type": provider_type}

    if provider_type == "aws":
        config_kwargs["region"] = os.getenv("AWS_SECRETS_REGION", "us-east-1")

    elif provider_type == "azure":
        config_kwargs["endpoint"] = os.getenv("AZURE_KEYVAULT_URL")

    elif provider_type == "vault":
        config_kwargs["endpoint"] = os.getenv("VAULT_ADDR")

    config = SecretsConfig(**config_kwargs)
    return get_secrets_provider(config)
