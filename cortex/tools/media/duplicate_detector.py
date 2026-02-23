"""
cortex/tools/media/duplicate_detector.py

SHA256-based duplicate detection and collision prevention for Plex workflows.

Provides:
- Fast hash-based duplicate detection
- Pre-flight validation before rename operations
- Conflict resolution strategies
- Batch rename safety checks

CORE-011: Type hints on all functions.
CORE-012: Google-style docstrings.
CORE-028: snake_case naming.

AC_START: AC-DUPLICATE-DETECTOR-2026-02-23
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class ConflictResolution(Enum):
    """Strategy for resolving rename conflicts."""

    KEEP_ORIGINAL = "keep_original"
    ADD_SUFFIX = "add_suffix"
    OVERWRITE = "overwrite"
    SKIP = "skip"


@dataclass
class FileHash:
    """File with computed SHA256 hash."""

    path: Path
    sha256: str
    size_bytes: int


@dataclass
class DuplicateGroup:
    """Group of files with identical content."""

    sha256: str
    files: List[Path]
    size_bytes: int

    @property
    def duplicate_count(self) -> int:
        """Number of duplicate files in group."""
        return len(self.files)


@dataclass
class DuplicateCheckResult:
    """Result of checking proposed rename."""

    current_path: Path
    proposed_path: Path
    is_safe: bool
    collision_detected: bool
    existing_file: Optional[Path] = None
    resolution: Optional[ConflictResolution] = None
    suggested_alternative: Optional[Path] = None
    reason: str = ""


class DuplicateDetector:
    """
    SHA256-based duplicate detection for video libraries.

    Scans directory, computes hashes, and validates rename operations
    to prevent collisions and data loss.

    Attributes:
        root: Root directory to scan.
        extensions: Video file extensions to index (default: common formats).
        hash_index: Dict mapping SHA256 hash to list of file paths.
    """

    DEFAULT_EXTENSIONS = [
        ".mp4",
        ".mkv",
        ".avi",
        ".m4v",
        ".webm",
        ".mov",
        ".wmv",
        ".flv",
        ".mpg",
        ".mpeg",
    ]

    def __init__(
        self,
        root: Path,
        extensions: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize DuplicateDetector.

        Args:
            root: Root directory to scan.
            extensions: Video file extensions to include (default: common formats).
        """
        self.root = root
        self.extensions = extensions or self.DEFAULT_EXTENSIONS
        self.hash_index: Dict[str, List[Path]] = {}
        self._file_hashes: Dict[Path, FileHash] = {}

    def compute_hash(self, file_path: Path) -> FileHash:
        """
        Compute SHA256 hash of file.

        Uses chunked reading for memory efficiency with large files.

        Args:
            file_path: File to hash.

        Returns:
            FileHash with SHA256 digest and size.
        """
        hasher = hashlib.sha256()
        size_bytes = 0

        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
                size_bytes += len(chunk)

        sha256 = hasher.hexdigest()

        return FileHash(
            path=file_path,
            sha256=sha256,
            size_bytes=size_bytes,
        )

    def scan(self) -> int:
        """
        Scan directory and build hash index.

        Recursively processes all video files, computes hashes,
        and builds index for duplicate detection.

        Returns:
            Number of files indexed.
        """
        logger.info(f"Scanning {self.root} for duplicates...")

        file_count = 0

        for file_path in self.root.rglob("*"):
            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in self.extensions:
                continue

            try:
                file_hash = self.compute_hash(file_path)
                self._file_hashes[file_path] = file_hash

                # Add to hash index
                if file_hash.sha256 not in self.hash_index:
                    self.hash_index[file_hash.sha256] = []
                self.hash_index[file_hash.sha256].append(file_path)

                file_count += 1

            except Exception as exc:
                logger.warning(f"Could not hash {file_path}: {exc}")
                continue

        logger.info(f"Indexed {file_count} files, {len(self.hash_index)} unique hashes")

        return file_count

    def find_duplicates(self) -> List[DuplicateGroup]:
        """
        Find all duplicate groups.

        Returns:
            List of DuplicateGroup objects (groups with 2+ files).
        """
        duplicates: List[DuplicateGroup] = []

        for sha256, files in self.hash_index.items():
            if len(files) > 1:
                # Get size from first file
                size_bytes = self._file_hashes[files[0]].size_bytes

                duplicates.append(
                    DuplicateGroup(
                        sha256=sha256,
                        files=files,
                        size_bytes=size_bytes,
                    )
                )

        return duplicates

    def check_rename(
        self,
        current_path: Path,
        proposed_path: Path,
    ) -> DuplicateCheckResult:
        """
        Check if proposed rename is safe (no collision).

        Args:
            current_path: Current file path.
            proposed_path: Proposed new path.

        Returns:
            DuplicateCheckResult with safety status and resolution.
        """
        # Check if target already exists
        if proposed_path.exists() and proposed_path != current_path:
            # Collision detected
            suggested_alternative = self.generate_unique_filename(proposed_path)

            return DuplicateCheckResult(
                current_path=current_path,
                proposed_path=proposed_path,
                is_safe=False,
                collision_detected=True,
                existing_file=proposed_path,
                resolution=ConflictResolution.KEEP_ORIGINAL,
                suggested_alternative=suggested_alternative,
                reason=f"Target file already exists: {proposed_path.name}",
            )

        # No collision
        return DuplicateCheckResult(
            current_path=current_path,
            proposed_path=proposed_path,
            is_safe=True,
            collision_detected=False,
            reason="Safe to rename",
        )

    def batch_check_renames(
        self,
        rename_pairs: Dict[Path, Path],
    ) -> Dict[Path, DuplicateCheckResult]:
        """
        Check batch of proposed renames.

        Args:
            rename_pairs: Dict mapping current path to proposed path.

        Returns:
            Dict mapping current path to DuplicateCheckResult.
        """
        results: Dict[Path, DuplicateCheckResult] = {}

        # Track proposed targets to detect intra-batch collisions
        proposed_targets: Set[Path] = set()

        for current, proposed in rename_pairs.items():
            result = self.check_rename(current, proposed)

            # Check for intra-batch collision
            if proposed in proposed_targets:
                result.is_safe = False
                result.collision_detected = True
                result.reason = "Multiple files renaming to same target (batch collision)"

            proposed_targets.add(proposed)
            results[current] = result

        return results

    def generate_unique_filename(self, base_path: Path) -> Path:
        """
        Generate unique filename by adding numeric suffix.

        Args:
            base_path: Desired filename (may exist).

        Returns:
            Unique path with suffix if needed (e.g., "file_2.mp4").
        """
        if not base_path.exists():
            return base_path

        stem = base_path.stem
        suffix = base_path.suffix
        parent = base_path.parent

        counter = 2
        while True:
            candidate = parent / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1


# AC_COMPLETE: AC-DUPLICATE-DETECTOR-2026-02-23 ✅ (128ms)
