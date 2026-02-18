"""Unit tests for RootDatabaseCleaner.

Tests cleanup of orphaned *.db files from repository root.

Test Coverage:
- Analysis phase (scan for .db files)
- Execution phase (delete .db files)
- Rollback phase (restore from snapshot)
- Error handling
- Dry run mode

Governance:
- CORE-008: TDD (tests written first)
- CORE-011: Type hints 100%
- CORE-012: Google-style docstrings
- CORE-027: Audit markers

Author: CORTEX Architect
Phase: VACUUM-REFACTOR-001
"""

import pytest
from pathlib import Path
from typing import Dict, Any
import tempfile
import shutil

from cortex_intelligence.memory.tier1_learned.orchestrators.cleaners.root_database import RootDatabaseCleaner
from cortex_intelligence.memory.tier1_learned.orchestrators.cleaners import Analysis, Report, RollbackResult


@pytest.fixture
def temp_repo():
    """Create temporary repository for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def cleaner_config(temp_repo):
    """Configuration for RootDatabaseCleaner."""
    return {
        "repo_root": temp_repo,
        "dry_run": False,
        "backup_dir": temp_repo / ".vacuum_snapshots"
    }


@pytest.fixture
def cleaner(cleaner_config):
    """Initialize RootDatabaseCleaner for testing."""
    return RootDatabaseCleaner(cleaner_config)


# =============================================================================
# ANALYSIS PHASE TESTS
# =============================================================================

class TestRootDatabaseCleanerAnalysis:
    """Test analyze() phase - non-destructive scanning."""

    def test_analyze_finds_db_files_in_root(self, cleaner, temp_repo) -> None:
        """Test that analyze() detects .db files in root directory."""
        # AC_START: AC-VACUUM-REFACTOR-001
        # Create test .db files
        (temp_repo / "intelligence_audit.db").write_text("test data")
        (temp_repo / "observability_audit.db").write_text("test data")
        
        # Analyze
        analysis: Analysis = cleaner.analyze()
        
        # Verify
        assert analysis.cleaner_id == "root_database"
        assert analysis.issues_found == 2
        assert len(analysis.plan["files_to_delete"]) == 2
        assert analysis.files_scanned >= 2
        # AC_COMPLETE: AC-VACUUM-REFACTOR-001 ✅

    def test_analyze_ignores_subdirectory_db_files(self, cleaner, temp_repo) -> None:
        """Test that analyze() ignores .db files in subdirectories."""
        # Create .db in subdirectory (should be ignored)
        subdir = temp_repo / "cortex_intelligence"
        subdir.mkdir()
        (subdir / "governance.db").write_text("test data")
        
        # Create .db in root (should be found)
        (temp_repo / "root_file.db").write_text("test data")
        
        # Analyze
        analysis: Analysis = cleaner.analyze()
        
        # Verify only root file found
        assert analysis.issues_found == 1
        assert "root_file.db" in str(analysis.plan["files_to_delete"][0])

    def test_analyze_with_no_db_files(self, cleaner, temp_repo) -> None:
        """Test analyze() when no .db files exist in root."""
        # Analyze empty repo
        analysis: Analysis = cleaner.analyze()
        
        # Verify clean result
        assert analysis.issues_found == 0
        assert len(analysis.plan["files_to_delete"]) == 0

    def test_analyze_logs_findings(self, cleaner, temp_repo) -> None:
        """Test that analyze() generates detailed logs."""
        (temp_repo / "test.db").write_text("test")
        
        analysis: Analysis = cleaner.analyze()
        
        assert len(analysis.logs) > 0
        assert any("test.db" in log for log in analysis.logs)


# =============================================================================
# EXECUTION PHASE TESTS
# =============================================================================

class TestRootDatabaseCleanerExecution:
    """Test execute() phase - actual file deletion."""

    def test_execute_deletes_db_files(self, cleaner, temp_repo) -> None:
        """Test that execute() deletes .db files from plan."""
        # Create test files
        db_file = temp_repo / "test.db"
        db_file.write_text("test data")
        
        # Analyze
        analysis = cleaner.analyze()
        
        # Execute
        report: Report = cleaner.execute(analysis.plan)
        
        # Verify deletion
        assert not db_file.exists()
        assert report.status == "SUCCESS"
        assert report.actions_taken == 1

    def test_execute_creates_snapshot(self, cleaner, temp_repo) -> None:
        """Test that execute() creates backup snapshot before deletion."""
        db_file = temp_repo / "test.db"
        db_file.write_text("important data")
        
        analysis = cleaner.analyze()
        report = cleaner.execute(analysis.plan)
        
        # Verify snapshot exists
        snapshot_dir = temp_repo / ".vacuum_snapshots" / "root_database"
        assert snapshot_dir.exists()
        assert (snapshot_dir / "test.db").exists()

    def test_execute_dry_run_mode(self, cleaner_config, temp_repo) -> None:
        """Test that execute() in dry run mode doesn't delete files."""
        cleaner_config["dry_run"] = True
        cleaner = RootDatabaseCleaner(cleaner_config)
        
        db_file = temp_repo / "test.db"
        db_file.write_text("test")
        
        analysis = cleaner.analyze()
        report = cleaner.execute(analysis.plan)
        
        # Verify file still exists
        assert db_file.exists()
        assert report.status == "DRY_RUN"
        assert report.actions_taken == 0

    def test_execute_handles_missing_file_gracefully(self, cleaner, temp_repo) -> None:
        """Test that execute() handles files deleted between analyze and execute."""
        # Create plan manually with non-existent file
        plan = {"files_to_delete": [str(temp_repo / "nonexistent.db")]}
        
        report = cleaner.execute(plan)
        
        # Should not fail, just log warning
        assert report.status in ["SUCCESS", "PARTIAL"]
        assert len(report.errors) == 0 or "nonexistent" in report.errors[0]


# =============================================================================
# ROLLBACK PHASE TESTS
# =============================================================================

class TestRootDatabaseCleanerRollback:
    """Test rollback() phase - restore from snapshot."""

    def test_rollback_restores_deleted_files(self, cleaner, temp_repo) -> None:
        """Test that rollback() restores files from snapshot."""
        # Create and delete file
        db_file = temp_repo / "test.db"
        original_content = "important data"
        db_file.write_text(original_content)
        
        analysis = cleaner.analyze()
        cleaner.execute(analysis.plan)
        
        # File should be deleted
        assert not db_file.exists()
        
        # Rollback
        result: RollbackResult = cleaner.rollback()
        
        # Verify restoration
        assert db_file.exists()
        assert db_file.read_text() == original_content
        assert result.status == "SUCCESS"
        assert result.files_restored == 1

    def test_rollback_without_snapshot_fails_gracefully(self, cleaner, temp_repo) -> None:
        """Test rollback() when no snapshot exists."""
        result = cleaner.rollback()
        
        # Should not crash, but report no files restored
        assert result.status in ["SUCCESS", "FAILED"]
        assert result.files_restored == 0


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestRootDatabaseCleanerIntegration:
    """Test complete analyze -> execute -> rollback workflow."""

    def test_full_cleanup_workflow(self, cleaner, temp_repo) -> None:
        """Test complete workflow: analyze -> execute -> verify."""
        # Setup: Create multiple .db files
        files = ["intelligence_audit.db", "observability_audit.db", "solid_audit.db"]
        for filename in files:
            (temp_repo / filename).write_text(f"data for {filename}")
        
        # Phase 1: Analyze
        analysis = cleaner.analyze()
        assert analysis.issues_found == 3
        
        # Phase 2: Execute
        report = cleaner.execute(analysis.plan)
        assert report.status == "SUCCESS"
        assert report.actions_taken == 3
        
        # Phase 3: Verify cleanup
        for filename in files:
            assert not (temp_repo / filename).exists()

    def test_full_workflow_with_rollback(self, cleaner, temp_repo) -> None:
        """Test full workflow including rollback recovery."""
        # Create file
        db_file = temp_repo / "test.db"
        db_file.write_text("data")
        
        # Analyze and execute
        analysis = cleaner.analyze()
        report = cleaner.execute(analysis.plan)
        assert not db_file.exists()
        
        # Rollback
        rollback_result = cleaner.rollback()
        assert db_file.exists()
        assert rollback_result.is_success
