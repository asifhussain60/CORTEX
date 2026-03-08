"""
SubPhaseCheckpointInjector — Git-backed checkpoint/rollback safety wrapper.

Phase 138-b: Provides a lifecycle wrapper for CAPE PlanExecutionLoop sub-phases.

Components:
  - CheckpointState dataclass — carries checkpoint context
  - SubPhaseCheckpointInjector — create/commit/rollback lifecycle

The injector wraps any sub-phase callback with:
  create_checkpoint → execute callback → commit on success → rollback on failure

Non-git workspaces produce CheckpointState.skipped=True (no exceptions).

Author: Asif Hussain
"""
from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
import subprocess
from typing import Callable, Optional, TypeVar

from cortex.core.rollback_manager import RollbackManager

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class CheckpointState:
    """Context for a single sub-phase checkpoint.

    Attributes:
        sub_phase_id: Identifier of the sub-phase being wrapped.
        baseline_sha: HEAD SHA recorded before execution, or None if skipped.
        stash_created: True if dirty workspace was stashed before execution.
        skipped: True if checkpoint was skipped (e.g. non-git workspace).
    """

    sub_phase_id: str
    baseline_sha: Optional[str]
    stash_created: bool
    skipped: bool


class SubPhaseCheckpointInjector:
    """Wraps sub-phase execution in a git checkpoint safety envelope.

    Lifecycle:
      1. create_checkpoint() — record HEAD SHA; stash dirty tree if present
      2. Execute sub-phase callback
      3. On success: commit_on_success() — create "[CORTEX] sub-phase {id} COMPLETE" commit
      4. On failure: rollback to baseline_sha via RollbackManager; restore stash if created

    Args:
        workspace: Path to workspace root. Defaults to current directory.
    """

    def __init__(self, workspace: Optional[Path] = None) -> None:
        _ws = Path(workspace) if workspace else Path.cwd()
        self._workspace = _ws
        self.rollback_manager = RollbackManager(workspace=_ws)

    # ── Public API ────────────────────────────────────────────────────────

    def create_checkpoint(self, sub_phase_id: str) -> CheckpointState:
        """Record the current HEAD SHA and stash any dirty changes.

        Args:
            sub_phase_id: Identifier for the sub-phase about to execute.

        Returns:
            CheckpointState with baseline context. If not a git workspace,
            returns skipped=True state.
        """
        if not self._is_git_workspace():
            return CheckpointState(
                sub_phase_id=sub_phase_id,
                baseline_sha=None,
                stash_created=False,
                skipped=True,
            )

        # Record HEAD SHA
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(self._workspace),
        )
        baseline_sha = sha_result.stdout.strip() if sha_result.returncode == 0 else None

        # Check for dirty tree
        diff_result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True,
            text=True,
            cwd=str(self._workspace),
        )
        has_changes = bool(diff_result.stdout.strip())
        stash_created = False

        if has_changes:
            stash_result = subprocess.run(
                ["git", "stash", "push", "-m", f"[CORTEX] checkpoint for {sub_phase_id}"],
                capture_output=True,
                text=True,
                cwd=str(self._workspace),
            )
            stash_created = stash_result.returncode == 0

        logger.info(
            "SubPhaseCheckpointInjector: checkpoint created for %s "
            "(sha=%s, stash=%s)",
            sub_phase_id,
            baseline_sha,
            stash_created,
        )
        return CheckpointState(
            sub_phase_id=sub_phase_id,
            baseline_sha=baseline_sha,
            stash_created=stash_created,
            skipped=False,
        )

    def commit_on_success(self, state: CheckpointState) -> None:
        """Create a git commit marking the sub-phase as complete.

        No-op if state.skipped is True or workspace has nothing to commit.

        Args:
            state: CheckpointState returned by create_checkpoint().
        """
        if state.skipped:
            return
        if not self._is_git_workspace():
            return

        # Stage all changes
        subprocess.run(
            ["git", "add", "-A"],
            capture_output=True,
            text=True,
            cwd=str(self._workspace),
        )
        # Commit — may be a no-op if nothing staged
        message = f"[CORTEX] sub-phase {state.sub_phase_id} COMPLETE"
        subprocess.run(
            ["git", "commit", "-m", message, "--allow-empty"],
            capture_output=True,
            text=True,
            cwd=str(self._workspace),
        )
        logger.info(
            "SubPhaseCheckpointInjector: committed checkpoint for %s",
            state.sub_phase_id,
        )

    def wrap_sub_phase(self, sub_phase_id: str, callback: Callable[[], T]) -> T:
        """Execute callback within a checkpoint safety envelope.

        Steps:
          1. create_checkpoint(sub_phase_id)
          2. Execute callback()
          3. On success: commit_on_success()
          4. On failure: rollback_to(baseline_sha); restore_stash if needed; re-raise

        Args:
            sub_phase_id: Sub-phase identifier for checkpoint context.
            callback: Zero-argument callable to execute.

        Returns:
            The return value of callback() on success.

        Raises:
            Exception: Re-raises any exception from callback after rollback.
        """
        state = self.create_checkpoint(sub_phase_id)

        try:
            result = callback()
            if not state.skipped:
                self.commit_on_success(state)
            return result
        except Exception:
            logger.error(
                "SubPhaseCheckpointInjector: sub-phase %s failed — initiating rollback",
                sub_phase_id,
            )
            if not state.skipped and state.baseline_sha is not None:
                self.rollback_manager.rollback_to(
                    state.baseline_sha, sub_phase_id=sub_phase_id
                )
                if state.stash_created:
                    self.rollback_manager.restore_stash()
            raise

    # ── Internal helpers ─────────────────────────────────────────────────

    def _is_git_workspace(self) -> bool:
        """Return True if workspace contains a .git directory."""
        return (self._workspace / ".git").exists()


__all__ = ["CheckpointState", "SubPhaseCheckpointInjector"]
