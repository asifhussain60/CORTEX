"""HashiCorp Vault provider"""

from typing import Any, Dict, List, Optional

import hvac
import hvac.exceptions

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


class VaultProvider(ISecretsProvider):
    """HashiCorp Vault provider for on-premise/hybrid secrets management"""

    def __init__(self, config: SecretsConfig):
        """
        Initialize HashiCorp Vault provider.

        Args:
            config: SecretsConfig with provider_type='vault', endpoint (Vault URL)
        """
        if config.provider_type != "vault":
            raise ValueError(f"VaultProvider requires provider_type='vault', got {config.provider_type}")

        if not config.endpoint:
            raise ValueError("VaultProvider requires endpoint (Vault server URL)")

        self.config = config

        # Create Vault client
        self.client = hvac.Client(url=config.endpoint)

        # Authenticate based on auth_type
        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate to Vault based on configuration"""
        auth_type = self.config.auth_type or "env"

        if auth_type == "approle":
            # AppRole authentication
            role_id = self.config.metadata.get("role_id")
            secret_id = self.config.metadata.get("secret_id")

            if role_id and secret_id:
                self.client.auth.approle.login(role_id, secret_id)

        elif auth_type == "token":
            # Token authentication (from metadata or env)
            token = self.config.metadata.get("token")
            if token:
                self.client.token = token

        # If no explicit auth, rely on environment variables or system auth

    def get(self, secret_id: str) -> Optional[str]:
        """
        Retrieve secret from Vault.

        Args:
            secret_id: Secret path in Vault (e.g., 'secret/my-secret')

        Returns:
            Secret value as string

        Raises:
            SecretNotFoundError: If secret doesn't exist
            AuthError: If authentication fails
            PermissionError: If lacking access
            StorageError: If backend fails
        """
        try:
            response = self.client.secrets.kv.read_secret_version(path=secret_id)
            data = response.get('data', {}).get('data', {})

            # If single 'value' key, return it; otherwise return first value
            if 'value' in data:
                return data['value']

            # Return first value or None
            values = list(data.values())
            return str(values[0]) if values else None

        except Exception as e:
            error_type_name = type(e).__name__
            error_msg = str(e).lower()

            # Handle all InvalidPath exceptions (real or mocked)
            if error_type_name == "InvalidPath":
                raise SecretNotFoundError(f"Secret not found: {secret_id}") from e
            # Handle all Unauthorized exceptions (real or mocked)
            elif error_type_name == "Unauthorized":
                raise AuthError(f"Authentication failed for secret: {secret_id}") from e
            # Handle all Forbidden exceptions (real or mocked)
            elif error_type_name == "Forbidden":
                raise SecretsPermissionError(f"Permission denied for secret: {secret_id}") from e
            # Handle string-based error messages
            elif 'not found' in error_msg or 'invalid' in error_msg:
                raise SecretNotFoundError(f"Secret not found: {secret_id}") from e
            elif 'unauthorized' in error_msg or 'auth' in error_msg:
                raise AuthError(f"Authentication failed for secret: {secret_id}") from e
            elif 'forbidden' in error_msg or 'permission' in error_msg:
                raise SecretsPermissionError(f"Permission denied for secret: {secret_id}") from e

            raise StorageError(f"Failed to retrieve secret: {str(e)}")

    def set(self, secret_id: str, value: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Create or update secret in Vault.

        Args:
            secret_id: Secret path in Vault
            value: Secret value
            metadata: Optional metadata (description, tags, etc.)

        Raises:
            AuthError: If authentication fails
            PermissionError: If lacking write access
            StorageError: If backend fails
        """
        try:
            secret_data = {"value": value}

            # Add custom fields if provided in metadata
            if metadata:
                for key in metadata:
                    if key not in ("description", "tags"):
                        secret_data[key] = metadata[key]

            self.client.secrets.kv.create_or_update_secret(
                path=secret_id,
                secret=secret_data
            )

        except hvac.exceptions.Unauthorized:
            raise AuthError("Authentication failed")

        except hvac.exceptions.Forbidden:
            raise SecretsPermissionError(f"Permission denied for secret: {secret_id}")

        except Exception as e:
            raise StorageError(f"Failed to create secret: {str(e)}")

    def delete(self, secret_id: str) -> None:
        """
        Delete secret from Vault.

        Args:
            secret_id: Secret path in Vault

        Raises:
            SecretNotFoundError: If secret doesn't exist
            AuthError: If authentication fails
            PermissionError: If lacking delete access
            StorageError: If backend fails
        """
        try:
            self.client.secrets.kv.delete_secret(path=secret_id)

        except hvac.exceptions.InvalidPath:
            raise SecretNotFoundError(f"Secret not found: {secret_id}")

        except hvac.exceptions.Unauthorized:
            raise AuthError("Authentication failed")

        except hvac.exceptions.Forbidden:
            raise SecretsPermissionError(f"Permission denied for secret: {secret_id}")

        except Exception as e:
            raise StorageError(f"Failed to delete secret: {str(e)}")

    def rotate(self, secret_id: str) -> str:
        """
        Rotate secret by creating new version in Vault.

        Args:
            secret_id: Secret path in Vault

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
            current = self.client.secrets.kv.read_secret_version(path=secret_id)
            current_data = current.get('data', {}).get('data', {})

            # Generate new rotation token (in production, use proper rotation logic)
            import uuid
            new_value = str(uuid.uuid4())

            # Create new version
            new_data = dict(current_data)
            new_data['value'] = new_value

            self.client.secrets.kv.create_or_update_secret(
                path=secret_id,
                secret=new_data
            )

            return new_value

        except hvac.exceptions.InvalidPath:
            raise SecretNotFoundError(f"Secret not found: {secret_id}")

        except hvac.exceptions.Unauthorized:
            raise AuthError("Authentication failed")

        except hvac.exceptions.Forbidden:
            raise SecretsPermissionError(f"Permission denied for secret: {secret_id}")

        except Exception as e:
            raise StorageError(f"Failed to rotate secret: {str(e)}")

    def list(self, prefix: str = "") -> List[str]:
        """
        List secrets from Vault.

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
            response = self.client.secrets.kv.list_secrets(path="")
            secrets = response.get('data', {}).get('keys', [])

            # Filter by prefix if provided
            if prefix:
                secrets = [s for s in secrets if s.startswith(prefix)]

            return sorted(secrets)

        except hvac.exceptions.Unauthorized:
            raise AuthError("Authentication failed")

        except hvac.exceptions.Forbidden:
            raise SecretsPermissionError("Permission denied to list secrets")

        except Exception as e:
            raise StorageError(f"Failed to list secrets: {str(e)}")
