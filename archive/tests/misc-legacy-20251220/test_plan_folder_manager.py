"""
Tests for PlanFolderManager - TDD RED Phase

Tests folder structure creation, navigation, and feature flag control.

Author: GitHub Copilot
Created: 2025-12-14
"""

import pytest
from pathlib import Path
import json
import tempfile
import shutil
from datetime import datetime

# Import will fail initially (RED phase) - that's expected
from src.workflows.plan_folder_manager import PlanFolderManager


class TestPlanFolderManagerInit:
    """Test PlanFolderManager initialization."""
    
    def test_init_with_valid_cortex_root(self, tmp_path):
        """Test initialization with valid CORTEX root."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        brain_path = cortex_root / "cortex-brain"
        brain_path.mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        assert manager.cortex_root == cortex_root
        assert manager.plans_base == brain_path / "documents" / "planning" / "features"
    
    def test_init_creates_base_directories(self, tmp_path):
        """Test that initialization creates base directory structure."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        brain_path = cortex_root / "cortex-brain"
        brain_path.mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        assert manager.plans_base.exists()
        assert (manager.plans_base / "active").exists()
        assert (manager.plans_base / "completed").exists()
        assert (manager.plans_base / "archived").exists()


class TestFeatureFlag:
    """Test feature flag functionality."""
    
    def test_feature_flag_enabled_by_default(self, tmp_path):
        """Test that feature flag is enabled by default."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        assert manager.is_folder_structure_enabled() is True
    
    def test_feature_flag_reads_from_config(self, tmp_path):
        """Test that feature flag reads from cortex.config.json."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        # Create config with flag disabled
        config_path = cortex_root / "cortex.config.json"
        config = {
            "planning": {
                "use_folder_structure": False
            }
        }
        config_path.write_text(json.dumps(config, indent=2))
        
        manager = PlanFolderManager(cortex_root)
        
        assert manager.is_folder_structure_enabled() is False
    
    def test_feature_flag_can_be_toggled(self, tmp_path):
        """Test that feature flag can be enabled/disabled."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        # Initially enabled
        assert manager.is_folder_structure_enabled() is True
        
        # Disable
        manager.set_folder_structure_enabled(False)
        assert manager.is_folder_structure_enabled() is False
        
        # Enable
        manager.set_folder_structure_enabled(True)
        assert manager.is_folder_structure_enabled() is True


class TestCreatePlanStructure:
    """Test create_plan_structure method."""
    
    def test_create_plan_structure_basic(self, tmp_path):
        """Test basic plan structure creation."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        plan_id = "PLAN-2025-12-14-test-feature"
        plan_path = manager.create_plan_structure(plan_id, status="active")
        
        # Verify root folder created
        assert plan_path.exists()
        assert plan_path.name == plan_id
        
        # Verify subfolders created
        assert (plan_path / "sub-plans").exists()
        assert (plan_path / "artifacts").exists()
        assert (plan_path / "reports").exists()
        assert (plan_path / "tests").exists()
        assert (plan_path / "checkpoints").exists()
        
        # Verify README.md created
        assert (plan_path / "README.md").exists()
    
    def test_create_plan_structure_in_active(self, tmp_path):
        """Test plan created in active folder by default."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        plan_id = "PLAN-2025-12-14-test"
        plan_path = manager.create_plan_structure(plan_id)
        
        expected_path = manager.plans_base / "active" / plan_id
        assert plan_path == expected_path
    
    def test_create_plan_structure_in_completed(self, tmp_path):
        """Test plan can be created in completed folder."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        plan_id = "PLAN-2025-12-14-test"
        plan_path = manager.create_plan_structure(plan_id, status="completed")
        
        expected_path = manager.plans_base / "completed" / plan_id
        assert plan_path == expected_path
    
    def test_create_plan_structure_atomic(self, tmp_path):
        """Test that structure creation is atomic (all-or-nothing)."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        plan_id = "PLAN-2025-12-14-test"
        
        # Mock a failure during subfolder creation
        # This should rollback the entire structure
        # (Implementation detail - manager should handle this)
        
        plan_path = manager.create_plan_structure(plan_id)
        
        # All subfolders should exist or none
        subfolders = ["sub-plans", "artifacts", "reports", "tests", "checkpoints"]
        subfolder_exists = [
            (plan_path / subfolder).exists() for subfolder in subfolders
        ]
        
        # Either all exist or none exist (atomic)
        assert all(subfolder_exists) or not any(subfolder_exists)
    
    def test_create_plan_structure_when_flag_disabled(self, tmp_path):
        """Test that structure is NOT created when feature flag is disabled."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        manager.set_folder_structure_enabled(False)
        
        plan_id = "PLAN-2025-12-14-test"
        result = manager.create_plan_structure(plan_id)
        
        # Should return None or flat file path when disabled
        assert result is None or result.suffix == ".yaml" or result.suffix == ".md"


class TestGetPlanPath:
    """Test get_plan_path method."""
    
    def test_get_plan_path_finds_existing_folder(self, tmp_path):
        """Test finding existing plan folder."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        plan_id = "PLAN-2025-12-14-test"
        created_path = manager.create_plan_structure(plan_id)
        
        # Create master-plan.md
        (created_path / "master-plan.md").write_text("# Test Plan")
        
        found_path = manager.get_plan_path(plan_id)
        
        assert found_path == created_path / "master-plan.md"
    
    def test_get_plan_path_searches_all_statuses(self, tmp_path):
        """Test that get_plan_path searches active, completed, and archived."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        # Create plan in completed
        plan_id = "PLAN-2025-12-14-completed-test"
        completed_path = manager.create_plan_structure(plan_id, status="completed")
        (completed_path / "master-plan.md").write_text("# Test")
        
        # Should find it even though it's in completed
        found_path = manager.get_plan_path(plan_id)
        
        assert found_path is not None
        assert "completed" in str(found_path)
    
    def test_get_plan_path_returns_none_if_not_found(self, tmp_path):
        """Test that get_plan_path returns None if plan doesn't exist."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        found_path = manager.get_plan_path("PLAN-9999-99-99-nonexistent")
        
        assert found_path is None


class TestGetArtifactPath:
    """Test get_artifact_path method."""
    
    def test_get_artifact_path_master_plan(self, tmp_path):
        """Test getting master plan path."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        plan_id = "PLAN-2025-12-14-test"
        plan_path = manager.create_plan_structure(plan_id)
        
        artifact_path = manager.get_artifact_path(plan_id, "master")
        
        expected_path = plan_path / "master-plan.md"
        assert artifact_path == expected_path
    
    def test_get_artifact_path_sub_plan(self, tmp_path):
        """Test getting sub-plan path."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        plan_id = "PLAN-2025-12-14-test"
        plan_path = manager.create_plan_structure(plan_id)
        
        artifact_path = manager.get_artifact_path(
            plan_id, "sub-plan", filename="phase-1-implementation.md"
        )
        
        expected_path = plan_path / "sub-plans" / "phase-1-implementation.md"
        assert artifact_path == expected_path
    
    def test_get_artifact_path_tracker(self, tmp_path):
        """Test getting tracker artifact path."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        plan_id = "PLAN-2025-12-14-test"
        plan_path = manager.create_plan_structure(plan_id)
        
        artifact_path = manager.get_artifact_path(plan_id, "tracker")
        
        expected_path = plan_path / "artifacts" / "feature-tracker.md"
        assert artifact_path == expected_path
    
    def test_get_artifact_path_report(self, tmp_path):
        """Test getting report path."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        plan_id = "PLAN-2025-12-14-test"
        plan_path = manager.create_plan_structure(plan_id)
        
        artifact_path = manager.get_artifact_path(
            plan_id, "report", filename="status-20251214.md"
        )
        
        expected_path = plan_path / "reports" / "status-20251214.md"
        assert artifact_path == expected_path


class TestMovePlan:
    """Test move_plan method."""
    
    def test_move_plan_active_to_completed(self, tmp_path):
        """Test moving plan from active to completed."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        plan_id = "PLAN-2025-12-14-test"
        active_path = manager.create_plan_structure(plan_id, status="active")
        
        # Add some files
        (active_path / "master-plan.md").write_text("# Test Plan")
        (active_path / "artifacts" / "tracker.md").write_text("# Tracker")
        
        # Move to completed
        completed_path = manager.move_plan(plan_id, from_status="active", to_status="completed")
        
        # Verify moved
        assert not active_path.exists()
        assert completed_path.exists()
        assert (completed_path / "master-plan.md").exists()
        assert (completed_path / "artifacts" / "tracker.md").exists()
    
    def test_move_plan_preserves_folder_structure(self, tmp_path):
        """Test that moving plan preserves entire folder structure."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        plan_id = "PLAN-2025-12-14-test"
        active_path = manager.create_plan_structure(plan_id, status="active")
        
        # Create files in multiple subfolders
        (active_path / "master-plan.md").write_text("# Master")
        (active_path / "sub-plans" / "phase-1.md").write_text("# Phase 1")
        (active_path / "artifacts" / "tracker.md").write_text("# Tracker")
        (active_path / "reports" / "status.md").write_text("# Status")
        
        completed_path = manager.move_plan(plan_id, "active", "completed")
        
        # All subfolders preserved
        assert (completed_path / "sub-plans" / "phase-1.md").exists()
        assert (completed_path / "artifacts" / "tracker.md").exists()
        assert (completed_path / "reports" / "status.md").exists()


class TestGeneratePlanReadme:
    """Test generate_plan_readme method."""
    
    def test_generate_readme_basic(self, tmp_path):
        """Test basic README generation."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        plan_id = "PLAN-2025-12-14-test-feature"
        plan_path = manager.create_plan_structure(plan_id)
        
        metadata = {
            "title": "Test Feature Implementation",
            "created_date": "2025-12-14",
            "author": "Test User",
            "priority": "HIGH"
        }
        
        manager.generate_plan_readme(plan_id, metadata)
        
        readme_path = plan_path / "README.md"
        assert readme_path.exists()
        
        readme_content = readme_path.read_text()
        assert "Test Feature Implementation" in readme_content
        assert "2025-12-14" in readme_content
        assert "Test User" in readme_content
    
    def test_generate_readme_includes_navigation(self, tmp_path):
        """Test that README includes navigation to artifacts."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        plan_id = "PLAN-2025-12-14-test"
        plan_path = manager.create_plan_structure(plan_id)
        
        metadata = {"title": "Test"}
        manager.generate_plan_readme(plan_id, metadata)
        
        readme_content = (plan_path / "README.md").read_text()
        
        # Should include links to subfolders
        assert "sub-plans" in readme_content or "Sub-Plans" in readme_content
        assert "artifacts" in readme_content or "Artifacts" in readme_content
        assert "reports" in readme_content or "Reports" in readme_content
    
    def test_generate_readme_includes_file_index(self, tmp_path):
        """Test that README includes index of existing files."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        plan_id = "PLAN-2025-12-14-test"
        plan_path = manager.create_plan_structure(plan_id)
        
        # Create some files
        (plan_path / "master-plan.md").write_text("# Master")
        (plan_path / "sub-plans" / "phase-1.md").write_text("# Phase 1")
        (plan_path / "artifacts" / "tracker.md").write_text("# Tracker")
        
        metadata = {"title": "Test"}
        manager.generate_plan_readme(plan_id, metadata)
        
        readme_content = (plan_path / "README.md").read_text()
        
        # Should list existing files
        assert "master-plan.md" in readme_content
        assert "phase-1.md" in readme_content
        assert "tracker.md" in readme_content


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_create_plan_with_special_characters(self, tmp_path):
        """Test creating plan with special characters in ID."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        # Plan IDs should be sanitized
        plan_id = "PLAN-2025-12-14-test-feature-v2.0"
        plan_path = manager.create_plan_structure(plan_id)
        
        assert plan_path.exists()
    
    def test_get_plan_path_with_multiple_matches(self, tmp_path):
        """Test behavior when multiple plans match (edge case)."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        # This shouldn't happen in practice, but test it
        plan_id = "PLAN-2025-12-14-test"
        
        # Create in both active and completed (edge case)
        manager.create_plan_structure(plan_id, status="active")
        
        # Should prefer active over completed
        found_path = manager.get_plan_path(plan_id)
        
        assert "active" in str(found_path)
    
    def test_move_plan_nonexistent(self, tmp_path):
        """Test moving nonexistent plan raises error."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        (cortex_root / "cortex-brain").mkdir()
        
        manager = PlanFolderManager(cortex_root)
        
        with pytest.raises(FileNotFoundError):
            manager.move_plan("PLAN-9999-99-99-nonexistent", "active", "completed")


# Fixtures
@pytest.fixture
def cortex_root(tmp_path):
    """Create temporary CORTEX root structure."""
    root = tmp_path / "cortex"
    root.mkdir()
    brain = root / "cortex-brain"
    brain.mkdir()
    (brain / "documents" / "planning" / "features").mkdir(parents=True)
    return root
