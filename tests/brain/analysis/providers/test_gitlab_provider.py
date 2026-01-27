"""
Tests for GitLab Provider.

Authority: CORE-008 (TDD)
Phase: 10 - LENS Remote Intelligence
Task: LENS-010
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import base64

from cortex.brain.analysis.providers.gitlab_provider import GitLabProvider
from cortex.brain.analysis.remote_git_adapter import (
    ProviderConfig,
    ProviderType,
    RemoteFile,
    RemoteCommit,
    RemoteBlame,
)


@pytest.fixture
def gitlab_config():
    """GitLab provider configuration."""
    return ProviderConfig(
        provider_type=ProviderType.GITLAB,
        token="glpat_test_token",
        base_url="https://gitlab.com/api/v4",
    )


@pytest.fixture
def mock_session():
    """Mock requests session."""
    session = MagicMock()
    session.headers = {}
    return session


class TestGitLabProviderInit:
    """Tests for GitLab provider initialization."""
    
    def test_provider_initialization(self, gitlab_config):
        """Test provider initializes correctly."""
        with patch("cortex.brain.analysis.providers.gitlab_provider.requests"):
            provider = GitLabProvider(gitlab_config)
            
            assert provider.base_url == "https://gitlab.com/api/v4"
            assert provider.config == gitlab_config
    
    def test_session_setup_with_token(self, gitlab_config):
        """Test session is configured with token."""
        with patch("cortex.brain.analysis.providers.gitlab_provider.requests") as mock_requests:
            mock_session = MagicMock()
            mock_requests.Session.return_value = mock_session
            
            provider = GitLabProvider(gitlab_config)
            
            mock_session.headers.update.assert_called_once()
            call_args = mock_session.headers.update.call_args[0][0]
            assert "PRIVATE-TOKEN" in call_args
            assert call_args["PRIVATE-TOKEN"] == "glpat_test_token"


class TestGitLabProviderEncoding:
    """Tests for GitLab path encoding."""
    
    def test_encode_project_path(self, gitlab_config):
        """Test project path encoding."""
        with patch("cortex.brain.analysis.providers.gitlab_provider.requests"):
            provider = GitLabProvider(gitlab_config)
            
            encoded = provider._encode_project_path("group/project")
            assert encoded == "group%2Fproject"
    
    def test_encode_nested_path(self, gitlab_config):
        """Test nested path encoding."""
        with patch("cortex.brain.analysis.providers.gitlab_provider.requests"):
            provider = GitLabProvider(gitlab_config)
            
            encoded = provider._encode_project_path("group/subgroup/project")
            assert encoded == "group%2Fsubgroup%2Fproject"


class TestGitLabProviderFetchFile:
    """Tests for fetch_file method."""
    
    def test_fetch_file_success(self, gitlab_config, mock_session):
        """Test successful file fetch."""
        content_b64 = base64.b64encode(b"# Test README").decode("utf-8")
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": content_b64,
            "encoding": "base64",
            "blob_id": "abc123",
            "size": 13,
        }
        mock_session.get.return_value = mock_response
        
        with patch("cortex.brain.analysis.providers.gitlab_provider.requests"):
            provider = GitLabProvider(gitlab_config)
            provider.session = mock_session
            
            file = provider.fetch_file("group/project", "README.md", "main")
            
            assert file.path == "README.md"
            assert file.content == "# Test README"
            assert file.sha == "abc123"
            assert file.size == 13
            assert file.encoding == "utf-8"
    
    def test_fetch_file_url_encoding(self, gitlab_config, mock_session):
        """Test URL encoding in file fetch."""
        content_b64 = base64.b64encode(b"content").decode("utf-8")
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": content_b64,
            "encoding": "base64",
            "blob_id": "def456",
            "size": 7,
        }
        mock_session.get.return_value = mock_response
        
        with patch("cortex.brain.analysis.providers.gitlab_provider.requests"):
            provider = GitLabProvider(gitlab_config)
            provider.session = mock_session
            
            provider.fetch_file("group/project", "src/file.py", "main")
            
            # Verify URL encoding
            call_args = mock_session.get.call_args[0][0]
            assert "group%2Fproject" in call_args
            assert "src%2Ffile.py" in call_args


class TestGitLabProviderFetchCommits:
    """Tests for fetch_commits method."""
    
    def test_fetch_commits_success(self, gitlab_config, mock_session):
        """Test successful commits fetch."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "id": "abc123",
                "message": "Initial commit",
                "author_name": "Test Author",
                "author_email": "test@example.com",
                "created_at": "2024-01-01T12:00:00Z",
            },
            {
                "id": "def456",
                "message": "Second commit",
                "author_name": "Test Author 2",
                "author_email": "test2@example.com",
                "created_at": "2024-01-02T12:00:00Z",
            },
        ]
        mock_session.get.return_value = mock_response
        
        with patch("cortex.brain.analysis.providers.gitlab_provider.requests"):
            provider = GitLabProvider(gitlab_config)
            provider.session = mock_session
            
            commits = provider.fetch_commits("group/project", None, "main", 100)
            
            assert len(commits) == 2
            assert commits[0].sha == "abc123"
            assert commits[0].message == "Initial commit"
            assert commits[0].author == "Test Author"
    
    def test_fetch_commits_with_file_path(self, gitlab_config, mock_session):
        """Test fetching commits filtered by file path."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_session.get.return_value = mock_response
        
        with patch("cortex.brain.analysis.providers.gitlab_provider.requests"):
            provider = GitLabProvider(gitlab_config)
            provider.session = mock_session
            
            provider.fetch_commits("group/project", "specific/file.py", "main", 50)
            
            call_args = mock_session.get.call_args
            assert call_args[1]["params"]["path"] == "specific/file.py"


class TestGitLabProviderFetchBlame:
    """Tests for fetch_blame method."""
    
    def test_fetch_blame_success(self, gitlab_config, mock_session):
        """Test successful blame fetch."""
        # Mock blame response
        mock_blame_response = MagicMock()
        mock_blame_response.json.return_value = [
            {
                "commit": {
                    "id": "abc123",
                    "author_name": "Author 1",
                    "committed_date": "2024-01-01T12:00:00Z",
                },
                "lines": ["line 1", "line 2"],
            },
            {
                "commit": {
                    "id": "def456",
                    "author_name": "Author 2",
                    "committed_date": "2024-01-02T12:00:00Z",
                },
                "lines": ["line 3"],
            },
        ]
        
        # Setup mock session to return blame response
        mock_session.get.return_value = mock_blame_response
        
        with patch("cortex.brain.analysis.providers.gitlab_provider.requests"):
            provider = GitLabProvider(gitlab_config)
            provider.session = mock_session
            
            blame = provider.fetch_blame("group/project", "test.py", "main")
            
            assert blame.file_path == "test.py"
            assert len(blame.lines) == 3
            assert blame.lines[0][1] == "abc123"  # First line, commit sha
            assert blame.lines[0][2] == "Author 1"  # First line, author
            assert blame.lines[2][1] == "def456"  # Third line, commit sha


class TestGitLabProviderListBranches:
    """Tests for list_branches method."""
    
    def test_list_branches_success(self, gitlab_config, mock_session):
        """Test successful branch listing."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "main"},
            {"name": "develop"},
            {"name": "feature/test"},
        ]
        mock_session.get.return_value = mock_response
        
        with patch("cortex.brain.analysis.providers.gitlab_provider.requests"):
            provider = GitLabProvider(gitlab_config)
            provider.session = mock_session
            
            branches = provider.list_branches("group/project")
            
            assert len(branches) == 3
            assert "main" in branches
            assert "develop" in branches


class TestGitLabProviderCompareBranches:
    """Tests for compare_branches method."""
    
    def test_compare_branches_success(self, gitlab_config, mock_session):
        """Test successful branch comparison."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "commits": [
                {
                    "id": "abc123",
                    "message": "Feature commit",
                    "author_name": "Dev",
                    "author_email": "dev@example.com",
                    "created_at": "2024-01-03T12:00:00Z",
                },
            ],
            "diffs": [
                {"new_path": "file1.py"},
                {"new_path": "file2.py"},
            ],
        }
        mock_session.get.return_value = mock_response
        
        with patch("cortex.brain.analysis.providers.gitlab_provider.requests"):
            provider = GitLabProvider(gitlab_config)
            provider.session = mock_session
            
            comparison = provider.compare_branches("group/project", "main", "develop")
            
            assert len(comparison["commits"]) == 1
            assert comparison["commits"][0].sha == "abc123"
            assert len(comparison["files_changed"]) == 2
            assert "file1.py" in comparison["files_changed"]
            assert comparison["total_commits"] == 1
    
    def test_compare_branches_params(self, gitlab_config, mock_session):
        """Test branch comparison parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"commits": [], "diffs": []}
        mock_session.get.return_value = mock_response
        
        with patch("cortex.brain.analysis.providers.gitlab_provider.requests"):
            provider = GitLabProvider(gitlab_config)
            provider.session = mock_session
            
            provider.compare_branches("group/project", "main", "feature")
            
            call_args = mock_session.get.call_args
            assert call_args[1]["params"]["from"] == "main"
            assert call_args[1]["params"]["to"] == "feature"


class TestGitLabProviderValidateAuth:
    """Tests for validate_auth method."""
    
    def test_validate_auth_success(self, gitlab_config, mock_session):
        """Test successful auth validation."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        
        with patch("cortex.brain.analysis.providers.gitlab_provider.requests"):
            provider = GitLabProvider(gitlab_config)
            provider.session = mock_session
            
            assert provider.validate_auth() is True
    
    def test_validate_auth_failure(self, gitlab_config, mock_session):
        """Test failed auth validation."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
        mock_session.get.return_value = mock_response
        
        with patch("cortex.brain.analysis.providers.gitlab_provider.requests"):
            provider = GitLabProvider(gitlab_config)
            provider.session = mock_session
            
            assert provider.validate_auth() is False
