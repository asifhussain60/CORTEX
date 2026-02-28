"""Unit Tests — VacuumOrchestrator.run_digest_cleanup()

Tests for digested chat-* file cleanup across the workspace:
- Deletes chat-* files (JSON/MD) found outside _workspaces/
- Removes empty parent directories after cleanup
- Preserves chat-* files inside _workspaces/ (protected dir)
- Preserves non-chat files in the same directories
- Supports dry_run mode

Phase: PHASE-89
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings), CORE-028 (snake_case)
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture()
def workspace(tmp_path: Path) -> Path:
    """Build a workspace with digested chat-* files in various locations."""
    # ── DELETE targets: chat-* files inside cortex/ tree ─────────────────
    digests = tmp_path / "cortex" / "intelligence" / "state" / "state" / "digests"
    digests.mkdir(parents=True)
    (digests / "chat-20260207-142752.json").write_text('{"digest": "old"}')
    (digests / "chat-20260211-091552.json").write_text('{"digest": "old"}')
    (digests / "chat-20260211-091308.json").write_text('{"digest": "old"}')

    # A non-chat file in the same directory — must be preserved
    (digests / "summary.json").write_text('{"kept": true}')

    # ── DELETE targets: chat-* at project root ───────────────────────────
    (tmp_path / "chat-20260215-session.md").write_text("# stale root chat")

    # ── KEEP: chat-* inside _workspaces/ (protected) ────────────────────
    ws_chats = tmp_path / "_workspaces" / ".chats"
    ws_chats.mkdir(parents=True)
    (ws_chats / "chat-20260210-review.md").write_text("# keep this")

    # ── KEEP: legitimate file with chat- prefix in .github/templates ────
    gh_templates = tmp_path / ".github" / "templates"
    gh_templates.mkdir(parents=True)
    (gh_templates / "chat-vs-terminal-guide.md").write_text("# guide")

    return tmp_path


@pytest.fixture()
def vac(workspace: Path) -> object:
    """Instantiated VacuumOrchestrator on the workspace fixture."""
    from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

    return VacuumOrchestrator(workspace)


# ─────────────────────────────────────────────────────────────────────────────
# Interface contract
# ─────────────────────────────────────────────────────────────────────────────


class TestRunDigestCleanupInterface:
    """run_digest_cleanup() exists and returns the right shape."""

    def test_method_exists(self, vac: object) -> None:
        """run_digest_cleanup must be a public method on VacuumOrchestrator."""
        assert hasattr(vac, "run_digest_cleanup"), (
            "VacuumOrchestrator must expose run_digest_cleanup()"
        )

    def test_returns_list(self, vac: object) -> None:
        """Return type must be a list of OperationResult."""
        result = vac.run_digest_cleanup()  # type: ignore[union-attr]
        assert isinstance(result, list)

    def test_dry_run_returns_list(self, vac: object) -> None:
        """Dry-run mode must also return a list."""
        result = vac.run_digest_cleanup(dry_run=True)  # type: ignore[union-attr]
        assert isinstance(result, list)


# ─────────────────────────────────────────────────────────────────────────────
# Dry-run safety
# ─────────────────────────────────────────────────────────────────────────────


class TestDigestCleanupDryRun:
    """Dry-run must plan deletions without executing them."""

    def test_dry_run_deletes_nothing(self, vac: object, workspace: Path) -> None:
        """All chat-* files must still exist after dry-run."""
        vac.run_digest_cleanup(dry_run=True)  # type: ignore[union-attr]
        digests = workspace / "cortex" / "intelligence" / "state" / "state" / "digests"
        assert (digests / "chat-20260207-142752.json").exists()
        assert (digests / "chat-20260211-091552.json").exists()
        assert (workspace / "chat-20260215-session.md").exists()

    def test_dry_run_reports_planned_ops(self, vac: object) -> None:
        """Dry-run must report at least one planned operation."""
        results = vac.run_digest_cleanup(dry_run=True)  # type: ignore[union-attr]
        assert len(results) >= 3, (
            f"Expected ≥3 planned deletions, got {len(results)}"
        )
        for r in results:
            assert r.dry_run is True


# ─────────────────────────────────────────────────────────────────────────────
# Actual deletion
# ─────────────────────────────────────────────────────────────────────────────


class TestDigestCleanupExecution:
    """Execution mode must delete chat-* files outside protected dirs."""

    def test_deletes_chat_json_in_cortex_tree(self, vac: object, workspace: Path) -> None:
        """chat-*.json files under cortex/ must be deleted."""
        vac.run_digest_cleanup()  # type: ignore[union-attr]
        digests = workspace / "cortex" / "intelligence" / "state" / "state" / "digests"
        assert not (digests / "chat-20260207-142752.json").exists()
        assert not (digests / "chat-20260211-091552.json").exists()
        assert not (digests / "chat-20260211-091308.json").exists()

    def test_deletes_chat_md_at_root(self, vac: object, workspace: Path) -> None:
        """chat-*.md files at the workspace root must be deleted."""
        vac.run_digest_cleanup()  # type: ignore[union-attr]
        assert not (workspace / "chat-20260215-session.md").exists()

    def test_preserves_non_chat_files(self, vac: object, workspace: Path) -> None:
        """Non-chat files in the same directory must be preserved."""
        vac.run_digest_cleanup()  # type: ignore[union-attr]
        digests = workspace / "cortex" / "intelligence" / "state" / "state" / "digests"
        assert (digests / "summary.json").exists()

    def test_preserves_workspaces_chat_files(self, vac: object, workspace: Path) -> None:
        """chat-* files inside _workspaces/ must be preserved."""
        vac.run_digest_cleanup()  # type: ignore[union-attr]
        ws_chat = workspace / "_workspaces" / ".chats" / "chat-20260210-review.md"
        assert ws_chat.exists()

    def test_preserves_github_chat_files(self, vac: object, workspace: Path) -> None:
        """chat-* files inside .github/ must be preserved."""
        vac.run_digest_cleanup()  # type: ignore[union-attr]
        guide = workspace / ".github" / "templates" / "chat-vs-terminal-guide.md"
        assert guide.exists()

    def test_results_report_success(self, vac: object) -> None:
        """All executed operations must report success."""
        results = vac.run_digest_cleanup()  # type: ignore[union-attr]
        for r in results:
            assert r.success is True, f"Operation failed: {r}"


# ─────────────────────────────────────────────────────────────────────────────
# Integration with run()
# ─────────────────────────────────────────────────────────────────────────────


class TestDigestCleanupInRunPipeline:
    """Digest cleanup must be included in the standalone run() pipeline."""

    def test_run_deletes_chat_digests(self, vac: object, workspace: Path) -> None:
        """run() must include digest cleanup in its pipeline."""
        vac.run()  # type: ignore[union-attr]
        digests = workspace / "cortex" / "intelligence" / "state" / "state" / "digests"
        assert not (digests / "chat-20260207-142752.json").exists()

    def test_run_preserves_workspaces(self, vac: object, workspace: Path) -> None:
        """run() must still protect _workspaces/ chat files."""
        vac.run()  # type: ignore[union-attr]
        ws_chat = workspace / "_workspaces" / ".chats" / "chat-20260210-review.md"
        assert ws_chat.exists()
