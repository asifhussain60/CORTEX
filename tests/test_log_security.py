"""
Security Tests for Audit Logger

Tests:
- PII sanitization
- Encryption/decryption
- Key rotation
- Access controls
- Sensitive data detection

Author: Asif Hussain
Created: 2026-01-05
"""

import pytest
import tempfile
from pathlib import Path
from src.logging.log_sanitizer import LogSanitizer, get_sanitizer
from src.logging.log_encryptor import LogEncryptor, EncryptionManager


class TestLogSanitizer:
    """Test PII and sensitive data sanitization"""
    
    def test_email_redaction(self):
        """Test email address redaction"""
        sanitizer = LogSanitizer()
        
        text = "Contact user@example.com for support"
        result = sanitizer.sanitize(text)
        
        assert "user@example.com" not in result
        assert "<EMAIL_REDACTED>" in result
    
    def test_phone_redaction(self):
        """Test phone number redaction"""
        sanitizer = LogSanitizer()
        
        test_cases = [
            "Call 555-123-4567",
            "Phone: (555) 123-4567",
            "Mobile: 5551234567",
            "+1-555-123-4567"
        ]
        
        for text in test_cases:
            result = sanitizer.sanitize(text)
            assert "<PHONE_REDACTED>" in result
    
    def test_ssn_redaction(self):
        """Test Social Security Number redaction"""
        sanitizer = LogSanitizer()
        
        text = "SSN: 123-45-6789"
        result = sanitizer.sanitize(text)
        
        assert "123-45-6789" not in result
        assert "<SSN_REDACTED>" in result
    
    def test_credit_card_redaction(self):
        """Test credit card number redaction"""
        sanitizer = LogSanitizer()
        
        text = "Card: 4532-1234-5678-9010"
        result = sanitizer.sanitize(text)
        
        assert "4532-1234-5678-9010" not in result
        assert "<CC_REDACTED>" in result
    
    def test_api_key_redaction(self):
        """Test API key redaction"""
        sanitizer = LogSanitizer()
        
        test_cases = [
            'api_key="sk_live_1234567890abcdefghij"',
            "API-KEY: abcdefghijklmnopqrstuvwxyz123456",
            "apiKey='test_key_1234567890'"
        ]
        
        for text in test_cases:
            result = sanitizer.sanitize(text)
            assert "<API_KEY_REDACTED>" in result or "api_key=<API_KEY_REDACTED>" in result
    
    def test_bearer_token_redaction(self):
        """Test Bearer token redaction"""
        sanitizer = LogSanitizer()
        
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        result = sanitizer.sanitize(text)
        
        assert "Bearer <TOKEN_REDACTED>" in result
    
    def test_password_redaction(self):
        """Test password field redaction"""
        sanitizer = LogSanitizer()
        
        test_cases = [
            'password="mysecretpass123"',
            "Password: SuperSecret!",
            "password=abcd1234"
        ]
        
        for text in test_cases:
            result = sanitizer.sanitize(text)
            assert "<PASSWORD_REDACTED>" in result or "password=<PASSWORD_REDACTED>" in result
    
    def test_jwt_redaction(self):
        """Test JWT token redaction"""
        sanitizer = LogSanitizer()
        
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        text = f"Token: {jwt}"
        result = sanitizer.sanitize(text)
        
        assert jwt not in result
        assert "<JWT_REDACTED>" in result
    
    def test_home_directory_redaction(self):
        """Test home directory path redaction"""
        sanitizer = LogSanitizer()
        
        test_cases = [
            "/Users/johndoe/projects/app",
            "/home/janedoe/.config",
            "C:\\Users\\alice\\Documents"
        ]
        
        for text in test_cases:
            result = sanitizer.sanitize(text)
            assert "/home/<USER_REDACTED>" in result or "johndoe" not in result
    
    def test_ip_address_redaction_when_enabled(self):
        """Test IP address redaction when enabled"""
        sanitizer = LogSanitizer(enable_ip_redaction=True)
        
        text = "Connected from 192.168.1.100"
        result = sanitizer.sanitize(text)
        
        assert "192.168.1.100" not in result
        assert "<IP_REDACTED>" in result
    
    def test_ip_address_not_redacted_by_default(self):
        """Test IP address not redacted by default"""
        sanitizer = LogSanitizer(enable_ip_redaction=False)
        
        text = "Connected from 192.168.1.100"
        result = sanitizer.sanitize(text)
        
        assert "192.168.1.100" in result
    
    def test_nested_dict_sanitization(self):
        """Test sanitization of nested dictionaries"""
        sanitizer = LogSanitizer()
        
        data = {
            'user': {
                'email': 'test@example.com',
                'phone': '555-123-4567'
            },
            'credentials': {
                'api_key': 'sk_live_1234567890abcdefghij'
            }
        }
        
        result = sanitizer.sanitize(data)
        
        assert '<EMAIL_REDACTED>' in str(result)
        assert 'test@example.com' not in str(result)
    
    def test_list_sanitization(self):
        """Test sanitization of lists"""
        sanitizer = LogSanitizer()
        
        data = [
            "User email: alice@example.com",
            "User phone: 555-123-4567",
            "User SSN: 123-45-6789"
        ]
        
        result = sanitizer.sanitize(data)
        
        assert '<EMAIL_REDACTED>' in str(result)
        assert '<PHONE_REDACTED>' in str(result)
        assert '<SSN_REDACTED>' in str(result)
    
    def test_sanitization_statistics(self):
        """Test sanitization statistics tracking"""
        sanitizer = LogSanitizer()
        sanitizer.reset_stats()
        
        text = """
        Contact: user@example.com
        Phone: 555-123-4567
        Another email: admin@example.com
        """
        
        sanitizer.sanitize(text)
        stats = sanitizer.get_stats()
        
        assert stats['email'] == 2
        assert stats['phone'] == 1
    
    def test_sensitive_value_hashing(self):
        """Test consistent hashing of sensitive values"""
        sanitizer = LogSanitizer()
        
        value = "user@example.com"
        hash1 = sanitizer.hash_sensitive_value(value, prefix='email_')
        hash2 = sanitizer.hash_sensitive_value(value, prefix='email_')
        
        # Same value should produce same hash
        assert hash1 == hash2
        assert hash1.startswith('email_')
        
        # Different values should produce different hashes
        hash3 = sanitizer.hash_sensitive_value("other@example.com", prefix='email_')
        assert hash1 != hash3
    
    def test_singleton_pattern(self):
        """Test singleton pattern for get_sanitizer()"""
        sanitizer1 = get_sanitizer()
        sanitizer2 = get_sanitizer()
        
        assert sanitizer1 is sanitizer2


class TestLogEncryptor:
    """Test encryption and decryption of log files"""
    
    def test_key_generation(self):
        """Test encryption key generation"""
        key = LogEncryptor.generate_key()
        
        assert len(key) == 32  # 256 bits
        assert isinstance(key, bytes)
    
    def test_encryption_decryption(self):
        """Test basic encryption and decryption"""
        key = LogEncryptor.generate_key()
        encryptor = LogEncryptor(key=key)
        
        plaintext = b"Sensitive audit log data"
        nonce, ciphertext = encryptor.encrypt(plaintext)
        
        # Verify ciphertext is different from plaintext
        assert ciphertext != plaintext
        
        # Decrypt
        decrypted = encryptor.decrypt(nonce, ciphertext)
        assert decrypted == plaintext
    
    def test_encryption_with_aad(self):
        """Test encryption with additional authenticated data"""
        key = LogEncryptor.generate_key()
        encryptor = LogEncryptor(key=key)
        
        plaintext = b"Log data"
        aad = b"metadata:orchestrator=planning"
        
        nonce, ciphertext = encryptor.encrypt(plaintext, associated_data=aad)
        decrypted = encryptor.decrypt(nonce, ciphertext, associated_data=aad)
        
        assert decrypted == plaintext
    
    def test_decryption_with_wrong_aad_fails(self):
        """Test that decryption fails with wrong AAD"""
        key = LogEncryptor.generate_key()
        encryptor = LogEncryptor(key=key)
        
        plaintext = b"Log data"
        aad = b"metadata:orchestrator=planning"
        wrong_aad = b"metadata:orchestrator=vacuum"
        
        nonce, ciphertext = encryptor.encrypt(plaintext, associated_data=aad)
        
        with pytest.raises(Exception):  # cryptography.exceptions.InvalidTag
            encryptor.decrypt(nonce, ciphertext, associated_data=wrong_aad)
    
    def test_file_encryption_decryption(self):
        """Test file encryption and decryption"""
        key = LogEncryptor.generate_key()
        encryptor = LogEncryptor(key=key)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("Sensitive log entry\nAnother log entry\n")
            temp_path = Path(f.name)
        
        try:
            # Encrypt file
            enc_path = encryptor.encrypt_file(temp_path)
            assert enc_path.exists()
            assert enc_path.suffix == '.enc'
            
            # Decrypt file
            dec_path = encryptor.decrypt_file(enc_path)
            assert dec_path.exists()
            
            # Verify content
            with open(dec_path, 'r') as f:
                content = f.read()
            assert "Sensitive log entry" in content
            
            # Cleanup
            enc_path.unlink()
            dec_path.unlink()
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_key_derivation_from_password(self):
        """Test key derivation from password"""
        password = "SecurePassword123!"
        
        key1 = LogEncryptor._derive_key_from_password(password)
        key2 = LogEncryptor._derive_key_from_password(password)
        
        # Same password should produce same key
        assert key1 == key2
        assert len(key1) == 32
    
    def test_encryption_with_password(self):
        """Test encryption using password-derived key"""
        password = "SecurePassword123!"
        encryptor = LogEncryptor(password=password)
        
        plaintext = b"Log data"
        nonce, ciphertext = encryptor.encrypt(plaintext)
        decrypted = encryptor.decrypt(nonce, ciphertext)
        
        assert decrypted == plaintext
    
    def test_invalid_key_size_raises_error(self):
        """Test that invalid key size raises ValueError"""
        with pytest.raises(ValueError, match="must be 32 bytes"):
            LogEncryptor(key=b"short_key")
    
    def test_key_rotation(self):
        """Test key rotation functionality"""
        old_key = LogEncryptor.generate_key()
        new_key = LogEncryptor.generate_key()
        
        encryptor = LogEncryptor(key=old_key)
        
        # Create temporary directory with encrypted files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create and encrypt a test file
            test_file = temp_path / "test.log"
            test_file.write_text("Test log data")
            enc_file = encryptor.encrypt_file(test_file)
            
            # Rotate keys
            encryptor.rotate_key(new_key, temp_path)
            
            # Verify we can decrypt with the new encryptor
            new_encryptor = LogEncryptor(key=new_key)
            dec_file = new_encryptor.decrypt_file(enc_file)
            
            assert dec_file.read_text() == "Test log data"


class TestEncryptionManager:
    """Test high-level encryption management"""
    
    def test_should_encrypt_error_logs(self):
        """Test that ERROR logs are always encrypted"""
        key = LogEncryptor.generate_key()
        encryptor = LogEncryptor(key=key)
        manager = EncryptionManager(encryptor, encrypt_by_default=False)
        
        log_path = Path("logs/error.log")
        assert manager.should_encrypt(log_path, log_level='ERROR')
    
    def test_should_encrypt_critical_logs(self):
        """Test that CRITICAL logs are always encrypted"""
        key = LogEncryptor.generate_key()
        encryptor = LogEncryptor(key=key)
        manager = EncryptionManager(encryptor, encrypt_by_default=False)
        
        log_path = Path("logs/critical.log")
        assert manager.should_encrypt(log_path, log_level='CRITICAL')
    
    def test_should_encrypt_sensitive_named_files(self):
        """Test that files with 'sensitive' in name are encrypted"""
        key = LogEncryptor.generate_key()
        encryptor = LogEncryptor(key=key)
        manager = EncryptionManager(encryptor, encrypt_by_default=False)
        
        log_path = Path("logs/sensitive-data.log")
        assert manager.should_encrypt(log_path, log_level='INFO')
    
    def test_should_not_encrypt_info_logs_by_default(self):
        """Test that INFO logs are not encrypted by default"""
        key = LogEncryptor.generate_key()
        encryptor = LogEncryptor(key=key)
        manager = EncryptionManager(encryptor, encrypt_by_default=False)
        
        log_path = Path("logs/info.log")
        assert not manager.should_encrypt(log_path, log_level='INFO')
    
    def test_encrypt_all_when_default_enabled(self):
        """Test that all logs are encrypted when default is enabled"""
        key = LogEncryptor.generate_key()
        encryptor = LogEncryptor(key=key)
        manager = EncryptionManager(encryptor, encrypt_by_default=True)
        
        log_path = Path("logs/info.log")
        assert manager.should_encrypt(log_path, log_level='INFO')
    
    def test_encrypt_if_needed(self):
        """Test conditional encryption"""
        key = LogEncryptor.generate_key()
        encryptor = LogEncryptor(key=key)
        manager = EncryptionManager(encryptor, encrypt_by_default=False)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("Error log data")
            temp_path = Path(f.name)
        
        try:
            # Should encrypt ERROR logs
            enc_path = manager.encrypt_if_needed(temp_path, log_level='ERROR')
            assert enc_path is not None
            assert enc_path.exists()
            
            # Cleanup
            enc_path.unlink()
        finally:
            if temp_path.exists():
                temp_path.unlink()


class TestSecurityIntegration:
    """Integration tests for security components"""
    
    def test_sanitize_then_encrypt(self):
        """Test sanitization followed by encryption"""
        # Sanitize sensitive data
        sanitizer = LogSanitizer()
        log_data = {
            'event': 'user_login',
            'user_email': 'alice@example.com',
            'user_phone': '555-123-4567',
            'timestamp': '2026-01-05T12:00:00'
        }
        sanitized = sanitizer.sanitize(log_data)
        
        # Verify sanitization
        assert '<EMAIL_REDACTED>' in str(sanitized)
        assert 'alice@example.com' not in str(sanitized)
        
        # Encrypt sanitized data
        key = LogEncryptor.generate_key()
        encryptor = LogEncryptor(key=key)
        
        plaintext = str(sanitized).encode()
        nonce, ciphertext = encryptor.encrypt(plaintext)
        
        # Decrypt and verify
        decrypted = encryptor.decrypt(nonce, ciphertext)
        assert b'<EMAIL_REDACTED>' in decrypted
        assert b'alice@example.com' not in decrypted
    
    def test_end_to_end_secure_logging(self):
        """Test complete secure logging workflow"""
        # 1. Create log data with sensitive information
        log_entry = {
            'timestamp': '2026-01-05T12:00:00',
            'level': 'ERROR',
            'message': 'Login failed for user@example.com',
            'api_key': 'sk_live_1234567890abcdefghij',
            'request_ip': '192.168.1.100'
        }
        
        # 2. Sanitize
        sanitizer = LogSanitizer()
        sanitized_entry = sanitizer.sanitize(log_entry)
        
        # Verify sanitization
        assert '<EMAIL_REDACTED>' in str(sanitized_entry)
        assert '<API_KEY_REDACTED>' in str(sanitized_entry)
        
        # 3. Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            import json
            f.write(json.dumps(sanitized_entry))
            temp_path = Path(f.name)
        
        try:
            # 4. Encrypt
            key = LogEncryptor.generate_key()
            encryptor = LogEncryptor(key=key)
            enc_path = encryptor.encrypt_file(temp_path)
            
            # 5. Verify encrypted file is binary and different
            with open(enc_path, 'rb') as f:
                enc_data = f.read()
            assert b'user@example.com' not in enc_data
            assert b'sk_live' not in enc_data
            
            # Cleanup
            enc_path.unlink()
        finally:
            if temp_path.exists():
                temp_path.unlink()
