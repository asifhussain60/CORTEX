"""
Integration Tests: PII Sanitizer + Encryptor

Test the full security pipeline:
1. Sanitize sensitive data (PII Sanitizer)
2. Encrypt sanitized logs (Encryptor)
3. Decrypt and verify (Encryptor)

Author: Asif Hussain
Date: January 5, 2026
"""

import pytest
from pathlib import Path

from src.audit_logger.security.pii_sanitizer import PIISanitizer
from src.audit_logger.security.encryptor import Encryptor


class TestSecurityIntegration:
    """Integration tests for security layer components"""
    
    @pytest.fixture
    def sanitizer(self) -> PIISanitizer:
        """Create PII Sanitizer instance"""
        return PIISanitizer()
    
    @pytest.fixture
    def encryptor(self, tmp_path: Path) -> Encryptor:
        """Create Encryptor instance"""
        key_file = tmp_path / "integration_keys.json"
        return Encryptor(key_file=key_file, algorithm='AES-256-GCM')
    
    def test_sanitize_then_encrypt(self, sanitizer: PIISanitizer, encryptor: Encryptor):
        """Test sanitization followed by encryption"""
        # Log with PII
        original_log = "User SSN: 123-45-6789 logged in with password: MySecret123!"
        
        # Step 1: Sanitize PII
        sanitized = sanitizer.sanitize(original_log)
        assert "123-45-6789" not in sanitized
        assert "[REDACTED_SSN]" in sanitized
        # Note: Password pattern not in PII Sanitizer yet (future enhancement)
        
        # Step 2: Encrypt sanitized log
        encrypted = encryptor.encrypt(sanitized)
        assert encrypted['algorithm'] == 'AES-256-GCM'
        assert 'encrypted_data' in encrypted
        
        # Step 3: Decrypt and verify
        decrypted = encryptor.decrypt(encrypted)
        assert decrypted == sanitized
        assert "[REDACTED_SSN]" in decrypted
    
    def test_encrypt_with_sanitization_metadata(self, sanitizer: PIISanitizer, encryptor: Encryptor):
        """Test encryption with sanitization metadata"""
        original_log = "Email: user@example.com, API Key: sk-abc123xyz456"
        
        # Sanitize
        sanitized = sanitizer.sanitize(original_log)
        
        # Encrypt with metadata indicating sanitization
        metadata = {
            'sanitized': True,
            'log_level': 'INFO',
            'redacted_types': ['EMAIL', 'API_KEY']
        }
        encrypted = encryptor.encrypt(sanitized, metadata=metadata)
        
        # Verify metadata preserved
        assert encrypted['metadata'] == metadata
        
        # Decrypt
        decrypted = encryptor.decrypt(encrypted)
        assert "[REDACTED_EMAIL]" in decrypted
        assert "[REDACTED_API_KEY]" in decrypted
    
    def test_batch_sanitize_and_encrypt(self, sanitizer: PIISanitizer, encryptor: Encryptor):
        """Test batch processing of logs"""
        logs = [
            "User 123-45-6789 accessed file",
            "Payment with card 4532123456789010",
            "API call with key sk-liveabc123xyz456",
            "JWT token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        ]
        
        encrypted_logs = []
        for log in logs:
            # Sanitize
            sanitized = sanitizer.sanitize(log)
            
            # Encrypt
            encrypted = encryptor.encrypt(sanitized)
            encrypted_logs.append(encrypted)
        
        # Verify all encrypted
        assert len(encrypted_logs) == 4
        
        # Decrypt and verify sanitization
        for encrypted in encrypted_logs:
            decrypted = encryptor.decrypt(encrypted)
            assert "REDACTED" in decrypted  # All have redactions
    
    def test_key_rotation_with_sanitized_data(self, sanitizer: PIISanitizer, encryptor: Encryptor):
        """Test key rotation doesn't affect sanitized data"""
        original_log = "Phone: 555-123-4567, SSN: 987-65-4321"
        
        # Sanitize and encrypt with old key
        sanitized = sanitizer.sanitize(original_log)
        encrypted_old = encryptor.encrypt(sanitized)
        old_key_id = encrypted_old['key_id']
        
        # Rotate key
        new_key_id = encryptor.rotate_keys()
        assert new_key_id != old_key_id
        
        # Old encrypted data should still decrypt
        decrypted = encryptor.decrypt(encrypted_old)
        assert decrypted == sanitized
        
        # New encryptions use new key
        encrypted_new = encryptor.encrypt(sanitized)
        assert encrypted_new['key_id'] == new_key_id
        
        # Both decrypt to same sanitized data
        assert encryptor.decrypt(encrypted_new) == decrypted
    
    def test_dict_sanitize_and_encrypt(self, sanitizer: PIISanitizer, encryptor: Encryptor):
        """Test sanitizing and encrypting dictionary data"""
        log_dict = {
            'user': 'john.doe@example.com',
            'ssn': '123-45-6789',
            'action': 'login',
            'api_key': 'sk-prodxyz789abc'
        }
        
        # Sanitize dictionary
        sanitized_dict = sanitizer.sanitize_dict(log_dict)
        
        # Convert to JSON string for encryption
        import json
        sanitized_json = json.dumps(sanitized_dict)
        
        # Encrypt
        encrypted = encryptor.encrypt(sanitized_json)
        
        # Decrypt and parse
        decrypted_json = encryptor.decrypt(encrypted)
        decrypted_dict = json.loads(decrypted_json)
        
        # Verify sanitization preserved
        assert decrypted_dict['user'] == '[REDACTED_EMAIL]'
        assert decrypted_dict['ssn'] == '[REDACTED_SSN]'
        assert decrypted_dict['action'] == 'login'  # Unchanged
        assert decrypted_dict['api_key'] == '[REDACTED_API_KEY]'
    
    def test_large_sanitized_log_encryption(self, sanitizer: PIISanitizer, encryptor: Encryptor):
        """Test encryption of large sanitized logs"""
        # Create large log with multiple PII instances
        log_entries = []
        for i in range(100):
            log_entries.append(
                f"User {i}: email user{i}@example.com, SSN 123-45-{i:04d}, "
                f"card 4532-{i:04d}-5678-9010"
            )
        large_log = "\\n".join(log_entries)
        
        # Sanitize
        sanitized = sanitizer.sanitize(large_log)
        
        # Verify sanitization
        assert "@example.com" not in sanitized
        assert "123-45-" not in sanitized
        
        # Encrypt
        encrypted = encryptor.encrypt(sanitized)
        
        # Decrypt
        decrypted = encryptor.decrypt(encrypted)
        assert decrypted == sanitized
    
    def test_tamper_detection_on_sanitized_data(self, sanitizer: PIISanitizer, encryptor: Encryptor):
        """Test tamper detection works with sanitized data"""
        original_log = "Credit card: 4532-1234-5678-9010"
        
        # Sanitize and encrypt
        sanitized = sanitizer.sanitize(original_log)
        encrypted = encryptor.encrypt(sanitized)
        
        # Tamper with encrypted data
        encrypted['encrypted_data'] = 'TAMPERED'
        
        # Should raise TamperDetectedError
        from src.audit_logger.security.encryptor import TamperDetectedError
        with pytest.raises(TamperDetectedError):
            encryptor.decrypt(encrypted)
    
    def test_unicode_and_emoji_sanitization(self, sanitizer: PIISanitizer, encryptor: Encryptor):
        """Test sanitization and encryption of Unicode data"""
        log = "用户 john@example.com 登录 🎉 SSN: 123-45-6789"
        
        # Sanitize
        sanitized = sanitizer.sanitize(log)
        
        # Encrypt
        encrypted = encryptor.encrypt(sanitized)
        
        # Decrypt
        decrypted = encryptor.decrypt(encrypted)
        
        # Verify Unicode preserved and PII redacted
        assert "用户" in decrypted
        assert "登录" in decrypted
        assert "🎉" in decrypted
        assert "john@example.com" not in decrypted
        assert "[REDACTED_EMAIL]" in decrypted
    
    def test_performance_full_pipeline(self, sanitizer: PIISanitizer, encryptor: Encryptor):
        """Test performance of full sanitization + encryption pipeline"""
        import time
        
        log = "User email: user@example.com, SSN: 123-45-6789, accessed system"
        iterations = 100
        
        start_time = time.perf_counter()
        for _ in range(iterations):
            sanitized = sanitizer.sanitize(log)
            encrypted = encryptor.encrypt(sanitized)
            decrypted = encryptor.decrypt(encrypted)
        elapsed = time.perf_counter() - start_time
        
        avg_time = elapsed / iterations
        # Full pipeline should complete in <5ms
        assert avg_time < 0.005, f"Pipeline too slow: {avg_time*1000:.2f}ms"
