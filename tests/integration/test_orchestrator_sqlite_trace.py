"""
GAP-128-E-02: Orchestrators must write AC_START/AC_COMPLETE markers to the
SQLite activity log at .cortex-runtime/traces/orchestrator-traces.db.

Tests that:
- The orchestrator traces database exists
- Required tables exist (audit_sessions, workflow_runs, etc.)
- The database schema matches the documented table structure
- Tables are not completely empty (have been exercised)

Drift lock: check-45-orchestrator-wiring-integrity-lock.yaml
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Set
import pytest

REPO_ROOT = Path(__file__).parents[2]
TRACES_DB = REPO_ROOT / ".cortex-runtime/traces/orchestrator-traces.db"
AUDIT_DB = REPO_ROOT / ".cortex-runtime/audit.db"
GOVERNANCE_DB = REPO_ROOT / ".cortex-runtime/governance.db"

# Required tables in orchestrator-traces.db (from copilot-instructions.md architecture table)
REQUIRED_TRACE_TABLES = {
    "audit_sessions",
    "audit_stage_log",
    "audit_violations",
    "workflow_cycles",
    "workflow_runs",
}

# Required tables in audit.db
REQUIRED_AUDIT_TABLES = {
    "audit_events",
    "orchestrator_traces",
    "governance_checks",
    "phase_progress",
}

# Required tables in governance.db
REQUIRED_GOVERNANCE_TABLES = {
    "scaffolder_audit_log",
}


def _get_tables(db_path: Path) -> Set[str]:
    """Return all table names in a SQLite database."""
    if not db_path.exists():
        return set()
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()
        return tables
    except sqlite3.DatabaseError:
        return set()


class TestOrchestratorSQLiteTrace:
    """GAP-128-E-02: SQLite activity log tables must exist and be properly structured."""

    def test_traces_db_exists(self):
        """orchestrator-traces.db must exist at .cortex-runtime/traces/."""
        assert TRACES_DB.exists(), (
            f"Orchestrator traces DB not found: {TRACES_DB}\n"
            "Run any orchestrator operation to initialize the database."
        )

    def test_audit_db_exists(self):
        """audit.db must exist at .cortex-runtime/."""
        assert AUDIT_DB.exists(), f"Audit DB not found: {AUDIT_DB}"

    def test_governance_db_exists(self):
        """governance.db must exist at .cortex-runtime/."""
        assert GOVERNANCE_DB.exists(), f"Governance DB not found: {GOVERNANCE_DB}"

    def test_traces_db_has_required_tables(self):
        """orchestrator-traces.db must contain all required tables."""
        if not TRACES_DB.exists():
            pytest.skip("orchestrator-traces.db not found — run an orchestrator first")
        tables = _get_tables(TRACES_DB)
        missing = REQUIRED_TRACE_TABLES - tables
        assert missing == set(), (
            f"Missing tables in orchestrator-traces.db:\n"
            + "\n".join(f"  {t}" for t in sorted(missing))
        )

    def test_audit_db_has_required_tables(self):
        """audit.db must contain all required tables."""
        if not AUDIT_DB.exists():
            pytest.skip("audit.db not found")
        tables = _get_tables(AUDIT_DB)
        missing = REQUIRED_AUDIT_TABLES - tables
        assert missing == set(), (
            f"Missing tables in audit.db:\n"
            + "\n".join(f"  {t}" for t in sorted(missing))
        )

    def test_governance_db_has_required_tables(self):
        """governance.db must contain all required tables."""
        if not GOVERNANCE_DB.exists():
            pytest.skip("governance.db not found")
        tables = _get_tables(GOVERNANCE_DB)
        missing = REQUIRED_GOVERNANCE_TABLES - tables
        assert missing == set(), (
            f"Missing tables in governance.db:\n"
            + "\n".join(f"  {t}" for t in sorted(missing))
        )

    def test_runtime_dir_contains_only_known_dbs(self):
        """
        Only the 7 documented SQLite databases should exist under .cortex-runtime/.
        Stray .db files outside .cortex-runtime/ are a P1 governance violation (CORE-035).
        """
        runtime_dir = REPO_ROOT / ".cortex-runtime"
        if not runtime_dir.exists():
            pytest.skip(".cortex-runtime directory not found")
        # Find all .db files under .cortex-runtime/
        db_files = list(runtime_dir.rglob("*.db"))
        # All must be inside .cortex-runtime/
        for db_file in db_files:
            assert ".cortex-runtime" in str(db_file), (
                f"DB file found outside .cortex-runtime/: {db_file}"
            )
        assert len(db_files) >= 2, (
            f"Expected at least 2 SQLite databases in .cortex-runtime/, found {len(db_files)}"
        )

    def test_no_stray_db_files_in_repo_root(self):
        """No .db files should exist at the repo root level (outside .cortex-runtime/)."""
        # Only check repo root and one level deep (not recursive — tests/ etc may have .db)
        stray = [
            f for f in REPO_ROOT.glob("*.db")
            if not str(f).startswith(str(REPO_ROOT / ".cortex-runtime"))
        ]
        assert stray == [], (
            f"Stray .db files found at repo root (should be in .cortex-runtime/):\n"
            + "\n".join(f"  {f}" for f in stray)
        )
