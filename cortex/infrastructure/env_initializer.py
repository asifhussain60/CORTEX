"""
CORTEX Environment Initializer — Canonical Fast Setup

Initializes all 7 SQLite databases and .cortex-runtime/ directory structure
in a single pass. Idempotent, additive-only, cross-platform.

Authority: CORE-035 (single canonical implementation)
Called by:
  - scripts/setup_env.py  (CLI, user-facing)
  - audit-fix-pipeline Stage -2  (automated, pre-flight)

CORE-002: All output inline — no generated report files.
CORE-008: TDD — tests in tests/unit/infrastructure/test_env_initializer.py
CORE-011: Type hints on all functions.
CORE-012: Docstrings on all public APIs.
"""

from __future__ import annotations

import logging
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# =============================================================================
# CANONICAL RUNTIME DIRECTORY STRUCTURE
# =============================================================================
RUNTIME_DIRS = [
    "traces",
    "rca",
    "state",
    "wiring",
    "intelligence",
    "logs",
    "baselines",
    "certification",
    "lens-dashboard",
]

# =============================================================================
# CANONICAL DATABASE REGISTRY
# Each entry: (relative_path, max_size_mb, retention_days, list_of_(sql, description))
# =============================================================================

# --- orchestrator-traces.db ---
_TRACES_DDL: List[Tuple[str, str]] = [
    (
        """
        CREATE TABLE IF NOT EXISTS trace_metadata (
            id TEXT PRIMARY KEY,
            orchestrator_id TEXT NOT NULL,
            orchestrator_class TEXT NOT NULL,
            table_name TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            last_updated TEXT NOT NULL,
            row_count INTEGER DEFAULT 0,
            last_flush_time TEXT,
            schema_version TEXT
        )
        """,
        "trace_metadata",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS trace_flush_log (
            flush_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            reason TEXT NOT NULL,
            tables_flushed TEXT NOT NULL,
            total_rows_removed INTEGER,
            total_rows_remaining INTEGER,
            duration_ms REAL
        )
        """,
        "trace_flush_log",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_flush_timestamp ON trace_flush_log(timestamp DESC)",
        "idx_flush_timestamp",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS trace_master (
            trace_id        TEXT PRIMARY KEY,
            timestamp       TEXT NOT NULL,
            action          TEXT NOT NULL,
            level           TEXT NOT NULL,
            correlation_id  TEXT,
            request_id      TEXT,
            context         TEXT,
            result          TEXT,
            violation_type  TEXT,
            duration_ms     REAL,
            metadata        TEXT
        )
        """,
        "trace_master",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_trace_master_action ON trace_master(action, timestamp DESC)",
        "idx_trace_master_action",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS audit_sessions (
            session_id      TEXT PRIMARY KEY,
            trigger         TEXT NOT NULL,
            branch          TEXT,
            origin_sha      TEXT,
            started_at      TEXT NOT NULL,
            completed_at    TEXT,
            exit_status     TEXT,
            p0_count_final  INTEGER DEFAULT 0,
            p1_count_final  INTEGER DEFAULT 0,
            p2_count_final  INTEGER DEFAULT 0,
            total_fixed     INTEGER DEFAULT 0,
            stages_run      TEXT,
            test_result     TEXT
        )
        """,
        "audit_sessions",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_audit_sessions_started ON audit_sessions(started_at DESC)",
        "idx_audit_sessions_started",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS audit_stage_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      TEXT NOT NULL,
            stage           INTEGER NOT NULL,
            stage_name      TEXT NOT NULL,
            orchestrator    TEXT,
            started_at      TEXT NOT NULL,
            completed_at    TEXT,
            duration_ms     INTEGER,
            status          TEXT NOT NULL DEFAULT 'RUNNING',
            p0_count        INTEGER DEFAULT 0,
            p1_count        INTEGER DEFAULT 0,
            issues_found    INTEGER DEFAULT 0,
            issues_fixed    INTEGER DEFAULT 0,
            violations_json TEXT,
            ac_marker       TEXT,
            notes           TEXT
        )
        """,
        "audit_stage_log",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_audit_stage_session ON audit_stage_log(session_id, stage)",
        "idx_audit_stage_session",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS audit_violations (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      TEXT NOT NULL,
            stage_num       INTEGER NOT NULL,
            check_num       INTEGER,
            severity        TEXT NOT NULL,
            rule_id         TEXT,
            file_path       TEXT,
            description     TEXT NOT NULL,
            auto_fixed      INTEGER DEFAULT 0,
            fix_description TEXT,
            detected_at     TEXT NOT NULL
        )
        """,
        "audit_violations",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_audit_violations_session ON audit_violations(session_id, severity)",
        "idx_audit_violations_session",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS audit_certifications (
            certification_id   TEXT PRIMARY KEY,
            session_id         TEXT NOT NULL,
            git_sha            TEXT NOT NULL,
            git_branch         TEXT NOT NULL,
            audit_checks_total INTEGER NOT NULL,
            audit_p0_final     INTEGER NOT NULL,
            audit_p1_final     INTEGER NOT NULL,
            test_tier          TEXT NOT NULL,
            test_pass_count    INTEGER NOT NULL,
            test_fail_count    INTEGER NOT NULL,
            golden_test_pass   INTEGER,
            guard_tests_gen    INTEGER DEFAULT 0,
            rca_analyses_run   INTEGER DEFAULT 0,
            prevention_rules   INTEGER DEFAULT 0,
            readiness_score    REAL,
            certified_at       TEXT NOT NULL,
            certified_by       TEXT DEFAULT 'CORTEX-AUDIT-FIX',
            notes              TEXT
        )
        """,
        "audit_certifications",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS workflow_runs (
            run_id          TEXT PRIMARY KEY,
            orchestrator    TEXT NOT NULL,
            mode            TEXT NOT NULL,
            template_id     TEXT NOT NULL,
            label           TEXT,
            caller          TEXT,
            status          TEXT NOT NULL,
            total_cycles    INTEGER DEFAULT 0,
            steps_completed INTEGER DEFAULT 0,
            total_issues_fixed INTEGER DEFAULT 0,
            final_predicate INTEGER DEFAULT 0,
            exit_reason     TEXT,
            duration_ms     REAL DEFAULT 0,
            started_at      TEXT NOT NULL,
            completed_at    TEXT,
            error           TEXT
        )
        """,
        "workflow_runs",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_workflow_runs_session ON workflow_runs(started_at DESC)",
        "idx_workflow_runs_session",
    ),
    (
        """
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
        """,
        "workflow_cycles",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_workflow_cycles_run ON workflow_cycles(run_id, cycle_num)",
        "idx_workflow_cycles_run",
    ),
    # Phase 128 observability tables
    (
        """
        CREATE TABLE IF NOT EXISTS trace_registry_loads (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT NOT NULL,
            registry_id TEXT NOT NULL,
            load_time_ms REAL,
            rule_count  INTEGER DEFAULT 0,
            source_path TEXT,
            metadata    TEXT
        )
        """,
        "trace_registry_loads",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_trace_registry_created ON trace_registry_loads(timestamp DESC)",
        "idx_trace_registry_created",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS trace_response_selection (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT NOT NULL,
            intent          TEXT NOT NULL,
            template_id     TEXT,
            template_source TEXT,
            selection_ms    REAL,
            metadata        TEXT
        )
        """,
        "trace_response_selection",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS trace_governance_checks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT NOT NULL,
            check_id    TEXT NOT NULL,
            severity    TEXT NOT NULL,
            result      TEXT NOT NULL,
            rule_id     TEXT,
            file_path   TEXT,
            message     TEXT,
            metadata    TEXT
        )
        """,
        "trace_governance_checks",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_trace_governance_created ON trace_governance_checks(timestamp DESC)",
        "idx_trace_governance_created",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS trace_output_hashes (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT NOT NULL,
            orchestrator    TEXT NOT NULL,
            operation       TEXT NOT NULL,
            output_hash     TEXT NOT NULL,
            is_duplicate    INTEGER DEFAULT 0,
            metadata        TEXT
        )
        """,
        "trace_output_hashes",
    ),
]

# --- rca/rca_store.db ---
_RCA_DDL: List[Tuple[str, str]] = [
    (
        """
        CREATE TABLE IF NOT EXISTS rca_analyses (
            id                   TEXT PRIMARY KEY,
            failure_id           TEXT NOT NULL,
            methodology          TEXT NOT NULL,
            category             TEXT NOT NULL,
            root_cause           TEXT NOT NULL,
            confidence           REAL NOT NULL,
            analysis_data        TEXT NOT NULL DEFAULT '{}',
            recurrence_signature TEXT,
            created_at           TEXT NOT NULL
        )
        """,
        "rca_analyses",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_rca_category ON rca_analyses(category)",
        "idx_rca_category",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_rca_created ON rca_analyses(created_at DESC)",
        "idx_rca_created",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS prevention_rules (
            id                   TEXT PRIMARY KEY,
            rca_id               TEXT NOT NULL,
            rule_text            TEXT NOT NULL,
            gate_level           TEXT NOT NULL,
            active               INTEGER NOT NULL DEFAULT 1,
            trigger_count        INTEGER NOT NULL DEFAULT 0,
            false_positive_count INTEGER NOT NULL DEFAULT 0,
            created_at           TEXT NOT NULL,
            FOREIGN KEY (rca_id) REFERENCES rca_analyses(id)
        )
        """,
        "prevention_rules",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS recurrence_signatures (
            id          TEXT PRIMARY KEY,
            rca_id      TEXT NOT NULL,
            signature   TEXT NOT NULL UNIQUE,
            created_at  TEXT NOT NULL,
            FOREIGN KEY (rca_id) REFERENCES rca_analyses(id)
        )
        """,
        "recurrence_signatures",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS recurrence_incidents (
            id              TEXT PRIMARY KEY,
            signature_id    TEXT NOT NULL,
            failure_id      TEXT NOT NULL,
            similarity      REAL NOT NULL,
            detected_at     TEXT NOT NULL,
            FOREIGN KEY (signature_id) REFERENCES recurrence_signatures(id)
        )
        """,
        "recurrence_incidents",
    ),
]

# --- audit.db (root level) ---
_AUDIT_DDL: List[Tuple[str, str]] = [
    (
        """
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            orchestrator_id TEXT NOT NULL,
            status TEXT NOT NULL,
            duration_ms INTEGER,
            error_message TEXT,
            metadata TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """,
        "audit_events",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_audit_events_created ON audit_events(timestamp DESC)",
        "idx_audit_events_created",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_audit_events_type ON audit_events(event_type)",
        "idx_audit_events_type",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS orchestrator_traces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orchestrator_id TEXT NOT NULL,
            phase_id TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT,
            status TEXT,
            result_summary TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """,
        "orchestrator_traces",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_trace_orchestrator ON orchestrator_traces(orchestrator_id)",
        "idx_trace_orchestrator",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS governance_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            rule_id TEXT NOT NULL,
            orchestrator_id TEXT NOT NULL,
            result TEXT,
            violation_details TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """,
        "governance_checks",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS phase_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phase_id TEXT NOT NULL UNIQUE,
            status TEXT,
            started_at TEXT,
            completed_at TEXT,
            tests_passing INTEGER,
            tests_total INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """,
        "phase_progress",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT NOT NULL,
            ac_id TEXT NOT NULL,
            operation TEXT NOT NULL,
            source_project TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        )
        """,
        "audit_log",
    ),
]

# --- governance.db (root level) ---
_GOVERNANCE_DDL: List[Tuple[str, str]] = [
    (
        """
        CREATE TABLE IF NOT EXISTS scaffolder_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            operation TEXT NOT NULL,
            orchestrator_name TEXT NOT NULL,
            ac_marker TEXT NOT NULL,
            details TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        "scaffolder_audit_log",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_scaffolder_audit_operation ON scaffolder_audit_log(operation)",
        "idx_scaffolder_audit_operation",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_scaffolder_audit_orchestrator ON scaffolder_audit_log(orchestrator_name)",
        "idx_scaffolder_audit_orchestrator",
    ),
]

# --- state/conversations.db ---
_CONVERSATIONS_DDL: List[Tuple[str, str]] = [
    (
        """
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            orchestrator_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            total_turns INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            is_complete BOOLEAN DEFAULT 0,
            context_state TEXT NOT NULL
        )
        """,
        "conversations",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at DESC)",
        "idx_conversations_updated",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at DESC)",
        "idx_conversations_created",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS turn_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            turn_number INTEGER NOT NULL,
            user_input TEXT NOT NULL,
            orchestrator_output TEXT NOT NULL,
            context_state TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            duration_ms REAL NOT NULL,
            tokens_used INTEGER NOT NULL,
            continuation_reason TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
            UNIQUE (conversation_id, turn_number)
        )
        """,
        "turn_records",
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_turn_records_conversation ON turn_records(conversation_id, turn_number)",
        "idx_turn_records_conversation",
    ),
]

# --- wiring/contract_validation_audit.db ---
_WIRING_DDL: List[Tuple[str, str]] = [
    (
        """
        CREATE TABLE IF NOT EXISTS validation_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            orchestrator TEXT NOT NULL,
            method TEXT,
            validation_type TEXT NOT NULL,
            result TEXT NOT NULL,
            violations TEXT,
            metadata TEXT
        )
        """,
        "validation_audit",
    ),
    (
        """
        CREATE TABLE IF NOT EXISTS contract_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            orchestrator TEXT NOT NULL,
            version TEXT NOT NULL,
            contract_hash TEXT NOT NULL,
            metadata TEXT
        )
        """,
        "contract_versions",
    ),
]

# --- intelligence/intelligence_audit.db ---
_INTELLIGENCE_DDL: List[Tuple[str, str]] = [
    (
        """
        CREATE TABLE IF NOT EXISTS intelligence_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            operation TEXT NOT NULL,
            target TEXT NOT NULL,
            metadata TEXT
        )
        """,
        "intelligence_audit",
    ),
]

# =============================================================================
# DATABASE REGISTRY — single source of truth
# =============================================================================
DB_REGISTRY: Dict[str, dict] = {
    "orchestrator-traces": {
        "path": "traces/orchestrator-traces.db",
        "max_mb": 50,
        "retention_days": 30,
        "ddl": _TRACES_DDL,
        "wal_mode": True,
    },
    "rca-store": {
        "path": "rca/rca_store.db",
        "max_mb": 10,
        "retention_days": 30,
        "ddl": _RCA_DDL,
        "wal_mode": False,
    },
    "audit": {
        "path": "audit.db",
        "max_mb": 20,
        "retention_days": 30,
        "ddl": _AUDIT_DDL,
        "wal_mode": True,
    },
    "governance": {
        "path": "governance.db",
        "max_mb": 5,
        "retention_days": 30,
        "ddl": _GOVERNANCE_DDL,
        "wal_mode": False,
    },
    "conversations": {
        "path": "state/conversations.db",
        "max_mb": 10,
        "retention_days": 90,
        "ddl": _CONVERSATIONS_DDL,
        "wal_mode": False,
    },
    "wiring-audit": {
        "path": "wiring/contract_validation_audit.db",
        "max_mb": 5,
        "retention_days": 30,
        "ddl": _WIRING_DDL,
        "wal_mode": False,
    },
    "intelligence-audit": {
        "path": "intelligence/intelligence_audit.db",
        "max_mb": 10,
        "retention_days": 30,
        "ddl": _INTELLIGENCE_DDL,
        "wal_mode": False,
    },
}


# =============================================================================
# RESULT TYPES
# =============================================================================

@dataclass
class DBResult:
    """Result for a single database initialization."""
    name: str
    path: str
    existed: bool
    tables_created: int
    columns_added: int
    was_corrupt: bool
    was_rebuilt: bool
    duration_ms: float
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass
class EnvSetupResult:
    """Aggregate result from environment initialization."""
    runtime_root: Path
    dirs_created: int
    databases: List[DBResult] = field(default_factory=list)
    total_duration_ms: float = 0.0
    clean_mode: bool = False

    @property
    def ok(self) -> bool:
        return all(db.ok for db in self.databases)

    @property
    def failed_dbs(self) -> List[DBResult]:
        return [db for db in self.databases if not db.ok]

    def summary(self) -> str:
        ok_count = sum(1 for db in self.databases if db.ok)
        return (
            f"✅ {ok_count}/{len(self.databases)} databases initialized "
            f"({self.dirs_created} dirs created, {self.total_duration_ms:.0f}ms)"
        )


# =============================================================================
# CORE INITIALIZER
# =============================================================================

class EnvironmentInitializer:
    """
    Canonical CORTEX environment initializer.

    Idempotent: safe to run multiple times — uses CREATE TABLE IF NOT EXISTS
    and additive ALTER TABLE ADD COLUMN (never drops existing data).

    Fast: pure stdlib sqlite3, no network calls, < 3s on any modern machine.

    Cross-platform: uses pathlib everywhere, no shell commands.
    """

    def __init__(
        self,
        runtime_root: Optional[Path] = None,
        verbose: bool = False,
    ) -> None:
        """Initialize the environment initializer.

        Args:
            runtime_root: Path to .cortex-runtime/ directory.
                          Defaults to .cortex-runtime/ relative to cwd.
            verbose: If True, emit debug-level messages for every step.
        """
        self._root = runtime_root or Path(".cortex-runtime")
        self._verbose = verbose

    def setup(self, clean: bool = False) -> EnvSetupResult:
        """Run full environment setup.

        Args:
            clean: If True, delete and recreate all databases (destructive!).
                   Only use when explicitly requested by user.

        Returns:
            EnvSetupResult with summary of actions taken.
        """
        t_start = time.monotonic()
        result = EnvSetupResult(
            runtime_root=self._root,
            dirs_created=0,
            clean_mode=clean,
        )

        # Step 1: Create directory tree
        result.dirs_created = self._create_dirs()

        # Step 2: Initialize each database
        for db_name, db_spec in DB_REGISTRY.items():
            db_result = self._init_database(
                db_name=db_name,
                db_spec=db_spec,
                clean=clean,
            )
            result.databases.append(db_result)
            if self._verbose or not db_result.ok:
                self._log(db_result)

        result.total_duration_ms = (time.monotonic() - t_start) * 1000
        return result

    def verify(self) -> Tuple[bool, List[str]]:
        """Verify environment integrity without making changes.

        Returns:
            (all_ok, list_of_issues)
        """
        issues: List[str] = []

        # Check dirs
        for subdir in RUNTIME_DIRS:
            p = self._root / subdir
            if not p.exists():
                issues.append(f"Missing directory: {p}")

        # Check databases
        for db_name, db_spec in DB_REGISTRY.items():
            db_path = self._root / db_spec["path"]
            if not db_path.exists():
                issues.append(f"Missing database: {db_path}")
                continue
            corruption = self._check_integrity(db_path)
            if corruption:
                issues.append(f"Corrupt database {db_name}: {corruption}")
                continue
            # Check all expected tables
            missing = self._get_missing_tables(db_path, db_spec["ddl"])
            if missing:
                issues.append(f"Missing tables in {db_name}: {missing}")

        return len(issues) == 0, issues

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _create_dirs(self) -> int:
        """Create .cortex-runtime and all subdirectories. Returns count created."""
        created = 0
        dirs_to_create = [self._root] + [self._root / d for d in RUNTIME_DIRS]
        for d in dirs_to_create:
            if not d.exists():
                d.mkdir(parents=True, exist_ok=True)
                created += 1
                logger.debug(f"Created: {d}")
        return created

    def _init_database(self, db_name: str, db_spec: dict, clean: bool) -> DBResult:
        """Initialize a single database.

        Strategy:
        1. If clean=True, delete existing file.
        2. Check integrity — if corrupt, delete and recreate.
        3. Apply all DDL (CREATE TABLE IF NOT EXISTS — idempotent).
        4. Add missing columns via ALTER TABLE (additive only).
        5. Enable WAL mode if configured.
        """
        t_start = time.monotonic()
        db_path = self._root / db_spec["path"]
        existed = db_path.exists()
        was_corrupt = False
        was_rebuilt = False
        tables_created = 0
        columns_added = 0

        try:
            # --- Clean mode: drop-and-recreate via SQL (Windows-safe) ---
            # Prefer SQL DROP TABLE + VACUUM over file deletion to avoid WinError 32
            # (Windows holds SQLite file locks until connection objects are GC'd).
            if clean and existed:
                was_rebuilt = True
                try:
                    _clean_conn = sqlite3.connect(str(db_path), timeout=10.0)
                    try:
                        existing_tbl = [
                            r[0] for r in _clean_conn.execute(
                                "SELECT name FROM sqlite_master "
                                "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                            ).fetchall()
                        ]
                        for t in existing_tbl:
                            _clean_conn.execute(f"DROP TABLE IF EXISTS [{t}]")
                        _clean_conn.commit()
                        logger.debug(
                            f"[{db_name}] Dropped {len(existing_tbl)} tables (clean mode)"
                        )
                    finally:
                        _clean_conn.close()
                except Exception as clean_err:
                    # Fallback: file deletion (works when no handles are open)
                    try:
                        db_path.unlink(missing_ok=True)
                        for ext in ("-wal", "-shm"):
                            db_path.with_suffix(db_path.suffix + ext).unlink(missing_ok=True)
                        existed = False
                    except OSError:
                        logger.warning(f"[{db_name}] Clean mode: cannot drop or delete: {clean_err}")

            # --- Integrity check on existing files ---
            if db_path.exists() and not clean:
                corruption = self._check_integrity(db_path)
                if corruption:
                    was_corrupt = True
                    was_rebuilt = True
                    try:
                        db_path.unlink(missing_ok=True)
                        for ext in ("-wal", "-shm"):
                            db_path.with_suffix(db_path.suffix + ext).unlink(missing_ok=True)
                        logger.warning(f"[{db_name}] Corrupt DB deleted and rebuilt: {corruption}")
                    except OSError as del_err:
                        logger.warning(f"[{db_name}] Corrupt DB: cannot delete ({del_err}); attempting SQL clear")
                        # Fallback: if the corrupt file can still be opened partially,
                        # try connecting and clearing it
                        try:
                            _corrupt_conn = sqlite3.connect(str(db_path), timeout=5.0)
                            try:
                                tbl_names = [
                                    r[0] for r in _corrupt_conn.execute(
                                        "SELECT name FROM sqlite_master WHERE type='table'"
                                    ).fetchall()
                                ]
                                for t in tbl_names:
                                    _corrupt_conn.execute(f"DROP TABLE IF EXISTS [{t}]")
                                _corrupt_conn.commit()
                            finally:
                                _corrupt_conn.close()
                        except Exception:
                            pass  # Will fail gracefully; DDL below recreates tables

            # --- Ensure parent dir ---
            db_path.parent.mkdir(parents=True, exist_ok=True)

            # --- Apply DDL (explicit close for Windows file-handle release) ---
            conn = sqlite3.connect(str(db_path), timeout=10.0)
            try:
                if db_spec.get("wal_mode"):
                    conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA foreign_keys=ON")

                before_tables = self._get_table_names(conn)

                for sql, label in db_spec["ddl"]:
                    try:
                        conn.execute(sql.strip())
                    except sqlite3.OperationalError as e:
                        if "duplicate column" in str(e).lower():
                            pass  # Column already exists — additive only
                        else:
                            logger.warning(f"[{db_name}] DDL warning ({label}): {e}")

                after_tables = self._get_table_names(conn)
                tables_created = len(after_tables - before_tables)

                # Migrate missing columns on existing tables
                columns_added = self._migrate_columns(conn, db_spec["ddl"])

                conn.commit()
            finally:
                conn.close()  # Explicit close: releases Windows file lock immediately

            duration_ms = (time.monotonic() - t_start) * 1000
            return DBResult(
                name=db_name,
                path=str(db_path),
                existed=existed,
                tables_created=tables_created,
                columns_added=columns_added,
                was_corrupt=was_corrupt,
                was_rebuilt=was_rebuilt,
                duration_ms=duration_ms,
            )

        except Exception as exc:
            duration_ms = (time.monotonic() - t_start) * 1000
            logger.error(f"[{db_name}] Initialization failed: {exc}")
            return DBResult(
                name=db_name,
                path=str(db_path),
                existed=existed,
                tables_created=0,
                columns_added=0,
                was_corrupt=was_corrupt,
                was_rebuilt=was_rebuilt,
                duration_ms=duration_ms,
                error=str(exc),
            )

    @staticmethod
    def _check_integrity(db_path: Path) -> Optional[str]:
        """Run PRAGMA integrity_check. Returns error string or None if ok."""
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=5.0)
            result = conn.execute("PRAGMA integrity_check").fetchone()
            if result and result[0] != "ok":
                return result[0]
            return None
        except Exception as e:
            return str(e)
        finally:
            if conn is not None:
                conn.close()

    @staticmethod
    def _get_table_names(conn: sqlite3.Connection) -> set:
        """Return set of existing table names."""
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        return {r[0] for r in rows}

    @staticmethod
    def _get_missing_tables(db_path: Path, ddl: List[Tuple[str, str]]) -> List[str]:
        """Return table names from DDL that don't exist in db_path."""
        import re
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=5.0)
            existing = {
                r[0]
                for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
        except Exception:
            return []
        finally:
            if conn is not None:
                conn.close()
        missing = []
        for sql, _ in ddl:
            m = re.search(r"CREATE TABLE IF NOT EXISTS\s+(\w+)", sql, re.IGNORECASE)
            if m:
                table = m.group(1)
                if table not in existing:
                    missing.append(table)
        return missing

    @staticmethod
    def _migrate_columns(conn: sqlite3.Connection, ddl: List[Tuple[str, str]]) -> int:
        """
        Add any columns defined in DDL that are missing from existing tables.
        Additive only — never drops columns.
        Returns count of columns added.
        """
        import re
        added = 0
        for sql, _ in ddl:
            # Only process CREATE TABLE statements
            if "CREATE TABLE" not in sql.upper():
                continue
            m = re.search(
                r"CREATE TABLE IF NOT EXISTS\s+(\w+)\s*\((.+)\)",
                sql.strip(),
                re.IGNORECASE | re.DOTALL,
            )
            if not m:
                continue
            table_name = m.group(1)
            columns_block = m.group(2)

            # Get existing columns
            try:
                existing_cols = {
                    row[1].lower()
                    for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()
                }
            except sqlite3.OperationalError:
                continue  # Table doesn't exist yet — will be created by CREATE TABLE

            if not existing_cols:
                continue

            if table_name == "audit_stage_log":
                added += EnvironmentInitializer._migrate_audit_stage_log_alias_columns(
                    conn,
                    existing_cols,
                )

            # Parse column definitions (simple: each line with a "name type" pattern)
            for line in columns_block.splitlines():
                line = line.strip().rstrip(",")
                # Skip constraints
                if any(
                    line.upper().startswith(kw)
                    for kw in ("PRIMARY", "FOREIGN", "UNIQUE", "CHECK", "CONSTRAINT")
                ):
                    continue
                col_match = re.match(r"^(\w+)\s+\w+", line)
                if not col_match:
                    continue
                col_name = col_match.group(1).lower()
                if col_name not in existing_cols:
                    try:
                        # Extract the full column definition
                        col_def_match = re.match(r"^(\w+\s+\S+(?:\s+[^,]+)?)", line)
                        if col_def_match:
                            conn.execute(
                                f"ALTER TABLE {table_name} ADD COLUMN {col_def_match.group(1)}"
                            )
                            added += 1
                            logger.debug(
                                f"Migrated: ALTER TABLE {table_name} ADD COLUMN {col_name}"
                            )
                    except sqlite3.OperationalError as e:
                        if "duplicate column" not in str(e).lower():
                            logger.debug(f"Column migration skipped ({table_name}.{col_name}): {e}")
        return added

    @staticmethod
    def _migrate_audit_stage_log_alias_columns(
        conn: sqlite3.Connection,
        existing_cols: set,
    ) -> int:
        """Backfill canonical audit_stage_log columns from legacy aliases.

        Legacy environments used `stage_num` and `stage_label` in `audit_stage_log`.
        Golden tests and canonical schema require `stage` and `stage_name`.

        Args:
            conn: Active sqlite connection.
            existing_cols: Lowercased column names currently in audit_stage_log.

        Returns:
            Number of columns added.
        """
        added = 0

        if "stage" not in existing_cols and "stage_num" in existing_cols:
            conn.execute("ALTER TABLE audit_stage_log ADD COLUMN stage INTEGER")
            conn.execute(
                "UPDATE audit_stage_log SET stage = stage_num "
                "WHERE stage IS NULL"
            )
            existing_cols.add("stage")
            added += 1

        if "stage_name" not in existing_cols and "stage_label" in existing_cols:
            conn.execute("ALTER TABLE audit_stage_log ADD COLUMN stage_name TEXT")
            conn.execute(
                "UPDATE audit_stage_log SET stage_name = stage_label "
                "WHERE stage_name IS NULL"
            )
            existing_cols.add("stage_name")
            added += 1

        return added

    def _log(self, db_result: DBResult) -> None:
        """Emit a log line for a database result."""
        icon = "✅" if db_result.ok else "❌"
        rebuilt = " [REBUILT]" if db_result.was_rebuilt else ""
        corrupt = " [was CORRUPT]" if db_result.was_corrupt else ""
        logger.info(
            f"{icon} {db_result.name}{rebuilt}{corrupt} — "
            f"{db_result.tables_created} tables/{db_result.columns_added} cols "
            f"({db_result.duration_ms:.0f}ms) → {db_result.path}"
        )


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def initialize_runtime_environment(
    runtime_root: Optional[Path] = None,
    clean: bool = False,
    verbose: bool = False,
) -> EnvSetupResult:
    """Initialize the full .cortex-runtime/ environment.

    This is the single canonical entry point called by:
    - scripts/setup_env.py
    - audit-fix-pipeline Stage -2
    - Bootstrap hooks on first run

    Args:
        runtime_root: Override the runtime root (default: .cortex-runtime/ in cwd).
        clean: Delete and recreate all databases. Use only when explicitly requested.
        verbose: Log every step.

    Returns:
        EnvSetupResult — check .ok and .summary() for status.
    """
    initializer = EnvironmentInitializer(runtime_root=runtime_root, verbose=verbose)
    return initializer.setup(clean=clean)


def verify_runtime_environment(
    runtime_root: Optional[Path] = None,
) -> Tuple[bool, List[str]]:
    """Verify the runtime environment without modifying it.

    Args:
        runtime_root: Override the runtime root.

    Returns:
        (all_ok, list_of_issues)
    """
    initializer = EnvironmentInitializer(runtime_root=runtime_root)
    return initializer.verify()
