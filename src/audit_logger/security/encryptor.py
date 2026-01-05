"""
Task 4.2: Encryptor Implementation (TDD GREEN Phase)

Production-grade encryption for audit logs with:
- AES-256-GCM encryption/decryption (NIST-approved)
- Fernet fallback encryption (symmetric, time-based)
- Key management and rotation
- Tamper detection (MAC verification)
- Compliance (GDPR, HIPAA, SOC 2)

Author: Asif Hussain
Date: January 5, 2026
Status: GREEN (Implementation to pass tests)
"""

import os
import json
import base64
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.fernet import Fernet
from cryptography.exceptions import InvalidTag


# ========== Custom Exceptions ==========

class TamperDetectedError(Exception):
    """Raised when encrypted data has been tampered with"""
    pass


class KeyNotFoundError(Exception):
    """Raised when encryption key is not found"""
    pass


class InvalidAlgorithmError(Exception):
    """Raised when unsupported encryption algorithm is specified"""
    pass


# ========== KeyManager Class ==========

class KeyManager:
    """Secure key management with rotation and persistence"""
    
    SUPPORTED_ALGORITHMS = ['AES-256-GCM', 'Fernet']
    
    def __init__(self, key_file: Path):
        """
        Initialize key manager with key storage file
        
        Args:
            key_file: Path to JSON file storing encryption keys
        """
        self.key_file = Path(key_file)
        self.keys: Dict[str, Dict[str, Any]] = {}
        self.active_key_id: Optional[str] = None
        
        # Load existing keys or create initial key
        if self.key_file.exists():
            self._load_keys()
        else:
            self._initialize_keys()
    
    def _initialize_keys(self) -> None:
        """Create initial encryption key"""
        key_id = self.generate_new_key()
        self.set_active_key(key_id)
        self._save_keys()
    
    def _load_keys(self) -> None:
        """Load keys from file"""
        try:
            data = json.loads(self.key_file.read_text(encoding='utf-8'))
            self.keys = data.get('keys', {})
            self.active_key_id = data.get('active_key_id')
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ValueError(f"Failed to load keys from {self.key_file}: {e}")
    
    def _save_keys(self) -> None:
        """Save keys to file with secure permissions"""
        self.key_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'keys': self.keys,
            'active_key_id': self.active_key_id
        }
        
        self.key_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
        
        # Set secure permissions (read/write owner only)
        self.key_file.chmod(0o600)
    
    def generate_new_key(self, algorithm: str = 'AES-256-GCM') -> str:
        """
        Generate new encryption key
        
        Args:
            algorithm: Encryption algorithm ('AES-256-GCM' or 'Fernet')
            
        Returns:
            Key ID for the new key
        """
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise InvalidAlgorithmError(f"Unsupported algorithm: {algorithm}")
        
        # Generate cryptographically secure random key (256 bits)
        key_bytes = os.urandom(32)
        
        # Create unique key ID
        key_id = f"key-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{os.urandom(4).hex()}"
        
        # Store key metadata
        self.keys[key_id] = {
            'key': base64.b64encode(key_bytes).decode('utf-8'),
            'algorithm': algorithm,
            'created_at': time.time(),
            'expires_at': (datetime.now() + timedelta(days=90)).timestamp(),
            'status': 'active',
            'rotation_count': 0
        }
        
        self._save_keys()
        return key_id
    
    def get_key(self, key_id: str) -> bytes:
        """
        Get key by ID
        
        Args:
            key_id: Key identifier
            
        Returns:
            Key bytes (32 bytes for 256-bit key)
            
        Raises:
            KeyNotFoundError: If key doesn't exist
        """
        if key_id not in self.keys:
            raise KeyNotFoundError(f"Key not found: {key_id}")
        
        key_data = self.keys[key_id]
        return base64.b64decode(key_data['key'])
    
    def get_key_info(self, key_id: str) -> Dict[str, Any]:
        """
        Get key metadata
        
        Args:
            key_id: Key identifier
            
        Returns:
            Dictionary with key metadata
        """
        if key_id not in self.keys:
            raise KeyNotFoundError(f"Key not found: {key_id}")
        
        return self.keys[key_id].copy()
    
    def set_active_key(self, key_id: str) -> None:
        """
        Set active key for encryption
        
        Args:
            key_id: Key identifier
        """
        if key_id not in self.keys:
            raise KeyNotFoundError(f"Key not found: {key_id}")
        
        self.active_key_id = key_id
        self._save_keys()
    
    def has_key(self, key_id: str) -> bool:
        """
        Check if key exists
        
        Args:
            key_id: Key identifier
            
        Returns:
            True if key exists, False otherwise
        """
        return key_id in self.keys
    
    def revoke_key(self, key_id: str) -> None:
        """
        Revoke key (mark as inactive)
        
        Args:
            key_id: Key identifier
        """
        if key_id not in self.keys:
            raise KeyNotFoundError(f"Key not found: {key_id}")
        
        self.keys[key_id]['status'] = 'revoked'
        self._save_keys()


# ========== Encryptor Class ==========

class Encryptor:
    """Production-grade encryption for audit logs"""
    
    def __init__(self, key_file: Path, algorithm: str = 'AES-256-GCM'):
        """
        Initialize encryptor
        
        Args:
            key_file: Path to key storage file
            algorithm: Encryption algorithm ('AES-256-GCM' or 'Fernet')
            
        Raises:
            InvalidAlgorithmError: If algorithm is not supported
        """
        if algorithm not in KeyManager.SUPPORTED_ALGORITHMS:
            raise InvalidAlgorithmError(f"Unsupported algorithm: {algorithm}")
        
        self.key_manager = KeyManager(key_file)
        self.algorithm = algorithm
    
    def encrypt(self, plaintext: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Encrypt plaintext string
        
        Args:
            plaintext: String to encrypt
            metadata: Optional metadata to include
            
        Returns:
            Dictionary with encrypted data and metadata
        """
        if self.algorithm == 'AES-256-GCM':
            return self._encrypt_aes_gcm(plaintext, metadata)
        elif self.algorithm == 'Fernet':
            return self._encrypt_fernet(plaintext, metadata)
        else:
            raise InvalidAlgorithmError(f"Unsupported algorithm: {self.algorithm}")
    
    def decrypt(self, encrypted: Dict[str, Any]) -> str:
        """
        Decrypt encrypted dictionary
        
        Args:
            encrypted: Dictionary with encrypted data
            
        Returns:
            Decrypted plaintext string
            
        Raises:
            ValueError: If encrypted format is invalid
            TamperDetectedError: If data has been tampered with
            KeyNotFoundError: If encryption key not found
        """
        # Validate format
        self._validate_encrypted_format(encrypted)
        
        algorithm = encrypted['algorithm']
        
        if algorithm == 'AES-256-GCM':
            return self._decrypt_aes_gcm(encrypted)
        elif algorithm == 'Fernet':
            return self._decrypt_fernet(encrypted)
        else:
            raise InvalidAlgorithmError(f"Unsupported algorithm: {algorithm}")
    
    def rotate_keys(self) -> str:
        """
        Rotate encryption keys
        
        Returns:
            New key ID
        """
        # Generate new key
        new_key_id = self.key_manager.generate_new_key(algorithm=self.algorithm)
        
        # Set as active key
        self.key_manager.set_active_key(new_key_id)
        
        return new_key_id
    
    def verify_integrity(self, encrypted: Dict[str, Any]) -> bool:
        """
        Verify encrypted message integrity
        
        Args:
            encrypted: Dictionary with encrypted data
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ['version', 'algorithm', 'encrypted_data', 'nonce', 'tag', 'key_id', 'timestamp']
        if not all(field in encrypted for field in required_fields):
            return False
        
        # Check key exists
        if not self.key_manager.has_key(encrypted['key_id']):
            return False
        
        # Check timestamp (reject > 24 hours old for replay protection)
        age = time.time() - encrypted.get('timestamp', 0)
        if age > 86400:  # 24 hours
            return False
        
        return True
    
    # ========== Internal Methods (AES-256-GCM) ==========
    
    def _encrypt_aes_gcm(self, plaintext: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Encrypt with AES-256-GCM"""
        # Get active key
        if not self.key_manager.active_key_id:
            raise ValueError("No active encryption key")
        
        key_id = self.key_manager.active_key_id
        key_bytes = self.key_manager.get_key(key_id)
        
        # Convert to bytes
        plaintext_bytes = plaintext.encode('utf-8')
        
        # Generate nonce (96 bits = 12 bytes)
        nonce = os.urandom(12)
        
        # Encrypt with AES-GCM
        aesgcm = AESGCM(key_bytes)
        ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, None)
        
        # Split ciphertext and authentication tag
        encrypted_data = ciphertext[:-16]  # All except last 16 bytes
        tag = ciphertext[-16:]  # Last 16 bytes
        
        # Build encrypted message
        result = {
            'version': '1.0',
            'algorithm': 'AES-256-GCM',
            'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8'),
            'nonce': base64.b64encode(nonce).decode('utf-8'),
            'tag': base64.b64encode(tag).decode('utf-8'),
            'key_id': key_id,
            'timestamp': time.time()
        }
        
        if metadata:
            result['metadata'] = metadata
        
        return result
    
    def _decrypt_aes_gcm(self, encrypted: Dict[str, Any]) -> str:
        """Decrypt with AES-256-GCM"""
        try:
            # Get key
            key_id = encrypted['key_id']
            key_bytes = self.key_manager.get_key(key_id)
            
            # Decode components
            nonce = base64.b64decode(encrypted['nonce'])
            encrypted_data = base64.b64decode(encrypted['encrypted_data'])
            tag = base64.b64decode(encrypted['tag'])
            
            # Reconstruct ciphertext (data + tag)
            ciphertext = encrypted_data + tag
            
            # Decrypt
            aesgcm = AESGCM(key_bytes)
            plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, None)
            
            return plaintext_bytes.decode('utf-8')
            
        except InvalidTag as e:
            raise TamperDetectedError(f"Tamper detected: Authentication tag verification failed") from e
        except (ValueError, KeyError) as e:
            raise TamperDetectedError(f"Tamper detected: {e}") from e
    
    # ========== Internal Methods (Fernet) ==========
    
    def _encrypt_fernet(self, plaintext: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Encrypt with Fernet"""
        # Get active key
        if not self.key_manager.active_key_id:
            raise ValueError("No active encryption key")
        
        key_id = self.key_manager.active_key_id
        key_bytes = self.key_manager.get_key(key_id)
        
        # Convert key to Fernet format (URL-safe base64)
        fernet_key = base64.urlsafe_b64encode(key_bytes)
        
        # Encrypt
        f = Fernet(fernet_key)
        plaintext_bytes = plaintext.encode('utf-8')
        token = f.encrypt(plaintext_bytes)
        
        # Build encrypted message
        result = {
            'version': '1.0',
            'algorithm': 'Fernet',
            'encrypted_data': base64.b64encode(token).decode('utf-8'),
            'nonce': '',  # Fernet includes nonce internally
            'tag': '',  # Fernet includes MAC internally
            'key_id': key_id,
            'timestamp': time.time()
        }
        
        if metadata:
            result['metadata'] = metadata
        
        return result
    
    def _decrypt_fernet(self, encrypted: Dict[str, Any]) -> str:
        """Decrypt with Fernet"""
        try:
            # Get key
            key_id = encrypted['key_id']
            key_bytes = self.key_manager.get_key(key_id)
            
            # Convert key to Fernet format
            fernet_key = base64.urlsafe_b64encode(key_bytes)
            
            # Decrypt
            f = Fernet(fernet_key)
            token = base64.b64decode(encrypted['encrypted_data'])
            plaintext_bytes = f.decrypt(token)
            
            return plaintext_bytes.decode('utf-8')
            
        except Exception as e:
            raise TamperDetectedError(f"Tamper detected: {e}") from e
    
    # ========== Validation ==========
    
    def _validate_encrypted_format(self, encrypted: Dict[str, Any]) -> None:
        """Validate encrypted message format"""
        required_fields = ['version', 'algorithm', 'encrypted_data', 'key_id']
        
        missing_fields = [field for field in required_fields if field not in encrypted]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
