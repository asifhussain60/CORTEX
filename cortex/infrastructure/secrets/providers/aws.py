"""AWSSecretsProvider — AWS Secrets Manager backend."""
from __future__ import annotations

from typing import Any, List, Optional

from cortex.infrastructure.secrets.config import SecretsConfig
from cortex.infrastructure.secrets.errors import AuthError, SecretNotFoundError
from cortex.infrastructure.secrets.secrets_provider import ISecretsProvider

try:
    import boto3
except ImportError:  # pragma: no cover
    boto3 = None


class AWSSecretsProvider(ISecretsProvider):
    """Secrets provider backed by AWS Secrets Manager."""

    def __init__(self, config: Optional[SecretsConfig] = None, region: str = "us-east-1", **kwargs: Any) -> None:
        """Initialise AWS Secrets Manager provider."""
        if isinstance(config, SecretsConfig):
            self.config = config
            self.region = config.region or region
        else:
            self.config = SecretsConfig(provider_type="aws", region=region)
            self.region = region
        self._client: Optional[Any] = None
        self._kwargs = kwargs

    def _get_client(self) -> Any:
        """Get client."""
        if boto3 is None:
            raise AuthError("boto3 is not installed")
        if self._client is None:
            self._client = boto3.client("secretsmanager", region_name=self.region)
        return self._client

    @staticmethod
    def _error_code(exc: Exception) -> str:
        """Extract AWS error code from boto exceptions and mocked variants."""
        response = getattr(exc, "response", None)
        if isinstance(response, dict):
            return str(response.get("Error", {}).get("Code", ""))
        if getattr(exc, "args", None):
            first = exc.args[0]
            if isinstance(first, dict):
                return str(first.get("Error", {}).get("Code", ""))
        return ""

    def get_secret(self, key: str) -> str:
        """Retrieve a secret value by key."""
        try:
            client = self._get_client()
            resp = client.get_secret_value(SecretId=key)
            return resp.get("SecretString", "")
        except Exception as exc:
            code = self._error_code(exc)
            if code == "ResourceNotFoundException" or "ResourceNotFoundException" in type(exc).__name__:
                raise SecretNotFoundError(key) from exc
            if code == "AccessDeniedException":
                raise AuthError(f"Access denied for secret '{key}'") from exc
            raise

    def set_secret(self, key: str, value: str, **meta: Any) -> bool:
        """Store or update a secret value."""
        client = self._get_client()
        metadata = dict(getattr(self.config, "metadata", {}) or {})
        metadata.update(meta)
        create_kwargs = {"Name": key, "SecretString": value}
        kms_key_id = metadata.get("kms_key_id")
        if kms_key_id:
            create_kwargs["KmsKeyId"] = kms_key_id
        try:
            client.create_secret(**create_kwargs)
        except Exception:
            client.put_secret_value(SecretId=key, SecretString=value)
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
        client = self._get_client()
        rotate_kwargs = {"SecretId": key}
        rotation_lambda_arn = (getattr(self.config, "metadata", {}) or {}).get("rotation_lambda_arn")
        if rotation_lambda_arn:
            rotate_kwargs["RotationLambdaARN"] = rotation_lambda_arn
        client.rotate_secret(**rotate_kwargs)
        return key

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
        secrets = self.list_secrets()
        if not prefix:
            return secrets
        return [name for name in secrets if name.startswith(prefix)]

    def rotate(self, secret_id: str) -> str:
        """Compatibility alias for rotate_secret."""
        return self.rotate_secret(secret_id)
