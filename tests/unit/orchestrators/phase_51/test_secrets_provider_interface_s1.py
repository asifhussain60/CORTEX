"""
Phase 51 S1: Secrets Manager Abstraction
Test the ISecretsProvider protocol and SecretsProviderFactory

AC-PHASE51-S1-001: ISecretsProvider defines CRUD + rotate
AC-PHASE51-S1-002: Factory supports AWS/Azure/Vault/Local
AC-PHASE51-S1-003: Error handling for auth failures
"""

import pytest
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, Any
from enum import Enum
from unittest.mock import Mock, patch, MagicMock


# ============================================================================
# TESTS (RED PHASE)
# ============================================================================

class TestISecretsProviderInterface:
    """AC-PHASE51-S1-001: ISecretsProvider defines CRUD + rotate"""

    def test_secrets_provider_is_abstract_protocol(self):
        """ISecretsProvider must be abstract base class"""
        from cortex.secrets.provider import ISecretsProvider
        
        assert hasattr(ISecretsProvider, '__abstractmethods__')
        assert len(ISecretsProvider.__abstractmethods__) > 0

    def test_secrets_provider_has_get_method(self):
        """get(secret_id: str) retrieves secret by identifier"""
        from cortex.secrets.provider import ISecretsProvider
        
        assert hasattr(ISecretsProvider, 'get')
        provider_method = getattr(ISecretsProvider, 'get')
        assert callable(provider_method)

    def test_secrets_provider_has_set_method(self):
        """set(secret_id: str, value: str, metadata: Dict) stores secret"""
        from cortex.secrets.provider import ISecretsProvider
        
        assert hasattr(ISecretsProvider, 'set')
        provider_method = getattr(ISecretsProvider, 'set')
        assert callable(provider_method)

    def test_secrets_provider_has_rotate_method(self):
        """rotate(secret_id: str) triggers secret rotation"""
        from cortex.secrets.provider import ISecretsProvider
        
        assert hasattr(ISecretsProvider, 'rotate')
        provider_method = getattr(ISecretsProvider, 'rotate')
        assert callable(provider_method)

    def test_secrets_provider_has_delete_method(self):
        """delete(secret_id: str) marks secret for deletion"""
        from cortex.secrets.provider import ISecretsProvider
        
        assert hasattr(ISecretsProvider, 'delete')
        provider_method = getattr(ISecretsProvider, 'delete')
        assert callable(provider_method)

    def test_secrets_provider_has_list_method(self):
        """list(prefix: str = '') returns all secrets matching prefix"""
        from cortex.secrets.provider import ISecretsProvider
        
        assert hasattr(ISecretsProvider, 'list')
        provider_method = getattr(ISecretsProvider, 'list')
        assert callable(provider_method)


class TestSecretsConfig:
    """SecretsConfig dataclass holds provider configuration"""

    def test_secrets_config_has_provider_type(self):
        """SecretsConfig.provider_type: str (aws|azure|vault|local)"""
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(provider_type="aws")
        assert hasattr(config, 'provider_type')
        assert config.provider_type == "aws"

    def test_secrets_config_has_endpoint(self):
        """SecretsConfig.endpoint: Optional[str] (URL/ARN)"""
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(
            provider_type="aws",
            endpoint="arn:aws:secretsmanager:us-east-1:123456789:secret:my-secret"
        )
        assert config.endpoint == "arn:aws:secretsmanager:us-east-1:123456789:secret:my-secret"

    def test_secrets_config_has_region(self):
        """SecretsConfig.region: Optional[str] (AWS region)"""
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(provider_type="aws", region="us-west-2")
        assert config.region == "us-west-2"

    def test_secrets_config_has_auth_type(self):
        """SecretsConfig.auth_type: str (iam|managed_identity|approle|env)"""
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(provider_type="aws", auth_type="iam")
        assert config.auth_type == "iam"

    def test_secrets_config_has_metadata(self):
        """SecretsConfig.metadata: Dict for provider-specific settings"""
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(
            provider_type="aws",
            metadata={"kms_key_id": "arn:aws:kms:..."}
        )
        assert config.metadata == {"kms_key_id": "arn:aws:kms:..."}

    def test_secrets_config_defaults(self):
        """SecretsConfig has sensible defaults"""
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(provider_type="local")
        assert config.auth_type == "env"
        assert config.metadata == {}


class TestSecretsProviderFactory:
    """AC-PHASE51-S1-002: Factory supports AWS/Azure/Vault/Local"""

    def test_factory_function_exists(self):
        """get_secrets_provider(config) → ISecretsProvider"""
        from cortex.secrets.factory import get_secrets_provider
        
        assert callable(get_secrets_provider)

    def test_factory_returns_local_provider(self):
        """Factory returns LocalSecretsProvider for provider_type='local'"""
        from cortex.secrets.factory import get_secrets_provider
        from cortex.secrets.config import SecretsConfig
        from cortex.secrets.providers.local import LocalSecretsProvider
        
        config = SecretsConfig(provider_type="local")
        provider = get_secrets_provider(config)
        
        assert isinstance(provider, LocalSecretsProvider)

    def test_factory_supports_aws_provider_type(self):
        """Factory recognizes provider_type='aws'"""
        from cortex.secrets.factory import get_secrets_provider
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(provider_type="aws", region="us-east-1")
        # Should not raise
        provider = get_secrets_provider(config)
        assert provider is not None

    def test_factory_supports_azure_provider_type(self):
        """Factory recognizes provider_type='azure'"""
        from cortex.secrets.factory import get_secrets_provider
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(provider_type="azure", endpoint="https://vault.azure.net")
        # Should not raise
        provider = get_secrets_provider(config)
        assert provider is not None

    def test_factory_supports_vault_provider_type(self):
        """Factory recognizes provider_type='vault'"""
        from cortex.secrets.factory import get_secrets_provider
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(provider_type="vault", endpoint="https://vault.company.com")
        # Should not raise
        provider = get_secrets_provider(config)
        assert provider is not None

    def test_factory_raises_on_unknown_provider(self):
        """Factory raises ConfigError for unknown provider_type"""
        from cortex.secrets.factory import get_secrets_provider
        from cortex.secrets.config import SecretsConfig
        from cortex.secrets.errors import ConfigError
        
        # ConfigError should be raised during SecretsConfig creation
        with pytest.raises(ConfigError):
            config = SecretsConfig(provider_type="unknown")
            get_secrets_provider(config)

    def test_factory_environment_based_selection(self):
        """Factory can select provider from SECRETS_PROVIDER env var"""
        import os
        from cortex.secrets.factory import get_secrets_provider_from_env
        
        with patch.dict(os.environ, {"SECRETS_PROVIDER": "local"}):
            provider = get_secrets_provider_from_env()
            assert provider is not None


class TestSecretsProviderErrorHandling:
    """AC-PHASE51-S1-003: Error handling for auth failures"""

    def test_auth_error_raised_on_invalid_credentials(self):
        """AuthError raised when credentials invalid"""
        from cortex.secrets.errors import AuthError
        
        assert issubclass(AuthError, Exception)

    def test_config_error_for_missing_required_config(self):
        """ConfigError raised when required config missing"""
        from cortex.secrets.errors import ConfigError
        
        assert issubclass(ConfigError, Exception)

    def test_secret_not_found_error(self):
        """SecretNotFoundError raised when secret doesn't exist"""
        from cortex.secrets.errors import SecretNotFoundError
        
        assert issubclass(SecretNotFoundError, Exception)

    def test_permission_error_for_access_denied(self):
        """PermissionError raised when user lacks access"""
        from cortex.secrets.errors import PermissionError as SecretsPermissionError
        
        assert issubclass(SecretsPermissionError, Exception)

    def test_storage_error_for_backend_failures(self):
        """StorageError raised for secrets backend issues"""
        from cortex.secrets.errors import StorageError
        
        assert issubclass(StorageError, Exception)

    def test_local_provider_auth_failure(self):
        """LocalSecretsProvider doesn't require .env - auth always succeeds locally"""
        from cortex.secrets.providers.local import LocalSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(provider_type="local")
        provider = LocalSecretsProvider(config)
        
        # Local provider should handle missing secrets gracefully (returns None)
        # No AuthError should be raised for local development
        value = provider.get("nonexistent_secret_not_in_env")
        assert value is None


class TestLocalSecretsProvider:
    """LocalSecretsProvider for development/testing"""

    def test_local_provider_implements_interface(self):
        """LocalSecretsProvider implements ISecretsProvider"""
        from cortex.secrets.providers.local import LocalSecretsProvider
        from cortex.secrets.provider import ISecretsProvider
        
        assert issubclass(LocalSecretsProvider, ISecretsProvider)

    def test_local_provider_reads_from_env(self):
        """LocalSecretsProvider.get() reads from environment"""
        from cortex.secrets.providers.local import LocalSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        with patch.dict('os.environ', {'DB_PASSWORD': 'secret123'}):
            config = SecretsConfig(provider_type="local")
            provider = LocalSecretsProvider(config)
            
            value = provider.get("DB_PASSWORD")
            assert value == "secret123"

    def test_local_provider_returns_none_for_missing_secret(self):
        """LocalSecretsProvider.get() returns None if not in environment"""
        from cortex.secrets.providers.local import LocalSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(provider_type="local")
        provider = LocalSecretsProvider(config)
        
        value = provider.get("NONEXISTENT_SECRET_12345")
        assert value is None

    def test_local_provider_set_method(self):
        """LocalSecretsProvider.set() stores in memory"""
        from cortex.secrets.providers.local import LocalSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(provider_type="local")
        provider = LocalSecretsProvider(config)
        
        provider.set("MY_SECRET", "value123")
        assert provider.get("MY_SECRET") == "value123"

    def test_local_provider_delete_method(self):
        """LocalSecretsProvider.delete() removes secret"""
        from cortex.secrets.providers.local import LocalSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(provider_type="local")
        provider = LocalSecretsProvider(config)
        
        provider.set("MY_SECRET", "value123")
        provider.delete("MY_SECRET")
        
        assert provider.get("MY_SECRET") is None

    def test_local_provider_list_method(self):
        """LocalSecretsProvider.list() returns all secrets"""
        from cortex.secrets.providers.local import LocalSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(provider_type="local")
        provider = LocalSecretsProvider(config)
        
        provider.set("DB_HOST", "localhost")
        provider.set("DB_PORT", "5432")
        provider.set("API_KEY", "key123")
        
        secrets = provider.list()
        assert "DB_HOST" in secrets
        assert "DB_PORT" in secrets
        assert "API_KEY" in secrets

    def test_local_provider_list_with_prefix(self):
        """LocalSecretsProvider.list(prefix) filters by prefix"""
        from cortex.secrets.providers.local import LocalSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(provider_type="local")
        provider = LocalSecretsProvider(config)
        
        provider.set("DB_HOST", "localhost")
        provider.set("DB_PORT", "5432")
        provider.set("API_KEY", "key123")
        
        db_secrets = provider.list(prefix="DB_")
        assert "DB_HOST" in db_secrets
        assert "DB_PORT" in db_secrets
        assert "API_KEY" not in db_secrets

    def test_local_provider_rotate_method(self):
        """LocalSecretsProvider.rotate() updates secret version"""
        from cortex.secrets.providers.local import LocalSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(provider_type="local")
        provider = LocalSecretsProvider(config)
        
        provider.set("API_KEY", "key_v1")
        old_value = provider.get("API_KEY")
        
        # rotate() should update the version
        new_key = provider.rotate("API_KEY")
        assert new_key != old_value


class TestSecretsProviderIntegration:
    """Integration tests for secrets provider system"""

    def test_factory_to_provider_workflow(self):
        """Full workflow: config → factory → provider → operations"""
        from cortex.secrets.config import SecretsConfig
        from cortex.secrets.factory import get_secrets_provider
        
        config = SecretsConfig(provider_type="local")
        provider = get_secrets_provider(config)
        
        provider.set("API_KEY", "secret")
        value = provider.get("API_KEY")
        
        assert value == "secret"

    def test_provider_isolation(self):
        """Each provider instance maintains separate secrets"""
        from cortex.secrets.config import SecretsConfig
        from cortex.secrets.factory import get_secrets_provider
        
        config1 = SecretsConfig(provider_type="local")
        config2 = SecretsConfig(provider_type="local")
        
        provider1 = get_secrets_provider(config1)
        provider2 = get_secrets_provider(config2)
        
        provider1.set("SECRET1", "value1")
        provider2.set("SECRET2", "value2")
        
        # Each provider should have its own secrets
        assert provider1.get("SECRET1") == "value1"
        assert provider1.get("SECRET2") is None
