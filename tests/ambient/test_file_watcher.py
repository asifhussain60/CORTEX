"""
CORTEX 2.0 - FileSystemWatcher Tests

Tests for file system monitoring component.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add scripts/cortex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "cortex"))

from auto_capture_daemon import FileSystemWatcher, WATCH_PATTERNS, IGNORE_PATTERNS


class TestFileSystemWatcher:
    """Test FileSystemWatcher component."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            
            # Create directory structure
            (workspace / "src").mkdir()
            (workspace / ".git").mkdir()
            (workspace / "__pycache__").mkdir()
            
            yield workspace
    
    @pytest.fixture
    def mock_callback(self):
        """Create mock callback for event testing."""
        return Mock()
    
    def test_watcher_initialization(self, temp_workspace, mock_callback):
        """Should initialize watcher with valid workspace."""
        watcher = FileSystemWatcher(str(temp_workspace), mock_callback)
        
        assert watcher.workspace_path == temp_workspace.resolve()
        assert watcher.callback == mock_callback
        assert watcher.observer is not None
    
    def test_rejects_invalid_workspace(self, mock_callback):
        """Should reject non-existent workspace path."""
        with pytest.raises(FileNotFoundError):
            FileSystemWatcher("/nonexistent/path/that/does/not/exist", mock_callback)
    
    def test_rejects_file_as_workspace(self, temp_workspace, mock_callback):
        """Should reject file path (must be directory)."""
        test_file = temp_workspace / "test.txt"
        test_file.write_text("test")
        
        with pytest.raises(ValueError, match="must be a directory"):
            FileSystemWatcher(str(test_file), mock_callback)
    
    def test_detects_file_creation(self, temp_workspace, mock_callback):
        """Should detect new file creation."""
        watcher = FileSystemWatcher(str(temp_workspace), mock_callback)
        watcher.start()
        
        # Allow observer to start
        time.sleep(0.5)
        
        # Create new Python file
        new_file = temp_workspace / "src" / "new_module.py"
        new_file.write_text("# New module")
        
        # Allow time for event processing
        time.sleep(1)
        
        # Stop watcher
        watcher.observer.stop()
        watcher.observer.join(timeout=2)
        
        # Callback should have been triggered
        assert mock_callback.called
        
        # Verify event details
        call_args = mock_callback.call_args[0][0]
        assert call_args["type"] == "file_change"
        assert "new_module.py" in call_args["file"]
        assert call_args["event"] in ["created", "modified"]
    
    def test_detects_file_modification(self, temp_workspace, mock_callback):
        """Should detect file modification."""
        # Create file first
        test_file = temp_workspace / "src" / "existing.py"
        test_file.write_text("# Original content")
        
        watcher = FileSystemWatcher(str(temp_workspace), mock_callback)
        watcher.start()
        
        time.sleep(0.5)
        
        # Modify file
        test_file.write_text("# Modified content")
        
        time.sleep(1)
        
        watcher.observer.stop()
        watcher.observer.join(timeout=2)
        
        # Should detect modification
        assert mock_callback.called
        
        call_args = mock_callback.call_args[0][0]
        assert call_args["type"] == "file_change"
        assert "existing.py" in call_args["file"]
    
    def test_ignores_pycache_files(self, temp_workspace, mock_callback):
        """Should ignore __pycache__ directory files."""
        watcher = FileSystemWatcher(str(temp_workspace), mock_callback)
        watcher.start()
        
        time.sleep(0.5)
        
        # Create file in __pycache__
        pycache_file = temp_workspace / "__pycache__" / "module.pyc"
        pycache_file.write_text("compiled")
        
        time.sleep(1)
        
        watcher.observer.stop()
        watcher.observer.join(timeout=2)
        
        # Should not trigger callback for ignored files
        assert not mock_callback.called
    
    def test_ignores_git_directory(self, temp_workspace, mock_callback):
        """Should ignore .git directory files."""
        watcher = FileSystemWatcher(str(temp_workspace), mock_callback)
        watcher.start()
        
        time.sleep(0.5)
        
        # Create file in .git
        git_file = temp_workspace / ".git" / "config"
        git_file.write_text("git config")
        
        time.sleep(1)
        
        watcher.observer.stop()
        watcher.observer.join(timeout=2)
        
        # Should not trigger callback for git files
        assert not mock_callback.called
    
    def test_only_watches_allowed_extensions(self, temp_workspace, mock_callback):
        """Should only watch whitelisted file extensions."""
        watcher = FileSystemWatcher(str(temp_workspace), mock_callback)
        
        # Test allowed extensions
        assert watcher._is_allowed_extension(Path("test.py"))
        assert watcher._is_allowed_extension(Path("README.md"))
        assert watcher._is_allowed_extension(Path("config.json"))
        assert watcher._is_allowed_extension(Path("docker.yml"))
        assert watcher._is_allowed_extension(Path("component.tsx"))
        
        # Test disallowed extensions
        assert not watcher._is_allowed_extension(Path("binary.exe"))
        assert not watcher._is_allowed_extension(Path("library.dll"))
        assert not watcher._is_allowed_extension(Path("archive.zip"))
        assert not watcher._is_allowed_extension(Path("image.png"))
    
    def test_relative_paths_in_events(self, temp_workspace, mock_callback):
        """Should use relative paths in event context."""
        watcher = FileSystemWatcher(str(temp_workspace), mock_callback)
        watcher.start()
        
        time.sleep(0.5)
        
        # Create nested file
        nested_file = temp_workspace / "src" / "utils" / "helper.py"
        nested_file.parent.mkdir(parents=True, exist_ok=True)
        nested_file.write_text("# Helper")
        
        time.sleep(1)
        
        watcher.observer.stop()
        watcher.observer.join(timeout=2)
        
        # Event should contain relative path
        if mock_callback.called:
            call_args = mock_callback.call_args[0][0]
            file_path = call_args["file"]
            
            # Should be relative path
            assert not file_path.startswith("/")
            assert not ":" in file_path[0:2]  # Windows absolute path
            assert "src" in file_path
            assert "helper.py" in file_path
    
    def test_safe_path_validation(self, temp_workspace, mock_callback):
        """Should validate paths are within workspace."""
        watcher = FileSystemWatcher(str(temp_workspace), mock_callback)
        
        # Valid workspace paths
        assert watcher._is_safe_path(temp_workspace / "src" / "main.py")
        assert watcher._is_safe_path(temp_workspace / "README.md")
        
        # Paths outside workspace
        assert not watcher._is_safe_path(temp_workspace.parent / "outside.py")
        assert not watcher._is_safe_path(Path("/etc/passwd"))
        
        # Path traversal attempts
        assert not watcher._is_safe_path(temp_workspace / ".." / "outside.py")
    
    def test_event_contains_timestamp(self, temp_workspace, mock_callback):
        """Should include timestamp in events."""
        watcher = FileSystemWatcher(str(temp_workspace), mock_callback)
        watcher.start()
        
        time.sleep(0.5)
        
        test_file = temp_workspace / "src" / "test.py"
        test_file.write_text("# Test")
        
        time.sleep(1)
        
        watcher.observer.stop()
        watcher.observer.join(timeout=2)
        
        # Event should contain timestamp
        if mock_callback.called:
            call_args = mock_callback.call_args[0][0]
            assert "timestamp" in call_args
            assert call_args["timestamp"] is not None


class TestFileWatcherPatterns:
    """Test pattern matching configuration."""
    
    def test_watch_patterns_includes_common_extensions(self):
        """Should watch common development file types."""
        patterns_str = str(WATCH_PATTERNS)
        
        assert "*.py" in patterns_str
        assert "*.md" in patterns_str
        assert "*.json" in patterns_str
        assert "*.yaml" in patterns_str or "*.yml" in patterns_str
        assert "*.tsx" in patterns_str or "*.ts" in patterns_str
    
    def test_ignore_patterns_excludes_build_artifacts(self):
        """Should ignore build artifacts and dependencies."""
        patterns_str = str(IGNORE_PATTERNS)
        
        assert "__pycache__" in patterns_str
        assert ".git" in patterns_str
        assert "node_modules" in patterns_str
        assert ".pyc" in patterns_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
