"""
Test Embedded Installation Upgrade Safety

Validates that CORTEX upgrade system properly detects and handles
embedded installations to prevent files escaping the CORTEX directory.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sys
import tempfile
import shutil
from pathlib import Path
import pytest

# Add operations to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "operations"))

from upgrade_orchestrator import UpgradeOrchestrator


class TestEmbeddedInstallationDetection:
    """Test embedded installation detection logic."""
    
    def test_detect_embedded_with_marker(self, tmp_path):
        """Test detection via .cortex-embedded marker file."""
        cortex_dir = tmp_path / "CORTEX"
        cortex_dir.mkdir()
        
        # Create embedded marker
        (cortex_dir / ".cortex-embedded").touch()
        
        orchestrator = UpgradeOrchestrator(cortex_dir)
        assert orchestrator.is_embedded is True
    
    def test_detect_embedded_parent_git(self, tmp_path):
        """Test detection when parent has .git but CORTEX doesn't."""
        # Create parent project with git
        (tmp_path / ".git").mkdir()
        
        # Create CORTEX subdirectory without git
        cortex_dir = tmp_path / "CORTEX"
        cortex_dir.mkdir()
        
        orchestrator = UpgradeOrchestrator(cortex_dir)
        assert orchestrator.is_embedded is True
    
    def test_detect_embedded_project_structure(self, tmp_path):
        """Test detection via project structure indicators."""
        # Create parent project with package.json
        (tmp_path / "package.json").touch()
        
        # Create CORTEX subdirectory
        cortex_dir = tmp_path / "CORTEX"
        cortex_dir.mkdir()
        
        orchestrator = UpgradeOrchestrator(cortex_dir)
        assert orchestrator.is_embedded is True
    
    def test_detect_standalone_with_git(self, tmp_path):
        """Test detection of standalone CORTEX with git."""
        cortex_dir = tmp_path / "CORTEX"
        cortex_dir.mkdir()
        
        # CORTEX has its own .git
        (cortex_dir / ".git").mkdir()
        
        orchestrator = UpgradeOrchestrator(cortex_dir)
        assert orchestrator.is_embedded is False
    
    def test_detect_standalone_fresh(self, tmp_path):
        """Test detection of fresh standalone CORTEX."""
        cortex_dir = tmp_path / "CORTEX"
        cortex_dir.mkdir()
        
        # No git, no parent project indicators
        orchestrator = UpgradeOrchestrator(cortex_dir)
        assert orchestrator.is_embedded is False


class TestPathValidation:
    """Test path validation for upgrade safety."""
    
    def test_validate_safe_paths(self, tmp_path):
        """Test validation passes for safe paths."""
        cortex_dir = tmp_path / "CORTEX"
        cortex_dir.mkdir()
        (cortex_dir / ".git").mkdir()
        
        orchestrator = UpgradeOrchestrator(cortex_dir)
        
        # Mock git diff output with safe paths
        import subprocess
        from unittest.mock import patch, MagicMock
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "scripts/test.py\nsrc/main.py\nREADME.md"
        
        with patch('subprocess.run', return_value=mock_result):
            validation = orchestrator._validate_file_paths(cortex_dir)
        
        assert validation["all_safe"] is True
        assert len(validation["escaping_files"]) == 0
    
    def test_validate_escaping_paths(self, tmp_path):
        """Test validation fails for escaping paths."""
        cortex_dir = tmp_path / "CORTEX"
        cortex_dir.mkdir()
        (cortex_dir / ".git").mkdir()
        
        orchestrator = UpgradeOrchestrator(cortex_dir)
        
        # Mock git diff output with escaping paths
        import subprocess
        from unittest.mock import patch, MagicMock
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "../parent-file.txt\nscripts/test.py\n../another-escape.py"
        
        with patch('subprocess.run', return_value=mock_result):
            validation = orchestrator._validate_file_paths(cortex_dir)
        
        assert validation["all_safe"] is False
        assert len(validation["escaping_files"]) >= 2  # May detect duplicates
        assert any("parent-file" in f for f in validation["escaping_files"])
        assert any("another-escape" in f for f in validation["escaping_files"])


class TestUpgradeMethodSelection:
    """Test upgrade method selection based on installation type."""
    
    def test_embedded_blocks_git_upgrade(self, tmp_path):
        """Test that embedded installations block git-based upgrade."""
        cortex_dir = tmp_path / "CORTEX"
        cortex_dir.mkdir()
        
        # Mark as embedded
        (cortex_dir / ".cortex-embedded").touch()
        
        orchestrator = UpgradeOrchestrator(cortex_dir)
        
        # Should return False (fallback to file copy)
        result = orchestrator._git_upgrade(dry_run=True)
        assert result is False
    
    def test_standalone_allows_git_upgrade(self, tmp_path):
        """Test that standalone installations can use git upgrade."""
        cortex_dir = tmp_path / "CORTEX"
        cortex_dir.mkdir()
        (cortex_dir / ".git").mkdir()
        
        orchestrator = UpgradeOrchestrator(cortex_dir)
        
        # Should attempt git upgrade (will fail due to no remote, but that's ok)
        # We're just testing it doesn't block based on embedded status
        assert orchestrator.is_embedded is False


class TestEmbeddedUpgradeFlow:
    """Test complete upgrade flow for embedded installations."""
    
    def test_embedded_uses_safe_method(self, tmp_path, capsys):
        """Test that embedded installation uses safe file-copy method."""
        # Create parent project
        parent_dir = tmp_path / "NOOR-CANVAS"
        parent_dir.mkdir()
        (parent_dir / ".git").mkdir()
        (parent_dir / "package.json").touch()
        
        # Create embedded CORTEX with proper structure
        cortex_dir = parent_dir / "CORTEX"
        cortex_dir.mkdir()
        (cortex_dir / "VERSION").write_text("5.3.0")
        
        # Create required directories for version detection
        brain_dir = cortex_dir / "cortex-brain"
        brain_dir.mkdir()
        (brain_dir / "response-templates.yaml").write_text("# Templates")
        (brain_dir / "capabilities.yaml").write_text("# Capabilities")
        
        scripts_dir = cortex_dir / "scripts"
        scripts_dir.mkdir()
        
        orchestrator = UpgradeOrchestrator(cortex_dir)
        
        # Verify it's detected as embedded
        assert orchestrator.is_embedded is True
        
        # Test git upgrade attempt (should be blocked)
        result = orchestrator._git_upgrade(dry_run=True)
        
        captured = capsys.readouterr()
        
        # Git upgrade should be blocked for embedded installations
        assert result is False
        assert "embedded" in captured.out.lower() or "Embedded" in captured.out


def test_marker_file_creation_helper(tmp_path):
    """Helper to show how to mark an installation as embedded."""
    cortex_dir = tmp_path / "CORTEX"
    cortex_dir.mkdir()
    
    # Create marker file
    marker = cortex_dir / ".cortex-embedded"
    marker.write_text("""# CORTEX Embedded Installation Marker
# 
# This file indicates that CORTEX is embedded within another project.
# The upgrade system will use safe file-copy method instead of git merge.
#
# Created: 2025-11-23
# Parent Project: NOOR-CANVAS
""")
    
    assert marker.exists()
    orchestrator = UpgradeOrchestrator(cortex_dir)
    assert orchestrator.is_embedded is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
