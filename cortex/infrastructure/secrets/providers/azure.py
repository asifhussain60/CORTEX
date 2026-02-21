"""AzureKeyVaultProvider — Azure Key Vault backend stub."""
from __future__ import annotations

from typing import Any, List, Optional

from cortex.infrastructure.secrets.errors import AuthError, SecretNotFoundError
from cortex.infrastructure.secrets.secrets_provider import ISecretsProvider


class AzureKeyVaultProvider(ISecretsProvider):
    """Secrets provider backed by Azure Key Vault."""

    def __init__(self, vault_url: str, **kwargs: Any) -> None:
        self.vault_url = vault_url
        self._client: Optional[Any] = None
        self._kwargs = kwargs

    def _get_client(self) -> Any:
        try:
            from azure.keyvault.secrets import SecretClient  # type: ignore
            from azure.identity import DefaultAzureCredential  # type: ignore
            if self._client is None:
                credential = DefaultAzureCredential()
                self._client = SecretClient(vault_url=self.vault_url, credential=credential)
            return self._client
        except ImportError as exc:
            raise AuthError("azure-keyvault-secrets is not installed") from exc

    def get_secret(self, key: str) -> str:
        client = self._get_client()
        try:
            return client.get_secret(key).value or ""
        except Exception as exc:
            if "SecretNotFound" in str(exc):
                raise SecretNotFoundError(key) from exc
            raise

    def set_secret(self, key: str, value: str, **meta: Any) -> bool:
        self._get_client().set_secret(key, value)
        return True

    def delete_secret(self, key: str) -> bool:
        self._get_client().begin_delete_secret(key).wait()
        return True

    def list_secrets(self) -> List[str]:
        return [p.name for p in self._get_client().list_properties_of_secrets()]

    def rotate_secret(self, key: str) -> str:
        import secrets as _secrets
        new_val = _secrets.token_urlsafe(32)
        self.set_secret(key, new_val)
        return new_val
