"""
Tests for Remote Git Adapter.

Authority: CORE-008 (TDD)
Phase: 10 - LENS Remote Intelligence
Task: LENS-010
"""

import os
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Environment checks for integration tests
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
HAS_GITHUB_TOKEN = GITHUB_TOKEN is not None
HAS_GITLAB_TOKEN = GITLAB_TOKEN is not None

from cortex.brain.analysis.remote_git_adapter import (
    RemoteGitProvider,
    RemoteGitAdapter,
    RemoteFile,
    RemoteCommit,
    RemoteBlame,
    ProviderConfig,
    ProviderType,
    create_adapter,
)


class TestRemoteFile:
    """Tests for RemoteFile dataclass."""
    
    def test_remote_file_creation(self):
        """Test creating RemoteFile."""
        file = RemoteFile(
            path="README.md",
            content="# Test",
            sha="abc123",
            size=6,
            encoding="utf-8",
        )
        
        assert file.path == "README.md"
        assert file.content == "# Test"
        assert file.sha == "abc123"
        assert file.size == 6
        assert file.encoding == "utf-8"


class TestRemoteCommit:
    """Tests for RemoteCommit dataclass."""
    
    def test_remote_commit_creation(self):
        """Test creating RemoteCommit."""
        commit = RemoteCommit(
            sha="abc123",
            message="Initial commit",
            author="Test Author",
            author_email="test@example.com",
            date=datetime(2024, 1, 1, 12, 0, 0),
            files_changed=["README.md"],
        )
        
        assert commit.sha == "abc123"
        assert commit.message == "Initial commit"
        assert commit.author == "Test Author"
        assert commit.author_email == "test@example.com"
        assert commit.date == datetime(2024, 1, 1, 12, 0, 0)
        assert commit.files_changed == ["README.md"]


class TestRemoteBlame:
    """Tests for RemoteBlame dataclass."""
    
    def test_remote_blame_creation(self):
        """Test creating RemoteBlame."""
        lines = [
            (1, "abc123", "Author 1", datetime(2024, 1, 1)),
            (2, "def456", "Author 2", datetime(2024, 1, 2)),
        ]
        
        blame = RemoteBlame(
            file_path="test.py",
            lines=lines,
        )
        
        assert blame.file_path == "test.py"
        assert len(blame.lines) == 2
        assert blame.lines[0][0] == 1
        assert blame.lines[0][1] == "abc123"


class TestProviderConfig:
    """Tests for ProviderConfig dataclass."""
    
    def test_provider_config_github(self):
        """Test creating GitHub provider config."""
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_test",
            base_url="https://api.github.com",
        )
        
        assert config.provider_type == ProviderType.GITHUB
        assert config.token == "ghp_test"
        assert config.base_url == "https://api.github.com"
    
    def test_provider_config_gitlab(self):
        """Test creating GitLab provider config."""
        config = ProviderConfig(
            provider_type=ProviderType.GITLAB,
            token="glpat-test",
            base_url="https://gitlab.com/api/v4",
        )
        
        assert config.provider_type == ProviderType.GITLAB
        assert config.token == "glpat-test"


class TestRemoteGitAdapter:
    """Tests for RemoteGitAdapter."""
    
    def test_adapter_initialization(self):
        """Test adapter initializes with provider."""
        mock_provider = Mock(spec=RemoteGitProvider)
        adapter = RemoteGitAdapter(mock_provider)
        assert adapter.provider == mock_provider
    
    def test_fetch_file_delegates_to_provider(self):
        """Test fetch_file delegates to provider."""
        mock_provider = Mock(spec=RemoteGitProvider)
        mock_provider.fetch_file.return_value = RemoteFile(
            path="test.py",
            content="print('test')",
            sha="abc123",
            size=13,
            encoding="utf-8",
        )
        
        adapter = RemoteGitAdapter(mock_provider)
        file = adapter.fetch_file("owner/repo", "test.py", "main")
        
        mock_provider.fetch_file.assert_called_once_with("owner/repo", "test.py", "main")
        assert file.path == "test.py"
        assert file.content == "print('test')"
    
    def test_fetch_commits_delegates_to_provider(self):
        """Test fetch_commits delegates to provider."""
        mock_provider = Mock(spec=RemoteGitProvider)
        mock_commits = [
            RemoteCommit(
                sha="abc123",
                message="Test commit",
                author="Test",
                author_email="test@example.com",
                date=datetime(2024, 1, 1),
                files_changed=[],
            ),
        ]
        mock_provider.fetch_commits.return_value = mock_commits
        
        adapter = RemoteGitAdapter(mock_provider)
        commits = adapter.fetch_commits("owner/repo", "test.py", "main", 10)
        
        mock_provider.fetch_commits.assert_called_once_with("owner/repo", "test.py", "main", 10)
        assert len(commits) == 1
        assert commits[0].sha == "abc123"
    
    def test_fetch_blame_delegates_to_provider(self):
        """Test fetch_blame delegates to provider."""
        mock_provider = Mock(spec=RemoteGitProvider)
        mock_blame = RemoteBlame(
            file_path="test.py",
            lines=[(1, "abc123", "Test", datetime(2024, 1, 1))],
        )
        mock_provider.fetch_blame.return_value = mock_blame
        
        adapter = RemoteGitAdapter(mock_provider)
        blame = adapter.fetch_blame("owner/repo", "test.py", "main")
        
        mock_provider.fetch_blame.assert_called_once_with("owner/repo", "test.py", "main")
        assert blame.file_path == "test.py"
    
    def test_list_branches_delegates_to_provider(self):
        """Test list_branches delegates to provider."""
        mock_provider = Mock(spec=RemoteGitProvider)
        mock_provider.list_branches.return_value = ["main", "develop", "feature/test"]
        
        adapter = RemoteGitAdapter(mock_provider)
        branches = adapter.list_branches("owner/repo")
        
        mock_provider.list_branches.assert_called_once_with("owner/repo")
        assert len(branches) == 3
        assert "main" in branches
    
    def test_compare_branches_delegates_to_provider(self):
        """Test compare_branches delegates to provider."""
        mock_provider = Mock(spec=RemoteGitProvider)
        mock_comparison = {
            "commits": [],
            "files_changed": ["file1.py", "file2.py"],
            "additions": 10,
            "deletions": 5,
        }
        mock_provider.compare_branches.return_value = mock_comparison
        
        adapter = RemoteGitAdapter(mock_provider)
        comparison = adapter.compare_branches("owner/repo", "main", "develop")
        
        mock_provider.compare_branches.assert_called_once_with("owner/repo", "main", "develop")
        assert len(comparison["files_changed"]) == 2


class TestCreateAdapter:
    """Tests for create_adapter factory function."""
    
    @patch("cortex.brain.analysis.providers.GitHubProvider")
    def test_create_github_adapter(self, mock_github_provider_class):
        """Test creating GitHub adapter."""
        mock_provider_instance = Mock(spec=RemoteGitProvider)
        mock_github_provider_class.return_value = mock_provider_instance
        
        config = ProviderConfig(provider_type=ProviderType.GITHUB, token="test")
        adapter = create_adapter(config)
        
        mock_github_provider_class.assert_called_once_with(config)
        assert isinstance(adapter, RemoteGitAdapter)
        assert adapter.provider == mock_provider_instance
    
    @patch("cortex.brain.analysis.providers.GitLabProvider")
    def test_create_gitlab_adapter(self, mock_gitlab_provider_class):
        """Test creating GitLab adapter."""
        mock_provider_instance = Mock(spec=RemoteGitProvider)
        mock_gitlab_provider_class.return_value = mock_provider_instance
        
        config = ProviderConfig(provider_type=ProviderType.GITLAB, token="test")
        adapter = create_adapter(config)
        
        mock_gitlab_provider_class.assert_called_once_with(config)
        assert isinstance(adapter, RemoteGitAdapter)
        assert adapter.provider == mock_provider_instance
    
    def test_create_adapter_unsupported_type(self):
        """Test creating adapter with unsupported type."""
        config = ProviderConfig(provider_type=ProviderType.GENERIC_GIT, token="test")
        
        with pytest.raises(ValueError, match="Unsupported provider"):
            create_adapter(config)


# Integration tests (require actual API access - skipped by default)
class TestGitHubProviderIntegration:
    """Integration tests for GitHub provider (requires real token)."""
    
    @pytest.mark.skipif(not HAS_GITHUB_TOKEN, reason="Requires GITHUB_TOKEN environment variable")
    @pytest.mark.integration
    def test_github_fetch_file_real(self):
        """Test fetching real file from GitHub."""
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=GITHUB_TOKEN,
        )
        
        adapter = create_adapter(config)
        file = adapter.fetch_file("octocat/Hello-World", "README", "master")
        
        assert file.path == "README"
        assert len(file.content) > 0
        assert file.sha is not None


class TestGitLabProviderIntegration:
    """Integration tests for GitLab provider (requires real token)."""
    
    @pytest.mark.skipif(not HAS_GITLAB_TOKEN, reason="Requires GITLAB_TOKEN environment variable")
    @pytest.mark.integration
    def test_gitlab_fetch_file_real(self):
        """Test fetching real file from GitLab."""
        config = ProviderConfig(
            provider_type=ProviderType.GITLAB,
            token=GITLAB_TOKEN,
        )
        
        adapter = create_adapter(config)
        file = adapter.fetch_file("gitlab-org/gitlab", "README.md", "master")
        
        assert file.path == "README.md"
        assert len(file.content) > 0
        assert file.sha is not None
