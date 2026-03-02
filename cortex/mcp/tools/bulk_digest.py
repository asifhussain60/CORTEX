"""
cortex_bulk_digest_files — MCP tool for bulk markdown ingestion.

Ingests multiple markdown files via DigestSessionOrchestrator with intelligent
routing, filtering, and optional cleanup after successful processing.

AC: AC-BULK-DIGEST-001
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def cortex_bulk_digest_files(
    directory: str = ".",
    pattern: str = "*.md",
    exclude_patterns: Optional[List[str]] = None,
    auto_delete: bool = False,
    dry_run: bool = False,
    min_confidence: float = 0.0,
    parallel: bool = False,
    max_workers: int = 4,
    batch_size: int = 50,
) -> Dict[str, Any]:
    """
    Ingest markdown files from *directory* in bulk.

    Args:
        directory: Root directory to scan for files.
        pattern: Glob pattern for files (default: ``*.md``).
        exclude_patterns: Glob patterns for paths to skip (e.g. ``["docs/**"]``).
        auto_delete: Delete successfully ingested files.
        dry_run: Report what *would* happen without actually processing or deleting.
        min_confidence: Minimum confidence score to process a file (0–10 scale).
        parallel: Enable concurrent processing.
        max_workers: Max worker threads when *parallel* is True.
        batch_size: Files per batch for progress reporting.

    Returns:
        Dict with keys: success, files_found, files_processed, files_skipped,
        files_deleted, files_failed, files_excluded, total_enhancements,
        dry_run, parallel, processing_time_seconds.
    """
    from cortex.orchestrators.support.bulk_digest_orchestrator import BulkDigestOrchestrator

    # Always exclude README.md — it is a project-level file, not a session log
    default_excludes = ["README.md"]
    combined_excludes = default_excludes + list(exclude_patterns or [])

    orchestrator = BulkDigestOrchestrator()
    return orchestrator.process_directory(
        directory=directory,
        pattern=pattern,
        exclude_patterns=combined_excludes,
        auto_delete=auto_delete,
        dry_run=dry_run,
        min_confidence=min_confidence,
        parallel=parallel,
        max_workers=max_workers,
        batch_size=batch_size,
        continue_on_error=True,
    )
