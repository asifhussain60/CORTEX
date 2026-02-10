#!/usr/bin/env python3
"""
Bulk Markdown Ingestion Script

Standalone script to ingest all *.md files from CORTEX root with visual progress feedback.

Usage:
    python scripts/utilities/bulk_ingest_root.py [--dry-run] [--no-delete]

Author: CORTEX Architect
Date: 2026-02-10
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cortex.mcp.tools.bulk_digest import cortex_bulk_digest_files


def main() -> None:
    """Main execution."""
    # Parse arguments
    dry_run = "--dry-run" in sys.argv
    auto_delete = "--no-delete" not in sys.argv
    
    print("\n" + "═" * 70)
    print("  CORTEX Bulk Markdown Ingestion")
    print("═" * 70)
    print(f"  Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    print(f"  Auto-delete: {'YES' if auto_delete else 'NO'}")
    print("═" * 70 + "\n")
    
    # Execute bulk digest
    result = cortex_bulk_digest_files(
        directory=".",
        pattern="*.md",
        min_confidence=5.0,
        auto_delete=auto_delete,
        dry_run=dry_run,
        parallel=False,  # Sequential for visual feedback
        continue_on_error=True
    )
    
    # Print summary
    if result["success"]:
        print("\n" + "═" * 70)
        print("  ✅ BULK INGESTION COMPLETE")
        print("═" * 70)
        print(f"  Files Found:      {result['files_found']}")
        print(f"  Files Processed:  {result['files_processed']}")
        print(f"  Files Skipped:    {result['files_skipped']}")
        print(f"  Files Excluded:   {result['files_excluded']}")
        print(f"  Files Deleted:    {result['files_deleted']}")
        print(f"  Files Failed:     {result['files_failed']}")
        print(f"  Enhancements:     {result['total_enhancements']}")
        print(f"  Processing Time:  {result['processing_time_seconds']:.2f}s")
        print("═" * 70 + "\n")
        
        if result['files_failed'] > 0:
            print("\n⚠️  ERRORS ENCOUNTERED:")
            for error in result.get('errors', []):
                print(f"  • {error}")
            print()
    else:
        print("\n" + "═" * 70)
        print("  ❌ BULK INGESTION FAILED")
        print("═" * 70)
        print(f"  Error: {result.get('error_message', 'Unknown error')}")
        print("═" * 70 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
