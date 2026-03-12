"""
Tests for DatabaseHealthVerifier — Phase 148-a.

TDD RED phase: all tests must fail before implementation exists.
"""
from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest


class TestDatabaseHealthResultDataclass:
    """Tests for DatabaseHealthResult dataclass."""

    def test_database_health_result_has_required_fields(self) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthResult
        r = DatabaseHealthResult(
            db_name="test",
            path="/tmp/test.db",
            exists=True,
            tables_ok=True,
            roundtrip_ok=True,
            integrity_ok=True,
            error=None,
        )
        assert r.db_name == "test"
        assert r.path == "/tmp/test.db"
        assert r.exists is True
        assert r.tables_ok is True
        assert r.roundtrip_ok is True
        assert r.integrity_ok is True
        assert r.error is None

    def test_healthy_result_ok_property_true(self) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthResult
        r = DatabaseHealthResult("x", "/p", True, True, True, True, None)
        assert r.ok is True

    def test_result_ok_false_when_not_exists(self) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthResult
        r = DatabaseHealthResult("x", "/p", False, False, False, False, "not found")
        assert r.ok is False

    def test_result_ok_false_when_tables_fail(self) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthResult
        r = DatabaseHealthResult("x", "/p", True, False, True, True, "table missing")
        assert r.ok is False

    def test_result_ok_false_when_roundtrip_fails(self) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthResult
        r = DatabaseHealthResult("x", "/p", True, True, False, True, "write failed")
        assert r.ok is False

    def test_result_ok_false_when_integrity_fails(self) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthResult
        r = DatabaseHealthResult("x", "/p", True, True, True, False, "corrupt")
        assert r.ok is False


class TestDatabaseHealthReportDataclass:
    """Tests for DatabaseHealthReport dataclass."""

    def test_empty_report_all_ok_true(self) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthReport
        r = DatabaseHealthReport(results=[], all_ok=True, failed_count=0)
        assert r.all_ok is True
        assert r.failed_count == 0

    def test_report_all_ok_reflects_failed_count(self) -> None:
        from cortex.infrastructure.database_health_verifier import (
            DatabaseHealthReport,
            DatabaseHealthResult,
        )
        bad = DatabaseHealthResult("x", "/p", False, False, False, False, "err")
        r = DatabaseHealthReport(results=[bad], all_ok=False, failed_count=1)
        assert r.all_ok is False
        assert r.failed_count == 1


class TestDatabaseHealthVerifier:
    """Tests for DatabaseHealthVerifier class."""

    def test_verifier_instantiates(self) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthVerifier
        v = DatabaseHealthVerifier()
        assert v is not None

    def test_verifier_instantiates_with_custom_root(self, tmp_path: Path) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthVerifier
        v = DatabaseHealthVerifier(runtime_root=tmp_path)
        assert v is not None

    def test_verify_one_returns_database_health_result(self, tmp_path: Path) -> None:
        from cortex.infrastructure.database_health_verifier import (
            DatabaseHealthResult,
            DatabaseHealthVerifier,
        )
        v = DatabaseHealthVerifier(runtime_root=tmp_path)
        result = v.verify_one("test-db", tmp_path / "test.db")
        assert isinstance(result, DatabaseHealthResult)

    def test_verify_one_missing_db_returns_not_exists(self, tmp_path: Path) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthVerifier
        v = DatabaseHealthVerifier(runtime_root=tmp_path)
        result = v.verify_one("ghost", tmp_path / "ghost.db")
        assert result.exists is False
        assert result.ok is False

    def test_verify_one_healthy_db_all_layers_pass(self, tmp_path: Path) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthVerifier

        # Create a real SQLite database with a known table
        db_path = tmp_path / "healthy.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE _health_check (id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()

        v = DatabaseHealthVerifier(runtime_root=tmp_path)
        result = v.verify_one("healthy", db_path)
        assert result.exists is True
        assert result.roundtrip_ok is True
        assert result.integrity_ok is True

    def test_verify_one_corrupt_db_fails_integrity(self, tmp_path: Path) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthVerifier

        # Write garbage bytes that SQLite's integrity_check will reject
        db_path = tmp_path / "corrupt.db"
        db_path.write_bytes(b"NOT A VALID SQLITE DATABASE\x00" * 20)

        v = DatabaseHealthVerifier(runtime_root=tmp_path)
        result = v.verify_one("corrupt", db_path)
        # exists=True but integrity_ok=False
        assert result.exists is True
        assert result.integrity_ok is False
        assert result.ok is False

    def test_verify_all_returns_database_health_report(self, tmp_path: Path) -> None:
        from cortex.infrastructure.database_health_verifier import (
            DatabaseHealthReport,
            DatabaseHealthVerifier,
        )
        v = DatabaseHealthVerifier(runtime_root=tmp_path)
        report = v.verify_all()
        assert isinstance(report, DatabaseHealthReport)

    def test_verify_all_covers_all_db_registry_entries(self, tmp_path: Path) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthVerifier
        from cortex.infrastructure.env_initializer import DB_REGISTRY

        v = DatabaseHealthVerifier(runtime_root=tmp_path)
        report = v.verify_all()
        # Should check all databases registered in DB_REGISTRY
        assert len(report.results) == len(DB_REGISTRY)

    def test_verify_all_all_ok_false_when_dbs_missing(self, tmp_path: Path) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthVerifier
        # tmp_path has no databases → all missing → all_ok=False
        v = DatabaseHealthVerifier(runtime_root=tmp_path)
        report = v.verify_all()
        assert report.all_ok is False

    def test_verify_all_failed_count_matches_missing_dbs(self, tmp_path: Path) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthVerifier
        from cortex.infrastructure.env_initializer import DB_REGISTRY

        v = DatabaseHealthVerifier(runtime_root=tmp_path)
        report = v.verify_all()
        assert report.failed_count == len(DB_REGISTRY)

    def test_verify_one_roundtrip_ok_writes_and_reads(self, tmp_path: Path) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthVerifier

        db_path = tmp_path / "roundtrip.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE _health_check (id INTEGER PRIMARY KEY, val TEXT)")
        conn.commit()
        conn.close()

        v = DatabaseHealthVerifier(runtime_root=tmp_path)
        result = v.verify_one("rt", db_path)
        assert result.roundtrip_ok is True

    def test_verify_one_db_name_captured_in_result(self, tmp_path: Path) -> None:
        from cortex.infrastructure.database_health_verifier import DatabaseHealthVerifier
        v = DatabaseHealthVerifier(runtime_root=tmp_path)
        result = v.verify_one("my-special-db", tmp_path / "special.db")
        assert result.db_name == "my-special-db"
