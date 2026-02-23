#!/usr/bin/env python3
"""
CORTEX Plex Fix for Wicked Library

Scans G:\FLICKS\Wicked, normalizes filenames, and enriches metadata.
"""

from cortex.mcp.tools.video_library_tool import cortex_plex_workflow_full


def main():
    """Execute plex workflow on Wicked directory."""
    print("=" * 80)
    print("CORTEX PLEX FIX - Wicked Library")
    print("=" * 80)
    print()

    # STEP 1: DRY RUN - Preview changes
    print("STEP 1: PREVIEW (DRY RUN)")
    print("-" * 80)
    
    result_preview = cortex_plex_workflow_full(
        root_path="G:\\FLICKS\\Wicked",
        studio_filter="Wicked",
        dry_run=True,
        use_iafd=True,
        normalize_filenames=True,
        auto_organize=False,  # Files stay in same folder
        min_match_confidence=0.75,
    )

    print(f"Success: {result_preview['success']}")
    print(f"Total files: {result_preview['total_files']}")
    print(f"Files to rename: {result_preview['files_renamed']}")
    print(f"Files to tag: {result_preview['files_tagged']}")
    print(f"Duration: {result_preview['duration_seconds']:.2f}s")
    print()

    if result_preview["errors"]:
        print("ERRORS:")
        for err in result_preview["errors"]:
            print(f"  - {err}")
        print()

    print("Workflow Steps:")
    for step in result_preview["steps"]:
        status_icon = (
            "✅" if step["status"] == "success"
            else ("❌" if step["status"] == "failed" else "⏭️")
        )
        print(
            f"  {status_icon} {step['name']}: {step['status']} "
            f"({step['duration_ms']:.0f}ms)"
        )
    print()

    # STEP 2: Confirm and apply
    print("=" * 80)
    print("STEP 2: APPLY CHANGES")
    print("-" * 80)
    
    result_apply = cortex_plex_workflow_full(
        root_path="G:\\FLICKS\\Wicked",
        studio_filter="Wicked",
        dry_run=False,  # APPLY CHANGES
        use_iafd=True,
        normalize_filenames=True,
        auto_organize=False,  # Files stay in same folder
        min_match_confidence=0.75,
    )

    print(f"Success: {result_apply['success']}")
    print(f"Total files: {result_apply['total_files']}")
    print(f"Files renamed: {result_apply['files_renamed']}")
    print(f"Files tagged: {result_apply['files_tagged']}")
    print(f"Duration: {result_apply['duration_seconds']:.2f}s")
    print()

    if result_apply["errors"]:
        print("ERRORS:")
        for err in result_apply["errors"]:
            print(f"  - {err}")
        print()

    if result_apply["warnings"]:
        print("WARNINGS:")
        for warn in result_apply["warnings"]:
            print(f"  - {warn}")
        print()

    print("Applied Workflow Steps:")
    for step in result_apply["steps"]:
        status_icon = (
            "✅" if step["status"] == "success"
            else ("❌" if step["status"] == "failed" else "⏭️")
        )
        print(
            f"  {status_icon} {step['name']}: {step['status']} "
            f"({step['duration_ms']:.0f}ms)"
        )
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files processed: {result_apply['total_files']}")
    print(f"Files renamed: {result_apply['files_renamed']}")
    print(f"Files tagged: {result_apply['files_tagged']}")
    print(f"Files organized: {result_apply['files_organized']}")
    print(f"Total duration: {result_apply['duration_seconds']:.2f}s")
    print()
    
    if result_apply["success"]:
        print("✅ Plex fix completed successfully!")
        print("   - All files renamed to meaningful, uncensored names")
        print("   - Metadata enriched from IAFD")
        print("   - Files remain in original location (G:\\FLICKS\\Wicked)")
    else:
        print("❌ Plex fix encountered errors. Review output above.")

    return 0 if result_apply["success"] else 1


if __name__ == "__main__":
    exit(main())
