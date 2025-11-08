"""
CORTEX 2.0 - VSCodeMonitor Tests

Tests for VS Code editor state monitoring.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "cortex"))

from auto_capture_daemon import VSCodeMonitor, MAX_FILE_SIZE


class TestVSCodeMonitor:
    """Test VSCodeMonitor component."""
    
    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create temporary workspace with .vscode directory."""
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        return tmp_path
    
    def test_monitor_initialization(self, temp_workspace):
        """Should initialize monitor with valid workspace."""
        monitor = VSCodeMonitor(str(temp_workspace))
        
        assert monitor.workspace_path == temp_workspace.resolve()
        assert monitor.vscode_path == temp_workspace / ".vscode"
    
    def test_get_open_files_with_valid_workspace(self, temp_workspace):
        """Should parse workspace.json for open files."""
        workspace_file = temp_workspace / ".vscode" / "workspace.json"
        
        # Create valid workspace JSON
        workspace_data = {
            "folders": [
                {"path": str(temp_workspace / "src")},
                {"path": str(temp_workspace / "tests")}
            ]
        }
        workspace_file.write_text(json.dumps(workspace_data))
        
        monitor = VSCodeMonitor(str(temp_workspace))
        open_files = monitor.get_open_files()
        
        # Should return file paths
        assert isinstance(open_files, list)
        assert len(open_files) == 2
        assert "src" in str(open_files[0])
        assert "tests" in str(open_files[1])
    
    def test_get_open_files_returns_empty_if_no_workspace(self, temp_workspace):
        """Should return empty list if no workspace file."""
        monitor = VSCodeMonitor(str(temp_workspace))
        open_files = monitor.get_open_files()
        
        assert open_files == []
    
    def test_get_open_files_handles_invalid_json(self, temp_workspace):
        """Should handle malformed JSON gracefully."""
        workspace_file = temp_workspace / ".vscode" / "workspace.json"
        workspace_file.write_text("{invalid json")
        
        monitor = VSCodeMonitor(str(temp_workspace))
        open_files = monitor.get_open_files()
        
        # Should return empty list on parse error
        assert open_files == []
    
    def test_get_open_files_limits_file_count(self, temp_workspace):
        """Should limit number of files returned (max 100)."""
        workspace_file = temp_workspace / ".vscode" / "workspace.json"
        
        # Create workspace with 200 files
        workspace_data = {
            "folders": [
                {"path": f"/path/to/file{i}"} for i in range(200)
            ]
        }
        workspace_file.write_text(json.dumps(workspace_data))
        
        monitor = VSCodeMonitor(str(temp_workspace))
        open_files = monitor.get_open_files()
        
        # Should limit to 100 files
        assert len(open_files) <= 100
    
    def test_rejects_oversized_workspace_file(self, temp_workspace):
        """Should reject workspace files exceeding MAX_FILE_SIZE."""
        workspace_file = temp_workspace / ".vscode" / "workspace.json"
        
        # Create oversized file
        workspace_file.write_bytes(b"x" * (MAX_FILE_SIZE + 1))
        
        monitor = VSCodeMonitor(str(temp_workspace))
        open_files = monitor.get_open_files()
        
        # Should return empty list for oversized file
        assert open_files == []
    
    def test_sanitize_path_validates_workspace_boundary(self, temp_workspace):
        """Should validate paths are within workspace."""
        monitor = VSCodeMonitor(str(temp_workspace))
        
        # Valid workspace path
        valid_path = str(temp_workspace / "src" / "main.py")
        sanitized = monitor._sanitize_path(valid_path)
        assert sanitized is not None
        assert "src" in sanitized
        
        # Path outside workspace
        outside_path = str(temp_workspace.parent / "outside.py")
        sanitized = monitor._sanitize_path(outside_path)
        assert sanitized is None
    
    def test_sanitize_path_handles_invalid_paths(self, temp_workspace):
        """Should handle invalid path strings."""
        monitor = VSCodeMonitor(str(temp_workspace))
        
        # Empty path
        assert monitor._sanitize_path("") is None
        
        # Malformed path
        assert monitor._sanitize_path(":::invalid:::") is None
    
    def test_get_active_file_returns_none(self, temp_workspace):
        """Should return None (requires extension for full implementation)."""
        monitor = VSCodeMonitor(str(temp_workspace))
        active_file = monitor.get_active_file()
        
        # Simplified implementation returns None
        assert active_file is None


class TestVSCodeStateValidation:
    """Test VS Code state validation."""
    
    def test_validates_json_structure(self, tmp_path):
        """Should validate JSON has expected structure."""
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        workspace_file = vscode_dir / "workspace.json"
        
        # Missing 'folders' key
        workspace_file.write_text(json.dumps({"other": "data"}))
        
        monitor = VSCodeMonitor(str(tmp_path))
        open_files = monitor.get_open_files()
        
        # Should handle missing 'folders' key
        assert open_files == []
    
    def test_validates_folder_entries(self, tmp_path):
        """Should validate folder entries have 'path' property."""
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        workspace_file = vscode_dir / "workspace.json"
        
        # Invalid folder entries (no 'path')
        workspace_data = {
            "folders": [
                {"name": "folder1"},  # Missing path
                {"path": str(tmp_path / "valid")}  # Valid
            ]
        }
        workspace_file.write_text(json.dumps(workspace_data))
        
        monitor = VSCodeMonitor(str(tmp_path))
        open_files = monitor.get_open_files()
        
        # Should only return valid entries
        assert len(open_files) == 1
        assert "valid" in open_files[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
