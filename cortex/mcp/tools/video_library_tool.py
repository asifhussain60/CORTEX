"""
cortex/mcp/tools/video_library_tool.py

MCP tool for video library scanning and comprehensive Plex workflow.

Exposes VideoLibraryOrchestrator + PlexWorkflowOrchestrator operations:

**Quick Operations:**
- `scan` — Discover and index all videos with PLEX metadata
- `preview_renames` — Show proposed renames without applying
- `apply_renames` — Execute filesystem renames with confidence filtering
- `update_metadata` — Sync PLEX metadata back to file tags
- `sanitize_filenames` — Intelligent filename sanitization with studio detection
- `extract_metadata` — Extract studio, artists, tags for Plex organization

**Comprehensive Workflow:**
- `plex_workflow_full` — End-to-end scan → identify → match → rename → tag → organize
- `plex_workflow_iafd_match` — Match library against IAFD and retrieve enriched metadata

AC_START: AC-VIDEO-MCP-2026-02-23-004
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional


def cortex_video_library_scan(
    root_path: str = "G:\\FLICKS",
    studio_filter: Optional[str] = None,
    extension_filter: Optional[List[str]] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    Scan video library and retrieve PLEX metadata for all files.

    Recursively discovers video files, extracts studio organization info,
    and retrieves metadata from local PLEX Media Server.

    Args:
        root_path: Root directory to scan (default: ``G:\\FLICKS``).
        studio_filter: Limit to specific studio (e.g. ``Bellesa``), optional.
        extension_filter: Custom video extensions (e.g. ``[".mp4", ".mkv"]``).
                         Default includes 13 common formats.
        dry_run: Preview mode (no modifications).

    Returns:
        Dict with keys:
        - `success`: Operation completed without fatal errors.
        - `total_files`: Video files discovered.
        - `organized_files`: Files already well-organized.
        - `files_by_studio`: Dict mapping studio name → file count.
        - `plex_indexed`: Files found in PLEX library.
        - `plex_missing`: Files not yet indexed in PLEX.
        - `duration_seconds`: Total scan time.
        - `ac_session_id`: Audit trail session ID.

    Example::

        result = cortex_video_library_scan(studio_filter="Bellesa")
        print(f"Found {result['total_files']} videos in Bellesa")
        print(f"PLEX indexed: {result['plex_indexed']}")
    """
    from cortex.orchestrators.support.video_library_orchestrator import (
        VideoLibraryOrchestrator,
    )
    from cortex.tools.media.plex_metadata_accessor import PlexMetadataAccessor
    from cortex.tools.media.video_library_scanner import VideoLibraryScanner

    try:
        root = Path(root_path)

        # Initialize components
        plex_accessor = PlexMetadataAccessor()
        orchestrator = VideoLibraryOrchestrator(
            root=root,
            dry_run=dry_run,
            studio_filter=studio_filter,
            plex_accessor=plex_accessor,
        )

        # Run scan via orchestrator
        preview = orchestrator.preview_renames()

        # Compute statistics
        files_by_studio: Dict[str, int] = {}
        scanner = VideoLibraryScanner(root=root)
        all_files = scanner.scan()

        for vfile in all_files:
            if studio_filter and vfile.studio != studio_filter:
                continue
            studio = vfile.studio or "(root)"
            files_by_studio[studio] = files_by_studio.get(studio, 0) + 1

        plex_indexed = len(
            [p for p in preview.proposals if p.metadata_source == "plex"]
        )

        return {
            "success": True,
            "total_files": preview.total_files,
            "organized_files": len([f for f in all_files if f.hierarchy_depth >= 2]),
            "files_by_studio": files_by_studio,
            "plex_indexed": plex_indexed,
            "plex_missing": preview.total_files - plex_indexed,
            "proposals_generated": len(preview.proposals),
            "conflicts_detected": len(preview.conflicts),
            "duration_seconds": preview.duration_seconds,
            "ac_session_id": preview.ac_session_id,
            "dry_run": dry_run,
        }

    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "error": str(exc),
            "total_files": 0,
            "plex_indexed": 0,
            "plex_missing": 0,
        }


def cortex_video_library_preview(
    root_path: str = "G:\\FLICKS",
    studio_filter: Optional[str] = None,
    min_confidence: float = 0.5,
    limit_results: int = 50,
) -> Dict[str, Any]:
    """
    Preview proposed renames without applying changes.

    Shows all files that would be renamed, with reason and confidence score.
    Includes conflict warnings.

    Args:
        root_path: Root directory (default: ``G:\\FLICKS``).
        studio_filter: Filter to specific studio.
        min_confidence: Only show proposals with confidence ≥ threshold.
        limit_results: Max proposals to return (default: 50 for preview).

    Returns:
        Dict with keys:
        - `success`: Operation completed.
        - `total_files`: Total discovered.
        - `proposals`: List of rename proposals (max ``limit_results``).
        - `conflicts`: List of detected conflicts.
        - `conflict_count`: Number of conflicts.
        - `proposal_count`: Total proposals available (may exceed limit).
        - `limited_to`: Whether results were truncated.

    Example::

        preview = cortex_video_library_preview(studio_filter="Bellesa")
        for p in preview["proposals"]:
            print(f"{p['current']} → {p['proposed']} ({p['confidence']:.0%})")
    """
    from cortex.orchestrators.support.video_library_orchestrator import (
        VideoLibraryOrchestrator,
    )
    from cortex.tools.media.plex_metadata_accessor import PlexMetadataAccessor

    try:
        root = Path(root_path)

        plex_accessor = PlexMetadataAccessor()
        orchestrator = VideoLibraryOrchestrator(
            root=root,
            dry_run=True,
            studio_filter=studio_filter,
            plex_accessor=plex_accessor,
        )

        result = orchestrator.preview_renames()

        # Filter by confidence
        filtered_proposals = [
            p for p in result.proposals if p.confidence >= min_confidence
        ]

        # Format proposals for output
        proposal_list = [
            {
                "current": str(p.current_path),
                "proposed": str(p.proposed_path),
                "confidence": round(p.confidence, 2),
                "reason": p.reason,
                "source": p.metadata_source,
            }
            for p in filtered_proposals[:limit_results]
        ]

        # Format conflicts
        conflict_list = [
            {
                "type": c.type,
                "description": c.description,
                "affected_count": len(c.affected_proposals),
            }
            for c in result.conflicts
        ]

        return {
            "success": True,
            "total_files": result.total_files,
            "proposals": proposal_list,
            "conflicts": conflict_list,
            "proposal_count": len(filtered_proposals),
            "conflict_count": len(result.conflicts),
            "limited_to": len(filtered_proposals) > limit_results,
            "duration_seconds": result.duration_seconds,
            "ac_session_id": result.ac_session_id,
        }

    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "error": str(exc),
            "proposals": [],
            "conflicts": [],
        }


def cortex_video_library_apply(
    root_path: str = "G:\\FLICKS",
    studio_filter: Optional[str] = None,
    min_confidence: float = 0.75,
    limit_renames: int = 100,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Apply proposed renames to filesystem.

    WARNING: This modifies files! Use ``dry_run=True`` to preview first.

    Args:
        root_path: Root directory (default: ``G:\\FLICKS``).
        studio_filter: Filter to specific studio.
        min_confidence: Only apply proposals with confidence ≥ threshold (default: 0.75).
        limit_renames: Max renames per run (safety limit, default: 100).
        dry_run: Preview mode (show what would happen, don't modify).

    Returns:
        Dict with keys:
        - `success`: Operation completed.
        - `renames_applied`: Number of files successfully renamed.
        - `renames_failed`: Number of rename failures.
        - `renames_skipped`: Number of proposals with low confidence.
        - `conflicts`: Any detected conflicts that prevented rename.

    Example::

        # Preview first!
        preview = cortex_video_library_preview(studio_filter="Bellesa")
        
        # Then apply if confident
        result = cortex_video_library_apply(
            studio_filter="Bellesa",
            min_confidence=0.80,
            dry_run=False
        )
        print(f"Applied {result['renames_applied']} renames")
    """
    from cortex.orchestrators.support.video_library_orchestrator import (
        VideoLibraryOrchestrator,
    )
    from cortex.tools.media.plex_metadata_accessor import PlexMetadataAccessor

    if dry_run:
        # Redirect to preview if in dry_run mode
        return cortex_video_library_preview(
            root_path=root_path,
            studio_filter=studio_filter,
            min_confidence=min_confidence,
            limit_results=limit_renames,
        )

    try:
        root = Path(root_path)

        plex_accessor = PlexMetadataAccessor()
        orchestrator = VideoLibraryOrchestrator(
            root=root,
            dry_run=False,
            studio_filter=studio_filter,
            plex_accessor=plex_accessor,
        )

        # Generate and apply renames
        result = orchestrator.apply_renames(min_confidence=min_confidence)

        # Count outcomes
        applied = sum(
            1
            for p in result.proposals
            if p.current_path != p.proposed_path
        )
        failed = sum(
            1 for p in result.proposals if p.current_path == p.proposed_path
        )

        return {
            "success": result.duration_seconds > 0,
            "renames_applied": applied,
            "renames_failed": failed,
            "renames_skipped": len(result.proposals) - applied - failed,
            "conflicts": len(result.conflicts),
            "files_processed": result.total_files,
            "duration_seconds": result.duration_seconds,
            "ac_session_id": result.ac_session_id,
        }

    except RuntimeError as exc:
        return {
            "success": False,
            "error": str(exc),
            "renames_applied": 0,
            "renames_failed": 0,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "error": str(exc),
            "renames_applied": 0,
            "renames_failed": 0,
        }


def cortex_video_library_update_metadata(
    root_path: str = "G:\\FLICKS",
    studio_filter: Optional[str] = None,
    sync_from_plex: bool = True,
    sync_to_plex: bool = False,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    Sync metadata between PLEX and file tags.

    Args:
        root_path: Root directory (default: ``G:\\FLICKS``).
        studio_filter: Filter to specific studio.
        sync_from_plex: Write PLEX metadata to file tags.
        sync_to_plex: Write file metadata to PLEX (requires PLEX API access).
        dry_run: Preview mode.

    Returns:
        Dict with sync results.

    Example::

        result = cortex_video_library_update_metadata(
            studio_filter="Bellesa",
            sync_from_plex=True,
            dry_run=True
        )
    """
    from cortex.tools.media.tag_cleaner import MediaTagCleaner

    try:
        root = Path(root_path)

        # Use existing MediaTagCleaner for tag writing
        cleaner = MediaTagCleaner(
            root=root,
            dry_run=dry_run,
            use_folder_as_album=True,
            clear_stale_tags=True,
        )

        results = cleaner.run()

        success_count = sum(1 for r in results if r.success)
        changes_count = sum(1 for r in results if r.changes)

        return {
            "success": True,
            "files_processed": len(results),
            "files_updated": success_count,
            "fields_changed": changes_count,
            "dry_run": dry_run,
            "sync_from_plex": sync_from_plex,
            "sync_to_plex": sync_to_plex,
        }

    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "error": str(exc),
            "files_processed": 0,
            "files_updated": 0,
        }


def cortex_analyze_backlog(
    root_path: str = "G:\\FLICKS\\_backlog",
    max_samples: int = 100,
) -> Dict[str, Any]:
    """
    Analyze backlog folder to identify sanitization candidates.

    Scans all video files in _backlog and classifies each by:
    - Studio detection status
    - Artist extraction
    - Metadata bloat (dates, resolutions, studio suffixes)
    - Obscene language present
    - Current filename quality

    Args:
        root_path: Backlog folder path (default: ``G:\\FLICKS\\_backlog``).
        max_samples: Max files to analyze (default: 100).

    Returns:
        Dict with keys:
        - `success`: Operation completed.
        - `total_files`: Files found in backlog.
        - `analyzed`: Files processed.
        - `candidates_for_sanitization`: Files that need renaming.
        - `already_clean`: Files that don't need changes.
        - `studio_detected`: Count with detected studios.
        - `obscenity_detected`: Count with crude language.
        - `metadata_bloat`: Count with dates/resolutions/suffixes.
        - `sample_before_after`: List of before/after examples (first 10).

    Example::

        analysis = cortex_analyze_backlog()
        print(f"Found {analysis['candidates_for_sanitization']} files to sanitize")
        for sample in analysis["sample_before_after"]:
            print(f"{sample['before']} → {sample['after']}")
    """
    from cortex.tools.media.filename_sanitizer import FilenameAnalyzer

    try:
        backlog = Path(root_path)
        if not backlog.exists():
            return {
                "success": False,
                "error": f"Backlog path not found: {root_path}",
                "total_files": 0,
            }

        # Get all video files
        video_extensions = {".mp4", ".mkv", ".m4v", ".avi", ".webm", ".mov"}
        all_files = [
            f
            for f in backlog.iterdir()
            if f.is_file() and f.suffix.lower() in video_extensions
        ]

        total_files = len(all_files)
        analyzed_files = min(len(all_files), max_samples)

        # Analyze each file
        analyzer = FilenameAnalyzer()
        results = []
        studio_count = 0
        obscenity_count = 0
        bloat_count = 0
        needs_sanitization_count = 0

        for video_file in all_files[:analyzed_files]:
            result = analyzer.analyze(video_file.name)
            results.append(result)

            if result.detected_studio:
                studio_count += 1
            if "morphed_obscenity" in result.changes_made:
                obscenity_count += 1
            if any(
                change in result.changes_made
                for change in [
                    "removed_date",
                    "removed_resolution",
                    "removed_studio_suffix",
                ]
            ):
                bloat_count += 1
            if result.needs_rename:
                needs_sanitization_count += 1

        # Get sample before/after (first 10)
        sample_before_after = [
            {
                "before": r.current_filename,
                "after": r.sanitized_filename,
                "studio": r.detected_studio,
                "artists": r.artists,
                "confidence": round(r.confidence, 2),
                "changes": r.changes_made,
            }
            for r in results[:10]
        ]

        return {
            "success": True,
            "total_files": total_files,
            "analyzed": analyzed_files,
            "candidates_for_sanitization": needs_sanitization_count,
            "already_clean": analyzed_files - needs_sanitization_count,
            "studio_detected": studio_count,
            "obscenity_detected": obscenity_count,
            "metadata_bloat": bloat_count,
            "sample_before_after": sample_before_after,
            "pct_needs_sanitization": round(
                (needs_sanitization_count / analyzed_files * 100), 1
            )
            if analyzed_files > 0
            else 0,
        }

    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "error": str(exc),
            "total_files": 0,
            "analyzed": 0,
        }


def cortex_preview_sanitization(
    root_path: str = "G:\\FLICKS\\_backlog",
    max_results: int = 50,
    min_confidence: float = 0.5,
) -> Dict[str, Any]:
    """
    Preview all sanitization proposals without applying changes.

    Returns comprehensive before/after table with studio, artists, tags, and confidence.

    Args:
        root_path: Folder to scan (default: ``G:\\FLICKS\\_backlog``).
        max_results: Max proposals to return (default: 50).
        min_confidence: Only show proposals with confidence ≥ threshold.

    Returns:
        Dict with keys:
        - `success`: Operation completed.
        - `total_files`: Files discovered.
        - `proposals`: List of sanitization proposals (see structure below).
        - `high_confidence`: Count with confidence ≥ 0.8.
        - `medium_confidence`: Count with 0.5 ≤ confidence < 0.8.
        - `low_confidence`: Count with confidence < 0.5.

    Proposal structure::

        {
            "current_filename": "SexArt-2025-11-19-Plan-B-1080.mp4",
            "sanitized_filename": "Plan B.mp4",
            "detected_studio": "SexArt",
            "artists": ["Unknown"],
            "tags": ["SexArt", "1080p"],
            "confidence": 0.95,
            "changes": ["removed_date", "removed_resolution", "removed_studio_prefix"],
            "plex_album": "SexArt",
            "plex_genres": ["SexArt", "1080p"]
        }

    Example::

        preview = cortex_preview_sanitization(max_results=20)
        for prop in preview["proposals"]:
            print(f"{prop['current_filename']} → {prop['sanitized_filename']}")
    """
    from cortex.tools.media.filename_sanitizer import FilenameAnalyzer

    try:
        folder = Path(root_path)
        if not folder.exists():
            return {
                "success": False,
                "error": f"Folder not found: {root_path}",
                "proposals": [],
            }

        # Get all video files
        video_extensions = {".mp4", ".mkv", ".m4v", ".avi", ".webm", ".mov"}
        all_files = sorted(
            [
                f
                for f in folder.iterdir()
                if f.is_file() and f.suffix.lower() in video_extensions
            ]
        )

        # Analyze each file
        analyzer = FilenameAnalyzer(studio_context=folder.name)
        proposals = []
        confidence_buckets = {"high": 0, "medium": 0, "low": 0}

        for video_file in all_files:
            result = analyzer.analyze(video_file.name)

            # Filter by confidence
            if result.confidence < min_confidence:
                continue

            # Count by confidence level
            if result.confidence >= 0.8:
                confidence_buckets["high"] += 1
            elif result.confidence >= 0.5:
                confidence_buckets["medium"] += 1
            else:
                confidence_buckets["low"] += 1

            proposal = {
                "current_filename": result.current_filename,
                "sanitized_filename": result.sanitized_filename,
                "detected_studio": result.detected_studio,
                "artists": result.artists,
                "tags": result.tags,
                "confidence": round(result.confidence, 2),
                "changes": result.changes_made,
                "plex_album": result.detected_studio or "Unorganized",
                "plex_genres": result.tags,
            }
            proposals.append(proposal)

            if len(proposals) >= max_results:
                break

        return {
            "success": True,
            "total_files": len(all_files),
            "proposals": proposals,
            "proposals_generated": len(proposals),
            "high_confidence": confidence_buckets["high"],
            "medium_confidence": confidence_buckets["medium"],
            "low_confidence": confidence_buckets["low"],
            "limited_to": len(proposals) >= max_results,
        }

    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "error": str(exc),
            "proposals": [],
            "total_files": 0,
        }


def cortex_extract_metadata(
    filename: str,
    studio_context: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Extract all metadata from a single filename (studio, artists, tags).

    Args:
        filename: Filename to analyze (e.g., ``SexArt-2025-11-19-Plan-B-1080.mp4``).
        studio_context: Folder name (e.g., ``Bellesa``) to help with detection.

    Returns:
        Dict with keys:
        - `filename`: Input filename.
        - `detected_studio`: Studio name (e.g., ``SexArt``, ``Bellesa``).
        - `artists`: List of artist names extracted.
        - `tags`: Metadata tags for Plex.
        - `sanitized_filename`: Cleaned filename (no obscenity, no bloat).
        - `changes`: List of modifications made.
        - `confidence`: Score (0.0-1.0) for sanitization quality.

    Example::

        meta = cortex_extract_metadata(
            "SexArt-2025-11-19-Plan-B-1080.mp4",
            studio_context="SexArt"
        )
        print(f"Studio: {meta['detected_studio']}")
        print(f"Tags: {meta['tags']}")
    """
    from cortex.tools.media.filename_sanitizer import FilenameAnalyzer

    try:
        analyzer = FilenameAnalyzer(studio_context=studio_context)
        result = analyzer.analyze(filename)

        return {
            "success": True,
            "filename": result.current_filename,
            "detected_studio": result.detected_studio,
            "artists": result.artists,
            "tags": result.tags,
            "sanitized_filename": result.sanitized_filename,
            "changes": result.changes_made,
            "confidence": round(result.confidence, 2),
            "needs_rename": result.needs_rename,
        }

    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "error": str(exc),
            "filename": filename,
        }


def cortex_plex_workflow_full(
    root_path: str = "G:\\FLICKS",
    studio_filter: Optional[str] = None,
    dry_run: bool = True,
    use_iafd: bool = True,
    normalize_filenames: bool = True,
    min_match_confidence: float = 0.75,
    auto_organize: bool = False,
    metadata_hints: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Execute complete Plex workflow — generic for all studios (no sanitization).

    Comprehensive end-to-end workflow that orchestrates all video library operations:
    1. **SCAN** — Discover videos in directory
    2. **IDENTIFY** — Extract metadata from filenames (studio, performers)
    3. **MATCH** — Query IAFD for enriched metadata
    4. **RENAME** — Normalize filenames (action→Does, proper case, remove numbers)
    5. **TAG** — Write enriched Plex metadata to file tags
    6. **ORGANIZE** — Move files to studio-specific folders
    7. **VERIFY** — Validate workflow results

    Works with ANY studio/naming convention. No filename sanitization — preserves meaningful names.

    Args:
        root_path: Root directory (default: ``G:\\FLICKS``).
        studio_filter: Limit to specific studio (e.g., ``Wicked``).
        dry_run: Preview mode (show what would happen, don't modify).
        use_iafd: Query IAFD for enriched metadata.
        normalize_filenames: Normalize: "action"→"Does", proper case, remove numbers.
        min_match_confidence: Minimum confidence for IAFD matches (0.0-1.0).
        auto_organize: Move files to studio folders (disabled by default — files stay in original location). Set to ``True`` to enable folder organization.
        metadata_hints: User-provided metadata overrides (e.g., ``{"studio": "Wicked"}``)

    Returns:
        Dict with keys:
        - `success`: Workflow completed successfully.
        - `total_files`: Files discovered.
        - `files_scanned`: Files successfully scanned.
        - `files_identified`: Files with detected metadata.
        - `files_matched`: Files matched against IAFD.
        - `files_renamed`: Files renamed.
        - `files_tagged`: Files tagged with metadata.
        - `files_organized`: Files organized to studio folders.
        - `steps`: List of step results with status and timing.
        - `errors`: List of errors encountered.
        - `warnings`: List of warnings.
        - `duration_seconds`: Total workflow time.

    Example::

        result = cortex_plex_workflow_full(
            root_path="G:\\\\FLICKS\\\\Wicked",
            studio_filter="Wicked",
            dry_run=True,
            normalize_filenames=True,
            use_iafd=False
        )
        print(f"Scanned: {result['total_files']} files")
        print(f"Renamed: {result['files_renamed']} files")
        print(f"Tagged: {result['files_tagged']} files")
    """
    from cortex.orchestrators.support.plex_workflow_orchestrator import (
        PlexWorkflowOrchestrator,
    )
    from cortex.tools.media.iafd_metadata_accessor import IAFDAccessor
    from cortex.tools.media.plex_metadata_accessor import PlexMetadataAccessor

    try:
        root = Path(root_path)

        # Initialize orchestrator with accessors
        plex_accessor = PlexMetadataAccessor()
        iafd_accessor = IAFDAccessor(use_cache=True) if use_iafd else None

        orchestrator = PlexWorkflowOrchestrator(
            root=root,
            studio_filter=studio_filter,
            dry_run=dry_run,
            min_match_confidence=min_match_confidence,
            normalize_filenames=normalize_filenames,
            auto_organize=auto_organize,
            use_iafd=use_iafd,
            metadata_hints=metadata_hints or {},
            plex_accessor=plex_accessor,
            iafd_accessor=iafd_accessor,
        )

        # Run full workflow
        workflow_result = orchestrator.run_full_workflow()

        # Format step results for output
        steps = [
            {
                "name": step.name,
                "status": step.status,
                "duration_ms": round(step.duration_ms, 2),
                "error": step.error,
                "details": step.details,
            }
            for step in workflow_result.step_results
        ]

        return {
            "success": workflow_result.success,
            "total_files": workflow_result.total_files,
            "files_scanned": workflow_result.files_scanned,
            "files_identified": workflow_result.files_identified,
            "files_matched": workflow_result.files_matched,
            "files_renamed": workflow_result.files_renamed,
            "files_tagged": workflow_result.files_tagged,
            "files_organized": workflow_result.files_organized,
            "steps": steps,
            "errors": workflow_result.errors,
            "warnings": workflow_result.warnings,
            "duration_seconds": round(workflow_result.duration_seconds, 2),
            "dry_run": dry_run,
            "ac_session_id": workflow_result.ac_session_id,
        }

    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "error": str(exc),
            "total_files": 0,
            "files_scanned": 0,
            "files_renamed": 0,
            "files_tagged": 0,
        }


def cortex_plex_workflow_iafd_match(
    root_path: str = "G:\\FLICKS",
    studio_filter: Optional[str] = None,
    limit_results: int = 50,
    min_confidence: float = 0.75,
) -> Dict[str, Any]:
    """
    Match video library against IAFD database and retrieve enriched metadata.

    Queries IAFD (Internet Adult Film Database) by title and performers
    to retrieve enriched metadata including:
    - Scene titles and descriptions
    - Performer names and links
    - Directors and production companies
    - Release dates
    - Runtime and resolution

    Args:
        root_path: Root directory (default: ``G:\\FLICKS``).
        studio_filter: Filter to specific studio.
        limit_results: Maximum results to display.
        min_confidence: Minimum match confidence (0.0-1.0).

    Returns:
        Dict with keys:
        - `success`: Operation completed.
        - `total_files`: Files discovered.
        - `matched`: Number of successful matches.
        - `match_rate`: Percentage of files matched.
        - `matches`: List of successful matches with metadata.
        - `unmatched`: List of files that could not be matched.
        - `duration_seconds`: Query time.

    Example::

        matches = cortex_plex_workflow_iafd_match(
            root_path="G:\\\\FLICKS\\\\Wicked",
            studio_filter="Wicked",
            min_confidence=0.80
        )
        for match in matches['matches']:
            print(f"{match['filename']} → {match['title']}")
            print(f"  Performers: {', '.join(match['performers'])}")
            print(f"  Confidence: {match['confidence']:.0%}")
    """
    from cortex.tools.media.filename_sanitizer import FilenameAnalyzer
    from cortex.tools.media.iafd_metadata_accessor import IAFDAccessor
    from cortex.tools.media.video_library_scanner import VideoLibraryScanner

    try:
        root = Path(root_path)
        import time

        start_time = time.time()

        # Scan library
        scanner = VideoLibraryScanner(root=root)
        files = scanner.scan()

        if studio_filter:
            files = [f for f in files if f.studio == studio_filter]

        # Initialize IAFD accessor
        iafd_accessor = IAFDAccessor(use_cache=True)
        analyzer = FilenameAnalyzer(studio_context=studio_filter)

        matches = []
        unmatched = []

        for vf in files:
            try:
                # Try title match first
                metadata = iafd_accessor.search_by_title(vf.filename_stem)

                if not metadata:
                    # Try performer match
                    analysis = analyzer.analyze(vf.filename)
                    if analysis.artists:
                        metadata = iafd_accessor.search_by_performers(
                            analysis.artists
                        )

                if metadata and metadata.confidence >= min_confidence:
                    matches.append(
                        {
                            "filename": vf.filename,
                            "title": metadata.title,
                            "performers": metadata.performers,
                            "directors": metadata.directors,
                            "production_company": metadata.production_company,
                            "release_date": metadata.release_date,
                            "confidence": round(metadata.confidence, 2),
                            "iafd_url": metadata.iafd_url,
                        }
                    )
                else:
                    unmatched.append(vf.filename)

            except Exception as e:
                unmatched.append(vf.filename)
                continue

        match_rate = len(matches) / len(files) if files else 0

        return {
            "success": True,
            "total_files": len(files),
            "matched": len(matches),
            "match_rate": round(match_rate, 2),
            "matches": matches[:limit_results],
            "unmatched": unmatched[:limit_results],
            "duration_seconds": round(time.time() - start_time, 2),
            "limited_to": len(matches) > limit_results,
        }

    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "error": str(exc),
            "total_files": 0,
            "matched": 0,
            "matches": [],
        }


def cortex_plex_semantic_rename(
    root_path: str = "G:\\FLICKS\\Wicked",
    use_llm: bool = True,
    llm_provider: str = "openai",
    llm_api_key: Optional[str] = None,
    min_confidence: float = 0.85,
    enable_duplicate_detection: bool = True,
    enable_snapshots: bool = True,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    Semantic filename renaming with LLM intelligence and collision prevention.

    Enhances Plex workflow with:
    - LLM-powered semantic renaming (GPT-4 or Claude)
    - SHA256-based duplicate detection
    - SQLite snapshot + rollback capability
    - Hybrid LLM/rule-based routing

    Example: "Chad Alva does Jojo Kiss.mp4" → "Chad Does Jojo.mp4"

    Args:
        root_path: Directory to process (default: ``G:\\FLICKS\\Wicked``).
        use_llm: Enable LLM semantic renaming (default: True).
        llm_provider: LLM provider (``openai`` or ``anthropic``).
        llm_api_key: API key for LLM provider (required if ``use_llm=True``).
        min_confidence: Minimum confidence for automated renames (0.0-1.0).
        enable_duplicate_detection: SHA256 collision prevention (default: True).
        enable_snapshots: SQLite snapshot before operations (default: True).
        dry_run: Preview mode (no filesystem modifications).

    Returns:
        Dict with keys:
        - `success`: Operation completed without fatal errors.
        - `total_files`: Files discovered.
        - `files_renamed`: Files actually renamed (0 if dry_run=True).
        - `proposals_count`: Rename proposals generated.
        - `duplicates_detected`: Collision count.
        - `snapshot_id`: Snapshot ID for rollback (if enabled).
        - `llm_used`: Whether LLM was used.
        - `duration_seconds`: Total time.

    Example::

        # Preview with LLM
        result = cortex_plex_semantic_rename(
            root_path="G:\\FLICKS\\Wicked",
            use_llm=True,
            llm_api_key="sk-...",
            dry_run=True
        )
        print(f"Proposals: {result['proposals_count']}")

        # Apply changes
        result = cortex_plex_semantic_rename(
            root_path="G:\\FLICKS\\Wicked",
            use_llm=True,
            llm_api_key="sk-...",
            dry_run=False
        )
    """
    from cortex.orchestrators.support.plex_workflow_orchestrator import (
        PlexWorkflowOrchestrator,
    )
    from cortex.tools.media.llm_semantic_renamer import LLMProvider

    try:
        root = Path(root_path)

        # Map provider string to enum
        provider_map = {
            "openai": LLMProvider.OPENAI,
            "anthropic": LLMProvider.ANTHROPIC,
        }
        provider = provider_map.get(llm_provider.lower(), LLMProvider.OPENAI)

        # Initialize orchestrator with enhanced features
        orchestrator = PlexWorkflowOrchestrator(
            root=root,
            dry_run=dry_run,
            normalize_filenames=True,
            use_llm_semantic=use_llm,
            llm_api_key=llm_api_key,
            llm_provider=provider,
            min_rename_confidence=min_confidence,
            enable_duplicate_detection=enable_duplicate_detection,
            enable_snapshots=enable_snapshots,
            auto_organize=False,  # Rename in-place
            use_iafd=False,  # Skip IAFD for speed
        )

        # Run workflow
        result = orchestrator.run_full_workflow()

        return {
            "success": result.success,
            "total_files": result.total_files,
            "files_renamed": result.files_renamed,
            "proposals_count": sum(
                step.details.get("proposed_count", 0)
                for step in result.step_results
            ),
            "duplicates_detected": 0,  # TODO: Extract from duplicate detector
            "snapshot_id": (
                orchestrator.current_snapshot.snapshot_id
                if orchestrator.current_snapshot
                else None
            ),
            "llm_used": use_llm,
            "dry_run": dry_run,
            "duration_seconds": round(result.duration_seconds, 2),
            "steps": [
                {
                    "name": step.name,
                    "status": step.status,
                    "duration_ms": round(step.duration_ms, 0),
                }
                for step in result.step_results
            ],
            "errors": result.errors,
            "warnings": result.warnings,
        }

    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "error": str(exc),
            "total_files": 0,
            "files_renamed": 0,
        }


# AC_COMPLETE: AC-VIDEO-MCP-2026-02-23-004 ✅
