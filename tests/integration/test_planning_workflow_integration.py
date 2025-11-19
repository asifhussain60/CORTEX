"""
Integration Tests: Planning Workflow with Two-Way Sync

Tests the complete planning workflow integration:
- InteractivePlannerAgent creates plans
- PlanningFileManager manages lifecycle
- PlanSyncManager syncs to database
- Status changes sync bidirectionally

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain
License: Proprietary
Repository: https://github.com/asifhussain60/CORTEX
"""

import pytest
import tempfile
import time
import json
from pathlib import Path
from datetime import datetime

# Import components
from src.operations.modules.planning.plan_sync_manager import PlanSyncManager
from scripts.planning_file_manager import PlanningFileManager, FileStatus


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as temp_root:
        # Create planning structure
        planning_root = Path(temp_root) / "cortex-brain" / "documents" / "planning"
        planning_root.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (planning_root / "ado" / "active").mkdir(parents=True, exist_ok=True)
        (planning_root / "ado" / "approved").mkdir(parents=True, exist_ok=True)
        (planning_root / "ado" / "completed").mkdir(parents=True, exist_ok=True)
        (planning_root / "features" / "active").mkdir(parents=True, exist_ok=True)
        
        # Create database directory
        db_dir = Path(temp_root) / "cortex-brain" / "tier2"
        db_dir.mkdir(parents=True, exist_ok=True)
        db_path = db_dir / "planning-tracker.db"
        
        yield {
            "planning_root": planning_root,
            "db_path": str(db_path),
            "temp_root": Path(temp_root)
        }


@pytest.fixture
def sync_manager(temp_dirs):
    """Initialize PlanSyncManager with temporary paths."""
    manager = PlanSyncManager(
        db_path=temp_dirs["db_path"],
        planning_root=temp_dirs["planning_root"]
    )
    yield manager
    
    # Cleanup
    try:
        manager.stop_file_watcher()
        manager.conn.close()
    except:
        pass


@pytest.fixture
def file_manager(temp_dirs):
    """Initialize PlanningFileManager with temporary paths."""
    # Override plan_sync_manager to use temp database
    manager = PlanningFileManager(base_path=str(temp_dirs["planning_root"]))
    
    # Replace sync manager with temp one
    manager.plan_sync_manager = PlanSyncManager(
        db_path=temp_dirs["db_path"],
        planning_root=temp_dirs["planning_root"]
    )
    
    yield manager
    
    # Cleanup
    try:
        if manager.plan_sync_manager:
            manager.plan_sync_manager.stop_file_watcher()
            manager.plan_sync_manager.conn.close()
    except:
        pass


class TestPlanningWorkflowIntegration:
    """Integration tests for complete planning workflow."""
    
    def test_create_plan_syncs_to_database(self, file_manager, temp_dirs):
        """Test: Creating plan file automatically syncs to database."""
        # Create plan using file manager
        template_content = """# Test Feature Plan

**Status:** Active
**Created:** 2025-11-19
**ADO:** ADO-12345

## Description
Test feature implementation plan.

## Phases
### Phase 1: Foundation
- Task 1: Setup structure
- Task 2: Create scaffolding
"""
        
        success, file_path = file_manager.create_planning_file(
            ado_number="ADO-12345",
            title="Test Feature Implementation",
            template_content=template_content,
            status=FileStatus.ACTIVE
        )
        
        assert success, f"Failed to create plan: {file_path}"
        
        # Verify file exists
        assert Path(file_path).exists()
        
        # Give sync a moment to complete
        time.sleep(0.5)
        
        # Verify database record exists
        plan = file_manager.plan_sync_manager.resolve_plan_by_name("Test Feature")
        assert plan is not None, "Plan not found in database"
        assert plan["title"] == "Test Feature Plan"
        assert plan["status"] == "active"
        assert plan["plan_type"] == "ado"
    
    def test_status_change_syncs_to_database(self, file_manager, temp_dirs):
        """Test: Changing plan status syncs to database."""
        # Create plan
        template_content = """# Approval Test Plan

**Status:** Active
**Created:** 2025-11-19

## Description
Test plan approval workflow.
"""
        
        success, file_path = file_manager.create_planning_file(
            ado_number="ADO-67890",
            title="Approval Test",
            template_content=template_content,
            status=FileStatus.ACTIVE
        )
        
        assert success
        time.sleep(0.5)
        
        # Verify initial status in database
        plan = file_manager.plan_sync_manager.resolve_plan_by_name("Approval Test")
        assert plan["status"] == "active"
        
        # Approve the plan
        success, message = file_manager.approve_plan("ADO-67890", "test_user")
        assert success, f"Failed to approve: {message}"
        time.sleep(0.5)  # Allow sync to complete
        
        # Verify status change synced to database
        plan = file_manager.plan_sync_manager.resolve_plan_by_name("Approval Test")
        assert plan["status"] == "approved", f"Status not synced: {plan['status']}"
    
    def test_database_to_file_sync(self, sync_manager, temp_dirs):
        """Test: Database status changes sync back to file."""
        # Create a plan file manually
        plan_file = temp_dirs["planning_root"] / "ado" / "active" / "PLAN-2025-11-19-test.md"
        plan_file.write_text("""# Test Database Sync

**Status:** Active
**Created:** 2025-11-19

## Description
Testing database to file sync.
""", encoding='utf-8')
        
        # Sync to database
        result = sync_manager.sync_file_to_database(plan_file)
        assert result["success"]
        plan_id = result["plan_id"]
        
        # Update status in database
        sync_manager._update_plan_status(plan_id, "completed")
        
        # Sync back to file
        result = sync_manager.sync_database_to_file(plan_id)
        assert result["success"]
        
        # Verify file was updated
        content = plan_file.read_text(encoding='utf-8')
        assert "**Status:** Completed" in content, "Status not updated in file"
    
    def test_complete_workflow_lifecycle(self, file_manager, temp_dirs):
        """Test: Complete workflow from creation to completion."""
        # Step 1: Create plan (Active)
        template_content = """# Feature Complete Test

**Status:** Active
**Created:** 2025-11-19
**ADO:** ADO-99999

## Description
Full lifecycle test.
"""
        
        success, file_path = file_manager.create_planning_file(
            ado_number="ADO-99999",
            title="Feature Complete",
            template_content=template_content,
            status=FileStatus.ACTIVE
        )
        assert success
        time.sleep(0.5)
        
        # Verify Active in database
        plan = file_manager.plan_sync_manager.resolve_plan_by_name("Feature Complete")
        assert plan["status"] == "active"
        
        # Step 2: Approve plan
        success, _ = file_manager.approve_plan("ADO-99999", "test_user")
        assert success
        time.sleep(0.5)
        
        # Verify Approved in database
        plan = file_manager.plan_sync_manager.resolve_plan_by_name("Feature Complete")
        assert plan["status"] == "approved"
        
        # Step 3: Complete plan
        success, _ = file_manager.complete_plan("ADO-99999")
        assert success
        time.sleep(0.5)
        
        # Verify Completed in database
        plan = file_manager.plan_sync_manager.resolve_plan_by_name("Feature Complete")
        assert plan["status"] == "completed"
    
    def test_sync_integrity_validation(self, file_manager, temp_dirs):
        """Test: Integrity validation detects inconsistencies."""
        # Create plan via file manager (synced)
        template_content = """# Integrity Test

**Status:** Active
**Created:** 2025-11-19

## Description
Testing integrity validation.
"""
        
        success, file_path = file_manager.create_planning_file(
            ado_number="ADO-11111",
            title="Integrity Test",
            template_content=template_content,
            status=FileStatus.ACTIVE
        )
        assert success
        time.sleep(0.5)
        
        # Create orphaned file (not synced)
        orphan_file = temp_dirs["planning_root"] / "ado" / "active" / "ORPHAN-2025-11-19-test.md"
        orphan_file.write_text("""# Orphaned Plan

**Status:** Active
**Created:** 2025-11-19

## Description
This file is not in database.
""", encoding='utf-8')
        
        # Run integrity validation
        result = file_manager.plan_sync_manager.validate_sync_integrity()
        
        # Check result structure (may be list or dict)
        if isinstance(result, dict):
            assert result.get("success", False) or "conflicts" in result
            orphaned_files = result.get("orphaned_files", [])
        else:
            # Result is a list of conflicts
            orphaned_files = [c for c in result if c.get("type") == "orphaned_file"]
        
        # Check for orphaned file detection
        assert len(orphaned_files) >= 1, "Should detect at least 1 orphaned file"
    
    def test_plan_resolution_with_sync(self, file_manager, temp_dirs):
        """Test: Plan resolution searches database first, then filesystem."""
        # Create plan in database only (simulate external creation)
        sync_manager = file_manager.plan_sync_manager
        plan_file = temp_dirs["planning_root"] / "features" / "active" / "PLAN-2025-11-19-search-test.md"
        plan_file.write_text("""# Search Test Plan

**Status:** Active
**Created:** 2025-11-19

## Description
Testing search functionality.
""", encoding='utf-8')
        
        # Sync to database
        result = sync_manager.sync_file_to_database(plan_file)
        assert result["success"]
        plan_id = result["plan_id"]
        
        # Test database search
        plan = sync_manager.resolve_plan_by_name("Search Test")
        assert plan is not None, "Plan not found via database search"
        assert plan["title"] == "Search Test Plan"
        
        # Delete from database to test filesystem fallback
        sync_manager._delete_plan_from_db(plan_id)
        
        # Test filesystem fallback
        plan = sync_manager.resolve_plan_by_name("Search Test")
        assert plan is not None, "Plan not found via filesystem fallback"
        assert plan["title"] == "Search Test Plan"


class TestFileWatcherIntegration:
    """Integration tests for file watcher with planning workflow."""
    
    def test_file_watcher_detects_manual_changes(self, sync_manager, temp_dirs):
        """Test: File watcher detects manual file modifications."""
        # Start file watcher
        sync_manager.start_file_watcher()
        
        # Create plan file manually
        plan_file = temp_dirs["planning_root"] / "ado" / "active" / "WATCH-2025-11-19-test.md"
        plan_file.write_text("""# Watch Test

**Status:** Active
**Created:** 2025-11-19

## Description
Original content.
""")
        
        # Wait for watcher to detect and process (debounce + processing)
        time.sleep(2.5)
        
        # Verify plan in database
        plan = sync_manager.resolve_plan_by_name("Watch Test")
        assert plan is not None, "Plan not synced by file watcher"
        
        # Modify file
        plan_file.write_text("""# Watch Test UPDATED

**Status:** Active
**Created:** 2025-11-19

## Description
Modified content.
""")
        
        # Wait for modification to sync
        time.sleep(2.5)
        
        # Verify database was updated
        plan = sync_manager.resolve_plan_by_name("Watch Test")
        assert "UPDATED" in plan["title"], "File modification not synced"
        
        # Cleanup
        sync_manager.stop_file_watcher()


class TestErrorHandling:
    """Integration tests for error scenarios."""
    
    def test_handles_missing_plan_file(self, file_manager):
        """Test: Gracefully handles missing plan file."""
        # Try to move nonexistent plan
        success, message = file_manager.move_to_status("ADO-MISSING", FileStatus.APPROVED)
        assert not success
        assert "not found" in message.lower()
    
    def test_handles_database_sync_failure(self, file_manager, temp_dirs):
        """Test: Continues operation even if sync fails."""
        # Break sync manager
        file_manager.plan_sync_manager = None
        
        # Create plan should still work
        template_content = """# No Sync Test

**Status:** Active
**Created:** 2025-11-19

## Description
Testing without sync.
"""
        
        success, file_path = file_manager.create_planning_file(
            ado_number="ADO-NOSYNC",
            title="No Sync Test",
            template_content=template_content,
            status=FileStatus.ACTIVE
        )
        
        # Should succeed even without sync
        assert success
        assert Path(file_path).exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
