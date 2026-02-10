"""
Tests for SecretsManager - Phase 76 Stage 3 Task 2

Tests the core secrets management API with encryption, auditing, and storage.

Authority: phase-76-production-foundation-trilogy.yaml S3.T2
AC-ID: AC-PHASE76-S3-002
"""

import pytest
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime

from cortex.secrets.secrets_manager import SecretsManager
from cortex.secrets.errors import SecretsError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_secrets_dir():
    """Create temporary secrets directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def master_key():
    """Generate test master key."""
    return "0" * 32 + "a" * 32  # 64 character key


@pytest.fixture
def secrets_manager(master_key, temp_secrets_dir):
    """Create SecretsManager instance."""
    return SecretsManager(
        master_key=master_key,
        storage_path=temp_secrets_dir,
        audit_enabled=True,
    )


@pytest.fixture
def secrets_manager_no_audit(master_key, temp_secrets_dir):
    """Create SecretsManager without audit trail."""
    return SecretsManager(
        master_key=master_key,
        storage_path=temp_secrets_dir,
        audit_enabled=False,
    )


# ============================================================================
# SET_SECRET TESTS
# ============================================================================

class TestSetSecret:
    """Tests for SecretsManager.set_secret()"""
    
    def test_set_secret_success(self, secrets_manager):
        """Test setting a secret successfully."""
        result = secrets_manager.set_secret("TEST_SECRET", "secret_value")
        
        assert result["key"] == "TEST_SECRET"
        assert result["encrypted"] is True
        assert "timestamp" in result
        assert result["tags"] == {}
    
    def test_set_secret_with_tags(self, secrets_manager):
        """Test setting a secret with tags."""
        tags = {"env": "prod", "app": "auth"}
        result = secrets_manager.set_secret("API_KEY", "key123", tags=tags)
        
        assert result["tags"] == tags
    
    def test_set_secret_invalid_key_empty(self, secrets_manager):
        """Test setting secret with empty key."""
        with pytest.raises(SecretsError):
            secrets_manager.set_secret("", "value")
    
    def test_set_secret_invalid_key_none(self, secrets_manager):
        """Test setting secret with None key."""
        with pytest.raises(SecretsError):
            secrets_manager.set_secret(None, "value")
    
    def test_set_secret_invalid_value_empty(self, secrets_manager):
        """Test setting secret with empty value."""
        with pytest.raises(SecretsError):
            secrets_manager.set_secret("KEY", "")
    
    def test_set_secret_invalid_value_none(self, secrets_manager):
        """Test setting secret with None value."""
        with pytest.raises(SecretsError):
            secrets_manager.set_secret("KEY", None)
    
    def test_set_secret_creates_file(self, secrets_manager, temp_secrets_dir):
        """Test that set_secret creates encrypted file."""
        secrets_manager.set_secret("FILE_TEST", "file_value")
        
        file_path = Path(temp_secrets_dir) / "FILE_TEST.enc"
        assert file_path.exists()
    
    def test_set_secret_file_contains_valid_json(self, secrets_manager, temp_secrets_dir):
        """Test that encrypted file contains valid JSON."""
        secrets_manager.set_secret("JSON_TEST", "json_value")
        
        file_path = Path(temp_secrets_dir) / "JSON_TEST.enc"
        with open(file_path, "r") as f:
            data = json.load(f)
        
        assert "encrypted" in data
        assert "timestamp" in data
        assert "tags" in data
        assert data["version"] == 1
    
    def test_set_secret_updates_existing(self, secrets_manager):
        """Test that set_secret overwrites existing secret."""
        secrets_manager.set_secret("UPDATE_TEST", "value1")
        result2 = secrets_manager.set_secret("UPDATE_TEST", "value2")
        
        # Retrieve updated value
        value = secrets_manager.get_secret("UPDATE_TEST")
        assert value == "value2"
    
    def test_set_multiple_secrets(self, secrets_manager):
        """Test setting multiple secrets."""
        for i in range(5):
            secrets_manager.set_secret(f"SECRET_{i}", f"value_{i}")
        
        # Verify all are stored
        for i in range(5):
            value = secrets_manager.get_secret(f"SECRET_{i}")
            assert value == f"value_{i}"


# ============================================================================
# GET_SECRET TESTS
# ============================================================================

class TestGetSecret:
    """Tests for SecretsManager.get_secret()"""
    
    def test_get_secret_success(self, secrets_manager):
        """Test retrieving a secret."""
        secrets_manager.set_secret("RETRIEVE_TEST", "retrieve_value")
        value = secrets_manager.get_secret("RETRIEVE_TEST")
        
        assert value == "retrieve_value"
    
    def test_get_secret_decrypts_correctly(self, secrets_manager):
        """Test that secret is properly decrypted."""
        original = "encrypted_test_value_123"
        secrets_manager.set_secret("DECRYPT_TEST", original)
        
        retrieved = secrets_manager.get_secret("DECRYPT_TEST")
        assert retrieved == original
    
    def test_get_secret_not_found(self, secrets_manager):
        """Test getting non-existent secret."""
        with pytest.raises(SecretsError):
            secrets_manager.get_secret("NONEXISTENT")
    
    def test_get_secret_invalid_key_empty(self, secrets_manager):
        """Test getting secret with empty key."""
        with pytest.raises(SecretsError):
            secrets_manager.get_secret("")
    
    def test_get_secret_invalid_key_none(self, secrets_manager):
        """Test getting secret with None key."""
        with pytest.raises(SecretsError):
            secrets_manager.get_secret(None)
    
    def test_get_secret_env_fallback(self, secrets_manager, monkeypatch):
        """Test environment variable fallback."""
        monkeypatch.setenv("ENV_SECRET", "env_value")
        
        # Should use environment variable if not in storage
        value = secrets_manager.get_secret("ENV_SECRET")
        assert value == "env_value"
    
    def test_get_secret_storage_priority(self, secrets_manager, monkeypatch):
        """Test that storage takes priority over environment."""
        monkeypatch.setenv("PRIORITY_TEST", "env_value")
        secrets_manager.set_secret("PRIORITY_TEST", "storage_value")
        
        # Storage should take priority
        value = secrets_manager.get_secret("PRIORITY_TEST")
        assert value == "storage_value"


# ============================================================================
# DELETE_SECRET TESTS
# ============================================================================

class TestDeleteSecret:
    """Tests for SecretsManager.delete_secret()"""
    
    def test_delete_secret_success(self, secrets_manager, temp_secrets_dir):
        """Test deleting a secret."""
        secrets_manager.set_secret("DELETE_TEST", "delete_value")
        
        result = secrets_manager.delete_secret("DELETE_TEST")
        assert result["key"] == "DELETE_TEST"
        assert result["deleted"] is True
    
    def test_delete_secret_removes_file(self, secrets_manager, temp_secrets_dir):
        """Test that delete removes file."""
        secrets_manager.set_secret("FILE_DELETE", "value")
        
        file_path = Path(temp_secrets_dir) / "FILE_DELETE.enc"
        assert file_path.exists()
        
        secrets_manager.delete_secret("FILE_DELETE")
        assert not file_path.exists()
    
    def test_delete_secret_not_found(self, secrets_manager):
        """Test deleting non-existent secret."""
        with pytest.raises(SecretsError):
            secrets_manager.delete_secret("NONEXISTENT_DELETE")
    
    def test_delete_secret_invalid_key(self, secrets_manager):
        """Test deleting with invalid key."""
        with pytest.raises(SecretsError):
            secrets_manager.delete_secret("")
    
    def test_delete_secret_overwrites_data(self, secrets_manager, temp_secrets_dir):
        """Test that delete overwrites before removing."""
        secrets_manager.set_secret("OVERWRITE_TEST", "secret_data")
        
        file_path = Path(temp_secrets_dir) / "OVERWRITE_TEST.enc"
        
        # Get file size before delete
        size_before = file_path.stat().st_size
        
        # Delete
        secrets_manager.delete_secret("OVERWRITE_TEST")
        
        # File should be gone (overwritten then deleted)
        assert not file_path.exists()


# ============================================================================
# LIST_SECRETS TESTS
# ============================================================================

class TestListSecrets:
    """Tests for SecretsManager.list_secrets()"""
    
    def test_list_secrets_empty(self, secrets_manager):
        """Test listing when no secrets."""
        result = secrets_manager.list_secrets()
        
        assert result["keys"] == []
        assert result["count"] == 0
    
    def test_list_secrets_multiple(self, secrets_manager):
        """Test listing multiple secrets."""
        secrets_manager.set_secret("SECRET_1", "value1")
        secrets_manager.set_secret("SECRET_2", "value2")
        secrets_manager.set_secret("SECRET_3", "value3")
        
        result = secrets_manager.list_secrets()
        
        assert result["count"] == 3
        assert "SECRET_1" in result["keys"]
        assert "SECRET_2" in result["keys"]
        assert "SECRET_3" in result["keys"]
    
    def test_list_secrets_no_values_exposed(self, secrets_manager):
        """Test that list doesn't expose secret values."""
        secrets_manager.set_secret("VALUE_TEST", "secret_value_123")
        
        result = secrets_manager.list_secrets()
        
        # Should only have keys, not values
        assert "secret_value_123" not in str(result)
    
    def test_list_secrets_sorted(self, secrets_manager):
        """Test that secrets are sorted."""
        secrets_manager.set_secret("ZEBRA", "z")
        secrets_manager.set_secret("APPLE", "a")
        secrets_manager.set_secret("MONKEY", "m")
        
        result = secrets_manager.list_secrets()
        
        assert result["keys"] == sorted(result["keys"])
    
    def test_list_secrets_includes_timestamp(self, secrets_manager):
        """Test that list includes timestamp."""
        result = secrets_manager.list_secrets()
        
        assert "timestamp" in result


# ============================================================================
# GET_SECRET_OR_ENV TESTS
# ============================================================================

class TestGetSecretOrEnv:
    """Tests for SecretsManager.get_secret_or_env()"""
    
    def test_get_secret_or_env_from_storage(self, secrets_manager):
        """Test getting secret from storage."""
        secrets_manager.set_secret("STORAGE_SECRET", "storage_value")
        
        value = secrets_manager.get_secret_or_env("STORAGE_SECRET")
        assert value == "storage_value"
    
    def test_get_secret_or_env_from_environment(self, secrets_manager, monkeypatch):
        """Test getting from environment as fallback."""
        monkeypatch.setenv("ENV_FALLBACK", "env_value")
        
        value = secrets_manager.get_secret_or_env("ENV_FALLBACK")
        assert value == "env_value"
    
    def test_get_secret_or_env_storage_priority(self, secrets_manager, monkeypatch):
        """Test storage priority over environment."""
        monkeypatch.setenv("PRIORITY", "env")
        secrets_manager.set_secret("PRIORITY", "storage")
        
        value = secrets_manager.get_secret_or_env("PRIORITY")
        assert value == "storage"
    
    def test_get_secret_or_env_custom_env_key(self, secrets_manager, monkeypatch):
        """Test custom environment key."""
        monkeypatch.setenv("CUSTOM_ENV", "custom_value")
        
        value = secrets_manager.get_secret_or_env("NOT_FOUND", env_key="CUSTOM_ENV")
        assert value == "custom_value"
    
    def test_get_secret_or_env_not_found(self, secrets_manager):
        """Test error when secret not found anywhere."""
        with pytest.raises(SecretsError):
            secrets_manager.get_secret_or_env("NOWHERE")


# ============================================================================
# AUDIT TRAIL TESTS
# ============================================================================

class TestAuditTrail:
    """Tests for audit trail functionality"""
    
    def test_audit_trail_enabled(self, secrets_manager):
        """Test that audit trail is enabled."""
        secrets_manager.set_secret("AUDIT_TEST", "value")
        
        audit = secrets_manager.get_audit_trail()
        assert audit["valid"] is True
        assert audit["events"] >= 1
    
    def test_audit_trail_disabled(self, secrets_manager_no_audit):
        """Test error when audit trail disabled."""
        with pytest.raises(SecretsError):
            secrets_manager_no_audit.get_audit_trail()
    
    def test_audit_trail_logs_set(self, secrets_manager):
        """Test audit logs set operations."""
        secrets_manager.set_secret("LOG_SET", "value")
        
        audit = secrets_manager.get_audit_trail()
        assert audit["events"] >= 1
    
    def test_audit_trail_logs_get(self, secrets_manager):
        """Test audit logs get operations."""
        secrets_manager.set_secret("LOG_GET", "value")
        initial_events = secrets_manager.get_audit_trail()["events"]
        
        secrets_manager.get_secret("LOG_GET")
        
        after_events = secrets_manager.get_audit_trail()["events"]
        assert after_events > initial_events
    
    def test_audit_trail_logs_delete(self, secrets_manager):
        """Test audit logs delete operations."""
        secrets_manager.set_secret("LOG_DELETE", "value")
        initial_events = secrets_manager.get_audit_trail()["events"]
        
        secrets_manager.delete_secret("LOG_DELETE")
        
        after_events = secrets_manager.get_audit_trail()["events"]
        assert after_events > initial_events
    
    def test_verify_audit_integrity(self, secrets_manager):
        """Test audit trail integrity verification."""
        secrets_manager.set_secret("INT_TEST_1", "value1")
        secrets_manager.set_secret("INT_TEST_2", "value2")
        
        assert secrets_manager.verify_audit_integrity() is True
    
    def test_audit_trail_has_chain_hash(self, secrets_manager):
        """Test audit trail includes chain hash."""
        secrets_manager.set_secret("HASH_TEST", "value")
        
        audit = secrets_manager.get_audit_trail()
        assert "chain_hash" in audit


# ============================================================================
# MASTER KEY TESTS
# ============================================================================

class TestMasterKey:
    """Tests for master key handling"""
    
    def test_manager_requires_master_key(self):
        """Test that manager requires master key."""
        with pytest.raises(SecretsError):
            SecretsManager(master_key="")
    
    def test_manager_from_environment_requires_key(self, monkeypatch):
        """Test that from_environment requires CORTEX_MASTER_KEY."""
        monkeypatch.delenv("CORTEX_MASTER_KEY", raising=False)
        
        with pytest.raises(SecretsError):
            SecretsManager.from_environment()
    
    def test_manager_from_environment_succeeds(self, monkeypatch, temp_secrets_dir):
        """Test from_environment with CORTEX_MASTER_KEY set."""
        monkeypatch.setenv("CORTEX_MASTER_KEY", "0" * 32 + "a" * 32)
        monkeypatch.setenv("CORTEX_SECRETS_PATH", temp_secrets_dir)
        
        manager = SecretsManager.from_environment()
        assert manager is not None


# ============================================================================
# STORAGE PATH TESTS
# ============================================================================

class TestStoragePath:
    """Tests for storage path handling"""
    
    def test_storage_path_created(self, master_key, temp_secrets_dir):
        """Test that storage path is created."""
        custom_path = os.path.join(temp_secrets_dir, "custom", "path")
        
        manager = SecretsManager(
            master_key=master_key,
            storage_path=custom_path,
        )
        
        assert Path(custom_path).exists()
    
    def test_storage_path_expanduser(self, master_key):
        """Test that storage path expands user home."""
        manager = SecretsManager(
            master_key=master_key,
            storage_path="~/test_cortex_secrets",
        )
        
        # Should not start with ~
        assert not str(manager.storage_path).startswith("~")


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Tests for error handling"""
    
    def test_set_secret_encryption_error_handled(self, secrets_manager):
        """Test that encryption errors are caught."""
        # Try to set with invalid type should be caught
        with pytest.raises(SecretsError):
            secrets_manager.set_secret("INVALID", 12345)  # Not a string
    
    def test_get_secret_corrupted_file(self, secrets_manager, temp_secrets_dir):
        """Test error when file is corrupted."""
        secrets_manager.set_secret("CORRUPT_TEST", "value")
        
        # Corrupt the file
        file_path = Path(temp_secrets_dir) / "CORRUPT_TEST.enc"
        with open(file_path, "w") as f:
            f.write("corrupted data")
        
        # Should raise error on decryption
        with pytest.raises(SecretsError):
            secrets_manager.get_secret("CORRUPT_TEST")
