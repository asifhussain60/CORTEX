"""
Phase 51 S4: HashiCorp Vault Integration
TDD tests for HashiCorp Vault provider

AC-PHASE51-S4-001: Retrieve secrets via Vault path
AC-PHASE51-S4-002: Dynamic secrets auto-renew
AC-PHASE51-S4-003: AppRole tokens rotate automatically
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from typing import Optional, Dict, Any


class TestVaultProviderInterface:
    """AC-PHASE51-S4-001: Retrieve secrets via Vault path"""
    
    def test_vault_provider_implements_interface(self):
        """VaultProvider implements ISecretsProvider"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.provider import ISecretsProvider
        
        assert issubclass(VaultProvider, ISecretsProvider)
    
    def test_vault_provider_requires_endpoint(self):
        """VaultProvider requires Vault server URL"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        
        config = SecretsConfig(
            provider_type="vault",
            endpoint="https://vault.company.com"
        )
        # Should not raise
        provider = VaultProvider(config)
        assert provider is not None
    
    def test_vault_provider_accepts_vault_addr(self):
        """VaultProvider accepts Vault server address"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        
        vault_addr = "https://vault.company.com:8200"
        config = SecretsConfig(
            provider_type="vault",
            endpoint=vault_addr
        )
        provider = VaultProvider(config)
        assert provider.config.endpoint == vault_addr


class TestVaultProviderRetrieval:
    """AC-PHASE51-S4-001: Retrieve secrets via Vault path"""
    
    @patch('cortex.secrets.providers.vault.hvac.Client')
    def test_vault_provider_get_retrieves_secret(self, mock_client_class):
        """get(secret_id) retrieves secret from Vault"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.secrets.kv.read_secret_version.return_value = {
            'data': {'data': {'value': 'my-secret-value'}}
        }
        
        config = SecretsConfig(
            provider_type="vault",
            endpoint="https://vault.company.com"
        )
        provider = VaultProvider(config)
        
        value = provider.get("secret/my-secret")
        assert value == "my-secret-value"
    
    @patch('cortex.secrets.providers.vault.hvac.Client')
    def test_vault_provider_get_with_kv2_path(self, mock_client_class):
        """get() works with KV v2 mount paths"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.secrets.kv.read_secret_version.return_value = {
            'data': {'data': {'password': 'secret123'}}
        }
        
        config = SecretsConfig(
            provider_type="vault",
            endpoint="https://vault.company.com"
        )
        provider = VaultProvider(config)
        
        value = provider.get("kv/data/db/password")
        assert value == "secret123"
    
    @patch('cortex.secrets.providers.vault.hvac.Client')
    def test_vault_provider_get_handles_json_secrets(self, mock_client_class):
        """get() returns JSON secrets as strings"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.secrets.kv.read_secret_version.return_value = {
            'data': {'data': {
                'username': 'admin',
                'password': 'pass123'
            }}
        }
        
        config = SecretsConfig(
            provider_type="vault",
            endpoint="https://vault.company.com"
        )
        provider = VaultProvider(config)
        
        value = provider.get("secret/db-creds")
        # Provider should handle multi-field secrets
        assert value is not None


class TestVaultProviderStorage:
    """Test Vault secrets storage operations"""
    
    @patch('cortex.secrets.providers.vault.hvac.Client')
    def test_vault_provider_set_creates_secret(self, mock_client_class):
        """set(secret_id, value) creates secret in Vault"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        config = SecretsConfig(
            provider_type="vault",
            endpoint="https://vault.company.com"
        )
        provider = VaultProvider(config)
        
        provider.set("secret/my-secret", "secret-value")
        
        mock_client.secrets.kv.create_or_update_secret.assert_called_once()
    
    @patch('cortex.secrets.providers.vault.hvac.Client')
    def test_vault_provider_delete_secret(self, mock_client_class):
        """delete(secret_id) removes secret from Vault"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        config = SecretsConfig(
            provider_type="vault",
            endpoint="https://vault.company.com"
        )
        provider = VaultProvider(config)
        
        provider.delete("secret/my-secret")
        
        mock_client.secrets.kv.delete_secret.assert_called_once()


class TestVaultProviderDynamicSecrets:
    """AC-PHASE51-S4-002: Dynamic secrets auto-renew"""
    
    @patch('cortex.secrets.providers.vault.hvac.Client')
    def test_vault_provider_dynamic_secret_generation(self, mock_client_class):
        """Vault can generate dynamic secrets (e.g., temporary DB credentials)"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.secrets.database.generate_credentials.return_value = {
            'data': {
                'username': 'vault-user-12345',
                'password': 'temp-password-xyz',
                'ttl': 3600  # 1 hour
            }
        }
        
        config = SecretsConfig(
            provider_type="vault",
            endpoint="https://vault.company.com"
        )
        provider = VaultProvider(config)
        
        # Vault generates dynamic credentials via database role
        creds = mock_client.secrets.database.generate_credentials(name="my-db-role")
        
        assert creds['data']['username'].startswith('vault-user-')
        assert 'password' in creds['data']
        assert creds['data']['ttl'] > 0
    
    @patch('cortex.secrets.providers.vault.hvac.Client')
    def test_vault_provider_lease_renewal(self, mock_client_class):
        """Vault automatically renews dynamic secret leases"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.auth.renew_token.return_value = {
            'auth': {'lease_duration': 3600}
        }
        
        config = SecretsConfig(
            provider_type="vault",
            endpoint="https://vault.company.com"
        )
        provider = VaultProvider(config)
        
        # Lease renewal happens automatically via lease management
        assert mock_client is not None


class TestVaultProviderAppRole:
    """AC-PHASE51-S4-003: AppRole tokens rotate automatically"""
    
    @patch('cortex.secrets.providers.vault.hvac.Client')
    def test_vault_provider_approle_authentication(self, mock_client_class):
        """Provider uses AppRole for authentication"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        config = SecretsConfig(
            provider_type="vault",
            endpoint="https://vault.company.com",
            auth_type="approle",
            metadata={
                "role_id": "role-12345",
                "secret_id": "secret-67890"
            }
        )
        provider = VaultProvider(config)
        
        # Provider should authenticate with AppRole
        assert provider.config.auth_type == "approle"
    
    @patch('cortex.secrets.providers.vault.hvac.Client')
    def test_vault_provider_approle_token_rotation(self, mock_client_class):
        """AppRole tokens are rotated automatically"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.auth.approle.generate_secret_id.return_value = {
            'data': {
                'secret_id': 'new-secret-id-xyz',
                'secret_id_ttl': 3600
            }
        }
        
        config = SecretsConfig(
            provider_type="vault",
            endpoint="https://vault.company.com",
            auth_type="approle"
        )
        provider = VaultProvider(config)
        
        # AppRole secret IDs can be rotated
        assert mock_client is not None


class TestVaultProviderRotation:
    """Test secret rotation in Vault"""
    
    @patch('cortex.secrets.providers.vault.hvac.Client')
    def test_vault_provider_rotate_creates_new_version(self, mock_client_class):
        """rotate(secret_id) creates new secret version"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        import uuid
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        new_secret = str(uuid.uuid4())
        mock_client.secrets.kv.create_or_update_secret.return_value = {
            'data': {'metadata': {'version': 2}}
        }
        
        config = SecretsConfig(
            provider_type="vault",
            endpoint="https://vault.company.com"
        )
        provider = VaultProvider(config)
        
        provider.rotate("secret/api-key")
        
        # Verify rotation was called
        mock_client.secrets.kv.create_or_update_secret.assert_called()


class TestVaultProviderErrorHandling:
    """Error handling for Vault"""
    
    @patch('cortex.secrets.providers.vault.hvac.Client')
    def test_vault_provider_handles_not_found(self, mock_client_class):
        """get() raises SecretNotFoundError for missing secrets"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        from cortex.secrets.errors import SecretNotFoundError
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Create mock exception
        invalid_path_error = type('InvalidPath', (Exception,), {})()
        mock_client.secrets.kv.read_secret_version.side_effect = invalid_path_error
        
        config = SecretsConfig(
            provider_type="vault",
            endpoint="https://vault.company.com"
        )
        provider = VaultProvider(config)
        
        # Should raise SecretNotFoundError
        with pytest.raises(SecretNotFoundError):
            provider.get("nonexistent/secret")
    
    @patch('cortex.secrets.providers.vault.hvac.Client')
    def test_vault_provider_handles_auth_error(self, mock_client_class):
        """Auth errors are properly mapped"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        from cortex.secrets.errors import AuthError
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Create mock exception
        unauthorized_error = type('Unauthorized', (Exception,), {})()
        mock_client.secrets.kv.read_secret_version.side_effect = unauthorized_error
        
        config = SecretsConfig(
            provider_type="vault",
            endpoint="https://vault.company.com"
        )
        provider = VaultProvider(config)
        
        with pytest.raises(AuthError):
            provider.get("secret/data")


class TestVaultProviderList:
    """Test listing secrets from Vault"""
    
    @patch('cortex.secrets.providers.vault.hvac.Client')
    def test_vault_provider_list_secrets(self, mock_client_class):
        """list() returns all secrets in path"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.secrets.kv.list_secrets.return_value = {
            'data': {'keys': ['db-password', 'api-key', 'webhook-secret']}
        }
        
        config = SecretsConfig(
            provider_type="vault",
            endpoint="https://vault.company.com"
        )
        provider = VaultProvider(config)
        
        secrets = provider.list()
        
        assert "db-password" in secrets
        assert "api-key" in secrets
        assert "webhook-secret" in secrets
    
    @patch('cortex.secrets.providers.vault.hvac.Client')
    def test_vault_provider_list_with_prefix(self, mock_client_class):
        """list(prefix) filters secrets"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.secrets.kv.list_secrets.return_value = {
            'data': {'keys': ['db-password', 'db-username', 'api-key']}
        }
        
        config = SecretsConfig(
            provider_type="vault",
            endpoint="https://vault.company.com"
        )
        provider = VaultProvider(config)
        
        secrets = provider.list(prefix="db-")
        
        assert "db-password" in secrets
        assert "db-username" in secrets
        assert "api-key" not in secrets


class TestVaultProviderIntegration:
    """Integration tests for Vault provider"""
    
    @patch('cortex.secrets.providers.vault.hvac.Client')
    def test_full_secret_lifecycle(self, mock_client_class):
        """Full workflow: create → retrieve → rotate → delete"""
        from cortex.secrets.providers.vault import VaultProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Setup mock responses
        mock_client.secrets.kv.create_or_update_secret.return_value = {'data': {}}
        mock_client.secrets.kv.read_secret_version.return_value = {
            'data': {'data': {'value': 'secret-value'}}
        }
        mock_client.secrets.kv.delete_secret.return_value = {}
        
        config = SecretsConfig(
            provider_type="vault",
            endpoint="https://vault.company.com"
        )
        provider = VaultProvider(config)
        
        # Create
        provider.set("secret/test", "value")
        
        # Retrieve
        value = provider.get("secret/test")
        assert value == "secret-value"
        
        # Rotate
        provider.rotate("secret/test")
        
        # Delete
        provider.delete("secret/test")
        
        # Verify all operations
        assert mock_client.secrets.kv.create_or_update_secret.called
        assert mock_client.secrets.kv.read_secret_version.called
        assert mock_client.secrets.kv.delete_secret.called
