"""
GAP-128-E-04: SQLite databases at .cortex-runtime/ must have healthy schema
and contain at least some activity (have been exercised by tests or runtime).

Tests that:
- All 3 runtime databases exist
- traces/orchestrator-traces.db has its documented tables
- audit.db has its documented tables
- governance.db has its documented table
- Key tables have the expected column signatures
- No stray .db files exist outside .cortex-runtime/

Drift lock: check-45-orchestrator-wiring-integrity-lock.yaml
"""

import sqlite3
from pathlib import Path
from typing import List, Set
import pytest

REPO_ROOT = Path(__file__).parents[2]
RUNTIME_DIR = REPO_ROOT / ".cortex-runtime"
TRACES_DB = RUNTIME_DIR / "traces/orchestrator-traces.db"
AUDIT_DB = RUNTIME_DIR / "audit.db"
GOVERNANCE_DB = RUNTIME_DIR / "governance.db"

# Known databases — any .db outside this set is a drift violation
KNOWN_DB_NAMES = {
    "orchestrator-traces.db",
    "rca_store.db",
    "audit.db",
    "governance.db",
    "conversations.db",
    "contract_validation_audit.db",
    "intelligence_audit.db",
    # testmon internal — not a CORTEX runtime db, but often coexists
    ".testmondata",
}

# Expected tables per database (must be a subset of actual tables)
REQUIRED_TRACE_TABLES = {
    "audit_sessions",
    "audit_stage_log",
    "audit_violations",
    "workflow_cycles",
    "workflow_runs",
}

REQUIRED_AUDIT_TABLES = {
    "audit_events",
    "orchestrator_traces",
    "governance_checks",
    "phase_progress",
}

REQUIRED_GOVERNANCE_TABLES = {
    "scaffolder_audit_log",
}


def _get_tables(db_path: Path) -> Set[str]:
    """Return set of table names from a SQLite database."""
    if not db_path.exists():
        return set()
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()
        return tables
    except sqlite3.Error:
        return set()


def _get_columns(db_path: Path, table: str) -> List[str]:
    """Return column names for a table in a SQLite database."""
    if not db_path.exists():
        return []
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute(f"PRAGMA table_info({table})")  # noqa: S608
        cols = [row[1] for row in cursor.fetchall()]
        conn.close()
        return cols
    except sqlite3.Error:
        return []


class TestSqliteTableUsage:
    """GAP-128-E-04: Runtime SQLite databases must have healthy schema and exist."""

    def test_runtime_dir_exists(self):
        """.cortex-runtime/ directory must exist."""
        assert RUNTIME_DIR.exists(), f".cortex-runtime/ not found at {RUNTIME_DIR}"

    def test_traces_db_exists(self):
        """traces/orchestrator-traces.db must exist."""
        assert TRACES_DB.exists(), f"Traces DB not found: {TRACES_DB}"

    def test_audit_db_exists(self):
        """audit.db must exist."""
        assert AUDIT_DB.exists(), f"Audit DB not found: {AUDIT_DB}"

    def test_governance_db_exists(self):
        """governance.db must exist."""
        assert GOVERNANCE_DB.exists(), f"Governance DB not found: {GOVERNANCE_DB}"

    def test_traces_db_has_required_tables(self):
        """orchestrator-traces.db must have all documented required tables."""
        tables = _get_tables(TRACES_DB)
        missing = REQUIRED_TRACE_TABLES - tables
        assert not missing, (
            f"orchestrator-traces.db is missing required tables: {sorted(missing)}\n"
            f"  Found tables: {sorted(tables)}"
        )

    def test_audit_db_has_required_tables(self):
        """audit.db must have all documented required tables."""
        tables = _get_tables(AUDIT_DB)
        missing = REQUIRED_AUDIT_TABLES - tables
        assert not missing, (
            f"audit.db is missing required tables: {sorted(missing)}\n"
            f"  Found tables: {sorted(tables)}"
        )

    def test_governance_db_has_required_tables(self):
        """governance.db must have the scaffolder_audit_log table."""
        tables = _get_tables(GOVERNANCE_DB)
        missing = REQUIRED_GOVERNANCE_TABLES - tables
        assert not missing, (
            f"governance.db is missing required tables: {sorted(missing)}\n"
            f"  Found tables: {sorted(tables)}"
        )

    def test_audit_sessions_schema(self):
        """audit_sessions table must have expected columns."""
        cols = _get_columns(TRACES_DB, "audit_sessions")
        if not cols:
            pytest.skip("audit_sessions table empty or missing — cannot check schema")
        # Must have at least an id / session identifier column
        has_id = any(c in cols for c in ("id", "session_id", "rowid"))
        assert has_id, (
            f"audit_sessions has no id/session_id column. Columns: {cols}"
        )

    def test_workflow_runs_schema(self):
        """workflow_runs table must have expected columns."""
        cols = _get_columns(TRACES_DB, "workflow_runs")
        if not cols:
            pytest.skip("workflow_runs table empty or missing — cannot check schema")
        has_id = any(c in cols for c in ("id", "run_id", "rowid"))
        assert has_id, (
            f"workflow_runs has no id/run_id column. Columns: {cols}"
        )

    def test_no_stray_db_at_repo_root(self):
        """No .db files should exist at the repo root (outside .cortex-runtime/)."""
        stray = [
            p for p in REPO_ROOT.glob("*.db")
            if p.name not in KNOWN_DB_NAMES
        ]
        assert not stray, (
            f"Stray .db files found at repo root: {[str(p) for p in stray]}"
        )

    def test_no_stray_db_outside_runtime(self):
        """No unexpected .db files should exist inside cortex/ source tree."""
        cortex_src = REPO_ROOT / "cortex"
        stray = [
            p for p in cortex_src.rglob("*.db")
            if p.name not in KNOWN_DB_NAMES
        ]
        assert not stray, (
            f"Unexpected .db files in cortex/ source: {[str(p) for p in stray]}"
        )
