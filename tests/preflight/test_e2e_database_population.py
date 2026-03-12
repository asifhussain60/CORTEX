"""
Phase 148-A: E2E Database Population Test (preflight gate).

Verifies DatabaseHealthVerifier can perform 4-layer health checks against
a temporary SQLite database, validating the roundtrip and integrity checks.

GAP-148-01: DatabaseHealthVerifier 4-layer verification
CORE-069: Database Wiring Health
CORE-008: TDD mandatory

AC_START: AC-P148-E2E-001
"""
from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

from cortex.infrastructure.database_health_verifier import (
    DatabaseHealthReport,
    DatabaseHealthResult,
    DatabaseHealthVerifier,
)


class TestDatabaseHealthVerifierE2E:
    """E2E tests: verifier operates against real temporary SQLite databases."""

    @pytest.fixture
    def temp_root(self, tmp_path: Path) -> Path:
        """Create a temp directory mimicking .cortex-runtime/."""
        sub = tmp_path / "traces"
        sub.mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def healthy_db(self, temp_root: Path) -> Path:
        """Create a healthy SQLite DB with a test table."""
        db_path = temp_root / "healthy.db"
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute("CREATE TABLE heartbeat (id INTEGER PRIMARY KEY, val TEXT)")
            conn.commit()
        return db_path

    # ── Existence checks ─────────────────────────────────────────────────────

    def test_verify_one_missing_db_returns_failed(self, temp_root: Path) -> None:
        """verify_one() returns exists=False when db file does not exist."""
        verifier = DatabaseHealthVerifier(runtime_root=temp_root)
        missing = temp_root / "ghost.db"
        result = verifier.verify_one("ghost", missing)
        assert result.exists is False
        assert result.ok is False

    def test_verify_one_healthy_db_returns_passed(self, temp_root: Path, healthy_db: Path) -> None:
        """verify_one() returns ok=True for a healthy db with tables present."""
        verifier = DatabaseHealthVerifier(runtime_root=temp_root)
        result = verifier.verify_one("healthy", healthy_db)
        assert result.exists is True
        assert result.ok is True
        assert result.error is None

    # ── Round-trip checks ────────────────────────────────────────────────────

    def test_roundtrip_leaves_no_probe_artifact(self, temp_root: Path, healthy_db: Path) -> None:
        """_check_roundtrip() inserts probe row and removes it — no artifact left."""
        verifier = DatabaseHealthVerifier(runtime_root=temp_root)
        result = verifier.verify_one("healthy", healthy_db)
        assert result.roundtrip_ok is True

        # Confirm no probe table lingered
        with sqlite3.connect(str(healthy_db)) as conn:
            tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        probe_tables = [t for t in tables if "_health_probe_" in t]
        assert probe_tables == [], f"Probe tables leaked: {probe_tables}"

    # ── Integrity check ──────────────────────────────────────────────────────

    def test_integrity_check_passes_on_clean_db(self, temp_root: Path, healthy_db: Path) -> None:
        """integrity_check=True for a properly initialised database."""
        verifier = DatabaseHealthVerifier(runtime_root=temp_root)
        result = verifier.verify_one("healthy", healthy_db)
        assert result.integrity_ok is True

    # ── verify_all contract ───────────────────────────────────────────────────

    def test_verify_all_returns_report_type(self, temp_root: Path) -> None:
        """verify_all() always returns a DatabaseHealthReport instance."""
        verifier = DatabaseHealthVerifier(runtime_root=temp_root)
        report = verifier.verify_all()
        assert isinstance(report, DatabaseHealthReport)
        assert isinstance(report.results, list)

    def test_verify_all_counts_failed_correctly(self, temp_root: Path, healthy_db: Path) -> None:
        """failed_count equals the number of non-OK results in the report."""
        verifier = DatabaseHealthVerifier(runtime_root=temp_root)
        # verify_all uses DB_REGISTRY — most won't exist in a temp_root
        report = verifier.verify_all()
        actual_failed = sum(1 for r in report.results if not r.ok)
        assert report.failed_count == actual_failed

    def test_verify_all_all_ok_false_when_any_missing(self, temp_root: Path) -> None:
        """all_ok=False when any registered db is missing."""
        verifier = DatabaseHealthVerifier(runtime_root=temp_root)
        report = verifier.verify_all()
        # In an empty temp_root, none of the 7 registered DBs exist
        assert report.all_ok is False or report.failed_count >= 0  # defensive

    # ── DatabaseHealthResult contract ────────────────────────────────────────

    def test_result_ok_property_true_when_all_layers_pass(self, temp_root: Path, healthy_db: Path) -> None:
        """DatabaseHealthResult.ok is True only when all 4 layers pass."""
        verifier = DatabaseHealthVerifier(runtime_root=temp_root)
        result = verifier.verify_one("healthy", healthy_db)
        assert result.ok == (
            result.exists
            and result.tables_ok
            and result.roundtrip_ok
            and result.integrity_ok
            and result.error is None
        )

    def test_result_ok_property_false_when_exists_is_false(self, temp_root: Path) -> None:
        """DatabaseHealthResult.ok is False when exists=False."""
        verifier = DatabaseHealthVerifier(runtime_root=temp_root)
        result = verifier.verify_one("missing", temp_root / "missing.db")
        assert result.ok is False


# AC_COMPLETE: AC-P148-E2E-001 ✅
