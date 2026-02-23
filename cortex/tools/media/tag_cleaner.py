"""
cortex/tools/media/tag_cleaner.py

MediaTagCleaner — top-level orchestrator that wires together:

    MediaScanner  →  FilenameParser  →  TagWriterFactory  →  mutagen save

Responsibilities
----------------
* Recurse every media file under ``root`` via :class:`MediaScanner`.
* Derive clean metadata from the filename via :class:`FilenameParser`.
* Optionally use the immediate parent folder name as the **album** tag.
* Detect which fields have actually changed (avoids unnecessary writes).
* Support **dry-run** mode — compute all changes, emit results, write nothing.
* Return a :class:`CleanResult` for every file so callers can report/audit.

Usage (programmatic)::

    from pathlib import Path
    from cortex.tools.media.tag_cleaner import MediaTagCleaner

    cleaner = MediaTagCleaner(
        root=Path("Z:/MUSIC/Bollywood"),
        dry_run=False,
        use_folder_as_album=True,
        clear_stale_tags=True,
        genre="Bollywood",
    )
    results = cleaner.run()
    errors = [r for r in results if not r.success]

CORE-011: All functions have type hints.
CORE-012: All public APIs have docstrings.
CORE-028: snake_case naming.

AC_START: AC-MEDIA-2026-02-23-004
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from cortex.tools.media.filename_parser import FilenameParser, ParsedMetadata
from cortex.tools.media.media_scanner import MediaFile, MediaScanner
from cortex.tools.media.tag_writer import TagFields, TagWriterFactory

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class CleanResult:
    """
    Outcome of processing a single media file.

    Attributes:
        path:       Absolute path to the file.
        success:    ``True`` if tags were written (or would be in dry-run).
        old_title:  Title tag value *before* cleaning (``None`` if unreadable).
        new_title:  Title tag value that was (or would be) written.
        changes:    Dict mapping field name → ``(old_value, new_value)`` for
                    every tag that changed.
        dry_run:    Whether this result is from a dry-run (no real write).
        error:      Error message if ``success`` is ``False``.
        duration_ms: Time taken to process this file in milliseconds.
    """

    path: Path
    success: bool
    old_title: Optional[str]
    new_title: str
    changes: Dict[str, Tuple[Optional[str], str]]
    dry_run: bool = False
    error: Optional[str] = None
    duration_ms: float = 0.0


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


class MediaTagCleaner:
    """
    High-level orchestrator: scan → parse → diff → write (or report in dry-run).

    Attributes:
        root:              Root directory to scan recursively.
        dry_run:           If ``True``, compute changes without writing.
        use_folder_as_album: Use the immediate parent folder name as the album tag.
        clear_stale_tags:  Pass ``clear_stale=True`` to every :class:`TagWriter`.
        extensions:        Override default scanner extension set.
        genre:             Override genre for all files (``None`` = keep existing).
        year:              Override year for all files (``None`` = keep existing).
        comment:           Override comment field (``None`` = keep existing).
    """

    def __init__(
        self,
        root: Path,
        dry_run: bool = False,
        use_folder_as_album: bool = True,
        clear_stale_tags: bool = True,
        extensions: Optional[Set[str]] = None,
        genre: Optional[str] = None,
        year: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> None:
        """
        Initialise a :class:`MediaTagCleaner`.

        Args:
            root:                Root directory to scan.
            dry_run:             When ``True`` no files are modified.
            use_folder_as_album: Parent folder → album tag.
            clear_stale_tags:    Remove stale legacy atoms before writing.
            extensions:          Custom extension whitelist for :class:`MediaScanner`.
            genre:               Force a genre string onto every processed file.
            year:                Force a year string onto every processed file.
            comment:             Force a comment string onto every processed file.
        """
        self.root = root
        self.dry_run = dry_run
        self.use_folder_as_album = use_folder_as_album
        self.clear_stale_tags = clear_stale_tags
        self.extensions = extensions
        self.genre = genre
        self.year = year
        self.comment = comment

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> List[CleanResult]:
        """
        Execute the full scan → clean cycle.

        Returns:
            List of :class:`CleanResult`, one per discovered media file.
            Always returns a list — never raises (errors are captured in results).
        """
        # AC_START: AC-MEDIA-RUN-{ts}
        ts_start = time.monotonic()

        scanner = MediaScanner(self.root, extensions=self.extensions)
        try:
            media_files: List[MediaFile] = scanner.scan()
        except FileNotFoundError as exc:
            logger.error("Root not found: %s", exc)
            return []

        results: List[CleanResult] = []
        for mf in media_files:
            result = self._process_file(mf)
            results.append(result)
            self._log_result(result)

        total_ms = (time.monotonic() - ts_start) * 1000
        passed = sum(1 for r in results if r.success)
        skipped = sum(1 for r in results if r.success and not r.changes)
        failed = sum(1 for r in results if not r.success)
        logger.info(
            "MediaTagCleaner complete | files=%d passed=%d skipped=%d failed=%d "
            "total_ms=%.0f dry_run=%s",
            len(results),
            passed,
            skipped,
            failed,
            total_ms,
            self.dry_run,
        )
        # AC_COMPLETE: AC-MEDIA-RUN ✅
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _process_file(self, mf: MediaFile) -> CleanResult:
        """Process a single :class:`MediaFile`, returning a :class:`CleanResult`."""
        t0 = time.monotonic()
        writer = TagWriterFactory.for_file(mf.path)
        if writer is None:
            return CleanResult(
                path=mf.path,
                success=False,
                old_title=None,
                new_title="",
                changes={},
                dry_run=self.dry_run,
                error=f"No tag writer for extension '{mf.extension}'",
                duration_ms=0.0,
            )

        # Read existing tags
        try:
            existing: TagFields = writer.read_tags(mf.path)
        except Exception as exc:  # noqa: BLE001
            return CleanResult(
                path=mf.path,
                success=False,
                old_title=None,
                new_title="",
                changes={},
                dry_run=self.dry_run,
                error=f"read_tags failed: {exc}",
                duration_ms=_ms(t0),
            )

        # Parse filename → desired metadata
        parsed: ParsedMetadata = FilenameParser.from_path(mf.path)

        # Resolve album
        album: Optional[str] = (
            mf.folder_name if self.use_folder_as_album else existing.album
        )

        # Build desired TagFields, applying overrides
        desired = TagFields(
            title=parsed.title,
            artist=parsed.artist if parsed.artist is not None else existing.artist,
            album=album,
            year=self.year if self.year is not None else existing.year,
            genre=self.genre if self.genre is not None else existing.genre,
            track_number=(
                parsed.track_number
                if parsed.track_number is not None
                else existing.track_number
            ),
            comment=self.comment if self.comment is not None else existing.comment,
        )

        # Diff — which fields actually changed?
        changes = _diff_fields(existing, desired)

        if not changes:
            # Nothing to do
            return CleanResult(
                path=mf.path,
                success=True,
                old_title=existing.title or None,
                new_title=desired.title,
                changes={},
                dry_run=self.dry_run,
                duration_ms=_ms(t0),
            )

        # Write (unless dry-run)
        if not self.dry_run:
            try:
                ok = writer.write_tags(mf.path, desired, clear_stale=self.clear_stale_tags)
            except Exception as exc:  # noqa: BLE001
                return CleanResult(
                    path=mf.path,
                    success=False,
                    old_title=existing.title or None,
                    new_title=desired.title,
                    changes=changes,
                    dry_run=self.dry_run,
                    error=f"write_tags failed: {exc}",
                    duration_ms=_ms(t0),
                )
            if not ok:
                return CleanResult(
                    path=mf.path,
                    success=False,
                    old_title=existing.title or None,
                    new_title=desired.title,
                    changes=changes,
                    dry_run=self.dry_run,
                    error="write_tags returned False (corrupt file?)",
                    duration_ms=_ms(t0),
                )

        return CleanResult(
            path=mf.path,
            success=True,
            old_title=existing.title or None,
            new_title=desired.title,
            changes=changes,
            dry_run=self.dry_run,
            duration_ms=_ms(t0),
        )

    @staticmethod
    def _log_result(result: CleanResult) -> None:
        """Emit a log line summarising the result."""
        prefix = "[DRY-RUN] " if result.dry_run else ""
        if result.success and result.changes:
            logger.info(
                "%s✅ %s | title: '%s' → '%s'",
                prefix,
                result.path.name,
                result.old_title,
                result.new_title,
            )
        elif result.success and not result.changes:
            logger.debug("%s⏭  %s — no changes", prefix, result.path.name)
        else:
            logger.warning(
                "%s❌ %s — %s", prefix, result.path.name, result.error
            )


# ---------------------------------------------------------------------------
# Private utilities
# ---------------------------------------------------------------------------


def _ms(t0: float) -> float:
    """Elapsed milliseconds since *t0* (from :func:`time.monotonic`)."""
    return (time.monotonic() - t0) * 1000


def _diff_fields(
    existing: TagFields,
    desired: TagFields,
) -> Dict[str, Tuple[Optional[str], str]]:
    """
    Compare *existing* vs *desired* :class:`TagFields`.

    Returns:
        Dict ``{field_name: (old_value, new_value)}`` for every field that
        differs.  Only string-comparable fields are included; ``track_number``
        is compared numerically.
    """
    changes: Dict[str, Tuple[Optional[str], str]] = {}

    def _check(name: str, old: Optional[str], new: Optional[str]) -> None:
        if new is not None and old != new:
            changes[name] = (old, new)

    _check("title", existing.title or None, desired.title or None)
    _check("artist", existing.artist, desired.artist)
    _check("album", existing.album, desired.album)
    _check("year", existing.year, desired.year)
    _check("genre", existing.genre, desired.genre)
    _check("comment", existing.comment, desired.comment)

    # Track number — convert to str for homogeneous comparison
    old_trk = str(existing.track_number) if existing.track_number is not None else None
    new_trk = str(desired.track_number) if desired.track_number is not None else None
    _check("track_number", old_trk, new_trk)

    return changes


# AC_COMPLETE: AC-MEDIA-2026-02-23-004 ✅
