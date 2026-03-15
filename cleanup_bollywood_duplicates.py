"""
Scan and cleanup duplicates in Z:\\MUSIC\\Bollywood using a persistent SQLite hash cache.

This script uses BollywoodPlexDuplicateOrchestrator and stores file hashes in:
.cortex-runtime/plex-dedupe/bollywood_plex_duplicates.db

The database is purpose-marked and enforced for this workflow only.

Usage:
    python cleanup_bollywood_duplicates.py --scan
    python cleanup_bollywood_duplicates.py --cleanup --dry-run
    python cleanup_bollywood_duplicates.py --cleanup

AC_START: AC-BOLLYWOOD-DUP-CLEANUP-CLI-2026-03-15-001
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys

from cortex.orchestrators.support.bollywood_plex_duplicate_orchestrator import (
    BollywoodPlexDuplicateOrchestrator,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def _to_mb(value_bytes: int) -> float:
    """Convert byte count to MB."""
    return round(value_bytes / (1024 * 1024), 2)


def main() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Bollywood Plex duplicate scan/cleanup with persistent hash cache"
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        default=True,
        help="Scan only (default)",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Delete duplicate files (keeps one preferred copy per hash)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview cleanup mode without deleting files",
    )
    parser.add_argument(
        "--force-rehash",
        action="store_true",
        help="Ignore cached hashes and recompute all file hashes",
    )
    parser.add_argument(
        "--root",
        type=str,
        default=r"Z:\MUSIC\Bollywood",
        help="Bollywood library root",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=r".cortex-runtime\plex-dedupe\bollywood_plex_duplicates.db",
        help="Dedicated SQLite DB path for duplicate index",
    )

    args = parser.parse_args()

    root_dir = Path(args.root)
    db_path = Path(args.db_path)

    if not root_dir.exists():
        logger.error(f"Root directory not found: {root_dir}")
        return 1

    cleanup_mode = bool(args.cleanup)
    dry_run = bool(args.dry_run) if cleanup_mode else True

    logger.info("=" * 80)
    logger.info("BOLLYWOOD PLEX DUPLICATE ORCHESTRATOR")
    logger.info("=" * 80)
    logger.info(f"Root: {root_dir}")
    logger.info(f"DB: {db_path}")
    logger.info(f"Cleanup mode: {cleanup_mode}")
    logger.info(f"Dry-run: {dry_run}")
    logger.info(f"Force rehash: {bool(args.force_rehash)}")
    logger.info("=" * 80)

    orchestrator = BollywoodPlexDuplicateOrchestrator(
        root_path=root_dir,
        db_path=db_path,
        cleanup=cleanup_mode,
        dry_run=dry_run,
        force_rehash=bool(args.force_rehash),
    )
    result = orchestrator.run_duplicate_sweep()

    logger.info("")
    logger.info("SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Run ID: {result.run_id}")
    logger.info(f"Files scanned: {result.total_files}")
    logger.info(f"Unique hashes: {result.unique_hashes}")
    logger.info(f"Cached hash hits: {result.cached_hash_hits}")
    logger.info(f"Rehashed files: {result.rehashed_files}")
    logger.info(f"Duplicate groups: {result.duplicate_groups}")
    logger.info(f"Duplicate files: {result.duplicate_files}")
    logger.info(f"Wasted space: {_to_mb(result.wasted_bytes)} MB")
    logger.info(f"Deleted files: {result.deleted_files}")
    logger.info(f"Freed space: {_to_mb(result.freed_bytes)} MB")
    logger.info(f"Duration: {round(result.duration_seconds, 2)} s")

    if result.errors:
        logger.info("Errors:")
        for err in result.errors:
            logger.info(f"  - {err}")

    logger.info("=" * 80)

    if cleanup_mode and not dry_run:
        logger.info("Cleanup complete")
    elif cleanup_mode and dry_run:
        logger.info("Cleanup preview complete (no files deleted)")
    else:
        logger.info("Scan complete")

    # AC_COMPLETE: AC-BOLLYWOOD-DUP-CLEANUP-CLI-2026-03-15-001 ✅
    return 0


if __name__ == "__main__":
    sys.exit(main())
