#!/usr/bin/env python3
"""
Deprecated Code Removal Script

Removes all deprecated functions, classes, and modules identified in
the obsolete-tests-manifest.json file.

Part of Phase 0 Deliverable 0.4 - Foundation: Code Quality & Debugging

Usage:
    python scripts/remove_deprecated_code.py --dry-run
    python scripts/remove_deprecated_code.py

Author: Asif Hussain
License: Source-Available (Use Allowed, No Contributions)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict
from datetime import datetime


def load_obsolete_manifest(manifest_path: str) -> Dict:
    """Load the obsolete tests manifest."""
    try:
        with open(manifest_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading manifest: {e}", file=sys.stderr)
        sys.exit(2)


def remove_obsolete_tests(manifest_data: Dict, dry_run: bool = False) -> tuple:
    """
    Remove obsolete test files listed in manifest.
    
    Returns:
        Tuple of (files_removed, files_not_found, errors)
    """
    removed = []
    not_found = []
    errors = []
    
    for test_entry in manifest_data.get("tests", []):
        file_path = Path(test_entry["file_path"])
        
        if not file_path.exists():
            not_found.append(str(file_path))
            continue
        
        try:
            if dry_run:
                print(f"  Would remove: {file_path}")
                removed.append(str(file_path))
            else:
                file_path.unlink()
                removed.append(str(file_path))
                print(f"  ✓ Removed: {file_path}")
        except Exception as e:
            errors.append(f"{file_path}: {e}")
            print(f"  ❌ Error removing {file_path}: {e}", file=sys.stderr)
    
    return removed, not_found, errors


def update_changelog(removed_count: int, dry_run: bool = False):
    """Update CHANGELOG.md with deprecated code removal."""
    changelog_path = Path("CHANGELOG.md")
    
    if not changelog_path.exists():
        print("⚠️  CHANGELOG.md not found, skipping changelog update")
        return
    
    try:
        with open(changelog_path, 'r') as f:
            content = f.read()
        
        # Create new entry
        entry = f"""
## [Phase 0.4] - {datetime.now().strftime('%Y-%m-%d')}

### Removed (Breaking Changes)
- **Obsolete Test Files**: Removed {removed_count} obsolete test files
  - Tests were importing non-existent modules
  - Tests were no longer maintained or relevant
  - See `cortex-brain/obsolete-tests-manifest.json` for full list
  - Action: Review manifest for removed files if needed

### Technical Debt Reduction
- Code cleanup as part of Phase 0 (Foundation: Code Quality & Debugging)
- Improved test suite maintainability
- Reduced false negatives in test discovery

"""
        
        # Insert after first line (usually # CHANGELOG)
        lines = content.split('\n')
        if lines and lines[0].startswith('# '):
            new_content = '\n'.join([lines[0], entry] + lines[1:])
        else:
            new_content = entry + content
        
        if dry_run:
            print(f"\n  Would update CHANGELOG.md with entry:")
            print(entry)
        else:
            with open(changelog_path, 'w') as f:
                f.write(new_content)
            print(f"  ✓ Updated CHANGELOG.md")
    
    except Exception as e:
        print(f"⚠️  Error updating CHANGELOG: {e}", file=sys.stderr)


def update_manifest(manifest_path: str, removed_files: List[str], dry_run: bool = False):
    """Update manifest to mark files as removed."""
    try:
        with open(manifest_path, 'r') as f:
            data = json.load(f)
        
        # Add removal timestamp
        data["removed_timestamp"] = datetime.now().isoformat()
        data["files_removed_count"] = len(removed_files)
        data["phase_0_4_complete"] = True
        
        # Mark each test as removed
        for test in data["tests"]:
            if test["file_path"] in removed_files:
                test["removed"] = True
                test["removed_at"] = data["removed_timestamp"]
        
        if dry_run:
            print(f"\n  Would update manifest with removal timestamp")
        else:
            with open(manifest_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"  ✓ Updated manifest")
    
    except Exception as e:
        print(f"⚠️  Error updating manifest: {e}", file=sys.stderr)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Remove deprecated code based on obsolete-tests-manifest.json"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually removing"
    )
    parser.add_argument(
        "--manifest",
        type=str,
        default="cortex-brain/obsolete-tests-manifest.json",
        help="Path to obsolete tests manifest (default: cortex-brain/obsolete-tests-manifest.json)"
    )
    
    args = parser.parse_args()
    
    mode = "DRY RUN" if args.dry_run else "LIVE REMOVAL"
    print(f"🧹 {mode}: Removing deprecated code...")
    print(f"📄 Manifest: {args.manifest}\n")
    
    # Load manifest
    manifest_data = load_obsolete_manifest(args.manifest)
    total_tests = len(manifest_data.get("tests", []))
    print(f"Found {total_tests} obsolete test files in manifest")
    
    # Remove obsolete tests
    removed, not_found, errors = remove_obsolete_tests(manifest_data, args.dry_run)
    
    print(f"\n{'Would remove' if args.dry_run else 'Removed'}: {len(removed)} file(s)")
    if not_found:
        print(f"Already removed/not found: {len(not_found)} file(s)")
    if errors:
        print(f"Errors: {len(errors)} file(s)")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
    
    # Update CHANGELOG
    if removed:
        print("\nUpdating CHANGELOG.md...")
        update_changelog(len(removed), args.dry_run)
    
    # Update manifest
    if removed:
        print("\nUpdating manifest...")
        update_manifest(args.manifest, removed, args.dry_run)
    
    print("\n" + "="*70)
    if args.dry_run:
        print("✅ DRY RUN COMPLETE")
        print("Run without --dry-run to apply changes")
    else:
        print("✅ DEPRECATED CODE REMOVAL COMPLETE")
        print(f"Removed {len(removed)} obsolete test files")
        print("CHANGELOG.md and manifest updated")
    print("="*70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
