"""
Integration Tests for Secrets Management - Phase 76 Stage 3

End-to-end integration tests for the complete secrets management system
with encryption, audit trail, environment validation, and integrity enforcement.

Authority: phase-76-production-foundation-trilogy.yaml S3
AC-ID: AC-PHASE76-S3-INTEGRATION
"""

import pytest
import os
import tempfile
from pathlib import Path

from cortex.secrets.secrets_manager import SecretsManager
from cortex.secrets.environment_validation import EnvironmentValidator
from cortex.governance.enforcement.agents.secrets_integrity_agent import SecretsIntegrityAgent


class TestE2ESecretsManagement:
    """End-to-end secrets management workflow tests"""
    
    def test_complete_workflow_with_audit(self):
        """Test complete workflow: set → get → list → audit → delete."""
        with tempfile.TemporaryDirectory() as tmpdir:
            master_key = "0" * 32 + "a" * 32
            manager = SecretsManager(
                master_key=master_key,
                storage_path=tmpdir,
                audit_enabled=True,
            )
            
            # Set multiple secrets
            manager.set_secret("DB_PASSWORD", "prod_password123")
            manager.set_secret("API_TOKEN", "token_xyz789")
            manager.set_secret("ADMIN_KEY", "admin_secret_key")
            
            # List secrets (verify no values exposed)
            secrets = manager.list_secrets()
            assert secrets["count"] == 3
            assert "prod_password123" not in str(secrets)
            
            # Get secrets back
            db_pass = manager.get_secret("DB_PASSWORD")
            assert db_pass == "prod_password123"
            
            api_token = manager.get_secret("API_TOKEN")
            assert api_token == "token_xyz789"
            
            # Verify audit trail
            audit = manager.get_audit_trail()
            assert audit["valid"] is True
            assert audit["events"] >= 5  # 3 sets + 2 gets
            
            # Delete one secret
            manager.delete_secret("API_TOKEN")
            
            # Verify deletion
            secrets_after = manager.list_secrets()
            assert secrets_after["count"] == 2
            assert "API_TOKEN" not in str(secrets_after["keys"])
            
            # Verify audit logs deletion
            audit_final = manager.get_audit_trail()
            assert audit_final["events"] > audit["events"]
    
    def test_encryption_decryption_roundtrip(self):
        """Test that encryption/decryption preserves original value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            master_key = "test_master_key_" + "a" * 32
            manager = SecretsManager(
                master_key=master_key,
                storage_path=tmpdir,
            )
            
            original_values = [
                "simple_password",
                "complex!@#$%^&*()_+-=[]{}|;:',.<>?/",
                "unicode_测试_🔐",
                "multiline\nvalue\nwith\nnewlines",
                "very_" + "long_" * 100 + "value",
            ]
            
            for i, value in enumerate(original_values):
                key = f"TEST_{i}"
                manager.set_secret(key, value)
                
                retrieved = manager.get_secret(key)
                assert retrieved == value, f"Roundtrip failed for {value}"
    
    def test_multi_secret_isolation(self):
        """Test that secrets are properly isolated from each other."""
        with tempfile.TemporaryDirectory() as tmpdir:
            master_key = "0" * 32 + "a" * 32
            manager = SecretsManager(
                master_key=master_key,
                storage_path=tmpdir,
            )
            
            manager.set_secret("SECRET_A", "value_a")
            manager.set_secret("SECRET_B", "value_b")
            manager.set_secret("SECRET_C", "value_c")
            
            # Verify each secret has its own storage
            assert len(list(Path(tmpdir).glob("*.enc"))) == 3
            
            # Verify no cross-contamination
            assert manager.get_secret("SECRET_A") == "value_a"
            assert manager.get_secret("SECRET_B") == "value_b"
            assert manager.get_secret("SECRET_C") == "value_c"
    
    def test_environment_validation_integration(self):
        """Test environment validation in secrets context."""
        validator = EnvironmentValidator()
        validator.add_schema("TEST_KEY", var_type="string", required=True)
        validator.add_schema("TEST_PORT", var_type="port", required=False)
        
        os.environ["TEST_KEY"] = "value"
        os.environ["TEST_PORT"] = "8080"
        
        result = validator.validate_all()
        assert result["valid"] is True
        assert result["values"]["TEST_KEY"] == "value"
        assert result["values"]["TEST_PORT"] == 8080
    
    def test_integrity_agent_with_real_keys(self, monkeypatch):
        """Test SecretsIntegrityAgent with realistic scenario."""
        agent = SecretsIntegrityAgent()
        
        # Scenario 1: Missing key
        monkeypatch.delenv("CORTEX_MASTER_KEY", raising=False)
        result = agent.validate_pre_flight(check_environment=False)
        assert result.passed is False
        
        # Scenario 2: Valid key
        valid_key = "0" * 32 + "a" * 32
        monkeypatch.setenv("CORTEX_MASTER_KEY", valid_key)
        result = agent.validate_pre_flight(check_environment=False)
        assert result.passed is True
        
        # Scenario 3: Production deployment
        monkeypatch.setenv("CORTEX_MASTER_KEY", valid_key)
        result = agent.validate_operation_context("DEPLOY")
        assert result.passed is True


class TestSecureStoragePatterns:
    """Tests for secure storage patterns and best practices"""
    
    def test_storage_isolation_per_workspace(self):
        """Test that different workspaces have isolated storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            master_key = "0" * 32 + "a" * 32
            
            # Workspace 1
            workspace1_dir = os.path.join(tmpdir, "workspace1")
            manager1 = SecretsManager(master_key, workspace1_dir)
            manager1.set_secret("SECRET", "workspace1_value")
            
            # Workspace 2
            workspace2_dir = os.path.join(tmpdir, "workspace2")
            manager2 = SecretsManager(master_key, workspace2_dir)
            manager2.set_secret("SECRET", "workspace2_value")
            
            # Verify isolation
            assert manager1.get_secret("SECRET") == "workspace1_value"
            assert manager2.get_secret("SECRET") == "workspace2_value"
    
    def test_master_key_sensitivity(self):
        """Test that wrong master key fails decryption."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager1 = SecretsManager("0" * 32 + "a" * 32, tmpdir)
            manager1.set_secret("SENSITIVE", "secret_data")
            
            # Try to decrypt with wrong key
            manager2 = SecretsManager("1" * 32 + "b" * 32, tmpdir)
            
            with pytest.raises(Exception):  # Should fail decryption
                manager2.get_secret("SENSITIVE")


class TestAuditTrailIntegrity:
    """Tests for audit trail integrity and compliance"""
    
    def test_audit_chain_integrity_preserved(self):
        """Test that audit chain integrity is maintained."""
        with tempfile.TemporaryDirectory() as tmpdir:
            master_key = "0" * 32 + "a" * 32
            manager = SecretsManager(master_key, tmpdir, audit_enabled=True)
            
            # Perform operations
            manager.set_secret("KEY1", "value1")
            manager.get_secret("KEY1")
            manager.set_secret("KEY2", "value2")
            manager.delete_secret("KEY1")
            
            # Verify chain integrity
            assert manager.verify_audit_integrity() is True
            
            # Get audit trail
            audit = manager.get_audit_trail()
            assert audit["valid"] is True
            assert audit["events"] >= 4
    
    def test_audit_trail_completeness(self):
        """Test that all operations are logged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            master_key = "0" * 32 + "a" * 32
            manager = SecretsManager(master_key, tmpdir, audit_enabled=True)
            
            # Track initial audit state
            initial_audit = manager.get_audit_trail()
            initial_count = initial_audit["events"]
            
            # Perform operations
            manager.set_secret("LOG_TEST", "value")
            audit_after_set = manager.get_audit_trail()
            assert audit_after_set["events"] > initial_count
            
            count_after_set = audit_after_set["events"]
            
            manager.get_secret("LOG_TEST")
            audit_after_get = manager.get_audit_trail()
            assert audit_after_get["events"] > count_after_set
            
            count_after_get = audit_after_get["events"]
            
            manager.delete_secret("LOG_TEST")
            audit_after_delete = manager.get_audit_trail()
            assert audit_after_delete["events"] > count_after_get


class TestErrorRecovery:
    """Tests for error handling and recovery"""
    
    def test_corrupted_secret_recovery(self):
        """Test handling of corrupted secret files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            master_key = "0" * 32 + "a" * 32
            manager = SecretsManager(master_key, tmpdir)
            
            # Set a secret
            manager.set_secret("RECOVER_TEST", "original_value")
            
            # Corrupt the file
            secret_file = Path(tmpdir) / "RECOVER_TEST.enc"
            with open(secret_file, "w") as f:
                f.write("corrupted_data_xyz")
            
            # Try to retrieve - should fail gracefully
            with pytest.raises(Exception):
                manager.get_secret("RECOVER_TEST")
            
            # File still exists
            assert secret_file.exists()
    
    def test_partial_deletion_recovery(self):
        """Test recovery from partial deletion scenarios."""
        with tempfile.TemporaryDirectory() as tmpdir:
            master_key = "0" * 32 + "a" * 32
            manager = SecretsManager(master_key, tmpdir)
            
            manager.set_secret("KEEP", "keep_value")
            manager.set_secret("DELETE", "delete_value")
            
            manager.delete_secret("DELETE")
            
            # Verify kept secret is still there
            assert manager.get_secret("KEEP") == "keep_value"
            
            # Verify deleted secret is gone
            with pytest.raises(Exception):
                manager.get_secret("DELETE")
