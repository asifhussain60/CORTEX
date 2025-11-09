"""Tests for ErrorCorrector validators."""

import pytest
from pathlib import Path
from src.cortex_agents.error_corrector.validators import (
    PathValidator,
    FixValidator
)


class TestPathValidator:
    """Tests for path validator."""
    
    def test_protected_path_detection(self):
        validator = PathValidator([
            "CORTEX/tests",
            "CORTEX/src/cortex_agents",
            "cortex-brain"
        ])
        
        # Protected paths
        assert validator.is_protected("CORTEX/tests/test_file.py") is True
        assert validator.is_protected("CORTEX/src/cortex_agents/error_corrector.py") is True
        assert validator.is_protected("cortex-brain/tier1/test.db") is True
        
        # Non-protected paths
        assert validator.is_protected("src/myapp/main.py") is False
        assert validator.is_protected("application/models.py") is False
    
    def test_empty_protected_paths(self):
        validator = PathValidator([])
        assert validator.is_protected("any/file.py") is False
    
    def test_relative_path_resolution(self):
        validator = PathValidator(["CORTEX/tests"])
        # Different ways to refer to same path
        assert validator.is_protected("CORTEX/tests/test_module.py") is True


class TestFixValidator:
    """Tests for fix validator."""
    
    def test_validate_successful_fix(self):
        validator = FixValidator()
        fix_result = {
            "success": True,
            "message": "Fixed indentation",
            "changes": ["Convert tabs to spaces"],
            "fixed_content": "def test():\n    pass"
        }
        assert validator.validate(fix_result) is True
    
    def test_validate_fix_with_changes_only(self):
        validator = FixValidator()
        fix_result = {
            "success": True,
            "message": "Added import",
            "changes": ["from pathlib import Path"]
        }
        assert validator.validate(fix_result) is True
    
    def test_validate_failed_fix(self):
        validator = FixValidator()
        fix_result = {
            "success": False,
            "message": "Could not fix"
        }
        assert validator.validate(fix_result) is False
    
    def test_validate_fix_missing_changes(self):
        validator = FixValidator()
        fix_result = {
            "success": True,
            "message": "Fixed"
            # No changes or fixed_content
        }
        assert validator.validate(fix_result) is False
    
    def test_validate_invalid_fixed_content_type(self):
        validator = FixValidator()
        fix_result = {
            "success": True,
            "message": "Fixed",
            "fixed_content": 123  # Should be string
        }
        assert validator.validate(fix_result) is False
    
    def test_is_safe_for_successful_fix(self):
        validator = FixValidator()
        fix_result = {
            "success": True,
            "message": "Fixed",
            "changes": ["Some change"]
        }
        parsed_error = {"type": "syntax"}
        assert validator.is_safe(fix_result, parsed_error) is True
    
    def test_is_safe_for_invalid_fix(self):
        validator = FixValidator()
        fix_result = {"success": False}
        parsed_error = {}
        assert validator.is_safe(fix_result, parsed_error) is False
