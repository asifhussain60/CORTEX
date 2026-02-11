"""
Local secrets provider for development and testing
"""

import os
import secrets
from typing import Any, Dict, List, Optional

from cortex.secrets.config import SecretsConfig
from cortex.secrets.errors import AuthError
from cortex.secrets.provider import ISecretsProvider


class LocalSecretsProvider(ISecretsProvider):
    """
    Local secrets provider using environment variables and in-memory storage.

    Suitable for development, testing, and local development workflows.
    Secrets are NOT persisted and ARE lost on process restart.
    """

    def __init__(self, config: SecretsConfig):
        """
        Initialize local secrets provider.

        Args:
            config: SecretsConfig with provider_type="local"
        """
        if config.provider_type != "local":
            raise ValueError(f"LocalSecretsProvider requires provider_type='local', got {config.provider_type}")

        self.config = config
        self._secrets: Dict[str, str] = {}

    def get(self, secret_id: str) -> Optional[str]:
        """
        Retrieve secret from environment or in-memory storage.

        Priority:
        1. In-memory storage (secrets.set())
        2. Environment variables
        3. None (not found)

        Args:
            secret_id: Secret identifier

        Returns:
            Secret value or None if not found
        """
        # Check in-memory storage first
        if secret_id in self._secrets:
            return self._secrets[secret_id]

        # Fall back to environment variables
        return os.getenv(secret_id)

    def set(self, secret_id: str, value: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Store secret in memory.

        Args:
            secret_id: Secret identifier
            value: Secret value
            metadata: Optional metadata (ignored for local provider)
        """
        self._secrets[secret_id] = value

    def delete(self, secret_id: str) -> None:
        """
        Remove secret from in-memory storage.

        Args:
            secret_id: Secret identifier
        """
        if secret_id in self._secrets:
            del self._secrets[secret_id]

    def rotate(self, secret_id: str) -> str:
        """
        Generate new random value for secret.

        Args:
            secret_id: Secret identifier

        Returns:
            New secret value
        """
        # Generate new random token (URL-safe, 32 bytes)
        new_value = secrets.token_urlsafe(32)
        self._secrets[secret_id] = new_value
        return new_value

    def list(self, prefix: str = "") -> List[str]:
        """
        List all secrets matching optional prefix.

        Includes both in-memory secrets and environment variables.

        Args:
            prefix: Optional prefix filter

        Returns:
            List of secret identifiers
        """
        # Collect from in-memory storage
        secrets_list = list(self._secrets.keys())

        # Add environment variables
        secrets_list.extend(os.environ.keys())

        # Remove duplicates
        secrets_list = list(set(secrets_list))

        # Filter by prefix if provided
        if prefix:
            secrets_list = [s for s in secrets_list if s.startswith(prefix)]

        return sorted(secrets_list)
