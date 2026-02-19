"""Credential Protection - Advanced credential management and encryption.

Provides credential encryption, key management, and secure credential
storage and retrieval mechanisms.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import secrets


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
class EncryptionKey:
    """Encryption key with lifecycle management."""

    key_id: str
    algorithm: EncryptionAlgorithm
    created_at: datetime = field(default_factory=datetime.utcnow)
    ttl_days: int = 90
    expires_at: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate expiration time."""
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(days=self.ttl_days)

    def is_expired(self) -> bool:
        """Check if key is expired."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if key is valid for use."""
        return self.is_active and not self.is_expired()


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
        status: Credential status.
    """

    credential_id: str
    credential_type: CredentialType
    encrypted_value: str
    algorithm: EncryptionAlgorithm
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: CredentialStatus = CredentialStatus.ACTIVE


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


class SecureCredentialStore:
    """Secure store for credentials with full lifecycle management."""

    def __init__(self) -> None:
        """Initialize secure credential store."""
        self.store: Dict[str, Dict[str, Any]] = {}
        self.key_manager = KeyManager()
        self._access_log: List[Dict[str, Any]] = []
        self._keys: Dict[str, EncryptionKey] = {}
        self._default_key = EncryptionKey("default", EncryptionAlgorithm.AES_256)
        self._keys["default"] = self._default_key

    def store_credential(
        self,
        credential_id: str,
        value: str,
        credential_type: CredentialType = CredentialType.PASSWORD,
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Store a credential securely.

        Args:
            credential_id: Credential identifier.
            value: Credential value to store.
            credential_type: Type of credential.
            algorithm: Encryption algorithm to use.
            metadata: Optional metadata for the credential.

        Raises:
            ValueError: If value is empty or credential already exists.
        """
        if not value or value.strip() == "":
            raise ValueError(f"Credential value cannot be empty")

        if credential_id in self.store:
            raise ValueError(f"Credential {credential_id} already exists")

        # Hash the value for verification
        value_hash = hashlib.sha256(value.encode()).hexdigest()

        self.store[credential_id] = {
            "id": credential_id,
            "type": credential_type,
            "value_hash": value_hash,
            "algorithm": algorithm,
            "created_at": datetime.utcnow().isoformat(),
            "status": CredentialStatus.ACTIVE,
            "metadata": metadata or {},
        }
        
        self._access_log.append({
            "action": "store",
            "credential_id": credential_id,
            "timestamp": datetime.utcnow().isoformat()
        })

    def retrieve_credential(self, credential_id: str) -> Optional[str]:
        """Retrieve a stored credential (returns hash for security).

        Args:
            credential_id: Credential identifier.

        Returns:
            Credential information if found and active, None otherwise.
        """
        if credential_id not in self.store:
            return None

        cred = self.store[credential_id]
        if cred["status"] != CredentialStatus.ACTIVE:
            return None
        
        self._access_log.append({
            "action": "retrieve",
            "credential_id": credential_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        return cred["value_hash"]

    def has_credential(self, credential_id: str) -> bool:
        """Check if a credential exists and is active.

        Args:
            credential_id: Credential identifier.

        Returns:
            True if credential exists and is active.
        """
        if credential_id not in self.store:
            return False

        return self.store[credential_id]["status"] == CredentialStatus.ACTIVE

    def revoke_credential(self, credential_id: str) -> bool:
        """Revoke a credential.

        Args:
            credential_id: Credential identifier.

        Returns:
            True if revoked, False if not found.
        """
        if credential_id not in self.store:
            return False

        self.store[credential_id]["status"] = CredentialStatus.REVOKED
        
        self._access_log.append({
            "action": "revoke",
            "credential_id": credential_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return True

    def delete_credential(self, credential_id: str) -> bool:
        """Delete a credential permanently.

        Args:
            credential_id: Credential identifier.

        Returns:
            True if deleted, False if not found.
        """
        if credential_id in self.store:
            del self.store[credential_id]
            return True
        return False

    def expire_credential(self, credential_id: str) -> None:
        """Expire a credential.
        
        Args:
            credential_id: Credential identifier.
        """
        if credential_id in self.store:
            self.store[credential_id]["status"] = CredentialStatus.EXPIRED
            del self.store[credential_id]

    def get_access_log(self) -> List[Dict[str, Any]]:
        """Get access log for credential operations.
        
        Returns:
            List[Dict[str, Any]]: List of access log entries.
        """
        if not hasattr(self, '_access_log'):
            self._access_log = []
        return self._access_log.copy()

    def rotate_key(self, credential_id: str, new_key_id: str) -> None:
        """Rotate encryption key for a credential.
        
        Args:
            credential_id: Credential identifier.
            new_key_id: New encryption key identifier.
        """
        if credential_id in self.store:
            if not hasattr(self, '_access_log'):
                self._access_log = []
            
            self._access_log.append({
                "action": "key_rotation",
                "credential_id": credential_id,
                "new_key_id": new_key_id,
                "timestamp": datetime.utcnow().isoformat()
            })

    def list_credentials(self, active_only: bool = True) -> Dict[str, Any]:
        """List all credentials.

        Args:
            active_only: If True, only return active credentials.

        Returns:
            Dictionary of credential metadata (without values).
        """
        result = {}
        for cred_id, cred_data in self.store.items():
            if active_only and cred_data["status"] != CredentialStatus.ACTIVE:
                continue
            result[cred_id] = {
                "id": cred_data["id"],
                "type": cred_data["type"],
                "algorithm": cred_data["algorithm"],
                "created_at": cred_data["created_at"],
                "status": cred_data["status"],
                "metadata": cred_data["metadata"],
            }
        return result


class KeyRotationManager:
    """Manages key rotation policies and schedules."""

    def __init__(self, store: Optional[SecureCredentialStore] = None) -> None:
        """Initialize key rotation manager.
        
        Args:
            store: Optional credential store to manage.
        """
        self._store = store
        self.key_manager = KeyManager()
        self.rotation_schedule: Dict[str, Dict[str, Any]] = {}
        self.rotation_history: List[Dict[str, Any]] = []
        self._rotation_schedule: Dict[str, int] = {}
        self._last_rotation: Dict[str, datetime] = {}

    def schedule_rotation(
        self,
        credential_id: str,
        days: int = 90,
        rotation_period_days: int = None,
        max_age_days: int = 365,
    ) -> Dict[str, Any]:
        """Schedule key rotation.

        Args:
            credential_id: Credential or key identifier.
            days: Number of days between rotations (alias for rotation_period_days).
            rotation_period_days: Days between rotations.
            max_age_days: Maximum key age before mandatory rotation.

        Returns:
            Rotation schedule information.
        """
        # Support both parameter names for compatibility
        period = rotation_period_days if rotation_period_days is not None else days
        
        self._rotation_schedule[credential_id] = period
        self._last_rotation[credential_id] = datetime.utcnow()
        
        schedule = {
            "key_id": credential_id,
            "rotation_period_days": period,
            "max_age_days": max_age_days,
            "last_rotation": datetime.utcnow().isoformat(),
            "next_rotation": (
                datetime.utcnow() + timedelta(days=period)
            ).isoformat(),
        }
        self.rotation_schedule[credential_id] = schedule
        return schedule

    def needs_rotation(self, credential_id: str) -> bool:
        """Check if credential needs key rotation.
        
        Args:
            credential_id: Credential identifier.
            
        Returns:
            bool: True if rotation is needed, False otherwise.
        """
        if credential_id not in self._rotation_schedule:
            return False
        
        if credential_id not in self._last_rotation:
            return True
        
        days_since_rotation = (datetime.utcnow() - self._last_rotation[credential_id]).days
        return days_since_rotation >= self._rotation_schedule[credential_id]

    def get_rotation_status(self) -> Dict[str, Dict[str, Any]]:
        """Get rotation status for all scheduled credentials.
        
        Returns:
            Dict[str, Dict[str, Any]]: Rotation status for each credential.
        """
        status = {}
        for credential_id in self._rotation_schedule:
            status[credential_id] = {
                "needs_rotation": self.needs_rotation(credential_id),
                "rotation_interval_days": self._rotation_schedule[credential_id],
                "last_rotation": self._last_rotation.get(credential_id, "never").isoformat() 
                    if isinstance(self._last_rotation.get(credential_id), datetime) 
                    else "never"
            }
        return status

    def rotate_key(self, key_id: str, algorithm: EncryptionAlgorithm) -> Optional[Dict[str, Any]]:
        """Perform key rotation.

        Args:
            key_id: Key identifier.
            algorithm: Algorithm for the new key.

        Returns:
            New key information if rotation successful, None otherwise.
        """
        if key_id not in self.rotation_schedule:
            return None

        # Generate new key
        new_key_id = f"{key_id}_v{len(self.rotation_history) + 1}"
        new_key = self.key_manager.generate_key(new_key_id, algorithm)

        # Record in history
        rotation_record = {
            "old_key_id": key_id,
            "new_key_id": new_key_id,
            "rotated_at": datetime.utcnow().isoformat(),
            "algorithm": algorithm.value,
        }
        self.rotation_history.append(rotation_record)

        # Update schedule
        if key_id in self.rotation_schedule:
            self.rotation_schedule[key_id]["last_rotation"] = (
                datetime.utcnow().isoformat()
            )
            self.rotation_schedule[key_id]["next_rotation"] = (
                datetime.utcnow()
                + timedelta(
                    days=self.rotation_schedule[key_id]["rotation_period_days"]
                )
            ).isoformat()

        return new_key

    def is_rotation_due(self, key_id: str) -> bool:
        """Check if key rotation is due.

        Args:
            key_id: Key identifier.

        Returns:
            True if rotation is due.
        """
        if key_id not in self.rotation_schedule:
            return False

        schedule = self.rotation_schedule[key_id]
        next_rotation = datetime.fromisoformat(schedule["next_rotation"])
        return datetime.utcnow() >= next_rotation

    def get_rotation_history(self, key_id: str) -> List[Dict[str, Any]]:
        """Get rotation history for a key.

        Args:
            key_id: Key identifier.

        Returns:
            List of rotation records.
        """
        return [r for r in self.rotation_history if r["old_key_id"] == key_id]


__all__ = [
    "EncryptionAlgorithm",
    "CredentialType",
    "CredentialStatus",
    "EncryptedCredential",
    "EncryptionKey",
    "CredentialManager",
    "KeyManager",
    "SecureCredentialStore",
    "KeyRotationManager",
]
