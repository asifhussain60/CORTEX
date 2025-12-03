#!/usr/bin/env python3
"""
Live execution script for Enhanced Cleanup Orchestrator v3.0

CAUTION: This will make actual changes to the repository!

Author: Asif Hussain
Date: December 3, 2025
"""

import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.operations.modules.cleanup.cleanup_orchestrator import CleanupOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run enhanced cleanup - LIVE EXECUTION"""
    
    print("=" * 80)
    print("ENHANCED CLEANUP ORCHESTRATOR v3.0 - LIVE EXECUTION")
    print("⚠️  WARNING: This will make actual changes!")
    print("=" * 80)
    print()
    
    # Safety confirmation
    print("Based on dry-run results, this will:")
    print("  - Delete 1 file (empty log)")
    print("  - Move 6 files to scripts/misc/")
    print("  - Update references (if any)")
    print("  - Commit changes to git")
    print()
    
    try:
        # Initialize orchestrator
        logger.info("Initializing cleanup orchestrator...")
        orchestrator = CleanupOrchestrator(project_root=project_root)
        
        # Execute enhanced cleanup in LIVE mode
        logger.info("Executing enhanced cleanup (LIVE MODE)...")
        print()
        
        result = orchestrator.execute_enhanced({
            'profile': 'comprehensive',
            'dry_run': False  # LIVE EXECUTION
        })
        
        print()
        print("=" * 80)
        print("LIVE EXECUTION RESULTS")
        print("=" * 80)
        
        if result.success:
            print("✅ LIVE EXECUTION SUCCESSFUL")
            print()
            
            # Display key metrics
            metrics = result.data.get('metrics', {})
            scan_stats = result.data.get('scan_stats', {})
            deletion_results = result.data.get('deletion_results', {})
            reorg_results = result.data.get('reorganization_results', {})
            verification = result.data.get('verification', {})
            
            print("📊 EXECUTION SUMMARY:")
            print(f"   Duration: {metrics.get('duration_seconds', 0):.2f}s")
            print(f"   Files scanned: {scan_stats.get('total_files', 0)}")
            print(f"   Files deleted: {deletion_results.get('deleted_count', 0)}")
            print(f"   Files moved: {reorg_results.get('moved_count', 0)}")
            print(f"   References updated: {reorg_results.get('references_updated', 0)}")
            print(f"   Space freed: {deletion_results.get('space_freed_mb', 0):.2f}MB")
            print()
            
            if deletion_results.get('deleted_files'):
                print("🗑️  DELETED FILES:")
                for file in deletion_results['deleted_files']:
                    print(f"   - {file}")
                print()
            
            if reorg_results.get('moved_files'):
                print("📦 MOVED FILES:")
                for file in reorg_results['moved_files']:
                    print(f"   - {file} → scripts/misc/")
                print()
            
            if reorg_results.get('failed_moves'):
                print("❌ FAILED MOVES:")
                for failure in reorg_results['failed_moves']:
                    print(f"   - {failure['old_path']}: {failure['error']}")
                print()
            
            # Verification status
            if verification.get('verification_passed'):
                print("✅ VERIFICATION: No essential files deleted")
            else:
                print(f"⚠️  VERIFICATION: {len(verification.get('essential_deleted', []))} essential files deleted")
                print("   Review recovery commands in report")
            print()
            
            # Git status
            if metrics.get('git_commits_created', 0) > 0:
                print("✅ Changes committed to git")
            else:
                print("⚠️  Changes not yet committed (no files changed)")
            print()
            
            print("=" * 80)
            print("✅ LIVE EXECUTION COMPLETED SUCCESSFULLY")
            print("=" * 80)
            print()
            print("Changes have been made to the repository.")
            print("Review with: git status")
            print("Review commit: git log -1")
            print("Rollback if needed: git reset --hard HEAD~1")
            print()
            
            return 0
            
        else:
            print("❌ LIVE EXECUTION FAILED")
            print(f"   Error: {result.message}")
            print()
            
            if result.data.get('error'):
                print(f"   Details: {result.data['error']}")
            
            return 1
    
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ LIVE EXECUTION FAILED WITH EXCEPTION")
        print("=" * 80)
        print(f"Error: {e}")
        print()
        
        import traceback
        traceback.print_exc()
        
        print()
        print("Repository may be in inconsistent state.")
        print("Check: git status")
        print("Restore if needed: git reset --hard HEAD")
        print()
        
        return 1


if __name__ == '__main__':
    sys.exit(main())
