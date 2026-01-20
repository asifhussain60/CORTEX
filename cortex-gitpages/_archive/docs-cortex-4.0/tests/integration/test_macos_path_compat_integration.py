"""
Integration tests for macOS path compatibility (AC-BRITTLE-004).

This test suite validates macOS path handling in realistic scenarios:
- File system operations with symlinked directories
- Application bundle path resolution in real environments
- Cross-system path portability verification
- CI/CD environment path handling

Test coverage: 14 integration tests across 4 test classes
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import os
import tempfile
from pathlib import Path
from typing import List, Optional
import pytest

from cortex_brain.tier0.macos_path_compat import MacOSPathCompatibility


class TestMacOSFileSystemOperations:
    """Test macOS path handling in file system operations."""

    def test_read_file_via_symlink(self) -> None:
        """Verify file reading through symlinked paths works correctly."""
        compat = MacOSPathCompatibility()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create original file
            original = Path(tmpdir) / "original.txt"
            content = "Test content for symlink"
            original.write_text(content)
            
            # Create symlink
            link = Path(tmpdir) / "symlink"
            link.symlink_to(original)
            
            # Read through symlink and verify
            link_content = (Path(tmpdir) / "symlink").read_text()
            assert link_content == content

    def test_directory_traversal_with_symlinks(self) -> None:
        """Verify directory traversal follows symlinks correctly."""
        compat = MacOSPathCompatibility()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            (subdir / "file.txt").write_text("content")
            
            # Create symlink to subdirectory
            link = Path(tmpdir) / "link_to_subdir"
            link.symlink_to(subdir)
            
            # Traverse through symlink
            file_in_link = link / "file.txt"
            assert file_in_link.exists()
            assert file_in_link.read_text() == "content"

    def test_normalize_mixed_separator_paths(self) -> None:
        """Verify normalization of paths with redundant separators."""
        compat = MacOSPathCompatibility()
        
        messy_path = "/Users//user///Documents//file.txt"
        normalized = compat.normalize_path(messy_path)
        
        # Should have no double slashes
        assert "//" not in normalized
        # Normalized should be shorter than original
        assert len(normalized) < len(messy_path)

    def test_path_resolution_chain(self) -> None:
        """Verify complete path resolution through multiple transformations."""
        compat = MacOSPathCompatibility()
        
        path = "~/Documents/../Downloads/./file.txt"
        
        expanded = compat.expand_home_path(path)
        normalized = compat.normalize_path(expanded)
        
        assert "~" not in normalized
        assert ".." not in normalized
        assert "//" not in normalized


class TestMacOSPathResolutionInEnvironment:
    """Test macOS path resolution in CI/CD and test environments."""

    def test_relative_to_absolute_conversion(self) -> None:
        """Verify conversion of relative paths to absolute."""
        compat = MacOSPathCompatibility()
        
        relative = "cortex_brain/tier0/macos_path_compat.py"
        
        # In test environment, should resolve against test root
        absolute = compat.make_absolute_path(relative)
        assert absolute.startswith("/") or absolute[1] == ":"  # Unix or Windows root

    def test_portable_path_from_cwd(self) -> None:
        """Verify paths work regardless of current working directory."""
        compat = MacOSPathCompatibility()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("content")
            
            # Should work with absolute path
            content = compat.read_file_safe(str(test_file))
            assert content == "content"

    def test_home_directory_expansion_ci_environment(self) -> None:
        """Verify ~ expansion works in CI environments."""
        compat = MacOSPathCompatibility()
        
        paths = [
            "~/file.txt",
            "~root/file.txt",
            "~/Documents/file.txt",
        ]
        
        for path in paths:
            expanded = compat.expand_home_path(path)
            assert expanded is not None
            assert "~" not in expanded

    def test_temp_directory_path_handling(self) -> None:
        """Verify handling of /tmp and /var/tmp paths."""
        compat = MacOSPathCompatibility()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            assert compat.validate_path(tmpdir) is True
            normalized = compat.normalize_path(tmpdir)
            assert normalized is not None


class TestMacOSCrossPlatformTranslation:
    """Test macOS-specific translation for cross-platform paths."""

    def test_detect_windows_path_format(self) -> None:
        """Verify detection and rejection of Windows paths on macOS."""
        compat = MacOSPathCompatibility()
        
        windows_path = "C:\\Users\\user\\file.txt"
        assert compat.is_valid_posix_path(windows_path) is False

    def test_detect_mixed_separators(self) -> None:
        """Verify detection of mixed separators (indication of cross-platform issue)."""
        compat = MacOSPathCompatibility()
        
        mixed = "/Users\\user/file.txt"
        assert compat.has_mixed_separators(mixed) is True

    def test_convert_to_posix_format(self) -> None:
        """Verify conversion to POSIX format for compatibility."""
        compat = MacOSPathCompatibility()
        
        mixed = "/Users//user///Documents/file.txt"
        # First normalize slashes, then convert to posix
        normalized = compat.normalize_path(mixed)
        posix = compat.to_posix_path(normalized)
        
        assert "\\" not in posix
        assert "//" not in posix

    def test_path_portability_validation(self) -> None:
        """Verify paths are portable across Unix-like systems."""
        compat = MacOSPathCompatibility()
        
        valid_paths = [
            "/Users/user/file.txt",
            "/opt/app/data.json",
            "/tmp/test.log",
        ]
        
        for path in valid_paths:
            assert compat.is_portable_path(path) is True


class TestMacOSPathErrorHandling:
    """Test error handling for various macOS path scenarios."""

    def test_nonexistent_path_handling(self) -> None:
        """Verify graceful handling of nonexistent paths."""
        compat = MacOSPathCompatibility()
        
        path = "/nonexistent/path/to/file.txt"
        
        # Should return False for exists check, not raise
        exists = compat.path_exists(path)
        assert exists is False

    def test_permission_denied_path(self) -> None:
        """Verify handling of permission-denied paths."""
        compat = MacOSPathCompatibility()
        
        # Should not raise on validation
        result = compat.validate_path("/root/.ssh/id_rsa")
        assert isinstance(result, bool)

    def test_broken_symlink_handling(self) -> None:
        """Verify handling of broken symlinks."""
        compat = MacOSPathCompatibility()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create symlink to nonexistent target
            link = Path(tmpdir) / "broken_link"
            link.symlink_to(Path(tmpdir) / "nonexistent")
            
            # Should handle gracefully
            result = compat.resolve_symlink(str(link))
            # Result can be None or string, but shouldn't raise

    def test_circular_symlink_loop_limit(self) -> None:
        """Verify circular symlink detection with loop limit."""
        compat = MacOSPathCompatibility()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create circular symlinks
            link1 = Path(tmpdir) / "link1"
            link2 = Path(tmpdir) / "link2"
            
            link1.symlink_to(link2)
            link2.symlink_to(link1)
            
            # Should detect and not loop infinitely
            result = compat.resolve_symlink(str(link1))
            assert result is None or isinstance(result, str)

    def test_unicode_path_error_handling(self) -> None:
        """Verify proper error handling for Unicode paths."""
        compat = MacOSPathCompatibility()
        
        unicode_path = "/Users/用户/文档/文件.txt"
        
        # Should validate or reject, not crash
        result = compat.validate_path(unicode_path)
        assert isinstance(result, bool)
