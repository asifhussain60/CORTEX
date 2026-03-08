"""
Tests for Phase-138 Git Checkpoint Safety.

Covers:
  138-a: RollbackManager — get_head_sha, rollback_to, restore_stash
  138-b: SubPhaseCheckpointInjector — CheckpointState + wrap_sub_phase lifecycle
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest

from cortex.core.rollback_manager import RollbackManager
from cortex.core.sub_phase_checkpoint_injector import (
    CheckpointState,
    SubPhaseCheckpointInjector,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

FAKE_SHA = "a" * 40
FAKE_SHA_2 = "b" * 40


@pytest.fixture
def non_git_tmp(tmp_path: Path) -> Path:
    """Temp dir with no .git directory — simulates non-git workspace."""
    return tmp_path


@pytest.fixture
def mock_git_workspace(tmp_path: Path) -> Path:
    """Temp dir with a fake .git directory — simulates git workspace."""
    (tmp_path / ".git").mkdir()
    return tmp_path


# ─────────────────────────────────────────────────────────────────────────────
# 138-a: RollbackManager tests
# ─────────────────────────────────────────────────────────────────────────────


class TestRollbackManagerGetHeadSha:
    """get_head_sha() returns current HEAD SHA or None for non-git workspace."""

    def test_get_head_sha_returns_sha(self, mock_git_workspace: Path) -> None:
        """git rev-parse HEAD returns a 40-char hex string."""
        manager = RollbackManager(workspace=mock_git_workspace)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=FAKE_SHA + "\n",
            )
            sha = manager.get_head_sha()
        assert sha == FAKE_SHA
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "rev-parse" in args
        assert "HEAD" in args

    def test_get_head_sha_non_git_workspace(self, non_git_tmp: Path) -> None:
        """No .git dir → returns None, no exception raised."""
        manager = RollbackManager(workspace=non_git_tmp)
        sha = manager.get_head_sha()
        assert sha is None

    def test_get_head_sha_git_error_returns_none(self, mock_git_workspace: Path) -> None:
        """git command fails → returns None gracefully."""
        manager = RollbackManager(workspace=mock_git_workspace)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="")
            sha = manager.get_head_sha()
        assert sha is None


class TestRollbackManagerRollbackTo:
    """rollback_to() resets to a SHA and emits URS MILD_PUNISHMENT."""

    def test_rollback_to_valid_sha(self, mock_git_workspace: Path) -> None:
        """git reset --hard {sha} runs successfully."""
        manager = RollbackManager(workspace=mock_git_workspace)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="HEAD is now at ...")
            result = manager.rollback_to(FAKE_SHA, sub_phase_id="138-a")
        assert result is True
        args = mock_run.call_args[0][0]
        assert "reset" in args
        assert "--hard" in args
        assert FAKE_SHA in args

    def test_rollback_emits_urs_punishment(self, mock_git_workspace: Path) -> None:
        """MILD_PUNISHMENT signal emitted after successful rollback."""
        manager = RollbackManager(workspace=mock_git_workspace)
        with (
            patch("subprocess.run") as mock_run,
            patch.object(manager, "_emit_urs_punishment") as mock_emit,
        ):
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            manager.rollback_to(FAKE_SHA, sub_phase_id="138-a")
        mock_emit.assert_called_once_with("138-a")

    def test_rollback_non_git_workspace(self, non_git_tmp: Path) -> None:
        """No .git dir → no-op, returns False, no exception."""
        manager = RollbackManager(workspace=non_git_tmp)
        result = manager.rollback_to(FAKE_SHA, sub_phase_id="138-a")
        assert result is False

    def test_rollback_git_command_failure(self, mock_git_workspace: Path) -> None:
        """git reset --hard fails → returns False, no URS signal."""
        manager = RollbackManager(workspace=mock_git_workspace)
        with (
            patch("subprocess.run") as mock_run,
            patch.object(manager, "_emit_urs_punishment") as mock_emit,
        ):
            mock_run.return_value = MagicMock(returncode=1, stdout="")
            result = manager.rollback_to(FAKE_SHA, sub_phase_id="138-a")
        assert result is False
        mock_emit.assert_not_called()


class TestRollbackManagerRestoreStash:
    """restore_stash() pops a stash or is a no-op when no stash exists."""

    def test_restore_stash_with_stash(self, mock_git_workspace: Path) -> None:
        """git stash pop runs when stash is present."""
        manager = RollbackManager(workspace=mock_git_workspace)
        with patch("subprocess.run") as mock_run:
            # First call: git stash list (returns non-empty = stash exists)
            # Second call: git stash pop
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout="stash@{0}: WIP on main: abc"),
                MagicMock(returncode=0, stdout=""),
            ]
            result = manager.restore_stash()
        assert result is True
        assert mock_run.call_count == 2
        second_call_args = mock_run.call_args_list[1][0][0]
        assert "stash" in second_call_args
        assert "pop" in second_call_args

    def test_restore_stash_empty(self, mock_git_workspace: Path) -> None:
        """No stash present → returns False, no pop attempted."""
        manager = RollbackManager(workspace=mock_git_workspace)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")  # empty stash list
            result = manager.restore_stash()
        assert result is False
        # Only stash list was called — no pop
        assert mock_run.call_count == 1

    def test_restore_stash_non_git_workspace(self, non_git_tmp: Path) -> None:
        """No .git dir → returns False, no exception."""
        manager = RollbackManager(workspace=non_git_tmp)
        result = manager.restore_stash()
        assert result is False


# ─────────────────────────────────────────────────────────────────────────────
# 138-b: SubPhaseCheckpointInjector tests
# ─────────────────────────────────────────────────────────────────────────────


class TestCheckpointState:
    """CheckpointState dataclass carries checkpoint context."""

    def test_checkpoint_state_fields(self) -> None:
        """CheckpointState has sub_phase_id, baseline_sha, stash_created, skipped."""
        state = CheckpointState(
            sub_phase_id="138-b",
            baseline_sha=FAKE_SHA,
            stash_created=False,
            skipped=False,
        )
        assert state.sub_phase_id == "138-b"
        assert state.baseline_sha == FAKE_SHA
        assert state.stash_created is False
        assert state.skipped is False

    def test_checkpoint_state_skipped_default(self) -> None:
        """skipped=False by default; baseline_sha=None allowed for skipped states."""
        state = CheckpointState(
            sub_phase_id="test",
            baseline_sha=None,
            stash_created=False,
            skipped=True,
        )
        assert state.skipped is True
        assert state.baseline_sha is None


class TestSubPhaseCheckpointInjectorCreate:
    """create_checkpoint() sets baseline_sha and stash_created."""

    def test_create_checkpoint_records_sha(self, mock_git_workspace: Path) -> None:
        """CheckpointState.baseline_sha set to HEAD SHA."""
        injector = SubPhaseCheckpointInjector(workspace=mock_git_workspace)
        with patch("subprocess.run") as mock_run:
            # First call: git rev-parse HEAD, Second call: git diff --name-only (clean)
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout=FAKE_SHA),  # rev-parse HEAD
                MagicMock(returncode=0, stdout=""),         # diff --name-only (clean)
            ]
            state = injector.create_checkpoint("138-b")
        assert state.baseline_sha == FAKE_SHA
        assert state.sub_phase_id == "138-b"

    def test_create_checkpoint_stashes_dirty_tree(self, mock_git_workspace: Path) -> None:
        """Dirty workspace (unstaged changes) → stash_created True."""
        injector = SubPhaseCheckpointInjector(workspace=mock_git_workspace)
        with patch("subprocess.run") as mock_run:
            # get_head_sha call, stash check (non-empty diff), stash create
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout=FAKE_SHA),   # git rev-parse HEAD
                MagicMock(returncode=0, stdout="M file.py"),  # git diff --name-only (dirty)
                MagicMock(returncode=0, stdout=""),           # git stash push
            ]
            state = injector.create_checkpoint("138-b")
        assert state.stash_created is True

    def test_create_checkpoint_clean_workspace(self, mock_git_workspace: Path) -> None:
        """Clean workspace → stash_created False."""
        injector = SubPhaseCheckpointInjector(workspace=mock_git_workspace)
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout=FAKE_SHA),   # git rev-parse HEAD
                MagicMock(returncode=0, stdout=""),           # git diff --name-only (clean)
            ]
            state = injector.create_checkpoint("138-b")
        assert state.stash_created is False

    def test_checkpoint_skipped_non_git(self, non_git_tmp: Path) -> None:
        """No .git → CheckpointState.skipped True, no exception."""
        injector = SubPhaseCheckpointInjector(workspace=non_git_tmp)
        state = injector.create_checkpoint("138-b")
        assert state.skipped is True
        assert state.baseline_sha is None


class TestSubPhaseCheckpointInjectorCommit:
    """commit_on_success() creates a git commit with CORTEX sub-phase message."""

    def test_commit_on_success_makes_commit(self, mock_git_workspace: Path) -> None:
        """Successful callback → git commit with CORTEX message."""
        injector = SubPhaseCheckpointInjector(workspace=mock_git_workspace)
        state = CheckpointState(
            sub_phase_id="138-b",
            baseline_sha=FAKE_SHA,
            stash_created=False,
            skipped=False,
        )
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            injector.commit_on_success(state)
        mock_run.assert_called()
        # Verify commit was attempted
        all_calls_args = [str(c) for c in mock_run.call_args_list]
        assert any("commit" in args for args in all_calls_args)

    def test_commit_message_format(self, mock_git_workspace: Path) -> None:
        """Commit message contains sub_phase_id."""
        injector = SubPhaseCheckpointInjector(workspace=mock_git_workspace)
        state = CheckpointState(
            sub_phase_id="phase-138-b",
            baseline_sha=FAKE_SHA,
            stash_created=False,
            skipped=False,
        )
        captured_args: list[Any] = []
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = lambda args, **kw: (
                captured_args.append(args),
                MagicMock(returncode=0, stdout=""),
            )[1]
            injector.commit_on_success(state)
        commit_calls = [a for a in captured_args if "commit" in a]
        assert commit_calls, "No git commit call found"
        commit_args_str = " ".join(commit_calls[0])
        assert "phase-138-b" in commit_args_str or "[CORTEX]" in commit_args_str

    def test_commit_skipped_on_skipped_state(self, non_git_tmp: Path) -> None:
        """skipped=True → no git commit attempted."""
        injector = SubPhaseCheckpointInjector(workspace=non_git_tmp)
        state = CheckpointState(
            sub_phase_id="138-b",
            baseline_sha=None,
            stash_created=False,
            skipped=True,
        )
        with patch("subprocess.run") as mock_run:
            injector.commit_on_success(state)
        mock_run.assert_not_called()


class TestSubPhaseCheckpointInjectorWrap:
    """wrap_sub_phase() full lifecycle — success and failure paths."""

    def test_wrap_sub_phase_success_path(self, mock_git_workspace: Path) -> None:
        """Callback returns value → value returned from wrap_sub_phase."""
        injector = SubPhaseCheckpointInjector(workspace=mock_git_workspace)
        with (
            patch.object(injector, "create_checkpoint") as mock_create,
            patch.object(injector, "commit_on_success") as mock_commit,
        ):
            state = CheckpointState(
                sub_phase_id="138-b",
                baseline_sha=FAKE_SHA,
                stash_created=False,
                skipped=False,
            )
            mock_create.return_value = state
            result = injector.wrap_sub_phase("138-b", lambda: "done")
        assert result == "done"
        mock_commit.assert_called_once_with(state)

    def test_wrap_sub_phase_failure_path(self, mock_git_workspace: Path) -> None:
        """Callback raises → exception re-raised after rollback."""
        injector = SubPhaseCheckpointInjector(workspace=mock_git_workspace)
        with (
            patch.object(injector, "create_checkpoint") as mock_create,
            patch.object(injector.rollback_manager, "rollback_to") as mock_rollback,
            patch.object(injector.rollback_manager, "restore_stash"),
        ):
            state = CheckpointState(
                sub_phase_id="138-b",
                baseline_sha=FAKE_SHA,
                stash_created=False,
                skipped=False,
            )
            mock_create.return_value = state

            def boom() -> None:
                raise ValueError("sub-phase failed")

            with pytest.raises(ValueError, match="sub-phase failed"):
                injector.wrap_sub_phase("138-b", boom)
        mock_rollback.assert_called_once_with(FAKE_SHA, sub_phase_id="138-b")

    def test_rollback_restores_stash_if_created(self, mock_git_workspace: Path) -> None:
        """stash_created=True → restore_stash() called after rollback on failure."""
        injector = SubPhaseCheckpointInjector(workspace=mock_git_workspace)
        with (
            patch.object(injector, "create_checkpoint") as mock_create,
            patch.object(injector.rollback_manager, "rollback_to"),
            patch.object(injector.rollback_manager, "restore_stash") as mock_restore,
        ):
            state = CheckpointState(
                sub_phase_id="138-b",
                baseline_sha=FAKE_SHA,
                stash_created=True,
                skipped=False,
            )
            mock_create.return_value = state
            with pytest.raises(RuntimeError):
                injector.wrap_sub_phase("138-b", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
        mock_restore.assert_called_once()
