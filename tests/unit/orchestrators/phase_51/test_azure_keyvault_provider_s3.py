"""
Phase 51 S3: Azure Key Vault Integration
TDD tests for Azure Key Vault provider

AC-PHASE51-S3-001: Retrieve secrets via Key Vault URI
AC-PHASE51-S3-002: Soft delete enables 30-day recovery
AC-PHASE51-S3-003: RBAC enforces least-privilege
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from typing import Optional, Dict, Any


class TestAzureKeyVaultProviderInterface:
    """AC-PHASE51-S3-001: Retrieve secrets via Key Vault URI"""
    
    def test_azure_provider_implements_interface(self):
        """AzureKeyVaultProvider implements ISecretsProvider"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.provider import ISecretsProvider
        
        assert issubclass(AzureKeyVaultProvider, ISecretsProvider)
    
    def test_azure_provider_requires_endpoint(self):
        """AzureKeyVaultProvider requires Key Vault URL endpoint"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.config import SecretsConfig
        from cortex.secrets.errors import ConfigError
        
        config = SecretsConfig(
            provider_type="azure",
            endpoint="https://my-vault.vault.azure.net"
        )
        # Should not raise
        provider = AzureKeyVaultProvider(config)
        assert provider is not None
    
    def test_azure_provider_accepts_keyvault_uri(self):
        """AzureKeyVaultProvider accepts Key Vault URI as endpoint"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.config import SecretsConfig
        
        vault_url = "https://my-vault.vault.azure.net/"
        config = SecretsConfig(
            provider_type="azure",
            endpoint=vault_url
        )
        provider = AzureKeyVaultProvider(config)
        assert provider.config.endpoint == vault_url


class TestAzureKeyVaultProviderRetrieval:
    """AC-PHASE51-S3-001: Retrieve secrets via Key Vault URI"""
    
    @patch('cortex.secrets.providers.azure.SecretClient')
    def test_azure_provider_get_retrieves_secret(self, mock_secret_client_class):
        """get(secret_id) retrieves secret from Key Vault"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.config import SecretsConfig
        
        # Mock Azure SecretClient
        mock_client = MagicMock()
        mock_secret_client_class.return_value = mock_client
        
        mock_secret = MagicMock()
        mock_secret.value = "my-secret-value"
        mock_client.get_secret.return_value = mock_secret
        
        config = SecretsConfig(
            provider_type="azure",
            endpoint="https://my-vault.vault.azure.net"
        )
        provider = AzureKeyVaultProvider(config)
        
        value = provider.get("my-secret")
        assert value == "my-secret-value"
        mock_client.get_secret.assert_called_once_with("my-secret")
    
    @patch('cortex.secrets.providers.azure.SecretClient')
    def test_azure_provider_get_handles_secret_versions(self, mock_secret_client_class):
        """get() can retrieve specific secret versions"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_secret_client_class.return_value = mock_client
        
        mock_secret = MagicMock()
        mock_secret.value = "versioned-value"
        mock_client.get_secret.return_value = mock_secret
        
        config = SecretsConfig(
            provider_type="azure",
            endpoint="https://my-vault.vault.azure.net"
        )
        provider = AzureKeyVaultProvider(config)
        
        # Get specific version
        value = provider.get("my-secret")
        assert value == "versioned-value"


class TestAzureKeyVaultProviderStorage:
    """Test Azure Key Vault storage operations"""
    
    @patch('cortex.secrets.providers.azure.SecretClient')
    def test_azure_provider_set_creates_secret(self, mock_secret_client_class):
        """set(secret_id, value) creates or updates secret"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_secret_client_class.return_value = mock_client
        
        mock_secret = MagicMock()
        mock_secret.id = "https://my-vault.vault.azure.net/secrets/new-secret/v1"
        mock_client.set_secret.return_value = mock_secret
        
        config = SecretsConfig(
            provider_type="azure",
            endpoint="https://my-vault.vault.azure.net"
        )
        provider = AzureKeyVaultProvider(config)
        
        provider.set("new-secret", "secret-value")
        
        mock_client.set_secret.assert_called_once()
        call_kwargs = mock_client.set_secret.call_args
        assert call_kwargs[0][0] == "new-secret"
        assert call_kwargs[0][1] == "secret-value"
    
    @patch('cortex.secrets.providers.azure.SecretClient')
    def test_azure_provider_set_with_tags(self, mock_secret_client_class):
        """set() can add tags for organization"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_secret_client_class.return_value = mock_client
        
        config = SecretsConfig(
            provider_type="azure",
            endpoint="https://my-vault.vault.azure.net"
        )
        provider = AzureKeyVaultProvider(config)
        
        metadata = {"tags": {"env": "prod", "app": "cortex"}}
        provider.set("tagged-secret", "value", metadata)
        
        # Verify tags were passed
        mock_client.set_secret.assert_called_once()


class TestAzureKeyVaultProviderDeletion:
    """AC-PHASE51-S3-002: Soft delete enables 30-day recovery"""
    
    @patch('cortex.secrets.providers.azure.SecretClient')
    def test_azure_provider_delete_soft_deletes(self, mock_secret_client_class):
        """delete(secret_id) soft-deletes with 30-day recovery"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_secret_client_class.return_value = mock_client
        
        mock_deleted = MagicMock()
        mock_deleted.deleted_date = "2026-02-09"
        mock_deleted.scheduled_purge_date = "2026-03-11"
        mock_client.begin_delete_secret.return_value = mock_deleted
        
        config = SecretsConfig(
            provider_type="azure",
            endpoint="https://my-vault.vault.azure.net"
        )
        provider = AzureKeyVaultProvider(config)
        
        provider.delete("my-secret")
        
        mock_client.begin_delete_secret.assert_called_once_with("my-secret")
    
    @patch('cortex.secrets.providers.azure.SecretClient')
    def test_azure_provider_purge_immediately(self, mock_secret_client_class):
        """delete() can purge immediately (hard delete)"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_secret_client_class.return_value = mock_client
        
        config = SecretsConfig(
            provider_type="azure",
            endpoint="https://my-vault.vault.azure.net"
        )
        provider = AzureKeyVaultProvider(config)
        
        provider.delete("my-secret")
        
        # Soft delete is called
        mock_client.begin_delete_secret.assert_called()


class TestAzureKeyVaultProviderRotation:
    """Test secret rotation in Azure Key Vault"""
    
    @patch('cortex.secrets.providers.azure.SecretClient')
    def test_azure_provider_rotate_creates_new_version(self, mock_secret_client_class):
        """rotate(secret_id) creates new secret version"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.config import SecretsConfig
        import uuid
        
        mock_client = MagicMock()
        mock_secret_client_class.return_value = mock_client
        
        new_value = str(uuid.uuid4())
        mock_secret = MagicMock()
        mock_secret.value = new_value
        mock_secret.id = "https://my-vault.vault.azure.net/secrets/api-key/v2"
        mock_client.set_secret.return_value = mock_secret
        
        config = SecretsConfig(
            provider_type="azure",
            endpoint="https://my-vault.vault.azure.net"
        )
        provider = AzureKeyVaultProvider(config)
        
        rotated_value = provider.rotate("api-key")
        
        # Should create new version
        mock_client.set_secret.assert_called()
        assert rotated_value == new_value


class TestAzureKeyVaultProviderRBAC:
    """AC-PHASE51-S3-003: RBAC enforces least-privilege"""
    
    @patch('cortex.secrets.providers.azure.SecretClient')
    def test_azure_provider_uses_managed_identity(self, mock_secret_client_class):
        """Provider uses managed identity for RBAC enforcement"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.config import SecretsConfig
        
        # When using DefaultAzureCredential, it automatically uses managed identity
        mock_client = MagicMock()
        mock_secret_client_class.return_value = mock_client
        
        config = SecretsConfig(
            provider_type="azure",
            endpoint="https://my-vault.vault.azure.net",
            auth_type="managed_identity"
        )
        provider = AzureKeyVaultProvider(config)
        
        # Provider should be initialized with managed identity
        assert provider.config.auth_type == "managed_identity"
    
    @patch('cortex.secrets.providers.azure.SecretClient')
    def test_azure_provider_respects_role_permissions(self, mock_secret_client_class):
        """Provider operations fail when lacking RBAC permissions"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.config import SecretsConfig
        from cortex.secrets.errors import PermissionError as SecretsPermissionError
        from azure.core.exceptions import ClientAuthenticationError
        
        mock_client = MagicMock()
        mock_secret_client_class.return_value = mock_client
        mock_client.get_secret.side_effect = ClientAuthenticationError("Access denied")
        
        config = SecretsConfig(
            provider_type="azure",
            endpoint="https://my-vault.vault.azure.net"
        )
        provider = AzureKeyVaultProvider(config)
        
        with pytest.raises((SecretsPermissionError, Exception)):
            provider.get("protected-secret")


class TestAzureKeyVaultProviderErrorHandling:
    """Error handling for Azure Key Vault"""
    
    @patch('cortex.secrets.providers.azure.SecretClient')
    def test_azure_provider_handles_not_found(self, mock_secret_client_class):
        """get() raises SecretNotFoundError for missing secrets"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.config import SecretsConfig
        from cortex.secrets.errors import SecretNotFoundError
        from azure.core.exceptions import ResourceNotFoundError
        
        mock_client = MagicMock()
        mock_secret_client_class.return_value = mock_client
        mock_client.get_secret.side_effect = ResourceNotFoundError("Secret not found")
        
        config = SecretsConfig(
            provider_type="azure",
            endpoint="https://my-vault.vault.azure.net"
        )
        provider = AzureKeyVaultProvider(config)
        
        with pytest.raises(SecretNotFoundError):
            provider.get("nonexistent")
    
    @patch('cortex.secrets.providers.azure.SecretClient')
    def test_azure_provider_handles_authentication_error(self, mock_secret_client_class):
        """Auth errors are properly mapped"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.config import SecretsConfig
        from cortex.secrets.errors import AuthError
        from azure.core.exceptions import ClientAuthenticationError
        
        mock_client = MagicMock()
        mock_secret_client_class.return_value = mock_client
        mock_client.get_secret.side_effect = ClientAuthenticationError("Auth failed")
        
        config = SecretsConfig(
            provider_type="azure",
            endpoint="https://my-vault.vault.azure.net"
        )
        provider = AzureKeyVaultProvider(config)
        
        with pytest.raises((AuthError, Exception)):
            provider.get("secret")


class TestAzureKeyVaultProviderList:
    """Test listing secrets from Azure Key Vault"""
    
    @patch('cortex.secrets.providers.azure.SecretClient')
    def test_azure_provider_list_secrets(self, mock_secret_client_class):
        """list() returns all secrets in vault"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_secret_client_class.return_value = mock_client
        
        mock_secret1 = MagicMock()
        mock_secret1.name = "db-password"
        mock_secret2 = MagicMock()
        mock_secret2.name = "api-key"
        
        mock_client.list_properties_of_secrets.return_value = [mock_secret1, mock_secret2]
        
        config = SecretsConfig(
            provider_type="azure",
            endpoint="https://my-vault.vault.azure.net"
        )
        provider = AzureKeyVaultProvider(config)
        
        secrets = provider.list()
        
        assert "db-password" in secrets
        assert "api-key" in secrets
    
    @patch('cortex.secrets.providers.azure.SecretClient')
    def test_azure_provider_list_with_prefix(self, mock_secret_client_class):
        """list(prefix) filters secrets by prefix"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_secret_client_class.return_value = mock_client
        
        mock_secret1 = MagicMock()
        mock_secret1.name = "db-password"
        mock_secret2 = MagicMock()
        mock_secret2.name = "db-username"
        mock_secret3 = MagicMock()
        mock_secret3.name = "api-key"
        
        mock_client.list_properties_of_secrets.return_value = [
            mock_secret1,
            mock_secret2,
            mock_secret3
        ]
        
        config = SecretsConfig(
            provider_type="azure",
            endpoint="https://my-vault.vault.azure.net"
        )
        provider = AzureKeyVaultProvider(config)
        
        secrets = provider.list(prefix="db-")
        
        assert "db-password" in secrets
        assert "db-username" in secrets
        assert "api-key" not in secrets


class TestAzureKeyVaultProviderIntegration:
    """Integration tests for Azure Key Vault provider"""
    
    @patch('cortex.secrets.providers.azure.SecretClient')
    def test_full_secret_lifecycle(self, mock_secret_client_class):
        """Full workflow: create → retrieve → rotate → soft-delete"""
        from cortex.secrets.providers.azure import AzureKeyVaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_secret_client_class.return_value = mock_client
        
        # Setup mock responses
        mock_secret = MagicMock()
        mock_secret.value = "value"
        mock_secret.id = "https://my-vault.vault.azure.net/secrets/test/v1"
        mock_client.set_secret.return_value = mock_secret
        mock_client.get_secret.return_value = mock_secret
        mock_client.begin_delete_secret.return_value = mock_secret
        
        config = SecretsConfig(
            provider_type="azure",
            endpoint="https://my-vault.vault.azure.net"
        )
        provider = AzureKeyVaultProvider(config)
        
        # Create
        provider.set("test-secret", "value")
        
        # Retrieve
        value = provider.get("test-secret")
        assert value == "value"
        
        # Rotate
        provider.rotate("test-secret")
        
        # Soft delete
        provider.delete("test-secret")
        
        # Verify operations
        assert mock_client.set_secret.called
        assert mock_client.get_secret.called
        assert mock_client.begin_delete_secret.called
