"""
Tests for CORTEX setup .gitignore configuration.

Tests verify that setup operation properly manages .gitignore:
- Creates .gitignore if missing
- Appends CORTEX/ exclusion to existing .gitignore
- Detects existing CORTEX exclusions (avoids duplicates)
- Handles edge cases (no trailing newline, etc.)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.operations.setup import configure_gitignore


class TestSetupGitignore:
    """Test .gitignore configuration during setup."""
    
    @pytest.fixture
    def temp_project_root(self):
        """Create temporary project root directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_creates_gitignore_if_missing(self, temp_project_root):
        """Test creating new .gitignore with CORTEX exclusion."""
        # Arrange
        gitignore_path = temp_project_root / '.gitignore'
        assert not gitignore_path.exists()
        
        # Act
        success, message = configure_gitignore(temp_project_root)
        
        # Assert
        assert success is True
        assert "Created .gitignore" in message
        assert gitignore_path.exists()
        
        # Verify content
        content = gitignore_path.read_text()
        assert "CORTEX/" in content
        assert "CORTEX AI Assistant" in content
        assert "local only" in content.lower()
    
    def test_appends_to_existing_gitignore(self, temp_project_root):
        """Test appending CORTEX exclusion to existing .gitignore."""
        # Arrange
        gitignore_path = temp_project_root / '.gitignore'
        existing_content = """# Python
*.pyc
__pycache__/
.venv/
"""
        gitignore_path.write_text(existing_content)
        
        # Act
        success, message = configure_gitignore(temp_project_root)
        
        # Assert
        assert success is True
        assert "Added CORTEX/" in message
        
        # Verify content preserved + CORTEX added
        content = gitignore_path.read_text()
        assert "*.pyc" in content
        assert "__pycache__/" in content
        assert ".venv/" in content
        assert "CORTEX/" in content
        assert "CORTEX AI Assistant" in content
    
    def test_detects_existing_cortex_exclusion(self, temp_project_root):
        """Test detecting CORTEX already in .gitignore."""
        # Arrange
        gitignore_path = temp_project_root / '.gitignore'
        existing_content = """# Python
*.pyc

# CORTEX
CORTEX/
"""
        gitignore_path.write_text(existing_content)
        
        # Act
        success, message = configure_gitignore(temp_project_root)
        
        # Assert
        assert success is True
        assert "already contains" in message.lower()
        
        # Verify no duplicate added
        content = gitignore_path.read_text()
        assert content.count("CORTEX/") == 1
    
    def test_handles_no_trailing_newline(self, temp_project_root):
        """Test appending when existing file has no trailing newline."""
        # Arrange
        gitignore_path = temp_project_root / '.gitignore'
        existing_content = "*.pyc"  # No trailing newline
        gitignore_path.write_text(existing_content)
        
        # Act
        success, message = configure_gitignore(temp_project_root)
        
        # Assert
        assert success is True
        
        # Verify proper formatting
        content = gitignore_path.read_text()
        lines = content.split('\n')
        assert lines[0] == "*.pyc"
        assert lines[1] == ""  # Newline added before CORTEX section
        assert any("CORTEX/" in line for line in lines)
    
    def test_preserves_existing_comments(self, temp_project_root):
        """Test that existing comments and structure are preserved."""
        # Arrange
        gitignore_path = temp_project_root / '.gitignore'
        existing_content = """# Build outputs
dist/
build/

# IDE
.vscode/
.idea/
"""
        gitignore_path.write_text(existing_content)
        
        # Act
        success, message = configure_gitignore(temp_project_root)
        
        # Assert
        assert success is True
        
        content = gitignore_path.read_text()
        assert "# Build outputs" in content
        assert "dist/" in content
        assert "# IDE" in content
        assert ".vscode/" in content
        assert "CORTEX/" in content
    
    def test_handles_various_cortex_patterns(self, temp_project_root):
        """Test detecting CORTEX/ in various formats."""
        patterns = [
            "CORTEX/",
            "CORTEX/*",
            "/CORTEX/",
            "**/CORTEX/**",
        ]
        
        for pattern in patterns:
            # Arrange
            gitignore_path = temp_project_root / '.gitignore'
            gitignore_path.write_text(f"# Test\n{pattern}\n")
            
            # Act
            success, message = configure_gitignore(temp_project_root)
            
            # Assert
            assert success is True
            assert "already contains" in message.lower(), f"Failed for pattern: {pattern}"
            
            # Cleanup for next iteration
            gitignore_path.unlink()
    
    def test_error_handling_permission_denied(self, temp_project_root):
        """Test error handling when .gitignore is read-only."""
        # Arrange
        gitignore_path = temp_project_root / '.gitignore'
        gitignore_path.write_text("# Existing content")
        gitignore_path.chmod(0o444)  # Read-only
        
        # Act
        success, message = configure_gitignore(temp_project_root)
        
        # Assert
        assert success is False
        assert "Failed" in message
        
        # Cleanup
        gitignore_path.chmod(0o644)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
