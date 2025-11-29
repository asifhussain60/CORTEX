"""
Tests for FileSystemWalker component.

Tests the file system traversal functionality with filtering and exclusion patterns.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.crawlers.file_system_walker import FileSystemWalker


class TestFileSystemWalkerInitialization:
    """Test FileSystemWalker class initialization."""
    
    def test_walker_exists(self):
        """Test that FileSystemWalker class can be imported and instantiated."""
        walker = FileSystemWalker()
        assert walker is not None


class TestFileSystemWalkerTraversal:
    """Test directory traversal functionality."""
    
    def test_walk_method_exists(self):
        """Test that walk() method exists and accepts root_path."""
        walker = FileSystemWalker()
        # Method should exist (will implement in GREEN phase)
        assert hasattr(walker, 'walk')
    
    def test_walk_returns_list(self, tmp_path):
        """Test that walk() returns a list of file paths."""
        walker = FileSystemWalker()
        result = walker.walk(str(tmp_path))
        assert isinstance(result, list)


class TestFileSystemWalkerFiltering:
    """Test file filtering functionality."""
    
    def test_filter_by_extensions(self, tmp_path):
        """Test filtering files by extensions."""
        # Create test files
        (tmp_path / "test.py").write_text("# python")
        (tmp_path / "test.js").write_text("// js")
        (tmp_path / "test.txt").write_text("text")
        
        walker = FileSystemWalker()
        walker.set_extensions(['.py', '.js'])
        result = walker.walk(str(tmp_path))
        
        # Should only return .py and .js files
        extensions = {path.suffix for path in result}
        assert '.py' in extensions
        assert '.js' in extensions
        assert '.txt' not in extensions


class TestFileSystemWalkerExclusion:
    """Test directory exclusion patterns."""
    
    def test_exclude_directories(self, tmp_path):
        """Test excluding directories like .git, node_modules."""
        # Create directory structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "app.py").write_text("# app")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("git config")
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "lib.js").write_text("// lib")
        
        walker = FileSystemWalker()
        walker.set_exclusions(['.git', 'node_modules'])
        result = walker.walk(str(tmp_path))
        
        # Should not include files from excluded directories
        paths_str = [str(p) for p in result]
        assert any('app.py' in p for p in paths_str)
        assert not any('.git' in p for p in paths_str)
        assert not any('node_modules' in p for p in paths_str)
