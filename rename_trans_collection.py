"""
Simple script to rename Trans collection to TRANS.

This script:
1. Scans G:\\FLICKS\\Trans directory
2. Renames files based on PLEX metadata
3. Updates file tags/metadata
4. Organizes into proper structure

No snapshots - direct operation.
"""

from pathlib import Path
from cortex.mcp.tools.video_library_tool import (
    cortex_video_library_preview,
    cortex_video_library_apply,
    cortex_video_library_update_metadata,
)
import json


def main():
    root = "G:\\FLICKS\\Trans"
    studio = "TRANS"
    
    print("=" * 80)
    print("CORTEX Trans Collection Rename Workflow")
    print("=" * 80)
    print(f"Target: {root}")
    print(f"Studio: {studio}")
    print()
    
    # Step 1: Preview renames
    print("\n[STEP 1] Preview proposed renames...")
    print("-" * 80)
    preview = cortex_video_library_preview(
        root_path=root,
        studio_filter=studio,
        min_confidence=0.5,
        limit_results=100
    )
    
    if not preview["success"]:
        print(f"ERROR: {preview.get('error')}")
        return
    
    print(f"Total files found: {preview['total_files']}")
    print(f"Rename proposals: {preview['proposal_count']}")
    print(f"Conflicts detected: {preview['conflict_count']}")
    print()
    
    if preview['proposal_count'] > 0:
        print("Sample proposals (first 10):")
        for i, p in enumerate(preview['proposals'][:10], 1):
            current = Path(p['current']).name
            proposed = Path(p['proposed']).name
            print(f"  {i}. {current}")
            print(f"     → {proposed}")
            print(f"     (confidence: {p['confidence']:.0%}, source: {p['source']})")
        print()
    
    # Step 2: Apply renames
    response = input("\n[STEP 2] Apply renames? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return
    
    print("\nApplying renames...")
    print("-" * 80)
    apply_result = cortex_video_library_apply(
        root_path=root,
        studio_filter=studio,
        min_confidence=0.75,
        limit_renames=200,
        dry_run=False
    )
    
    if not apply_result["success"]:
        print(f"ERROR: {apply_result.get('error')}")
        return
    
    print(f"✓ Renames applied: {apply_result['renames_applied']}")
    print(f"✗ Renames failed: {apply_result['renames_failed']}")
    print(f"- Renames skipped: {apply_result['renames_skipped']}")
    print()
    
    # Step 3: Update metadata/tags
    response = input("\n[STEP 3] Update file metadata/tags? (y/n): ")
    if response.lower() != 'y':
        print("Skipped metadata update.")
        return
    
    print("\nUpdating metadata/tags...")
    print("-" * 80)
    metadata_result = cortex_video_library_update_metadata(
        root_path=root,
        studio_filter=studio,
        sync_from_plex=True,
        dry_run=False
    )
    
    if not metadata_result["success"]:
        print(f"ERROR: {metadata_result.get('error')}")
        return
    
    print(f"✓ Files processed: {metadata_result['files_processed']}")
    print(f"✓ Files updated: {metadata_result['files_updated']}")
    print(f"✓ Fields changed: {metadata_result['fields_changed']}")
    print()
    
    print("=" * 80)
    print("✓ WORKFLOW COMPLETE")
    print("=" * 80)
    print(f"Total files renamed: {apply_result['renames_applied']}")
    print(f"Total metadata updated: {metadata_result['files_updated']}")
    print()


if __name__ == "__main__":
    main()
