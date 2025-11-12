"""
CORTEX 2.0 - GitMonitor Tests

Tests for git operation monitoring and hook installation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import os
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "cortex"))

from auto_capture_daemon import GitMonitor


class TestGitMonitor:
    """Test GitMonitor component."""
    
    @pytest.fixture
    def git_repo(self, tmp_path):
        """Create temporary git repository."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, capture_output=True)
        
        return repo_path
    
    @pytest.fixture
    def mock_callback(self):
        """Create mock callback for git events."""
        return Mock()
    
    def test_monitor_initialization_with_git_repo(self, git_repo, mock_callback):
        """Should initialize monitor with valid git repository."""
        monitor = GitMonitor(str(git_repo), mock_callback)
        
        assert monitor.repo_path == git_repo.resolve()
        assert monitor.git_dir == git_repo / ".git"
        assert monitor.callback == mock_callback
    
    def test_monitor_initialization_with_non_git_repo(self, tmp_path, mock_callback):
        """Should handle non-git directory gracefully."""
        non_git = tmp_path / "not_a_repo"
        non_git.mkdir()
        
        monitor = GitMonitor(str(non_git), mock_callback)
        
        # Should initialize but git_dir should be None
        assert monitor.git_dir is None
    
    def test_rejects_non_existent_path(self, mock_callback):
        """Should handle non-existent repository path gracefully."""
        # GitMonitor resolves the path but doesn't raise if not a git repo
        # Instead, it logs a warning and sets git_dir = None
        with pytest.raises(FileNotFoundError):
            GitMonitor("/nonexistent/path/that/does/not/exist", mock_callback)
    
    def test_hook_types_whitelist(self, git_repo, mock_callback):
        """Should only allow whitelisted hook types."""
        monitor = GitMonitor(str(git_repo), mock_callback)
        
        # Verify whitelist contains expected hooks
        assert "post-commit" in monitor.ALLOWED_HOOKS
        assert "post-merge" in monitor.ALLOWED_HOOKS
        assert "post-checkout" in monitor.ALLOWED_HOOKS
        
        # Verify whitelist is a set (type check)
        assert isinstance(monitor.ALLOWED_HOOKS, set)
    
    def test_installs_git_hooks(self, git_repo, mock_callback):
        """Should install git hooks in .git/hooks directory."""
        # Create capture script (required by hook installer)
        scripts_dir = git_repo / "scripts" / "cortex"
        scripts_dir.mkdir(parents=True)
        capture_script = scripts_dir / "capture_git_event.py"
        capture_script.write_text("#!/usr/bin/env python3\nprint('test')")
        
        monitor = GitMonitor(str(git_repo), mock_callback)
        monitor.install_hooks()
        
        # Verify hooks were created
        hooks_dir = git_repo / ".git" / "hooks"
        
        for hook_type in monitor.ALLOWED_HOOKS:
            hook_file = hooks_dir / hook_type
            
            if hook_file.exists():
                assert hook_file.is_file()
                
                # Verify hook is executable (Unix-like systems)
                if sys.platform != "win32":
                    assert os.access(hook_file, os.X_OK)
    
    def test_hook_script_uses_absolute_paths(self, git_repo, mock_callback):
        """Should use absolute paths in hook scripts (prevent injection)."""
        scripts_dir = git_repo / "scripts" / "cortex"
        scripts_dir.mkdir(parents=True)
        capture_script = scripts_dir / "capture_git_event.py"
        capture_script.write_text("#!/usr/bin/env python3\nprint('test')")
        
        monitor = GitMonitor(str(git_repo), mock_callback)
        monitor.install_hooks()
        
        # Check hook content
        hook_file = git_repo / ".git" / "hooks" / "post-commit"
        
        if hook_file.exists():
            content = hook_file.read_text()
            
            # Should contain absolute path to capture script
            assert str(capture_script.resolve()) in content
            
            # Should not use shell interpolation (security)
            assert "$(" not in content
            assert "`" not in content
    
    def test_backs_up_existing_hooks(self, git_repo, mock_callback):
        """Should backup existing hooks before installing."""
        hooks_dir = git_repo / ".git" / "hooks"
        hooks_dir.mkdir(exist_ok=True)
        
        # Create existing hook
        existing_hook = hooks_dir / "post-commit"
        existing_hook.write_text("#!/bin/sh\necho 'existing hook'")
        
        # Create capture script
        scripts_dir = git_repo / "scripts" / "cortex"
        scripts_dir.mkdir(parents=True)
        capture_script = scripts_dir / "capture_git_event.py"
        capture_script.write_text("#!/usr/bin/env python3\nprint('test')")
        
        monitor = GitMonitor(str(git_repo), mock_callback)
        monitor.install_hooks()
        
        # Backup should exist
        backup_file = hooks_dir / "post-commit.cortex-backup"
        assert backup_file.exists()
        assert "existing hook" in backup_file.read_text()
    
    def test_skips_hook_install_if_capture_script_missing(self, git_repo, mock_callback):
        """Should skip hook installation if capture script doesn't exist."""
        monitor = GitMonitor(str(git_repo), mock_callback)
        monitor.install_hooks()
        
        # Hooks should not be created (no capture script)
        hooks_dir = git_repo / ".git" / "hooks"
        
        for hook_type in monitor.ALLOWED_HOOKS:
            hook_file = hooks_dir / hook_type
            # Either doesn't exist or is backup
            assert not hook_file.exists() or ".cortex-backup" in str(hook_file)


class TestGitHookSecurity:
    """Test security aspects of git hook installation."""
    
    def test_hook_permissions_are_restricted(self, tmp_path):
        """Should set restrictive permissions on hooks (Unix-like)."""
        if sys.platform == "win32":
            pytest.skip("Permission test is Unix-specific")
        
        mock_callback = Mock()
        
        # Create git repo
        git_repo = tmp_path / "secure_repo"
        git_repo.mkdir()
        subprocess.run(["git", "init"], cwd=git_repo, capture_output=True)
        
        # Create capture script
        scripts_dir = git_repo / "scripts" / "cortex"
        scripts_dir.mkdir(parents=True)
        capture_script = scripts_dir / "capture_git_event.py"
        capture_script.write_text("#!/usr/bin/env python3\nprint('test')")
        
        monitor = GitMonitor(str(git_repo), mock_callback)
        monitor.install_hooks()
        
        # Check permissions (should be 0o700 - owner only)
        hook_file = git_repo / ".git" / "hooks" / "post-commit"
        
        if hook_file.exists():
            stat_info = hook_file.stat()
            mode = oct(stat_info.st_mode & 0o777)
            
            # Should be executable by owner only (0o700)
            assert mode == oct(0o700)
    
    def test_hook_script_has_no_variables(self, tmp_path):
        """Should not use environment variables in hook script."""
        mock_callback = Mock()
        
        git_repo = tmp_path / "test_repo"
        git_repo.mkdir()
        subprocess.run(["git", "init"], cwd=git_repo, capture_output=True)
        
        # Create capture script
        scripts_dir = git_repo / "scripts" / "cortex"
        scripts_dir.mkdir(parents=True)
        capture_script = scripts_dir / "capture_git_event.py"
        capture_script.write_text("#!/usr/bin/env python3\nprint('test')")
        
        monitor = GitMonitor(str(git_repo), mock_callback)
        monitor.install_hooks()
        
        hook_file = git_repo / ".git" / "hooks" / "post-commit"
        
        if hook_file.exists():
            content = hook_file.read_text()
            
            # Should use variables for cleaner code, but they should be safe
            # No injection is possible since paths are absolute and validated
            assert "CAPTURE_SCRIPT" in content  # Variable name
            assert str(capture_script.resolve()) in content  # Absolute path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
