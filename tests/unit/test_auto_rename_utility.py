"""
Auto-rename utility tests (simplified).

Tests basic rename functionality with safety features.
"""

import pytest
from pathlib import Path


class TestAutoRenameUtility:
    """Test auto-rename utility."""
    
    def test_can_rename_file(self, tmp_path):
        """Should rename file with invalid name."""
        from src.governance.auto_rename_utility import AutoRenameUtility
        
        # Create test file
        bad_file = tmp_path / "userService.py"
        bad_file.write_text("# test")
        
        utility = AutoRenameUtility()
        new_path = utility.rename(bad_file, dry_run=False)
        
        assert new_path.name == "user_service.py"
        assert new_path.exists()
        assert not bad_file.exists()
    
    def test_dry_run_mode(self, tmp_path):
        """Should not actually rename in dry-run mode."""
        from src.governance.auto_rename_utility import AutoRenameUtility
        
        bad_file = tmp_path / "userService.py"
        bad_file.write_text("# test")
        
        utility = AutoRenameUtility()
        suggested = utility.rename(bad_file, dry_run=True)
        
        # Original file should still exist
        assert bad_file.exists()
        assert suggested.name == "user_service.py"
    
    def test_detects_collision(self, tmp_path):
        """Should detect naming collisions."""
        from src.governance.auto_rename_utility import AutoRenameUtility
        
        # Create both files
        bad_file = tmp_path / "userService.py"
        bad_file.write_text("# bad")
        
        good_file = tmp_path / "user_service.py"
        good_file.write_text("# good")
        
        utility = AutoRenameUtility()
        
        # Should detect collision
        assert utility.would_collide(bad_file) is True
    
    def test_batch_rename(self, tmp_path):
        """Should rename multiple files."""
        from src.governance.auto_rename_utility import AutoRenameUtility
        
        # Create multiple invalid files
        files = []
        for name in ["userService.py", "testUser.py", "apiClient.py"]:
            f = tmp_path / name
            f.write_text("# test")
            files.append(f)
        
        utility = AutoRenameUtility()
        results = utility.batch_rename(files, dry_run=False)
        
        assert len(results) == 3
        assert all(r["success"] for r in results.values())
    
    def test_skips_valid_files(self, tmp_path):
        """Should skip files that are already valid."""
        from src.governance.auto_rename_utility import AutoRenameUtility
        
        good_file = tmp_path / "user_service.py"
        good_file.write_text("# test")
        
        utility = AutoRenameUtility()
        result = utility.rename(good_file, dry_run=False)
        
        # Should return same path (no rename needed)
        assert result == good_file
