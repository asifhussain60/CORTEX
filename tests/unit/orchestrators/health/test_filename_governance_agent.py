"""Tests for Filename Governance Agent

Author: CORTEX Framework
Created: 2026-02-17
"""

import tempfile
from pathlib import Path
import pytest

from cortex.orchestrators.health.agents.filename_governance_agent import (
    FilenameGovernanceAgent,
)
from cortex.orchestrators.health.agents.base_agent import HealthIssueSeverity, HealthIssueCategory


class TestFilenameGovernanceAgent:
    """Test suite for FilenameGovernanceAgent."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            yield workspace
    
    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        agent = FilenameGovernanceAgent()
        
        assert agent.name == "FilenameGovernanceAgent"
        assert agent.is_enabled()
        assert "__init__.py" in agent.exceptions
        assert "__main__.py" in agent.exceptions
    
    def test_detects_screaming_case(self, temp_workspace):
        """Test detects SCREAMING_CASE Python files."""
        agent = FilenameGovernanceAgent()
        
        # Create SCREAMING_CASE file
        screaming_file = temp_workspace / "MY_FEATURE.py"
        screaming_file.write_text("# Module")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 1
        assert result.issues[0].category == HealthIssueCategory.CONFIGURATION
        assert result.issues[0].severity == HealthIssueSeverity.HIGH
        assert "CORE-028" in result.issues[0].description
        assert "MY_FEATURE" in str(result.issues[0].file_path)
    
    def test_allows_snake_case(self, temp_workspace):
        """Test allows snake_case filenames."""
        agent = FilenameGovernanceAgent()
        
        # Create snake_case file
        snake_file = temp_workspace / "my_module.py"
        snake_file.write_text("# Module")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 0
    
    def test_allows_init_py(self, temp_workspace):
        """Test allows __init__.py exception."""
        agent = FilenameGovernanceAgent()
        
        # Create __init__.py
        init_file = temp_workspace / "__init__.py"
        init_file.write_text("# Init")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 0
    
    def test_allows_main_py(self, temp_workspace):
        """Test allows __main__.py exception."""
        agent = FilenameGovernanceAgent()
        
        # Create __main__.py
        main_file = temp_workspace / "__main__.py"
        main_file.write_text("# Main")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 0
    
    def test_detects_multiple_violations(self, temp_workspace):
        """Test detects multiple SCREAMING_CASE files."""
        agent = FilenameGovernanceAgent()
        
        # Create multiple violations
        (temp_workspace / "FEATURE_A.py").write_text("# Feature A")
        (temp_workspace / "HELPER_UTILS.py").write_text("# Utils")
        (temp_workspace / "CONFIG_LOADER.py").write_text("# Config")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 3
        assert all(issue.severity == HealthIssueSeverity.HIGH for issue in result.issues)
    
    def test_recommendation_kebab_case(self, temp_workspace):
        """Test recommendation suggests kebab-case conversion."""
        agent = FilenameGovernanceAgent()
        
        # Create SCREAMING_CASE file
        (temp_workspace / "MY_FEATURE.py").write_text("# Module")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 1
        assert "my-feature.py" in result.issues[0].suggested_fix
    
    def test_skips_venv_directory(self, temp_workspace):
        """Test skips .venv directory."""
        agent = FilenameGovernanceAgent()
        
        # Create file in .venv
        venv_dir = temp_workspace / ".venv" / "lib"
        venv_dir.mkdir(parents=True)
        (venv_dir / "SOME_LIB.py").write_text("# Lib")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 0
    
    def test_skips_archives(self, temp_workspace):
        """Test skips _archives directory."""
        agent = FilenameGovernanceAgent()
        
        # Create file in _archives
        archives_dir = temp_workspace / "_archives"
        archives_dir.mkdir(parents=True)
        (archives_dir / "OLD_CODE.py").write_text("# Old")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 0
    
    def test_to_kebab_case_conversion(self):
        """Test SCREAMING_CASE to kebab-case conversion."""
        agent = FilenameGovernanceAgent()
        
        assert agent._to_kebab_case("MY_FEATURE") == "my-feature"
        assert agent._to_kebab_case("HELPER_UTILS") == "helper-utils"
        assert agent._to_kebab_case("CONFIG") == "config"
    
    def test_minimum_length_pattern(self, temp_workspace):
        """Test pattern requires minimum 5 uppercase chars."""
        agent = FilenameGovernanceAgent()
        
        # Create files with different lengths
        (temp_workspace / "ABC.py").write_text("# Short")  # Too short
        (temp_workspace / "ABCDE.py").write_text("# Long enough")
        
        result = agent.check(temp_workspace)
        
        # Only ABCDE.py should be flagged (5+ chars)
        assert len(result.issues) == 1
        assert "ABCDE.py" in str(result.issues[0].file_path)
    
    def test_nested_directory_scan(self, temp_workspace):
        """Test scans nested directories."""
        agent = FilenameGovernanceAgent()
        
        # Create nested structure
        nested = temp_workspace / "src" / "features"
        nested.mkdir(parents=True)
        (nested / "MY_FEATURE.py").write_text("# Feature")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 1
        assert "MY_FEATURE.py" in str(result.issues[0].file_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
