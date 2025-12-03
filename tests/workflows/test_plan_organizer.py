"""
Tests for plan file organization by status.

This module tests automatic organization of plan files into status-specific
directories (active, completed, etc.) and auto-move on status changes.
"""

import pytest
from pathlib import Path
from src.workflows.plan_organizer import PlanOrganizer, PlanOrganizerError


@pytest.fixture
def organizer(tmp_path):
    """Create a plan organizer with temporary brain path."""
    brain_path = tmp_path / "cortex-brain"
    brain_path.mkdir(parents=True)
    return PlanOrganizer(brain_path)


@pytest.fixture
def planning_dir_with_plan(tmp_path):
    """Create planning directory with a sample plan."""
    brain_path = tmp_path / "cortex-brain"
    planning_dir = brain_path / "documents" / "planning"
    planning_dir.mkdir(parents=True)
    
    # Create a plan file in root planning directory
    plan_file = planning_dir / "test-plan.md"
    plan_file.write_text("""---
plan_id: ORG-001
title: Test Plan
status: proposed
priority: medium
created_date: 2025-12-03
estimated_hours: 10
---
# Test Plan Content
""")
    
    return brain_path, plan_file


class TestPlanOrganizerInitialization:
    """Test organizer initialization."""
    
    def test_creates_status_directories(self, organizer):
        """Should create active/ and completed/ directories."""
        planning_dir = organizer.brain_path / "documents" / "planning" / "features"
        
        assert (planning_dir / "active").exists()
        assert (planning_dir / "completed").exists()


class TestPlanOrganizerMove:
    """Test moving plans to status directories."""
    
    def test_move_to_active(self, planning_dir_with_plan):
        """Should move proposed/approved plan to active/."""
        brain_path, plan_file = planning_dir_with_plan
        organizer = PlanOrganizer(brain_path)
        
        new_path = organizer.move_to_status_dir(plan_file, "in-progress")
        
        assert not plan_file.exists()
        assert new_path.exists()
        assert new_path.parent.name == "active"
        assert new_path.name == "test-plan.md"
    
    def test_move_to_completed(self, planning_dir_with_plan):
        """Should move completed plan to completed/."""
        brain_path, plan_file = planning_dir_with_plan
        organizer = PlanOrganizer(brain_path)
        
        new_path = organizer.move_to_status_dir(plan_file, "completed")
        
        assert not plan_file.exists()
        assert new_path.exists()
        assert new_path.parent.name == "completed"
    
    def test_move_preserves_filename(self, planning_dir_with_plan):
        """Should preserve original filename."""
        brain_path, plan_file = planning_dir_with_plan
        organizer = PlanOrganizer(brain_path)
        
        original_name = plan_file.name
        new_path = organizer.move_to_status_dir(plan_file, "in-progress")
        
        assert new_path.name == original_name
    
    def test_move_returns_new_path(self, planning_dir_with_plan):
        """Should return Path object of new location."""
        brain_path, plan_file = planning_dir_with_plan
        organizer = PlanOrganizer(brain_path)
        
        new_path = organizer.move_to_status_dir(plan_file, "completed")
        
        assert isinstance(new_path, Path)
        assert new_path.exists()


class TestPlanOrganizerCollisionHandling:
    """Test handling filename collisions."""
    
    def test_collision_adds_suffix(self, tmp_path):
        """Should add numeric suffix if filename exists."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        features_dir = planning_dir / "features"
        active_dir = features_dir / "active"
        active_dir.mkdir(parents=True)
        
        # Create existing file in active/
        existing = active_dir / "test-plan.md"
        existing.write_text("existing content")
        
        # Create plan to move with same name
        plan_file = planning_dir / "test-plan.md"
        plan_file.write_text("""---
plan_id: ORG-002
title: Test Plan
status: proposed
priority: medium
created_date: 2025-12-03
estimated_hours: 10
---
# New content
""")
        
        organizer = PlanOrganizer(brain_path)
        new_path = organizer.move_to_status_dir(plan_file, "in-progress")
        
        # Should create test-plan-1.md
        assert new_path.name == "test-plan-1.md"
        assert new_path.exists()
        assert existing.exists()  # Original unchanged
    
    def test_collision_increments_suffix(self, tmp_path):
        """Should increment suffix for multiple collisions."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        features_dir = planning_dir / "features"
        active_dir = features_dir / "active"
        active_dir.mkdir(parents=True)
        
        # Create existing files
        (active_dir / "test-plan.md").write_text("first")
        (active_dir / "test-plan-1.md").write_text("second")
        
        # Create plan to move
        plan_file = planning_dir / "test-plan.md"
        plan_file.write_text("""---
plan_id: ORG-003
title: Test Plan
status: proposed
priority: medium
created_date: 2025-12-03
estimated_hours: 10
---
# Third content
""")
        
        organizer = PlanOrganizer(brain_path)
        new_path = organizer.move_to_status_dir(plan_file, "in-progress")
        
        # Should create test-plan-2.md
        assert new_path.name == "test-plan-2.md"


class TestPlanOrganizerIntegration:
    """Test integration with PlanRegistry."""
    
    def test_organizer_updates_registry_path(self, tmp_path):
        """Should update registry with new file path after move."""
        from src.workflows.plan_registry import PlanRegistry
        
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        # Create plan
        plan_file = planning_dir / "integration-test.md"
        plan_file.write_text("""---
plan_id: INT-001
title: Integration Test
status: proposed
priority: medium
created_date: 2025-12-03
estimated_hours: 10
---
# Content
""")
        
        # Initialize registry and scan
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        # Move plan
        organizer = PlanOrganizer(brain_path)
        new_path = organizer.move_to_status_dir(plan_file, "in-progress")
        
        # Update registry
        organizer.update_registry_after_move("INT-001", new_path, registry)
        
        # Verify registry has new path
        plan = registry.get_plan("INT-001")
        assert "active" in plan["file_path"]
