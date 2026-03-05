"""
Tests for cortex.infrastructure.env_initializer — Phase 109

CORE-008: Tests written before/alongside implementation.
Tests cover:
  - Fresh initialization (all databases created)
  - Idempotent re-initialization (no errors on second run)
  - Clean mode (databases deleted and recreated)
  - Corrupt database detection and auto-rebuild
  - Schema migration (missing columns added)
  - Verify mode (read-only check)
  - Cross-platform path handling
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from cortex.infrastructure.env_initializer import (
    DB_REGISTRY,
    RUNTIME_DIRS,
    EnvironmentInitializer,
    initialize_runtime_environment,
    verify_runtime_environment,
)


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture()
def tmp_runtime(tmp_path: Path) -> Path:
    """Isolated .cortex-runtime/ directory for each test."""
    return tmp_path / ".cortex-runtime"


@pytest.fixture()
def initializer(tmp_runtime: Path) -> EnvironmentInitializer:
    return EnvironmentInitializer(runtime_root=tmp_runtime, verbose=True)


# ===========================================================================
# Directory creation
# ===========================================================================


class TestDirectoryCreation:
    def test_creates_runtime_root(self, initializer: EnvironmentInitializer, tmp_runtime: Path) -> None:
        result = initializer.setup()
        assert tmp_runtime.exists()
        assert result.ok

    def test_creates_all_subdirs(self, initializer: EnvironmentInitializer, tmp_runtime: Path) -> None:
        initializer.setup()
        for subdir in RUNTIME_DIRS:
            assert (tmp_runtime / subdir).is_dir(), f"Missing: {subdir}"

    def test_idempotent_dir_creation(self, initializer: EnvironmentInitializer) -> None:
        # Run twice — no error on second pass
        r1 = initializer.setup()
        r2 = initializer.setup()
        assert r1.ok
        assert r2.ok

    def test_counts_only_new_dirs(self, initializer: EnvironmentInitializer) -> None:
        r1 = initializer.setup()
        r2 = initializer.setup()
        assert r1.dirs_created > 0
        assert r2.dirs_created == 0  # Nothing new on second pass


# ===========================================================================
# Database initialization
# ===========================================================================


class TestDatabaseInit:
    def test_all_databases_created(self, initializer: EnvironmentInitializer, tmp_runtime: Path) -> None:
        result = initializer.setup()
        assert result.ok
        for db_name, db_spec in DB_REGISTRY.items():
            db_path = tmp_runtime / db_spec["path"]
            assert db_path.exists(), f"Missing: {db_name} at {db_path}"

    def test_orchestrator_traces_tables(self, initializer: EnvironmentInitializer, tmp_runtime: Path) -> None:
        initializer.setup()
        db_path = tmp_runtime / "traces/orchestrator-traces.db"
        with sqlite3.connect(str(db_path)) as conn:
            tables = {
                r[0]
                for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
        expected = {
            "trace_metadata", "trace_flush_log", "trace_master",
            "audit_sessions", "audit_stage_log", "audit_violations", "audit_certifications",
            "workflow_runs", "workflow_cycles",
            "trace_registry_loads", "trace_response_selection",
            "trace_governance_checks", "trace_output_hashes",
        }
        missing = expected - tables
        assert not missing, f"Missing tables in orchestrator-traces.db: {missing}"

    def test_rca_store_tables(self, initializer: EnvironmentInitializer, tmp_runtime: Path) -> None:
        initializer.setup()
        db_path = tmp_runtime / "rca/rca_store.db"
        with sqlite3.connect(str(db_path)) as conn:
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        expected = {"rca_analyses", "prevention_rules", "recurrence_signatures", "recurrence_incidents"}
        assert expected <= tables

    def test_audit_db_tables(self, initializer: EnvironmentInitializer, tmp_runtime: Path) -> None:
        initializer.setup()
        db_path = tmp_runtime / "audit.db"
        with sqlite3.connect(str(db_path)) as conn:
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        expected = {"audit_events", "orchestrator_traces", "governance_checks", "phase_progress", "audit_log"}
        assert expected <= tables

    def test_conversations_db_tables(self, initializer: EnvironmentInitializer, tmp_runtime: Path) -> None:
        initializer.setup()
        db_path = tmp_runtime / "state/conversations.db"
        with sqlite3.connect(str(db_path)) as conn:
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        assert {"conversations", "turn_records"} <= tables

    def test_governance_db_tables(self, initializer: EnvironmentInitializer, tmp_runtime: Path) -> None:
        initializer.setup()
        db_path = tmp_runtime / "governance.db"
        with sqlite3.connect(str(db_path)) as conn:
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        assert "scaffolder_audit_log" in tables

    def test_wiring_db_tables(self, initializer: EnvironmentInitializer, tmp_runtime: Path) -> None:
        initializer.setup()
        db_path = tmp_runtime / "wiring/contract_validation_audit.db"
        with sqlite3.connect(str(db_path)) as conn:
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        assert {"validation_audit", "contract_versions"} <= tables

    def test_intelligence_audit_tables(self, initializer: EnvironmentInitializer, tmp_runtime: Path) -> None:
        initializer.setup()
        db_path = tmp_runtime / "intelligence/intelligence_audit.db"
        with sqlite3.connect(str(db_path)) as conn:
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        assert "intelligence_audit" in tables

    def test_idempotent_double_init(self, initializer: EnvironmentInitializer) -> None:
        r1 = initializer.setup()
        r2 = initializer.setup()
        assert r1.ok
        assert r2.ok
        # Second pass creates no new tables
        for db in r2.databases:
            assert db.tables_created == 0, f"{db.name}: unexpected new tables on re-init"

    def test_wal_mode_on_traces_db(self, initializer: EnvironmentInitializer, tmp_runtime: Path) -> None:
        initializer.setup()
        db_path = tmp_runtime / "traces/orchestrator-traces.db"
        with sqlite3.connect(str(db_path)) as conn:
            mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert mode == "wal", "orchestrator-traces.db should use WAL mode"

    def test_wal_mode_on_audit_db(self, initializer: EnvironmentInitializer, tmp_runtime: Path) -> None:
        initializer.setup()
        db_path = tmp_runtime / "audit.db"
        with sqlite3.connect(str(db_path)) as conn:
            mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert mode == "wal", "audit.db should use WAL mode"


# ===========================================================================
# Clean mode
# ===========================================================================


class TestCleanMode:
    def test_clean_rebuilds_database(self, initializer: EnvironmentInitializer, tmp_runtime: Path) -> None:
        initializer.setup()
        # Insert a sentinel row — use explicit close so Windows releases the file lock
        db_path = tmp_runtime / "governance.db"
        _c = sqlite3.connect(str(db_path))
        try:
            _c.execute(
                "INSERT INTO scaffolder_audit_log (timestamp, operation, orchestrator_name, ac_marker, details) "
                "VALUES ('2026-01-01', 'TEST', 'test-orch', 'AC-TEST', 'sentinel')"
            )
            _c.commit()
        finally:
            _c.close()  # Explicit close — Python 'with conn:' only manages transactions, not lifetime
        # Clean rebuild
        result = initializer.setup(clean=True)
        assert result.ok
        # Sentinel row must be gone
        with sqlite3.connect(str(db_path)) as conn:
            count = conn.execute("SELECT COUNT(*) FROM scaffolder_audit_log").fetchone()[0]
        assert count == 0

    def test_clean_mode_marks_rebuilt(self, initializer: EnvironmentInitializer) -> None:
        initializer.setup()
        result = initializer.setup(clean=True)
        rebuilt_dbs = [db for db in result.databases if db.was_rebuilt]
        assert len(rebuilt_dbs) == len(DB_REGISTRY), "All DBs should be rebuilt in clean mode"


# ===========================================================================
# Corrupt database detection
# ===========================================================================


class TestCorruptionHandling:
    def test_corrupt_db_is_rebuilt(self, initializer: EnvironmentInitializer, tmp_runtime: Path) -> None:
        initializer.setup()
        # Force GC to release all SQLite connections before overwriting the file
        import gc
        gc.collect()
        db_path = tmp_runtime / "governance.db"
        db_path.write_bytes(b"This is not a valid SQLite database!!!") 

        # Re-initialize — must detect corruption and rebuild
        result = initializer.setup()
        assert result.ok

        # Find the govern DB result
        gov_result = next(db for db in result.databases if db.name == "governance")
        assert gov_result.was_corrupt
        assert gov_result.was_rebuilt

        # Database must be functional after rebuild
        with sqlite3.connect(str(db_path)) as conn:
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        assert "scaffolder_audit_log" in tables


# ===========================================================================
# Column migration
# ===========================================================================


class TestSchemaMigration:
    def test_missing_column_is_added(self, initializer: EnvironmentInitializer, tmp_runtime: Path) -> None:
        initializer.setup()
        # Drop a column by recreating the table without it (SQLite doesn't support DROP COLUMN pre-3.35)
        db_path = tmp_runtime / "governance.db"
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute("ALTER TABLE scaffolder_audit_log RENAME TO _old_scaffolder_audit_log")
            conn.execute("""
                CREATE TABLE scaffolder_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    orchestrator_name TEXT NOT NULL,
                    ac_marker TEXT NOT NULL
                    -- 'details' column intentionally omitted
                )
            """)
            conn.commit()

        # Re-initialize — must add 'details' column
        result = initializer.setup()
        assert result.ok

        gov_result = next(db for db in result.databases if db.name == "governance")
        assert gov_result.columns_added >= 1

        # Column must be present in actual schema
        with sqlite3.connect(str(db_path)) as conn:
            cols = {row[1] for row in conn.execute("PRAGMA table_info(scaffolder_audit_log)").fetchall()}
        assert "details" in cols


# ===========================================================================
# Verify mode
# ===========================================================================


class TestVerifyMode:
    def test_verify_fails_on_missing_env(self, tmp_runtime: Path) -> None:
        initializer = EnvironmentInitializer(runtime_root=tmp_runtime)
        ok, issues = initializer.verify()
        assert not ok
        assert len(issues) > 0

    def test_verify_passes_after_setup(self, initializer: EnvironmentInitializer) -> None:
        initializer.setup()
        ok, issues = initializer.verify()
        assert ok, f"Verify failed after setup: {issues}"
        assert not issues

    def test_verify_detects_missing_database(self, initializer: EnvironmentInitializer, tmp_runtime: Path) -> None:
        initializer.setup()
        import gc
        gc.collect()  # Ensure all SQLite connections are released on Windows
        (tmp_runtime / "governance.db").unlink()
        ok, issues = initializer.verify()
        assert not ok
        assert any("governance" in issue for issue in issues)


# ===========================================================================
# Convenience functions
# ===========================================================================


class TestConvenienceFunctions:
    def test_initialize_runtime_environment(self, tmp_runtime: Path) -> None:
        result = initialize_runtime_environment(runtime_root=tmp_runtime)
        assert result.ok

    def test_verify_runtime_environment(self, tmp_runtime: Path) -> None:
        initialize_runtime_environment(runtime_root=tmp_runtime)
        ok, issues = verify_runtime_environment(runtime_root=tmp_runtime)
        assert ok
        assert not issues

    def test_result_summary_string(self, tmp_runtime: Path) -> None:
        result = initialize_runtime_environment(runtime_root=tmp_runtime)
        summary = result.summary()
        assert "7/7" in summary or "databases" in summary

    def test_result_total_duration_measured(self, tmp_runtime: Path) -> None:
        result = initialize_runtime_environment(runtime_root=tmp_runtime)
        assert result.total_duration_ms > 0

    def test_db_registry_has_all_canonical_dbs(self) -> None:
        expected = {
            "orchestrator-traces", "rca-store", "audit",
            "governance", "conversations", "wiring-audit", "intelligence-audit"
        }
        assert set(DB_REGISTRY.keys()) == expected

    def test_runtime_dirs_complete(self) -> None:
        required = {"traces", "rca", "state", "wiring", "intelligence", "logs"}
        assert required <= set(RUNTIME_DIRS)


# ===========================================================================
# Performance
# ===========================================================================


class TestPerformance:
    def test_fresh_init_under_3_seconds(self, tmp_runtime: Path) -> None:
        import time
        t0 = time.monotonic()
        result = initialize_runtime_environment(runtime_root=tmp_runtime)
        elapsed = time.monotonic() - t0
        assert result.ok
        assert elapsed < 3.0, f"Fresh init took {elapsed:.2f}s — must be < 3s"

    def test_warm_verify_under_500ms(self, tmp_runtime: Path) -> None:
        import time
        initialize_runtime_environment(runtime_root=tmp_runtime)
        t0 = time.monotonic()
        ok, _ = verify_runtime_environment(runtime_root=tmp_runtime)
        elapsed = time.monotonic() - t0
        assert ok
        assert elapsed < 0.5, f"Warm verify took {elapsed:.2f}s — must be < 500ms"
