"""
tests/unit/tools/media/test_duplicate_detector.py

Unit tests for DuplicateDetector — SHA256-based collision prevention.

Tests cover:
- Hash computation and indexing
- Duplicate detection across directory
- Conflict resolution strategies
- Pre-flight validation before rename operations

CORE-008: Tests written BEFORE implementation.
CORE-011: Type hints mandatory.
CORE-012: Google-style docstrings.

AC_START: AC-DUPLICATE-DETECTOR-TEST-2026-02-23
"""

from __future__ import annotations

import hashlib
import pytest
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from cortex.tools.media.duplicate_detector import (
    DuplicateDetector,
    FileHash,
    DuplicateGroup,
    ConflictResolution,
    DuplicateCheckResult,
)


class TestFileHash:
    """Test FileHash dataclass."""

    def test_file_hash_creation(self) -> None:
        """Create FileHash instance."""
        fh = FileHash(
            path=Path("G:\\FLICKS\\test.mp4"),
            sha256="abc123",
            size_bytes=1024000,
        )

        assert fh.path == Path("G:\\FLICKS\\test.mp4")
        assert fh.sha256 == "abc123"
        assert fh.size_bytes == 1024000


class TestDuplicateGroup:
    """Test DuplicateGroup dataclass."""

    def test_duplicate_group_creation(self) -> None:
        """Create DuplicateGroup instance."""
        group = DuplicateGroup(
            sha256="abc123",
            files=[
                Path("G:\\FLICKS\\file1.mp4"),
                Path("G:\\FLICKS\\file2.mp4"),
            ],
            size_bytes=1024000,
        )

        assert group.sha256 == "abc123"
        assert len(group.files) == 2
        assert group.size_bytes == 1024000

    def test_duplicate_group_count(self) -> None:
        """Count duplicates in group."""
        group = DuplicateGroup(
            sha256="abc123",
            files=[
                Path("G:\\FLICKS\\file1.mp4"),
                Path("G:\\FLICKS\\file2.mp4"),
                Path("G:\\FLICKS\\file3.mp4"),
            ],
            size_bytes=1024000,
        )

        assert group.duplicate_count == 3


class TestDuplicateDetector:
    """Test DuplicateDetector functionality."""

    def test_detector_initialization(self, tmp_path: Path) -> None:
        """Initialize DuplicateDetector."""
        detector = DuplicateDetector(root=tmp_path)

        assert detector.root == tmp_path
        assert len(detector.hash_index) == 0

    def test_compute_sha256(self, tmp_path: Path) -> None:
        """Compute SHA256 hash of file."""
        # Create test file
        test_file = tmp_path / "test.mp4"
        test_file.write_bytes(b"test content")

        detector = DuplicateDetector(root=tmp_path)
        file_hash = detector.compute_hash(test_file)

        expected_hash = hashlib.sha256(b"test content").hexdigest()
        assert file_hash.sha256 == expected_hash
        assert file_hash.size_bytes == 12
        assert file_hash.path == test_file

    def test_compute_sha256_large_file(self, tmp_path: Path) -> None:
        """Compute SHA256 with chunked reading for large files."""
        # Create 5MB test file
        test_file = tmp_path / "large.mp4"
        test_file.write_bytes(b"x" * (5 * 1024 * 1024))

        detector = DuplicateDetector(root=tmp_path)
        file_hash = detector.compute_hash(test_file)

        assert file_hash.sha256 is not None
        assert file_hash.size_bytes == 5 * 1024 * 1024

    def test_scan_directory(self, tmp_path: Path) -> None:
        """Scan directory and build hash index."""
        # Create test files
        (tmp_path / "file1.mp4").write_bytes(b"content1")
        (tmp_path / "file2.mp4").write_bytes(b"content2")
        (tmp_path / "file3.mkv").write_bytes(b"content3")

        detector = DuplicateDetector(root=tmp_path)
        detector.scan()

        assert len(detector.hash_index) == 3

    def test_detect_no_duplicates(self, tmp_path: Path) -> None:
        """Detect no duplicates when all files unique."""
        (tmp_path / "file1.mp4").write_bytes(b"content1")
        (tmp_path / "file2.mp4").write_bytes(b"content2")

        detector = DuplicateDetector(root=tmp_path)
        detector.scan()
        duplicates = detector.find_duplicates()

        assert len(duplicates) == 0

    def test_detect_exact_duplicates(self, tmp_path: Path) -> None:
        """Detect exact duplicate files (same content)."""
        # Create identical files
        (tmp_path / "file1.mp4").write_bytes(b"identical content")
        (tmp_path / "file2.mp4").write_bytes(b"identical content")
        (tmp_path / "file3.mp4").write_bytes(b"different")

        detector = DuplicateDetector(root=tmp_path)
        detector.scan()
        duplicates = detector.find_duplicates()

        assert len(duplicates) == 1
        assert duplicates[0].duplicate_count == 2
        assert duplicates[0].files[0].name in ("file1.mp4", "file2.mp4")

    def test_detect_multiple_duplicate_groups(self, tmp_path: Path) -> None:
        """Detect multiple groups of duplicates."""
        # Group 1: identical
        (tmp_path / "file1.mp4").write_bytes(b"group1")
        (tmp_path / "file2.mp4").write_bytes(b"group1")

        # Group 2: identical
        (tmp_path / "file3.mp4").write_bytes(b"group2")
        (tmp_path / "file4.mp4").write_bytes(b"group2")

        # Unique
        (tmp_path / "file5.mp4").write_bytes(b"unique")

        detector = DuplicateDetector(root=tmp_path)
        detector.scan()
        duplicates = detector.find_duplicates()

        assert len(duplicates) == 2
        assert all(g.duplicate_count == 2 for g in duplicates)

    def test_check_proposed_rename_no_collision(self, tmp_path: Path) -> None:
        """Check proposed rename with no collision."""
        (tmp_path / "original.mp4").write_bytes(b"content")

        detector = DuplicateDetector(root=tmp_path)
        detector.scan()

        result = detector.check_rename(
            current_path=tmp_path / "original.mp4",
            proposed_path=tmp_path / "renamed.mp4",
        )

        assert result.is_safe is True
        assert result.collision_detected is False
        assert result.resolution is None

    def test_check_proposed_rename_with_collision(self, tmp_path: Path) -> None:
        """Check proposed rename that would cause collision."""
        (tmp_path / "original.mp4").write_bytes(b"content")
        (tmp_path / "target.mp4").write_bytes(b"existing")

        detector = DuplicateDetector(root=tmp_path)
        detector.scan()

        result = detector.check_rename(
            current_path=tmp_path / "original.mp4",
            proposed_path=tmp_path / "target.mp4",  # Already exists!
        )

        assert result.is_safe is False
        assert result.collision_detected is True
        assert result.existing_file == tmp_path / "target.mp4"

    def test_check_proposed_rename_to_duplicate_content(self, tmp_path: Path) -> None:
        """Check rename where target has same content (safe duplicate)."""
        # Create identical content files
        (tmp_path / "file1.mp4").write_bytes(b"same content")
        (tmp_path / "file2.mp4").write_bytes(b"same content")

        detector = DuplicateDetector(root=tmp_path)
        detector.scan()

        result = detector.check_rename(
            current_path=tmp_path / "file1.mp4",
            proposed_path=tmp_path / "new_name.mp4",
        )

        # Should be safe since no name collision
        assert result.is_safe is True

    def test_suggest_resolution_keep_original(self, tmp_path: Path) -> None:
        """Suggest resolution: keep original filename."""
        (tmp_path / "original.mp4").write_bytes(b"content")
        (tmp_path / "target.mp4").write_bytes(b"existing")

        detector = DuplicateDetector(root=tmp_path)
        detector.scan()

        result = detector.check_rename(
            current_path=tmp_path / "original.mp4",
            proposed_path=tmp_path / "target.mp4",
        )

        assert result.resolution == ConflictResolution.KEEP_ORIGINAL

    def test_suggest_resolution_add_suffix(self, tmp_path: Path) -> None:
        """Suggest resolution: add numeric suffix."""
        (tmp_path / "original.mp4").write_bytes(b"content")
        (tmp_path / "target.mp4").write_bytes(b"existing")

        detector = DuplicateDetector(root=tmp_path)
        detector.scan()

        result = detector.check_rename(
            current_path=tmp_path / "original.mp4",
            proposed_path=tmp_path / "target.mp4",
        )

        # Should suggest target_2.mp4 or similar
        assert result.suggested_alternative is not None
        assert "_2" in result.suggested_alternative.name or "-2" in result.suggested_alternative.name

    def test_batch_check_renames(self, tmp_path: Path) -> None:
        """Check batch of proposed renames."""
        (tmp_path / "file1.mp4").write_bytes(b"content1")
        (tmp_path / "file2.mp4").write_bytes(b"content2")
        (tmp_path / "existing.mp4").write_bytes(b"blocker")

        detector = DuplicateDetector(root=tmp_path)
        detector.scan()

        rename_pairs: Dict[Path, Path] = {
            tmp_path / "file1.mp4": tmp_path / "safe_rename.mp4",
            tmp_path / "file2.mp4": tmp_path / "existing.mp4",  # Collision!
        }

        results = detector.batch_check_renames(rename_pairs)

        assert len(results) == 2
        assert results[tmp_path / "file1.mp4"].is_safe is True
        assert results[tmp_path / "file2.mp4"].is_safe is False

    def test_skip_non_video_files(self, tmp_path: Path) -> None:
        """Skip non-video files during scan."""
        (tmp_path / "video.mp4").write_bytes(b"video")
        (tmp_path / "image.jpg").write_bytes(b"image")
        (tmp_path / "document.txt").write_bytes(b"text")

        detector = DuplicateDetector(
            root=tmp_path,
            extensions=[".mp4", ".mkv", ".avi"],
        )
        detector.scan()

        # Should only index .mp4
        assert len(detector.hash_index) == 1

    def test_recursive_scan(self, tmp_path: Path) -> None:
        """Scan subdirectories recursively."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        (tmp_path / "root.mp4").write_bytes(b"root")
        (subdir / "nested.mp4").write_bytes(b"nested")

        detector = DuplicateDetector(root=tmp_path)
        detector.scan()

        assert len(detector.hash_index) == 2

    def test_generate_unique_filename(self, tmp_path: Path) -> None:
        """Generate unique filename with suffix."""
        (tmp_path / "file.mp4").write_bytes(b"exists")

        detector = DuplicateDetector(root=tmp_path)
        detector.scan()

        unique = detector.generate_unique_filename(tmp_path / "file.mp4")

        assert unique != tmp_path / "file.mp4"
        assert not unique.exists()
        assert unique.suffix == ".mp4"


# AC_COMPLETE: AC-DUPLICATE-DETECTOR-TEST-2026-02-23 ✅
