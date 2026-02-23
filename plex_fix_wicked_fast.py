#!/usr/bin/env python3
r"""
CORTEX Plex Fix for Wicked Library - Fast Mode

Applies metadata enrichment without IAFD (avoids rate limiting).
Files are already meaningfully named - this ensures metadata tags are current.
"""

from cortex.mcp.tools.video_library_tool import cortex_plex_workflow_full


def main():
    """Execute plex workflow on Wicked directory (fast mode - no IAFD)."""
    print("=" * 80)
    print("CORTEX PLEX FIX - Wicked Library (Fast Mode)")
    print("=" * 80)
    print()

    # Run workflow without IAFD to avoid rate limiting
    # Files already have meaningful names, so focus on metadata tagging
    print("Applying metadata enrichment to all files...")
    print()
    
    result = cortex_plex_workflow_full(
        root_path="G:\\FLICKS\\Wicked",
        studio_filter="Wicked",
        dry_run=False,  # APPLY CHANGES
        use_iafd=False,  # Skip IAFD (rate limited) - filenames are already good
        normalize_filenames=True,  # Ensure consistent naming
        auto_organize=False,  # Keep files in same directory
        min_match_confidence=0.75,
    )

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Total files processed: {result['total_files']}")
    print(f"Files scanned: {result['files_scanned']}")
    print(f"Files identified: {result['files_identified']}")
    print(f"Files renamed: {result['files_renamed']}")
    print(f"Files tagged: {result['files_tagged']}")
    print(f"Duration: {result['duration_seconds']:.2f}s")
    print()

    if result["errors"]:
        print("ERRORS:")
        for err in result["errors"]:
            print(f"  [ERROR] {err}")
        print()

    if result["warnings"]:
        print("WARNINGS:")
        for warn in result["warnings"]:
            print(f"  [WARN] {warn}")
        print()

    print("Workflow Steps:")
    for step in result["steps"]:
        status_icon = (
            "[PASS]" if step["status"] == "success"
            else ("[FAIL]" if step["status"] == "failed" else "[SKIP]")
        )
        print(
            f"  {status_icon} {step['name']}: {step['status']} "
            f"({step['duration_ms']:.0f}ms)"
        )
    print()

    # Final status
    print("=" * 80)
    if result["success"]:
        print("[SUCCESS] PLEX FIX COMPLETED")
        print()
        print("Summary:")
        print("  + All files have meaningful, uncensored names")
        print("  + Metadata enriched and tagged")
        print("  + Files remain in G:\\FLICKS\\Wicked (no nesting)")
        print("  + Ready for Plex Media Server library import")
    else:
        print("[ERROR] PLEX FIX COMPLETED WITH ERRORS")
        print("   Review warnings and errors above")
    print("=" * 80)

    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit(main())
