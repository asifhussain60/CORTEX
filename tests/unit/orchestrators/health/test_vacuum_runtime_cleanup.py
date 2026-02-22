"""Unit Tests — VacuumOrchestrator.run_runtime_cleanup()

Tests for the .cortex-runtime/ targeted cleanup:
- Stale archived-docs (markdown + txt files older than policy)
- Stale log files (setup.log, *.log)
- Stale report JSON files
- Stale session markdown
- Empty subdirectories within .cortex-runtime/
- KEEP: traces/*.db, wiring/*.db, intelligence/*.db, health_cache/*.json, setup-mcp.py

Phase: PHASE-51 (VacuumOrchestrator extension)
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
def runtime(tmp_path: Path) -> Path:
    """Build a representative .cortex-runtime/ tree under tmp_path."""
    rt = tmp_path / ".cortex-runtime"

    # canonical runtime dirs
    (rt / "traces").mkdir(parents=True)
    (rt / "wiring").mkdir(parents=True)
    (rt / "intelligence").mkdir(parents=True)
    (rt / "health_cache").mkdir(parents=True)
    (rt / "locks").mkdir(parents=True)
    (rt / "sweeps").mkdir(parents=True)
    (rt / "telemetry").mkdir(parents=True)
    (rt / "vacuum_cache").mkdir(parents=True)
    (rt / "sessions").mkdir(parents=True)
    (rt / "reports").mkdir(parents=True)
    (rt / "archived-docs").mkdir(parents=True)
    (rt / "archived-docs" / "workspaces").mkdir(parents=True)

    # ── KEEP: live DB files
    (rt / "traces" / "orchestrator-traces.db").write_text("db")
    (rt / "wiring" / "contract_validation_audit.db").write_text("db")
    (rt / "intelligence" / "intelligence_audit.db").write_text("db")
    (rt / "audit.db").write_text("db")
    (rt / "audit.db-shm").write_text("shm")
    (rt / "audit.db-wal").write_text("wal")

    # ── KEEP: health cache + setup script
    (rt / "health_cache" / "file_cache.json").write_text('{"x":1}')
    (rt / "setup-mcp.py").write_text("# setup")

    # ── DELETE: stale archived-docs
    (rt / "archived-docs" / "workspaces" / "chat01.md").write_text("# old chat")
    (rt / "archived-docs" / "workspaces" / "PHASE-53-STATUS-SNAPSHOT-2026-02-09.txt").write_text("old")

    # ── DELETE: stale log files
    (rt / "setup.log").write_text("log line\n")
    (rt / "mcp-self-healing.log").write_text("- fix: ok\n")

    # ── DELETE: stale report JSON
    (rt / "reports" / "phase-38-readiness-20260221-104928.json").write_text('{"ok":true}')
    (rt / "reports" / "phase-38-readiness-20260221-104933.json").write_text('{"ok":true}')

    # ── DELETE: stale session markdown
    (rt / "sessions" / "mcp-production-readiness-summary.md").write_text("# stale")

    return tmp_path


@pytest.fixture()
def vac(runtime: Path) -> object:
    """Instantiated VacuumOrchestrator on the runtime fixture workspace."""
    from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

    return VacuumOrchestrator(runtime)


# ─────────────────────────────────────────────────────────────────────────────
# Interface contract
# ─────────────────────────────────────────────────────────────────────────────


class TestRunRuntimeCleanupInterface:
    """run_runtime_cleanup() exists and returns the right shape."""

    def test_method_exists(self, vac: object) -> None:
        assert hasattr(vac, "run_runtime_cleanup"), (
            "VacuumOrchestrator must expose run_runtime_cleanup()"
        )

    def test_returns_list(self, vac: object) -> None:
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        result = vac.run_runtime_cleanup()  # type: ignore[union-attr]
        assert isinstance(result, list)

    def test_dry_run_returns_list(self, vac: object) -> None:
        result = vac.run_runtime_cleanup(dry_run=True)  # type: ignore[union-attr]
        assert isinstance(result, list)

    def test_dry_run_deletes_nothing(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup(dry_run=True)  # type: ignore[union-attr]
        rt = runtime / ".cortex-runtime"
        # All stale files must still be present
        assert (rt / "setup.log").exists()
        assert (rt / "mcp-self-healing.log").exists()
        assert (rt / "sessions" / "mcp-production-readiness-summary.md").exists()


# ─────────────────────────────────────────────────────────────────────────────
# Stale file deletion
# ─────────────────────────────────────────────────────────────────────────────


class TestRuntimeLogCleanup:
    """Stale *.log files at .cortex-runtime/ root are deleted."""

    def test_setup_log_deleted(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        assert not (runtime / ".cortex-runtime" / "setup.log").exists()

    def test_mcp_healing_log_deleted(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        assert not (runtime / ".cortex-runtime" / "mcp-self-healing.log").exists()

    def test_operations_include_log_deletes(self, vac: object) -> None:
        results = vac.run_runtime_cleanup()  # type: ignore[union-attr]
        deleted = [r.source.name for r in results if r.success and r.op_type == "delete"]
        assert "setup.log" in deleted or "mcp-self-healing.log" in deleted


class TestRuntimeReportCleanup:
    """Stale report JSON files in .cortex-runtime/reports/ are deleted."""

    def test_stale_report_json_deleted(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        reports_dir = runtime / ".cortex-runtime" / "reports"
        remaining = list(reports_dir.glob("*.json"))
        assert remaining == [], f"Expected no JSON reports, found: {remaining}"

    def test_reports_dir_emptied(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        reports_dir = runtime / ".cortex-runtime" / "reports"
        # Either the dir is gone (removed as empty) or it exists but has no files
        if reports_dir.exists():
            assert not any(reports_dir.iterdir())


class TestRuntimeSessionCleanup:
    """Stale session markdown files in .cortex-runtime/sessions/ are deleted."""

    def test_session_markdown_deleted(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        sessions_dir = runtime / ".cortex-runtime" / "sessions"
        remaining = list(sessions_dir.glob("*.md"))
        assert remaining == [], f"Stale session .md found: {remaining}"


class TestRuntimeArchivedDocsCleanup:
    """Stale files inside .cortex-runtime/archived-docs/ are deleted."""

    def test_archived_chat_deleted(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        f = runtime / ".cortex-runtime" / "archived-docs" / "workspaces" / "chat01.md"
        assert not f.exists()

    def test_archived_snapshot_txt_deleted(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        f = (
            runtime
            / ".cortex-runtime"
            / "archived-docs"
            / "workspaces"
            / "PHASE-53-STATUS-SNAPSHOT-2026-02-09.txt"
        )
        assert not f.exists()


# ─────────────────────────────────────────────────────────────────────────────
# KEEP: canonical runtime artifacts must survive
# ─────────────────────────────────────────────────────────────────────────────


class TestRuntimeKeptArtifacts:
    """Live DB files, health cache, and setup-mcp.py must NOT be deleted."""

    def test_orchestrator_traces_db_kept(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        assert (runtime / ".cortex-runtime" / "traces" / "orchestrator-traces.db").exists()

    def test_wiring_db_kept(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        assert (runtime / ".cortex-runtime" / "wiring" / "contract_validation_audit.db").exists()

    def test_intelligence_db_kept(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        assert (runtime / ".cortex-runtime" / "intelligence" / "intelligence_audit.db").exists()

    def test_root_audit_db_kept(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        assert (runtime / ".cortex-runtime" / "audit.db").exists()

    def test_audit_db_shm_kept(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        assert (runtime / ".cortex-runtime" / "audit.db-shm").exists()

    def test_audit_db_wal_kept(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        assert (runtime / ".cortex-runtime" / "audit.db-wal").exists()

    def test_health_cache_json_kept(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        assert (runtime / ".cortex-runtime" / "health_cache" / "file_cache.json").exists()

    def test_setup_mcp_py_kept(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        assert (runtime / ".cortex-runtime" / "setup-mcp.py").exists()


# ─────────────────────────────────────────────────────────────────────────────
# Empty directory cleanup
# ─────────────────────────────────────────────────────────────────────────────


class TestRuntimeEmptyDirCleanup:
    """Empty runtime subdirectories are pruned."""

    def test_empty_sweeps_dir_removed(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        sweeps = runtime / ".cortex-runtime" / "sweeps"
        assert not sweeps.exists(), "Empty sweeps/ dir should be removed"

    def test_empty_telemetry_dir_removed(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        telemetry = runtime / ".cortex-runtime" / "telemetry"
        assert not telemetry.exists(), "Empty telemetry/ dir should be removed"

    def test_empty_vacuum_cache_dir_removed(self, vac: object, runtime: Path) -> None:
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        vc = runtime / ".cortex-runtime" / "vacuum_cache"
        assert not vc.exists(), "Empty vacuum_cache/ dir should be removed"

    def test_non_empty_dir_kept(self, vac: object, runtime: Path) -> None:
        """traces/ has a .db file — must not be removed."""
        vac.run_runtime_cleanup()  # type: ignore[union-attr]
        assert (runtime / ".cortex-runtime" / "traces").exists()


# ─────────────────────────────────────────────────────────────────────────────
# OperationResult shape
# ─────────────────────────────────────────────────────────────────────────────


class TestOperationResultShape:
    """Each returned OperationResult has the required attributes."""

    def test_results_have_op_type(self, vac: object) -> None:
        results = vac.run_runtime_cleanup()  # type: ignore[union-attr]
        for r in results:
            assert hasattr(r, "op_type"), f"Missing op_type on {r}"

    def test_results_have_source(self, vac: object) -> None:
        results = vac.run_runtime_cleanup()  # type: ignore[union-attr]
        for r in results:
            assert hasattr(r, "source"), f"Missing source on {r}"

    def test_results_have_success(self, vac: object) -> None:
        results = vac.run_runtime_cleanup()  # type: ignore[union-attr]
        for r in results:
            assert hasattr(r, "success"), f"Missing success on {r}"

    def test_all_operations_succeed(self, vac: object) -> None:
        results = vac.run_runtime_cleanup()  # type: ignore[union-attr]
        failures = [r for r in results if not r.success]
        assert failures == [], f"Unexpected failures: {failures}"
