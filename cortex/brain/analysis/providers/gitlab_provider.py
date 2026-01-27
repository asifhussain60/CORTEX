"""
GitLab Provider - Remote git operations via GitLab API.

Supports:
- REST API v4
- Authentication via personal/project/group tokens
- Rate limiting (configurable, default 600 req/min)
- Both GitLab.com and self-hosted instances

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 10 - LENS Remote Intelligence
Task: LENS-010
"""

import base64
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

from cortex.brain.analysis.remote_git_adapter import (
    RemoteGitProvider,
    RemoteFile,
    RemoteCommit,
    RemoteBlame,
    ProviderConfig,
)


logger = logging.getLogger(__name__)


class GitLabProvider(RemoteGitProvider):
    """
    GitLab API provider for remote git operations.
    
    Uses GitLab REST API v4 for repository access.
    Supports both gitlab.com and self-hosted GitLab.
    
    Example:
        ```python
        from cortex.brain.analysis.providers import GitLabProvider
        from cortex.brain.analysis.remote_git_adapter import (
            ProviderConfig,
            ProviderType,
        )
        
        config = ProviderConfig(
            provider_type=ProviderType.GITLAB,
            token=os.getenv("GITLAB_TOKEN"),
        )
        
        provider = GitLabProvider(config)
        file = provider.fetch_file("group/project", "README.md", "main")
        ```
    
    Attributes:
        config: Provider configuration
        base_url: GitLab API base URL
        session: Requests session with auth
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize GitLab provider.
        
        Args:
            config: Provider configuration with token
        """
        super().__init__(config)
        self.base_url = config.base_url or "https://gitlab.com/api/v4"
        self._setup_session()
    
    def _setup_session(self) -> None:
        """Setup requests session with authentication."""
        try:
            import requests
            self.session = requests.Session()
            if self.config.token:
                self.session.headers.update({
                    "PRIVATE-TOKEN": self.config.token,
                })
        except ImportError:
            self.logger.error("requests library not installed")
            raise ImportError("requests is required for GitLab provider")
    
    def _encode_project_path(self, project: str) -> str:
        """
        URL-encode project path for GitLab API.
        
        GitLab requires project paths to be URL-encoded.
        Example: "group/project" → "group%2Fproject"
        
        Args:
            project: Project path (group/project)
            
        Returns:
            URL-encoded project path
        """
        import urllib.parse
        return urllib.parse.quote(project, safe='')
    
    def fetch_file(
        self,
        repo: str,
        file_path: str,
        ref: str = "main",
    ) -> RemoteFile:
        """
        Fetch file from GitLab repository.
        
        Args:
            repo: Repository in format "group/project"
            file_path: Path to file in repository
            ref: Branch, tag, or commit SHA
            
        Returns:
            RemoteFile with content and metadata
            
        Raises:
            FileNotFoundError: If file doesn't exist
            requests.HTTPError: If API request fails
        """
        project_encoded = self._encode_project_path(repo)
        file_path_encoded = self._encode_project_path(file_path)
        
        url = f"{self.base_url}/projects/{project_encoded}/repository/files/{file_path_encoded}"
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
            sha=data["blob_id"],
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
        Fetch commit history from GitLab.
        
        Args:
            repo: Repository identifier
            file_path: Optional file path filter
            ref: Git ref (branch, tag, SHA)
            max_count: Maximum commits to fetch
            
        Returns:
            List of RemoteCommit objects
        """
        project_encoded = self._encode_project_path(repo)
        url = f"{self.base_url}/projects/{project_encoded}/repository/commits"
        
        params = {
            "ref_name": ref,
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
                sha=commit_data["id"],
                message=commit_data["message"],
                author=commit_data["author_name"],
                author_email=commit_data["author_email"],
                date=datetime.fromisoformat(
                    commit_data["created_at"].replace("Z", "+00:00")
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
        Fetch git blame for file from GitLab.
        
        GitLab provides a blame endpoint that returns line-by-line attribution.
        
        Args:
            repo: Repository identifier
            file_path: Path to file
            ref: Git ref
            
        Returns:
            RemoteBlame with line attribution
        """
        project_encoded = self._encode_project_path(repo)
        file_path_encoded = self._encode_project_path(file_path)
        
        url = f"{self.base_url}/projects/{project_encoded}/repository/files/{file_path_encoded}/blame"
        params = {"ref": ref}
        
        self.logger.debug(f"Fetching blame for {file_path} from {repo}@{ref}")
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        blame_data = response.json()
        
        lines = []
        line_num = 1
        
        for range_data in blame_data:
            commit_info = range_data["commit"]
            line_content = range_data["lines"]
            
            # Each range may contain multiple lines
            for _ in line_content:
                lines.append((
                    line_num,
                    commit_info["id"],
                    commit_info["author_name"],
                    datetime.fromisoformat(
                        commit_info["committed_date"].replace("Z", "+00:00")
                    ),
                ))
                line_num += 1
        
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
        project_encoded = self._encode_project_path(repo)
        url = f"{self.base_url}/projects/{project_encoded}/repository/branches"
        
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
        Compare two branches using GitLab compare API.
        
        Args:
            repo: Repository identifier
            base_branch: Base branch name
            head_branch: Head branch name
            
        Returns:
            Comparison data with commits and file changes
        """
        project_encoded = self._encode_project_path(repo)
        url = f"{self.base_url}/projects/{project_encoded}/repository/compare"
        
        params = {
            "from": base_branch,
            "to": head_branch,
        }
        
        self.logger.debug(f"Comparing {base_branch}...{head_branch} in {repo}")
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "commits": [
                RemoteCommit(
                    sha=c["id"],
                    message=c["message"],
                    author=c["author_name"],
                    author_email=c["author_email"],
                    date=datetime.fromisoformat(
                        c["created_at"].replace("Z", "+00:00")
                    ),
                    files_changed=[],
                )
                for c in data.get("commits", [])
            ],
            "files_changed": [d["new_path"] for d in data.get("diffs", [])],
            "total_commits": len(data.get("commits", [])),
        }
    
    def validate_auth(self) -> bool:
        """
        Validate GitLab authentication.
        
        Returns:
            True if token is valid
        """
        try:
            url = f"{self.base_url}/user"
            response = self.session.get(url)
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"GitLab auth validation failed: {e}")
            return False
