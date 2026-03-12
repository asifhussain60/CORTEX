"""
RollbackManager — Git reset --hard safety wrapper with URS punishment signal.

Phase 138-a: Backs primitives/execution/git-checkpoint.yaml with Python.

Provides:
  - get_head_sha() — current HEAD SHA or None for non-git workspace
  - rollback_to(target_sha, sub_phase_id) — git reset --hard + URS MILD_PUNISHMENT
  - restore_stash() — git stash pop when stash exists

All methods are graceful no-ops in non-git workspaces (no exceptions).

Author: Asif Hussain
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)

_SHA_PATTERN = re.compile(r"^[a-f0-9]{40}$")
"""Valid 40-character hexadecimal SHA-1 pattern."""


class RollbackManager:
    """Git-backed rollback manager for CORTEX sub-phase safety.

    Wraps git reset --hard and stash operations with URS signal emission.
    All operations gracefully degrade to no-ops in non-git workspaces.

    Args:
        workspace: Path to the workspace root. Defaults to current directory.
    """

    def __init__(self, workspace: Optional[Path] = None) -> None:
        self._workspace = Path(workspace) if workspace else Path.cwd()

    # ── Public API ────────────────────────────────────────────────────────

    def get_head_sha(self) -> Optional[str]:
        """Return current HEAD SHA (40-char hex) or None if not in a git repo.

        Returns:
            Current HEAD SHA string, or None for non-git workspaces or errors.
        """
        if not self._is_git_workspace():
            return None
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(self._workspace),
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        return result.stdout.strip()

    def rollback_to(self, target_sha: str, *, sub_phase_id: str) -> bool:
        """Reset workspace to target_sha using git reset --hard.

        Emits a URS MILD_PUNISHMENT signal on success to record the rollback
        in the CORTEX learning system.

        Args:
            target_sha: The git SHA to reset to.
            sub_phase_id: Sub-phase identifier for URS signal context.

        Returns:
            True if rollback succeeded, False otherwise (including non-git).
        """
        if not _SHA_PATTERN.match(target_sha):
            raise ValueError(
                f"RollbackManager: invalid SHA format '{target_sha}' — "
                "expected 40-character lowercase hexadecimal string."
            )

        if not self._is_git_workspace():
            logger.debug("RollbackManager: not a git workspace — skip rollback")
            return False

        result = subprocess.run(
            ["git", "reset", "--hard", target_sha],
            capture_output=True,
            text=True,
            cwd=str(self._workspace),
        )
        if result.returncode != 0:
            logger.warning(
                "RollbackManager: git reset --hard failed for %s: %s",
                sub_phase_id,
                result.stdout,
            )
            return False

        logger.info("RollbackManager: rolled back to %s for %s", target_sha, sub_phase_id)
        self._emit_urs_punishment(sub_phase_id)
        return True

    def restore_stash(self) -> bool:
        """Pop the most recent git stash if one exists.

        Returns:
            True if stash was popped, False if no stash or not a git workspace.
        """
        if not self._is_git_workspace():
            return False

        list_result = subprocess.run(
            ["git", "stash", "list"],
            capture_output=True,
            text=True,
            cwd=str(self._workspace),
        )
        if not list_result.stdout.strip():
            logger.debug("RollbackManager: no stash to restore")
            return False

        subprocess.run(
            ["git", "stash", "pop"],
            capture_output=True,
            text=True,
            cwd=str(self._workspace),
        )
        logger.info("RollbackManager: stash restored")
        return True

    # ── Internal helpers ─────────────────────────────────────────────────

    def _is_git_workspace(self) -> bool:
        """Return True if workspace contains a .git directory."""
        return (self._workspace / ".git").exists()

    def _emit_urs_punishment(self, sub_phase_id: str) -> None:
        """Emit a URS MILD_PUNISHMENT signal for the rollback event.

        Best-effort — never blocks rollback if URS emission fails.
        """
        try:
            from cortex.intelligence.learning.reinforcement_signal import (
                ReinforcementEngine,
                SignalType,
            )

            engine = ReinforcementEngine()
            engine.emit_signal(
                signal_type=SignalType.MILD_PUNISHMENT,
                pattern_id=f"rollback:{sub_phase_id}",
                source_orchestrator="RollbackManager",
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug("RollbackManager: URS emission skipped: %s", exc)


__all__ = ["RollbackManager"]
