"""Tests for ArchivedPhaseExecutorCleaner.

Authority: CORE-008 (TDD) | AC-VAC-ARCHIVED-001
Author: CORTEX Framework
Created: 2026-02-17
"""

import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cortex_intelligence.memory.tier1_learned.orchestrators.cleaners.archived_phase_executor import (
    ArchivedPhaseExecutorCleaner,
)
from cortex_intelligence.memory.tier1_learned.orchestrators.cleaners.base import Analysis, Report


class TestArchivedPhaseExecutorCleanerProperties:
    """Test cleaner properties."""
    
    def test_name_returns_expected_value(self):
        """Test name property."""
        config = {"repo_root": "/tmp"}
        cleaner = ArchivedPhaseExecutorCleaner(config)
        assert cleaner.name == "ArchivedPhaseExecutorCleaner"
    
    def test_version_returns_expected_value(self):
        """Test version property."""
        config = {"repo_root": "/tmp"}
        cleaner = ArchivedPhaseExecutorCleaner(config)
        assert cleaner.version == "1.0.0"
    
    def test_domain_returns_expected_value(self):
        """Test domain property."""
        config = {"repo_root": "/tmp"}
        cleaner = ArchivedPhaseExecutorCleaner(config)
        assert cleaner.domain == "archived_phase_executors"


class TestArchivedPhaseExecutorCleanerPatterns:
    """Test pattern matching for archived executors."""
    
    @pytest.fixture
    def cleaner(self):
        """Create cleaner instance."""
        return ArchivedPhaseExecutorCleaner({"repo_root": "/tmp"})
    
    @pytest.mark.parametrize("filename,expected", [
        ("execute_phase_49_complete.py", True),
        ("execute_phase_79_complete.py", True),
        ("execute_phase_100.py", True),
        ("phase-81-migration.py", True),
        ("phase_25_cleanup.py", True),
        ("__init__.py", False),
        ("README.md", False),
        ("some_utility.py", False),
        ("orchestrator.py", False),
    ])
    def test_is_archived_executor(self, cleaner, filename, expected):
        """Test archived executor pattern matching."""
        assert cleaner._is_archived_executor(filename) == expected


class TestArchivedPhaseExecutorCleanerAnalyze:
    """Test analyze method."""
    
    def test_analyze_empty_directory(self, tmp_path):
        """Test analysis of empty directory."""
        # Create archived directory structure
        archived_dir = tmp_path / "cortex" / "phase_executors" / "archived"
        archived_dir.mkdir(parents=True)
        
        config = {"repo_root": str(tmp_path)}
        cleaner = ArchivedPhaseExecutorCleaner(config)
        cleaner.ARCHIVED_DIRS = ["cortex/phase_executors/archived"]
        
        result = cleaner.analyze()
        
        assert isinstance(result, Analysis)
        assert result.cleaner_id == "ArchivedPhaseExecutorCleaner"
        assert result.files_scanned == 0
        assert result.issues_found == 0
    
    def test_analyze_skips_protected_files(self, tmp_path):
        """Test that protected files are skipped."""
        archived_dir = tmp_path / "cortex" / "phase_executors" / "archived"
        archived_dir.mkdir(parents=True)
        
        # Create protected file
        (archived_dir / "__init__.py").write_text("")
        
        config = {"repo_root": str(tmp_path)}
        cleaner = ArchivedPhaseExecutorCleaner(config)
        cleaner.ARCHIVED_DIRS = ["cortex/phase_executors/archived"]
        
        result = cleaner.analyze()
        
        assert result.issues_found == 0
        assert any("Protected" in log for log in result.logs)
    
    def test_analyze_skips_recent_files(self, tmp_path):
        """Test that recent files are skipped."""
        archived_dir = tmp_path / "cortex" / "phase_executors" / "archived"
        archived_dir.mkdir(parents=True)
        
        # Create recent file (today)
        recent_file = archived_dir / "execute_phase_99.py"
        recent_file.write_text("# Recent")
        
        config = {"repo_root": str(tmp_path), "min_age_days": 90}
        cleaner = ArchivedPhaseExecutorCleaner(config)
        cleaner.ARCHIVED_DIRS = ["cortex/phase_executors/archived"]
        
        result = cleaner.analyze()
        
        assert result.issues_found == 0
        assert any("Too recent" in log for log in result.logs)
    
    @patch.object(ArchivedPhaseExecutorCleaner, "_has_uncommitted_changes")
    def test_analyze_finds_old_executors(self, mock_uncommitted, tmp_path):
        """Test that old executors are found."""
        mock_uncommitted.return_value = False
        
        archived_dir = tmp_path / "cortex" / "phase_executors" / "archived"
        archived_dir.mkdir(parents=True)
        
        # Create old file
        old_file = archived_dir / "execute_phase_49_complete.py"
        old_file.write_text("# Old executor")
        
        # Set old modification time (100 days ago)
        old_time = datetime.now() - timedelta(days=100)
        os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))
        
        config = {"repo_root": str(tmp_path), "min_age_days": 90}
        cleaner = ArchivedPhaseExecutorCleaner(config)
        cleaner.ARCHIVED_DIRS = ["cortex/phase_executors/archived"]
        
        result = cleaner.analyze()
        
        assert result.issues_found == 1
        assert result.plan["issues"][0]["filename"] == "execute_phase_49_complete.py"
        assert result.plan["issues"][0]["action"] == "delete"
    
    @patch.object(ArchivedPhaseExecutorCleaner, "_has_uncommitted_changes")
    def test_analyze_skips_uncommitted_changes(self, mock_uncommitted, tmp_path):
        """Test that files with uncommitted changes are skipped."""
        mock_uncommitted.return_value = True  # Has uncommitted changes
        
        archived_dir = tmp_path / "cortex" / "phase_executors" / "archived"
        archived_dir.mkdir(parents=True)
        
        # Create old file
        old_file = archived_dir / "execute_phase_49_complete.py"
        old_file.write_text("# Old executor")
        
        # Set old modification time
        old_time = datetime.now() - timedelta(days=100)
        os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))
        
        config = {"repo_root": str(tmp_path), "min_age_days": 90}
        cleaner = ArchivedPhaseExecutorCleaner(config)
        cleaner.ARCHIVED_DIRS = ["cortex/phase_executors/archived"]
        
        result = cleaner.analyze()
        
        assert result.issues_found == 0
        assert any("Uncommitted" in log for log in result.logs)


class TestArchivedPhaseExecutorCleanerExecute:
    """Test execute method."""
    
    def test_execute_dry_run(self, tmp_path):
        """Test execute in dry run mode."""
        archived_dir = tmp_path / "cortex" / "phase_executors" / "archived"
        archived_dir.mkdir(parents=True)
        
        # Create file
        test_file = archived_dir / "execute_phase_49_complete.py"
        test_file.write_text("# Test")
        
        config = {"repo_root": str(tmp_path), "dry_run": True}
        cleaner = ArchivedPhaseExecutorCleaner(config)
        
        plan = {"issues": [{
            "path": str(test_file),
            "filename": "execute_phase_49_complete.py",
            "action": "delete",
        }]}
        
        result = cleaner.execute(plan)
        
        assert isinstance(result, Report)
        assert result.status == "SUCCESS"
        assert result.actions_taken == 1
        assert test_file.exists()  # File should still exist in dry run
        assert any("DRY RUN" in log for log in result.logs)
    
    def test_execute_deletes_files(self, tmp_path):
        """Test execute deletes files in live mode."""
        archived_dir = tmp_path / "cortex" / "phase_executors" / "archived"
        archived_dir.mkdir(parents=True)
        
        # Create file
        test_file = archived_dir / "execute_phase_49_complete.py"
        test_file.write_text("# Test")
        
        config = {"repo_root": str(tmp_path), "dry_run": False}
        cleaner = ArchivedPhaseExecutorCleaner(config)
        
        plan = {"issues": [{
            "path": str(test_file),
            "filename": "execute_phase_49_complete.py",
            "action": "delete",
        }]}
        
        result = cleaner.execute(plan)
        
        assert result.status == "SUCCESS"
        assert result.actions_taken == 1
        assert result.changes["deleted"] == 1
        assert not test_file.exists()  # File should be deleted
    
    def test_execute_handles_analysis_object(self, tmp_path):
        """Test execute handles Analysis object as plan."""
        archived_dir = tmp_path / "cortex" / "phase_executors" / "archived"
        archived_dir.mkdir(parents=True)
        
        # Create file
        test_file = archived_dir / "execute_phase_49_complete.py"
        test_file.write_text("# Test")
        
        config = {"repo_root": str(tmp_path), "dry_run": True}
        cleaner = ArchivedPhaseExecutorCleaner(config)
        
        # Create Analysis object
        analysis = Analysis(
            cleaner_id="ArchivedPhaseExecutorCleaner",
            timestamp=datetime.now().isoformat(),
            files_scanned=1,
            issues_found=1,
            plan={"issues": [{
                "path": str(test_file),
                "filename": "execute_phase_49_complete.py",
                "action": "delete",
            }]},
        )
        
        result = cleaner.execute(analysis)
        
        assert result.status == "SUCCESS"
        assert result.actions_taken == 1
    
    def test_execute_handles_errors(self, tmp_path):
        """Test execute handles deletion errors."""
        config = {"repo_root": str(tmp_path), "dry_run": False}
        cleaner = ArchivedPhaseExecutorCleaner(config)
        
        # Non-existent file
        plan = {"issues": [{
            "path": str(tmp_path / "nonexistent.py"),
            "filename": "nonexistent.py",
            "action": "delete",
        }]}
        
        result = cleaner.execute(plan)
        
        assert result.status == "FAILED"
        assert len(result.errors) == 1


class TestArchivedPhaseExecutorCleanerRollback:
    """Test rollback method."""
    
    def test_rollback_returns_failure(self):
        """Test rollback indicates not supported."""
        config = {"repo_root": "/tmp"}
        cleaner = ArchivedPhaseExecutorCleaner(config)
        
        report = Report(
            cleaner_id="ArchivedPhaseExecutorCleaner",
            timestamp=datetime.now().isoformat(),
            status="SUCCESS",
            actions_taken=1,
            changes={"deleted": 1},
        )
        
        result = cleaner.rollback(report)
        
        assert result.status == "FAILED"
        assert result.files_restored == 0
        assert any("git" in err.lower() for err in result.errors)
