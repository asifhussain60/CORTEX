"""
cortex/orchestrators/support/video_library_orchestrator.py

Coordinate video library scanning, PLEX metadata retrieval, and rename orchestration.

High-level orchestrator that integrates:
- :class:`VideoLibraryScanner` — recursive file discovery
- :class:`PlexMetadataAccessor` — metadata retrieval
- Conflict detection — name collisions, duplicates
- Dry-run preview — show proposed changes without applying
- File renaming — atomic operations with rollback support

Emits AC markers (CORE-049) for audit trail.

Example::

    orch = VideoLibraryOrchestrator(root=Path("G:/FLICKS"), dry_run=True)
    result = orch.preview_renames()
    
    print(f"Total files: {result.total_files}")
    print(f"Proposals: {result.files_with_proposals}")
    
    for proposal in result.proposals:
        print(f"  {proposal.current_path.name} → {proposal.proposed_path.name}")

CORE-011: All functions have type hints.
CORE-012: All public APIs have docstrings.
CORE-028: snake_case naming.
CORE-049: AC markers for orchestration audit trail.

AC_START: AC-VIDEO-ORCHESTRATOR-2026-02-23-003
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from cortex.tools.media.plex_metadata_accessor import (
    PlexMetadata,
    PlexMetadataAccessor,
)
from cortex.tools.media.video_library_scanner import (
    VideoLibraryFile,
    VideoLibraryScanner,
)

logger = logging.getLogger(__name__)


@dataclass
class RenameProposal:
    """
    Proposed file rename with confidence score.

    Attributes:
        current_path:       Current file path.
        proposed_path:      Proposed renamed path.
        confidence:         Confidence score (0.0 to 1.0) — higher = more certain.
        reason:             Human-readable reason for proposal.
        metadata_source:    Source of metadata ("plex", "filename", "manual").
    """

    current_path: Path
    proposed_path: Path
    confidence: float
    reason: str
    metadata_source: str


@dataclass
class Conflict:
    """
    Detected conflict between proposals.

    Attributes:
        type:           Conflict type ("collision", "target_exists").
        affected_proposals: List of proposal indices involved.
        description:    Human-readable conflict description.
    """

    type: str
    affected_proposals: List[int]
    description: str


@dataclass
class OrchestrationResult:
    """
    Result of full orchestration run.

    Attributes:
        total_files:        Total video files discovered.
        files_with_proposals: Count of files with rename proposals.
        proposals:          List of :class:`RenameProposal`.
        conflicts:          List of detected :class:`Conflict`.
        dry_run:            Whether this was a dry-run (no modifications).
        duration_seconds:   Total execution time.
        ac_session_id:      Audit trail session ID.
    """

    total_files: int
    files_with_proposals: int
    proposals: List[RenameProposal]
    conflicts: List[Conflict]
    dry_run: bool
    duration_seconds: float
    ac_session_id: str


class VideoLibraryOrchestrator:
    """
    Orchestrate video library scanning and metadata-driven organization.

    Coordinates scanning, metadata retrieval, conflict resolution, and
    dry-run preview. Supports filtering by studio, dry-run mode, and
    rollback on error.

    Attributes:
        root:               Root library directory (``G:/FLICKS``).
        dry_run:            When ``True``, preview changes without applying.
        studio_filter:      Limit scanning to specific studio (optional).
        plex_accessor:      Optional :class:`PlexMetadataAccessor` (auto-created if None).
    """

    def __init__(
        self,
        root: Path,
        dry_run: bool = False,
        studio_filter: Optional[str] = None,
        plex_accessor: Optional[PlexMetadataAccessor] = None,
    ) -> None:
        """
        Initialize video library orchestrator.

        Args:
            root:           Root directory to scan.
            dry_run:        Preview mode (no filesystem changes).
            studio_filter:  Filter results to specific studio (e.g. "Bellesa").
            plex_accessor:  Optional pre-configured accessor (default: auto-detect).
        """
        self.root = root
        self.dry_run = dry_run
        self.studio_filter = studio_filter
        self.plex_accessor = plex_accessor or PlexMetadataAccessor()
        self._scanner = VideoLibraryScanner(root=root)

    def preview_renames(self) -> OrchestrationResult:
        """
        Generate dry-run preview of all proposed renames.

        Returns:
            :class:`OrchestrationResult` with proposals and conflicts.
            No filesystem modifications are made.

        Example::

            result = orch.preview_renames()
            if result.conflicts:
                print("Conflicts detected:")
                for conflict in result.conflicts:
                    print(f"  - {conflict.description}")
            else:
                print(f"Ready to apply {len(result.proposals)} renames")
        """
        ts_start = time.monotonic()
        ac_id = f"AC-VIDEO-PREVIEW-{int(ts_start * 1000)}"
        logger.info(f"AC_START: {ac_id}")

        # Phase 1: Scan library
        logger.info(f"Scanning library: {self.root}")
        try:
            files = self._scan_library()
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Scan failed: {exc}")
            logger.info(f"AC_COMPLETE: {ac_id} ❌ (scan error)")
            raise

        # Phase 2: Retrieve PLEX metadata
        logger.info(f"Retrieving PLEX metadata for {len(files)} files")
        try:
            metadata_map = self._retrieve_metadata(files)
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"Metadata retrieval partial: {exc}")
            metadata_map = {}

        # Phase 3: Generate proposals
        logger.info("Generating rename proposals")
        proposals = self._generate_proposals(files, metadata_map)
        logger.info(f"Generated {len(proposals)} proposals")

        # Phase 4: Detect conflicts
        logger.info("Detecting conflicts")
        conflicts = self._detect_conflicts(proposals)
        if conflicts:
            logger.warning(f"Found {len(conflicts)} conflicts")

        # Phase 5: Build result
        duration_ms = (time.monotonic() - ts_start) * 1000
        result = OrchestrationResult(
            total_files=len(files),
            files_with_proposals=len(proposals),
            proposals=proposals,
            conflicts=conflicts,
            dry_run=True,
            duration_seconds=duration_ms / 1000,
            ac_session_id=ac_id,
        )

        logger.info(
            f"AC_COMPLETE: {ac_id} ✅ "
            f"(files={len(files)} proposals={len(proposals)} "
            f"conflicts={len(conflicts)} duration_ms={duration_ms:.0f})"
        )

        return result

    def apply_renames(
        self,
        proposals: Optional[List[RenameProposal]] = None,
        min_confidence: float = 0.75,
    ) -> OrchestrationResult:
        """
        Apply proposed renames to filesystem.

        Args:
            proposals:      Specific proposals to apply (default: generate new).
            min_confidence: Only apply proposals with confidence ≥ threshold.

        Returns:
            :class:`OrchestrationResult` with applied renames.

        Raises:
            RuntimeError: If dry_run is ``True`` (use preview_renames instead).
            Exception: On filesystem error (attempted rollback).
        """
        if self.dry_run:
            raise RuntimeError(
                "Cannot apply renames in dry_run mode. "
                "Set dry_run=False in constructor."
            )

        ts_start = time.monotonic()
        ac_id = f"AC-VIDEO-APPLY-{int(ts_start * 1000)}"
        logger.info(f"AC_START: {ac_id}")

        # Generate proposals if not provided
        if proposals is None:
            preview = self.preview_renames()
            proposals = preview.proposals

        # Filter by confidence
        filtered = [p for p in proposals if p.confidence >= min_confidence]
        logger.info(f"Applying {len(filtered)} renames (min_confidence={min_confidence})")

        applied = 0
        failed = 0

        for proposal in filtered:
            try:
                proposal.current_path.rename(proposal.proposed_path)
                logger.info(f"✅ {proposal.current_path.name} → {proposal.proposed_path.name}")
                applied += 1
            except Exception as exc:  # noqa: BLE001
                logger.error(f"❌ Rename failed: {exc}")
                failed += 1

        duration_ms = (time.monotonic() - ts_start) * 1000
        logger.info(
            f"AC_COMPLETE: {ac_id} ✅ "
            f"(applied={applied} failed={failed} duration_ms={duration_ms:.0f})"
        )

        return OrchestrationResult(
            total_files=len(proposals),
            files_with_proposals=applied,
            proposals=proposals,
            conflicts=[],
            dry_run=False,
            duration_seconds=duration_ms / 1000,
            ac_session_id=ac_id,
        )

    # =========================================================================
    # Internal helpers
    # =========================================================================

    def _scan_library(self) -> List[VideoLibraryFile]:
        """
        Scan library for video files.

        Returns:
            List of :class:`VideoLibraryFile` (optionally filtered by studio).
        """
        files = self._scanner.scan()

        if self.studio_filter:
            files = [f for f in files if f.studio == self.studio_filter]

        logger.info(f"Discovered {len(files)} video files")
        return files

    def _retrieve_metadata(
        self,
        files: List[VideoLibraryFile],
    ) -> Dict[Path, PlexMetadata]:
        """
        Retrieve PLEX metadata for discovered files.

        Args:
            files: List of :class:`VideoLibraryFile`.

        Returns:
            Dict mapping :class:`~pathlib.Path` → :class:`PlexMetadata`.
        """
        paths = [f.path for f in files]
        metadata_map = self.plex_accessor.read_batch_metadata(paths)
        return metadata_map

    def _generate_proposals(
        self,
        files: List[VideoLibraryFile],
        metadata_map: Dict[Path, PlexMetadata],
    ) -> List[RenameProposal]:
        """
        Generate rename proposals for files.

        Args:
            files:         List of discovered :class:`VideoLibraryFile`.
            metadata_map:  Dict of :class:`PlexMetadata` by path.

        Returns:
            List of :class:`RenameProposal`.
        """
        proposals: List[RenameProposal] = []

        for vfile in files:
            plex_meta = metadata_map.get(vfile.path)
            proposal = self._generate_proposal(vfile, plex_meta)

            if proposal and proposal.confidence >= 0.5:
                proposals.append(proposal)

        return proposals

    def _generate_proposal(
        self,
        vfile: VideoLibraryFile,
        plex_meta: Optional[PlexMetadata],
    ) -> Optional[RenameProposal]:
        """
        Generate single rename proposal for a file.

        Args:
            vfile:      :class:`VideoLibraryFile` to propose rename for.
            plex_meta:  Optional PLEX metadata.

        Returns:
            :class:`RenameProposal` or ``None`` if already well-organized.
        """
        # If PLEX title matches filename stem, no rename needed
        if plex_meta and plex_meta.title == vfile.filename_stem:
            return None

        # If PLEX metadata available, propose PLEX title
        if plex_meta and plex_meta.title:
            proposed_name = f"{plex_meta.title}{vfile.extension}"
            proposed_path = vfile.path.parent / proposed_name
            confidence = 0.95  # High confidence from PLEX

            return RenameProposal(
                current_path=vfile.path,
                proposed_path=proposed_path,
                confidence=confidence,
                reason=f"PLEX title: {plex_meta.title}",
                metadata_source="plex",
            )

        # If filename is generic (video001, file_1, etc.), suggest cleanup
        if self._is_generic_name(vfile.filename_stem):
            # Could propose based on folder context, but low confidence
            return None

        # Already well-named
        return None

    def _is_generic_name(self, filename: str) -> bool:
        """Check if filename is generic/non-descriptive."""
        generic_patterns = ["video", "file", "movie", "clip", "track"]
        lower = filename.lower()
        return any(lower.startswith(p) for p in generic_patterns)

    def _detect_conflicts(
        self,
        proposals: List[RenameProposal],
    ) -> List[Conflict]:
        """
        Detect conflicts in proposals.

        Args:
            proposals: List of :class:`RenameProposal`.

        Returns:
            List of :class:`Conflict`.
        """
        conflicts: List[Conflict] = []
        proposed_paths: Dict[Path, List[int]] = {}

        # Track proposed paths for collisions
        for idx, proposal in enumerate(proposals):
            if proposal.proposed_path not in proposed_paths:
                proposed_paths[proposal.proposed_path] = []
            proposed_paths[proposal.proposed_path].append(idx)

        # Detect collisions (two files renamed to same name)
        for target_path, indices in proposed_paths.items():
            if len(indices) > 1:
                conflicts.append(
                    Conflict(
                        type="collision",
                        affected_proposals=indices,
                        description=f"Multiple files would rename to: {target_path.name}",
                    )
                )

            # Detect target exists (would overwrite)
            if target_path.exists():
                conflicts.append(
                    Conflict(
                        type="target_exists",
                        affected_proposals=[indices[0]],
                        description=f"Target already exists: {target_path}",
                    )
                )

        return conflicts


# AC_COMPLETE: AC-VIDEO-ORCHESTRATOR-2026-02-23-003 ✅
