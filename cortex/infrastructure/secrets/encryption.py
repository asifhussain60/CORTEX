"""
Encryption Layer for Secrets Management

Implements AES-256-GCM encryption with key derivation,
encrypted storage format, and key rotation support.

Authority: phase-76-production-foundation-trilogy.yaml S3.T1
AC-ID: AC-PHASE76-S3-001
"""

import json
import logging
import os
import secrets
from typing import Any, Dict, Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


# ============================================================================
# KEY DERIVATION
# ============================================================================

def derive_key(master_key: str, salt: Optional[bytes] = None) -> bytes:
    """
    Derive encryption key from master key using PBKDF2.

    Args:
        master_key: Master key string (CORTEX_MASTER_KEY env var)
        salt: Optional salt for key derivation (for testing)

    Returns:
        32-byte key suitable for AES-256

    Raises:
        ValueError: If master_key is empty
    """
    if not master_key:
        raise ValueError("Master key cannot be empty")

    # Default salt (can be overridden for testing)
    if salt is None:
        salt = b"CORTEX_SECRETS_SALT_v1"

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256 bits for AES-256
        salt=salt,
        iterations=480000,
    )

    key = kdf.derive(master_key.encode())
    return key


# ============================================================================
# ENCRYPTION UTILITIES
# ============================================================================

class EncryptedValue:
    """Represents an encrypted secret with metadata."""

    def __init__(
        self,
        ciphertext: bytes,
        iv: bytes,
        tag: bytes,
    ) -> None:
        """Initialize encrypted value."""
        self.ciphertext = ciphertext
        self.iv = iv
        self.tag = tag

    def to_json(self) -> str:
        """Serialize to JSON for storage."""
        import base64
        data = {
            "ciphertext": base64.b64encode(self.ciphertext).decode(),
            "iv": base64.b64encode(self.iv).decode(),
            "tag": base64.b64encode(self.tag).decode(),
            "version": 1,
        }
        return json.dumps(data)

    @staticmethod
    def from_json(json_str: str) -> "EncryptedValue":
        """Deserialize from JSON."""
        import base64
        data = json.loads(json_str)
        return EncryptedValue(
            ciphertext=base64.b64decode(data["ciphertext"]),
            iv=base64.b64decode(data["iv"]),
            tag=base64.b64decode(data["tag"]),
        )


def encrypt_value(plaintext: str, master_key: str) -> str:
    """
    Encrypt a plaintext value using AES-256-GCM.

    Args:
        plaintext: Value to encrypt
        master_key: Master key from CORTEX_MASTER_KEY

    Returns:
        JSON string with ciphertext, IV, and tag

    Raises:
        ValueError: If encryption fails
    """
    try:
        # Derive encryption key
        key = derive_key(master_key)

        # Generate random IV (96 bits for GCM)
        iv = secrets.token_bytes(12)

        # Create cipher
        cipher = AESGCM(key)

        # Encrypt plaintext
        plaintext_bytes = plaintext.encode()
        ciphertext = cipher.encrypt(iv, plaintext_bytes, None)

        # GCM tag is last 16 bytes of ciphertext
        tag = ciphertext[-16:]
        ciphertext_data = ciphertext[:-16]

        # Create encrypted value object
        enc_value = EncryptedValue(ciphertext_data, iv, tag)

        return enc_value.to_json()

    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise ValueError(f"Encryption failed: {e}")


def decrypt_value(encrypted_json: str, master_key: str) -> str:
    """
    Decrypt a JSON-encoded encrypted value.

    Args:
        encrypted_json: JSON string with encrypted data
        master_key: Master key from CORTEX_MASTER_KEY

    Returns:
        Decrypted plaintext

    Raises:
        ValueError: If decryption fails (wrong key, corrupted data, etc.)
    """
    try:
        # Derive key
        key = derive_key(master_key)

        # Parse JSON
        enc_value = EncryptedValue.from_json(encrypted_json)

        # Create cipher
        cipher = AESGCM(key)

        # Reconstruct ciphertext with tag
        full_ciphertext = enc_value.ciphertext + enc_value.tag

        # Decrypt
        plaintext_bytes = cipher.decrypt(enc_value.iv, full_ciphertext, None)

        return plaintext_bytes.decode()

    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise ValueError(f"Decryption failed: {e}")


# ============================================================================
# ENCRYPTION MANAGER
# ============================================================================

class EncryptionManager:
    """High-level encryption manager."""

    def __init__(self, master_key: str) -> None:
        """
        Initialize encryption manager.

        Args:
            master_key: Master key for encryption

        Raises:
            ValueError: If master_key is empty
        """
        if not master_key:
            raise ValueError("Master key required")

        self.master_key = master_key
        logger.debug("EncryptionManager initialized")

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext.

        Args:
            plaintext: Value to encrypt

        Returns:
            Encrypted JSON string
        """
        return encrypt_value(plaintext, self.master_key)

    def decrypt(self, encrypted_json: str) -> str:
        """
        Decrypt encrypted value.

        Args:
            encrypted_json: JSON encrypted data

        Returns:
            Decrypted plaintext

        Raises:
            ValueError: If decryption fails
        """
        return decrypt_value(encrypted_json, self.master_key)

    @staticmethod
    def from_environment() -> "EncryptionManager":
        """
        Create manager from CORTEX_MASTER_KEY environment variable.

        Returns:
            EncryptionManager instance

        Raises:
            ValueError: If CORTEX_MASTER_KEY not set
        """
        master_key = os.getenv("CORTEX_MASTER_KEY")
        if not master_key:
            raise ValueError("CORTEX_MASTER_KEY environment variable not set")

        return EncryptionManager(master_key)


__all__ = [
    "EncryptionManager",
    "EncryptedValue",
    "encrypt_value",
    "decrypt_value",
    "derive_key",
]
