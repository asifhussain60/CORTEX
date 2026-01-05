"""
Task 4.2: Encryptor Tests (TDD RED Phase)

Production-grade encryption for audit logs with:
- AES-256-GCM encryption/decryption
- Fernet fallback encryption
- Key management and rotation
- Tamper detection (MAC verification)
- Compliance (GDPR, HIPAA, SOC 2)

Author: Asif Hussain
Date: January 5, 2026
Status: RED (Tests failing - implementation pending)
"""

import pytest
import json
import time
from pathlib import Path
from typing import Dict, Any

# Import will fail initially (RED phase)
from src.audit_logger.security.encryptor import (
    Encryptor,
    KeyManager,
    TamperDetectedError,
    KeyNotFoundError,
    InvalidAlgorithmError
)


class TestEncryptor:
    """Test suite for Encryptor class"""
    
    @pytest.fixture
    def temp_key_file(self, tmp_path: Path) -> Path:
        """Create temporary key file"""
        return tmp_path / "test_keys.json"
    
    @pytest.fixture
    def encryptor(self, temp_key_file: Path) -> Encryptor:
        """Create Encryptor instance with AES-256-GCM"""
        return Encryptor(key_file=temp_key_file, algorithm='AES-256-GCM')
    
    @pytest.fixture
    def encryptor_fernet(self, temp_key_file: Path) -> Encryptor:
        """Create Encryptor instance with Fernet"""
        return Encryptor(key_file=temp_key_file, algorithm='Fernet')
    
    # ========== Basic Encryption/Decryption Tests ==========
    
    def test_encrypt_decrypt_aes_gcm(self, encryptor: Encryptor):
        """Test AES-256-GCM encryption and decryption"""
        plaintext = "Sensitive audit log data"
        
        encrypted = encryptor.encrypt(plaintext)
        decrypted = encryptor.decrypt(encrypted)
        
        assert decrypted == plaintext
        assert isinstance(encrypted, dict)
        assert encrypted['algorithm'] == 'AES-256-GCM'
    
    def test_encrypt_decrypt_fernet(self, encryptor_fernet: Encryptor):
        """Test Fernet encryption and decryption"""
        plaintext = "Sensitive audit log data"
        
        encrypted = encryptor_fernet.encrypt(plaintext)
        decrypted = encryptor_fernet.decrypt(encrypted)
        
        assert decrypted == plaintext
        assert isinstance(encrypted, dict)
        assert encrypted['algorithm'] == 'Fernet'
    
    def test_encrypt_empty_string(self, encryptor: Encryptor):
        """Test encryption of empty string"""
        encrypted = encryptor.encrypt("")
        decrypted = encryptor.decrypt(encrypted)
        assert decrypted == ""
    
    def test_encrypt_unicode_data(self, encryptor: Encryptor):
        """Test encryption of Unicode data"""
        plaintext = "Unicode: 你好世界 🌍 Émojis 🎉"
        encrypted = encryptor.encrypt(plaintext)
        decrypted = encryptor.decrypt(encrypted)
        assert decrypted == plaintext
    
    def test_encrypt_large_data(self, encryptor: Encryptor):
        """Test encryption of large data (1 MB)"""
        plaintext = "A" * (1024 * 1024)  # 1 MB
        encrypted = encryptor.encrypt(plaintext)
        decrypted = encryptor.decrypt(encrypted)
        assert decrypted == plaintext
    
    # ========== Encrypted Message Format Tests ==========
    
    def test_encrypted_format_structure(self, encryptor: Encryptor):
        """Test encrypted message has required fields"""
        encrypted = encryptor.encrypt("Test data")
        
        # Required fields
        assert 'version' in encrypted
        assert 'algorithm' in encrypted
        assert 'encrypted_data' in encrypted
        assert 'nonce' in encrypted
        assert 'tag' in encrypted
        assert 'key_id' in encrypted
        assert 'timestamp' in encrypted
        
        # Field types
        assert isinstance(encrypted['version'], str)
        assert isinstance(encrypted['algorithm'], str)
        assert isinstance(encrypted['encrypted_data'], str)
        assert isinstance(encrypted['nonce'], str)
        assert isinstance(encrypted['tag'], str)
        assert isinstance(encrypted['key_id'], str)
        assert isinstance(encrypted['timestamp'], (int, float))
    
    def test_encrypted_format_values(self, encryptor: Encryptor):
        """Test encrypted message field values"""
        encrypted = encryptor.encrypt("Test data")
        
        assert encrypted['version'] == '1.0'
        assert encrypted['algorithm'] == 'AES-256-GCM'
        assert len(encrypted['nonce']) > 0  # Base64 encoded
        assert len(encrypted['tag']) > 0  # Base64 encoded
        assert encrypted['timestamp'] > 0
    
    def test_encrypted_metadata(self, encryptor: Encryptor):
        """Test encrypted message with metadata"""
        plaintext = "Test data"
        metadata = {'sanitized': True, 'log_level': 'INFO'}
        
        encrypted = encryptor.encrypt(plaintext, metadata=metadata)
        
        assert 'metadata' in encrypted
        assert encrypted['metadata'] == metadata
    
    # ========== Tamper Detection Tests ==========
    
    def test_tamper_detection_modified_ciphertext(self, encryptor: Encryptor):
        """Test tamper detection with modified ciphertext"""
        encrypted = encryptor.encrypt("Original data")
        
        # Tamper with encrypted data
        encrypted['encrypted_data'] = 'TAMPERED'
        
        with pytest.raises(TamperDetectedError):
            encryptor.decrypt(encrypted)
    
    def test_tamper_detection_modified_nonce(self, encryptor: Encryptor):
        """Test tamper detection with modified nonce"""
        encrypted = encryptor.encrypt("Original data")
        
        # Tamper with nonce
        encrypted['nonce'] = 'TAMPERED'
        
        with pytest.raises(TamperDetectedError):
            encryptor.decrypt(encrypted)
    
    def test_tamper_detection_modified_tag(self, encryptor: Encryptor):
        """Test tamper detection with modified tag"""
        encrypted = encryptor.encrypt("Original data")
        
        # Tamper with authentication tag
        encrypted['tag'] = 'TAMPERED'
        
        with pytest.raises(TamperDetectedError):
            encryptor.decrypt(encrypted)
    
    def test_integrity_verification(self, encryptor: Encryptor):
        """Test integrity verification of encrypted message"""
        encrypted = encryptor.encrypt("Test data")
        
        # Valid message
        assert encryptor.verify_integrity(encrypted) is True
        
        # Missing fields
        invalid = encrypted.copy()
        del invalid['nonce']
        assert encryptor.verify_integrity(invalid) is False
    
    # ========== Key Management Tests ==========
    
    def test_key_generation(self, temp_key_file: Path):
        """Test key generation on initialization"""
        encryptor = Encryptor(key_file=temp_key_file)
        
        # Key file should be created
        assert temp_key_file.exists()
        
        # Key file should have correct permissions (0o600)
        import stat
        mode = temp_key_file.stat().st_mode
        assert stat.S_IMODE(mode) == 0o600
    
    def test_key_persistence(self, temp_key_file: Path):
        """Test keys are persisted across instances"""
        encryptor1 = Encryptor(key_file=temp_key_file)
        plaintext = "Test data"
        encrypted = encryptor1.encrypt(plaintext)
        
        # Create new instance with same key file
        encryptor2 = Encryptor(key_file=temp_key_file)
        decrypted = encryptor2.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_key_rotation(self, encryptor: Encryptor):
        """Test key rotation and backward compatibility"""
        plaintext = "Test data"
        
        # Encrypt with initial key
        encrypted_old = encryptor.encrypt(plaintext)
        old_key_id = encrypted_old['key_id']
        
        # Rotate key
        new_key_id = encryptor.rotate_keys()
        
        # New key should be different
        assert new_key_id != old_key_id
        
        # Old encrypted data should still decrypt
        decrypted = encryptor.decrypt(encrypted_old)
        assert decrypted == plaintext
        
        # New encryptions use new key
        encrypted_new = encryptor.encrypt(plaintext)
        assert encrypted_new['key_id'] == new_key_id
    
    def test_multiple_key_rotations(self, encryptor: Encryptor):
        """Test multiple key rotations"""
        plaintext = "Test data"
        encrypted_messages = []
        
        # Create encrypted messages with 3 different keys
        for i in range(3):
            encrypted = encryptor.encrypt(f"{plaintext} {i}")
            encrypted_messages.append(encrypted)
            encryptor.rotate_keys()
        
        # All messages should still decrypt
        for i, encrypted in enumerate(encrypted_messages):
            decrypted = encryptor.decrypt(encrypted)
            assert decrypted == f"{plaintext} {i}"
    
    def test_key_not_found_error(self, encryptor: Encryptor):
        """Test decryption with non-existent key"""
        encrypted = encryptor.encrypt("Test data")
        
        # Modify key_id to non-existent key
        encrypted['key_id'] = 'non-existent-key-12345'
        
        with pytest.raises(KeyNotFoundError):
            encryptor.decrypt(encrypted)
    
    # ========== Algorithm Tests ==========
    
    def test_invalid_algorithm(self, temp_key_file: Path):
        """Test initialization with invalid algorithm"""
        with pytest.raises(InvalidAlgorithmError):
            Encryptor(key_file=temp_key_file, algorithm='INVALID')
    
    def test_supported_algorithms(self, temp_key_file: Path):
        """Test all supported algorithms"""
        algorithms = ['AES-256-GCM', 'Fernet']
        
        for algo in algorithms:
            encryptor = Encryptor(key_file=temp_key_file, algorithm=algo)
            encrypted = encryptor.encrypt("Test data")
            assert encrypted['algorithm'] == algo
    
    # ========== Error Handling Tests ==========
    
    def test_decrypt_invalid_format(self, encryptor: Encryptor):
        """Test decryption with invalid format"""
        invalid_encrypted = {'invalid': 'format'}
        
        with pytest.raises(ValueError):
            encryptor.decrypt(invalid_encrypted)
    
    def test_decrypt_missing_fields(self, encryptor: Encryptor):
        """Test decryption with missing required fields"""
        incomplete = {
            'version': '1.0',
            'algorithm': 'AES-256-GCM',
            # Missing other required fields
        }
        
        with pytest.raises(ValueError):
            encryptor.decrypt(incomplete)
    
    # ========== Performance Tests ==========
    
    def test_encryption_performance(self, encryptor: Encryptor):
        """Test encryption performance (<1ms per operation)"""
        plaintext = "Test audit log entry"
        iterations = 100
        
        start_time = time.perf_counter()
        for _ in range(iterations):
            encryptor.encrypt(plaintext)
        elapsed = time.perf_counter() - start_time
        
        avg_time = elapsed / iterations
        assert avg_time < 0.001, f"Encryption too slow: {avg_time*1000:.2f}ms"
    
    def test_decryption_performance(self, encryptor: Encryptor):
        """Test decryption performance (<1ms per operation)"""
        plaintext = "Test audit log entry"
        encrypted = encryptor.encrypt(plaintext)
        iterations = 100
        
        start_time = time.perf_counter()
        for _ in range(iterations):
            encryptor.decrypt(encrypted)
        elapsed = time.perf_counter() - start_time
        
        avg_time = elapsed / iterations
        assert avg_time < 0.001, f"Decryption too slow: {avg_time*1000:.2f}ms"


class TestKeyManager:
    """Test suite for KeyManager class"""
    
    @pytest.fixture
    def temp_key_file(self, tmp_path: Path) -> Path:
        """Create temporary key file"""
        return tmp_path / "test_keys.json"
    
    @pytest.fixture
    def key_manager(self, temp_key_file: Path) -> KeyManager:
        """Create KeyManager instance"""
        return KeyManager(key_file=temp_key_file)
    
    def test_generate_new_key(self, key_manager: KeyManager):
        """Test new key generation"""
        key_id = key_manager.generate_new_key()
        
        assert isinstance(key_id, str)
        assert len(key_id) > 0
        
        # Key should be retrievable
        key = key_manager.get_key(key_id)
        assert isinstance(key, bytes)
        assert len(key) == 32  # 256 bits
    
    def test_active_key_management(self, key_manager: KeyManager):
        """Test active key management"""
        key_id1 = key_manager.generate_new_key()
        key_manager.set_active_key(key_id1)
        
        assert key_manager.active_key_id == key_id1
        
        key_id2 = key_manager.generate_new_key()
        key_manager.set_active_key(key_id2)
        
        assert key_manager.active_key_id == key_id2
    
    def test_key_revocation(self, key_manager: KeyManager):
        """Test key revocation"""
        key_id = key_manager.generate_new_key()
        
        # Key should exist
        assert key_manager.has_key(key_id)
        
        # Revoke key
        key_manager.revoke_key(key_id)
        
        # Key should still exist but be inactive
        assert key_manager.has_key(key_id)
        key_info = key_manager.get_key_info(key_id)
        assert key_info['status'] == 'revoked'
    
    def test_key_file_persistence(self, temp_key_file: Path):
        """Test key file persistence"""
        # Create keys with first manager
        manager1 = KeyManager(key_file=temp_key_file)
        key_id = manager1.generate_new_key()
        
        # Load keys with second manager
        manager2 = KeyManager(key_file=temp_key_file)
        
        # Should have same key
        assert manager2.has_key(key_id)
        assert manager2.get_key(key_id) == manager1.get_key(key_id)
    
    def test_multiple_keys(self, key_manager: KeyManager):
        """Test managing multiple keys"""
        key_ids = [key_manager.generate_new_key() for _ in range(5)]
        
        # All keys should be accessible
        for key_id in key_ids:
            assert key_manager.has_key(key_id)
            key = key_manager.get_key(key_id)
            assert len(key) == 32
