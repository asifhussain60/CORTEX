"""
Git pre-commit hook integration tests (smoke tests).
"""

import pytest
from pathlib import Path


class TestGitHookIntegration:
    """Test git hook integration."""
    
    def test_hook_validator_exists(self):
        """Should have GitHookValidator class."""
        from src.governance.git_hook_validator import GitHookValidator
        
        validator = GitHookValidator()
        assert validator is not None
    
    def test_can_validate_staged_files(self, tmp_path):
        """Should validate staged files list."""
        from src.governance.git_hook_validator import GitHookValidator
        
        validator = GitHookValidator()
        
        # Mock staged files
        staged = ["user_service.py", "userService.py"]
        results = validator.validate_files(staged)
        
        assert len(results) == 2
        assert results[0]["valid"] is True
        assert results[1]["valid"] is False
