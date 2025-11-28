"""
Tests for Git History metadata storage foundation.

This module validates the .cortex/metadata directory structure and conventions.
"""

import pytest
from pathlib import Path
import json
from datetime import datetime, UTC


class TestGitHistoryMetadataFoundation:
    """Test .cortex/metadata directory structure and conventions."""
    
    def test_metadata_directory_exists(self):
        """Verify .cortex/metadata directory exists."""
        metadata_dir = Path(".cortex/metadata")
        assert metadata_dir.exists()
        assert metadata_dir.is_dir()
    
    def test_can_write_history_cache_file(self):
        """Verify ability to write history cache JSON."""
        metadata_dir = Path(".cortex/metadata")
        cache_file = metadata_dir / "history-cache.json"
        
        # Write test cache
        test_data = {
            "cached_at": datetime.now(UTC).isoformat(),
            "commits": [
                {
                    "sha": "abc123",
                    "message": "Test commit",
                    "author": "test@example.com",
                    "date": "2025-11-28T12:00:00Z"
                }
            ]
        }
        
        cache_file.write_text(json.dumps(test_data, indent=2))
        
        assert cache_file.exists()
        
        # Read back and verify
        loaded_data = json.loads(cache_file.read_text())
        assert "cached_at" in loaded_data
        assert len(loaded_data["commits"]) == 1
        
        # Cleanup
        cache_file.unlink()
    
    def test_can_write_file_history_cache(self):
        """Verify ability to write per-file history cache."""
        metadata_dir = Path(".cortex/metadata")
        file_cache = metadata_dir / "file-history-src-main.py.json"
        
        # Write test file history
        test_data = {
            "file_path": "src/main.py",
            "cached_at": datetime.now(UTC).isoformat(),
            "changes": [
                {
                    "sha": "def456",
                    "message": "Fix bug in main",
                    "lines_added": 5,
                    "lines_removed": 2
                }
            ]
        }
        
        file_cache.write_text(json.dumps(test_data, indent=2))
        
        assert file_cache.exists()
        
        # Read back and verify
        loaded_data = json.loads(file_cache.read_text())
        assert loaded_data["file_path"] == "src/main.py"
        assert len(loaded_data["changes"]) == 1
        
        # Cleanup
        file_cache.unlink()
    
    def test_metadata_directory_in_gitignore(self):
        """Verify .cortex/ is in .gitignore."""
        gitignore = Path(".gitignore")
        if gitignore.exists():
            content = gitignore.read_text()
            assert ".cortex/" in content or ".cortex" in content
    
    def test_cache_file_naming_convention(self):
        """Verify cache file naming follows convention."""
        # Convention: history-cache.json for global, file-history-{sanitized-path}.json for per-file
        
        test_path = "src/utils/helper.py"
        sanitized = test_path.replace("/", "-").replace("\\", "-")
        expected_filename = f"file-history-{sanitized}.json"
        
        assert expected_filename == "file-history-src-utils-helper.py.json"
