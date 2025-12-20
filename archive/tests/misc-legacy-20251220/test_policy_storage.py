"""
Tests for Policy Storage

Purpose: Test Tier 3 policy storage and tracking capabilities

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Repository: https://github.com/asifhussain60/CORTEX
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.policy.policy_storage import PolicyStorage


class TestPolicyStorage:
    """Test suite for PolicyStorage"""
    
    @pytest.fixture
    def temp_brain_path(self):
        """Create temporary brain directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def storage(self, temp_brain_path):
        """Create PolicyStorage instance"""
        return PolicyStorage(brain_path=temp_brain_path)
    
    @pytest.fixture
    def sample_policy_file(self):
        """Create sample policy file"""
        content = """# Test Policy
Version: 1.0
Date: 2025-11-26

## Security Requirements

- Passwords MUST NOT be stored in plain text.
- All user input MUST be validated.

## Testing Requirements

- Test coverage MUST be greater than 80%.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name
        yield temp_path
        Path(temp_path).unlink()
    
    def test_storage_initialization(self, storage, temp_brain_path):
        """Test storage initializes correctly"""
        assert storage is not None
        assert storage.brain_path == Path(temp_brain_path)
        assert storage.tier3_path.exists()
        assert storage.tier3_path == Path(temp_brain_path) / "tier3" / "policies"
    
    def test_get_repo_path(self, storage):
        """Test getting repository path"""
        repo_path = storage.get_repo_path("test-repo")
        
        assert repo_path.exists()
        assert (repo_path / "policies").exists()
        assert (repo_path / "reports").exists()
    
    def test_get_db_connection(self, storage):
        """Test database connection"""
        conn = storage.get_db_connection("test-repo")
        
        assert conn is not None
        
        # Verify schema
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'policies' in tables
        assert 'validations' in tables
        
        conn.close()
    
    def test_store_policy(self, storage, sample_policy_file):
        """Test storing a policy"""
        policy_id, changed = storage.store_policy(
            repo_name="test-repo",
            policy_file=sample_policy_file,
            policy_name="test-policy"
        )
        
        assert policy_id == "test-repo-test-policy"
        assert changed is True
        
        # Verify policy stored
        repo_path = storage.get_repo_path("test-repo")
        stored_policy = repo_path / "policies" / Path(sample_policy_file).name
        assert stored_policy.exists()
        
        # Verify hash file
        hash_file = repo_path / "policies" / f"{Path(sample_policy_file).name}.sha256"
        assert hash_file.exists()
    
    def test_store_policy_unchanged(self, storage, sample_policy_file):
        """Test storing same policy twice"""
        # First store
        policy_id1, changed1 = storage.store_policy(
            repo_name="test-repo",
            policy_file=sample_policy_file,
            policy_name="test-policy"
        )
        
        assert changed1 is True
        
        # Second store (unchanged)
        policy_id2, changed2 = storage.store_policy(
            repo_name="test-repo",
            policy_file=sample_policy_file,
            policy_name="test-policy"
        )
        
        assert policy_id1 == policy_id2
        assert changed2 is False
    
    def test_store_policy_with_changes(self, storage):
        """Test storing policy with changes"""
        # Create first version
        content1 = "# Policy v1\n\n- Rule MUST be followed."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content1)
            file1 = f.name
        
        try:
            policy_id1, changed1 = storage.store_policy(
                repo_name="test-repo",
                policy_file=file1,
                policy_name="versioned-policy"
            )
            assert changed1 is True
            
            # Modify file
            content2 = "# Policy v2\n\n- Rule MUST be followed.\n- New rule SHOULD apply."
            with open(file1, 'w') as f:
                f.write(content2)
            
            # Store modified version
            policy_id2, changed2 = storage.store_policy(
                repo_name="test-repo",
                policy_file=file1,
                policy_name="versioned-policy"
            )
            
            assert policy_id1 == policy_id2
            assert changed2 is True
        
        finally:
            Path(file1).unlink()
    
    def test_list_policies(self, storage, sample_policy_file):
        """Test listing policies"""
        # Store policy
        storage.store_policy(
            repo_name="test-repo",
            policy_file=sample_policy_file,
            policy_name="test-policy"
        )
        
        # List policies
        policies = storage.list_policies("test-repo")
        
        assert len(policies) == 1
        assert policies[0]['policy_name'] == "test-policy"
        assert policies[0]['rules_count'] > 0
    
    def test_check_for_changes_none(self, storage, sample_policy_file):
        """Test checking for changes when none exist"""
        storage.store_policy(
            repo_name="test-repo",
            policy_file=sample_policy_file,
            policy_name="test-policy"
        )
        
        changed = storage.check_for_changes("test-repo")
        assert len(changed) == 0
    
    def test_get_latest_report_empty(self, storage):
        """Test getting latest report when none exists"""
        report = storage.get_latest_report("test-repo")
        assert report is None
    
    def test_validate_and_store(self, storage, sample_policy_file):
        """Test validation and report storage"""
        # Store policy
        policy_id, _ = storage.store_policy(
            repo_name="test-repo",
            policy_file=sample_policy_file,
            policy_name="test-policy"
        )
        
        # Validate against current codebase
        report = storage.validate_and_store(
            repo_name="test-repo",
            policy_id=policy_id,
            codebase_path="."
        )
        
        assert report is not None
        assert hasattr(report, 'compliance_score')
        assert hasattr(report, 'violations')
        
        # Verify report saved
        repo_path = storage.get_repo_path("test-repo")
        latest_report = repo_path / "latest-report.json"
        assert latest_report.exists()
    
    def test_get_validation_history(self, storage, sample_policy_file):
        """Test getting validation history"""
        # Store and validate
        policy_id, _ = storage.store_policy(
            repo_name="test-repo",
            policy_file=sample_policy_file,
            policy_name="test-policy"
        )
        
        storage.validate_and_store(
            repo_name="test-repo",
            policy_id=policy_id,
            codebase_path="."
        )
        
        # Get history
        history = storage.get_validation_history("test-repo", policy_id)
        
        assert len(history) >= 1
        assert 'compliance_score' in history[0]
        assert 'violations_count' in history[0]
    
    def test_validate_nonexistent_policy(self, storage):
        """Test validating with nonexistent policy"""
        with pytest.raises(ValueError, match="Policy not found"):
            storage.validate_and_store(
                repo_name="test-repo",
                policy_id="nonexistent",
                codebase_path="."
            )
    
    def test_store_policy_missing_file(self, storage):
        """Test storing nonexistent policy file"""
        with pytest.raises(FileNotFoundError):
            storage.store_policy(
                repo_name="test-repo",
                policy_file="nonexistent.md",
                policy_name="test"
            )
