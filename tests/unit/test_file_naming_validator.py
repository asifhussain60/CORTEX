"""
File naming validator tests.

Tests validation rules for file naming conventions:
- snake_case for Python files (.py)
- kebab-case for markdown files (.md)
- No spaces in any filenames
- Max length 100 characters
- Allowed characters: [a-z0-9_-.]
"""

import pytest
from pathlib import Path


class TestFileNameValidator:
    """Test file name validation rules."""
    
    def test_valid_python_snake_case(self):
        """Should accept valid snake_case Python files."""
        from src.governance.file_naming_validator import FileNameValidator
        
        validator = FileNameValidator()
        
        valid_names = [
            "user_service.py",
            "test_user_service.py",
            "user_profile_storage.py",
            "plan_metadata.py",
            "__init__.py"
        ]
        
        for filename in valid_names:
            assert validator.validate(filename) is True, f"{filename} should be valid"
    
    def test_invalid_python_camelcase(self):
        """Should reject camelCase Python files."""
        from src.governance.file_naming_validator import FileNameValidator
        
        validator = FileNameValidator()
        
        invalid_names = [
            "userService.py",
            "UserService.py",
            "testUserService.py"
        ]
        
        for filename in invalid_names:
            assert validator.validate(filename) is False, f"{filename} should be invalid"
    
    def test_valid_markdown_kebab_case(self):
        """Should accept valid kebab-case markdown files."""
        from src.governance.file_naming_validator import FileNameValidator
        
        validator = FileNameValidator()
        
        valid_names = [
            "README.md",
            "shared-environment-setup.md",
            "user-profiling-guide.md",
            "plan-management-guide.md"
        ]
        
        for filename in valid_names:
            assert validator.validate(filename) is True, f"{filename} should be valid"
    
    def test_invalid_markdown_underscore(self):
        """Should reject underscore markdown files."""
        from src.governance.file_naming_validator import FileNameValidator
        
        validator = FileNameValidator()
        
        invalid_names = [
            "user_profile_guide.md",
            "shared_environment_setup.md",
            "plan_management.md"
        ]
        
        for filename in invalid_names:
            assert validator.validate(filename) is False, f"{filename} should be invalid"
    
    def test_rejects_spaces_in_filename(self):
        """Should reject filenames with spaces."""
        from src.governance.file_naming_validator import FileNameValidator
        
        validator = FileNameValidator()
        
        invalid_names = [
            "user service.py",
            "test file.md",
            "my document.txt"
        ]
        
        for filename in invalid_names:
            assert validator.validate(filename) is False, f"{filename} should be invalid (spaces)"
    
    def test_rejects_special_characters(self):
        """Should reject filenames with special characters."""
        from src.governance.file_naming_validator import FileNameValidator
        
        validator = FileNameValidator()
        
        invalid_names = [
            "user@service.py",
            "test#file.md",
            "file$name.txt",
            "file%name.py"
        ]
        
        for filename in invalid_names:
            assert validator.validate(filename) is False, f"{filename} should be invalid (special chars)"
    
    def test_rejects_too_long_filenames(self):
        """Should reject filenames exceeding 100 characters."""
        from src.governance.file_naming_validator import FileNameValidator
        
        validator = FileNameValidator()
        
        # 101 characters (including .py)
        long_name = "a" * 98 + ".py"  # 98 + 3 = 101
        assert len(long_name) == 101
        assert validator.validate(long_name) is False, "Should reject filenames >100 chars"
    
    def test_accepts_max_length_filenames(self):
        """Should accept filenames at exactly 100 characters."""
        from src.governance.file_naming_validator import FileNameValidator
        
        validator = FileNameValidator()
        
        # Exactly 100 characters
        max_name = "a" * 97 + ".py"  # 97 + 3 = 100
        assert len(max_name) == 100
        assert validator.validate(max_name) is True, "Should accept 100 char filenames"
    
    def test_get_violations_returns_reasons(self):
        """Should return specific violation reasons."""
        from src.governance.file_naming_validator import FileNameValidator
        
        validator = FileNameValidator()
        
        # Test various violations
        violations = validator.get_violations("User Service.py")
        
        assert len(violations) > 0
        assert any("space" in v.lower() for v in violations)
        assert any("camelcase" in v.lower() or "snake_case" in v.lower() for v in violations)
    
    def test_supports_path_objects(self):
        """Should accept Path objects in addition to strings."""
        from src.governance.file_naming_validator import FileNameValidator
        
        validator = FileNameValidator()
        
        # Test with Path object
        path = Path("user_service.py")
        assert validator.validate(path) is True
        
        # Test with string
        assert validator.validate("user_service.py") is True
    
    def test_validates_only_filename_not_full_path(self):
        """Should validate only the filename, ignoring directory path."""
        from src.governance.file_naming_validator import FileNameValidator
        
        validator = FileNameValidator()
        
        # Full path with valid filename
        full_path = "/Users/test/My Project/valid_file.py"
        assert validator.validate(full_path) is True, "Should validate only filename, not full path"
        
        # Full path with invalid filename
        invalid_path = "/Users/test/project/Invalid File.py"
        assert validator.validate(invalid_path) is False
    
    def test_allowed_exceptions_list(self):
        """Should allow common exception filenames."""
        from src.governance.file_naming_validator import FileNameValidator
        
        validator = FileNameValidator()
        
        exceptions = [
            "LICENSE",
            "VERSION",
            "README.md",
            "CHANGELOG.md",
            "Makefile",
            ".gitignore"
        ]
        
        for filename in exceptions:
            assert validator.validate(filename) is True, f"{filename} should be allowed exception"
