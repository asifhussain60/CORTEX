"""AWSSecretsProvider — AWS Secrets Manager backend."""
from __future__ import annotations

from typing import Any, List, Optional

from cortex.infrastructure.secrets.errors import AuthError, SecretNotFoundError
from cortex.infrastructure.secrets.secrets_provider import ISecretsProvider


class AWSSecretsProvider(ISecretsProvider):
    """Secrets provider backed by AWS Secrets Manager."""

    def __init__(self, region: str = "us-east-1", **kwargs: Any) -> None:
        """Initialise AWS Secrets Manager provider."""
        self.region = region
        self._client: Optional[Any] = None
        self._kwargs = kwargs

    def _get_client(self) -> Any:
        """Get client."""
        try:
            import boto3
            if self._client is None:
                self._client = boto3.client("secretsmanager", region_name=self.region)
            return self._client
        except ImportError as exc:
            raise AuthError("boto3 is not installed") from exc

    def get_secret(self, key: str) -> str:
        """Retrieve a secret value by key."""
        try:
            client = self._get_client()
            resp = client.get_secret_value(SecretId=key)
            return resp.get("SecretString", "")
        except Exception as exc:
            if "ResourceNotFoundException" in type(exc).__name__:
                raise SecretNotFoundError(key) from exc
            raise

    def set_secret(self, key: str, value: str, **meta: Any) -> bool:
        """Store or update a secret value."""
        client = self._get_client()
        try:
            client.put_secret_value(SecretId=key, SecretString=value)
        except Exception:
            client.create_secret(Name=key, SecretString=value)
        return True

    def delete_secret(self, key: str) -> bool:
        """Delete a secret by key."""
        client = self._get_client()
        client.delete_secret(SecretId=key, ForceDeleteWithoutRecovery=True)
        return True

    def list_secrets(self) -> List[str]:
        """List all available secret keys."""
        client = self._get_client()
        paginator = client.get_paginator("list_secrets")
        names: List[str] = []
        for page in paginator.paginate():
            names.extend(s["Name"] for s in page.get("SecretList", []))
        return names

    def rotate_secret(self, key: str) -> str:
        """Rotate a secret and return the new value."""
        import secrets as _secrets
        new_val = _secrets.token_urlsafe(32)
        self.set_secret(key, new_val)
        return new_val