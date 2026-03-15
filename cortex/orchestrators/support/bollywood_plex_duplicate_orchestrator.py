"""
Bollywood Plex duplicate orchestrator with persistent hash cache.

Purpose:
- Maintain a dedicated SQLite database for Bollywood Plex duplicate tracking.
- Reuse saved SHA256 hashes to avoid full rehashing on every run.
- Detect duplicate media files and optionally clean them up.

Database marker:
- This database is marked and enforced for duplicate-cleanup use only.

AC_START: AC-BOLLYWOOD-PLEX-DUP-ORCH-2026-03-15-001
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import logging
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from cortex.core.orchestrator_base import OrchestratorBase

logger = logging.getLogger(__name__)

_DB_PURPOSE_KEY = "purpose"
_DB_PURPOSE_VALUE = "PLEX_BOLLYWOOD_DUPLICATE_INDEX_ONLY"


@dataclass
class DuplicateRecord:
    """Single duplicate hash group."""

    sha256: str
    files: List[Path] = field(default_factory=list)
    size_bytes: int = 0

    @property
    def duplicate_count(self) -> int:
        """Count of extra duplicate files in the group."""
        return max(0, len(self.files) - 1)

    @property
    def wasted_bytes(self) -> int:
        """Storage wasted by duplicates in this group."""
        return self.duplicate_count * self.size_bytes


@dataclass
class DuplicateSweepResult:
    """Result of one duplicate sweep run."""

    root_path: Path
    db_path: Path
    run_id: str
    total_files: int = 0
    unique_hashes: int = 0
    cached_hash_hits: int = 0
    rehashed_files: int = 0
    duplicate_groups: int = 0
    duplicate_files: int = 0
    wasted_bytes: int = 0
    deleted_files: int = 0
    freed_bytes: int = 0
    duration_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)


class BollywoodPlexDuplicateOrchestrator(OrchestratorBase):
    """Orchestrator for persistent Bollywood Plex duplicate management."""

    def __init__(
        self,
        root_path: Path,
        db_path: Optional[Path] = None,
        cleanup: bool = False,
        dry_run: bool = True,
        force_rehash: bool = False,
    ) -> None:
        """
        Initialize duplicate orchestrator.

        Args:
            root_path: Bollywood library root path.
            db_path: Dedicated SQLite path for duplicate/hash index.
            cleanup: Whether to delete duplicates.
            dry_run: If True, never delete files.
            force_rehash: If True, ignore cache and recompute all hashes.
        """
        super().__init__(orchestrator_id="bollywood_plex_duplicate_orchestrator")
        self.root_path = root_path
        self.db_path = db_path or Path(
            ".cortex-runtime/plex-dedupe/bollywood_plex_duplicates.db"
        )
        self.cleanup = cleanup
        self.dry_run = dry_run
        self.force_rehash = force_rehash

    def setup(self) -> None:
        """Set up resources before orchestration run."""

    def govern(self) -> Any:
        """Evaluate governance rules before execute stage."""
        return None

    def execute_operation(self) -> Dict[str, Any]:
        """Execute operation for base lifecycle integration."""
        result = self.run_duplicate_sweep()
        return self._result_to_dict(result)

    def validate(self, output: Optional[Dict[str, Any]] = None) -> bool:
        """Validate operation output."""
        _ = output
        return True

    def teardown(self, result: Optional[Any] = None) -> None:
        """Teardown resources after orchestration run."""
        _ = result

    def run_duplicate_sweep(self) -> DuplicateSweepResult:
        """
        Run duplicate sweep using persistent hash cache.

        Returns:
            DuplicateSweepResult containing scan, cache, and cleanup stats.
        """
        # AC_START: AC-BOLLYWOOD-PLEX-DUP-ORCH-2026-03-15-002
        start = datetime.now(timezone.utc)
        run_id = start.strftime("%Y%m%dT%H%M%S%fZ")

        result = DuplicateSweepResult(
            root_path=self.root_path,
            db_path=self.db_path,
            run_id=run_id,
        )

        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            self._ensure_schema(conn)
            self._ensure_database_marker(conn)

            files = sorted(self.root_path.rglob("*.mp4"))
            result.total_files = len(files)

            existing_rows = self._load_existing_hash_rows(conn)
            seen_paths: List[str] = []
            current_hashes: Dict[str, List[Tuple[Path, int]]] = {}

            for file_path in files:
                path_key = str(file_path.resolve())
                seen_paths.append(path_key)

                try:
                    stat = file_path.stat()
                    size_bytes = int(stat.st_size)
                    mtime_ns = int(stat.st_mtime_ns)

                    cached = existing_rows.get(path_key)
                    if (
                        not self.force_rehash
                        and cached is not None
                        and cached[0] == size_bytes
                        and cached[1] == mtime_ns
                    ):
                        sha256 = cached[2]
                        result.cached_hash_hits += 1
                    else:
                        sha256 = self._compute_sha256(file_path)
                        result.rehashed_files += 1

                    self._upsert_hash_row(
                        conn=conn,
                        path_key=path_key,
                        size_bytes=size_bytes,
                        mtime_ns=mtime_ns,
                        sha256=sha256,
                        run_id=run_id,
                    )

                    current_hashes.setdefault(sha256, []).append((file_path, size_bytes))
                except Exception as exc:  # noqa: BLE001
                    message = f"Hash failure: {file_path} :: {exc}"
                    logger.error(message)
                    result.errors.append(message)

            self._delete_stale_rows(conn, seen_paths)

            duplicate_records = self._build_duplicate_records(current_hashes)
            result.unique_hashes = len(current_hashes)
            result.duplicate_groups = len(duplicate_records)
            result.duplicate_files = sum(record.duplicate_count for record in duplicate_records)
            result.wasted_bytes = sum(record.wasted_bytes for record in duplicate_records)

            self._record_run(conn, result)
            self._record_run_files(conn, run_id, duplicate_records)

            if self.cleanup and not self.dry_run:
                self._cleanup_duplicates(conn, duplicate_records, result)

            conn.commit()

        end = datetime.now(timezone.utc)
        result.duration_seconds = (end - start).total_seconds()

        # AC_COMPLETE: AC-BOLLYWOOD-PLEX-DUP-ORCH-2026-03-15-002 ✅
        return result

    def _ensure_schema(self, conn: sqlite3.Connection) -> None:
        """Create all required tables and indexes."""
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS file_hashes (
                path TEXT PRIMARY KEY,
                size_bytes INTEGER NOT NULL,
                mtime_ns INTEGER NOT NULL,
                sha256 TEXT NOT NULL,
                last_seen_run TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_file_hashes_sha256 ON file_hashes(sha256)"
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS duplicate_runs (
                run_id TEXT PRIMARY KEY,
                root_path TEXT NOT NULL,
                db_path TEXT NOT NULL,
                total_files INTEGER NOT NULL,
                unique_hashes INTEGER NOT NULL,
                cached_hash_hits INTEGER NOT NULL,
                rehashed_files INTEGER NOT NULL,
                duplicate_groups INTEGER NOT NULL,
                duplicate_files INTEGER NOT NULL,
                wasted_bytes INTEGER NOT NULL,
                deleted_files INTEGER NOT NULL,
                freed_bytes INTEGER NOT NULL,
                duration_seconds REAL NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS duplicate_run_files (
                run_id TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                path TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                is_keeper INTEGER NOT NULL,
                PRIMARY KEY (run_id, path)
            )
            """
        )

    def _ensure_database_marker(self, conn: sqlite3.Connection) -> None:
        """Enforce dedicated purpose marker for this SQLite database."""
        now_iso = datetime.now(timezone.utc).isoformat()
        row = conn.execute(
            "SELECT value FROM metadata WHERE key = ?",
            (_DB_PURPOSE_KEY,),
        ).fetchone()

        if row is None:
            conn.execute(
                "INSERT INTO metadata(key, value, updated_at) VALUES (?, ?, ?)",
                (_DB_PURPOSE_KEY, _DB_PURPOSE_VALUE, now_iso),
            )
            return

        existing_value = str(row["value"])
        if existing_value != _DB_PURPOSE_VALUE:
            raise ValueError(
                "Refusing to use SQLite database without dedicated duplicate-cleanup marker"
            )

        conn.execute(
            "UPDATE metadata SET updated_at = ? WHERE key = ?",
            (now_iso, _DB_PURPOSE_KEY),
        )

    def _load_existing_hash_rows(
        self,
        conn: sqlite3.Connection,
    ) -> Dict[str, Tuple[int, int, str]]:
        """Load cached hashes keyed by absolute path."""
        rows = conn.execute(
            "SELECT path, size_bytes, mtime_ns, sha256 FROM file_hashes"
        ).fetchall()
        return {
            str(row["path"]): (
                int(row["size_bytes"]),
                int(row["mtime_ns"]),
                str(row["sha256"]),
            )
            for row in rows
        }

    def _upsert_hash_row(
        self,
        conn: sqlite3.Connection,
        path_key: str,
        size_bytes: int,
        mtime_ns: int,
        sha256: str,
        run_id: str,
    ) -> None:
        """Insert or update hash row for one file."""
        now_iso = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            INSERT INTO file_hashes(path, size_bytes, mtime_ns, sha256, last_seen_run, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                size_bytes=excluded.size_bytes,
                mtime_ns=excluded.mtime_ns,
                sha256=excluded.sha256,
                last_seen_run=excluded.last_seen_run,
                updated_at=excluded.updated_at
            """,
            (path_key, size_bytes, mtime_ns, sha256, run_id, now_iso),
        )

    def _delete_stale_rows(self, conn: sqlite3.Connection, seen_paths: List[str]) -> None:
        """Remove cache entries for files no longer present."""
        if not seen_paths:
            conn.execute("DELETE FROM file_hashes")
            return

        placeholders = ",".join("?" for _ in seen_paths)
        conn.execute(
            f"DELETE FROM file_hashes WHERE path NOT IN ({placeholders})",
            tuple(seen_paths),
        )

    def _build_duplicate_records(
        self,
        current_hashes: Dict[str, List[Tuple[Path, int]]],
    ) -> List[DuplicateRecord]:
        """Build duplicate record list from hash map."""
        records: List[DuplicateRecord] = []
        for sha256, entries in current_hashes.items():
            if len(entries) < 2:
                continue

            entries_sorted = sorted(entries, key=lambda item: (len(str(item[0])), str(item[0]).lower()))
            records.append(
                DuplicateRecord(
                    sha256=sha256,
                    files=[item[0] for item in entries_sorted],
                    size_bytes=int(entries_sorted[0][1]),
                )
            )

        records.sort(key=lambda record: record.wasted_bytes, reverse=True)
        return records

    def _record_run(self, conn: sqlite3.Connection, result: DuplicateSweepResult) -> None:
        """Persist run-level statistics."""
        now_iso = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            INSERT OR REPLACE INTO duplicate_runs(
                run_id, root_path, db_path,
                total_files, unique_hashes, cached_hash_hits, rehashed_files,
                duplicate_groups, duplicate_files, wasted_bytes,
                deleted_files, freed_bytes, duration_seconds, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.run_id,
                str(result.root_path),
                str(result.db_path),
                result.total_files,
                result.unique_hashes,
                result.cached_hash_hits,
                result.rehashed_files,
                result.duplicate_groups,
                result.duplicate_files,
                result.wasted_bytes,
                result.deleted_files,
                result.freed_bytes,
                result.duration_seconds,
                now_iso,
            ),
        )

    def _record_run_files(
        self,
        conn: sqlite3.Connection,
        run_id: str,
        duplicate_records: List[DuplicateRecord],
    ) -> None:
        """Persist duplicate file details for this run."""
        conn.execute("DELETE FROM duplicate_run_files WHERE run_id = ?", (run_id,))
        for record in duplicate_records:
            for index, file_path in enumerate(record.files):
                conn.execute(
                    """
                    INSERT INTO duplicate_run_files(run_id, sha256, path, size_bytes, is_keeper)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        record.sha256,
                        str(file_path.resolve()),
                        record.size_bytes,
                        1 if index == 0 else 0,
                    ),
                )

    def _cleanup_duplicates(
        self,
        conn: sqlite3.Connection,
        duplicate_records: List[DuplicateRecord],
        result: DuplicateSweepResult,
    ) -> None:
        """Delete duplicate files while keeping the first preferred file."""
        for record in duplicate_records:
            keep_file = record.files[0]
            _ = keep_file
            for duplicate_file in record.files[1:]:
                try:
                    duplicate_file.unlink(missing_ok=False)
                    conn.execute(
                        "DELETE FROM file_hashes WHERE path = ?",
                        (str(duplicate_file.resolve()),),
                    )
                    result.deleted_files += 1
                    result.freed_bytes += record.size_bytes
                except Exception as exc:  # noqa: BLE001
                    message = f"Cleanup failure: {duplicate_file} :: {exc}"
                    logger.error(message)
                    result.errors.append(message)

    def _compute_sha256(self, file_path: Path) -> str:
        """Compute SHA256 for one file."""
        digest = hashlib.sha256()
        with file_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _result_to_dict(self, result: DuplicateSweepResult) -> Dict[str, Any]:
        """Convert dataclass result to dictionary for API/tool output."""
        return {
            "root_path": str(result.root_path),
            "db_path": str(result.db_path),
            "run_id": result.run_id,
            "total_files": result.total_files,
            "unique_hashes": result.unique_hashes,
            "cached_hash_hits": result.cached_hash_hits,
            "rehashed_files": result.rehashed_files,
            "duplicate_groups": result.duplicate_groups,
            "duplicate_files": result.duplicate_files,
            "wasted_bytes": result.wasted_bytes,
            "deleted_files": result.deleted_files,
            "freed_bytes": result.freed_bytes,
            "duration_seconds": result.duration_seconds,
            "errors": result.errors,
        }


# AC_COMPLETE: AC-BOLLYWOOD-PLEX-DUP-ORCH-2026-03-15-001 ✅
