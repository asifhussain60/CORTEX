"""
Tests for CommitHandler Agent

Validates git operations, commit message generation,
and commit execution functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock
from src.cortex_agents.commit_handler import CommitHandler
from src.cortex_agents.base_agent import AgentRequest, AgentResponse
from src.cortex_agents.agent_types import IntentType


class TestCommitHandlerBasics:
    """Test basic CommitHandler functionality"""
    
    def test_handler_initialization(self, mock_tier_apis):
        """Test CommitHandler initialization"""
        handler = CommitHandler("Committer", **mock_tier_apis)
        
        assert handler.name == "Committer"
        assert handler.tier1 is not None
        assert handler.tier2 is not None
        assert handler.tier3 is not None
        assert len(handler.supported_intents) > 0
        assert len(handler.COMMIT_TYPES) > 0
    
    def test_handler_can_handle_commit_intent(self, mock_tier_apis):
        """Test CommitHandler handles commit intents"""
        handler = CommitHandler("Committer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="commit",
            context={},
            user_message="Commit changes"
        )
        
        assert handler.can_handle(request) is True
    
    def test_handler_can_handle_git_commit_intent(self, mock_tier_apis):
        """Test CommitHandler handles git_commit intents"""
        handler = CommitHandler("Committer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="git_commit",
            context={},
            user_message="Git commit"
        )
        
        assert handler.can_handle(request) is True
    
    def test_handler_rejects_invalid_intent(self, mock_tier_apis):
        """Test CommitHandler rejects non-commit intents"""
        handler = CommitHandler("Committer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="code",
            context={},
            user_message="Write some code"
        )
        
        assert handler.can_handle(request) is False


class TestCommitMessageGeneration:
    """Test commit message generation"""
    
    def test_generate_feat_commit(self, mock_tier_apis, mocker):
        """Test generation of feature commit message"""
        handler = CommitHandler("Committer", **mock_tier_apis)
        
        # Mock git status to show staged files
        mock_subprocess = mocker.patch("subprocess.run")
        mock_subprocess.return_value = MagicMock(
            stdout="src/feature.py\ntests/test_feature.py\n",
            returncode=0
        )
        
        request = AgentRequest(
            intent="commit",
            context={
                "type": "feat",
                "description": "Add user authentication",
                "dry_run": True
            },
            user_message="Commit authentication feature"
        )
        
        response = handler.execute(request)
        
        assert response.success is True
        assert response.result["message"].startswith("feat:")
        assert "authentication" in response.result["message"].lower()
        assert response.result["dry_run"] is True
    
    def test_generate_fix_commit(self, mock_tier_apis, mocker):
        """Test generation of bugfix commit message"""
        handler = CommitHandler("Committer", **mock_tier_apis)
        
        # Mock git status
        mock_subprocess = mocker.patch("subprocess.run")
        mock_subprocess.return_value = MagicMock(
            stdout="src/bug.py\n",
            returncode=0
        )
        
        request = AgentRequest(
            intent="commit",
            context={
                "type": "fix",
                "description": "Fix null pointer exception",
                "dry_run": True
            },
            user_message="Commit bugfix"
        )
        
        response = handler.execute(request)
        
        assert response.success is True
        assert response.result["message"].startswith("fix:")
        assert "null pointer" in response.result["message"].lower()
    
    def test_generate_docs_commit(self, mock_tier_apis, mocker):
        """Test generation of documentation commit message"""
        handler = CommitHandler("Committer", **mock_tier_apis)
        
        # Mock git status
        mock_subprocess = mocker.patch("subprocess.run")
        mock_subprocess.return_value = MagicMock(
            stdout="README.md\ndocs/guide.md\n",
            returncode=0
        )
        
        request = AgentRequest(
            intent="commit",
            context={
                "type": "docs",
                "description": "Update installation guide",
                "dry_run": True
            },
            user_message="Commit documentation updates"
        )
        
        response = handler.execute(request)
        
        assert response.success is True
        assert response.result["message"].startswith("docs:")
    
    def test_infer_commit_type_from_files(self, mock_tier_apis, mocker):
        """Test automatic commit type inference"""
        handler = CommitHandler("Committer", **mock_tier_apis)
        
        # Mock git status with test files only
        mock_subprocess = mocker.patch("subprocess.run")
        mock_subprocess.return_value = MagicMock(
            stdout="tests/test_feature.py\ntests/test_utils.py\n",
            returncode=0
        )
        
        request = AgentRequest(
            intent="commit",
            context={
                "description": "Add tests for new feature",
                "dry_run": True
            },
            user_message="Commit tests"
        )
        
        response = handler.execute(request)
        
        assert response.success is True
        # Should infer "test" type from test files
        assert "test:" in response.result["message"].lower() or response.result["message"].startswith("test:")


class TestGitOperations:
    """Test git operation handling"""
    
    def test_commit_with_staged_changes(self, mock_tier_apis, mocker):
        """Test commit execution with staged changes"""
        handler = CommitHandler("Committer", **mock_tier_apis)
        
        # Mock git operations
        mock_subprocess = mocker.patch("subprocess.run")
        
        # First call: git diff --cached --name-only
        # Second call: git commit
        # Third call: git rev-parse (for hash)
        mock_subprocess.side_effect = [
            MagicMock(stdout="src/app.py\n", returncode=0),  # Status check
            MagicMock(stdout="[main abc123] feat: test\n", returncode=0),  # Commit
            MagicMock(stdout="abc123\n", returncode=0)  # Hash
        ]
        
        request = AgentRequest(
            intent="commit",
            context={
                "type": "feat",
                "description": "Test feature"
            },
            user_message="Commit test feature"
        )
        
        response = handler.execute(request)
        
        assert response.success is True
        assert response.result["committed"] is True
        assert response.result["files"] > 0
        assert response.result["commit_hash"] is not None
    
    def test_no_staged_changes(self, mock_tier_apis, mocker):
        """Test handling of no staged changes"""
        handler = CommitHandler("Committer", **mock_tier_apis)
        
        # Mock git status with no staged files
        mock_subprocess = mocker.patch("subprocess.run")
        mock_subprocess.return_value = MagicMock(
            stdout="",  # No staged files
            returncode=0
        )
        
        request = AgentRequest(
            intent="commit",
            context={},
            user_message="Commit changes"
        )
        
        response = handler.execute(request)
        
        assert response.success is False
        assert "no staged changes" in response.message.lower()
    
    def test_dry_run_mode(self, mock_tier_apis, mocker):
        """Test dry-run mode (no actual commit)"""
        handler = CommitHandler("Committer", **mock_tier_apis)
        
        # Mock git status
        mock_subprocess = mocker.patch("subprocess.run")
        mock_subprocess.return_value = MagicMock(
            stdout="src/test.py\n",
            returncode=0
        )
        
        request = AgentRequest(
            intent="commit",
            context={
                "type": "feat",
                "description": "Test feature",
                "dry_run": True  # Dry run mode
            },
            user_message="Preview commit message"
        )
        
        response = handler.execute(request)
        
        assert response.success is True
        assert response.result["dry_run"] is True
        assert response.result["committed"] is False
        assert response.result["commit_hash"] == "DRY_RUN"
        assert "would commit" in response.message.lower()
