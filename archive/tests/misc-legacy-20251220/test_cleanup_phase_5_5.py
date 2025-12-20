"""Test CleanupOrchestrator Phase 5.5 documentation archive cleanup"""

from pathlib import Path
from src.operations.modules.cleanup.cleanup_orchestrator import CleanupOrchestrator
import sys

def main():
    print("=" * 70)
    print("TESTING CLEANUP ORCHESTRATOR - PHASE 5.5")
    print("=" * 70)
    print()
    
    cortex_root = Path("D:/PROJECTS/CORTEX")
    co = CleanupOrchestrator(cortex_root)
    
    # Run cleanup with standard profile
    context = {
        'profile': 'standard',
        'dry_run': False
    }
    
    print("Executing cleanup with standard profile...")
    print()
    
    result = co.execute(context)
    
    # Extract metrics
    metrics = result.data.get('metrics', {})
    
    print()
    print("=" * 70)
    print("CLEANUP RESULTS")
    print("=" * 70)
    print(f"Success: {result.success}")
    print(f"Status: {result.status}")
    print(f"Message: {result.message}")
    print()
    print("METRICS:")
    print(f"  Backups deleted: {metrics.get('backups_deleted', 0)}")
    print(f"  Root files cleaned: {metrics.get('root_files_cleaned', 0)}")
    print(f"  Files reorganized: {metrics.get('files_reorganized', 0)}")
    print(f"  MD files consolidated: {metrics.get('md_files_consolidated', 0)}")
    print(f"  Archived docs removed: {metrics.get('archived_docs_removed', 0)} ⭐")
    print(f"  Bloated files found: {metrics.get('bloated_files_found', 0)}")
    print(f"  Space freed: {metrics.get('space_freed_mb', 0):.2f} MB")
    print(f"  Git commits created: {metrics.get('git_commits_created', 0)}")
    print(f"  Duration: {metrics.get('duration_seconds', 0):.1f}s")
    print()
    
    # Verify Phase 5.5 executed
    archived_docs_removed = metrics.get('archived_docs_removed', 0)
    
    print("=" * 70)
    print("PHASE 5.5 VALIDATION")
    print("=" * 70)
    
    if 'archived_docs_removed' in metrics:
        print("✅ Phase 5.5 integration confirmed - archived_docs_removed metric present")
        print(f"✅ Removed {archived_docs_removed} archived documentation files")
    else:
        print("❌ Phase 5.5 integration missing - archived_docs_removed metric not found")
        return 1
    
    if result.success:
        print("✅ Cleanup completed successfully")
        return 0
    else:
        print("❌ Cleanup failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
