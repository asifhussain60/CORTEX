"""
Log Encryptor - Encryption at Rest for Audit Logs

Provides AES-256-GCM encryption for sensitive log files with:
- Key rotation support
- Secure key storage (environment variables or key management service)
- Per-file encryption with unique IVs
- Integrity verification (GCM mode provides authentication)

Author: Asif Hussain
Created: 2026-01-05
"""

import os
import base64
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pathlib import Path
import json


class LogEncryptor:
    """
    Encrypts and decrypts audit log files using AES-256-GCM.
    
    Features:
    - AES-256-GCM (authenticated encryption)
    - Unique IV per file
    - Key derivation from password (PBKDF2)
    - Key rotation support
    - Integrity verification
    """
    
    def __init__(self, key: Optional[bytes] = None, password: Optional[str] = None):
        """
        Initialize the encryptor.
        
        Args:
            key: 32-byte encryption key (if provided, password is ignored)
            password: Password for key derivation (if key not provided)
        
        Raises:
            ValueError: If neither key nor password provided
        """
        if key is not None:
            if len(key) != 32:
                raise ValueError("Encryption key must be 32 bytes for AES-256")
            self._key = key
        elif password is not None:
            self._key = self._derive_key_from_password(password)
        else:
            # Try to load from environment variable
            env_key = os.environ.get('CORTEX_AUDIT_ENCRYPTION_KEY')
            if env_key:
                self._key = base64.b64decode(env_key)
            else:
                raise ValueError("Must provide either key, password, or set CORTEX_AUDIT_ENCRYPTION_KEY environment variable")
        
        self._aesgcm = AESGCM(self._key)
    
    @staticmethod
    def _derive_key_from_password(password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Derive a 32-byte encryption key from a password using PBKDF2.
        
        Args:
            password: The password to derive from
            salt: Optional salt (if None, a default salt is used - NOT RECOMMENDED for production)
        
        Returns:
            32-byte derived key
        """
        if salt is None:
            # Default salt - ONLY for development/testing
            # In production, use a unique salt per user/system
            salt = b'cortex_audit_logger_salt_v1'
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # OWASP recommendation
        )
        return kdf.derive(password.encode())
    
    @staticmethod
    def generate_key() -> bytes:
        """
        Generate a random 32-byte encryption key.
        
        Returns:
            Random 32-byte key suitable for AES-256
        """
        return AESGCM.generate_key(bit_length=256)
    
    def encrypt(self, plaintext: bytes, associated_data: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Encrypt data using AES-256-GCM.
        
        Args:
            plaintext: The data to encrypt
            associated_data: Optional additional authenticated data (AAD)
        
        Returns:
            Tuple of (nonce, ciphertext)
        """
        # Generate a random 96-bit nonce (12 bytes is optimal for GCM)
        nonce = os.urandom(12)
        
        # Encrypt
        ciphertext = self._aesgcm.encrypt(nonce, plaintext, associated_data)
        
        return nonce, ciphertext
    
    def decrypt(self, nonce: bytes, ciphertext: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """
        Decrypt data using AES-256-GCM.
        
        Args:
            nonce: The nonce used during encryption
            ciphertext: The encrypted data
            associated_data: Optional additional authenticated data (AAD)
        
        Returns:
            Decrypted plaintext
        
        Raises:
            cryptography.exceptions.InvalidTag: If authentication fails
        """
        return self._aesgcm.decrypt(nonce, ciphertext, associated_data)
    
    def encrypt_file(self, input_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Encrypt a log file.
        
        Args:
            input_path: Path to the plaintext log file
            output_path: Path for encrypted file (if None, adds .enc extension)
        
        Returns:
            Path to the encrypted file
        """
        if output_path is None:
            output_path = input_path.with_suffix(input_path.suffix + '.enc')
        
        # Read plaintext
        with open(input_path, 'rb') as f:
            plaintext = f.read()
        
        # Encrypt
        nonce, ciphertext = self.encrypt(plaintext)
        
        # Write encrypted file with metadata
        with open(output_path, 'wb') as f:
            # Write nonce length (4 bytes)
            f.write(len(nonce).to_bytes(4, 'big'))
            # Write nonce
            f.write(nonce)
            # Write ciphertext
            f.write(ciphertext)
        
        return output_path
    
    def decrypt_file(self, input_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Decrypt an encrypted log file.
        
        Args:
            input_path: Path to the encrypted log file
            output_path: Path for decrypted file (if None, removes .enc extension)
        
        Returns:
            Path to the decrypted file
        
        Raises:
            cryptography.exceptions.InvalidTag: If decryption fails (corrupted or tampered)
        """
        if output_path is None:
            if input_path.suffix == '.enc':
                output_path = input_path.with_suffix('')
            else:
                output_path = input_path.with_suffix('.dec')
        
        # Read encrypted file
        with open(input_path, 'rb') as f:
            # Read nonce length
            nonce_len = int.from_bytes(f.read(4), 'big')
            # Read nonce
            nonce = f.read(nonce_len)
            # Read ciphertext
            ciphertext = f.read()
        
        # Decrypt
        plaintext = self.decrypt(nonce, ciphertext)
        
        # Write decrypted file
        with open(output_path, 'wb') as f:
            f.write(plaintext)
        
        return output_path
    
    def rotate_key(self, new_key: bytes, log_directory: Path):
        """
        Rotate encryption keys by re-encrypting all logs with a new key.
        
        Args:
            new_key: The new 32-byte encryption key
            log_directory: Directory containing encrypted log files
        
        Note:
            This is a potentially expensive operation. Consider doing this
            during maintenance windows or asynchronously.
        """
        if len(new_key) != 32:
            raise ValueError("New key must be 32 bytes for AES-256")
        
        # Create new encryptor with new key
        new_encryptor = LogEncryptor(key=new_key)
        
        # Find all encrypted files
        encrypted_files = list(log_directory.rglob('*.enc'))
        
        for enc_file in encrypted_files:
            # Decrypt with old key
            temp_decrypted = enc_file.with_suffix('.temp_dec')
            self.decrypt_file(enc_file, temp_decrypted)
            
            # Re-encrypt with new key
            new_encryptor.encrypt_file(temp_decrypted, enc_file)
            
            # Clean up temporary file
            temp_decrypted.unlink()
        
        # Update our key
        self._key = new_key
        self._aesgcm = AESGCM(self._key)


class EncryptionManager:
    """
    High-level encryption management for audit logs.
    
    Handles:
    - Automatic encryption of sensitive logs
    - Key management
    - Encryption policy enforcement
    """
    
    def __init__(self, encryptor: LogEncryptor, encrypt_by_default: bool = False):
        """
        Initialize the encryption manager.
        
        Args:
            encryptor: LogEncryptor instance
            encrypt_by_default: If True, encrypt all logs by default
        """
        self.encryptor = encryptor
        self.encrypt_by_default = encrypt_by_default
        self._encrypted_files = set()
    
    def should_encrypt(self, log_path: Path, log_level: str = 'INFO') -> bool:
        """
        Determine if a log file should be encrypted.
        
        Args:
            log_path: Path to the log file
            log_level: Log level (ERROR, WARNING, etc.)
        
        Returns:
            True if the file should be encrypted
        """
        # Always encrypt ERROR and CRITICAL logs
        if log_level in ('ERROR', 'CRITICAL'):
            return True
        
        # Always encrypt files with 'sensitive' in the name
        if 'sensitive' in log_path.name.lower() or 'security' in log_path.name.lower():
            return True
        
        # Otherwise, follow default policy
        return self.encrypt_by_default
    
    def encrypt_if_needed(self, log_path: Path, log_level: str = 'INFO') -> Optional[Path]:
        """
        Encrypt a log file if it meets encryption criteria.
        
        Args:
            log_path: Path to the log file
            log_level: Log level
        
        Returns:
            Path to encrypted file if encrypted, None otherwise
        """
        if self.should_encrypt(log_path, log_level):
            enc_path = self.encryptor.encrypt_file(log_path)
            self._encrypted_files.add(enc_path)
            
            # Optionally delete the plaintext file (security policy dependent)
            # log_path.unlink()
            
            return enc_path
        return None
    
    def get_encrypted_files(self) -> set:
        """Get the set of encrypted file paths"""
        return self._encrypted_files.copy()


# Global singleton instance
_encryptor_instance = None


def get_encryptor(password: Optional[str] = None) -> LogEncryptor:
    """
    Get the global LogEncryptor instance (singleton pattern).
    
    Args:
        password: Optional password for key derivation
    
    Returns:
        LogEncryptor instance
    """
    global _encryptor_instance
    if _encryptor_instance is None:
        _encryptor_instance = LogEncryptor(password=password)
    return _encryptor_instance
