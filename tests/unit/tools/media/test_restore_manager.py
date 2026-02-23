"""
tests/unit/tools/media/test_restore_manager.py

Unit tests for RestoreManager — SQLite-backed snapshot and rollback system.

Tests cover:
- Snapshot creation before rename batches
- Rollback to previous state on failure
- Multi-version snapshot history
- Atomic transaction support

CORE-008: Tests written BEFORE implementation.
CORE-011: Type hints mandatory.
CORE-012: Google-style docstrings.

AC_START: AC-RESTORE-MANAGER-TEST-2026-02-23
"""

from __future__ import annotations

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from cortex.tools.media.restore_manager import (
    RestoreManager,
    Snapshot,
    RestoreResult,
    RestoreStatus,
)


class TestSnapshot:
    """Test Snapshot dataclass."""

    def test_snapshot_creation(self) -> None:
        """Create Snapshot instance."""
        snapshot = Snapshot(
            snapshot_id=1,
            timestamp=datetime(2026, 2, 23, 14, 30),
            description="Pre-rename snapshot",
            file_count=50,
        )

        assert snapshot.snapshot_id == 1
        assert snapshot.file_count == 50
        assert snapshot.description == "Pre-rename snapshot"


class TestRestoreManager:
    """Test RestoreManager functionality."""

    def test_manager_initialization(self, tmp_path: Path) -> None:
        """Initialize RestoreManager with SQLite database."""
        db_path = tmp_path / "backups" / "plex-snapshots.db"

        manager = RestoreManager(db_path=db_path)

        assert manager.db_path == db_path
        assert db_path.exists()

    def test_create_snapshot(self, tmp_path: Path) -> None:
        """Create snapshot of current directory state."""
        # Create test files
        video_dir = tmp_path / "videos"
        video_dir.mkdir()
        (video_dir / "file1.mp4").write_text("content1")
        (video_dir / "file2.mp4").write_text("content2")

        db_path = tmp_path / "backups" / "plex-snapshots.db"
        manager = RestoreManager(db_path=db_path)

        snapshot = manager.create_snapshot(
            root=video_dir,
            description="Test snapshot",
        )

        assert snapshot.snapshot_id > 0
        assert snapshot.file_count == 2
        assert snapshot.description == "Test snapshot"

    def test_snapshot_stores_file_paths(self, tmp_path: Path) -> None:
        """Snapshot stores all file paths."""
        video_dir = tmp_path / "videos"
        video_dir.mkdir()
        (video_dir / "file1.mp4").write_text("content1")
        (video_dir / "file2.mp4").write_text("content2")

        db_path = tmp_path / "backups" / "plex-snapshots.db"
        manager = RestoreManager(db_path=db_path)

        snapshot = manager.create_snapshot(root=video_dir)

        # Query database to verify
        stored_files = manager.get_snapshot_files(snapshot.snapshot_id)

        assert len(stored_files) == 2
        assert any("file1.mp4" in str(p) for p in stored_files)
        assert any("file2.mp4" in str(p) for p in stored_files)

    def test_list_snapshots(self, tmp_path: Path) -> None:
        """List all snapshots in database."""
        video_dir = tmp_path / "videos"
        video_dir.mkdir()
        (video_dir / "file.mp4").write_text("content")

        db_path = tmp_path / "backups" / "plex-snapshots.db"
        manager = RestoreManager(db_path=db_path)

        # Create multiple snapshots
        manager.create_snapshot(root=video_dir, description="Snapshot 1")
        manager.create_snapshot(root=video_dir, description="Snapshot 2")

        snapshots = manager.list_snapshots()

        assert len(snapshots) == 2
        assert snapshots[0].description == "Snapshot 1"
        assert snapshots[1].description == "Snapshot 2"

    def test_rollback_to_snapshot(self, tmp_path: Path) -> None:
        """Rollback filesystem to previous snapshot."""
        video_dir = tmp_path / "videos"
        video_dir.mkdir()

        # Initial state
        file1 = video_dir / "file1.mp4"
        file2 = video_dir / "file2.mp4"
        file1.write_text("original1")
        file2.write_text("original2")

        db_path = tmp_path / "backups" / "plex-snapshots.db"
        manager = RestoreManager(db_path=db_path)

        # Create snapshot
        snapshot = manager.create_snapshot(root=video_dir)

        # Modify files (simulate rename operation)
        file1.rename(video_dir / "renamed1.mp4")
        file2.unlink()
        (video_dir / "new_file.mp4").write_text("new")

        # Verify modified state
        assert not file1.exists()
        assert not file2.exists()
        assert (video_dir / "renamed1.mp4").exists()

        # Rollback
        result = manager.rollback(snapshot_id=snapshot.snapshot_id)

        assert result.status == RestoreStatus.SUCCESS
        assert result.files_restored == 2

        # Verify restored state
        assert file1.exists()
        assert file2.exists()
        assert file1.read_text() == "original1"
        assert file2.read_text() == "original2"

    def test_rollback_nonexistent_snapshot(self, tmp_path: Path) -> None:
        """Attempt rollback to nonexistent snapshot."""
        db_path = tmp_path / "backups" / "plex-snapshots.db"
        manager = RestoreManager(db_path=db_path)

        result = manager.rollback(snapshot_id=999)

        assert result.status == RestoreStatus.FAILED
        assert "not found" in result.error.lower()

    def test_get_latest_snapshot(self, tmp_path: Path) -> None:
        """Get most recent snapshot."""
        video_dir = tmp_path / "videos"
        video_dir.mkdir()
        (video_dir / "file.mp4").write_text("content")

        db_path = tmp_path / "backups" / "plex-snapshots.db"
        manager = RestoreManager(db_path=db_path)

        manager.create_snapshot(root=video_dir, description="Snapshot 1")
        snapshot2 = manager.create_snapshot(root=video_dir, description="Snapshot 2")

        latest = manager.get_latest_snapshot()

        assert latest is not None
        assert latest.snapshot_id == snapshot2.snapshot_id
        assert latest.description == "Snapshot 2"

    def test_delete_snapshot(self, tmp_path: Path) -> None:
        """Delete snapshot from database."""
        video_dir = tmp_path / "videos"
        video_dir.mkdir()
        (video_dir / "file.mp4").write_text("content")

        db_path = tmp_path / "backups" / "plex-snapshots.db"
        manager = RestoreManager(db_path=db_path)

        snapshot = manager.create_snapshot(root=video_dir)

        # Delete snapshot
        manager.delete_snapshot(snapshot.snapshot_id)

        # Verify deleted
        snapshots = manager.list_snapshots()
        assert len(snapshots) == 0

    def test_prune_old_snapshots(self, tmp_path: Path) -> None:
        """Prune snapshots older than retention period."""
        video_dir = tmp_path / "videos"
        video_dir.mkdir()
        (video_dir / "file.mp4").write_text("content")

        db_path = tmp_path / "backups" / "plex-snapshots.db"
        manager = RestoreManager(db_path=db_path)

        # Create snapshots
        manager.create_snapshot(root=video_dir, description="Old 1")
        manager.create_snapshot(root=video_dir, description="Old 2")
        manager.create_snapshot(root=video_dir, description="Recent")

        # Prune keeping only 1
        deleted_count = manager.prune_snapshots(keep_count=1)

        assert deleted_count == 2

        snapshots = manager.list_snapshots()
        assert len(snapshots) == 1
        assert snapshots[0].description == "Recent"

    def test_snapshot_with_subdirectories(self, tmp_path: Path) -> None:
        """Snapshot includes files in subdirectories."""
        video_dir = tmp_path / "videos"
        subdir = video_dir / "subdir"
        subdir.mkdir(parents=True)

        (video_dir / "root.mp4").write_text("root")
        (subdir / "nested.mp4").write_text("nested")

        db_path = tmp_path / "backups" / "plex-snapshots.db"
        manager = RestoreManager(db_path=db_path)

        snapshot = manager.create_snapshot(root=video_dir)

        assert snapshot.file_count == 2

        stored_files = manager.get_snapshot_files(snapshot.snapshot_id)
        assert len(stored_files) == 2

    def test_atomic_rollback(self, tmp_path: Path) -> None:
        """Rollback is atomic (all or nothing)."""
        video_dir = tmp_path / "videos"
        video_dir.mkdir()

        (video_dir / "file1.mp4").write_text("content1")
        (video_dir / "file2.mp4").write_text("content2")

        db_path = tmp_path / "backups" / "plex-snapshots.db"
        manager = RestoreManager(db_path=db_path)

        snapshot = manager.create_snapshot(root=video_dir)

        # Delete one file
        (video_dir / "file1.mp4").unlink()

        # Rollback should restore both files
        result = manager.rollback(snapshot_id=snapshot.snapshot_id)

        assert result.status == RestoreStatus.SUCCESS
        assert (video_dir / "file1.mp4").exists()
        assert (video_dir / "file2.mp4").exists()

    def test_snapshot_metadata(self, tmp_path: Path) -> None:
        """Snapshot stores file metadata (size, mtime)."""
        video_dir = tmp_path / "videos"
        video_dir.mkdir()

        test_file = video_dir / "file.mp4"
        test_file.write_text("content")

        db_path = tmp_path / "backups" / "plex-snapshots.db"
        manager = RestoreManager(db_path=db_path)

        snapshot = manager.create_snapshot(root=video_dir)

        # Query metadata from database
        metadata = manager.get_file_metadata(
            snapshot_id=snapshot.snapshot_id,
            file_path=test_file,
        )

        assert metadata["size_bytes"] == len("content")
        assert "mtime" in metadata

    def test_verify_snapshot_integrity(self, tmp_path: Path) -> None:
        """Verify snapshot can be restored."""
        video_dir = tmp_path / "videos"
        video_dir.mkdir()
        (video_dir / "file.mp4").write_text("content")

        db_path = tmp_path / "backups" / "plex-snapshots.db"
        manager = RestoreManager(db_path=db_path)

        snapshot = manager.create_snapshot(root=video_dir)

        # Verify integrity
        is_valid = manager.verify_snapshot(snapshot.snapshot_id)

        assert is_valid is True


# AC_COMPLETE: AC-RESTORE-MANAGER-TEST-2026-02-23 ✅
