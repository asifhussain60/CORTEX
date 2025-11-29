"""
CORTEX Cleanup - Efficiently delete unnecessary documentation files.
One-shot script to remove temporary, summary, review, and informational files.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json
import shutil

# Protected files - NEVER delete these
PROTECTED_FILES = {
    'README.md', 'CHANGELOG.md', 'LICENSE.md', 'LICENSE',
    # Phase documentation (current/active)
    'PHASE-3-COMMIT-GUIDE.md', 'PHASE-3-SUMMARY.md',
    'PHASE-3-VISUAL-SUMMARY.md', 'PHASE-4-PRODUCTION-READY.md',
    'GIT-SYNC-COMPLETE.md',
    # Essential guides (keep)
    'QUICK-START.md',
    # CORTEX brain organized docs (keep structure)
    'cortex-brain/documents/',
}

# Directories to preserve entirely
PRESERVE_DIRS = {
    'cortex-brain/documents',  # Organized structure
    'cortex-brain/archives',    # Already archived
    '.git', '.github/prompts', '.github/workflows',
    'src', 'tests/fixtures', 'docs/api', 'docs/reference'
}


def should_preserve(file_path: Path, project_root: Path) -> tuple[bool, str]:
    """Check if file should be preserved."""
    try:
        rel_path = file_path.relative_to(project_root)
        rel_str = str(rel_path).replace('\\', '/')
        
        # Check protected files
        if file_path.name in PROTECTED_FILES:
            return True, f"Protected file: {file_path.name}"
        
        # Check preserve directories
        for preserve_dir in PRESERVE_DIRS:
            if rel_str.startswith(preserve_dir):
                return True, f"In preserved directory: {preserve_dir}"
        
        # Keep CORTEX 3.0 design docs
        if 'cortex-3.0-design' in rel_str:
            return True, "CORTEX 3.0 design documentation"
        
        # Keep essential phase docs
        if 'PHASE-' in file_path.name and any(x in file_path.name for x in ['COMMIT-GUIDE', 'SUMMARY', 'VISUAL', 'PRODUCTION-READY']):
            return True, "Active phase documentation"
        
        return False, ""
    
    except ValueError:
        return True, "Outside project root"


def load_scan_report(project_root: Path) -> dict:
    """Load the most recent scan report."""
    reports_dir = project_root / 'cortex-brain' / 'cleanup-reports'
    if not reports_dir.exists():
        return None
    
    # Find most recent report
    reports = sorted(reports_dir.glob('unnecessary-files-*.json'), reverse=True)
    if not reports:
        return None
    
    with open(reports[0], 'r', encoding='utf-8') as f:
        return json.load(f)


def cleanup_files(project_root: Path, dry_run: bool = True) -> dict:
    """Delete unnecessary files efficiently."""
    print("\n" + "="*80)
    print("🧠 CORTEX CLEANUP - Removing Unnecessary Files")
    print("="*80)
    
    # Load scan report
    scan_data = load_scan_report(project_root)
    if not scan_data:
        print("\n❌ No scan report found. Run scan_unnecessary_files.py first.")
        return {'success': False, 'error': 'No scan report'}
    
    print(f"\n📊 Loaded scan report:")
    print(f"   Total files: {scan_data['total_files']}")
    print(f"   Total size: {scan_data['total_size_mb']} MB")
    
    # Collect files to delete
    files_to_delete = []
    files_preserved = []
    
    for category, files in scan_data['files'].items():
        for file_info in files:
            file_path = project_root / file_info['path']
            
            if not file_path.exists():
                continue
            
            should_keep, reason = should_preserve(file_path, project_root)
            if should_keep:
                files_preserved.append((file_path, reason))
            else:
                files_to_delete.append((file_path, file_info, category))
    
    print(f"\n📁 Analysis:")
    print(f"   Files to delete: {len(files_to_delete)}")
    print(f"   Files preserved: {len(files_preserved)}")
    
    if files_preserved:
        print(f"\n✅ Preserved files (first 10):")
        for file_path, reason in files_preserved[:10]:
            print(f"     • {file_path.name}: {reason}")
        if len(files_preserved) > 10:
            print(f"     ... and {len(files_preserved) - 10} more")
    
    if not files_to_delete:
        print("\n✨ Nothing to delete!")
        return {'success': True, 'deleted': 0, 'space_freed_mb': 0.0}
    
    # Calculate total size
    total_size = sum(f[1]['size'] for f in files_to_delete)
    total_mb = total_size / (1024 * 1024)
    
    print(f"\n🗑️  Files to delete:")
    print(f"   Count: {len(files_to_delete)}")
    print(f"   Size: {total_mb:.2f} MB")
    
    # Show sample files by category
    by_category = {}
    for file_path, file_info, category in files_to_delete:
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(file_path)
    
    print(f"\n📋 By Category:")
    for category, paths in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n   {category.upper()}: {len(paths)} files")
        for path in paths[:3]:
            print(f"     • {path.relative_to(project_root)}")
        if len(paths) > 3:
            print(f"     ... and {len(paths) - 3} more")
    
    if dry_run:
        print(f"\n🔒 DRY RUN MODE - No files deleted")
        print(f"   Run with --execute to actually delete files")
        return {
            'success': True,
            'dry_run': True,
            'files_found': len(files_to_delete),
            'space_would_free_mb': total_mb
        }
    
    # Confirm deletion
    print(f"\n⚠️  WARNING: About to delete {len(files_to_delete)} files ({total_mb:.2f} MB)")
    response = input("   Continue? [y/N]: ")
    if response.lower() != 'y':
        print("❌ Cleanup cancelled")
        return {'success': False, 'cancelled': True}
    
    # Delete files
    deleted_count = 0
    deleted_size = 0
    errors = []
    
    print(f"\n🗑️  Deleting files...")
    for file_path, file_info, category in files_to_delete:
        try:
            if file_path.exists():
                size = file_path.stat().st_size
                file_path.unlink()
                deleted_count += 1
                deleted_size += size
                print(f"     ✓ Deleted: {file_path.name} ({category})")
        except Exception as e:
            errors.append(f"{file_path.name}: {e}")
            print(f"     ✗ Error: {file_path.name}: {e}")
    
    # Clean up empty directories
    print(f"\n🧹 Cleaning up empty directories...")
    empty_dirs_removed = 0
    for dirpath, dirnames, filenames in os.walk(project_root, topdown=False):
        dir_path = Path(dirpath)
        
        # Skip preserved directories
        try:
            rel_path = dir_path.relative_to(project_root)
            rel_str = str(rel_path).replace('\\', '/')
            if any(rel_str.startswith(pd) for pd in PRESERVE_DIRS):
                continue
        except ValueError:
            continue
        
        # Remove if empty
        try:
            if dir_path.exists() and not any(dir_path.iterdir()):
                dir_path.rmdir()
                empty_dirs_removed += 1
                print(f"     ✓ Removed empty dir: {dir_path.relative_to(project_root)}")
        except Exception as e:
            pass
    
    # Final summary
    deleted_mb = deleted_size / (1024 * 1024)
    
    print(f"\n" + "="*80)
    print(f"✅ CLEANUP COMPLETE!")
    print(f"="*80)
    print(f"\n📊 Results:")
    print(f"   Files deleted: {deleted_count}")
    print(f"   Space freed: {deleted_mb:.2f} MB")
    print(f"   Empty dirs removed: {empty_dirs_removed}")
    
    if errors:
        print(f"\n⚠️  Errors: {len(errors)}")
        for error in errors[:5]:
            print(f"     • {error}")
    
    print(f"\n" + "="*80)
    
    # Save cleanup report
    cleanup_report = {
        'timestamp': datetime.now().isoformat(),
        'deleted_count': deleted_count,
        'deleted_size_bytes': deleted_size,
        'deleted_size_mb': round(deleted_mb, 2),
        'empty_dirs_removed': empty_dirs_removed,
        'errors': errors,
        'preserved_count': len(files_preserved)
    }
    
    report_path = project_root / 'cortex-brain' / 'cleanup-reports' / f'cleanup-execution-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(cleanup_report, f, indent=2)
    
    print(f"💾 Cleanup report saved: {report_path.relative_to(project_root)}")
    
    return {
        'success': True,
        'deleted_count': deleted_count,
        'deleted_size_mb': deleted_mb,
        'empty_dirs_removed': empty_dirs_removed,
        'errors': errors
    }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='CORTEX Cleanup - Remove unnecessary documentation files'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually delete files (default is dry-run)'
    )
    parser.add_argument(
        '--project-root',
        type=Path,
        help='Project root directory (auto-detected if not specified)'
    )
    
    args = parser.parse_args()
    
    # Auto-detect project root
    if args.project_root:
        project_root = args.project_root
    else:
        project_root = Path(__file__).parent.parent
    
    if not project_root.exists():
        print(f"❌ Project root not found: {project_root}")
        sys.exit(1)
    
    # Run cleanup
    result = cleanup_files(project_root, dry_run=not args.execute)
    
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
