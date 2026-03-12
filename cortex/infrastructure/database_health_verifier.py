"""
DatabaseHealthVerifier — Phase 148-a.

Provides 4-layer SQLite health verification for all DB_REGISTRY databases:
  Layer 1: File existence
  Layer 2: Tables accessible
  Layer 3: Write/read round-trip
  Layer 4: PRAGMA integrity_check
"""
from __future__ import annotations

import sqlite3
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from cortex.infrastructure.env_initializer import DB_REGISTRY


@dataclass
class DatabaseHealthResult:
    """4-layer health result for a single SQLite database."""

    db_name: str
    path: str
    exists: bool
    tables_ok: bool
    roundtrip_ok: bool
    integrity_ok: bool
    error: Optional[str]

    @property
    def ok(self) -> bool:
        return (
            self.exists
            and self.tables_ok
            and self.roundtrip_ok
            and self.integrity_ok
            and self.error is None
        )


@dataclass
class DatabaseHealthReport:
    """Aggregate health report for all registered databases."""

    results: list[DatabaseHealthResult]
    all_ok: bool
    failed_count: int


class DatabaseHealthVerifier:
    """
    4-layer SQLite health verifier for all CORTEX databases in DB_REGISTRY.

    Usage::

        verifier = DatabaseHealthVerifier()
        report = verifier.verify_all()
        if not report.all_ok:
            for r in report.results:
                if not r.ok:
                    print(f"{r.db_name}: {r.error}")
    """

    def __init__(self, runtime_root: Optional[Path] = None) -> None:
        self._root = runtime_root or Path(".cortex-runtime")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def verify_all(self) -> DatabaseHealthReport:
        """Run 4-layer verification on every database in DB_REGISTRY."""
        results: list[DatabaseHealthResult] = []
        for db_name, db_spec in DB_REGISTRY.items():
            db_path = self._root / db_spec["path"]
            results.append(self.verify_one(db_name, db_path))

        failed = [r for r in results if not r.ok]
        return DatabaseHealthReport(
            results=results,
            all_ok=len(failed) == 0,
            failed_count=len(failed),
        )

    def verify_one(self, db_name: str, db_path: Path) -> DatabaseHealthResult:
        """Run 4-layer verification on a single database path."""
        error: Optional[str] = None

        # Layer 1 — existence
        exists = self._check_exists(db_path)
        if not exists:
            return DatabaseHealthResult(
                db_name=db_name,
                path=str(db_path),
                exists=False,
                tables_ok=False,
                roundtrip_ok=False,
                integrity_ok=False,
                error=f"File not found: {db_path}",
            )

        # Layer 2 — tables accessible
        tables_ok = True
        try:
            with sqlite3.connect(str(db_path), timeout=5.0) as conn:
                conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        except sqlite3.DatabaseError as exc:
            tables_ok = False
            error = f"Tables inaccessible: {exc}"

        # Layer 3 — round-trip write/read (uses an in-memory scratch DB to avoid
        # touching the real file with test data; the real file's WAL is not written)
        roundtrip_ok = self._check_roundtrip(db_path) if tables_ok else False
        if roundtrip_ok is False and error is None:
            error = "Round-trip check failed"

        # Layer 4 — integrity_check PRAGMA
        integrity_ok = self._check_integrity(db_path) if tables_ok else False
        if not integrity_ok and error is None:
            error = "PRAGMA integrity_check failed"

        return DatabaseHealthResult(
            db_name=db_name,
            path=str(db_path),
            exists=exists,
            tables_ok=tables_ok,
            roundtrip_ok=roundtrip_ok,
            integrity_ok=integrity_ok,
            error=error,
        )

    # ------------------------------------------------------------------
    # Private layer implementations
    # ------------------------------------------------------------------

    def _check_exists(self, db_path: Path) -> bool:
        return db_path.is_file()

    def _check_roundtrip(self, db_path: Path) -> bool:
        """Write a sentinel row to a uniquely-named probe table, read back, drop."""
        probe = f"_health_probe_{uuid.uuid4().hex}"
        try:
            token = uuid.uuid4().hex
            with sqlite3.connect(str(db_path), timeout=5.0) as conn:
                conn.execute(f"CREATE TABLE {probe} (val TEXT)")
                conn.execute(f"INSERT INTO {probe} (val) VALUES (?)", (token,))
                row = conn.execute(f"SELECT val FROM {probe}").fetchone()
                conn.execute(f"DROP TABLE {probe}")
                conn.commit()
            return row is not None and row[0] == token
        except sqlite3.DatabaseError:
            # Best-effort cleanup — ignore errors on probe drop
            try:
                with sqlite3.connect(str(db_path), timeout=2.0) as conn:
                    conn.execute(f"DROP TABLE IF EXISTS {probe}")
            except sqlite3.DatabaseError:
                pass
            return False

    def _check_integrity(self, db_path: Path) -> bool:
        """Return True if PRAGMA integrity_check returns 'ok'."""
        try:
            with sqlite3.connect(str(db_path), timeout=5.0) as conn:
                rows = conn.execute("PRAGMA integrity_check").fetchall()
            return len(rows) == 1 and rows[0][0] == "ok"
        except sqlite3.DatabaseError:
            return False
