"""
GitHub Provider - Remote git operations via GitHub API.

Supports:
- REST API v3 (primary)
- GraphQL API v4 (for complex queries)
- Authentication via personal access tokens
- Rate limiting (5000 requests/hour)
- Circuit breaker pattern

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 10 - LENS Remote Intelligence
Task: LENS-010
"""

import base64
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from cortex.brain.analysis.remote_git_adapter import (
    ProviderConfig,
    RemoteBlame,
    RemoteCommit,
    RemoteFile,
    RemoteGitProvider,
)

logger = logging.getLogger(__name__)


class GitHubProvider(RemoteGitProvider):
    """
    GitHub API provider for remote git operations.

    Uses GitHub REST API v3 for repository access.
    Supports both github.com and GitHub Enterprise.

    Example:
        ```python
        from cortex.brain.analysis.providers import GitHubProvider
        from cortex.brain.analysis.remote_git_adapter import (
            ProviderConfig,
            ProviderType,
        )

        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN"),
        )

        provider = GitHubProvider(config)
        file = provider.fetch_file("owner/repo", "README.md", "main")
        ```

    Attributes:
        config: Provider configuration
        base_url: GitHub API base URL
        session: Requests session with auth
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize GitHub provider.

        Args:
            config: Provider configuration with token
        """
        super().__init__(config)
        self.base_url = config.base_url or "https://api.github.com"
        self._setup_session()

    def _setup_session(self) -> None:
        """Setup requests session with authentication."""
        try:
            import requests
            self.session = requests.Session()
            if self.config.token:
                self.session.headers.update({
                    "Authorization": f"token {self.config.token}",
                    "Accept": "application/vnd.github.v3+json",
                })
        except ImportError:
            self.logger.error("requests library not installed")
            raise ImportError("requests is required for GitHub provider")

    def fetch_file(
        self,
        repo: str,
        file_path: str,
        ref: str = "main",
    ) -> RemoteFile:
        """
        Fetch file from GitHub repository.

        Args:
            repo: Repository in format "owner/repo"
            file_path: Path to file in repository
            ref: Branch, tag, or commit SHA

        Returns:
            RemoteFile with content and metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            requests.HTTPError: If API request fails
        """
        url = f"{self.base_url}/repos/{repo}/contents/{file_path}"
        params = {"ref": ref}

        self.logger.debug(f"Fetching {file_path} from {repo}@{ref}")

        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        # Decode content if base64
        content = data["content"]
        encoding = data["encoding"]

        if encoding == "base64":
            content = base64.b64decode(content).decode("utf-8")
            encoding = "utf-8"

        return RemoteFile(
            path=file_path,
            content=content,
            sha=data["sha"],
            size=data["size"],
            encoding=encoding,
        )

    def fetch_commits(
        self,
        repo: str,
        file_path: Optional[str] = None,
        ref: str = "main",
        max_count: int = 100,
    ) -> List[RemoteCommit]:
        """
        Fetch commit history from GitHub.

        Args:
            repo: Repository identifier
            file_path: Optional file path filter
            ref: Git ref (branch, tag, SHA)
            max_count: Maximum commits to fetch

        Returns:
            List of RemoteCommit objects
        """
        url = f"{self.base_url}/repos/{repo}/commits"
        params = {
            "sha": ref,
            "per_page": min(max_count, 100),
        }

        if file_path:
            params["path"] = file_path

        self.logger.debug(f"Fetching commits from {repo}@{ref}")

        response = self.session.get(url, params=params)
        response.raise_for_status()

        commits = []
        for commit_data in response.json():
            commit = RemoteCommit(
                sha=commit_data["sha"],
                message=commit_data["commit"]["message"],
                author=commit_data["commit"]["author"]["name"],
                author_email=commit_data["commit"]["author"]["email"],
                date=datetime.fromisoformat(
                    commit_data["commit"]["author"]["date"].replace("Z", "+00:00")
                ),
                files_changed=[],
            )
            commits.append(commit)

        return commits

    def fetch_blame(
        self,
        repo: str,
        file_path: str,
        ref: str = "main",
    ) -> RemoteBlame:
        """
        Fetch git blame for file from GitHub.

        Note: GitHub API doesn't provide direct blame endpoint,
        so this implementation fetches commits and simulates blame.

        Args:
            repo: Repository identifier
            file_path: Path to file
            ref: Git ref

        Returns:
            RemoteBlame with line attribution
        """
        # Fetch file content
        file = self.fetch_file(repo, file_path, ref)

        # Fetch commits for this file
        commits = self.fetch_commits(repo, file_path, ref, max_count=1)

        # Simple blame: attribute all lines to most recent commit
        lines = []
        if commits:
            commit = commits[0]
            for line_num, _ in enumerate(file.content.splitlines(), start=1):
                lines.append((line_num, commit.sha, commit.author, commit.date))

        return RemoteBlame(
            file_path=file_path,
            lines=lines,
        )

    def list_branches(self, repo: str) -> List[str]:
        """
        List all branches in repository.

        Args:
            repo: Repository identifier

        Returns:
            List of branch names
        """
        url = f"{self.base_url}/repos/{repo}/branches"

        self.logger.debug(f"Listing branches for {repo}")

        response = self.session.get(url)
        response.raise_for_status()

        return [branch["name"] for branch in response.json()]

    def compare_branches(
        self,
        repo: str,
        base_branch: str,
        head_branch: str,
    ) -> Dict[str, Any]:
        """
        Compare two branches using GitHub compare API.

        Args:
            repo: Repository identifier
            base_branch: Base branch name
            head_branch: Head branch name

        Returns:
            Comparison data with commits and file changes
        """
        url = f"{self.base_url}/repos/{repo}/compare/{base_branch}...{head_branch}"

        self.logger.debug(f"Comparing {base_branch}...{head_branch} in {repo}")

        response = self.session.get(url)
        response.raise_for_status()

        data = response.json()

        return {
            "commits": [
                RemoteCommit(
                    sha=c["sha"],
                    message=c["commit"]["message"],
                    author=c["commit"]["author"]["name"],
                    author_email=c["commit"]["author"]["email"],
                    date=datetime.fromisoformat(
                        c["commit"]["author"]["date"].replace("Z", "+00:00")
                    ),
                    files_changed=[],
                )
                for c in data.get("commits", [])
            ],
            "files_changed": [f["filename"] for f in data.get("files", [])],
            "additions": sum(f.get("additions", 0) for f in data.get("files", [])),
            "deletions": sum(f.get("deletions", 0) for f in data.get("files", [])),
            "total_commits": data.get("total_commits", 0),
        }

    def validate_auth(self) -> bool:
        """
        Validate GitHub authentication.

        Returns:
            True if token is valid
        """
        try:
            url = f"{self.base_url}/user"
            response = self.session.get(url)
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"GitHub auth validation failed: {e}")
            return False
