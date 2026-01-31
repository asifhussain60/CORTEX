"""
TDD Tests for Output Manager - Dashboard Location Routing.

Tests output path determination and gitignore creation based on:
- Repository type (external vs CORTEX)
- Execution context (local vs remote)
- Configuration override

Authority: CORE-008 (TDD First)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-001
"""

from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest

from cortex.visualization.output_manager import (
    DashboardOutputManager,
    OutputConfiguration,
    get_output_path,
)


class TestOutputConfiguration:
    """Test OutputConfiguration dataclass."""
    
    def test_create_local_external_config(self):
        """Test creating config for local external repository."""
        config = OutputConfiguration(
            repo_path=Path("/path/to/repo"),
            is_cortex=False,
            is_remote=False,
            output_path=Path("/path/to/repo/.cortex/lens-dashboard"),
            gitignore_entry=".cortex/",
        )
        
        assert config.repo_path == Path("/path/to/repo")
        assert config.is_cortex is False
        assert config.is_remote is False
        assert config.output_path == Path("/path/to/repo/.cortex/lens-dashboard")
        assert config.gitignore_entry == ".cortex/"
    
    def test_create_local_cortex_config(self):
        """Test creating config for local CORTEX repository."""
        config = OutputConfiguration(
            repo_path=Path("/path/to/CORTEX"),
            is_cortex=True,
            is_remote=False,
            output_path=Path("/path/to/CORTEX/reports/lens-dashboard"),
            gitignore_entry=None,  # No gitignore needed
        )
        
        assert config.is_cortex is True
        assert config.output_path == Path("/path/to/CORTEX/reports/lens-dashboard")
        assert config.gitignore_entry is None
    
    def test_create_remote_config(self):
        """Test creating config for remote repository."""
        config = OutputConfiguration(
            repo_path=Path("/tmp/remote-repo"),
            is_cortex=False,
            is_remote=True,
            output_path=Path.home() / ".cortex/cache/remote-repo-hash/lens-dashboard",
            gitignore_entry=None,  # No gitignore for remote
        )
        
        assert config.is_remote is True
        assert str(config.output_path).startswith(str(Path.home()))
        assert ".cortex/cache" in str(config.output_path)


class TestDashboardOutputManager:
    """Test DashboardOutputManager output path routing."""
    
    def test_get_output_path_external_local(self, tmp_path):
        """Test output path for external repository (local)."""
        manager = DashboardOutputManager()
        
        # Mock repository detector to return False (external repo)
        with patch("cortex.visualization.output_manager.is_cortex_repository", return_value=False):
            config = manager.get_output_configuration(tmp_path)
        
        assert config.repo_path == tmp_path
        assert config.is_cortex is False
        assert config.is_remote is False
        assert config.output_path == tmp_path / ".cortex/lens-dashboard"
        assert config.gitignore_entry == ".cortex/"
    
    def test_get_output_path_cortex_local(self, tmp_path):
        """Test output path for CORTEX repository (local)."""
        manager = DashboardOutputManager()
        
        # Mock repository detector to return True (CORTEX repo)
        with patch("cortex.visualization.output_manager.is_cortex_repository", return_value=True):
            config = manager.get_output_configuration(tmp_path)
        
        assert config.repo_path == tmp_path
        assert config.is_cortex is True
        assert config.is_remote is False
        assert config.output_path == tmp_path / "reports/lens-dashboard"
        assert config.gitignore_entry is None  # No gitignore for CORTEX
    
    def test_get_output_path_remote(self, tmp_path):
        """Test output path for remote repository."""
        manager = DashboardOutputManager()
        
        # Mock repository detector and is_remote=True
        with patch("cortex.visualization.output_manager.is_cortex_repository", return_value=False):
            config = manager.get_output_configuration(tmp_path, is_remote=True)
        
        assert config.repo_path == tmp_path
        assert config.is_cortex is False
        assert config.is_remote is True
        
        # Output path should be in ~/.cortex/cache/
        assert str(config.output_path).startswith(str(Path.home()))
        assert ".cortex/cache" in str(config.output_path)
        assert "lens-dashboard" in str(config.output_path)
        assert config.gitignore_entry is None  # No gitignore for remote
    
    def test_get_output_path_with_override(self, tmp_path):
        """Test output path with explicit override."""
        manager = DashboardOutputManager()
        custom_path = tmp_path / "custom/dashboard"
        
        with patch("cortex.visualization.output_manager.is_cortex_repository", return_value=False):
            config = manager.get_output_configuration(tmp_path, output_override=custom_path)
        
        assert config.output_path == custom_path
        assert config.gitignore_entry == ".cortex/"  # Still suggest gitignore
    
    def test_ensure_output_directory_creates_path(self, tmp_path):
        """Test ensure_output_directory creates missing directories."""
        manager = DashboardOutputManager()
        output_path = tmp_path / "deep/nested/dashboard"
        
        assert not output_path.exists()
        manager.ensure_output_directory(output_path)
        assert output_path.exists()
        assert output_path.is_dir()
    
    def test_ensure_output_directory_idempotent(self, tmp_path):
        """Test ensure_output_directory is idempotent (safe to call multiple times)."""
        manager = DashboardOutputManager()
        output_path = tmp_path / "dashboard"
        
        # Call twice
        manager.ensure_output_directory(output_path)
        manager.ensure_output_directory(output_path)
        
        assert output_path.exists()
        assert output_path.is_dir()
    
    def test_create_gitignore_entry_for_external_repo(self, tmp_path):
        """Test .gitignore creation for external repository."""
        manager = DashboardOutputManager()
        gitignore_path = tmp_path / ".gitignore"
        
        # Create new .gitignore
        manager.create_gitignore_entry(tmp_path, ".cortex/")
        
        assert gitignore_path.exists()
        content = gitignore_path.read_text()
        assert ".cortex/" in content
        assert "# CORTEX LENS Dashboard" in content
    
    def test_create_gitignore_entry_appends_if_exists(self, tmp_path):
        """Test .gitignore entry appended to existing file."""
        manager = DashboardOutputManager()
        gitignore_path = tmp_path / ".gitignore"
        
        # Create existing .gitignore
        gitignore_path.write_text("node_modules/\n*.log\n")
        
        manager.create_gitignore_entry(tmp_path, ".cortex/")
        
        content = gitignore_path.read_text()
        assert "node_modules/" in content  # Original content preserved
        assert ".cortex/" in content  # New entry added
    
    def test_create_gitignore_entry_idempotent(self, tmp_path):
        """Test .gitignore entry not duplicated on multiple calls."""
        manager = DashboardOutputManager()
        gitignore_path = tmp_path / ".gitignore"
        
        # Call twice
        manager.create_gitignore_entry(tmp_path, ".cortex/")
        manager.create_gitignore_entry(tmp_path, ".cortex/")
        
        content = gitignore_path.read_text()
        # Should only appear once
        assert content.count(".cortex/") == 1
    
    def test_create_gitignore_entry_skips_if_none(self, tmp_path):
        """Test no .gitignore created if gitignore_entry is None."""
        manager = DashboardOutputManager()
        gitignore_path = tmp_path / ".gitignore"
        
        # Pass None (e.g., for CORTEX or remote repos)
        manager.create_gitignore_entry(tmp_path, None)
        
        assert not gitignore_path.exists()
    
    def test_generate_index_html(self, tmp_path):
        """Test index.html generation."""
        manager = DashboardOutputManager()
        output_path = tmp_path / "dashboard"
        output_path.mkdir()
        
        manager.generate_index_html(output_path, repo_name="test-repo")
        
        index_path = output_path / "index.html"
        assert index_path.exists()
        
        content = index_path.read_text()
        assert "CORTEX LENS Dashboard" in content
        assert "test-repo" in content
        assert "<!DOCTYPE html>" in content
    
    def test_convenience_function_get_output_path(self, tmp_path):
        """Test convenience function get_output_path()."""
        with patch("cortex.visualization.output_manager.is_cortex_repository", return_value=False):
            output_path = get_output_path(tmp_path)
        
        assert output_path == tmp_path / ".cortex/lens-dashboard"
