"""
Bulk Digest MCP Tool - AC-BULK-DIGEST-001

MCP tool for bulk markdown file ingestion.

Exposes BulkDigestOrchestrator functionality via MCP interface.
"""

import logging
from typing import Any, Dict, List, Optional

from cortex.orchestrators.support.bulk_digest_orchestrator import BulkDigestOrchestrator

logger = logging.getLogger(__name__)


def cortex_bulk_digest_files(
    directory: str = ".",
    pattern: str = "*.md",
    exclude_patterns: Optional[List[str]] = None,
    min_confidence: float = 5.0,
    auto_delete: bool = True,
    dry_run: bool = False,
    parallel: bool = False,
    max_workers: int = 4,
    continue_on_error: bool = True
) -> Dict[str, Any]:
    """Bulk ingest markdown files with intelligent routing and cleanup.

    Scans directory for markdown files, ingests via DigestSessionOrchestrator,
    and optionally deletes files after successful ingestion.

    Args:
        directory: Directory to scan (default: current directory)
        pattern: Glob pattern for file matching (default: *.md)
        exclude_patterns: Additional patterns to exclude (docs/, README.md auto-excluded)
        min_confidence: Minimum confidence score (0-10) to process file
        auto_delete: Delete files after successful ingestion
        dry_run: Simulate without deleting files (reports what would happen)
        parallel: Enable parallel processing for faster execution
        max_workers: Maximum parallel workers (default: 4)
        continue_on_error: Continue processing remaining files on error

    Returns:
        Dictionary with bulk digest results:
        - success: bool
        - files_found: int (total files matching pattern)
        - files_processed: int (successfully processed)
        - files_skipped: int (low confidence or excluded)
        - files_excluded: int (matched exclusion patterns)
        - files_deleted: int (deleted after ingestion)
        - files_failed: int (processing errors)
        - total_enhancements: int (total enhancements extracted)
        - processing_time_seconds: float
        - files_by_category: Dict[str, int]
        - dry_run: bool
        - parallel: bool
        - errors: List[str] (up to 10 error messages)

    Example:
        >>> # Ingest all root-level markdown files
        >>> result = cortex_bulk_digest_files(
        ...     directory=".",
        ...     pattern="*.md",
        ...     auto_delete=True,
        ...     dry_run=False
        ... )
        >>> print(f"Processed: {result['files_processed']}")
        >>> print(f"Deleted: {result['files_deleted']}")
        >>> print(f"Enhancements: {result['total_enhancements']}")

        >>> # Dry run to see what would happen
        >>> result = cortex_bulk_digest_files(
        ...     directory=".",
        ...     pattern="PHASE-*.md",
        ...     dry_run=True
        ... )
        >>> print(f"Would process {result['files_processed']} files")

        >>> # Parallel processing for large batches
        >>> result = cortex_bulk_digest_files(
        ...     directory=".",
        ...     pattern="*.md",
        ...     parallel=True,
        ...     max_workers=8
        ... )
    """
    try:
        orchestrator = BulkDigestOrchestrator()

        result = orchestrator.process_directory(
            directory=directory,
            pattern=pattern,
            exclude_patterns=exclude_patterns,
            min_confidence=min_confidence,
            auto_delete=auto_delete,
            dry_run=dry_run,
            parallel=parallel,
            max_workers=max_workers,
            continue_on_error=continue_on_error
        )

        return result

    except Exception as e:
        logger.error(f"Bulk digest MCP tool error: {e}")
        return {
            "success": False,
            "error_message": f"MCP tool error: {str(e)}",
            "files_found": 0,
            "files_processed": 0,
            "files_skipped": 0,
            "files_excluded": 0,
            "files_deleted": 0,
            "files_failed": 0,
            "total_enhancements": 0,
            "processing_time_seconds": 0.0,
            "files_by_category": {},
            "dry_run": dry_run,
            "parallel": parallel,
            "errors": [str(e)]
        }


# MCP Tool Metadata for Registry
__mcp_tool__ = {
    "name": "cortex_bulk_digest_files",
    "description": "Bulk ingest markdown files with intelligent routing and cleanup",
    "parameters": {
        "directory": {
            "type": "string",
            "required": False,
            "default": ".",
            "description": "Directory to scan"
        },
        "pattern": {
            "type": "string",
            "required": False,
            "default": "*.md",
            "description": "Glob pattern for file matching"
        },
        "exclude_patterns": {
            "type": "array",
            "items": {"type": "string"},
            "required": False,
            "description": "Additional exclusion patterns"
        },
        "min_confidence": {
            "type": "number",
            "required": False,
            "default": 5.0,
            "description": "Minimum confidence score (0-10)"
        },
        "auto_delete": {
            "type": "boolean",
            "required": False,
            "default": True,
            "description": "Delete files after successful ingestion"
        },
        "dry_run": {
            "type": "boolean",
            "required": False,
            "default": False,
            "description": "Simulate without deleting files"
        },
        "parallel": {
            "type": "boolean",
            "required": False,
            "default": False,
            "description": "Enable parallel processing"
        },
        "max_workers": {
            "type": "integer",
            "required": False,
            "default": 4,
            "description": "Maximum parallel workers"
        },
        "continue_on_error": {
            "type": "boolean",
            "required": False,
            "default": True,
            "description": "Continue processing on errors"
        }
    },
    "returns": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "files_found": {"type": "integer"},
            "files_processed": {"type": "integer"},
            "files_skipped": {"type": "integer"},
            "files_excluded": {"type": "integer"},
            "files_deleted": {"type": "integer"},
            "files_failed": {"type": "integer"},
            "total_enhancements": {"type": "integer"},
            "processing_time_seconds": {"type": "number"},
            "files_by_category": {"type": "object"},
            "dry_run": {"type": "boolean"},
            "parallel": {"type": "boolean"},
            "errors": {"type": "array", "items": {"type": "string"}}
        }
    },
    "category": "digest",
    "tags": ["ingestion", "markdown", "cleanup", "bulk"]
}
