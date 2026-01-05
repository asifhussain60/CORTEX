"""
Task 4.3: RBAC Integration Tests

Tests RBAC Manager integration with:
- Encryptor (Task 4.2): Role-based encryption/decryption
- PII Sanitizer (Task 4.1): Role-based sanitization
- Full security pipeline: RBAC → Sanitize → Encrypt → Audit

Author: Asif Hussain
Date: January 5, 2026
"""

import pytest
from datetime import datetime
import tempfile
import os
from src.audit_logger.security.rbac import (
    RBACManager, User, Permission, Resource, PermissionDeniedError
)
from src.audit_logger.security.encryptor import Encryptor
from src.audit_logger.security.pii_sanitizer import PIISanitizer


class TestRBACEncryptorIntegration:
    """Test RBAC + Encryptor integration"""
    
    @pytest.fixture
    def rbac(self) -> RBACManager:
        """Create RBAC manager"""
        return RBACManager()
    
    @pytest.fixture
    def encryptor(self) -> Encryptor:
        """Create encryptor with temporary key file"""
        temp_dir = tempfile.mkdtemp()
        key_file = os.path.join(temp_dir, 'test.key')
        
        encryptor = Encryptor(algorithm='AES-256-GCM', key_file=key_file)
        
        yield encryptor
        
        # Cleanup
        if os.path.exists(key_file):
            os.remove(key_file)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
    
    def test_developer_can_encrypt_own_log(self, rbac: RBACManager, encryptor: Encryptor):
        """Test developer can encrypt their own logs"""
        dev = rbac.create_user('dev-1', 'developer')
        
        # Check encrypt permission
        can_encrypt = rbac.check_permission(dev, Permission.ENCRYPT_LOG)
        assert can_encrypt is True
        
        # Encrypt data
        log_data = "Sensitive audit log entry"
        encrypted = encryptor.encrypt(log_data)
        
        assert encrypted != log_data
        assert len(encrypted) > 0
    
    def test_developer_can_decrypt_own_log(self, rbac: RBACManager, encryptor: Encryptor):
        """Test developer can decrypt logs they encrypted"""
        dev = rbac.create_user('dev-1', 'developer')
        
        # Encrypt
        log_data = "Audit log with secrets"
        encrypted = encryptor.encrypt(log_data)
        
        # Check decrypt permission
        can_decrypt = rbac.check_permission(dev, Permission.DECRYPT_LOG)
        assert can_decrypt is True
        
        # Decrypt
        decrypted = encryptor.decrypt(encrypted)
        assert decrypted == log_data
    
    def test_auditor_can_decrypt_any_log(self, rbac: RBACManager, encryptor: Encryptor):
        """Test auditor can decrypt logs from any user"""
        auditor = rbac.create_user('auditor-1', 'auditor')
        
        # Simulate encrypted log from developer
        dev_log = "Developer's audit log"
        encrypted = encryptor.encrypt(dev_log)
        
        # Auditor decrypts
        can_decrypt = rbac.check_permission(auditor, Permission.DECRYPT_LOG)
        assert can_decrypt is True
        
        decrypted = encryptor.decrypt(encrypted)
        assert decrypted == dev_log
    
    def test_read_only_cannot_decrypt(self, rbac: RBACManager, encryptor: Encryptor):
        """Test read-only user cannot decrypt logs"""
        viewer = rbac.create_user('viewer-1', 'read_only')
        
        # Check permission
        can_decrypt = rbac.check_permission(viewer, Permission.DECRYPT_LOG)
        assert can_decrypt is False
        
        # Enforce check should raise
        with pytest.raises(PermissionDeniedError):
            rbac.check_permission(viewer, Permission.DECRYPT_LOG, enforce=True)
    
    def test_admin_can_rotate_keys(self, rbac: RBACManager):
        """Test only admin can rotate encryption keys"""
        admin = rbac.create_user('admin-1', 'admin')
        dev = rbac.create_user('dev-1', 'developer')
        
        # Admin can rotate
        assert admin.has_permission(Permission.ROTATE_KEYS)
        
        # Developer cannot
        assert not dev.has_permission(Permission.ROTATE_KEYS)
    
    def test_encryption_operations_logged(self, rbac: RBACManager, encryptor: Encryptor):
        """Test encryption operations are logged to audit trail"""
        dev = rbac.create_user('dev-1', 'developer')
        
        # Perform operations
        rbac.check_permission(dev, Permission.ENCRYPT_LOG)
        rbac.check_permission(dev, Permission.DECRYPT_LOG)
        
        # Check audit trail
        trail = rbac.get_audit_trail(user_id='dev-1')
        
        operations = [entry['operation'] for entry in trail]
        assert 'encrypt_log' in operations
        assert 'decrypt_log' in operations


class TestRBACSanitizerIntegration:
    """Test RBAC + PII Sanitizer integration"""
    
    @pytest.fixture
    def rbac(self) -> RBACManager:
        """Create RBAC manager"""
        return RBACManager()
    
    @pytest.fixture
    def sanitizer(self) -> PIISanitizer:
        """Create PII sanitizer"""
        return PIISanitizer()
    
    def test_developer_can_sanitize_pii(self, rbac: RBACManager, sanitizer: PIISanitizer):
        """Test developer can sanitize PII in logs"""
        dev = rbac.create_user('dev-1', 'developer')
        
        # Check permission
        can_sanitize = rbac.check_permission(dev, Permission.SANITIZE_PII)
        assert can_sanitize is True
        
        # Sanitize data
        log_with_pii = "User SSN: 123-45-6789 logged in"
        sanitized = sanitizer.sanitize(log_with_pii)
        
        assert "123-45-6789" not in sanitized
        assert "[REDACTED_SSN]" in sanitized
    
    def test_admin_can_sanitize_pii(self, rbac: RBACManager, sanitizer: PIISanitizer):
        """Test admin can sanitize PII"""
        admin = rbac.create_user('admin-1', 'admin')
        
        assert admin.has_permission(Permission.SANITIZE_PII)
        
        log_with_api_key = "API Key: sk-1234567890abcdef logged"
        sanitized = sanitizer.sanitize(log_with_api_key)
        
        assert "sk-1234567890abcdef" not in sanitized
        assert "[REDACTED_API_KEY]" in sanitized
    
    def test_auditor_cannot_sanitize(self, rbac: RBACManager):
        """Test auditor cannot sanitize PII (read-only audit)"""
        auditor = rbac.create_user('auditor-1', 'auditor')
        
        can_sanitize = rbac.check_permission(auditor, Permission.SANITIZE_PII)
        assert can_sanitize is False
    
    def test_read_only_cannot_sanitize(self, rbac: RBACManager):
        """Test read-only cannot sanitize PII"""
        viewer = rbac.create_user('viewer-1', 'read_only')
        
        can_sanitize = rbac.check_permission(viewer, Permission.SANITIZE_PII)
        assert can_sanitize is False


class TestFullSecurityPipeline:
    """Test complete security pipeline: RBAC → Sanitize → Encrypt → Audit"""
    
    @pytest.fixture
    def rbac(self) -> RBACManager:
        """Create RBAC manager"""
        return RBACManager()
    
    @pytest.fixture
    def encryptor(self) -> Encryptor:
        """Create encryptor with temporary key file"""
        temp_dir = tempfile.mkdtemp()
        key_file = os.path.join(temp_dir, 'test.key')
        
        encryptor = Encryptor(algorithm='AES-256-GCM', key_file=key_file)
        
        yield encryptor
        
        # Cleanup
        if os.path.exists(key_file):
            os.remove(key_file)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
    
    @pytest.fixture
    def sanitizer(self) -> PIISanitizer:
        """Create PII sanitizer"""
        return PIISanitizer()
    
    def test_full_pipeline_developer(
        self, rbac: RBACManager, sanitizer: PIISanitizer, encryptor: Encryptor
    ):
        """Test full pipeline for developer role"""
        dev = rbac.create_user('dev-1', 'developer')
        
        # Step 1: Sanitize PII
        raw_log = "User john@example.com (SSN: 123-45-6789) accessed API with key sk-1234567890"
        
        rbac.check_permission(dev, Permission.SANITIZE_PII, enforce=True)
        sanitized = sanitizer.sanitize(raw_log)
        
        assert "john@example.com" not in sanitized
        assert "123-45-6789" not in sanitized
        assert "sk-1234567890" not in sanitized
        
        # Step 2: Encrypt sanitized log
        rbac.check_permission(dev, Permission.ENCRYPT_LOG, enforce=True)
        encrypted = encryptor.encrypt(sanitized)
        
        assert encrypted != sanitized
        
        # Step 3: Decrypt (developer can decrypt own logs)
        rbac.check_permission(dev, Permission.DECRYPT_LOG, enforce=True)
        decrypted = encryptor.decrypt(encrypted)
        
        assert decrypted == sanitized
        assert "[REDACTED_EMAIL]" in decrypted
        assert "[REDACTED_SSN]" in decrypted
        assert "[REDACTED_API_KEY]" in decrypted
        
        # Step 4: Verify audit trail
        trail = rbac.get_audit_trail(user_id='dev-1')
        
        operations = [entry['operation'] for entry in trail]
        assert 'sanitize_pii' in operations
        assert 'encrypt_log' in operations
        assert 'decrypt_log' in operations
        assert all(entry['result'] == 'success' for entry in trail if entry['operation'] != 'user_created')
    
    def test_full_pipeline_auditor(
        self, rbac: RBACManager, encryptor: Encryptor
    ):
        """Test auditor workflow (read + decrypt only)"""
        auditor = rbac.create_user('auditor-1', 'auditor')
        
        # Simulate encrypted log from developer
        dev_log = "[REDACTED_EMAIL] logged in successfully"
        encrypted = encryptor.encrypt(dev_log)
        
        # Auditor can read all logs
        rbac.check_permission(auditor, Permission.READ_ALL_LOGS, enforce=True)
        
        # Auditor can decrypt
        rbac.check_permission(auditor, Permission.DECRYPT_LOG, enforce=True)
        decrypted = encryptor.decrypt(encrypted)
        
        assert decrypted == dev_log
        
        # Auditor cannot sanitize (not their job)
        with pytest.raises(PermissionDeniedError):
            rbac.check_permission(auditor, Permission.SANITIZE_PII, enforce=True)
        
        # Auditor cannot encrypt (read-only)
        with pytest.raises(PermissionDeniedError):
            rbac.check_permission(auditor, Permission.ENCRYPT_LOG, enforce=True)
    
    def test_admin_full_access(
        self, rbac: RBACManager, sanitizer: PIISanitizer, encryptor: Encryptor
    ):
        """Test admin has unrestricted pipeline access"""
        admin = rbac.create_user('admin-1', 'admin')
        
        raw_log = "Admin action: Updated user email=admin@corp.com SSN=987-65-4321"
        
        # Admin can do everything
        rbac.check_permission(admin, Permission.SANITIZE_PII, enforce=True)
        sanitized = sanitizer.sanitize(raw_log)
        
        rbac.check_permission(admin, Permission.ENCRYPT_LOG, enforce=True)
        encrypted = encryptor.encrypt(sanitized)
        
        rbac.check_permission(admin, Permission.DECRYPT_LOG, enforce=True)
        decrypted = encryptor.decrypt(encrypted)
        
        rbac.check_permission(admin, Permission.ROTATE_KEYS, enforce=True)
        rbac.check_permission(admin, Permission.VIEW_AUDIT_TRAIL, enforce=True)
        
        # All operations succeed
        trail = rbac.get_audit_trail(user_id='admin-1')
        assert len(trail) > 0
        assert all(entry['result'] == 'success' for entry in trail if entry['operation'] != 'user_created')
    
    def test_context_manager_with_pipeline(
        self, rbac: RBACManager, sanitizer: PIISanitizer, encryptor: Encryptor
    ):
        """Test context manager logs full pipeline operations"""
        dev = rbac.create_user('dev-1', 'developer')
        
        with rbac.as_user(dev):
            # Perform operations inside context
            raw_log = "Password: secret123 for john@example.com"
            sanitized = sanitizer.sanitize(raw_log)
            encrypted = encryptor.encrypt(sanitized)
            decrypted = encryptor.decrypt(encrypted)
        
        # Context operations logged
        trail = rbac.get_audit_trail(user_id='dev-1')
        operations = [entry['operation'] for entry in trail]
        
        assert 'context_start' in operations
        assert 'context_end' in operations


class TestRoleBasedResourceAccess:
    """Test role-based resource access with security components"""
    
    @pytest.fixture
    def rbac(self) -> RBACManager:
        """Create RBAC manager"""
        return RBACManager()
    
    def test_developer_accesses_own_encrypted_log(
        self, rbac: RBACManager
    ):
        """Test developer can only access logs they created"""
        dev1 = rbac.create_user('dev-1', 'developer')
        dev2 = rbac.create_user('dev-2', 'developer')
        
        # Dev1 creates encrypted log
        log1 = Resource(id='log-123', created_by='dev-1', metadata={'encrypted': True})
        
        # Dev1 can access own resource
        can_access = rbac.check_permission(dev1, Permission.READ_OWN_LOG, resource=log1)
        assert can_access is True
        
        # Dev2 cannot access dev1's resource
        can_access = rbac.check_permission(dev2, Permission.UPDATE_LOG, resource=log1)
        assert can_access is False
    
    def test_admin_overrides_ownership(self, rbac: RBACManager):
        """Test admin can access all resources regardless of ownership"""
        admin = rbac.create_user('admin-1', 'admin')
        dev = rbac.create_user('dev-1', 'developer')
        
        # Developer's resource
        dev_log = Resource(id='log-456', created_by='dev-1')
        
        # Admin can access even though not owner
        can_access = rbac.check_permission(admin, Permission.UPDATE_LOG, resource=dev_log)
        assert can_access is True
    
    def test_auditor_reads_all_logs_but_no_ownership(self, rbac: RBACManager):
        """Test auditor can read all logs but doesn't check ownership"""
        auditor = rbac.create_user('auditor-1', 'auditor')
        
        any_log = Resource(id='log-789', created_by='unknown-user')
        
        # Auditor has READ_ALL_LOGS (doesn't require ownership)
        can_read = rbac.check_permission(auditor, Permission.READ_ALL_LOGS, resource=any_log)
        assert can_read is True
