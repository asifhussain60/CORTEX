"""One-time migration: add audit_stage_log and workflow_cycles to production trace DB."""
import sqlite3
from pathlib import Path

db = Path(".cortex-runtime/traces/orchestrator-traces.db")
if not db.exists():
    print("DB not found - will be created fresh on next logger init")
    exit(0)

conn = sqlite3.connect(str(db))
try:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_stage_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL,
            stage       INTEGER NOT NULL,
            stage_name  TEXT NOT NULL,
            started_at  TEXT NOT NULL,
            completed_at TEXT,
            status      TEXT NOT NULL DEFAULT 'RUNNING',
            p0_count    INTEGER DEFAULT 0,
            p1_count    INTEGER DEFAULT 0,
            duration_ms REAL,
            notes       TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS workflow_cycles (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id          TEXT NOT NULL,
            template_id     TEXT NOT NULL,
            label           TEXT NOT NULL,
            cycle_num       INTEGER NOT NULL,
            p0_before       INTEGER NOT NULL DEFAULT 0,
            p1_before       INTEGER NOT NULL DEFAULT 0,
            p0_after        INTEGER NOT NULL DEFAULT 0,
            p1_after        INTEGER NOT NULL DEFAULT 0,
            issues_before   INTEGER NOT NULL DEFAULT 0,
            issues_after    INTEGER NOT NULL DEFAULT 0,
            issues_fixed    INTEGER NOT NULL DEFAULT 0,
            predicate_result INTEGER NOT NULL DEFAULT 0,
            fix_log_json    TEXT,
            scan_errors     INTEGER DEFAULT 0,
            fix_errors      INTEGER DEFAULT 0,
            duration_ms     INTEGER NOT NULL DEFAULT 0,
            timestamp       TEXT NOT NULL
        )
    """)
    conn.commit()
    tables = sorted([r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()])
    print("Tables after migration:", tables)
    assert "audit_stage_log" in tables, "audit_stage_log not created!"
    assert "workflow_cycles" in tables, "workflow_cycles not created!"
    print("OK — migration complete")
finally:
    conn.close()
