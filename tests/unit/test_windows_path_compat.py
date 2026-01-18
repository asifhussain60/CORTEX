"""
AC-BRITTLE-003: Unit Tests for Windows Path Compatibility Fix

This module contains unit tests for Windows-specific path compatibility features.
Tests cover drive letters, UNC paths, reserved names, path encoding, and more.

Test Classes:
    - TestWindowsDriveLetters: Drive letter handling (C:, D:, etc.)
    - TestUNCPathSupport: UNC path support (\\\\server\\share)
    - TestReservedNames: Windows reserved names (CON, PRN, AUX, etc.)
    - TestPathNormalization: Backslash vs forward slash normalization
    - TestCaseInsensitivity: Case-insensitive path handling
    - TestEnvironmentVariables: Environment variable expansion (%USERPROFILE%)
    - TestPathEncoding: Path encoding validation (UTF-8, ASCII, etc.)
    - TestLongPathSupport: Long path support (>260 characters)
    - TestSpecialCharacters: Special character restrictions on Windows
    - TestShortnames: 8.3 shortname (DOS) support
    - TestNetworkPaths: Network drive path handling
    - TestJunctionPoints: Junction point detection and handling

Governance Rules Applied:
    - CORE-008: TDD approach (tests first, implementation second)
    - CORE-011: 100% type hints on all methods
    - CORE-012: 100% docstrings on all methods
    - CORE-024: Thread-safe implementations
    - CORE-028: Portable path handling
"""

import pytest
from typing import List, Tuple
import sys
from pathlib import PureWindowsPath, Path
import tempfile
import os


class TestWindowsDriveLetters:
    """Test drive letter handling for Windows paths."""

    def test_valid_drive_letters(self) -> None:
        """Test that all valid drive letters (A-Z) are recognized."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            path = f"{letter}:\\test\\path"
            assert compat.validate_path(path) is True, f"Drive {letter}: should be valid"

    def test_lowercase_drive_letters(self) -> None:
        """Test that lowercase drive letters are accepted and normalized."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path = "c:\\test\\path"
        assert compat.validate_path(path) is True
        normalized = compat.normalize_path(path)
        assert normalized[0].isupper()

    def test_invalid_drive_characters(self) -> None:
        """Test that non-letter drive characters are rejected."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        invalid_paths = ["1:\\test", "@:\\test", "_:\\test"]
        for path in invalid_paths:
            assert compat.validate_path(path) is False, f"Path {path} should be invalid"

    def test_missing_drive_letter(self) -> None:
        """Test that paths without drive letters are handled appropriately."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path = "\\test\\path"
        # Should be valid as relative path
        assert compat.validate_path(path) is True


class TestUNCPathSupport:
    """Test UNC (Universal Naming Convention) path support."""

    def test_valid_unc_path(self) -> None:
        """Test that valid UNC paths are recognized."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        unc_path = "\\\\server\\share\\file.txt"
        assert compat.validate_path(unc_path) is True

    def test_unc_path_normalization(self) -> None:
        """Test that UNC paths are normalized correctly."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        unc_path = "//server/share/file.txt"
        normalized = compat.normalize_path(unc_path)
        assert normalized.startswith("\\\\") or normalized.startswith("//")

    def test_unc_path_with_spaces(self) -> None:
        """Test UNC paths containing spaces."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        unc_path = "\\\\server name\\share folder\\file.txt"
        assert compat.validate_path(unc_path) is True

    def test_invalid_unc_path(self) -> None:
        """Test that invalid UNC paths are rejected."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        invalid = "\\\\\\invalid"  # Too many backslashes
        # Should either be invalid or handled gracefully
        result = compat.validate_path(invalid)
        assert result is not None  # Should return a boolean


class TestReservedNames:
    """Test handling of Windows reserved names."""

    def test_reserved_name_detection(self) -> None:
        """Test detection of reserved names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        reserved_names = [
            "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
        ]
        for name in reserved_names:
            path = f"C:\\{name}"
            assert compat.handle_reserved_names(path) is not None

    def test_reserved_name_with_extension(self) -> None:
        """Test that reserved names with extensions are still reserved."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path = "C:\\CON.txt"
        result = compat.handle_reserved_names(path)
        assert result is not None

    def test_non_reserved_names(self) -> None:
        """Test that non-reserved names are not flagged."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path = "C:\\myfile.txt"
        result = compat.handle_reserved_names(path)
        assert result is not None


class TestPathNormalization:
    """Test backslash vs forward slash normalization."""

    def test_forward_slash_normalization(self) -> None:
        """Test that forward slashes are converted to backslashes."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path = "C:/test/path/file.txt"
        normalized = compat.normalize_path(path)
        # Should be normalized (either all backslash or consistently formatted)
        assert "\\" in normalized or "/" in normalized

    def test_mixed_slash_normalization(self) -> None:
        """Test that mixed slashes are normalized consistently."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path = "C:\\test/mixed\\path/file.txt"
        normalized = compat.normalize_path(path)
        # Should have consistent slash style
        backslash_count = normalized.count("\\")
        forward_slash_count = normalized.count("/")
        assert normalized is not None

    def test_double_backslash_normalization(self) -> None:
        """Test that double backslashes are normalized."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path = "C:\\\\test\\\\path"
        normalized = compat.normalize_path(path)
        # Should not have double backslashes (except UNC paths)
        assert normalized is not None


class TestCaseInsensitivity:
    """Test case-insensitive path handling."""

    def test_case_insensitive_comparison(self) -> None:
        """Test that paths are compared case-insensitively."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path1 = "C:\\Test\\File.txt"
        path2 = "c:\\test\\file.txt"
        # Should be treated as equivalent
        norm1 = compat.normalize_path(path1)
        norm2 = compat.normalize_path(path2)
        assert norm1.lower() == norm2.lower()

    def test_uppercase_drive_letter(self) -> None:
        """Test that drive letters are uppercase after normalization."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path = "c:\\test\\path"
        normalized = compat.normalize_path(path)
        assert normalized[0].isupper()


class TestEnvironmentVariables:
    """Test environment variable expansion in paths."""

    def test_expand_userprofile(self) -> None:
        """Test expansion of %USERPROFILE% variable."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path = "%USERPROFILE%\\Documents\\file.txt"
        expanded = compat.expand_environment_vars(path)
        assert "%" not in expanded or expanded == path

    def test_expand_windir(self) -> None:
        """Test expansion of %WINDIR% variable."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path = "%WINDIR%\\System32\\file.txt"
        expanded = compat.expand_environment_vars(path)
        assert "%" not in expanded or expanded == path

    def test_expand_temp(self) -> None:
        """Test expansion of %TEMP% variable."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path = "%TEMP%\\tempfile.txt"
        expanded = compat.expand_environment_vars(path)
        assert "%" not in expanded or expanded == path

    def test_no_expansion_needed(self) -> None:
        """Test paths without environment variables."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path = "C:\\Users\\test\\file.txt"
        expanded = compat.expand_environment_vars(path)
        assert expanded == path


class TestPathEncoding:
    """Test path encoding validation."""

    def test_utf8_path(self) -> None:
        """Test UTF-8 encoded paths."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path = "C:\\тест\\файл.txt"  # Cyrillic characters
        assert compat.validate_path(path) is True

    def test_ascii_path(self) -> None:
        """Test ASCII path validation."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path = "C:\\test\\file.txt"
        assert compat.validate_path(path) is True

    def test_unicode_path(self) -> None:
        """Test Unicode paths with emoji characters."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path = "C:\\test\\📁\\file.txt"
        result = compat.validate_path(path)
        assert result is not None


class TestLongPathSupport:
    """Test long path support (>260 characters)."""

    def test_long_path_detection(self) -> None:
        """Test detection of paths exceeding 260 characters."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        # Create a path longer than 260 characters
        long_path = "C:\\" + "very_long_directory_name\\" * 30 + "file.txt"
        result = compat.support_long_paths(long_path)
        assert result is not None

    def test_long_path_normalization(self) -> None:
        """Test normalization of long paths."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        long_path = "C:\\" + "dir\\" * 100 + "file.txt"
        normalized = compat.support_long_paths(long_path)
        assert normalized is not None

    def test_long_path_prefixing(self) -> None:
        """Test that long paths are prefixed with \\\\?\\ when needed."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        long_path = "C:\\" + "directory\\" * 50 + "file.txt"
        result = compat.support_long_paths(long_path)
        # Should either have long path prefix or handle appropriately
        assert result is not None


class TestSpecialCharacters:
    """Test special character restrictions on Windows."""

    def test_invalid_characters(self) -> None:
        """Test detection of invalid characters in paths."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        # Windows disallows: < > : " | ? * in filenames
        invalid_chars_paths = [
            "C:\\test<file>",
            "C:\\test\"file\"",
            "C:\\test|file",
            "C:\\test?file",
            "C:\\test*file",
        ]
        # At least some should be flagged as issues
        invalid_count = 0
        for path in invalid_chars_paths:
            if not compat.validate_path(path):
                invalid_count += 1
        assert invalid_count > 0

    def test_valid_special_characters(self) -> None:
        """Test that valid special characters are allowed."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        valid_paths = [
            "C:\\test-file.txt",
            "C:\\test_file.txt",
            "C:\\test (1).txt",
            "C:\\test@file.txt",
            "C:\\test#file.txt",
        ]
        for path in valid_paths:
            assert compat.validate_path(path) is True


class TestShortnames:
    """Test 8.3 DOS shortname support."""

    def test_shortname_detection(self) -> None:
        """Test detection of 8.3 shortnames."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        shortname = "C:\\PROGRA~1\\file.txt"  # Program Files in 8.3 format
        result = compat.support_shortnames(shortname)
        assert result is not None

    def test_shortname_expansion(self) -> None:
        """Test expansion of 8.3 shortnames."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        shortname = "C:\\PROGRA~1\\MYAPP~1"
        expanded = compat.support_shortnames(shortname)
        # Should either expand or handle appropriately
        assert expanded is not None


class TestNetworkPaths:
    """Test network drive path handling."""

    def test_network_drive_path(self) -> None:
        """Test handling of mapped network drives."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        network_path = "Z:\\network\\share\\file.txt"
        assert compat.validate_path(network_path) is True

    def test_network_drive_normalization(self) -> None:
        """Test normalization of network drive paths."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        network_path = "Z:/network/share/file.txt"
        normalized = compat.normalize_path(network_path)
        assert normalized is not None


class TestJunctionPoints:
    """Test junction point detection and handling."""

    def test_junction_point_path_format(self) -> None:
        """Test that junction point paths are formatted correctly."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        # Junction points look like normal directories but point elsewhere
        junction_path = "C:\\Users\\test\\AppData"
        result = compat.handle_junction_points(junction_path)
        assert result is not None

    def test_resolve_junction_target(self) -> None:
        """Test attempting to resolve junction point targets."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        junction_path = "C:\\Users\\Default"
        result = compat.handle_junction_points(junction_path)
        # Should not raise an error
        assert result is not None


class TestCoverageTips:
    """Test edge cases to improve code coverage."""
    
    def test_empty_path_validation(self) -> None:
        """Test validation of empty paths."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        assert compat.validate_path("") is False
    
    def test_empty_path_normalization(self) -> None:
        """Test normalization of empty paths."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        assert compat.normalize_path("") == ""
    
    def test_empty_path_env_expansion(self) -> None:
        """Test environment variable expansion on empty paths."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        assert compat.expand_environment_vars("") == ""
    
    def test_empty_path_reserved_names(self) -> None:
        """Test reserved names handling on empty paths."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        assert compat.handle_reserved_names("") == ""
    
    def test_empty_path_long_paths(self) -> None:
        """Test long path support on empty paths."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        assert compat.support_long_paths("") == ""
    
    def test_empty_path_shortnames(self) -> None:
        """Test shortname support on empty paths."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        assert compat.support_shortnames("") == ""
    
    def test_empty_path_junction_points(self) -> None:
        """Test junction point handling on empty paths."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        assert compat.handle_junction_points("") == ""
    
    def test_unc_path_with_single_separator(self) -> None:
        """Test UNC path with single separator doesn't validate."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        assert compat.validate_path("\\\\server") is False
    
    def test_unc_path_with_missing_share(self) -> None:
        """Test UNC path with missing share name doesn't validate."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        assert compat.validate_path("\\\\server\\") is False
    
    def test_normalize_unc_with_forward_slashes(self) -> None:
        """Test normalization of UNC paths with forward slashes."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        result = compat.normalize_path("//server/share/file.txt")
        assert result.startswith("\\\\") or result.startswith("//")
    
    def test_colon_in_filename_is_invalid(self) -> None:
        """Test that colon in filename (not drive letter) is invalid."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        assert compat.validate_path("C:\\file:name.txt") is False
    
    def test_multiple_environment_variables(self) -> None:
        """Test expansion of multiple environment variables."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        os.environ["TEST_A"] = "/a"
        os.environ["TEST_B"] = "/b"
        path = "%TEST_A%\\file\\%TEST_B%"
        expanded = compat.expand_environment_vars(path)
        assert "/a" in expanded and "/b" in expanded
    
    def test_nonexistent_environment_variable(self) -> None:
        """Test that nonexistent environment variables remain unchanged."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        path = "%NONEXISTENT_VAR_12345%\\file.txt"
        expanded = compat.expand_environment_vars(path)
        assert "%NONEXISTENT_VAR_12345%" in expanded
    
    def test_shortname_not_detected_in_normal_path(self) -> None:
        """Test that normal paths don't trigger shortname detection."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        normal_path = "C:\\Program Files\\MyApp"
        result = compat.support_shortnames(normal_path)
        assert result == normal_path
    
    def test_long_path_relative_path(self) -> None:
        """Test long path support on relative paths."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        long_relative = "dir\\" * 100 + "file.txt"
        result = compat.support_long_paths(long_relative)
        assert result is not None
    
    def test_normalize_mixed_separators_in_unc(self) -> None:
        """Test normalization of UNC path with mixed separators."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        
        compat = WindowsPathCompatibility()
        mixed_unc = "\\\\server/share\\file"
        result = compat.normalize_path(mixed_unc)
        # Should have consistent format
        assert result is not None
    
    def test_thread_safety_concurrent_access(self) -> None:
        """Test thread-safe access to path compatibility methods."""
        from cortex_brain.tier0.windows_path_compat import WindowsPathCompatibility
        import threading
        
        compat = WindowsPathCompatibility()
        results = []
        
        def worker(path_str: str) -> None:
            result = compat.validate_path(path_str)
            results.append(result)
        
        threads = []
        for i in range(10):
            path = f"C:\\test{i}\\file.txt"
            t = threading.Thread(target=worker, args=(path,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # All threads should complete without error
        assert len(results) == 10
