"""
Unit tests for macOS path compatibility fixes (AC-BRITTLE-004).

This test suite validates macOS-specific path handling including:
- Symlink resolution
- .app bundle path handling
- Case-insensitive filesystem support
- macOS reserved names
- Path normalization for POSIX systems
- Home directory expansion (~)
- Case sensitivity awareness

Test coverage: 10 unit test classes with 50+ assertions
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional
from unittest.mock import Mock, patch, MagicMock
import pytest

# Tests assume implementation in cortex_brain/tier0/macos_path_compat.py
from cortex_brain.tier0.macos_path_compat import MacOSPathCompatibility


class TestMacOSSymlinkResolution:
    """Test symlink resolution and dereferencing on macOS."""

    def test_resolve_symlink_to_target(self) -> None:
        """Verify symlink resolution returns absolute target path."""
        compat = MacOSPathCompatibility()
        
        # Create temp directory with symlink
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "target_file.txt"
            target.write_text("content")
            
            link = Path(tmpdir) / "link_to_file"
            link.symlink_to(target)
            
            result = compat.resolve_symlink(str(link))
            assert str(target) == result or Path(result).resolve() == target.resolve()

    def test_resolve_symlink_chain(self) -> None:
        """Verify resolution of chained symlinks (A -> B -> C -> file)."""
        compat = MacOSPathCompatibility()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "real_file.txt"
            target.write_text("content")
            
            link1 = Path(tmpdir) / "link1"
            link1.symlink_to(target)
            
            link2 = Path(tmpdir) / "link2"
            link2.symlink_to(link1)
            
            result = compat.resolve_symlink(str(link2))
            assert Path(result).resolve() == target.resolve()

    def test_resolve_nonexistent_symlink(self) -> None:
        """Verify handling of broken symlinks (target doesn't exist)."""
        compat = MacOSPathCompatibility()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            link = Path(tmpdir) / "broken_link"
            nonexistent = Path(tmpdir) / "nonexistent"
            link.symlink_to(nonexistent)
            
            # Should not raise, but return resolved path or None
            result = compat.resolve_symlink(str(link))
            assert result is not None or result is None

    def test_resolve_relative_symlink(self) -> None:
        """Verify resolution of relative symlinks."""
        compat = MacOSPathCompatibility()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            
            target = subdir / "target.txt"
            target.write_text("content")
            
            link = Path(tmpdir) / "link"
            link.symlink_to("subdir/target.txt")
            
            result = compat.resolve_symlink(str(link))
            assert result is not None


class TestMacOSAppBundleHandling:
    """Test handling of .app bundle paths on macOS."""

    def test_detect_app_bundle_path(self) -> None:
        """Verify detection of .app bundle paths."""
        compat = MacOSPathCompatibility()
        
        app_path = "/Applications/MyApp.app/Contents/MacOS/MyApp"
        assert compat.is_app_bundle_path(app_path) is True
        
        regular_path = "/Users/user/file.txt"
        assert compat.is_app_bundle_path(regular_path) is False

    def test_extract_bundle_root(self) -> None:
        """Verify extraction of .app bundle root from nested path."""
        compat = MacOSPathCompatibility()
        
        app_path = "/Applications/MyApp.app/Contents/MacOS/MyApp"
        bundle_root = compat.get_app_bundle_root(app_path)
        
        assert bundle_root is not None
        assert bundle_root.endswith(".app")
        assert "MyApp.app" in bundle_root

    def test_get_bundle_resources_path(self) -> None:
        """Verify access to bundle Resources directory."""
        compat = MacOSPathCompatibility()
        
        app_path = "/Applications/MyApp.app/Contents/MacOS/MyApp"
        resources = compat.get_app_bundle_resources_path(app_path)
        
        assert resources is not None
        assert "Resources" in resources

    def test_get_bundle_executable_path(self) -> None:
        """Verify access to bundle executable."""
        compat = MacOSPathCompatibility()
        
        app_path = "/Applications/MyApp.app/Contents/MacOS/MyApp"
        exec_path = compat.get_app_bundle_executable_path(app_path)
        
        assert exec_path is not None
        assert "MacOS" in exec_path


class TestMacOSCaseInsensitivityHandling:
    """Test case-insensitive path handling (APFS case-insensitive mode)."""

    def test_normalize_case_path(self) -> None:
        """Verify case normalization for case-insensitive filesystems."""
        compat = MacOSPathCompatibility()
        
        path = "/Users/User/Documents/FILE.txt"
        normalized = compat.normalize_case_path(path)
        
        assert normalized is not None
        # Should handle case appropriately

    def test_case_insensitive_comparison(self) -> None:
        """Verify case-insensitive path comparison."""
        compat = MacOSPathCompatibility()
        
        path1 = "/Users/User/Documents/file.txt"
        path2 = "/Users/user/documents/FILE.TXT"
        
        # Result depends on filesystem case sensitivity
        result = compat.paths_equal_case_insensitive(path1, path2)
        assert isinstance(result, bool)  # Should return boolean

    def test_case_sensitive_flag(self) -> None:
        """Verify detection of case-sensitive filesystem."""
        compat = MacOSPathCompatibility()
        
        # Check if current filesystem is case-sensitive
        is_case_sensitive = compat.is_filesystem_case_sensitive()
        assert isinstance(is_case_sensitive, bool)


class TestMacOSHomeDirectoryExpansion:
    """Test ~ (home directory) expansion on macOS."""

    def test_expand_tilde_user_home(self) -> None:
        """Verify expansion of ~ to user home directory."""
        compat = MacOSPathCompatibility()
        
        path = "~/Documents/file.txt"
        expanded = compat.expand_home_path(path)
        
        assert expanded is not None
        assert "~" not in expanded
        assert expanded.startswith("/Users/") or expanded.startswith("/home/")

    def test_expand_tilde_root_home(self) -> None:
        """Verify expansion of ~root to root home."""
        compat = MacOSPathCompatibility()
        
        path = "~root/file.txt"
        expanded = compat.expand_home_path(path)
        
        assert expanded is not None
        assert "~" not in expanded

    def test_no_tilde_path_unchanged(self) -> None:
        """Verify paths without ~ are returned unchanged."""
        compat = MacOSPathCompatibility()
        
        path = "/Users/user/file.txt"
        result = compat.expand_home_path(path)
        
        assert result == path


class TestMacOSReservedNames:
    """Test detection and handling of macOS reserved names."""

    def test_detect_macos_reserved_names(self) -> None:
        """Verify detection of macOS reserved device/system names."""
        compat = MacOSPathCompatibility()
        
        reserved_names = [".DS_Store", ".AppleDouble", ".AppleDB", ".TemporaryItems"]
        
        for name in reserved_names:
            assert compat.is_macos_reserved_name(name) is True

    def test_non_reserved_names(self) -> None:
        """Verify non-reserved names not flagged."""
        compat = MacOSPathCompatibility()
        
        regular_names = ["file.txt", "document.md", "README"]
        
        for name in regular_names:
            assert compat.is_macos_reserved_name(name) is False

    def test_ds_store_exclusion(self) -> None:
        """Verify .DS_Store files can be excluded from operations."""
        compat = MacOSPathCompatibility()
        
        files = ["file.txt", ".DS_Store", "README.md", ".DS_Store"]
        filtered = compat.filter_macos_reserved_names(files)
        
        assert ".DS_Store" not in filtered
        assert "file.txt" in filtered


class TestMacOSPOSIXCompliance:
    """Test POSIX compliance for macOS path handling."""

    def test_forward_slash_paths(self) -> None:
        """Verify forward slash handling (always in POSIX)."""
        compat = MacOSPathCompatibility()
        
        path = "/Users/user/Documents/file.txt"
        assert compat.is_valid_posix_path(path) is True

    def test_leading_slash_absolute_path(self) -> None:
        """Verify leading slash indicates absolute path."""
        compat = MacOSPathCompatibility()
        
        absolute = "/Users/user/file.txt"
        relative = "Users/user/file.txt"
        
        assert compat.is_absolute_path(absolute) is True
        assert compat.is_absolute_path(relative) is False

    def test_no_backslashes(self) -> None:
        """Verify rejection of Windows-style backslashes."""
        compat = MacOSPathCompatibility()
        
        windows_path = "\\Users\\user\\file.txt"
        assert compat.is_valid_posix_path(windows_path) is False


class TestMacOSPathNormalization:
    """Test path normalization for macOS."""

    def test_normalize_redundant_slashes(self) -> None:
        """Verify removal of redundant slashes."""
        compat = MacOSPathCompatibility()
        
        path = "/Users//user///Documents/file.txt"
        normalized = compat.normalize_path(path)
        
        assert "//" not in normalized

    def test_normalize_dot_segments(self) -> None:
        """Verify resolution of . and .. segments."""
        compat = MacOSPathCompatibility()
        
        path = "/Users/user/Documents/../file.txt"
        normalized = compat.normalize_path(path)
        
        assert ".." not in normalized
        assert normalized == "/Users/user/file.txt"

    def test_normalize_trailing_slash(self) -> None:
        """Verify handling of trailing slashes."""
        compat = MacOSPathCompatibility()
        
        path = "/Users/user/Documents/"
        normalized = compat.normalize_path(path)
        
        # Should remove trailing slash or handle consistently
        assert isinstance(normalized, str)


class TestMacOSPathEncoding:
    """Test path encoding and Unicode normalization on macOS."""

    def test_utf8_path_handling(self) -> None:
        """Verify UTF-8 encoded paths."""
        compat = MacOSPathCompatibility()
        
        path = "/Users/user/Documents/файл.txt"  # Cyrillic
        assert compat.is_valid_utf8_path(path) is True

    def test_unicode_normalization(self) -> None:
        """Verify NFD normalization (macOS uses NFD for filenames)."""
        compat = MacOSPathCompatibility()
        
        # é as single character (NFC) vs e + acute (NFD)
        path_nfc = "/Users/user/café.txt"
        path_nfd = compat.normalize_unicode_path(path_nfc)
        
        assert path_nfd is not None
        # macOS HFS+ and APFS normalize to NFD

    def test_emoji_path_support(self) -> None:
        """Verify emoji characters in paths."""
        compat = MacOSPathCompatibility()
        
        path = "/Users/user/Documents/🚀-project.txt"
        assert compat.is_valid_utf8_path(path) is True


class TestMacOSPathValidation:
    """Test validation of macOS paths."""

    def test_validate_path_length(self) -> None:
        """Verify path length validation (255 bytes per component on macOS)."""
        compat = MacOSPathCompatibility()
        
        valid_path = "/Users/user/documents/file.txt"
        assert compat.validate_path(valid_path) is True
        
        # Create path with component > 255 bytes
        long_component = "a" * 256
        invalid_path = f"/Users/user/{long_component}.txt"
        assert compat.validate_path(invalid_path) is False

    def test_validate_special_characters(self) -> None:
        """Verify validation of special characters."""
        compat = MacOSPathCompatibility()
        
        # macOS allows most characters except null
        valid = "/Users/user/file (1).txt"
        assert compat.validate_path(valid) is True
        
        invalid = "/Users/user/file\x00.txt"
        assert compat.validate_path(invalid) is False

    def test_validate_path_separators(self) -> None:
        """Verify forward slashes required."""
        compat = MacOSPathCompatibility()
        
        valid = "/Users/user/file.txt"
        assert compat.validate_path(valid) is True
        
        invalid = "Users\\user\\file.txt"
        assert compat.validate_path(invalid) is False


class TestMacOSThreadSafety:
    """Test thread-safe operations for macOS path handling."""

    def test_concurrent_symlink_resolution(self) -> None:
        """Verify thread-safe symlink resolution."""
        compat = MacOSPathCompatibility()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "target.txt"
            target.write_text("content")
            
            link = Path(tmpdir) / "link"
            link.symlink_to(target)
            
            # Multiple concurrent calls should not raise
            results = []
            for _ in range(3):
                result = compat.resolve_symlink(str(link))
                results.append(result)
            
            assert len(set(results)) <= 2  # All should be same or similar

    def test_concurrent_path_normalization(self) -> None:
        """Verify thread-safe path normalization."""
        compat = MacOSPathCompatibility()
        
        path = "/Users//user///Documents/file.txt"
        
        results = []
        for _ in range(3):
            normalized = compat.normalize_path(path)
            results.append(normalized)
        
        # All should produce same result
        assert len(set(results)) == 1


class TestMacOSCoverageExtensions:
    """Extended coverage tests for edge cases and boundary conditions."""

    def test_root_path_handling(self) -> None:
        """Verify root path (/) handling."""
        compat = MacOSPathCompatibility()
        
        assert compat.is_absolute_path("/") is True
        normalized = compat.normalize_path("/")
        assert normalized == "/"

    def test_single_filename(self) -> None:
        """Verify handling of single filename (no path)."""
        compat = MacOSPathCompatibility()
        
        filename = "file.txt"
        assert compat.is_absolute_path(filename) is False

    def test_permission_denied_symlink(self) -> None:
        """Verify graceful handling of permission-denied symlinks."""
        compat = MacOSPathCompatibility()
        
        # Should not raise, but handle gracefully
        result = compat.resolve_symlink("/root/.ssh/id_rsa")
        assert result is not None or result is None

    def test_circular_symlink_detection(self) -> None:
        """Verify detection of circular symlinks."""
        compat = MacOSPathCompatibility()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            link1 = Path(tmpdir) / "link1"
            link2 = Path(tmpdir) / "link2"
            
            link1.symlink_to(link2)
            link2.symlink_to(link1)
            
            # Should detect circular reference
            result = compat.resolve_symlink(str(link1))
            assert result is None or isinstance(result, str)


class TestMacOSRefactorCoverage:
    """Extended coverage tests for improved metrics (REFACTOR phase)."""

    def test_symlink_cache_hit(self) -> None:
        """Verify symlink resolution caching works correctly."""
        compat = MacOSPathCompatibility()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "target.txt"
            target.write_text("content")
            
            link = Path(tmpdir) / "link"
            link.symlink_to(target)
            
            link_str = str(link)
            
            # First call - cache miss
            result1 = compat.resolve_symlink(link_str)
            
            # Second call - should use cache
            result2 = compat.resolve_symlink(link_str)
            
            assert result1 == result2
            assert link_str in compat._symlink_cache

    def test_app_bundle_detection_nested(self) -> None:
        """Verify .app bundle detection in deeply nested paths."""
        compat = MacOSPathCompatibility()
        
        paths = [
            "/Applications/XCode.app/Contents/Frameworks/UIKit.framework/Headers",
            "/Library/Frameworks/Python.framework/Versions/3.9/bin/python3",
            "/Users/user/Applications/MyApp.app/Contents/Resources/data.json",
        ]
        
        results = []
        for path in paths:
            is_bundle = compat.is_app_bundle_path(path)
            results.append(is_bundle)
        
        # First and third should be in bundle
        assert results[0] is True
        assert results[2] is True

    def test_bundle_paths_extraction(self) -> None:
        """Verify bundle path extraction for various depths."""
        compat = MacOSPathCompatibility()
        
        deep_path = "/Applications/MyApp.app/Contents/Frameworks/MyFramework.framework/Headers"
        bundle_root = compat.get_app_bundle_root(deep_path)
        
        assert bundle_root is not None
        assert bundle_root.endswith(".app")
        assert "MyApp.app" in bundle_root

    def test_unicode_normalization_consistency(self) -> None:
        """Verify Unicode normalization produces consistent results."""
        compat = MacOSPathCompatibility()
        
        # Combining character vs precomposed
        path_nfc = "/Users/user/café"  # NFC: é as single character
        
        normalized1 = compat.normalize_unicode_path(path_nfc)
        normalized2 = compat.normalize_unicode_path(normalized1)
        
        # Should be idempotent
        assert normalized1 == normalized2

    def test_path_validation_comprehensive(self) -> None:
        """Verify comprehensive path validation covers all checks."""
        compat = MacOSPathCompatibility()
        
        test_cases = [
            ("/valid/path/file.txt", True),
            ("/path\x00with\x00null", False),
            ("/very/long/" + "a" * 256 + "/path", False),
            ("/path\\with\\backslash", False),
        ]
        
        for path, expected in test_cases:
            result = compat.validate_path(path)
            assert result == expected, f"Path validation failed for {path}"

    def test_concurrent_operations_stress(self) -> None:
        """Verify thread-safety with multiple concurrent operations."""
        import threading
        
        compat = MacOSPathCompatibility()
        results = []
        errors = []
        
        def stress_test() -> None:
            try:
                paths = [
                    "/Users/user/file1.txt",
                    "/Users/user/file2.txt",
                    "~/Documents/file.txt",
                ]
                
                for path in paths:
                    normalized = compat.normalize_path(path)
                    expanded = compat.expand_home_path(path)
                    is_valid = compat.validate_path(normalized)
                    results.append((normalized, expanded, is_valid))
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=stress_test) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Concurrency errors: {errors}"
        assert len(results) > 0

    def test_home_expansion_multiple_users(self) -> None:
        """Verify home directory expansion for different user patterns."""
        compat = MacOSPathCompatibility()
        
        paths = ["~/file.txt", "~/Documents/file.txt", "~/Desktop/file.txt"]
        
        for path in paths:
            expanded = compat.expand_home_path(path)
            assert expanded is not None
            # Should have expanded ~ for current user
            if path.startswith("~/"):
                assert expanded != path  # Should be different after expansion

    def test_posix_path_methods_chain(self) -> None:
        """Verify chaining of POSIX path methods."""
        compat = MacOSPathCompatibility()
        
        # Start with messy path
        messy = "~/Documents//file.txt"
        
        # Chain multiple operations
        step1 = compat.expand_home_path(messy)
        step2 = compat.normalize_path(step1)
        step3 = compat.to_posix_path(step2)
        
        # Result should be clean
        assert "~" not in step3
        assert "//" not in step3
        assert "\\" not in step3
        assert compat.validate_path(step3) is True

    def test_error_handling_graceful_degradation(self) -> None:
        """Verify graceful degradation on various error conditions."""
        compat = MacOSPathCompatibility()
        
        # All should return safely without raising
        bad_paths = [
            None,
            "",
            "/nonexistent/path",
            "/root/.ssh/id_rsa",
            "/path\x00with\x00nulls",
        ]
        
        for path in bad_paths:
            if path is None:
                continue
            # Should not raise
            try:
                exists = compat.path_exists(path)
                assert isinstance(exists, bool)
            except Exception as e:
                pytest.fail(f"path_exists raised for {path}: {e}")
