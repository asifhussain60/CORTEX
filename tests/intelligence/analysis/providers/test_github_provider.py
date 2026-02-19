"""
Tests for GitHub Provider.

Authority: CORE-008 (TDD)
Phase: 10 - LENS Remote Intelligence
Task: LENS-010
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import base64

from cortex.brain.analysis.providers.github_provider import GitHubProvider
from cortex.brain.analysis.remote_git_adapter import (
    ProviderConfig,
    ProviderType,
    RemoteFile,
    RemoteCommit,
    RemoteBlame,
)


@pytest.fixture
def github_config():
    """GitHub provider configuration."""
    return ProviderConfig(
        provider_type=ProviderType.GITHUB,
        token="ghp_test_token",
        base_url="https://api.github.com",
    )


@pytest.fixture
def mock_session():
    """Mock requests session."""
    session = MagicMock()
    session.headers = {}
    return session


class TestGitHubProviderInit:
    """Tests for GitHub provider initialization."""
    
    @patch("requests.Session")
    def test_provider_initialization(self, mock_session_class, github_config):
        """Test provider initializes correctly."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        provider = GitHubProvider(github_config)
        
        assert provider.base_url == "https://api.github.com"
        assert provider.config == github_config
    
    @patch("requests.Session")
    def test_session_setup_with_token(self, mock_session_class, github_config):
        """Test session is configured with token."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        provider = GitHubProvider(github_config)
        
        mock_session.headers.update.assert_called_once()
        call_args = mock_session.headers.update.call_args[0][0]
        assert "Authorization" in call_args
        assert call_args["Authorization"] == "token ghp_test_token"


class TestGitHubProviderFetchFile:
    """Tests for fetch_file method."""
    
    @patch("requests.Session")
    def test_fetch_file_success(self, mock_session_class, github_config, mock_session):
        """Test successful file fetch."""
        content_b64 = base64.b64encode(b"# Test README").decode("utf-8")
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": content_b64,
            "encoding": "base64",
            "sha": "abc123",
            "size": 13,
        }
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        provider = GitHubProvider(github_config)
        provider.session = mock_session
        
        file = provider.fetch_file("owner/repo", "README.md", "main")
        
        assert file.path == "README.md"
        assert file.content == "# Test README"
        assert file.sha == "abc123"
        assert file.size == 13
        assert file.encoding == "utf-8"
    
    @patch("requests.Session")
    def test_fetch_file_with_ref(self, mock_session_class, github_config, mock_session):
        """Test fetching file with specific ref."""
        content_b64 = base64.b64encode(b"content").decode("utf-8")
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": content_b64,
            "encoding": "base64",
            "sha": "def456",
            "size": 7,
        }
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        provider = GitHubProvider(github_config)
        provider.session = mock_session
        
        file = provider.fetch_file("owner/repo", "test.py", "develop")
        
        # Verify ref was passed in params
        call_args = mock_session.get.call_args
        assert call_args[1]["params"]["ref"] == "develop"
    
    @patch("requests.Session")
    def test_fetch_file_not_found(self, mock_session_class, github_config, mock_session):
        """Test file not found error."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        provider = GitHubProvider(github_config)
        provider.session = mock_session
        
        with pytest.raises(Exception, match="404 Not Found"):
            provider.fetch_file("owner/repo", "missing.py", "main")


class TestGitHubProviderFetchCommits:
    """Tests for fetch_commits method."""
    
    @patch("requests.Session")
    def test_fetch_commits_success(self, mock_session_class, github_config, mock_session):
        """Test successful commits fetch."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "sha": "abc123",
                "commit": {
                    "message": "Initial commit",
                    "author": {
                        "name": "Test Author",
                        "email": "test@example.com",
                        "date": "2024-01-01T12:00:00Z",
                    },
                },
            },
            {
                "sha": "def456",
                "commit": {
                    "message": "Second commit",
                    "author": {
                        "name": "Test Author 2",
                        "email": "test2@example.com",
                        "date": "2024-01-02T12:00:00Z",
                    },
                },
            },
        ]
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        provider = GitHubProvider(github_config)
        provider.session = mock_session
        
        commits = provider.fetch_commits("owner/repo", None, "main", 100)
        
        assert len(commits) == 2
        assert commits[0].sha == "abc123"
        assert commits[0].message == "Initial commit"
        assert commits[0].author == "Test Author"
        assert commits[1].sha == "def456"
    
    @patch("requests.Session")
    def test_fetch_commits_with_file_path(self, mock_session_class, github_config, mock_session):
        """Test fetching commits filtered by file path."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        provider = GitHubProvider(github_config)
        provider.session = mock_session
        
        provider.fetch_commits("owner/repo", "specific/file.py", "main", 50)
        
        call_args = mock_session.get.call_args
        assert call_args[1]["params"]["path"] == "specific/file.py"
    
    @patch("requests.Session")
    def test_fetch_commits_max_count(self, mock_session_class, github_config, mock_session):
        """Test max_count parameter."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        provider = GitHubProvider(github_config)
        provider.session = mock_session
        
        provider.fetch_commits("owner/repo", None, "main", 25)
        
        call_args = mock_session.get.call_args
        assert call_args[1]["params"]["per_page"] == 25


class TestGitHubProviderListBranches:
    """Tests for list_branches method."""
    
    @patch("requests.Session")
    def test_list_branches_success(self, mock_session_class, github_config, mock_session):
        """Test successful branch listing."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "main"},
            {"name": "develop"},
            {"name": "feature/test"},
        ]
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        provider = GitHubProvider(github_config)
        provider.session = mock_session
        
        branches = provider.list_branches("owner/repo")
        
        assert len(branches) == 3
        assert "main" in branches
        assert "develop" in branches
        assert "feature/test" in branches


class TestGitHubProviderCompareBranches:
    """Tests for compare_branches method."""
    
    @patch("requests.Session")
    def test_compare_branches_success(self, mock_session_class, github_config, mock_session):
        """Test successful branch comparison."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "commits": [
                {
                    "sha": "abc123",
                    "commit": {
                        "message": "Feature commit",
                        "author": {
                            "name": "Dev",
                            "email": "dev@example.com",
                            "date": "2024-01-03T12:00:00Z",
                        },
                    },
                },
            ],
            "files": [
                {"filename": "file1.py", "additions": 10, "deletions": 5},
                {"filename": "file2.py", "additions": 20, "deletions": 3},
            ],
            "total_commits": 1,
        }
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        provider = GitHubProvider(github_config)
        provider.session = mock_session
        
        comparison = provider.compare_branches("owner/repo", "main", "develop")
        
        assert len(comparison["commits"]) == 1
        assert comparison["commits"][0].sha == "abc123"
        assert len(comparison["files_changed"]) == 2
        assert comparison["additions"] == 30
        assert comparison["deletions"] == 8
        assert comparison["total_commits"] == 1


class TestGitHubProviderValidateAuth:
    """Tests for validate_auth method."""
    
    @patch("requests.Session")
    def test_validate_auth_success(self, mock_session_class, github_config, mock_session):
        """Test successful auth validation."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        provider = GitHubProvider(github_config)
        provider.session = mock_session
        
        assert provider.validate_auth() is True
    
    @patch("requests.Session")
    def test_validate_auth_failure(self, mock_session_class, github_config, mock_session):
        """Test failed auth validation."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        provider = GitHubProvider(github_config)
        provider.session = mock_session
        
        assert provider.validate_auth() is False
