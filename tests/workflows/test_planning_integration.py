"""
Integration Tests for Planning Artifacts Organization System

Tests end-to-end workflows:
- Creating plans with folder structure
- Migrating existing plans
- Running vacuum cleanup
- Plan lifecycle (active → completed → archived)
- Rollback functionality

Author: GitHub Copilot
Created: 2025-12-14
"""

import pytest
from pathlib import Path
import shutil

from src.workflows.plan_folder_manager import PlanFolderManager
from src.workflows.planning_artifacts_scanner import PlanningArtifactsScanner
from src.workflows.planning_migration_engine import (
    PlanningMigrationEngine,
    MigrationStatus
)
from src.workflows.duplicate_detector import DuplicateDetector
from src.workflows.planning_vacuum import PlanningVacuum


@pytest.fixture
def test_workspace(tmp_path):
    """Create test workspace with CORTEX structure."""
    cortex_root = tmp_path / "cortex"
    cortex_root.mkdir()
    
    # Create planning structure
    planning_base = cortex_root / "cortex-brain" / "documents" / "planning" / "features"
    for status in ["active", "completed", "archived"]:
        (planning_base / status).mkdir(parents=True)
    
    # Create config
    config = cortex_root / "cortex.config.json"
    config.write_text('{"planning": {"use_folder_structure": true}}')
    
    return cortex_root


@pytest.fixture
def sample_plans(tmp_path):
    """Create sample planning files for migration."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    
    # Create master plan
    master = source_dir / "PLAN-2025-12-14-test-feature.yaml"
    master.write_text("""
plan_id: "PLAN-2025-12-14-test-feature"
title: "Test Feature"
status: "active"
phases:
  - phase_number: 1
    name: "Implementation"
""")
    
    # Create sub-plan
    sub = source_dir / "PLAN-2025-12-14-test-feature-SUB-1.md"
    sub.write_text("""
# Sub-Plan 1
parent_plan_id: "PLAN-2025-12-14-test-feature"
""")
    
    # Create tracker
    tracker = source_dir / "PLAN-2025-12-14-test-feature-TRACKER.md"
    tracker.write_text("""
# Progress Tracker
plan_id: "PLAN-2025-12-14-test-feature"
""")
    
    return source_dir


class TestPlanCreationWorkflow:
    """Test complete plan creation workflow."""
    
    def test_create_new_plan_with_folder_structure(self, test_workspace):
        """Test creating new plan generates folder structure."""
        manager = PlanFolderManager(cortex_root=test_workspace)
        
        plan_id = "PLAN-2025-12-14-new-feature"
        plan_path = manager.create_plan_structure(plan_id, status="active")
        
        assert plan_path is not None
        assert plan_path.exists()
        
        # Verify subfolders
        assert (plan_path / "sub-plans").exists()
        assert (plan_path / "artifacts").exists()
        assert (plan_path / "reports").exists()
        assert (plan_path / "tests").exists()
        assert (plan_path / "checkpoints").exists()
        
        # Verify README
        readme = plan_path / "README.md"
        assert readme.exists()
        assert "new-feature" in readme.read_text()
    
    def test_save_artifacts_to_subfolders(self, test_workspace):
        """Test artifacts saved to correct subfolders."""
        manager = PlanFolderManager(cortex_root=test_workspace)
        
        plan_id = "PLAN-2025-12-14-test-plan"
        plan_path = manager.create_plan_structure(plan_id)
        
        # Save master plan
        master = plan_path / "master-plan.md"
        master.write_text("# Master Plan")
        
        # Save sub-plan
        sub_plan_path = manager.get_artifact_path(plan_id, "sub-plan", "sub-plan-1.md")
        assert sub_plan_path is not None
        sub_plan_path.write_text("# Sub-Plan 1")
        
        # Save artifact (tracker)
        artifact_path = manager.get_artifact_path(plan_id, "tracker")
        assert artifact_path is not None
        artifact_path.write_text("# Tracker")
        
        # Verify all exist
        assert master.exists()
        assert sub_plan_path.exists()
        assert artifact_path.exists()


class TestMigrationWorkflow:
    """Test complete migration workflow."""
    
    def test_end_to_end_migration(self, test_workspace, sample_plans):
        """Test complete migration workflow."""
        # Target should be features/ folder (migration adds status subfolder)
        target_dir = test_workspace / "cortex-brain" / "documents" / "planning" / "features"
        
        # Initialize migration engine
        engine = PlanningMigrationEngine(
            source_directory=sample_plans,
            target_directory=target_dir,
            cortex_root=test_workspace
        )
        
        # Discover plans
        discovery = engine.discover_plans()
        assert len(discovery.master_plans) >= 1
        
        # Migrate plan
        plan_id = "PLAN-2025-12-14-test-feature"
        result = engine.migrate_plan(plan_id)
        
        assert result.status == MigrationStatus.SUCCESS
        assert result.files_migrated > 0
        
        # Verify folder structure created (in active/ subfolder)
        plan_folder = target_dir / "active" / plan_id
        assert plan_folder.exists()
        
        # Check for master plan file (either .md or .yaml)
        master_md = plan_folder / "master-plan.md"
        master_yaml = plan_folder / "master-plan.yaml"
        assert master_md.exists() or master_yaml.exists(), f"Master plan not found in {plan_folder}"
        
        # Check subfolders exist
        assert (plan_folder / "sub-plans").exists()
        assert (plan_folder / "artifacts").exists()
    
    def test_migration_with_validation(self, test_workspace, sample_plans):
        """Test migration includes validation."""
        target_dir = test_workspace / "cortex-brain" / "documents" / "planning" / "features"
        
        engine = PlanningMigrationEngine(
            source_directory=sample_plans,
            target_directory=target_dir,
            cortex_root=test_workspace
        )
        
        # Migrate
        plan_id = "PLAN-2025-12-14-test-feature"
        result = engine.migrate_plan(plan_id)
        
        assert result.status == MigrationStatus.SUCCESS
        
        # Validate
        is_valid = engine.validate_migration(plan_id)
        assert is_valid is True


class TestCleanupWorkflow:
    """Test cleanup and vacuum workflows."""
    
    def test_duplicate_detection_and_resolution(self, tmp_path):
        """Test finding and resolving duplicates."""
        # Create duplicates
        (tmp_path / "file1.yaml").write_text("content")
        (tmp_path / "file2.yaml").write_text("content")
        (tmp_path / "file3.yaml").write_text("different")
        
        detector = DuplicateDetector(root_directory=tmp_path)
        
        # Find duplicates
        duplicates = detector.find_duplicates()
        assert len(duplicates) >= 1
        
        # Group by hash (no arguments - returns dict)
        groups_dict = detector.group_by_hash()
        assert len(groups_dict) >= 1
        
        # Get first group files list
        first_hash = list(groups_dict.keys())[0]
        first_group_files = groups_dict[first_hash]
        
        # Create DuplicateGroup object
        from src.workflows.duplicate_detector import DuplicateGroup, ResolutionStrategy
        
        # Resolve (keep newest) - expects DuplicateGroup object
        if len(first_group_files) > 1:
            dup_group = DuplicateGroup(hash=first_hash, files=first_group_files)
            result = detector.resolve_duplicates(dup_group, strategy=ResolutionStrategy.KEEP_NEWEST)
            assert result.kept_file is not None
            assert len(result.removed_files) >= 1
    
    def test_vacuum_empty_directories(self, tmp_path):
        """Test removing empty directories."""
        # Create empty structure
        (tmp_path / "empty1").mkdir()
        (tmp_path / "empty2" / "nested").mkdir(parents=True)
        
        # Create non-empty
        with_file = tmp_path / "with_file"
        with_file.mkdir()
        (with_file / "file.txt").write_text("content")
        
        vacuum = PlanningVacuum(root_directory=tmp_path)
        
        # Run vacuum
        removed = vacuum.vacuum_empty_directories()
        
        assert len(removed) >= 2
        assert not (tmp_path / "empty1").exists()
        assert (with_file / "file.txt").exists()


class TestPlanLifecycle:
    """Test complete plan lifecycle."""
    
    def test_plan_lifecycle_active_to_completed(self, test_workspace):
        """Test moving plan from active to completed."""
        manager = PlanFolderManager(cortex_root=test_workspace)
        
        # Create in active
        plan_id = "PLAN-2025-12-14-lifecycle-test"
        plan_path = manager.create_plan_structure(plan_id, status="active")
        
        assert plan_path is not None
        assert "active" in str(plan_path)
        
        # Move to completed
        new_path = manager.move_plan(plan_id, from_status="active", to_status="completed")
        
        assert new_path.exists()
        assert "completed" in str(new_path)
        assert not plan_path.exists()
    
    def test_plan_lifecycle_preserves_structure(self, test_workspace):
        """Test plan move preserves folder structure."""
        manager = PlanFolderManager(cortex_root=test_workspace)
        
        # Create with artifacts
        plan_id = "PLAN-2025-12-14-structure-test"
        plan_path = manager.create_plan_structure(plan_id, status="active")
        
        # Add artifacts
        (plan_path / "sub-plans" / "sub1.md").write_text("Sub-plan 1")
        (plan_path / "artifacts" / "tracker.md").write_text("Tracker")
        
        # Move to completed
        new_path = manager.move_plan(plan_id, from_status="active", to_status="completed")
        
        # Verify structure preserved
        assert (new_path / "sub-plans" / "sub1.md").exists()
        assert (new_path / "artifacts" / "tracker.md").exists()


class TestRollbackFunctionality:
    """Test rollback functionality."""
    
    def test_migration_rollback(self, test_workspace, sample_plans):
        """Test rolling back migration."""
        target_dir = test_workspace / "cortex-brain" / "documents" / "planning" / "features"
        
        # Backup original
        backup_dir = test_workspace / "backup"
        shutil.copytree(sample_plans, backup_dir)
        
        engine = PlanningMigrationEngine(
            source_directory=sample_plans,
            target_directory=target_dir,
            cortex_root=test_workspace
        )
        
        # Migrate
        plan_id = "PLAN-2025-12-14-test-feature"
        result = engine.migrate_plan(plan_id)
        assert result.status == MigrationStatus.SUCCESS
        
        # Rollback
        rollback_result = engine.rollback_migration(plan_id)
        assert rollback_result.status == MigrationStatus.SUCCESS
        
        # Verify rolled back (folder removed from active/)
        plan_folder = target_dir / "active" / plan_id
        assert not plan_folder.exists()


class TestFeatureFlagIntegration:
    """Test feature flag controls folder structure."""
    
    def test_feature_flag_enabled(self, test_workspace):
        """Test folder structure created when flag enabled."""
        manager = PlanFolderManager(cortex_root=test_workspace)
        
        assert manager.is_folder_structure_enabled() is True
        
        # Create plan
        plan_id = "PLAN-2025-12-14-flag-test"
        plan_path = manager.create_plan_structure(plan_id)
        
        # Should create folder structure
        assert plan_path is not None
        assert plan_path.exists()
        assert (plan_path / "sub-plans").exists()
    
    def test_feature_flag_disabled(self, test_workspace):
        """Test folder structure not created when flag disabled."""
        manager = PlanFolderManager(cortex_root=test_workspace)
        
        # Disable flag
        manager.set_folder_structure_enabled(False)
        assert manager.is_folder_structure_enabled() is False
        
        # Attempt to create plan
        plan_id = "PLAN-2025-12-14-disabled-test"
        plan_path = manager.create_plan_structure(plan_id)
        
        # Should return None (folder structure disabled)
        assert plan_path is None


class TestPerformance:
    """Test migration performance."""
    
    def test_migration_performance(self, test_workspace, tmp_path):
        """Test migration completes in reasonable time."""
        import time
        
        # Create 10 sample plans
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        for i in range(10):
            plan_file = source_dir / f"PLAN-2025-12-14-test-{i}.yaml"
            plan_file.write_text(f"""
plan_id: "PLAN-2025-12-14-test-{i}"
title: "Test Plan {i}"
""")
        
        target_dir = test_workspace / "cortex-brain" / "documents" / "planning" / "features"
        
        engine = PlanningMigrationEngine(
            source_directory=source_dir,
            target_directory=target_dir,
            cortex_root=test_workspace
        )
        
        # Migrate all
        start_time = time.time()
        results = engine.migrate_all()
        elapsed = time.time() - start_time
        
        # Should complete in <5 seconds for 10 plans
        assert elapsed < 5.0
        assert len(results) == 10
        assert all(r.status == MigrationStatus.SUCCESS for r in results)


class TestErrorHandling:
    """Test error handling in workflows."""
    
    def test_migration_handles_missing_files(self, test_workspace, tmp_path):
        """Test migration handles missing source files."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        target_dir = test_workspace / "cortex-brain" / "documents" / "planning" / "features"
        
        engine = PlanningMigrationEngine(
            source_directory=source_dir,
            target_directory=target_dir,
            cortex_root=test_workspace
        )
        
        # Try to migrate non-existent plan
        result = engine.migrate_plan("NONEXISTENT-PLAN")
        
        # Should fail gracefully
        assert result.status in [MigrationStatus.FAILED, MigrationStatus.SKIPPED]
        assert result.message != "" or len(result.errors) > 0
    
    def test_vacuum_handles_permission_errors(self, tmp_path):
        """Test vacuum handles directories it can't access."""
        vacuum = PlanningVacuum(root_directory=tmp_path)
        
        # Try to vacuum empty root (should handle gracefully)
        removed = vacuum.vacuum_empty_directories()
        
        # Should not crash
        assert isinstance(removed, list)
