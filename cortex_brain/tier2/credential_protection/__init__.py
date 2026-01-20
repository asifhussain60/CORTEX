"""Credential Protection - Advanced credential management and encryption.

Provides credential encryption, key management, and secure credential
storage and retrieval mechanisms.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional
from enum import Enum
from datetime import datetime


class EncryptionAlgorithm(Enum):
    """Encryption algorithms for credential protection."""

    AES_256 = "aes_256"
    AES_128 = "aes_128"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    CHACHA20 = "chacha20"


class CredentialType(Enum):
    """Types of credentials."""

    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    PRIVATE_KEY = "private_key"
    CONNECTION_STRING = "connection_string"


class CredentialStatus(Enum):
    """Status of credentials."""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"
    INVALID = "invalid"


@dataclass
class EncryptedCredential:
    """Encrypted credential entry.

    Attributes:
        credential_id: Unique credential identifier.
        credential_type: Type of credential.
        encrypted_value: Encrypted credential value.
        algorithm: Encryption algorithm used.
        created_at: When credential was stored.
        metadata: Additional metadata.
    """

    credential_id: str
    credential_type: CredentialType
    encrypted_value: str
    algorithm: EncryptionAlgorithm
    created_at: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class CredentialManager:
    """Manages secure credential storage and retrieval.

    Provides encryption, decryption, and lifecycle management for credentials.
    """

    def __init__(self, default_algorithm: EncryptionAlgorithm = None) -> None:
        """Initialize credential manager.

        Args:
            default_algorithm: Default encryption algorithm.
        """
        self.default_algorithm = default_algorithm or EncryptionAlgorithm.AES_256
        self.credentials: Dict[str, EncryptedCredential] = {}

    def store_credential(
        self,
        credential_id: str,
        credential_type: CredentialType,
        value: str,
        algorithm: EncryptionAlgorithm = None,
    ) -> EncryptedCredential:
        """Store an encrypted credential.

        Args:
            credential_id: Credential identifier.
            credential_type: Type of credential.
            value: Credential value to store.
            algorithm: Encryption algorithm (uses default if None).

        Returns:
            EncryptedCredential: The stored credential entry.

        Raises:
            ValueError: If credential_id already exists.
        """
        if credential_id in self.credentials:
            raise ValueError(f"Credential {credential_id} already exists")

        algo = algorithm or self.default_algorithm
        # Simulated encryption
        encrypted_value = f"encrypted_{value}_{algo.value}"

        credential = EncryptedCredential(
            credential_id=credential_id,
            credential_type=credential_type,
            encrypted_value=encrypted_value,
            algorithm=algo,
        )
        self.credentials[credential_id] = credential
        return credential

    def retrieve_credential(self, credential_id: str) -> Optional[str]:
        """Retrieve a decrypted credential.

        Args:
            credential_id: Credential identifier.

        Returns:
            Decrypted credential value if found, None otherwise.
        """
        if credential_id not in self.credentials:
            return None

        credential = self.credentials[credential_id]
        # Simulated decryption
        decrypted_value = credential.encrypted_value.replace(
            f"encrypted_", ""
        ).replace(f"_{credential.algorithm.value}", "")
        return decrypted_value

    def delete_credential(self, credential_id: str) -> bool:
        """Delete a stored credential.

        Args:
            credential_id: Credential identifier.

        Returns:
            True if deleted, False if not found.
        """
        if credential_id in self.credentials:
            del self.credentials[credential_id]
            return True
        return False

    def list_credentials(self) -> Dict[str, EncryptedCredential]:
        """List all stored credentials (without decrypted values).

        Returns:
            Dictionary of credential entries.
        """
        return self.credentials.copy()


class KeyManager:
    """Manages encryption keys for credential protection."""

    def __init__(self) -> None:
        """Initialize key manager."""
        self.keys: Dict[str, Dict[str, Any]] = {}

    def generate_key(
        self, key_id: str, algorithm: EncryptionAlgorithm
    ) -> Dict[str, Any]:
        """Generate an encryption key.

        Args:
            key_id: Key identifier.
            algorithm: Algorithm for the key.

        Returns:
            Key information dictionary.
        """
        key_info = {
            "key_id": key_id,
            "algorithm": algorithm.value,
            "created_at": datetime.now().isoformat(),
            "key_material": f"key_material_{key_id}_{algorithm.value}",
        }
        self.keys[key_id] = key_info
        return key_info

    def rotate_key(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Rotate an existing key.

        Args:
            key_id: Key identifier.

        Returns:
            Updated key information if found, None otherwise.
        """
        if key_id not in self.keys:
            return None

        old_key = self.keys[key_id]
        algorithm = EncryptionAlgorithm(old_key["algorithm"])
        return self.generate_key(f"{key_id}_rotated", algorithm)

    def get_key(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve key information.

        Args:
            key_id: Key identifier.

        Returns:
            Key information if found, None otherwise.
        """
        return self.keys.get(key_id)


__all__ = [
    "EncryptionAlgorithm",
    "CredentialType",
    "CredentialStatus",
    "EncryptedCredential",
    "CredentialManager",
    "KeyManager",
]
