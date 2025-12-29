"""
Tests for PlanFolderManager - Hierarchical Plan Structure

Validates:
- Folder creation with required subfolders
- Naming conventions (00-master-plan.md, 11-temp-planning-session.md)
- Progress tracker initialization
- README generation
- Version detection
- Folder validation
- Plan moving between statuses

Author: CORTEX Development Team
Created: December 27, 2025
"""

import json
import pytest
import shutil
from datetime import datetime
from pathlib import Path
from src.utils.plan_folder_manager import PlanFolderManager


@pytest.fixture
def temp_project_root(tmp_path):
    """Create temporary project structure."""
    project_root = tmp_path / "cortex"
    planning_root = project_root / "cortex-brain" / "documents" / "planning"
    planning_root.mkdir(parents=True, exist_ok=True)
    return project_root


@pytest.fixture
def folder_manager(temp_project_root):
    """Create PlanFolderManager instance."""
    return PlanFolderManager(temp_project_root)


class TestPlanFolderCreation:
    """Test folder structure creation."""
    
    def test_create_plan_folder_success(self, folder_manager, temp_project_root):
        """Test successful plan folder creation."""
        plan_folder = folder_manager.create_plan_folder(
            plan_id="test-feature-v1",
            title="Test Feature",
            complexity_tier=3,
            status="active"
        )
        
        # Check folder exists
        assert plan_folder.exists()
        assert plan_folder.name == "test-feature-v1"
        
        # Check required subfolders
        for subfolder in PlanFolderManager.REQUIRED_SUBFOLDERS:
            assert (plan_folder / subfolder).exists()
        
        # Check progress tracker
        tracker_path = plan_folder / PlanFolderManager.TRACKER_NAME
        assert tracker_path.exists()
        
        tracker_data = json.loads(tracker_path.read_text())
        assert tracker_data["plan_id"] == "test-feature-v1"
        assert tracker_data["title"] == "Test Feature"
        assert tracker_data["complexity_tier"] == 3
        assert tracker_data["status"] == "planning"
        
        # Check README
        readme_path = plan_folder / PlanFolderManager.README_NAME
        assert readme_path.exists()
        assert "Test Feature" in readme_path.read_text()
    
    def test_create_plan_folder_invalid_status(self, folder_manager):
        """Test folder creation with invalid status."""
        with pytest.raises(ValueError, match="Invalid status"):
            folder_manager.create_plan_folder(
                plan_id="test-v1",
                title="Test",
                complexity_tier=3,
                status="invalid-status"
            )
    
    def test_create_plan_folder_duplicate(self, folder_manager):
        """Test folder creation with existing plan."""
        folder_manager.create_plan_folder(
            plan_id="duplicate-v1",
            title="Duplicate",
            complexity_tier=3,
            status="active"
        )
        
        # Try to create same plan again
        with pytest.raises(ValueError, match="already exists"):
            folder_manager.create_plan_folder(
                plan_id="duplicate-v1",
                title="Duplicate",
                complexity_tier=3,
                status="active"
            )
    
    def test_create_plan_folder_with_metadata(self, folder_manager):
        """Test folder creation with custom metadata."""
        metadata = {
            "tags": ["security", "auth"],
            "priority": "high",
            "assigned_to": "team-alpha"
        }
        
        plan_folder = folder_manager.create_plan_folder(
            plan_id="metadata-test-v1",
            title="Metadata Test",
            complexity_tier=4,
            status="active",
            metadata=metadata
        )
        
        tracker_path = plan_folder / PlanFolderManager.TRACKER_NAME
        tracker_data = json.loads(tracker_path.read_text())
        
        assert tracker_data["metadata"] == metadata
        assert tracker_data["complexity_tier"] == 4


class TestVersionDetection:
    """Test version detection and increment."""
    
    def test_detect_next_version_no_existing(self, folder_manager):
        """Test version detection with no existing plans."""
        version = folder_manager.detect_next_version("new-feature", status="active")
        assert version == 1
    
    def test_detect_next_version_with_existing(self, folder_manager):
        """Test version detection with existing versions."""
        # Create v1 and v2
        folder_manager.create_plan_folder(
            plan_id="feature-v1",
            title="Feature V1",
            complexity_tier=3,
            status="active"
        )
        folder_manager.create_plan_folder(
            plan_id="feature-v2",
            title="Feature V2",
            complexity_tier=3,
            status="active"
        )
        
        # Next version should be 3
        version = folder_manager.detect_next_version("feature", status="active")
        assert version == 3
    
    def test_detect_next_version_noncontiguous(self, folder_manager):
        """Test version detection with gaps (v1, v3 exist, v2 missing)."""
        folder_manager.create_plan_folder(
            plan_id="gap-v1",
            title="Gap V1",
            complexity_tier=3,
            status="active"
        )
        folder_manager.create_plan_folder(
            plan_id="gap-v3",
            title="Gap V3",
            complexity_tier=3,
            status="active"
        )
        
        # Should return 4 (max + 1)
        version = folder_manager.detect_next_version("gap", status="active")
        assert version == 4


class TestPlanMoving:
    """Test moving plans between status folders."""
    
    def test_move_plan_success(self, folder_manager):
        """Test successful plan move from temp-plans to active."""
        # Create in temp-plans
        plan_folder = folder_manager.create_plan_folder(
            plan_id="moveable-v1",
            title="Moveable Plan",
            complexity_tier=3,
            status="temp-plans"
        )
        
        assert plan_folder.parent.name == "temp-plans"
        
        # Move to active
        new_folder = folder_manager.move_plan(
            plan_id="moveable-v1",
            from_status="temp-plans",
            to_status="active"
        )
        
        assert new_folder.parent.name == "active"
        assert not (plan_folder).exists()  # Old location gone
        assert new_folder.exists()  # New location exists
    
    def test_move_plan_nonexistent_source(self, folder_manager):
        """Test moving nonexistent plan."""
        with pytest.raises(ValueError, match="not found"):
            folder_manager.move_plan(
                plan_id="nonexistent-v1",
                from_status="temp-plans",
                to_status="active"
            )
    
    def test_move_plan_existing_target(self, folder_manager):
        """Test moving to existing target location."""
        folder_manager.create_plan_folder(
            plan_id="conflict-v1",
            title="Source",
            complexity_tier=3,
            status="temp-plans"
        )
        folder_manager.create_plan_folder(
            plan_id="conflict-v1",
            title="Target",
            complexity_tier=3,
            status="active"
        )
        
        with pytest.raises(ValueError, match="already exists"):
            folder_manager.move_plan(
                plan_id="conflict-v1",
                from_status="temp-plans",
                to_status="active"
            )


class TestFolderValidation:
    """Test folder structure validation."""
    
    def test_validate_folder_structure_valid(self, folder_manager):
        """Test validation of valid folder structure."""
        plan_folder = folder_manager.create_plan_folder(
            plan_id="valid-v1",
            title="Valid Plan",
            complexity_tier=3,
            status="active"
        )
        
        # Create master plan
        (plan_folder / PlanFolderManager.MASTER_PLAN_NAME).write_text("# Master Plan")
        
        is_valid, issues = folder_manager.validate_folder_structure(plan_folder)
        
        assert is_valid
        assert len(issues) == 0
    
    def test_validate_folder_structure_missing_subfolders(self, folder_manager, temp_project_root):
        """Test validation with missing subfolders."""
        # Create incomplete folder manually
        plan_folder = temp_project_root / "cortex-brain" / "documents" / "planning" / "active" / "incomplete-v1"
        plan_folder.mkdir(parents=True)
        
        # Only create context folder, missing others
        (plan_folder / "context").mkdir()
        
        is_valid, issues = folder_manager.validate_folder_structure(plan_folder)
        
        assert not is_valid
        assert len(issues) > 0
        assert any("Missing required subfolder" in issue for issue in issues)
    
    def test_validate_folder_structure_missing_master_plan(self, folder_manager):
        """Test validation with missing master plan."""
        plan_folder = folder_manager.create_plan_folder(
            plan_id="no-plan-v1",
            title="No Plan",
            complexity_tier=3,
            status="active"
        )
        
        # Don't create master plan file
        is_valid, issues = folder_manager.validate_folder_structure(plan_folder)
        
        assert not is_valid
        assert any("00-master-plan.md" in issue for issue in issues)
    
    def test_validate_folder_structure_nonexistent_folder(self, folder_manager, temp_project_root):
        """Test validation of nonexistent folder."""
        fake_folder = temp_project_root / "nonexistent"
        
        is_valid, issues = folder_manager.validate_folder_structure(fake_folder)
        
        assert not is_valid
        assert len(issues) == 1
        assert "does not exist" in issues[0]


class TestGetPlanFolder:
    """Test retrieving existing plan folders."""
    
    def test_get_plan_folder_exists(self, folder_manager):
        """Test getting existing plan folder."""
        created_folder = folder_manager.create_plan_folder(
            plan_id="exists-v1",
            title="Exists",
            complexity_tier=3,
            status="active"
        )
        
        retrieved_folder = folder_manager.get_plan_folder("exists-v1", status="active")
        
        assert retrieved_folder == created_folder
    
    def test_get_plan_folder_nonexistent(self, folder_manager):
        """Test getting nonexistent plan folder."""
        retrieved_folder = folder_manager.get_plan_folder("nonexistent-v1", status="active")
        
        assert retrieved_folder is None


class TestNamingConventions:
    """Test file naming conventions."""
    
    def test_master_plan_naming(self, folder_manager):
        """Verify 00-master-plan.md naming convention."""
        assert PlanFolderManager.MASTER_PLAN_NAME == "00-master-plan.md"
    
    def test_temp_plan_naming(self, folder_manager):
        """Verify 11-temp-planning-session.md naming convention."""
        assert PlanFolderManager.TEMP_PLAN_NAME == "11-temp-planning-session.md"
    
    def test_tracker_naming(self, folder_manager):
        """Verify progress-tracker.json location."""
        assert PlanFolderManager.TRACKER_NAME == "tracking/progress-tracker.json"
