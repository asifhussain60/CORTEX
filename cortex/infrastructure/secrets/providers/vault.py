"""VaultProvider — HashiCorp Vault backend."""
from __future__ import annotations

from typing import Any, List, Optional

from cortex.infrastructure.secrets.config import SecretsConfig
from cortex.infrastructure.secrets.errors import AuthError, SecretNotFoundError
from cortex.infrastructure.secrets.secrets_provider import ISecretsProvider

try:
    import hvac  # type: ignore
except ImportError:  # pragma: no cover
    hvac = None  # type: ignore


class VaultProvider(ISecretsProvider):
    """Secrets provider backed by HashiCorp Vault."""

    def __init__(
        self,
        addr: Any = "http://127.0.0.1:8200",
        token: Optional[str] = None,
        mount_point: str = "secret",
        **kwargs: Any,
    ) -> None:
        """Initialise HashiCorp Vault secrets provider."""
        if isinstance(addr, SecretsConfig):
            self.config = addr
            self.addr = addr.endpoint or addr.vault_addr or "http://127.0.0.1:8200"
            self.token = addr.vault_token
        else:
            self.addr = addr
            self.token = token
            self.config = SecretsConfig(provider_type="vault", endpoint=str(addr), vault_token=token)
        self.mount_point = mount_point
        self._client: Optional[Any] = None

    def _get_client(self) -> Any:
        """Get client."""
        if hvac is None:
            raise AuthError("hvac is not installed")
        if self._client is None:
            self._client = hvac.Client(url=self.addr, token=self.token)
            if hasattr(self._client, "is_authenticated") and not self._client.is_authenticated():
                raise AuthError("Vault authentication failed")
        return self._client

    def get_secret(self, key: str) -> str:
        """Retrieve a secret value by key."""
        client = self._get_client()
        try:
            resp = client.secrets.kv.read_secret_version(path=key)
            data = resp.get("data", {}).get("data", {})
            if not data:
                raise SecretNotFoundError(key)
            if "value" in data:
                return data["value"]
            first_value = next(iter(data.values()))
            return str(first_value)
        except Exception as exc:
            name = type(exc).__name__.lower()
            if "invalidpath" in name or "notfound" in name:
                raise SecretNotFoundError(key) from exc
            if "unauthorized" in name or "forbidden" in name:
                raise AuthError(f"Vault authentication/authorization failed for '{key}'") from exc
            raise

    def set_secret(self, key: str, value: str, **meta: Any) -> bool:
        """Store or update a secret value."""
        self._get_client().secrets.kv.create_or_update_secret(
            path=key, secret={"value": value}
        )
        return True

    def delete_secret(self, key: str) -> bool:
        """Delete a secret by key."""
        self._get_client().secrets.kv.delete_secret(path=key)
        return True

    def list_secrets(self) -> List[str]:
        """List all available secret keys."""
        resp = self._get_client().secrets.kv.list_secrets(path="")
        return resp.get("data", {}).get("keys", [])

    def rotate_secret(self, key: str) -> str:
        """Rotate a secret and return the new value."""
        import secrets as _secrets
        new_val = _secrets.token_urlsafe(32)
        self.set_secret(key, new_val)
        return new_val

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
        """Compatibility alias for list_secrets with prefix filter."""
        keys = self.list_secrets()
        if not prefix:
            return keys
        return [key for key in keys if key.startswith(prefix)]

    def rotate(self, secret_id: str) -> str:
        """Compatibility alias for rotate_secret."""
        return self.rotate_secret(secret_id)
