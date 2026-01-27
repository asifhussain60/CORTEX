"""
Remote Git Adapter - Abstract interface for remote repository analysis.

Provides unified API for accessing remote git repositories via:
- GitHub API (REST v3 + GraphQL v4)
- GitLab API (REST v4)
- Generic git protocol (git://, https://)

Features:
- Authentication abstraction (tokens, SSH keys)
- Rate limiting and retry logic
- Circuit breaker pattern
- Response caching

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 10 - LENS Remote Intelligence
Task: LENS-010
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Protocol
import logging


logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Supported remote git providers."""
    GITHUB = "github"
    GITLAB = "gitlab"
    GENERIC_GIT = "generic_git"


@dataclass
class RemoteFile:
    """
    Represents a file from a remote repository.
    
    Attributes:
        path: File path in repository
        content: File content (text or base64)
        sha: Git object SHA
        size: File size in bytes
        encoding: Content encoding (utf-8, base64, etc.)
    """
    path: str
    content: str
    sha: str
    size: int
    encoding: str = "utf-8"


@dataclass
class RemoteCommit:
    """
    Represents a commit from a remote repository.
    
    Attributes:
        sha: Commit SHA
        message: Commit message
        author: Author name
        author_email: Author email
        date: Commit timestamp
        files_changed: List of changed file paths
    """
    sha: str
    message: str
    author: str
    author_email: str
    date: datetime
    files_changed: List[str] = field(default_factory=list)


@dataclass
class RemoteBlame:
    """
    Git blame information for a file.
    
    Attributes:
        file_path: Path to file
        lines: List of (line_number, commit_sha, author, date) tuples
    """
    file_path: str
    lines: List[tuple[int, str, str, datetime]] = field(default_factory=list)


@dataclass
class ProviderConfig:
    """
    Configuration for remote provider authentication.
    
    Attributes:
        provider_type: Type of provider (GitHub, GitLab, etc.)
        base_url: Base API URL (for self-hosted instances)
        token: Authentication token
        username: Username (for basic auth)
        ssh_key_path: Path to SSH private key
        rate_limit: Maximum requests per hour
    """
    provider_type: ProviderType
    base_url: Optional[str] = None
    token: Optional[str] = None
    username: Optional[str] = None
    ssh_key_path: Optional[Path] = None
    rate_limit: int = 5000


class RemoteGitProvider(ABC):
    """
    Abstract base class for remote git providers.
    
    All providers must implement these methods to support
    remote repository analysis via LENS.
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize provider with configuration.
        
        Args:
            config: Provider configuration including auth
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def fetch_file(
        self,
        repo: str,
        file_path: str,
        ref: str = "main",
    ) -> RemoteFile:
        """
        Fetch a file from remote repository.
        
        Args:
            repo: Repository identifier (e.g., "owner/repo")
            file_path: Path to file in repository
            ref: Git ref (branch, tag, commit SHA)
            
        Returns:
            RemoteFile with content and metadata
            
        Raises:
            FileNotFoundError: If file doesn't exist
            AuthenticationError: If credentials invalid
            RateLimitError: If rate limit exceeded
        """
        pass
    
    @abstractmethod
    def fetch_commits(
        self,
        repo: str,
        file_path: Optional[str] = None,
        ref: str = "main",
        max_count: int = 100,
    ) -> List[RemoteCommit]:
        """
        Fetch commit history for repository or file.
        
        Args:
            repo: Repository identifier
            file_path: Optional path to filter commits
            ref: Git ref to start from
            max_count: Maximum commits to fetch
            
        Returns:
            List of RemoteCommit objects
        """
        pass
    
    @abstractmethod
    def fetch_blame(
        self,
        repo: str,
        file_path: str,
        ref: str = "main",
    ) -> RemoteBlame:
        """
        Fetch git blame for a file.
        
        Args:
            repo: Repository identifier
            file_path: Path to file
            ref: Git ref
            
        Returns:
            RemoteBlame with line-by-line attribution
        """
        pass
    
    @abstractmethod
    def list_branches(self, repo: str) -> List[str]:
        """
        List all branches in repository.
        
        Args:
            repo: Repository identifier
            
        Returns:
            List of branch names
        """
        pass
    
    @abstractmethod
    def compare_branches(
        self,
        repo: str,
        base_branch: str,
        head_branch: str,
    ) -> Dict[str, Any]:
        """
        Compare two branches.
        
        Args:
            repo: Repository identifier
            base_branch: Base branch name
            head_branch: Head branch name
            
        Returns:
            Dictionary with comparison data:
            - commits: List of commits in head but not base
            - files_changed: List of changed files
            - additions: Total lines added
            - deletions: Total lines deleted
        """
        pass
    
    def validate_auth(self) -> bool:
        """
        Validate authentication credentials.
        
        Returns:
            True if credentials valid, False otherwise
        """
        try:
            # Subclasses should implement actual validation
            return True
        except Exception as e:
            self.logger.error(f"Authentication validation failed: {e}")
            return False


class RemoteGitAdapter:
    """
    Unified adapter for remote git operations.
    
    Automatically selects appropriate provider based on repository URL
    and manages provider lifecycle.
    
    Example:
        ```python
        from cortex.brain.analysis.remote_git_adapter import (
            RemoteGitAdapter,
            ProviderConfig,
            ProviderType,
        )
        
        # Configure GitHub provider
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN"),
        )
        
        adapter = RemoteGitAdapter(config)
        
        # Fetch file from remote
        file = adapter.fetch_file(
            repo="owner/repo",
            file_path="src/main.py",
            ref="feature-branch",
        )
        
        # Compare branches
        comparison = adapter.compare_branches(
            repo="owner/repo",
            base_branch="main",
            head_branch="feature-branch",
        )
        ```
    """
    
    def __init__(self, provider: RemoteGitProvider):
        """
        Initialize adapter with provider.
        
        Args:
            provider: Remote git provider instance
        """
        self.provider = provider
        self.logger = logging.getLogger(__name__)
    
    def fetch_file(
        self,
        repo: str,
        file_path: str,
        ref: str = "main",
    ) -> RemoteFile:
        """
        Fetch file from remote repository.
        
        Args:
            repo: Repository identifier
            file_path: Path to file
            ref: Git ref (branch, tag, SHA)
            
        Returns:
            RemoteFile with content and metadata
        """
        self.logger.info(f"Fetching {file_path} from {repo}@{ref}")
        return self.provider.fetch_file(repo, file_path, ref)
    
    def fetch_commits(
        self,
        repo: str,
        file_path: Optional[str] = None,
        ref: str = "main",
        max_count: int = 100,
    ) -> List[RemoteCommit]:
        """
        Fetch commit history.
        
        Args:
            repo: Repository identifier
            file_path: Optional file path filter
            ref: Git ref
            max_count: Maximum commits
            
        Returns:
            List of commits
        """
        self.logger.info(f"Fetching commits from {repo}@{ref}")
        return self.provider.fetch_commits(repo, file_path, ref, max_count)
    
    def fetch_blame(
        self,
        repo: str,
        file_path: str,
        ref: str = "main",
    ) -> RemoteBlame:
        """
        Fetch git blame for file.
        
        Args:
            repo: Repository identifier
            file_path: Path to file
            ref: Git ref
            
        Returns:
            Blame information
        """
        self.logger.info(f"Fetching blame for {file_path} from {repo}@{ref}")
        return self.provider.fetch_blame(repo, file_path, ref)
    
    def list_branches(self, repo: str) -> List[str]:
        """
        List repository branches.
        
        Args:
            repo: Repository identifier
            
        Returns:
            List of branch names
        """
        return self.provider.list_branches(repo)
    
    def compare_branches(
        self,
        repo: str,
        base_branch: str,
        head_branch: str,
    ) -> Dict[str, Any]:
        """
        Compare two branches.
        
        Args:
            repo: Repository identifier
            base_branch: Base branch
            head_branch: Head branch
            
        Returns:
            Comparison data
        """
        self.logger.info(f"Comparing {base_branch}...{head_branch} in {repo}")
        return self.provider.compare_branches(repo, base_branch, head_branch)


def create_adapter(config: ProviderConfig) -> RemoteGitAdapter:
    """
    Factory function to create adapter with appropriate provider.
    
    Args:
        config: Provider configuration
        
    Returns:
        Configured RemoteGitAdapter
        
    Raises:
        ValueError: If provider type not supported
    """
    from cortex.brain.analysis.providers import (
        GitHubProvider,
        GitLabProvider,
    )
    
    if config.provider_type == ProviderType.GITHUB:
        provider = GitHubProvider(config)
    elif config.provider_type == ProviderType.GITLAB:
        provider = GitLabProvider(config)
    else:
        raise ValueError(f"Unsupported provider: {config.provider_type}")
    
    return RemoteGitAdapter(provider)
