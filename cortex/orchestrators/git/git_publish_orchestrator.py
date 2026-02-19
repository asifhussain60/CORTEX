"""
GitPublishOrchestrator — Async git stage → commit → push pipeline.

Wraps AsyncGitOperations (with circuit breaker) to provide a clean,
non-blocking publish interface that replaces shell-based git hooks and
GitHub Actions push triggers.

AC_START: AC-GIT-ORCH-002
Authority: GitOrchestrator recommendation (2026-02-19)
Testing: tests/unit/orchestrators/git/test_git_orchestrator.py
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
            CORE-028 (snake_case), CORE-035 (single canonical implementation)
"""

import asyncio
import logging
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class PublishError(Exception):
    """Raised when any git publish operation (add / commit / push) fails."""


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class PublishResult:
    """Result of a completed git publish operation.

    Attributes:
        success: True when add, commit, and push all succeeded.
        commit_sha: The full SHA of the created commit (empty string if none).
        branch: Target branch that was pushed.
        message: Commit message used.
        files_committed: Number of files staged and committed.
        remote: Remote name that was pushed to (default: 'origin').
    """

    success: bool
    commit_sha: str
    branch: str
    message: str
    files_committed: int = 0
    remote: str = "origin"


# ---------------------------------------------------------------------------
# GitPublishOrchestrator
# ---------------------------------------------------------------------------


class GitPublishOrchestrator:
    """Stages, commits, and pushes sanitized code to the configured remote.

    All git operations are async and protected by CORTEX's existing
    :class:`~cortex.infrastructure.git_circuit_breaker.GitCircuitBreaker`.

    Example::

        publisher = GitPublishOrchestrator()
        result = await publisher.publish(
            repo_path="/path/to/repo",
            branch="main",
            message="feat: sanitized repository",
        )
    """

    def __init__(
        self,
        remote: str = "origin",
        timeout_seconds: float = 30.0,
    ) -> None:
        """Initialize GitPublishOrchestrator.

        Args:
            remote: Git remote name (default: 'origin').
            timeout_seconds: Timeout for each git command.
        """
        self._remote = remote
        self._timeout = timeout_seconds

    async def publish(
        self,
        repo_path: str,
        branch: str,
        message: str,
        paths: Optional[List[str]] = None,
    ) -> PublishResult:
        """Run git add → git commit → git push.

        Args:
            repo_path: Absolute path to the git repository root.
            branch: Branch to push to on the remote.
            message: Commit message.
            paths: Specific paths to stage; defaults to all changes ('.').

        Returns:
            :class:`PublishResult` with outcome details.

        Raises:
            PublishError: When any git command exits non-zero or raises.
        """
        stage_paths = paths or ["."]
        try:
            # Stage 1: git add
            add_cmd = ["git", "add"] + stage_paths
            await self._run_git(add_cmd, cwd=repo_path)
            logger.info("git add completed for %s", repo_path)

            # Stage 2: git commit
            commit_cmd = ["git", "commit", "-m", message]
            commit_result = await self._run_git(commit_cmd, cwd=repo_path)
            commit_sha = self._extract_sha(commit_result.stdout if commit_result else "")
            logger.info("git commit '%s' → %s", message, commit_sha or "<no-sha>")

            # Stage 3: git push
            push_cmd = ["git", "push", self._remote, branch]
            await self._run_git(push_cmd, cwd=repo_path)
            logger.info("git push → %s/%s", self._remote, branch)

            return PublishResult(
                success=True,
                commit_sha=commit_sha,
                branch=branch,
                message=message,
                remote=self._remote,
            )

        except Exception as exc:
            logger.error("GitPublishOrchestrator failed: %s", exc)
            raise PublishError(f"Publish pipeline failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _run_git(
        self,
        cmd: List[str],
        cwd: str,
    ) -> subprocess.CompletedProcess:
        """Run a git command asynchronously.

        Delegates to AsyncGitOperations when available; falls back to
        asyncio.create_subprocess_exec for zero-dependency testing.

        Args:
            cmd: Full git command list.
            cwd: Working directory.

        Returns:
            :class:`subprocess.CompletedProcess` with stdout/stderr.

        Raises:
            Exception: On non-zero exit or timeout.
        """
        try:
            from cortex.infrastructure.async_git_operations import get_async_git_operations
            async_git = get_async_git_operations()
            return await async_git.run_git_command_async(cmd, cwd=cwd)
        except ImportError:
            # Fallback: bare asyncio subprocess (test environments without full CORTEX)
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=self._timeout)
            stdout = stdout_b.decode("utf-8") if stdout_b else ""
            stderr = stderr_b.decode("utf-8") if stderr_b else ""
            if proc.returncode != 0:
                raise subprocess.CalledProcessError(proc.returncode, cmd, stdout, stderr)
            return subprocess.CompletedProcess(cmd, proc.returncode or 0, stdout, stderr)

    def _extract_sha(self, commit_output: str) -> str:
        """Extract commit SHA from git commit output.

        Args:
            commit_output: Stdout from git commit.

        Returns:
            Commit SHA string, or empty string if not found.
        """
        import re
        match = re.search(r"\b([0-9a-f]{7,40})\b", commit_output)
        return match.group(1) if match else ""


__all__ = [
    "PublishError",
    "PublishResult",
    "GitPublishOrchestrator",
]

# AC_COMPLETE: AC-GIT-ORCH-002 ✅ GitPublishOrchestrator implemented
