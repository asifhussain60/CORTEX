"""Tests for BuildArtifactCleaner.

Authority: CORE-008 (TDD) | AC-VAC-BUILD-001
Author: CORTEX Framework
Created: 2026-02-17
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cortex_intelligence.memory.tier1_learned.orchestrators.cleaners.build_artifact import (
    BuildArtifactCleaner,
)
from cortex_intelligence.memory.tier1_learned.orchestrators.cleaners.base import Analysis, Report


class TestBuildArtifactCleanerProperties:
    """Test cleaner properties."""
    
    def test_name_returns_expected_value(self):
        """Test name property."""
        config = {"repo_root": "/tmp"}
        cleaner = BuildArtifactCleaner(config)
        assert cleaner.name == "BuildArtifactCleaner"
    
    def test_version_returns_expected_value(self):
        """Test version property."""
        config = {"repo_root": "/tmp"}
        cleaner = BuildArtifactCleaner(config)
        assert cleaner.version == "1.0.0"
    
    def test_domain_returns_expected_value(self):
        """Test domain property."""
        config = {"repo_root": "/tmp"}
        cleaner = BuildArtifactCleaner(config)
        assert cleaner.domain == "build_artifacts"


class TestBuildArtifactCleanerPatterns:
    """Test pattern matching for build directories."""
    
    @pytest.fixture
    def cleaner(self):
        """Create cleaner instance."""
        return BuildArtifactCleaner({"repo_root": "/tmp"})
    
    @pytest.mark.parametrize("dirname,expected", [
        ("obj", True),
        ("bin", True),
        ("build", True),
        ("dist", True),
        ("__pycache__", True),
        (".pytest_cache", True),
        (".mypy_cache", True),
        ("node_modules", True),
        ("mypackage.egg-info", True),
        ("src", False),
        ("tests", False),
        ("cortex", False),
    ])
    def test_is_build_directory(self, cleaner, dirname, expected):
        """Test build directory pattern matching."""
        assert cleaner._is_build_directory(dirname) == expected
    
    @pytest.mark.parametrize("path_parts,expected", [
        (["tmp", ".git", "objects"], True),
        (["tmp", ".venv", "lib"], True),
        (["tmp", ".github", "workflows"], True),
        (["tmp", "cortex", "src"], False),
        (["tmp", "tests", "unit"], False),
    ])
    def test_is_protected_path(self, cleaner, path_parts, expected):
        """Test protected path detection."""
        path = Path(*path_parts)
        assert cleaner._is_protected_path(path) == expected


class TestBuildArtifactCleanerAnalyze:
    """Test analyze method."""
    
    def test_analyze_empty_directory(self, tmp_path):
        """Test analysis of empty directory."""
        # Create target directory
        target_dir = tmp_path / "cortex"
        target_dir.mkdir()
        
        config = {"repo_root": str(tmp_path)}
        cleaner = BuildArtifactCleaner(config)
        cleaner.TARGET_DIRS = ["cortex"]
        
        result = cleaner.analyze()
        
        assert isinstance(result, Analysis)
        assert result.cleaner_id == "BuildArtifactCleaner"
        assert result.issues_found == 0
    
    def test_analyze_finds_pycache(self, tmp_path):
        """Test analysis finds __pycache__ directories."""
        target_dir = tmp_path / "cortex"
        target_dir.mkdir()
        
        # Create __pycache__ with files
        pycache = target_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "module.cpython-39.pyc").write_bytes(b"compiled")
        
        config = {"repo_root": str(tmp_path)}
        cleaner = BuildArtifactCleaner(config)
        cleaner.TARGET_DIRS = ["cortex"]
        
        result = cleaner.analyze()
        
        assert result.issues_found == 1
        assert result.plan["issues"][0]["name"] == "__pycache__"
        assert result.plan["issues"][0]["action"] == "delete"
    
    def test_analyze_finds_obj_directory(self, tmp_path):
        """Test analysis finds obj directories."""
        target_dir = tmp_path / "cortex_lens" / "dotnet" / "roslyn_cli"
        target_dir.mkdir(parents=True)
        
        # Create obj with build artifacts
        obj_dir = target_dir / "obj"
        obj_dir.mkdir()
        (obj_dir / "Debug").mkdir()
        (obj_dir / "Debug" / "project.assets.json").write_text("{}")
        
        config = {"repo_root": str(tmp_path)}
        cleaner = BuildArtifactCleaner(config)
        cleaner.TARGET_DIRS = ["cortex_lens"]
        
        result = cleaner.analyze()
        
        assert result.issues_found == 1
        assert result.plan["issues"][0]["name"] == "obj"
    
    def test_analyze_finds_bin_directory(self, tmp_path):
        """Test analysis finds bin directories."""
        target_dir = tmp_path / "cortex_lens" / "dotnet" / "roslyn_cli"
        target_dir.mkdir(parents=True)
        
        # Create bin with output
        bin_dir = target_dir / "bin"
        bin_dir.mkdir()
        (bin_dir / "Debug").mkdir()
        (bin_dir / "Debug" / "app.dll").write_bytes(b"binary")
        
        config = {"repo_root": str(tmp_path)}
        cleaner = BuildArtifactCleaner(config)
        cleaner.TARGET_DIRS = ["cortex_lens"]
        
        result = cleaner.analyze()
        
        assert result.issues_found == 1
        assert result.plan["issues"][0]["name"] == "bin"
    
    def test_analyze_skips_protected_directories(self, tmp_path):
        """Test analysis skips .git and .venv."""
        target_dir = tmp_path / "cortex"
        target_dir.mkdir()
        
        # Create protected directories
        git_dir = target_dir / ".git" / "objects"
        git_dir.mkdir(parents=True)
        
        config = {"repo_root": str(tmp_path)}
        cleaner = BuildArtifactCleaner(config)
        cleaner.TARGET_DIRS = ["cortex"]
        
        result = cleaner.analyze()
        
        assert result.issues_found == 0
    
    def test_analyze_calculates_total_size(self, tmp_path):
        """Test analysis calculates total reclaimable size."""
        target_dir = tmp_path / "cortex"
        target_dir.mkdir()
        
        # Create __pycache__ with files
        pycache = target_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "module.pyc").write_bytes(b"x" * 1000)
        
        config = {"repo_root": str(tmp_path)}
        cleaner = BuildArtifactCleaner(config)
        cleaner.TARGET_DIRS = ["cortex"]
        
        result = cleaner.analyze()
        
        assert result.plan["total_size"] >= 1000


class TestBuildArtifactCleanerExecute:
    """Test execute method."""
    
    def test_execute_dry_run(self, tmp_path):
        """Test execute in dry run mode."""
        target_dir = tmp_path / "cortex"
        target_dir.mkdir()
        
        # Create __pycache__
        pycache = target_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "module.pyc").write_bytes(b"compiled")
        
        config = {"repo_root": str(tmp_path), "dry_run": True}
        cleaner = BuildArtifactCleaner(config)
        
        plan = {"issues": [{
            "path": str(pycache),
            "type": "directory",
            "name": "__pycache__",
            "size": 100,
            "action": "delete",
        }]}
        
        result = cleaner.execute(plan)
        
        assert isinstance(result, Report)
        assert result.status == "SUCCESS"
        assert result.actions_taken == 1
        assert pycache.exists()  # Directory should still exist in dry run
        assert any("DRY RUN" in log for log in result.logs)
    
    def test_execute_deletes_directories(self, tmp_path):
        """Test execute deletes directories in live mode."""
        target_dir = tmp_path / "cortex"
        target_dir.mkdir()
        
        # Create __pycache__
        pycache = target_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "module.pyc").write_bytes(b"compiled")
        
        config = {"repo_root": str(tmp_path), "dry_run": False}
        cleaner = BuildArtifactCleaner(config)
        
        plan = {"issues": [{
            "path": str(pycache),
            "type": "directory",
            "name": "__pycache__",
            "size": 100,
            "action": "delete",
        }]}
        
        result = cleaner.execute(plan)
        
        assert result.status == "SUCCESS"
        assert result.actions_taken == 1
        assert not pycache.exists()  # Directory should be deleted
    
    def test_execute_handles_analysis_object(self, tmp_path):
        """Test execute handles Analysis object as plan."""
        target_dir = tmp_path / "cortex"
        target_dir.mkdir()
        
        # Create __pycache__
        pycache = target_dir / "__pycache__"
        pycache.mkdir()
        
        config = {"repo_root": str(tmp_path), "dry_run": True}
        cleaner = BuildArtifactCleaner(config)
        
        # Create Analysis object
        analysis = Analysis(
            cleaner_id="BuildArtifactCleaner",
            timestamp=datetime.now().isoformat(),
            files_scanned=10,
            issues_found=1,
            plan={"issues": [{
                "path": str(pycache),
                "type": "directory",
                "name": "__pycache__",
                "size": 100,
                "action": "delete",
            }]},
        )
        
        result = cleaner.execute(analysis)
        
        assert result.status == "SUCCESS"
        assert result.actions_taken == 1
    
    def test_execute_handles_errors(self, tmp_path):
        """Test execute handles deletion errors gracefully."""
        config = {"repo_root": str(tmp_path), "dry_run": False}
        cleaner = BuildArtifactCleaner(config)
        
        # Non-existent directory - should result in error
        plan = {"issues": [{
            "path": str(tmp_path / "nonexistent"),
            "type": "directory",
            "name": "nonexistent",
            "size": 0,
            "action": "delete",
        }]}
        
        result = cleaner.execute(plan)
        
        # Should fail since directory doesn't exist
        assert result.status == "FAILED"
        assert result.actions_taken == 0
        assert len(result.errors) == 1
    
    def test_execute_tracks_bytes_freed(self, tmp_path):
        """Test execute tracks bytes freed."""
        target_dir = tmp_path / "cortex"
        target_dir.mkdir()
        
        # Create __pycache__
        pycache = target_dir / "__pycache__"
        pycache.mkdir()
        
        config = {"repo_root": str(tmp_path), "dry_run": False}
        cleaner = BuildArtifactCleaner(config)
        
        plan = {"issues": [{
            "path": str(pycache),
            "type": "directory",
            "name": "__pycache__",
            "size": 5000,
            "action": "delete",
        }]}
        
        result = cleaner.execute(plan)
        
        assert result.changes["bytes_freed"] == 5000


class TestBuildArtifactCleanerRollback:
    """Test rollback method."""
    
    def test_rollback_returns_success_with_instructions(self):
        """Test rollback indicates regeneration instructions."""
        config = {"repo_root": "/tmp"}
        cleaner = BuildArtifactCleaner(config)
        
        report = Report(
            cleaner_id="BuildArtifactCleaner",
            timestamp=datetime.now().isoformat(),
            status="SUCCESS",
            actions_taken=1,
            changes={"deleted": 1},
        )
        
        result = cleaner.rollback(report)
        
        assert result.status == "SUCCESS"
        assert result.files_restored == 0
        assert any("regenerate" in err.lower() for err in result.errors)


class TestBuildArtifactCleanerSizeFormatting:
    """Test size formatting utilities."""
    
    @pytest.fixture
    def cleaner(self):
        """Create cleaner instance."""
        return BuildArtifactCleaner({"repo_root": "/tmp"})
    
    @pytest.mark.parametrize("size_bytes,expected_unit", [
        (500, "B"),
        (2048, "KB"),
        (5 * 1024 * 1024, "MB"),
        (3 * 1024 * 1024 * 1024, "GB"),
    ])
    def test_format_size(self, cleaner, size_bytes, expected_unit):
        """Test size formatting."""
        result = cleaner._format_size(size_bytes)
        assert expected_unit in result
