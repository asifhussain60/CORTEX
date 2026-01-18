"""
Test Suite for AC-NFR-003-03: Credential Protection & Secure Storage

Tests: 12 unit + 4 integration = 16 tests
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent / "cortex-brain"))

from tier2.credential_protection import (
    EncryptionAlgorithm,
    CredentialStatus,
    EncryptionKey,
    SecureCredentialStore,
    KeyRotationManager,
)


# ============================================================================
# UNIT TESTS: Encryption Key Management
# ============================================================================

class TestEncryptionKey:
    """Test encryption key functionality."""
    
    def test_key_creation(self):
        """Test encryption key creation."""
        key = EncryptionKey("key1", EncryptionAlgorithm.AES_256)
        assert key.key_id == "key1"
        assert key.is_active is True
    
    def test_key_expiration(self):
        """Test key expiration checking."""
        key = EncryptionKey("key1", EncryptionAlgorithm.AES_256, ttl_days=0)
        # Simulate expiration
        key.expires_at = datetime.utcnow() - timedelta(hours=1)
        assert key.is_expired() is True
    
    def test_key_validity(self):
        """Test key validity check."""
        key = EncryptionKey("key1", EncryptionAlgorithm.AES_128, ttl_days=90)
        assert key.is_valid() is True
    
    def test_expired_key_invalid(self):
        """Test expired key is invalid."""
        key = EncryptionKey("key1", EncryptionAlgorithm.AES_256, ttl_days=0)
        key.expires_at = datetime.utcnow() - timedelta(days=1)
        assert key.is_valid() is False


# ============================================================================
# UNIT TESTS: Secure Credential Store
# ============================================================================

class TestSecureCredentialStore:
    """Test secure credential storage."""
    
    def test_store_credential(self):
        """Test storing a credential."""
        store = SecureCredentialStore()
        store.store_credential("db_pass", "MyPassword123")
        assert store.has_credential("db_pass") is True
    
    def test_retrieve_credential(self):
        """Test retrieving a credential."""
        store = SecureCredentialStore()
        store.store_credential("api_key", "sk_live_abc123def456")
        retrieved = store.retrieve_credential("api_key")
        assert retrieved is not None
    
    def test_nonexistent_credential(self):
        """Test retrieving nonexistent credential."""
        store = SecureCredentialStore()
        retrieved = store.retrieve_credential("nonexistent")
        assert retrieved is None
    
    def test_empty_credential_rejected(self):
        """Test empty credential is rejected."""
        store = SecureCredentialStore()
        with pytest.raises(ValueError):
            store.store_credential("empty", "")
    
    def test_store_with_metadata(self):
        """Test storing credential with metadata."""
        store = SecureCredentialStore()
        meta = {"environment": "production", "owner": "admin"}
        store.store_credential("prod_db", "SecurePass123", metadata=meta)
        assert store.has_credential("prod_db") is True
    
    def test_revoke_credential(self):
        """Test revoking a credential."""
        store = SecureCredentialStore()
        store.store_credential("api_key", "sk_live_abc123def456")
        store.revoke_credential("api_key")
        assert store.has_credential("api_key") is False
    
    def test_expire_credential(self):
        """Test expiring a credential."""
        store = SecureCredentialStore()
        store.store_credential("temp_token", "temporary_access_token_12345")
        store.expire_credential("temp_token")
        assert store.has_credential("temp_token") is False
    
    def test_access_logging(self):
        """Test access logging."""
        store = SecureCredentialStore()
        store.store_credential("secret", "MySecretValue")
        store.retrieve_credential("secret")
        store.retrieve_credential("secret")
        
        log = store.get_access_log()
        assert len(log) >= 2
        assert all(entry["action"] == "retrieve" for entry in log[1:])
    
    def test_key_rotation(self):
        """Test key rotation."""
        store = SecureCredentialStore()
        # Create new key
        new_key = EncryptionKey("new_key", EncryptionAlgorithm.AES_256)
        store._keys["new_key"] = new_key
        
        # Store and rotate
        store.store_credential("important", "ImportantValue123")
        store.rotate_key("important", "new_key")
        
        # Verify rotation
        log = store.get_access_log()
        assert any(entry["action"] == "key_rotation" for entry in log)
    
    def test_multiple_credentials(self):
        """Test managing multiple credentials."""
        store = SecureCredentialStore()
        credentials = {
            "db_pass": "DbPassword123",
            "api_key": "sk_live_abc123def456",
            "jwt_token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0",
        }
        
        for cred_id, value in credentials.items():
            store.store_credential(cred_id, value)
        
        for cred_id in credentials:
            assert store.has_credential(cred_id) is True


# ============================================================================
# UNIT TESTS: Key Rotation Manager
# ============================================================================

class TestKeyRotationManager:
    """Test key rotation management."""
    
    def test_schedule_rotation(self):
        """Test scheduling key rotation."""
        store = SecureCredentialStore()
        manager = KeyRotationManager(store)
        manager.schedule_rotation("api_key", 30)
        
        # Should not need rotation immediately
        assert manager.needs_rotation("api_key") is False
    
    def test_rotation_needed(self):
        """Test detecting when rotation is needed."""
        store = SecureCredentialStore()
        manager = KeyRotationManager(store)
        manager.schedule_rotation("db_pass", 30)
        
        # Simulate past rotation
        manager._last_rotation["db_pass"] = datetime.utcnow() - timedelta(days=31)
        
        assert manager.needs_rotation("db_pass") is True
    
    def test_rotation_status(self):
        """Test getting rotation status."""
        store = SecureCredentialStore()
        manager = KeyRotationManager(store)
        manager.schedule_rotation("cred1", 30)
        manager.schedule_rotation("cred2", 90)
        
        status = manager.get_rotation_status()
        assert "cred1" in status
        assert "cred2" in status


# ============================================================================
# INTEGRATION TESTS: End-to-End Credential Management
# ============================================================================

class TestCredentialProtectionIntegration:
    """Integration tests for credential protection."""
    
    def test_complete_credential_lifecycle(self):
        """Test complete credential lifecycle."""
        store = SecureCredentialStore()
        
        # Store
        store.store_credential("api_key", "sk_live_abc123def456")
        assert store.has_credential("api_key") is True
        
        # Retrieve
        value = store.retrieve_credential("api_key")
        assert value is not None
        
        # Revoke
        store.revoke_credential("api_key")
        assert store.has_credential("api_key") is False
    
    def test_audit_trail_complete_workflow(self):
        """Test audit trail for complete workflow."""
        store = SecureCredentialStore()
        
        # Multiple operations
        store.store_credential("secret1", "Value1")
        store.retrieve_credential("secret1")
        store.retrieve_credential("secret1")
        store.revoke_credential("secret1")
        
        # Check audit log
        log = store.get_access_log()
        assert len(log) >= 3
        assert log[-1]["action"] == "revoke"
    
    def test_key_rotation_workflow(self):
        """Test key rotation workflow."""
        store = SecureCredentialStore()
        manager = KeyRotationManager(store)
        
        # Store credential
        store.store_credential("prod_key", "ProductionKeyValue123")
        
        # Schedule rotation
        manager.schedule_rotation("prod_key", 30)
        
        # Create new key
        new_key = EncryptionKey("rotated_key", EncryptionAlgorithm.AES_256)
        store._keys["rotated_key"] = new_key
        
        # Perform rotation
        store.rotate_key("prod_key", "rotated_key")
        
        # Verify credential still accessible
        value = store.retrieve_credential("prod_key")
        assert value is not None
    
    def test_multi_environment_credentials(self):
        """Test managing credentials for multiple environments."""
        store = SecureCredentialStore()
        
        environments = {
            "dev": "dev_password_123",
            "staging": "staging_password_456",
            "prod": "production_password_789",
        }
        
        for env, password in environments.items():
            cred_id = f"db_{env}"
            store.store_credential(cred_id, password, metadata={"env": env})
        
        # Verify all stored
        for env in environments:
            assert store.has_credential(f"db_{env}") is True
        
        # Verify all retrievable
        for env in environments:
            value = store.retrieve_credential(f"db_{env}")
            assert value is not None
    
    def test_emergency_revocation(self):
        """Test emergency credential revocation."""
        store = SecureCredentialStore()
        
        # Store multiple credentials
        creds = ["api_key_1", "api_key_2", "api_key_3"]
        for cred_id in creds:
            store.store_credential(cred_id, f"Value_{cred_id}")
        
        # Emergency revocation of all API keys
        for cred_id in creds:
            store.revoke_credential(cred_id)
        
        # Verify all revoked
        for cred_id in creds:
            assert store.has_credential(cred_id) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
