"""Azure Key Vault provider"""

from typing import Any, Dict, List, Optional

from azure.core.exceptions import ClientAuthenticationError, ResourceNotFoundError
from azure.keyvault.secrets import SecretClient

from cortex.secrets.config import SecretsConfig
from cortex.secrets.errors import (
    AuthError,
    SecretNotFoundError,
    StorageError,
)
from cortex.secrets.errors import (
    PermissionError as SecretsPermissionError,
)
from cortex.secrets.provider import ISecretsProvider


class AzureKeyVaultProvider(ISecretsProvider):
    """Azure Key Vault provider for enterprise secrets management"""

    def __init__(self, config: SecretsConfig):
        """
        Initialize Azure Key Vault provider.

        Args:
            config: SecretsConfig with provider_type='azure', endpoint (Key Vault URL)
        """
        if config.provider_type != "azure":
            raise ValueError(f"AzureKeyVaultProvider requires provider_type='azure', got {config.provider_type}")

        if not config.endpoint:
            raise ValueError("AzureKeyVaultProvider requires endpoint (Key Vault URL)")

        self.config = config

        # Create Azure SecretClient with managed identity (DefaultAzureCredential)
        # Automatically uses: Managed Identity > Service Principal > CLI > Environment
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=config.endpoint, credential=credential)

    def get(self, secret_id: str) -> Optional[str]:
        """
        Retrieve secret from Azure Key Vault.

        Args:
            secret_id: Secret name or full URI

        Returns:
            Secret value as string

        Raises:
            SecretNotFoundError: If secret doesn't exist
            AuthError: If authentication fails
            PermissionError: If lacking access
            StorageError: If backend fails
        """
        try:
            secret = self.client.get_secret(secret_id)
            return secret.value

        except ResourceNotFoundError:
            raise SecretNotFoundError(f"Secret not found: {secret_id}")

        except ClientAuthenticationError as e:
            raise AuthError(f"Authentication failed: {str(e)}")

        except Exception as e:
            if "access" in str(e).lower() or "permission" in str(e).lower():
                raise SecretsPermissionError(f"Permission denied: {str(e)}")
            raise StorageError(f"Failed to retrieve secret: {str(e)}")

    def set(self, secret_id: str, value: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Create or update secret in Azure Key Vault.

        Args:
            secret_id: Secret name
            value: Secret value
            metadata: Optional metadata (tags, description)

        Raises:
            AuthError: If authentication fails
            PermissionError: If lacking write access
            StorageError: If backend fails
        """
        try:
            kwargs = {}

            # Add tags if provided
            if metadata and "tags" in metadata:
                kwargs["tags"] = metadata["tags"]

            # Add description if provided
            if metadata and "description" in metadata:
                kwargs["content_type"] = metadata["description"]

            self.client.set_secret(secret_id, value, **kwargs)

        except ClientAuthenticationError as e:
            raise AuthError(f"Authentication failed: {str(e)}")

        except Exception as e:
            if "access" in str(e).lower() or "permission" in str(e).lower():
                raise SecretsPermissionError(f"Permission denied: {str(e)}")
            raise StorageError(f"Failed to create secret: {str(e)}")

    def delete(self, secret_id: str) -> None:
        """
        Soft-delete secret from Azure Key Vault (30-day recovery window).

        Args:
            secret_id: Secret name or URI

        Raises:
            SecretNotFoundError: If secret doesn't exist
            AuthError: If authentication fails
            PermissionError: If lacking delete access
            StorageError: If backend fails
        """
        try:
            # Azure soft-deletes by default with 30-day recovery
            self.client.begin_delete_secret(secret_id)

        except ResourceNotFoundError:
            raise SecretNotFoundError(f"Secret not found: {secret_id}")

        except ClientAuthenticationError as e:
            raise AuthError(f"Authentication failed: {str(e)}")

        except Exception as e:
            if "access" in str(e).lower() or "permission" in str(e).lower():
                raise SecretsPermissionError(f"Permission denied: {str(e)}")
            raise StorageError(f"Failed to delete secret: {str(e)}")

    def rotate(self, secret_id: str) -> str:
        """
        Rotate secret by creating a new version in Azure Key Vault.

        Args:
            secret_id: Secret name

        Returns:
            New secret value

        Raises:
            SecretNotFoundError: If secret doesn't exist
            AuthError: If authentication fails
            PermissionError: If lacking update access
            StorageError: If backend fails
        """
        try:
            # Get current secret
            current_secret = self.client.get_secret(secret_id)

            # Generate new value (in production, use proper rotation logic)
            import uuid
            new_value = str(uuid.uuid4())

            # Set new version
            new_secret = self.client.set_secret(secret_id, new_value)
            return new_secret.value

        except ResourceNotFoundError:
            raise SecretNotFoundError(f"Secret not found: {secret_id}")

        except ClientAuthenticationError as e:
            raise AuthError(f"Authentication failed: {str(e)}")

        except Exception as e:
            if "access" in str(e).lower() or "permission" in str(e).lower():
                raise SecretsPermissionError(f"Permission denied: {str(e)}")
            raise StorageError(f"Failed to rotate secret: {str(e)}")

    def list(self, prefix: str = "") -> List[str]:
        """
        List secrets from Azure Key Vault.

        Args:
            prefix: Optional prefix filter (applied client-side)

        Returns:
            List of secret names

        Raises:
            AuthError: If authentication fails
            PermissionError: If lacking list access
            StorageError: If backend fails
        """
        try:
            secrets = []

            # List all secret properties
            for secret_props in self.client.list_properties_of_secrets():
                secrets.append(secret_props.name)

            # Filter by prefix if provided
            if prefix:
                secrets = [s for s in secrets if s.startswith(prefix)]

            return sorted(secrets)

        except ClientAuthenticationError as e:
            raise AuthError(f"Authentication failed: {str(e)}")

        except Exception as e:
            if "access" in str(e).lower() or "permission" in str(e).lower():
                raise SecretsPermissionError(f"Permission denied: {str(e)}")
            raise StorageError(f"Failed to list secrets: {str(e)}")
