"""
Remote Git Providers - Implementation modules for GitHub, GitLab, and generic git.

This package contains concrete implementations of RemoteGitProvider for:
- GitHub (REST API v3 + GraphQL v4)
- GitLab (REST API v4)
- Generic git (git:// and https:// protocols)

Authority: CORE-008 (TDD), CORE-011 (Type hints)
Phase: 10 - LENS Remote Intelligence
"""

from cortex.brain.analysis.providers.github_provider import GitHubProvider
from cortex.brain.analysis.providers.gitlab_provider import GitLabProvider

__all__ = ["GitHubProvider", "GitLabProvider"]
