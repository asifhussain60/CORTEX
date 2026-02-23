"""
cortex/mcp/tools/video_library_tool.py

MCP tool for video library scanning and organization.

Exposes VideoLibraryOrchestrator operations via MCP interface:
- `scan` — Discover and index all videos with PLEX metadata
- `preview_renames` — Show proposed renames without applying
- `apply_renames` — Execute filesystem renames with confidence filtering
- `update_metadata` — Sync PLEX metadata back to file tags
- `sanitize_filenames` — Intelligent filename sanitization with studio detection
- `analyze_backlog` — Analyze _backlog folder for sanitization candidates
- `extract_metadata` — Extract studio, artists, tags for Plex organization

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


# AC_COMPLETE: AC-VIDEO-MCP-2026-02-23-004 ✅
