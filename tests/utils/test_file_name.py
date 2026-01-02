"""
Comprehensive tests for filename validation utility.

Tests cover all validation rules, edge cases, and suggestion algorithms.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.utils.file_name import (
    FileNameValidator,
    validate_filename,
    suggest_filename,
    sanitize_filename
)


class TestValidateFilename:
    """Test filename validation logic."""
    
    def test_valid_simple_name(self):
        """Valid single-word lowercase name."""
        is_valid, error = validate_filename("simple")
        assert is_valid is True
        assert error == ""
    
    def test_valid_hyphenated_name(self):
        """Valid multi-word kebab-case name."""
        is_valid, error = validate_filename("plan-orch-v5")
        assert is_valid is True
        assert error == ""
    
    def test_valid_with_numbers(self):
        """Valid name with numbers."""
        is_valid, error = validate_filename("test-123-file")
        assert is_valid is True
        assert error == ""
    
    def test_empty_name(self):
        """Empty filename is invalid."""
        is_valid, error = validate_filename("")
        assert is_valid is False
        assert "cannot be empty" in error.lower()
    
    def test_too_long(self):
        """Name exceeding max length."""
        is_valid, error = validate_filename("this-is-way-too-long-name")
        assert is_valid is False
        assert "exceeds 20 characters" in error
    
    def test_custom_max_length(self):
        """Custom max length parameter."""
        is_valid, error = validate_filename("short", max_len=3)
        assert is_valid is False
        assert "exceeds 3 characters" in error
    
    def test_uppercase_letters(self):
        """Uppercase letters are invalid."""
        is_valid, error = validate_filename("MyFile")
        assert is_valid is False
        assert "kebab-case" in error
    
    def test_underscores(self):
        """Underscores should be hyphens."""
        is_valid, error = validate_filename("my_file")
        assert is_valid is False
        assert "hyphens (-) instead of underscores" in error
    
    def test_special_characters(self):
        """Special characters are invalid."""
        is_valid, error = validate_filename("my@file")
        assert is_valid is False
        assert "Invalid format" in error
    
    def test_leading_hyphen(self):
        """Leading hyphen is invalid."""
        is_valid, error = validate_filename("-myfile")
        assert is_valid is False
        assert "Cannot start or end with hyphen" in error
    
    def test_trailing_hyphen(self):
        """Trailing hyphen is invalid."""
        is_valid, error = validate_filename("myfile-")
        assert is_valid is False
        assert "Cannot start or end with hyphen" in error
    
    def test_consecutive_hyphens(self):
        """Consecutive hyphens are invalid."""
        is_valid, error = validate_filename("my--file")
        assert is_valid is False
        assert "consecutive hyphens" in error
    
    def test_spaces(self):
        """Spaces are invalid."""
        is_valid, error = validate_filename("my file")
        assert is_valid is False
        assert "Invalid format" in error
    
    def test_at_max_length(self):
        """Name exactly at max length."""
        name = "a" * 20
        is_valid, error = validate_filename(name)
        assert is_valid is True
        assert error == ""


class TestSuggestFilename:
    """Test filename suggestion algorithm."""
    
    def test_convert_uppercase(self):
        """Convert uppercase to lowercase."""
        result = suggest_filename("MyFile")
        assert result == "myfile"
    
    def test_replace_underscores(self):
        """Replace underscores with hyphens."""
        result = suggest_filename("my_file_name")
        assert result == "my-file-name"
    
    def test_replace_spaces(self):
        """Replace spaces with hyphens."""
        result = suggest_filename("my file name")
        assert result == "my-file-name"
    
    def test_remove_special_chars(self):
        """Remove invalid special characters."""
        result = suggest_filename("my@file#name!")
        assert result == "myfilename"
    
    def test_consecutive_hyphens_collapsed(self):
        """Collapse consecutive hyphens."""
        result = suggest_filename("my---file---name")
        assert result == "my-file-name"
    
    def test_trim_hyphens(self):
        """Remove leading/trailing hyphens."""
        result = suggest_filename("-myfile-")
        assert result == "myfile"
    
    def test_abbreviate_orchestrator(self):
        """Abbreviate 'orchestrator' to 'orch'."""
        result = suggest_filename("planning-orchestrator-v5")
        assert "orch" in result
        assert len(result) <= 20
    
    def test_abbreviate_database(self):
        """Abbreviate 'database' to 'db'."""
        result = suggest_filename("planning-database-manager")
        assert "db" in result
    
    def test_abbreviate_version(self):
        """Abbreviate 'version' to 'v'."""
        result = suggest_filename("orchestrator-version-5")
        assert result == "orch-v-5"
    
    def test_very_long_name(self):
        """Handle extremely long name."""
        long_name = "this_is_an_extremely_long_filename_that_needs_serious_shortening"
        result = suggest_filename(long_name)
        assert len(result) <= 20
        assert result.count('--') == 0  # No consecutive hyphens
    
    def test_complex_abbreviation(self):
        """Complex name with multiple abbreviations."""
        result = suggest_filename("planning_orchestrator_implementation_version_5")
        assert len(result) <= 20
        assert "orch" in result or "impl" in result
    
    def test_preserve_short_valid(self):
        """Preserve already valid short names."""
        result = suggest_filename("valid-name")
        assert result == "valid-name"
    
    def test_custom_max_length(self):
        """Respect custom max length."""
        result = suggest_filename("toolongname", max_len=5)
        assert len(result) <= 5


class TestSanitizeFilename:
    """Test filename sanitization."""
    
    def test_already_valid(self):
        """Return valid names unchanged."""
        name = "valid-name"
        result = sanitize_filename(name)
        assert result == name
    
    def test_sanitize_invalid(self):
        """Sanitize invalid name."""
        result = sanitize_filename("My_Invalid@Name!")
        is_valid, _ = validate_filename(result)
        assert is_valid is True
    
    def test_sanitize_too_long(self):
        """Sanitize overly long name."""
        long_name = "this-is-way-too-long-for-the-standard"
        result = sanitize_filename(long_name)
        is_valid, _ = validate_filename(result)
        assert is_valid is True
        assert len(result) <= 20


class TestValidatePath:
    """Test path validation."""
    
    def test_valid_path(self):
        """Valid file path."""
        is_valid, error = FileNameValidator.validate_path("src/utils/valid-name.py")
        assert is_valid is True
        assert error == ""
    
    def test_invalid_path_stem(self):
        """Invalid filename in path."""
        is_valid, error = FileNameValidator.validate_path("src/utils/Invalid_Name.py")
        assert is_valid is False
    
    def test_path_too_long(self):
        """Path with filename exceeding max length."""
        is_valid, error = FileNameValidator.validate_path("src/this-is-too-long-filename.py")
        assert is_valid is False
        assert "exceeds" in error
    
    def test_windows_path(self):
        """Windows-style path."""
        is_valid, error = FileNameValidator.validate_path(r"C:\projects\valid-name.py")
        assert is_valid is True


class TestSuggestPath:
    """Test path suggestion."""
    
    def test_suggest_valid_path(self):
        """Suggest corrected path."""
        original = "src/utils/Invalid_Filename.py"
        suggested = FileNameValidator.suggest_path(original)
        
        path = Path(suggested)
        stem = path.stem
        is_valid, _ = validate_filename(stem)
        
        assert is_valid is True
        assert "src" in suggested
        assert "utils" in suggested
        assert suggested.endswith(".py")
    
    def test_preserve_directory(self):
        """Preserve directory structure."""
        original = "cortex-brain/config/Long_Invalid_Name.yaml"
        suggested = FileNameValidator.suggest_path(original)
        
        assert "cortex-brain" in suggested
        assert "config" in suggested
        assert suggested.endswith(".yaml")
    
    def test_preserve_extension(self):
        """Preserve file extension."""
        original = "my_file.json"
        suggested = FileNameValidator.suggest_path(original)
        assert suggested.endswith(".json")


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_single_character(self):
        """Single character name."""
        is_valid, error = validate_filename("a")
        assert is_valid is True
    
    def test_all_numbers(self):
        """Name with only numbers."""
        is_valid, error = validate_filename("12345")
        assert is_valid is True
    
    def test_mixed_numbers_letters(self):
        """Mixed numbers and letters."""
        is_valid, error = validate_filename("abc123def456")
        assert is_valid is True
    
    def test_suggest_empty(self):
        """Suggest on empty string."""
        result = suggest_filename("")
        # Should return something valid or empty
        if result:
            is_valid, _ = validate_filename(result)
            assert is_valid is True
    
    def test_suggest_only_special_chars(self):
        """Suggest on string with only special characters."""
        result = suggest_filename("@#$%^&*()")
        # Should return empty or valid
        if result:
            is_valid, _ = validate_filename(result)
            assert is_valid is True
    
    def test_unicode_characters(self):
        """Handle unicode characters."""
        result = suggest_filename("café-résumé")
        is_valid, _ = validate_filename(result)
        assert is_valid is True
        # Unicode should be stripped
        assert "café" not in result


class TestIntegrationScenarios:
    """Test real-world integration scenarios."""
    
    def test_orchestrator_naming(self):
        """Typical orchestrator filename."""
        original = "Planning_Orchestrator_V5"
        suggested = suggest_filename(original)
        
        is_valid, _ = validate_filename(suggested)
        assert is_valid is True
        assert len(suggested) <= 20
        assert "plan" in suggested or "orch" in suggested
    
    def test_database_file_naming(self):
        """Database file naming."""
        original = "planning_state_database"
        suggested = suggest_filename(original)
        
        is_valid, _ = validate_filename(suggested)
        assert is_valid is True
        assert "db" in suggested or "state" in suggested
    
    def test_config_file_naming(self):
        """Configuration file naming."""
        original = "MCP_Server_Configuration"
        suggested = suggest_filename(original)
        
        is_valid, _ = validate_filename(suggested)
        assert is_valid is True
        assert "mcp" in suggested
    
    def test_test_file_naming(self):
        """Test file naming convention."""
        original = "test_planning_orchestrator_v5"
        suggested = suggest_filename(original)
        
        is_valid, _ = validate_filename(suggested)
        assert is_valid is True
        assert suggested.startswith("test-")


class TestConvenienceFunctions:
    """Test module-level convenience functions."""
    
    def test_module_validate(self):
        """Module-level validate function."""
        is_valid, error = validate_filename("valid-name")
        assert is_valid is True
    
    def test_module_suggest(self):
        """Module-level suggest function."""
        result = suggest_filename("Invalid_Name")
        is_valid, _ = validate_filename(result)
        assert is_valid is True
    
    def test_module_sanitize(self):
        """Module-level sanitize function."""
        result = sanitize_filename("My@File!")
        is_valid, _ = validate_filename(result)
        assert is_valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
