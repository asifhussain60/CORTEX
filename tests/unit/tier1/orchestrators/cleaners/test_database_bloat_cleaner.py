"""
Golden Tests: DatabaseBloatCleaner — SQLite VACUUM and Cleanup

TDD-first tests driving DatabaseBloatCleaner implementation.
Tests VACUUM, WAL checkpoint, retention purge, orphan/duplicate deletion.

Authority: AC-SQLITE-HYGIENE-001
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
Phase: Phase 48 — Health-Vacuum Pipeline (SQLite extension)
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any

import pytest

from cortex_intelligence.memory.tier1_learned.orchestrators.cleaners.database_bloat import (
    DatabaseBloatCleaner,
)
from cortex_intelligence.memory.tier1_learned.orchestrators.cleaners.base import (
    Analysis,
    Report,
    RollbackResult,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Create workspace with database directories.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        Path to workspace root.
    """
    (tmp_path / "cortex_intelligence" / "state").mkdir(parents=True)
    (tmp_path / "cortex_intelligence" / "intelligence").mkdir(parents=True)
    (tmp_path / ".cortex-runtime" / "traces").mkdir(parents=True)
    (tmp_path / "cortex" / "wiring" / "registry").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def cleaner(workspace: Path) -> DatabaseBloatCleaner:
    """Create a DatabaseBloatCleaner instance.

    Args:
        workspace: Workspace root path.

    Returns:
        DatabaseBloatCleaner configured for workspace.
    """
    return DatabaseBloatCleaner({
        "repo_root": str(workspace),
        "dry_run": False,
        "verbose": False,
        "retention_days": 30,
    })


@pytest.fixture
def dry_run_cleaner(workspace: Path) -> DatabaseBloatCleaner:
    """Create a dry-run DatabaseBloatCleaner instance.

    Args:
        workspace: Workspace root path.

    Returns:
        DatabaseBloatCleaner in dry_run mode.
    """
    return DatabaseBloatCleaner({
        "repo_root": str(workspace),
        "dry_run": True,
        "verbose": False,
    })


def _create_db(path: Path, schema: str, rows: int = 0) -> None:
    """Helper to create a test database.

    Args:
        path: Database file path.
        schema: CREATE TABLE SQL.
        rows: Number of rows to insert.
    """
    conn = sqlite3.connect(str(path))
    conn.execute(schema)
    for i in range(rows):
        conn.execute(
            "INSERT INTO test_data (value, ts) VALUES (?, ?)",
            (f"row_{i}", f"2026-01-{(i % 28) + 1:02d}T00:00:00"),
        )
    conn.commit()
    conn.close()


# =============================================================================
# PROPERTIES
# =============================================================================


class TestCleanerProperties:
    """Verify cleaner interface properties."""

    def test_name(self, cleaner: DatabaseBloatCleaner) -> None:
        """Cleaner should have correct name."""
        assert cleaner.name == "Database Bloat Cleaner"

    def test_version(self, cleaner: DatabaseBloatCleaner) -> None:
        """Cleaner should have semantic version."""
        assert cleaner.version == "1.0.0"

    def test_domain(self, cleaner: DatabaseBloatCleaner) -> None:
        """Cleaner should have correct domain."""
        assert cleaner.domain == "database_bloat"


# =============================================================================
# ANALYZE
# =============================================================================


class TestAnalyze:
    """Tests for analyze() method."""

    def test_empty_workspace(self, cleaner: DatabaseBloatCleaner) -> None:
        """Analyze on workspace with no databases should return zero issues."""
        result = cleaner.analyze()

        assert isinstance(result, Analysis)
        assert result.cleaner_id == "database_bloat"
        assert result.files_scanned == 0
        assert result.issues_found == 0

    def test_healthy_database_no_actions(
        self, cleaner: DatabaseBloatCleaner, workspace: Path
    ) -> None:
        """Healthy database should produce minimal or no actions."""
        db_path = workspace / "cortex_intelligence" / "state" / "healthy.db"
        schema = "CREATE TABLE test_data (id INTEGER PRIMARY KEY, value TEXT, ts TEXT)"
        _create_db(db_path, schema, rows=5)

        result = cleaner.analyze()

        assert result.files_scanned >= 1

    def test_discovers_wal_orphans(
        self, cleaner: DatabaseBloatCleaner, workspace: Path
    ) -> None:
        """Should detect WAL/SHM orphan files."""
        db_dir = workspace / "cortex_intelligence" / "state"
        (db_dir / "test.db-wal").write_bytes(b"\x00" * 50)
        (db_dir / "test.db-shm").write_bytes(b"\x00" * 50)

        result = cleaner.analyze()

        orphan_actions = [
            a for a in result.plan["actions"]
            if a["type"] == "delete_orphan"
        ]
        assert len(orphan_actions) >= 2

    def test_discovers_duplicates(
        self, cleaner: DatabaseBloatCleaner, workspace: Path
    ) -> None:
        """Should detect duplicate databases with same schema."""
        schema = "CREATE TABLE test_data (id INTEGER PRIMARY KEY, value TEXT, ts TEXT)"

        db1 = workspace / "cortex_intelligence" / "intelligence" / "audit.db"
        _create_db(db1, schema, rows=10)

        dup_dir = workspace / "cortex" / "orchestrators" / "intelligence"
        dup_dir.mkdir(parents=True, exist_ok=True)
        db2 = dup_dir / "audit.db"
        _create_db(db2, schema, rows=3)

        result = cleaner.analyze()

        dup_actions = [
            a for a in result.plan["actions"]
            if a["type"] == "delete_duplicate"
        ]
        assert len(dup_actions) >= 1


# =============================================================================
# EXECUTE
# =============================================================================


class TestExecute:
    """Tests for execute() method."""

    def test_vacuum_execution(
        self, cleaner: DatabaseBloatCleaner, workspace: Path
    ) -> None:
        """VACUUM action should succeed on valid database."""
        db_path = workspace / "cortex_intelligence" / "state" / "to_vacuum.db"
        schema = "CREATE TABLE test_data (id INTEGER PRIMARY KEY, value TEXT, ts TEXT)"
        _create_db(db_path, schema, rows=5)

        plan: Dict[str, Any] = {
            "actions": [{"type": "vacuum", "path": str(db_path)}],
            "retention_days": 30,
        }
        result = cleaner.execute(plan)

        assert isinstance(result, Report)
        assert result.status == "SUCCESS"
        assert result.changes["vacuumed"] == 1

    def test_checkpoint_execution(
        self, cleaner: DatabaseBloatCleaner, workspace: Path
    ) -> None:
        """WAL checkpoint action should succeed."""
        db_path = workspace / "cortex_intelligence" / "state" / "wal_db.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY)")
        conn.execute("INSERT INTO t VALUES (1)")
        conn.commit()
        conn.close()

        plan: Dict[str, Any] = {
            "actions": [{"type": "wal_checkpoint", "path": str(db_path)}],
            "retention_days": 30,
        }
        result = cleaner.execute(plan)

        assert result.status == "SUCCESS"
        assert result.changes["checkpointed"] == 1

    def test_orphan_deletion(
        self, cleaner: DatabaseBloatCleaner, workspace: Path
    ) -> None:
        """Orphan WAL/SHM files should be deleted."""
        orphan = workspace / "cortex_intelligence" / "state" / "old.db-wal"
        orphan.write_bytes(b"\x00" * 50)

        plan: Dict[str, Any] = {
            "actions": [{"type": "delete_orphan", "path": str(orphan)}],
            "retention_days": 30,
        }
        result = cleaner.execute(plan)

        assert result.status == "SUCCESS"
        assert result.changes["orphans_deleted"] == 1
        assert not orphan.exists()

    def test_dry_run_no_changes(
        self, dry_run_cleaner: DatabaseBloatCleaner, workspace: Path
    ) -> None:
        """Dry run should not modify any files."""
        orphan = workspace / "cortex_intelligence" / "state" / "keep.db-wal"
        orphan.write_bytes(b"\x00" * 50)

        plan: Dict[str, Any] = {
            "actions": [{"type": "delete_orphan", "path": str(orphan)}],
            "retention_days": 30,
        }
        result = dry_run_cleaner.execute(plan)

        assert result.status == "SUCCESS"
        assert orphan.exists()  # File should still exist

    def test_error_handling(
        self, cleaner: DatabaseBloatCleaner, workspace: Path
    ) -> None:
        """Failed action should report PARTIAL or FAILED status."""
        plan: Dict[str, Any] = {
            "actions": [
                {"type": "vacuum", "path": "/nonexistent/path.db"},
            ],
            "retention_days": 30,
        }
        result = cleaner.execute(plan)

        assert result.status == "FAILED"
        assert len(result.errors) >= 1


# =============================================================================
# ROLLBACK
# =============================================================================


class TestRollback:
    """Tests for rollback() method."""

    def test_rollback_returns_partial(self, cleaner: DatabaseBloatCleaner) -> None:
        """Rollback should indicate limited support."""
        result = cleaner.rollback()

        assert isinstance(result, RollbackResult)
        assert result.status == "PARTIAL"
        assert result.files_restored == 0
        assert len(result.errors) >= 1


# =============================================================================
# RETENTION PURGE
# =============================================================================


class TestRetentionPurge:
    """Tests for retention purge execution."""

    def test_purges_old_rows(
        self, cleaner: DatabaseBloatCleaner, workspace: Path
    ) -> None:
        """Should delete rows older than retention threshold."""
        db_path = workspace / "cortex_intelligence" / "state" / "retention.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute(
            "CREATE TABLE logs (id INTEGER PRIMARY KEY, data TEXT, timestamp TEXT)"
        )
        # Insert old rows (>30 days ago)
        conn.execute(
            "INSERT INTO logs (data, timestamp) VALUES ('old', '2025-01-01T00:00:00')"
        )
        # Insert recent rows
        conn.execute(
            "INSERT INTO logs (data, timestamp) VALUES ('new', '2026-02-18T00:00:00')"
        )
        conn.commit()
        conn.close()

        plan: Dict[str, Any] = {
            "actions": [{
                "type": "retention_purge",
                "path": str(db_path),
                "table": "logs",
                "column": "timestamp",
            }],
            "retention_days": 30,
        }
        result = cleaner.execute(plan)

        assert result.status == "SUCCESS"
        assert result.changes["rows_purged"] >= 1

        # Verify old row is gone, new row remains
        conn = sqlite3.connect(str(db_path))
        remaining = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
        conn.close()
        assert remaining == 1


# =============================================================================
# TEARDOWN VERIFICATION
# =============================================================================


class TestTeardown:
    """Verify all SQLite connections are properly closed."""

    def test_no_leaked_connections(
        self, cleaner: DatabaseBloatCleaner, workspace: Path
    ) -> None:
        """After analyze+execute, no connections should be leaked."""
        db_path = workspace / "cortex_intelligence" / "state" / "leak_test.db"
        schema = "CREATE TABLE test_data (id INTEGER PRIMARY KEY, value TEXT, ts TEXT)"
        _create_db(db_path, schema, rows=5)

        analysis = cleaner.analyze()
        cleaner.execute(analysis.plan)

        # Should be able to get exclusive lock (proves no leaks)
        conn = sqlite3.connect(str(db_path))
        conn.execute("BEGIN EXCLUSIVE")
        conn.execute("SELECT 1")
        conn.rollback()
        conn.close()
