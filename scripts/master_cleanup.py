"""
CORTEX Master Cleanup Script - One-Shot Efficient Cleanup

This script orchestrates comprehensive cleanup in one efficient pass:
1. Scans for unnecessary files (documentation, summaries, reports, reviews)
2. Categorizes and reports findings
3. Efficiently deletes all identified files in one operation
4. Cleans up empty directories
5. Generates cleanup report

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import our scan and cleanup modules
from scripts.scan_unnecessary_files import scan_repository, generate_report
from scripts.cleanup_unnecessary_files import cleanup_files


def main():
    """Execute master cleanup workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='CORTEX Master Cleanup - One-shot efficient cleanup'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually delete files (default is dry-run)'
    )
    parser.add_argument(
        '--skip-scan',
        action='store_true',
        help='Skip scan phase and use existing report'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("🧠 CORTEX MASTER CLEANUP - One-Shot Efficient Cleanup")
    print("="*80)
    print("\nAuthor: Asif Hussain")
    print("Copyright: © 2024-2025 Asif Hussain. All rights reserved.")
    print("="*80)
    
    # Phase 1: Scan (if not skipped)
    if not args.skip_scan:
        print("\n📡 Phase 1: Scanning Repository...")
        print("-" * 80)
        
        results = scan_repository(project_root)
        report_path = generate_report(results, project_root)
        
        print("\n✅ Phase 1 Complete - Scan report generated")
    else:
        print("\n⏭️  Phase 1: Skipped (using existing scan report)")
    
    # Phase 2: Cleanup
    print("\n🗑️  Phase 2: Cleanup Execution...")
    print("-" * 80)
    
    result = cleanup_files(project_root, dry_run=not args.execute)
    
    if result.get('success'):
        print("\n✅ Phase 2 Complete")
        
        if not result.get('dry_run'):
            print("\n" + "="*80)
            print("🎉 MASTER CLEANUP COMPLETE!")
            print("="*80)
            print(f"\n📊 Final Results:")
            print(f"   Files deleted: {result.get('deleted_count', 0)}")
            print(f"   Space freed: {result.get('deleted_size_mb', 0):.2f} MB")
            print(f"   Empty directories removed: {result.get('empty_dirs_removed', 0)}")
            print("\n" + "="*80)
        else:
            print("\n🔒 Dry-run complete. Run with --execute to actually delete files.")
    else:
        print("\n❌ Phase 2 Failed")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    
    return 0 if result.get('success') else 1


if __name__ == '__main__':
    sys.exit(main())
