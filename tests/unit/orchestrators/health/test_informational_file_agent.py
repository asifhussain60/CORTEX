"""Tests for Informational File Agent

Author: CORTEX Framework
Created: 2026-02-17
"""

import tempfile
from pathlib import Path
import pytest

from cortex.orchestrators.health.agents.informational_file_agent import (
    InformationalFileAgent,
)
from cortex.orchestrators.health.agents.base_agent import HealthIssueSeverity, HealthIssueCategory


class TestInformationalFileAgent:
    """Test suite for InformationalFileAgent."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            yield workspace
    
    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        agent = InformationalFileAgent()
        
        assert agent.name == "InformationalFileAgent"
        assert agent.is_enabled()
        assert ".md" in agent.extensions
        assert ".log" in agent.extensions
        assert ".txt" in agent.extensions
    
    def test_detects_markdown_drift(self, temp_workspace):
        """Test detects .md files outside allowed directories."""
        agent = InformationalFileAgent()
        
        # Create drifting markdown file
        drift_file = temp_workspace / "straggler.md"
        drift_file.write_text("# Straggling markdown")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 1
        assert result.issues[0].category == HealthIssueCategory.PATH_DRIFT
        assert result.issues[0].severity == HealthIssueSeverity.MEDIUM
        assert "straggler.md" in str(result.issues[0].file_path)
    
    def test_allows_readme(self, temp_workspace):
        """Test allows root README.md."""
        agent = InformationalFileAgent()
        
        # Create README.md
        readme = temp_workspace / "README.md"
        readme.write_text("# Project")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 0
    
    def test_allows_github_prompts(self, temp_workspace):
        """Test allows .github/prompts/*.md."""
        agent = InformationalFileAgent()
        
        # Create .github/prompts/test.md
        prompts_dir = temp_workspace / ".github" / "prompts"
        prompts_dir.mkdir(parents=True)
        (prompts_dir / "test.md").write_text("# Prompt")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 0
    
    def test_allows_workspaces_exception(self, temp_workspace):
        """Test allows _workspaces/*.md (EXCEPTION)."""
        agent = InformationalFileAgent()
        
        # Create _workspaces/.chats/chat.md
        workspaces_dir = temp_workspace / "_workspaces" / ".chats"
        workspaces_dir.mkdir(parents=True)
        (workspaces_dir / "chat.md").write_text("# Chat")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 0
    
    def test_detects_log_files(self, temp_workspace):
        """Test detects .log files."""
        agent = InformationalFileAgent()
        
        # Create straggling log file
        log_file = temp_workspace / "debug.log"
        log_file.write_text("Debug output")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 1
        assert result.issues[0].category == HealthIssueCategory.PATH_DRIFT
        assert ".log" in result.issues[0].description
    
    def test_detects_txt_files(self, temp_workspace):
        """Test detects .txt files (except config)."""
        agent = InformationalFileAgent()
        
        # Create straggling txt file
        txt_file = temp_workspace / "notes.txt"
        txt_file.write_text("Some notes")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 1
        assert result.issues[0].category == HealthIssueCategory.PATH_DRIFT
    
    def test_allows_requirements_txt(self, temp_workspace):
        """Test allows requirements.txt configuration file."""
        agent = InformationalFileAgent()
        
        # Create requirements.txt
        req_file = temp_workspace / "requirements.txt"
        req_file.write_text("pytest==7.4.0")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 0
    
    def test_detects_multiple_drifts(self, temp_workspace):
        """Test detects multiple drifting files."""
        agent = InformationalFileAgent()
        
        # Create multiple drifts
        (temp_workspace / "notes.md").write_text("# Notes")
        (temp_workspace / "debug.log").write_text("Debug")
        (temp_workspace / "temp.txt").write_text("Temp")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 3
        assert result.files_scanned >= 3
    
    def test_allows_cortex_docs(self, temp_workspace):
        """Test allows cortex-docs/*.md."""
        agent = InformationalFileAgent()
        
        # Create cortex-docs/guide.md
        docs_dir = temp_workspace / "cortex-docs" / "guides"
        docs_dir.mkdir(parents=True)
        (docs_dir / "guide.md").write_text("# Guide")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 0
    
    def test_recommendation_format(self, temp_workspace):
        """Test recommendation provides actionable guidance."""
        agent = InformationalFileAgent()
        
        # Create drifting file
        (temp_workspace / "straggler.md").write_text("# Straggler")
        
        result = agent.check(temp_workspace)
        
        assert len(result.issues) == 1
        issue = result.issues[0]
        assert "cortex-docs/" in issue.suggested_fix or "delete" in issue.suggested_fix.lower()
        assert "YAML" in issue.description


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
