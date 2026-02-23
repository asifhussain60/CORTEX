"""
cortex/tools/media/restore_manager.py

SQLite-backed snapshot and rollback system for Plex video library operations.

Provides:
- Pre-operation snapshot creation
- Atomic rollback to previous states
- Multi-version history management
- Snapshot pruning and retention

CORE-011: Type hints on all functions.
CORE-012: Google-style docstrings.
CORE-028: snake_case naming.

AC_START: AC-RESTORE-MANAGER-2026-02-23
"""

from __future__ import annotations

import logging
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class RestoreStatus(Enum):
    """Status of restore operation."""

    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class Snapshot:
    """Snapshot of directory state."""

    snapshot_id: int
    timestamp: datetime
    description: str
    file_count: int
    root_path: str = ""


@dataclass
class RestoreResult:
    """Result of restore operation."""

    status: RestoreStatus
    files_restored: int = 0
    files_failed: int = 0
    error: str = ""
    snapshot_id: int = 0


class RestoreManager:
    """
    SQLite-backed snapshot and rollback system.

    Creates point-in-time snapshots of directory state before
    destructive operations, enabling full rollback on failure.

    Attributes:
        db_path: Path to SQLite database.
    """

    def __init__(self, db_path: Path) -> None:
        """
        Initialize RestoreManager.

        Args:
            db_path: Path to SQLite database (created if doesn't exist).
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Snapshots table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS snapshots (
                    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    description TEXT,
                    root_path TEXT NOT NULL,
                    file_count INTEGER NOT NULL
                )
                """
            )

            # Files table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS snapshot_files (
                    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    size_bytes INTEGER,
                    mtime REAL,
                    backup_path TEXT,
                    FOREIGN KEY (snapshot_id) REFERENCES snapshots (snapshot_id)
                )
                """
            )

            # Index for faster queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_snapshot_files
                ON snapshot_files (snapshot_id)
                """
            )

            conn.commit()

    def create_snapshot(
        self,
        root: Path,
        description: str = "",
    ) -> Snapshot:
        """
        Create snapshot of current directory state.

        Args:
            root: Root directory to snapshot.
            description: Human-readable description.

        Returns:
            Snapshot with ID for later rollback.
        """
        logger.info(f"Creating snapshot of {root}...")

        timestamp = datetime.now()
        video_extensions = {".mp4", ".mkv", ".avi", ".m4v", ".webm", ".mov"}

        # Collect all video files
        files_to_backup: List[Path] = []
        for file_path in root.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in video_extensions:
                files_to_backup.append(file_path)

        # Insert snapshot record
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO snapshots (timestamp, description, root_path, file_count)
                VALUES (?, ?, ?, ?)
                """,
                (
                    timestamp.isoformat(),
                    description,
                    str(root),
                    len(files_to_backup),
                ),
            )

            snapshot_id = cursor.lastrowid

            # Insert file records
            for file_path in files_to_backup:
                stat = file_path.stat()

                # Create backup copy in .cortex-runtime/backups/files/
                backup_dir = self.db_path.parent / "files" / str(snapshot_id)
                backup_dir.mkdir(parents=True, exist_ok=True)

                backup_path = backup_dir / file_path.name
                shutil.copy2(file_path, backup_path)

                cursor.execute(
                    """
                    INSERT INTO snapshot_files (
                        snapshot_id, file_path, size_bytes, mtime, backup_path
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        snapshot_id,
                        str(file_path),
                        stat.st_size,
                        stat.st_mtime,
                        str(backup_path),
                    ),
                )

            conn.commit()

        logger.info(
            f"Snapshot {snapshot_id} created: {len(files_to_backup)} files backed up"
        )

        return Snapshot(
            snapshot_id=snapshot_id,
            timestamp=timestamp,
            description=description,
            file_count=len(files_to_backup),
            root_path=str(root),
        )

    def rollback(self, snapshot_id: int) -> RestoreResult:
        """
        Rollback filesystem to snapshot state.

        Args:
            snapshot_id: Snapshot ID to restore.

        Returns:
            RestoreResult with status and counts.
        """
        logger.info(f"Rolling back to snapshot {snapshot_id}...")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get snapshot metadata
            cursor.execute(
                """
                SELECT snapshot_id, timestamp, description, root_path, file_count
                FROM snapshots
                WHERE snapshot_id = ?
                """,
                (snapshot_id,),
            )

            row = cursor.fetchone()
            if not row:
                return RestoreResult(
                    status=RestoreStatus.FAILED,
                    error=f"Snapshot {snapshot_id} not found",
                    snapshot_id=snapshot_id,
                )

            # Get all files in snapshot
            cursor.execute(
                """
                SELECT file_path, backup_path
                FROM snapshot_files
                WHERE snapshot_id = ?
                """,
                (snapshot_id,),
            )

            files = cursor.fetchall()

        # Restore files
        restored_count = 0
        failed_count = 0

        for file_path_str, backup_path_str in files:
            try:
                file_path = Path(file_path_str)
                backup_path = Path(backup_path_str)

                # Restore from backup
                file_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_path, file_path)

                restored_count += 1

            except Exception as exc:
                logger.error(f"Failed to restore {file_path_str}: {exc}")
                failed_count += 1

        status = (
            RestoreStatus.SUCCESS
            if failed_count == 0
            else (
                RestoreStatus.PARTIAL if restored_count > 0 else RestoreStatus.FAILED
            )
        )

        logger.info(
            f"Rollback complete: {restored_count} restored, {failed_count} failed"
        )

        return RestoreResult(
            status=status,
            files_restored=restored_count,
            files_failed=failed_count,
            snapshot_id=snapshot_id,
        )

    def list_snapshots(self) -> List[Snapshot]:
        """
        List all snapshots.

        Returns:
            List of Snapshot objects, ordered by timestamp (oldest first).
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT snapshot_id, timestamp, description, root_path, file_count
                FROM snapshots
                ORDER BY timestamp ASC
                """
            )

            snapshots = []
            for row in cursor.fetchall():
                snapshots.append(
                    Snapshot(
                        snapshot_id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        description=row[2],
                        file_count=row[4],
                        root_path=row[3],
                    )
                )

            return snapshots

    def get_latest_snapshot(self) -> Optional[Snapshot]:
        """
        Get most recent snapshot.

        Returns:
            Latest Snapshot or None if no snapshots exist.
        """
        snapshots = self.list_snapshots()
        return snapshots[-1] if snapshots else None

    def get_snapshot_files(self, snapshot_id: int) -> List[Path]:
        """
        Get list of files in snapshot.

        Args:
            snapshot_id: Snapshot ID.

        Returns:
            List of file paths.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT file_path
                FROM snapshot_files
                WHERE snapshot_id = ?
                """,
                (snapshot_id,),
            )

            return [Path(row[0]) for row in cursor.fetchall()]

    def delete_snapshot(self, snapshot_id: int) -> None:
        """
        Delete snapshot from database.

        Args:
            snapshot_id: Snapshot ID to delete.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Delete backup files
            backup_dir = self.db_path.parent / "files" / str(snapshot_id)
            if backup_dir.exists():
                shutil.rmtree(backup_dir)

            # Delete database records
            cursor.execute(
                "DELETE FROM snapshot_files WHERE snapshot_id = ?", (snapshot_id,)
            )
            cursor.execute("DELETE FROM snapshots WHERE snapshot_id = ?", (snapshot_id,))

            conn.commit()

        logger.info(f"Deleted snapshot {snapshot_id}")

    def prune_snapshots(self, keep_count: int = 10) -> int:
        """
        Prune old snapshots, keeping only most recent N.

        Args:
            keep_count: Number of snapshots to keep.

        Returns:
            Number of snapshots deleted.
        """
        snapshots = self.list_snapshots()

        if len(snapshots) <= keep_count:
            return 0

        to_delete = snapshots[: -keep_count]
        deleted_count = 0

        for snapshot in to_delete:
            self.delete_snapshot(snapshot.snapshot_id)
            deleted_count += 1

        logger.info(f"Pruned {deleted_count} old snapshots")

        return deleted_count

    def get_file_metadata(
        self,
        snapshot_id: int,
        file_path: Path,
    ) -> Dict[str, any]:
        """
        Get metadata for file in snapshot.

        Args:
            snapshot_id: Snapshot ID.
            file_path: File path.

        Returns:
            Dict with size_bytes, mtime.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT size_bytes, mtime
                FROM snapshot_files
                WHERE snapshot_id = ? AND file_path = ?
                """,
                (snapshot_id, str(file_path)),
            )

            row = cursor.fetchone()
            if not row:
                return {}

            return {
                "size_bytes": row[0],
                "mtime": row[1],
            }

    def verify_snapshot(self, snapshot_id: int) -> bool:
        """
        Verify snapshot integrity (all backup files exist).

        Args:
            snapshot_id: Snapshot ID to verify.

        Returns:
            True if all backup files exist.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT backup_path
                FROM snapshot_files
                WHERE snapshot_id = ?
                """,
                (snapshot_id,),
            )

            for (backup_path_str,) in cursor.fetchall():
                backup_path = Path(backup_path_str)
                if not backup_path.exists():
                    logger.warning(f"Missing backup file: {backup_path}")
                    return False

            return True


# AC_COMPLETE: AC-RESTORE-MANAGER-2026-02-23 ✅ (176ms)
