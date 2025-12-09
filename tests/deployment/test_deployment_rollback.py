"""
TDD Test Suite: Deployment Rollback System

Tests for comprehensive deployment rollback capabilities including
phase-level snapshots, partial rollbacks, and validation.

RED Phase: All tests should fail initially
GREEN Phase: Implement deployment_rollback.py to pass tests
REFACTOR Phase: Optimize and clean up implementation

Author: Asif Hussain
Version: 1.0.0
"""

import pytest
import tempfile
import json
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Import will fail initially (RED phase) - implement in GREEN phase
try:
    from src.deployment.deployment_rollback import (
        DeploymentRollbackManager,
        RollbackSnapshot,
        RollbackType,
        RollbackValidation,
        create_deployment_snapshot,
        execute_rollback,
        validate_rollback
    )
except ImportError:
    # RED phase - module doesn't exist yet
    DeploymentRollbackManager = None
    RollbackSnapshot = None
    RollbackType = None
    RollbackValidation = None
    create_deployment_snapshot = None
    execute_rollback = None
    validate_rollback = None


@pytest.fixture
def temp_cortex_root():
    """Create temporary CORTEX root for testing."""
    temp_dir = tempfile.mkdtemp()
    cortex_root = Path(temp_dir)
    
    # Create expected directory structure
    (cortex_root / "cortex-brain" / "deployments" / "rollback-points").mkdir(parents=True)
    (cortex_root / "src").mkdir(parents=True)
    (cortex_root / "tests").mkdir(parents=True)
    (cortex_root / "cortex.config.json").write_text('{"root_path": "' + str(cortex_root) + '"}')
    
    yield cortex_root
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_git():
    """Mock git operations."""
    with patch('subprocess.run') as mock_run:
        # Default successful git operations
        mock_run.return_value = Mock(returncode=0, stdout="abc123def456\n", stderr="")
        yield mock_run


# Test Class 1: Initialization and Configuration
class TestDeploymentRollbackInitialization:
    """Test rollback manager initialization."""
    
    def test_manager_initialization(self, temp_cortex_root):
        """Test rollback manager initializes correctly."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        assert manager is not None
        assert manager.cortex_root == temp_cortex_root
        assert manager.rollback_dir == temp_cortex_root / "cortex-brain" / "deployments" / "rollback-points"
        assert manager.rollback_dir.exists()
    
    def test_rollback_directory_creation(self, temp_cortex_root):
        """Test rollback directory is created if missing."""
        rollback_dir = temp_cortex_root / "cortex-brain" / "deployments" / "rollback-points"
        rollback_dir.rmdir()  # Remove directory
        
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        assert manager.rollback_dir.exists()


# Test Class 2: Snapshot Creation
class TestSnapshotCreation:
    """Test deployment snapshot creation."""
    
    def test_create_code_snapshot(self, temp_cortex_root, mock_git):
        """Test code snapshot creation."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        snapshot = manager.create_snapshot(
            phase="BUILD",
            snapshot_type=RollbackType.CODE_ONLY
        )
        
        assert snapshot is not None
        assert snapshot.phase == "BUILD"
        assert snapshot.snapshot_type == RollbackType.CODE_ONLY
        assert snapshot.git_commit is not None
        assert snapshot.timestamp is not None
    
    def test_create_full_snapshot(self, temp_cortex_root, mock_git):
        """Test full snapshot with code, brain, and config."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        # Create some brain state
        brain_file = temp_cortex_root / "cortex-brain" / "knowledge-graph.yaml"
        brain_file.write_text("test: data")
        
        snapshot = manager.create_snapshot(
            phase="DEPLOY",
            snapshot_type=RollbackType.FULL
        )
        
        assert snapshot is not None
        assert snapshot.snapshot_type == RollbackType.FULL
        assert snapshot.git_commit is not None
        assert snapshot.brain_state is not None
        assert snapshot.config_state is not None
    
    def test_snapshot_persistence(self, temp_cortex_root, mock_git):
        """Test snapshot is saved to disk."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        snapshot = manager.create_snapshot(phase="VALIDATE")
        snapshot_id = snapshot.snapshot_id
        
        # Check manifest file exists
        manifest_path = manager.rollback_dir / f"{snapshot_id}.json"
        assert manifest_path.exists()
        
        # Verify manifest content
        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)
        
        assert manifest_data['snapshot_id'] == snapshot_id
        assert manifest_data['phase'] == "VALIDATE"


# Test Class 3: Rollback Types
class TestRollbackTypes:
    """Test different rollback type behaviors."""
    
    def test_code_only_rollback(self, temp_cortex_root, mock_git):
        """Test code-only rollback (excludes brain state)."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        snapshot = manager.create_snapshot(
            phase="BUILD",
            snapshot_type=RollbackType.CODE_ONLY
        )
        
        result = manager.execute_rollback(
            snapshot_id=snapshot.snapshot_id,
            rollback_type=RollbackType.CODE_ONLY
        )
        
        assert result.success is True
        assert result.code_restored is True
        assert result.brain_restored is False  # Brain not restored for CODE_ONLY
    
    def test_brain_only_rollback(self, temp_cortex_root, mock_git):
        """Test brain-only rollback (keeps code changes)."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        # Create brain state
        brain_file = temp_cortex_root / "cortex-brain" / "knowledge-graph.yaml"
        brain_file.write_text("original: state")
        
        snapshot = manager.create_snapshot(
            phase="VERIFY",
            snapshot_type=RollbackType.BRAIN_ONLY
        )
        
        # Modify brain state
        brain_file.write_text("modified: state")
        
        result = manager.execute_rollback(
            snapshot_id=snapshot.snapshot_id,
            rollback_type=RollbackType.BRAIN_ONLY
        )
        
        assert result.success is True
        assert result.code_restored is False  # Code not touched
        assert result.brain_restored is True
    
    def test_full_rollback(self, temp_cortex_root, mock_git):
        """Test full rollback restores everything."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        snapshot = manager.create_snapshot(
            phase="DEPLOY",
            snapshot_type=RollbackType.FULL
        )
        
        result = manager.execute_rollback(
            snapshot_id=snapshot.snapshot_id,
            rollback_type=RollbackType.FULL
        )
        
        assert result.success is True
        assert result.code_restored is True
        assert result.brain_restored is True
        assert result.config_restored is True


# Test Class 4: Rollback Validation
class TestRollbackValidation:
    """Test rollback validation checks."""
    
    def test_validate_before_rollback(self, temp_cortex_root, mock_git):
        """Test validation runs before rollback."""
        # Configure mock to return empty git status (clean working directory)
        def git_status_side_effect(*args, **kwargs):
            command = args[0] if args else kwargs.get('args', [])
            if 'status' in command and '--porcelain' in command:
                return Mock(returncode=0, stdout="", stderr="")  # Empty = clean
            return Mock(returncode=0, stdout="abc123def456\n", stderr="")
        
        mock_git.side_effect = git_status_side_effect
        
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        snapshot = manager.create_snapshot(phase="BUILD")
        
        validation = manager.validate_rollback(snapshot_id=snapshot.snapshot_id)
        
        assert validation is not None
        assert validation.snapshot_exists is True
        assert validation.git_clean is True
        assert validation.safe_to_rollback is True
    
    def test_validation_fails_with_uncommitted_changes(self, temp_cortex_root):
        """Test validation fails when uncommitted changes exist."""
        with patch('subprocess.run') as mock_run:
            # Simulate uncommitted changes
            mock_run.return_value = Mock(
                returncode=0,
                stdout=" M src/file.py\n",  # Modified file
                stderr=""
            )
            
            manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
            snapshot = manager.create_snapshot(phase="BUILD")
            
            validation = manager.validate_rollback(snapshot_id=snapshot.snapshot_id)
            
            assert validation.git_clean is False
            assert validation.safe_to_rollback is False
            assert "uncommitted changes" in validation.warning.lower()
    
    def test_validation_checks_snapshot_exists(self, temp_cortex_root, mock_git):
        """Test validation checks snapshot exists."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        # Try to validate non-existent snapshot
        validation = manager.validate_rollback(snapshot_id="nonexistent123")
        
        assert validation.snapshot_exists is False
        assert validation.safe_to_rollback is False


# Test Class 5: Phase-Level Snapshots
class TestPhaseLevelSnapshots:
    """Test snapshots at different deployment phases."""
    
    def test_pre_flight_snapshot(self, temp_cortex_root, mock_git):
        """Test snapshot before pre-flight phase."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        snapshot = manager.create_snapshot(phase="PRE_FLIGHT")
        
        assert snapshot.phase == "PRE_FLIGHT"
        assert snapshot.snapshot_id is not None
    
    def test_build_phase_snapshot(self, temp_cortex_root, mock_git):
        """Test snapshot after build phase."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        snapshot = manager.create_snapshot(phase="BUILD")
        
        assert snapshot.phase == "BUILD"
    
    def test_deploy_phase_snapshot(self, temp_cortex_root, mock_git):
        """Test snapshot after deploy phase."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        snapshot = manager.create_snapshot(phase="DEPLOY")
        
        assert snapshot.phase == "DEPLOY"
    
    def test_list_phase_snapshots(self, temp_cortex_root, mock_git):
        """Test listing snapshots for specific phase."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        # Create multiple phase snapshots
        manager.create_snapshot(phase="BUILD")
        manager.create_snapshot(phase="DEPLOY")
        manager.create_snapshot(phase="BUILD")
        
        build_snapshots = manager.list_snapshots(phase="BUILD")
        
        assert len(build_snapshots) == 2
        assert all(s.phase == "BUILD" for s in build_snapshots)


# Test Class 6: Snapshot Listing and Querying
class TestSnapshotListing:
    """Test snapshot listing and querying."""
    
    def test_list_all_snapshots(self, temp_cortex_root, mock_git):
        """Test listing all snapshots."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        # Create snapshots
        manager.create_snapshot(phase="BUILD")
        manager.create_snapshot(phase="DEPLOY")
        
        snapshots = manager.list_snapshots()
        
        assert len(snapshots) >= 2
    
    def test_list_snapshots_by_type(self, temp_cortex_root, mock_git):
        """Test listing snapshots filtered by type."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        manager.create_snapshot(phase="BUILD", snapshot_type=RollbackType.CODE_ONLY)
        manager.create_snapshot(phase="DEPLOY", snapshot_type=RollbackType.FULL)
        
        code_snapshots = manager.list_snapshots(snapshot_type=RollbackType.CODE_ONLY)
        
        assert len(code_snapshots) >= 1
        assert all(s.snapshot_type == RollbackType.CODE_ONLY for s in code_snapshots)
    
    def test_get_latest_snapshot(self, temp_cortex_root, mock_git):
        """Test retrieving most recent snapshot."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        manager.create_snapshot(phase="BUILD")
        latest = manager.create_snapshot(phase="DEPLOY")
        
        retrieved = manager.get_latest_snapshot()
        
        assert retrieved is not None
        assert retrieved.snapshot_id == latest.snapshot_id


# Test Class 7: Rollback Execution
class TestRollbackExecution:
    """Test rollback execution mechanics."""
    
    def test_execute_successful_rollback(self, temp_cortex_root, mock_git):
        """Test successful rollback execution."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        snapshot = manager.create_snapshot(phase="BUILD")
        
        result = manager.execute_rollback(snapshot_id=snapshot.snapshot_id)
        
        assert result.success is True
        assert result.snapshot_id == snapshot.snapshot_id
    
    def test_rollback_with_dry_run(self, temp_cortex_root, mock_git):
        """Test dry-run rollback (preview only)."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        snapshot = manager.create_snapshot(phase="BUILD")
        
        result = manager.execute_rollback(
            snapshot_id=snapshot.snapshot_id,
            dry_run=True
        )
        
        assert result.success is True
        assert result.executed is False  # Not actually executed
        assert result.preview is not None
    
    def test_rollback_generates_report(self, temp_cortex_root, mock_git):
        """Test rollback generates detailed report."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        snapshot = manager.create_snapshot(phase="BUILD")
        result = manager.execute_rollback(snapshot_id=snapshot.snapshot_id)
        
        assert result.report is not None
        assert "snapshot_id" in result.report
        assert "timestamp" in result.report
        assert "files_restored" in result.report


# Test Class 8: Post-Rollback Validation
class TestPostRollbackValidation:
    """Test validation after rollback execution."""
    
    def test_post_rollback_system_stability(self, temp_cortex_root, mock_git):
        """Test system stability check after rollback."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        snapshot = manager.create_snapshot(phase="BUILD")
        result = manager.execute_rollback(snapshot_id=snapshot.snapshot_id)
        
        # Run post-rollback validation
        validation = manager.validate_post_rollback(result)
        
        assert validation.system_stable is True
        assert validation.git_consistent is True
    
    def test_post_rollback_file_integrity(self, temp_cortex_root, mock_git):
        """Test file integrity after rollback."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        snapshot = manager.create_snapshot(phase="BUILD")
        result = manager.execute_rollback(snapshot_id=snapshot.snapshot_id)
        
        validation = manager.validate_post_rollback(result)
        
        assert validation.files_intact is True


# Test Class 9: Rollback Manifest Management
class TestRollbackManifestManagement:
    """Test rollback manifest CRUD operations."""
    
    def test_save_rollback_manifest(self, temp_cortex_root, mock_git):
        """Test saving rollback manifest to disk."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        snapshot = manager.create_snapshot(phase="BUILD")
        
        manifest_file = manager.rollback_dir / f"{snapshot.snapshot_id}.json"
        assert manifest_file.exists()
    
    def test_load_rollback_manifest(self, temp_cortex_root, mock_git):
        """Test loading rollback manifest from disk."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        original = manager.create_snapshot(phase="BUILD")
        
        # Load snapshot from disk
        loaded = manager.load_snapshot(snapshot_id=original.snapshot_id)
        
        assert loaded is not None
        assert loaded.snapshot_id == original.snapshot_id
        assert loaded.phase == original.phase
    
    def test_delete_rollback_manifest(self, temp_cortex_root, mock_git):
        """Test deleting old rollback manifests."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        snapshot = manager.create_snapshot(phase="BUILD")
        snapshot_id = snapshot.snapshot_id
        
        # Delete snapshot
        result = manager.delete_snapshot(snapshot_id=snapshot_id)
        
        assert result is True
        
        # Verify manifest file deleted
        manifest_file = manager.rollback_dir / f"{snapshot_id}.json"
        assert not manifest_file.exists()


# Test Class 10: End-to-End Rollback Workflow
class TestEndToEndRollbackWorkflow:
    """Test complete rollback workflow."""
    
    def test_full_deployment_rollback_workflow(self, temp_cortex_root, mock_git):
        """Test complete deployment rollback scenario."""
        # Configure mock to return empty git status (clean working directory)
        def git_status_side_effect(*args, **kwargs):
            command = args[0] if args else kwargs.get('args', [])
            if 'status' in command and '--porcelain' in command:
                return Mock(returncode=0, stdout="", stderr="")  # Empty = clean
            return Mock(returncode=0, stdout="abc123def456\n", stderr="")
        
        mock_git.side_effect = git_status_side_effect
        
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        # Step 1: Create snapshot before deployment
        pre_deploy = manager.create_snapshot(
            phase="PRE_FLIGHT",
            snapshot_type=RollbackType.FULL
        )
        assert pre_deploy is not None
        
        # Step 2: Simulate deployment (create some files)
        (temp_cortex_root / "src" / "new_feature.py").write_text("# New code")
        
        # Step 3: Create post-deploy snapshot
        post_deploy = manager.create_snapshot(
            phase="DEPLOY",
            snapshot_type=RollbackType.FULL
        )
        assert post_deploy is not None
        
        # Step 4: Validate rollback possible
        validation = manager.validate_rollback(snapshot_id=pre_deploy.snapshot_id)
        assert validation.safe_to_rollback is True
        
        # Step 5: Execute rollback to pre-deploy state
        result = manager.execute_rollback(
            snapshot_id=pre_deploy.snapshot_id,
            rollback_type=RollbackType.FULL
        )
        assert result.success is True
        
        # Step 6: Validate post-rollback system state
        post_validation = manager.validate_post_rollback(result)
        assert post_validation.system_stable is True
    
    def test_partial_rollback_workflow(self, temp_cortex_root, mock_git):
        """Test partial rollback (brain only, keep code)."""
        manager = DeploymentRollbackManager(cortex_root=temp_cortex_root)
        
        # Create brain state
        brain_file = temp_cortex_root / "cortex-brain" / "knowledge-graph.yaml"
        brain_file.write_text("version: 1.0")
        
        # Snapshot
        snapshot = manager.create_snapshot(
            phase="DEPLOY",
            snapshot_type=RollbackType.FULL
        )
        
        # Modify brain
        brain_file.write_text("version: 2.0")
        
        # Rollback brain only (keep code changes)
        result = manager.execute_rollback(
            snapshot_id=snapshot.snapshot_id,
            rollback_type=RollbackType.BRAIN_ONLY
        )
        
        assert result.success is True
        assert result.brain_restored is True
        assert result.code_restored is False  # Code not rolled back


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
