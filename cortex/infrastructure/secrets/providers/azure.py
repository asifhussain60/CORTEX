"""AzureKeyVaultProvider — Azure Key Vault backend."""
from __future__ import annotations

from typing import Any, List, Optional

from cortex.infrastructure.secrets.config import SecretsConfig
from cortex.infrastructure.secrets.errors import AuthError, SecretNotFoundError
from cortex.infrastructure.secrets.secrets_provider import ISecretsProvider

try:
    from azure.keyvault.secrets import SecretClient  # type: ignore
except ImportError:  # pragma: no cover
    SecretClient = None  # type: ignore

try:
    from azure.identity import DefaultAzureCredential  # type: ignore
except ImportError:  # pragma: no cover
    DefaultAzureCredential = None  # type: ignore

try:
    from azure.core.exceptions import ClientAuthenticationError, ResourceNotFoundError  # type: ignore
except ImportError:  # pragma: no cover
    ClientAuthenticationError = Exception  # type: ignore
    ResourceNotFoundError = Exception  # type: ignore


class AzureKeyVaultProvider(ISecretsProvider):
    """Secrets provider backed by Azure Key Vault."""

    def __init__(self, config: Optional[SecretsConfig] = None, vault_url: Optional[str] = None, **kwargs: Any) -> None:
        """Initialise Azure Key Vault provider."""
        if isinstance(config, SecretsConfig):
            self.config = config
            resolved_url = config.endpoint or config.azure_vault_url or vault_url
        else:
            resolved_url = vault_url
            self.config = SecretsConfig(provider_type="azure", endpoint=vault_url)

        if not resolved_url:
            raise AuthError("Azure Key Vault endpoint is required")

        self.vault_url = resolved_url
        self._client: Optional[Any] = None
        self._kwargs = kwargs

    def _get_client(self) -> Any:
        """Get client."""
        if SecretClient is None or DefaultAzureCredential is None:
            raise AuthError("azure-keyvault-secrets is not installed")
        if self._client is None:
            credential = DefaultAzureCredential()
            self._client = SecretClient(vault_url=self.vault_url, credential=credential)
        return self._client

    def get_secret(self, key: str) -> str:
        """Retrieve a secret value by key."""
        client = self._get_client()
        try:
            return client.get_secret(key).value or ""
        except Exception as exc:
            if isinstance(exc, ResourceNotFoundError) or "SecretNotFound" in str(exc):
                raise SecretNotFoundError(key) from exc
            if isinstance(exc, ClientAuthenticationError):
                raise AuthError(f"Authentication failed for secret '{key}'") from exc
            raise

    def set_secret(self, key: str, value: str, **meta: Any) -> bool:
        """Store or update a secret value."""
        tags = (meta.get("tags") or {}) if isinstance(meta, dict) else {}
        self._get_client().set_secret(key, value, tags=tags)
        return True

    def delete_secret(self, key: str) -> bool:
        """Delete a secret by key."""
        self._get_client().begin_delete_secret(key)
        return True

    def list_secrets(self) -> List[str]:
        """List secrets."""
        return [p.name for p in self._get_client().list_properties_of_secrets()]

    def rotate_secret(self, key: str) -> str:
        """Rotate a secret and return the new value."""
        import uuid
        new_val = str(uuid.uuid4())
        response = self._get_client().set_secret(key, new_val)
        return getattr(response, "value", new_val)

    def get(self, secret_id: str) -> str:
        """Compatibility alias for get_secret."""
        return self.get_secret(secret_id)

    def set(self, secret_id: str, value: str, metadata: Optional[dict] = None) -> bool:
        """Compatibility alias for set_secret."""
        return self.set_secret(secret_id, value, **(metadata or {}))

    def delete(self, secret_id: str) -> bool:
        """Compatibility alias for delete_secret."""
        return self.delete_secret(secret_id)

    def list(self, prefix: str = "") -> List[str]:
        """Compatibility alias for list_secrets with optional prefix filter."""
        names = self.list_secrets()
        if not prefix:
            return names
        return [name for name in names if name.startswith(prefix)]

    def rotate(self, secret_id: str) -> str:
        """Compatibility alias for rotate_secret."""
        return self.rotate_secret(secret_id)
