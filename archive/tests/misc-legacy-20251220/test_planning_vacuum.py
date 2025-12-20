"""
Tests for PlanningVacuum - TDD RED Phase

Tests vacuum and cleanup operations for planning artifacts.

Author: GitHub Copilot
Created: 2025-12-14
"""

import pytest
from pathlib import Path

from src.workflows.planning_vacuum import (
    PlanningVacuum,
    CleanupReport,
    CleanupAction
)


@pytest.fixture
def vacuum(tmp_path):
    """Fixture for PlanningVacuum."""
    return PlanningVacuum(root_directory=tmp_path)


@pytest.fixture
def sample_structure_with_empties(tmp_path):
    """Create sample structure with empty directories."""
    # Create nested empty directories
    (tmp_path / "empty1").mkdir()
    (tmp_path / "empty2" / "nested_empty").mkdir(parents=True)
    
    # Create directory with file
    with_file = tmp_path / "with_file"
    with_file.mkdir()
    (with_file / "file.txt").write_text("content")
    
    # Create plan with broken reference
    plan = tmp_path / "plan.md"
    plan.write_text("See [sub-plan](./nonexistent/sub-plan.md)")
    
    return tmp_path


class TestVacuumInit:
    """Test vacuum initialization."""
    
    def test_vacuum_initialization(self, vacuum):
        """Test vacuum can be initialized."""
        assert vacuum is not None
        assert vacuum.root_directory.exists()
    
    def test_vacuum_validates_directory(self, tmp_path):
        """Test vacuum validates directory existence."""
        nonexistent = tmp_path / "nonexistent"
        
        with pytest.raises(ValueError):
            PlanningVacuum(root_directory=nonexistent)


class TestEmptyDirectoryRemoval:
    """Test removing empty directories."""
    
    def test_vacuum_removes_empty_directories(self, vacuum, sample_structure_with_empties):
        """Test removing empty directories."""
        vacuum.root_directory = sample_structure_with_empties
        
        removed = vacuum.vacuum_empty_directories()
        
        assert isinstance(removed, list)
        assert len(removed) >= 2  # empty1 and nested_empty
    
    def test_vacuum_preserves_directories_with_files(self, vacuum, sample_structure_with_empties):
        """Test preserving directories with files."""
        vacuum.root_directory = sample_structure_with_empties
        
        vacuum.vacuum_empty_directories()
        
        # Directory with file should still exist
        assert (sample_structure_with_empties / "with_file").exists()
        assert (sample_structure_with_empties / "with_file" / "file.txt").exists()
    
    def test_vacuum_recursive(self, vacuum, tmp_path):
        """Test recursive empty directory removal."""
        # Create deeply nested empty structure
        nested = tmp_path / "level1" / "level2" / "level3"
        nested.mkdir(parents=True)
        
        vacuum.root_directory = tmp_path
        removed = vacuum.vacuum_empty_directories()
        
        # Should remove all empty levels
        assert len(removed) >= 3


class TestBrokenReferenceFixing:
    """Test fixing broken references."""
    
    def test_find_broken_references(self, vacuum, tmp_path):
        """Test finding broken references in plan files."""
        # Create plan with broken reference
        plan = tmp_path / "plan.md"
        plan.write_text("""
# Plan
See [sub-plan](./nonexistent.md)
Also see [other](./also-missing.md)
""")
        
        vacuum.root_directory = tmp_path
        broken = vacuum.find_broken_references()
        
        assert isinstance(broken, list)
        assert len(broken) >= 2
    
    def test_fix_broken_references(self, vacuum, tmp_path):
        """Test fixing broken references."""
        # Create plan with fixable reference
        active_dir = tmp_path / "active"
        active_dir.mkdir()
        
        plan = active_dir / "plan.md"
        plan.write_text("See [sub](../sub-plan.md)")
        
        # Create actual file in new location
        new_location = tmp_path / "plans" / "PLAN-001" / "sub-plans"
        new_location.mkdir(parents=True)
        (new_location / "sub-plan.md").write_text("content")
        
        vacuum.root_directory = tmp_path
        fixed = vacuum.fix_broken_references("PLAN-001")
        
        assert isinstance(fixed, int)
    
    def test_update_cross_references(self, vacuum, tmp_path):
        """Test updating cross-references after migration."""
        # Old structure reference
        plan = tmp_path / "plan.md"
        plan.write_text("See [tracker](./PLAN-001-TRACKER.md)")
        
        vacuum.root_directory = tmp_path
        
        # Update to new structure
        updated = vacuum.update_cross_references(
            old_path="./PLAN-001-TRACKER.md",
            new_path="./PLAN-001/artifacts/tracker.md"
        )
        
        assert updated >= 0


class TestOrphanedFileArchiving:
    """Test archiving orphaned files."""
    
    def test_archive_orphaned_files(self, vacuum, tmp_path):
        """Test archiving files without parent plan."""
        # Create orphaned file
        orphan = tmp_path / "orphaned-sub-plan.md"
        orphan.write_text("parent_plan_id: nonexistent")
        
        vacuum.root_directory = tmp_path
        archived = vacuum.archive_orphaned_files([orphan])
        
        assert len(archived) >= 1
        # File should be moved to orphaned/ folder
        orphaned_dir = tmp_path / "orphaned"
        assert orphaned_dir.exists()
    
    def test_generate_orphan_manifest(self, vacuum, tmp_path):
        """Test generating manifest of orphaned files."""
        orphan1 = tmp_path / "orphan1.md"
        orphan1.write_text("content1")
        
        orphan2 = tmp_path / "orphan2.md"
        orphan2.write_text("content2")
        
        vacuum.root_directory = tmp_path
        vacuum.archive_orphaned_files([orphan1, orphan2])
        
        manifest_path = tmp_path / "orphaned" / "MANIFEST.md"
        assert manifest_path.exists()


class TestCleanupReporting:
    """Test cleanup reporting."""
    
    def test_generate_cleanup_report(self, vacuum, sample_structure_with_empties):
        """Test generating cleanup report."""
        vacuum.root_directory = sample_structure_with_empties
        
        # Perform cleanup operations
        vacuum.vacuum_empty_directories()
        
        # Generate report
        report = vacuum.generate_cleanup_report()
        
        assert isinstance(report, CleanupReport)
        assert hasattr(report, 'directories_removed')
        assert hasattr(report, 'orphans_archived')
    
    def test_report_includes_statistics(self, vacuum, sample_structure_with_empties):
        """Test report includes statistics."""
        vacuum.root_directory = sample_structure_with_empties
        
        vacuum.vacuum_empty_directories()
        report = vacuum.generate_cleanup_report()
        
        assert isinstance(report.directories_removed, int)
    
    def test_report_format(self, vacuum):
        """Test report can be formatted as string."""
        report = CleanupReport(
            directories_removed=5,
            orphans_archived=3,
            references_fixed=10
        )
        
        report_str = str(report)
        
        assert isinstance(report_str, str)
        assert "5" in report_str
        assert "3" in report_str


class TestCleanupActions:
    """Test cleanup action tracking."""
    
    def test_track_cleanup_actions(self, vacuum):
        """Test tracking individual cleanup actions."""
        vacuum.track_action(CleanupAction.REMOVE_EMPTY_DIR, "/path/to/dir")
        vacuum.track_action(CleanupAction.ARCHIVE_ORPHAN, "/path/to/file")
        
        actions = vacuum.get_actions()
        
        assert isinstance(actions, list)
        assert len(actions) >= 2
    
    def test_action_history(self, vacuum, tmp_path):
        """Test action history is maintained."""
        vacuum.root_directory = tmp_path
        
        # Perform operations
        (tmp_path / "empty").mkdir()
        vacuum.vacuum_empty_directories()
        
        history = vacuum.get_action_history()
        
        assert isinstance(history, list)


class TestFullCleanup:
    """Test full cleanup workflow."""
    
    def test_full_cleanup_workflow(self, vacuum, sample_structure_with_empties):
        """Test complete cleanup workflow."""
        vacuum.root_directory = sample_structure_with_empties
        
        # Run full cleanup
        report = vacuum.run_full_cleanup()
        
        assert isinstance(report, CleanupReport)
        assert report.directories_removed >= 0
    
    def test_cleanup_with_dry_run(self, vacuum, sample_structure_with_empties):
        """Test cleanup in dry-run mode."""
        vacuum.root_directory = sample_structure_with_empties
        
        # Dry run should not modify files
        report = vacuum.run_full_cleanup(dry_run=True)
        
        assert isinstance(report, CleanupReport)
        # Empty directories should still exist in dry-run
        assert (sample_structure_with_empties / "empty1").exists()


class TestEdgeCases:
    """Test edge cases."""
    
    def test_empty_root_directory(self, vacuum):
        """Test vacuum handles empty root directory."""
        removed = vacuum.vacuum_empty_directories()
        
        assert isinstance(removed, list)
        assert len(removed) == 0
    
    def test_no_orphaned_files(self, vacuum, tmp_path):
        """Test vacuum handles no orphaned files."""
        # Create only valid files
        plan = tmp_path / "PLAN-001.yaml"
        plan.write_text("plan_id: PLAN-001")
        
        vacuum.root_directory = tmp_path
        orphans = vacuum.find_orphaned_files()
        
        assert isinstance(orphans, list)
        assert len(orphans) == 0
    
    def test_protected_directories(self, vacuum, tmp_path):
        """Test vacuum does not remove protected directories."""
        # Create .git directory (should be protected)
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        vacuum.root_directory = tmp_path
        removed = vacuum.vacuum_empty_directories()
        
        # .git should not be removed
        assert git_dir.exists()


class TestIntegration:
    """Integration tests."""
    
    def test_full_vacuum_workflow(self, vacuum, sample_structure_with_empties):
        """Test complete vacuum workflow."""
        vacuum.root_directory = sample_structure_with_empties
        
        # 1. Find issues
        empty_dirs = vacuum.find_empty_directories()
        broken_refs = vacuum.find_broken_references()
        
        # 2. Fix issues
        vacuum.vacuum_empty_directories()
        
        # 3. Generate report
        report = vacuum.generate_cleanup_report()
        
        assert isinstance(report, CleanupReport)
        assert report.directories_removed >= len(empty_dirs)
    
    def test_integration_with_duplicate_detector(self, vacuum, tmp_path):
        """Test vacuum works with duplicate detector."""
        from src.workflows.duplicate_detector import DuplicateDetector
        
        # Create duplicates
        file1 = tmp_path / "file1.yaml"
        file1.write_text("content")
        
        file2 = tmp_path / "file2.yaml"
        file2.write_text("content")
        
        # Detect and archive duplicates
        detector = DuplicateDetector(root_directory=tmp_path)
        duplicates = detector.find_duplicates()
        
        if duplicates:
            detector.archive_duplicates(duplicates[0])
        
        # Vacuum should not remove duplicates/ folder
        vacuum.root_directory = tmp_path
        vacuum.vacuum_empty_directories()
        
        assert (tmp_path / "duplicates").exists()
