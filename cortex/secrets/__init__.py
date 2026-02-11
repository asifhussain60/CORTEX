"""
Phase 51: Secrets Management & Audit Trail Hardening
Core provider interface and configuration
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from cortex.secrets.encryption import (
    EncryptedValue,
    EncryptionManager,
    decrypt_value,
    derive_key,
    encrypt_value,
)


class ISecretsProvider(ABC):
    """
    Abstract base class for secrets providers.

    All secrets providers must implement:
    - get(secret_id): Retrieve secret
    - set(secret_id, value, metadata): Store secret
    - delete(secret_id): Remove secret
    - rotate(secret_id): Rotate/regenerate secret
    - list(prefix): List all secrets matching prefix
    """

    @abstractmethod
    def get(self, secret_id: str) -> Optional[str]:
        """
        Retrieve secret by identifier.

        Args:
            secret_id: Unique identifier for the secret (e.g., "DB_PASSWORD", "arn:aws:...")

        Returns:
            Secret value or None if not found

        Raises:
            AuthError: If authentication fails
            PermissionError: If lacking access
            SecretNotFoundError: If secret doesn't exist (depends on provider)
        """
        pass

    @abstractmethod
    def set(self, secret_id: str, value: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Store/update secret.

        Args:
            secret_id: Unique identifier for the secret
            value: Secret value to store
            metadata: Optional metadata (tags, expiration, KMS key, etc.)

        Raises:
            AuthError: If authentication fails
            PermissionError: If lacking write access
            StorageError: If backend fails
        """
        pass

    @abstractmethod
    def delete(self, secret_id: str) -> None:
        """
        Mark secret for deletion (may be soft-delete with recovery).

        Args:
            secret_id: Unique identifier for the secret

        Raises:
            AuthError: If authentication fails
            PermissionError: If lacking delete access
            SecretNotFoundError: If secret doesn't exist
            StorageError: If backend fails
        """
        pass

    @abstractmethod
    def rotate(self, secret_id: str) -> str:
        """
        Rotate/regenerate secret (create new version).

        Args:
            secret_id: Unique identifier for the secret

        Returns:
            New secret value after rotation

        Raises:
            AuthError: If authentication fails
            PermissionError: If lacking rotate access
            SecretNotFoundError: If secret doesn't exist
            StorageError: If backend fails
        """
        pass

    @abstractmethod
    def list(self, prefix: str = "") -> List[str]:
        """
        List all secrets matching optional prefix.

        Args:
            prefix: Optional prefix filter (e.g., "DB_", "aws:arn:")

        Returns:
            List of secret identifiers

        Raises:
            AuthError: If authentication fails
            PermissionError: If lacking read access
            StorageError: If backend fails
        """
        pass
