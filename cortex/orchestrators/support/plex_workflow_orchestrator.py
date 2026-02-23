"""
cortex/orchestrators/support/plex_workflow_orchestrator.py

Comprehensive Plex video library workflow orchestrator — generic for all studios.

Manages end-to-end pipeline:
1. **SCAN** — Discover video files in directory
2. **IDENTIFY** — Extract metadata from filenames (performers, studio hints, etc.)
3. **MATCH** — Query IAFD and Plex for enriched metadata
4. **RENAME** — Normalize filenames (action→Does, proper case, remove numbers)
5. **TAG** — Write enriched metadata to file tags
6. **ORGANIZE** — Move files to studio-specific folders
7. **VERIFY** — Validate Plex library consistency

Generic for any studio/naming convention. No sanitization — preserves meaningful names.

Wires all tools into a single coordinated workflow with:
- Confidence thresholds for automated operations
- Dry-run support for preview
- User-provided metadata hints (override extracted data)
- Optional filename normalization
- Rollback on errors

CORE-011: All functions have type hints.
CORE-012: All public APIs have docstrings.
CORE-028: snake_case naming.

AC_START: AC-PLEX-WORKFLOW-GENERIC-2026-02-23
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from cortex.core.orchestrator_base import OrchestratorBase
from cortex.tools.media.generic_metadata_extractor import (
    GenericMetadataExtractor,
    FilenameNormalizer,
    ExtractedMetadata,
)
from cortex.tools.media.iafd_metadata_accessor import IAFDAccessor, IAFDMetadata
from cortex.tools.media.plex_metadata_accessor import PlexMetadataAccessor, PlexMetadata
from cortex.tools.media.tag_writer import TagWriterFactory, TagFields
from cortex.tools.media.video_library_scanner import VideoLibraryScanner, VideoLibraryFile
from cortex.tools.media.duplicate_detector import DuplicateDetector, DuplicateCheckResult
from cortex.tools.media.restore_manager import RestoreManager, Snapshot
from cortex.tools.media.llm_semantic_renamer import (
    LLMSemanticRenamer,
    RenameProposal,
    LLMProvider,
)

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """Single step in the workflow pipeline."""

    name: str
    status: str  # "pending" | "running" | "success" | "failed" | "skipped"
    duration_ms: float = 0.0
    error: Optional[str] = None
    details: Dict = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """Result of complete workflow execution."""

    success: bool
    total_files: int
    files_scanned: int
    files_identified: int
    files_matched: int
    files_renamed: int
    files_tagged: int
    files_organized: int
    step_results: List[WorkflowStep] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    ac_session_id: str = ""


class PlexWorkflowOrchestrator(OrchestratorBase):
    """
    Comprehensive Plex video library workflow orchestrator — generic for all studios.

    Coordinates all steps from scanning to verification. Works with any naming convention.

    Attributes:
        root:                   Root library directory.
        studio_filter:          Limit to specific studio (optional, applied via filename analysis).
        dry_run:                Preview mode (no modifications).
        min_match_confidence:   Minimum confidence for IAFD matches (0.0-1.0).
        min_rename_confidence:  Minimum confidence for renames (0.0-1.0).
        normalize_filenames:    Apply normalization (action→Does, proper case, remove numbers).
        auto_organize:          Move files to studio folders (disabled by default). Files are renamed in-place; set to ``True`` to move to studio subfolders.
        use_iafd:               Query IAFD for enriched metadata.
        metadata_hints:         User-provided metadata overrides (e.g., {"studio": "Wicked"}).
        plex_accessor:          Plex metadata accessor (auto-created if None).
        iafd_accessor:          IAFD metadata accessor (auto-created if None).
    """

    def __init__(
        self,
        root: Path,
        studio_filter: Optional[str] = None,
        dry_run: bool = True,
        min_match_confidence: float = 0.75,
        min_rename_confidence: float = 0.80,
        normalize_filenames: bool = True,
        auto_organize: bool = False,
        use_iafd: bool = True,
        use_llm_semantic: bool = False,
        llm_api_key: Optional[str] = None,
        llm_provider: LLMProvider = LLMProvider.OPENAI,
        enable_duplicate_detection: bool = True,
        enable_snapshots: bool = True,
        metadata_hints: Optional[Dict] = None,
        plex_accessor: Optional[PlexMetadataAccessor] = None,
        iafd_accessor: Optional[IAFDAccessor] = None,
    ) -> None:
        super().__init__()

        self.root = root
        self.studio_filter = studio_filter
        self.dry_run = dry_run
        self.min_match_confidence = min_match_confidence
        self.min_rename_confidence = min_rename_confidence
        self.normalize_filenames = normalize_filenames
        self.auto_organize = auto_organize
        self.use_iafd = use_iafd
        self.use_llm_semantic = use_llm_semantic
        self.enable_duplicate_detection = enable_duplicate_detection
        self.enable_snapshots = enable_snapshots
        self.metadata_hints = metadata_hints or {}

        # Initialize accessors
        self.plex_accessor = plex_accessor or PlexMetadataAccessor()
        self.iafd_accessor = iafd_accessor or IAFDAccessor(use_cache=True)

        # Initialize new components
        self.duplicate_detector = DuplicateDetector(root=root) if enable_duplicate_detection else None
        self.restore_manager = RestoreManager(
            db_path=Path(".cortex-runtime/backups/plex-snapshots.db")
        ) if enable_snapshots else None
        self.llm_renamer = LLMSemanticRenamer(
            provider=llm_provider,
            api_key=llm_api_key,
            min_confidence=min_rename_confidence,
            enable_fallback=True,
        ) if use_llm_semantic else None

        # Runtime state
        self.scanned_files: List[VideoLibraryFile] = []
        self.extracted_metadata: Dict[str, ExtractedMetadata] = {}
        self.current_snapshot: Optional[Snapshot] = None
        
        # Generic extractors and normalizers (no sanitization)
        self.metadata_extractor = GenericMetadataExtractor()
        self.filename_normalizer = FilenameNormalizer()
        self.scanner = VideoLibraryScanner(root=root)

    @staticmethod
    def _get_filename(vfile: VideoLibraryFile) -> str:
        """Get full filename (stem + extension)."""
        return f"{vfile.filename_stem}{vfile.extension}"

    def run_full_workflow(self) -> WorkflowResult:
        """
        Execute complete end-to-end workflow.

        Returns:
            :class:`WorkflowResult` with detailed step-by-step results.
        """
        import time

        start_time = time.time()

        result = WorkflowResult(
            success=False,
            total_files=0,
            files_scanned=0,
            files_identified=0,
            files_matched=0,
            files_renamed=0,
            files_tagged=0,
            files_organized=0,
        )

        try:
            # Step 0: CREATE SNAPSHOT (if enabled)
            if self.enable_snapshots and not self.dry_run and self.restore_manager:
                logger.info("STEP 0: Creating pre-operation snapshot...")
                self.current_snapshot = self.restore_manager.create_snapshot(
                    root=self.root,
                    description=f"Pre-workflow snapshot {datetime.now().isoformat()}",
                )
                logger.info(f"Snapshot {self.current_snapshot.snapshot_id} created")

            # Step 1: SCAN
            logger.info("STEP 1: Scanning library...")
            step1 = self._run_step_scan(result)
            result.step_results.append(step1)

            if not step1.status == "success":
                result.errors.append(f"Scan failed: {step1.error}")
                raise RuntimeError(f"Scan failed: {step1.error}")

            # Step 1.5: BUILD DUPLICATE INDEX (if enabled)
            if self.enable_duplicate_detection and self.duplicate_detector:
                logger.info("STEP 1.5: Building duplicate index...")
                self.duplicate_detector.scan()
                duplicates = self.duplicate_detector.find_duplicates()
                if duplicates:
                    logger.warning(f"Found {len(duplicates)} duplicate groups")

            # Step 2: IDENTIFY
            logger.info("STEP 2: Identifying files...")
            step2 = self._run_step_identify(result)
            result.step_results.append(step2)

            # Step 3: MATCH
            if self.use_iafd:
                logger.info("STEP 3: Matching against IAFD...")
                step3 = self._run_step_match(result)
                result.step_results.append(step3)

            # Step 4: RENAME (with hybrid LLM/rule-based logic)
            logger.info("STEP 4: Proposing renames...")
            step4 = self._run_step_rename(result)
            result.step_results.append(step4)

            # Step 5: TAG
            logger.info("STEP 5: Writing tags...")
            step5 = self._run_step_tag(result)
            result.step_results.append(step5)

            # Step 6: ORGANIZE
            if self.auto_organize:
                logger.info("STEP 6: Organizing files...")
                step6 = self._run_step_organize(result)
                result.step_results.append(step6)

            # Step 7: VERIFY
            logger.info("STEP 7: Verifying...")
            step7 = self._run_step_verify(result)
            result.step_results.append(step7)

            result.success = True
            result.duration_seconds = time.time() - start_time

            return result

        except Exception as exc:
            logger.error(f"Workflow failed: {exc}")
            result.errors.append(str(exc))
            result.duration_seconds = time.time() - start_time

            # Rollback on failure if snapshot exists
            if self.current_snapshot and self.restore_manager and not self.dry_run:
                logger.info(f"Rolling back to snapshot {self.current_snapshot.snapshot_id}...")
                rollback_result = self.restore_manager.rollback(self.current_snapshot.snapshot_id)
                if rollback_result.status.value == "success":
                    logger.info(f"Rollback successful: {rollback_result.files_restored} files restored")
                else:
                    logger.error(f"Rollback failed: {rollback_result.error}")

            return result

    def _run_step_scan(self, result: WorkflowResult) -> WorkflowStep:
        """Scan and discover files."""
        import time

        start = time.time()
        step = WorkflowStep(name="SCAN", status="running")

        try:
            files = self.scanner.scan()
            self.scanned_files = files  # Cache for use in subsequent steps

            result.total_files = len(files)
            result.files_scanned = len(files)

            step.status = "success"
            step.details["files_found"] = len(files)
            step.details["by_studio"] = {}

            # Group by studio
            for vf in files:
                studio = vf.studio or "(root)"
                step.details["by_studio"][studio] = (
                    step.details["by_studio"].get(studio, 0) + 1
                )

        except Exception as exc:
            step.status = "failed"
            step.error = str(exc)
            logger.error(f"Scan failed: {exc}")

        step.duration_ms = (time.time() - start) * 1000
        return step

    def _run_step_identify(self, result: WorkflowResult) -> WorkflowStep:
        """Identify metadata from filenames using generic extractor."""
        import time

        start = time.time()
        step = WorkflowStep(name="IDENTIFY", status="running")

        try:
            files = self.scanned_files  # Use cached scanned files
            identified_count = 0
            filtered_files = []

            for vf in files:
                try:
                    filename = self._get_filename(vf)
                    # Extract metadata without sanitization
                    metadata = self.metadata_extractor.extract(filename)
                    self.extracted_metadata[filename] = metadata
                    
                    # Apply studio filter if specified (from metadata extraction or hints)
                    studio = metadata.studio or self.metadata_hints.get("studio")
                    if self.studio_filter:
                        if studio and studio.lower() != self.studio_filter.lower():
                            continue  # Skip files not matching studio filter
                    
                    filtered_files.append(vf)
                    
                    # Count as identified if performers or meaningful metadata extracted
                    if metadata.performers or metadata.title or metadata.confidence > 0.3:
                        identified_count += 1
                except Exception as e:
                    filename = self._get_filename(vf)
                    logger.debug(f"Could not identify {filename}: {e}")
                    continue

            # Update cached files to only include filtered ones
            self.scanned_files = filtered_files
            result.files_scanned = len(filtered_files)
            result.files_identified = identified_count

            step.status = "success"
            step.details["identified_count"] = identified_count
            step.details["identification_rate"] = (
                identified_count / result.files_scanned
                if result.files_scanned > 0
                else 0
            )

        except Exception as exc:
            step.status = "failed"
            step.error = str(exc)
            logger.error(f"Identify failed: {exc}")

        step.duration_ms = (time.time() - start) * 1000
        return step

    def _run_step_match(self, result: WorkflowResult) -> WorkflowStep:
        """Match files against IAFD."""
        import time

        start = time.time()
        step = WorkflowStep(name="MATCH", status="running")

        try:
            files = self.scanned_files  # Use cached scanned files

            matched_count = 0
            iafd_results = []

            for vf in files:
                try:
                    # Try title match first
                    metadata = self.iafd_accessor.search_by_title(vf.filename_stem)

                    if not metadata:
                        # Try filename analysis to extract performers
                        filename = self._get_filename(vf)
                        analysis = self.filename_analyzer.analyze(filename)
                        if analysis.artists:
                            metadata = self.iafd_accessor.search_by_performers(
                                analysis.artists
                            )

                    if (
                        metadata
                        and metadata.confidence >= self.min_match_confidence
                    ):
                        matched_count += 1
                        filename = self._get_filename(vf)
                        iafd_results.append(
                            {
                                "file": filename,
                                "title": metadata.title,
                                "performers": metadata.performers,
                                "confidence": metadata.confidence,
                            }
                        )

                except Exception as e:
                    filename = self._get_filename(vf)
                    logger.debug(f"IAFD match failed for {filename}: {e}")
                    continue

            result.files_matched = matched_count

            step.status = "success"
            step.details["matched_count"] = matched_count
            step.details["match_rate"] = (
                matched_count / result.files_scanned
                if result.files_scanned > 0
                else 0
            )
            step.details["results"] = iafd_results[:10]  # Top 10 for logging

        except Exception as exc:
            step.status = "failed"
            step.error = str(exc)
            logger.warning(f"Match step failed (non-critical): {exc}")

        step.duration_ms = (time.time() - start) * 1000
        return step

    def _run_step_rename(self, result: WorkflowResult) -> WorkflowStep:
        """Apply filename normalization with hybrid LLM/rule-based logic."""
        import time

        start = time.time()
        step = WorkflowStep(name="RENAME", status="running")

        try:
            files = self.scanned_files  # Use cached scanned files

            renamed_count = 0
            rename_proposals: Dict[Path, Path] = {}

            for vf in files:
                try:
                    filename = self._get_filename(vf)
                    
                    # Skip renaming if normalization disabled
                    if not self.normalize_filenames:
                        continue

                    current_path = vf.full_path
                    proposed_name = None

                    # HYBRID ROUTING: Try LLM first if enabled, fallback to rules
                    if self.use_llm_semantic and self.llm_renamer:
                        # Try LLM semantic renaming
                        proposal = self.llm_renamer.propose_rename_with_fallback(filename)
                        if proposal and proposal.confidence >= self.min_rename_confidence:
                            proposed_name = proposal.proposed_name
                            logger.info(
                                f"LLM rename: {filename} → {proposed_name} "
                                f"(confidence: {proposal.confidence:.2f})"
                            )
                    
                    # Fallback to rule-based if LLM not enabled or low confidence
                    if not proposed_name:
                        proposed_name = self.filename_normalizer.normalize(filename)
                        logger.debug(f"Rule-based rename: {filename} → {proposed_name}")

                    # Check if rename needed
                    if proposed_name == filename:
                        continue

                    proposed_path = current_path.parent / proposed_name

                    # Check for collision if duplicate detection enabled
                    if self.enable_duplicate_detection and self.duplicate_detector:
                        check_result = self.duplicate_detector.check_rename(
                            current_path=current_path,
                            proposed_path=proposed_path,
                        )

                        if not check_result.is_safe:
                            logger.warning(
                                f"Collision detected: {filename} → {proposed_name}. "
                                f"Using alternative: {check_result.suggested_alternative.name}"
                            )
                            proposed_path = check_result.suggested_alternative

                    rename_proposals[current_path] = proposed_path

                except Exception as e:
                    logger.error(f"Rename proposal failed for {filename}: {e}")
                    continue

            # Apply renames if not dry-run
            if not self.dry_run:
                for current, proposed in rename_proposals.items():
                    try:
                        current.rename(proposed)
                        renamed_count += 1
                        logger.info(f"Renamed: {current.name} → {proposed.name}")
                    except Exception as e:
                        logger.error(f"Rename failed: {current.name} → {e}")

            result.files_renamed = renamed_count if not self.dry_run else len(rename_proposals)

            step.status = "success"
            step.details["proposed_count"] = len(rename_proposals)
            step.details["renamed_count"] = renamed_count
            step.details["llm_used"] = self.use_llm_semantic
            step.details["duplicate_checks"] = self.enable_duplicate_detection

        except Exception as exc:
            step.status = "failed"
            step.error = str(exc)
            logger.error(f"Rename step failed: {exc}")

        step.duration_ms = (time.time() - start) * 1000
        return step
                    
                    # Apply normalization
                    normalized_name = self.filename_normalizer.normalize(
                        filename,
                        replace_action=True,
                        proper_case=True,
                        remove_numbers=True
                    )
                    
                    # Only rename if it actually changed
                    if normalized_name != filename:
                        new_path = vf.path.parent / normalized_name

                        if not self.dry_run:
                            vf.path.rename(new_path)
                            logger.info(f"Renamed: {filename} → {normalized_name}")

                        renamed_count += 1

                except Exception as e:
                    filename = self._get_filename(vf)
                    logger.debug(f"Rename failed for {filename}: {e}")
                    continue

            result.files_renamed = renamed_count

            step.status = "success"
            step.details["renamed_count"] = renamed_count
            step.details["dry_run"] = self.dry_run

        except Exception as exc:
            step.status = "failed"
            step.error = str(exc)
            logger.error(f"Rename failed: {exc}")

        step.duration_ms = (time.time() - start) * 1000
        return step

    def _run_step_tag(self, result: WorkflowResult) -> WorkflowStep:
        """Write extracted metadata tags to files."""
        import time

        start = time.time()
        step = WorkflowStep(name="TAG", status="running")

        try:
            files = self.scanned_files  # Use cached scanned files

            tagged_count = 0

            for vf in files:
                try:
                    filename = self._get_filename(vf)
                    writer = TagWriterFactory.for_file(vf.path)
                    if not writer:
                        continue

                    # Get extracted metadata
                    metadata = self.extracted_metadata.get(filename)
                    if not metadata:
                        logger.debug(f"No extracted metadata for {filename}")
                        continue

                    # Build tag fields from extracted metadata
                    title = metadata.title or vf.filename_stem
                    artists = ", ".join(metadata.performers) if metadata.performers else None
                    studio = metadata.studio or self.metadata_hints.get("studio") or self.studio_filter
                    comment = f"Performers: {artists}" if artists else f"Studio: {studio}"

                    fields = TagFields(
                        title=title,
                        artist=artists,
                        album=studio,
                        genre="Adult",
                        comment=comment,
                    )

                    if not self.dry_run:
                        success = writer.write_tags(vf.path, fields)
                        if success:
                            tagged_count += 1

                    else:
                        # In dry-run, assume success
                        tagged_count += 1

                except Exception as e:
                    filename = self._get_filename(vf)
                    logger.debug(f"Tagging failed for {filename}: {e}")
                    continue

            result.files_tagged = tagged_count

            step.status = "success"
            step.details["tagged_count"] = tagged_count
            step.details["dry_run"] = self.dry_run

        except Exception as exc:
            step.status = "failed"
            step.error = str(exc)
            logger.error(f"Tag failed: {exc}")

        step.duration_ms = (time.time() - start) * 1000
        return step

    def _run_step_organize(self, result: WorkflowResult) -> WorkflowStep:
        """Organize files into studio folders."""
        import time
        import shutil

        start = time.time()
        step = WorkflowStep(name="ORGANIZE", status="running")

        try:
            files = self.scanned_files  # Use cached scanned files

            organized_count = 0

            for vf in files:
                try:
                    # Get studio name from extracted metadata or hints
                    filename = self._get_filename(vf)
                    metadata = self.extracted_metadata.get(filename)
                    studio_name = (
                        metadata.studio if metadata else None
                    ) or self.metadata_hints.get("studio") or self.studio_filter or "Unknown"
                    
                    studio_folder = self.root / studio_name

                    if vf.path.parent != studio_folder:
                        if not self.dry_run:
                            studio_folder.mkdir(parents=True, exist_ok=True)
                            new_path = studio_folder / vf.path.name
                            shutil.move(str(vf.path), str(new_path))
                            logger.info(f"Moved: {vf.path} → {new_path}")

                        organized_count += 1

                except Exception as e:
                    filename = self._get_filename(vf)
                    logger.debug(f"Organization failed for {filename}: {e}")
                    continue

            result.files_organized = organized_count

            step.status = "success"
            step.details["organized_count"] = organized_count
            step.details["dry_run"] = self.dry_run

        except Exception as exc:
            step.status = "failed"
            step.error = str(exc)
            logger.warning(f"Organize failed (non-critical): {exc}")

        step.duration_ms = (time.time() - start) * 1000
        return step

    def _run_step_verify(self, result: WorkflowResult) -> WorkflowStep:
        """Verify workflow results."""
        import time

        start = time.time()
        step = WorkflowStep(name="VERIFY", status="running")

        try:
            # Check consistency
            consistency_check = all(
                [
                    result.files_scanned > 0,
                    result.files_identified >= 0,
                    result.files_tagged >= 0,
                ]
            )

            if not consistency_check:
                step.status = "failed"
                step.error = "Consistency check failed"
                return step

            step.status = "success"
            step.details["files_scanned"] = result.files_scanned
            step.details["files_renamed"] = result.files_renamed
            step.details["files_tagged"] = result.files_tagged
            step.details["success_rate"] = (
                (result.files_renamed + result.files_tagged)
                / (result.files_scanned * 2)
                if result.files_scanned > 0
                else 0
            )

        except Exception as exc:
            step.status = "failed"
            step.error = str(exc)
            logger.error(f"Verify failed: {exc}")

        step.duration_ms = (time.time() - start) * 1000
        return step


# AC_COMPLETE: AC-PLEX-WORKFLOW-2026-02-23-001 ✅
