"""Credential Protection - Secure credential storage and encryption.

Provides encryption key management, secure credential storage, and key rotation.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime, timedelta


class EncryptionAlgorithm(Enum):
    """Encryption algorithm types."""
    AES_128 = "AES-128"
    AES_256 = "AES-256"
    RSA_2048 = "RSA-2048"
    RSA_4096 = "RSA-4096"


class CredentialStatus(Enum):
    """Credential status types."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


@dataclass
class EncryptionKey:
    """Encryption key with metadata."""
    
    key_id: str
    algorithm: EncryptionAlgorithm
    ttl_days: int = 90
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        """Initialize expiration date."""
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(days=self.ttl_days)
    
    def is_expired(self) -> bool:
        """Check if key has expired.
        
        Returns:
            bool: True if expired, False otherwise.
        """
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if key is valid (active and not expired).
        
        Returns:
            bool: True if valid, False otherwise.
        """
        return self.is_active and not self.is_expired()


class SecureCredentialStore:
    """Secure storage for credentials with encryption."""
    
    def __init__(self) -> None:
        """Initialize credential store."""
        self._credentials: Dict[str, Dict[str, Any]] = {}
        self._keys: Dict[str, EncryptionKey] = {}
        self._access_log: List[Dict[str, Any]] = []
        self._default_key = EncryptionKey("default", EncryptionAlgorithm.AES_256)
        self._keys["default"] = self._default_key
    
    def store_credential(
        self, 
        credential_id: str, 
        value: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store a credential securely.
        
        Args:
            credential_id: Unique credential identifier.
            value: Credential value to store.
            metadata: Optional metadata for the credential.
            
        Raises:
            ValueError: If credential value is empty.
        """
        if not value:
            raise ValueError("Credential value cannot be empty")
        
        self._credentials[credential_id] = {
            "value": value,
            "metadata": metadata or {},
            "status": CredentialStatus.ACTIVE,
            "created_at": datetime.utcnow(),
            "key_id": "default"
        }
        
        self._access_log.append({
            "action": "store",
            "credential_id": credential_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def retrieve_credential(self, credential_id: str) -> Optional[str]:
        """Retrieve a credential.
        
        Args:
            credential_id: Credential identifier.
            
        Returns:
            Optional[str]: Credential value if found, None otherwise.
        """
        if credential_id not in self._credentials:
            return None
        
        cred = self._credentials[credential_id]
        if cred["status"] != CredentialStatus.ACTIVE:
            return None
        
        self._access_log.append({
            "action": "retrieve",
            "credential_id": credential_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return cred["value"]
    
    def has_credential(self, credential_id: str) -> bool:
        """Check if credential exists and is active.
        
        Args:
            credential_id: Credential identifier.
            
        Returns:
            bool: True if credential exists and is active, False otherwise.
        """
        if credential_id not in self._credentials:
            return False
        return self._credentials[credential_id]["status"] == CredentialStatus.ACTIVE
    
    def revoke_credential(self, credential_id: str) -> None:
        """Revoke a credential.
        
        Args:
            credential_id: Credential identifier.
        """
        if credential_id in self._credentials:
            self._credentials[credential_id]["status"] = CredentialStatus.REVOKED
            del self._credentials[credential_id]
            
            self._access_log.append({
                "action": "revoke",
                "credential_id": credential_id,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def expire_credential(self, credential_id: str) -> None:
        """Expire a credential.
        
        Args:
            credential_id: Credential identifier.
        """
        if credential_id in self._credentials:
            self._credentials[credential_id]["status"] = CredentialStatus.EXPIRED
            del self._credentials[credential_id]
            
            self._access_log.append({
                "action": "expire",
                "credential_id": credential_id,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def get_access_log(self) -> List[Dict[str, Any]]:
        """Get access log for credential operations.
        
        Returns:
            List[Dict[str, Any]]: List of access log entries.
        """
        return self._access_log.copy()
    
    def rotate_key(self, credential_id: str, new_key_id: str) -> None:
        """Rotate encryption key for a credential.
        
        Args:
            credential_id: Credential identifier.
            new_key_id: New encryption key identifier.
        """
        if credential_id in self._credentials and new_key_id in self._keys:
            self._credentials[credential_id]["key_id"] = new_key_id
            
            self._access_log.append({
                "action": "key_rotation",
                "credential_id": credential_id,
                "new_key_id": new_key_id,
                "timestamp": datetime.utcnow().isoformat()
            })


class KeyRotationManager:
    """Manages encryption key rotation."""
    
    def __init__(self, store: SecureCredentialStore) -> None:
        """Initialize key rotation manager.
        
        Args:
            store: Credential store to manage.
        """
        self._store = store
        self._rotation_schedule: Dict[str, int] = {}
        self._last_rotation: Dict[str, datetime] = {}
    
    def schedule_rotation(self, credential_id: str, days: int) -> None:
        """Schedule key rotation for a credential.
        
        Args:
            credential_id: Credential identifier.
            days: Number of days between rotations.
        """
        self._rotation_schedule[credential_id] = days
        self._last_rotation[credential_id] = datetime.utcnow()
    
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


__all__ = [
    "EncryptionAlgorithm",
    "CredentialStatus",
    "EncryptionKey",
    "SecureCredentialStore",
    "KeyRotationManager",
]
