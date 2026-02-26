"""VaultProvider — HashiCorp Vault backend."""
from __future__ import annotations

from typing import Any, List, Optional

from cortex.infrastructure.secrets.errors import AuthError, SecretNotFoundError
from cortex.infrastructure.secrets.secrets_provider import ISecretsProvider


class VaultProvider(ISecretsProvider):
    """Secrets provider backed by HashiCorp Vault."""

    def __init__(
        self,
        addr: str = "http://127.0.0.1:8200",
        token: Optional[str] = None,
        mount_point: str = "secret",
        **kwargs: Any,
    ) -> None:
        """Initialise HashiCorp Vault secrets provider."""
        self.addr = addr
        self.token = token
        self.mount_point = mount_point
        self._client: Optional[Any] = None

    def _get_client(self) -> Any:
        """Get client."""
        try:
            import hvac  # type: ignore
            if self._client is None:
                self._client = hvac.Client(url=self.addr, token=self.token)
                if not self._client.is_authenticated():
                    raise AuthError("Vault authentication failed")
            return self._client
        except ImportError as exc:
            raise AuthError("hvac is not installed") from exc

    def get_secret(self, key: str) -> str:
        """Retrieve a secret value by key."""
        client = self._get_client()
        resp = client.secrets.kv.v2.read_secret_version(path=key, mount_point=self.mount_point)
        data = resp.get("data", {}).get("data", {})
        if "value" not in data:
            raise SecretNotFoundError(key)
        return data["value"]

    def set_secret(self, key: str, value: str, **meta: Any) -> bool:
        """Store or update a secret value."""
        self._get_client().secrets.kv.v2.create_or_update_secret(
            path=key, secret={"value": value}, mount_point=self.mount_point
        )
        return True

    def delete_secret(self, key: str) -> bool:
        """Delete a secret by key."""
        self._get_client().secrets.kv.v2.delete_metadata_and_all_versions(
            path=key, mount_point=self.mount_point
        )
        return True

    def list_secrets(self) -> List[str]:
        """List all available secret keys."""
        resp = self._get_client().secrets.kv.v2.list_secrets(
            path="", mount_point=self.mount_point
        )
        return resp.get("data", {}).get("keys", [])

    def rotate_secret(self, key: str) -> str:
        """Rotate a secret and return the new value."""
        import secrets as _secrets
        new_val = _secrets.token_urlsafe(32)
        self.set_secret(key, new_val)
        return new_val