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
        success: True when add and commit succeeded (push is optional).
        commit_sha: The full SHA of the created commit (empty string if none).
        branch: Target branch name.
        message: Commit message used.
        files_committed: Number of files staged and committed.
        remote: Remote name configured (push may not have occurred).
        pushed: True only when a push to the remote actually ran.
    """

    success: bool
    commit_sha: str
    branch: str
    message: str
    files_committed: int = 0
    remote: str = "origin"
    pushed: bool = False


# ---------------------------------------------------------------------------
# GitPublishOrchestrator
# ---------------------------------------------------------------------------


class GitPublishOrchestrator:
    """Stages, commits, and optionally pushes sanitized code to the configured remote.

    By default **push is disabled** (``auto_push=False``).  The caller must
    explicitly set ``auto_push=True`` to push to the remote, ensuring no
    changes are sent to ``origin`` without explicit user approval.

    All git operations are async and protected by CORTEX's existing
    :class:`~cortex.infrastructure.git_circuit_breaker.GitCircuitBreaker`.

    Example — local commit only (default)::

        publisher = GitPublishOrchestrator()
        result = await publisher.publish(
            repo_path="/path/to/repo",
            branch="main",
            message="feat: sanitized repository",
        )
        # result.pushed is False — change is local only

    Example — explicit push (user-approved)::

        publisher = GitPublishOrchestrator(auto_push=True)
        result = await publisher.publish(...)
    """

    def __init__(
        self,
        remote: str = "origin",
        timeout_seconds: float = 30.0,
        auto_push: bool = False,
    ) -> None:
        """Initialize GitPublishOrchestrator.

        Args:
            remote: Git remote name (default: 'origin').
            timeout_seconds: Timeout for each git command.
            auto_push: When False (default), commit locally only.
                       Set True only with explicit user approval to push.
        """
        self._remote = remote
        self._timeout = timeout_seconds
        self._auto_push = auto_push

    async def publish(
        self,
        repo_path: str,
        branch: str,
        message: str,
        paths: Optional[List[str]] = None,
        auto_push: Optional[bool] = None,
    ) -> PublishResult:
        """Run git add → git commit → (optional) git push.

        Push only occurs when ``auto_push`` is True — either passed
        explicitly here or set at construction time.  The default is
        **False** (local commit only) to ensure no changes reach the
        remote without explicit user approval.

        Args:
            repo_path: Absolute path to the git repository root.
            branch: Target branch (used for push when enabled).
            message: Commit message.
            paths: Specific paths to stage; defaults to all changes ('.').
            auto_push: Per-call override for the push gate.  When None,
                       falls back to the instance-level ``auto_push`` flag.

        Returns:
            :class:`PublishResult` with outcome details.
            ``result.pushed`` is True only when a push actually occurred.

        Raises:
            PublishError: When any git command exits non-zero or raises.
        """
        should_push = auto_push if auto_push is not None else self._auto_push
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

            # Stage 3: git push (gated — requires explicit approval)
            pushed = False
            if should_push:
                push_cmd = ["git", "push", self._remote, branch]
                await self._run_git(push_cmd, cwd=repo_path)
                logger.info("git push → %s/%s", self._remote, branch)
                pushed = True
            else:
                logger.info(
                    "git push SKIPPED — auto_push=False. "
                    "Call publish(auto_push=True) to push to %s/%s after user approval.",
                    self._remote,
                    branch,
                )

            return PublishResult(
                success=True,
                commit_sha=commit_sha,
                branch=branch,
                message=message,
                remote=self._remote,
                pushed=pushed,
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
