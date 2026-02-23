"""
SweepCatalogueOrchestrator — Durable sweep catalogue for CORE-064 enforcement.

Implements the Sweep Completeness Contract: every FIX / REFACTOR / AUDIT session
must open a SweepCatalogue, resolve every catalogued item, and only then be
allowed to close the session (commit / "done" signal).

Catalogue data is persisted to:
    .cortex-runtime/sweeps/{sweep_id}.db  (SQLite WAL — CORE-058 pattern)

so that it survives session boundaries and cannot be silently abandoned.

CORTEX canonical support orchestrator · CORE-035 · priority 155
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class ExhaustedResult:
    """Result returned by assert_exhausted()."""

    ok: bool
    remaining: List[Dict[str, Any]] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        if self.ok:
            return "ExhaustedResult(ok=True)"
        return f"ExhaustedResult(ok=False, remaining={len(self.remaining)} items)"


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class SweepIncompleteError(RuntimeError):
    """Raised by MasterOrchestrator._finalize_operation() when open items remain.

    Contains the numbered list of remaining items so the caller can surface them.
    """

    def __init__(self, sweep_id: str, remaining: List[Dict[str, Any]]) -> None:
        """Initialise the sweep-incomplete error with the sweep ID and unresolved items list."""
        self.sweep_id = sweep_id
        self.remaining = remaining

        def _item_text(r: Any) -> str:
            if isinstance(r, dict):
                return f"[{r.get('file', '?')}] {r.get('description', '?')}"
            return str(r)

        items_text = "\n".join(
            f"  {i + 1}. {_item_text(r)}"
            for i, r in enumerate(remaining)
        )
        super().__init__(
            f"CORE-064: Sweep {sweep_id!r} has {len(remaining)} unresolved item(s).\n"
            f"Resolve all items before closing the session:\n{items_text}"
        )


# ---------------------------------------------------------------------------
# SweepCatalogueOrchestrator
# ---------------------------------------------------------------------------

# Scope-drift threshold: if >20 % of scope files changed hashes, invalidate.
_HASH_DRIFT_THRESHOLD = 0.20

_SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS issues (
    issue_id    TEXT PRIMARY KEY,
    sweep_id    TEXT NOT NULL,
    file        TEXT NOT NULL,
    description TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'OPEN',
    created_at  REAL NOT NULL,
    resolved_at REAL
);

CREATE TABLE IF NOT EXISTS manifests (
    sweep_id    TEXT PRIMARY KEY,
    intent      TEXT NOT NULL,
    scope_json  TEXT NOT NULL,
    hash_json   TEXT NOT NULL DEFAULT '{}',
    created_at  REAL NOT NULL,
    closed_at   REAL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    sweep_id    TEXT NOT NULL,
    event_type  TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at  REAL NOT NULL
);
"""


class SweepCatalogueOrchestrator(OrchestratorProtocolMixin):
    """Durable sweep catalogue — CORE-064 enforcement component.

    Methods
    -------
    open_catalogue(intent, scope_files)
        Open a new catalogue or resume an existing one for the same scope.
    get_manifest(sweep_id)
        Return metadata + open_count for a catalogue.
    add_issue(sweep_id, file, description)
        Register a new issue in the catalogue; returns issue_id.
    mark_resolved(sweep_id, issue_id)
        Mark a single issue RESOLVED; decrements open_count.
    assert_exhausted(sweep_id)
        Return ExhaustedResult(ok=True) if remaining==0, Err otherwise.
    resume_open_catalogue(intent, scope_files)
        Same as open_catalogue — explicit alias for clarity.
    approve_wont_fix(sweep_id, issue_id, justification)
        Mark an issue WONT_FIX with mandatory justification + audit entry.
    get_audit_log(sweep_id)
        Return list of audit entries for a sweep.
    health_check()
        Return {healthy: True, ...} if orchestrator is operational.
    """

    # Support tier priority (CORE-035 + wiring spec)
    PRIORITY: int = 155

    _orch_name = "SweepCatalogueOrchestrator"
    _orch_version = "1.0.0"

    def __init__(self) -> None:
        """Initialise instance; no arguments required."""
        self._runtime_dir: Optional[Path] = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_runtime_dir(self) -> Path:
        """Resolve the .cortex-runtime/sweeps/ directory, creating it if needed."""
        if self._runtime_dir is not None:
            return self._runtime_dir
        base = os.environ.get("CORTEX_RUNTIME_DIR")
        if base:
            root = Path(base)
        else:
            root = Path(".cortex-runtime")
        sweeps_dir = root / "sweeps"
        sweeps_dir.mkdir(parents=True, exist_ok=True)
        self._runtime_dir = sweeps_dir
        return sweeps_dir

    def _db_path(self, sweep_id: str) -> Path:
        return self._get_runtime_dir() / f"{sweep_id}.db"

    def _connect(self, sweep_id: str) -> sqlite3.Connection:
        """Open a WAL-mode SQLite connection to the catalogue DB."""
        conn = sqlite3.connect(str(self._db_path(sweep_id)))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(_SCHEMA_DDL)
        conn.commit()
        return conn

    @staticmethod
    def _scope_key(intent: str, scope_files: List[str]) -> str:
        """Deterministic key for intent + sorted scope_files."""
        canonical = json.dumps(
            {"intent": intent, "scope": sorted(scope_files)}, sort_keys=True
        )
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]

    @staticmethod
    def _file_hashes(scope_files: List[str]) -> Dict[str, str]:
        """Compute SHA-256 fingerprints for existing scope files."""
        hashes: Dict[str, str] = {}
        for path in scope_files:
            p = Path(path)
            if p.exists() and p.is_file():
                data = p.read_bytes()
                hashes[path] = hashlib.sha256(data).hexdigest()[:16]
            else:
                hashes[path] = "missing"
        return hashes

    def _detect_hash_drift(
        self, stored_hash_json: str, scope_files: List[str]
    ) -> float:
        """Return drift fraction (0.0–1.0). >0.20 triggers invalidation."""
        stored: Dict[str, str] = json.loads(stored_hash_json or "{}")
        current = self._file_hashes(scope_files)
        if not stored:
            return 0.0
        differing = sum(1 for f in scope_files if stored.get(f) != current.get(f))
        return differing / len(scope_files) if scope_files else 0.0

    def _find_open_catalogue(self, intent: str, scope_files: List[str]) -> Optional[str]:
        """Search all existing .db files for an open catalogue matching intent+scope."""
        sweeps_dir = self._get_runtime_dir()
        scope_key = self._scope_key(intent, scope_files)
        for db_file in sweeps_dir.glob("*.db"):
            sweep_id = db_file.stem
            try:
                conn = sqlite3.connect(str(db_file))
                conn.row_factory = sqlite3.Row
                row = conn.execute(
                    "SELECT scope_json, hash_json FROM manifests WHERE sweep_id=? AND closed_at IS NULL",
                    (sweep_id,),
                ).fetchone()
                conn.close()
                if row is None:
                    continue
                stored_scope = json.loads(row["scope_json"])
                if sorted(stored_scope) == sorted(scope_files):
                    drift = self._detect_hash_drift(row["hash_json"], scope_files)
                    if drift <= _HASH_DRIFT_THRESHOLD:
                        return sweep_id
            except Exception:  # noqa: BLE001
                continue
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def open_catalogue(self, intent: str, scope_files: List[str]) -> str:
        """Open a new catalogue or resume an existing one for the same scope.

        Parameters
        ----------
        intent:
            One of "FIX", "REFACTOR", "AUDIT".
        scope_files:
            List of file paths that are in scope for this sweep.

        Returns
        -------
        str
            The sweep_id (used for all subsequent operations).
        """
        existing = self._find_open_catalogue(intent, scope_files)
        if existing:
            logger.info("Resuming existing sweep catalogue %s (%d files)", existing, len(scope_files))
            return existing

        import time as _time_mod
        _ac_id = f"AC-SWEEP-{int(_time_mod.time() * 1000)}"
        # AC_START: {_ac_id}
        sweep_id = f"sweep-{uuid.uuid4().hex[:12]}"
        now = time.time()
        hash_json = json.dumps(self._file_hashes(scope_files))
        scope_json = json.dumps(sorted(scope_files))

        conn = self._connect(sweep_id)
        conn.execute(
            "INSERT INTO manifests (sweep_id, intent, scope_json, hash_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (sweep_id, intent, scope_json, hash_json, now),
        )
        conn.commit()
        conn.close()

        logger.info("Opened new sweep catalogue %s (%s · %d files)", sweep_id, intent, len(scope_files))
        # AC_COMPLETE: {_ac_id} ✅
        return sweep_id

    def resume_open_catalogue(self, intent: str, scope_files: List[str]) -> str:
        """Explicit alias for open_catalogue — resumes if possible, opens fresh otherwise."""
        return self.open_catalogue(intent=intent, scope_files=scope_files)

    def get_manifest(self, sweep_id: str) -> Dict[str, Any]:
        """Return manifest metadata + open_count for *sweep_id*.

        Returns
        -------
        dict with keys: sweep_id, intent, scope_files, open_count, created_at, closed_at
        """
        conn = self._connect(sweep_id)
        row = conn.execute(
            "SELECT * FROM manifests WHERE sweep_id=?", (sweep_id,)
        ).fetchone()
        if row is None:
            conn.close()
            raise KeyError(f"No manifest found for sweep_id={sweep_id!r}")
        open_count = conn.execute(
            "SELECT COUNT(*) FROM issues WHERE sweep_id=? AND status='OPEN'", (sweep_id,)
        ).fetchone()[0]
        conn.close()
        return {
            "sweep_id": sweep_id,
            "intent": row["intent"],
            "scope_files": json.loads(row["scope_json"]),
            "open_count": open_count,
            "created_at": row["created_at"],
            "closed_at": row["closed_at"],
        }

    def add_issue(self, sweep_id: str, file: str, description: str) -> str:
        """Register a new OPEN issue in the catalogue.

        Returns
        -------
        str
            The issue_id (UUID hex).
        """
        issue_id = uuid.uuid4().hex
        conn = self._connect(sweep_id)
        conn.execute(
            "INSERT INTO issues (issue_id, sweep_id, file, description, status, created_at) "
            "VALUES (?, ?, ?, ?, 'OPEN', ?)",
            (issue_id, sweep_id, file, description, time.time()),
        )
        conn.commit()
        conn.close()
        return issue_id

    def mark_resolved(self, sweep_id: str, issue_id: str) -> None:
        """Mark *issue_id* as RESOLVED; decrements open_count.

        Raises
        ------
        KeyError
            If issue_id is not found or not OPEN.
        """
        conn = self._connect(sweep_id)
        cursor = conn.execute(
            "UPDATE issues SET status='RESOLVED', resolved_at=? "
            "WHERE issue_id=? AND sweep_id=? AND status='OPEN'",
            (time.time(), issue_id, sweep_id),
        )
        if cursor.rowcount == 0:
            conn.close()
            raise KeyError(f"Issue {issue_id!r} not found or already closed in sweep {sweep_id!r}")
        self._write_audit(conn, sweep_id, "RESOLVED", {"issue_id": issue_id})
        conn.commit()
        conn.close()

    def assert_exhausted(self, sweep_id: str) -> ExhaustedResult:
        """Check whether all catalogued items are resolved.

        Returns
        -------
        ExhaustedResult(ok=True)  — catalogue is fully exhausted
        ExhaustedResult(ok=False, remaining=[...])  — items still open
        """
        conn = self._connect(sweep_id)
        rows = conn.execute(
            "SELECT issue_id, file, description FROM issues "
            "WHERE sweep_id=? AND status='OPEN'",
            (sweep_id,),
        ).fetchall()
        conn.close()
        if not rows:
            return ExhaustedResult(ok=True)
        remaining = [{"issue_id": r["issue_id"], "file": r["file"], "description": r["description"]} for r in rows]
        return ExhaustedResult(ok=False, remaining=remaining)

    def approve_wont_fix(
        self, sweep_id: str, issue_id: str, justification: str
    ) -> bool:
        """Mark an issue WONT_FIX with mandatory justification and audit entry.

        Parameters
        ----------
        sweep_id, issue_id:
            Target sweep and issue.
        justification:
            Non-empty rationale. Empty string raises ValueError.

        Returns
        -------
        bool
            True on success.

        Raises
        ------
        ValueError
            If justification is empty or whitespace-only.
        """
        if not justification or not justification.strip():
            raise ValueError(
                "CORE-064: approve_wont_fix() requires a non-empty justification. "
                "Bulk WONT-FIX without per-item justification is forbidden."
            )
        conn = self._connect(sweep_id)
        cursor = conn.execute(
            "UPDATE issues SET status='WONT_FIX', resolved_at=? "
            "WHERE issue_id=? AND sweep_id=? AND status='OPEN'",
            (time.time(), issue_id, sweep_id),
        )
        if cursor.rowcount == 0:
            conn.close()
            raise KeyError(f"Issue {issue_id!r} not found or already closed in sweep {sweep_id!r}")
        self._write_audit(
            conn,
            sweep_id,
            "WONT_FIX",
            {"issue_id": issue_id, "justification": justification},
        )
        conn.commit()
        conn.close()
        return True

    def get_audit_log(self, sweep_id: str) -> List[Dict[str, Any]]:
        """Return list of audit log entries for *sweep_id*, oldest first."""
        conn = self._connect(sweep_id)
        rows = conn.execute(
            "SELECT event_type, payload_json, created_at FROM audit_log "
            "WHERE sweep_id=? ORDER BY id ASC",
            (sweep_id,),
        ).fetchall()
        conn.close()
        return [
            {
                "event_type": r["event_type"],
                "payload": json.loads(r["payload_json"]),
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    def health_check(self) -> Dict[str, Any]:
        """Verify orchestrator is operational.

        Returns
        -------
        dict with keys: healthy (bool), storage_dir (str), note (str)
        """
        try:
            sweeps_dir = self._get_runtime_dir()
            # Quick smoke test: create + drop a temp DB
            test_id = f"_healthcheck_{uuid.uuid4().hex[:8]}"
            test_db = sweeps_dir / f"{test_id}.db"
            conn = sqlite3.connect(str(test_db))
            conn.execute("PRAGMA journal_mode=WAL")
            conn.close()
            test_db.unlink(missing_ok=True)
            return {
                "status": "healthy",
                "healthy": True,
                "storage_dir": str(sweeps_dir),
                "note": "SweepCatalogueOrchestrator operational (CORE-064)",
                "orchestrator": self.get_name(),
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "unhealthy",
                "healthy": False,
                "error": str(exc),
                "note": "SweepCatalogueOrchestrator health check failed",
            }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _write_audit(
        conn: sqlite3.Connection,
        sweep_id: str,
        event_type: str,
        payload: Dict[str, Any],
    ) -> None:
        conn.execute(
            "INSERT INTO audit_log (sweep_id, event_type, payload_json, created_at) VALUES (?, ?, ?, ?)",
            (sweep_id, event_type, json.dumps(payload), time.time()),
        )
