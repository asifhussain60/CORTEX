#!/usr/bin/env python3
"""
Test script for Enhanced Cleanup Orchestrator v3.0

Runs comprehensive dry-run test of all new cleanup capabilities.

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
    """Run enhanced cleanup test"""
    
    print("=" * 80)
    print("ENHANCED CLEANUP ORCHESTRATOR v3.0 - DRY RUN TEST")
    print("=" * 80)
    print()
    
    try:
        # Initialize orchestrator
        logger.info("Initializing cleanup orchestrator...")
        orchestrator = CleanupOrchestrator(project_root=project_root)
        
        # Execute enhanced cleanup in DRY RUN mode
        logger.info("Executing enhanced cleanup (DRY RUN)...")
        print()
        
        result = orchestrator.execute_enhanced({
            'profile': 'comprehensive',
            'dry_run': True  # CRITICAL: DRY RUN MODE
        })
        
        print()
        print("=" * 80)
        print("TEST RESULTS")
        print("=" * 80)
        
        if result.success:
            print("✅ TEST PASSED - Enhanced cleanup executed successfully")
            print()
            
            # Display key metrics
            metrics = result.data.get('metrics', {})
            scan_stats = result.data.get('scan_stats', {})
            ref_stats = result.data.get('reference_stats', {})
            del_stats = result.data.get('deletion_stats', {})
            
            print("📊 SCAN STATISTICS:")
            print(f"   Total files scanned: {scan_stats.get('total_files', 0)}")
            print(f"   Total size: {scan_stats.get('total_size_mb', 0):.2f}MB")
            print(f"   Duplicates found: {scan_stats.get('duplicate_count', 0)}")
            print(f"   Categories: {len(scan_stats.get('categories', {}))}")
            print()
            
            print("🔗 REFERENCE STATISTICS:")
            print(f"   Total references: {ref_stats.get('total_references', 0)}")
            print(f"   Python imports: {ref_stats.get('total_imports', 0)}")
            print(f"   Path references: {ref_stats.get('total_path_refs', 0)}")
            print(f"   Markdown links: {ref_stats.get('total_links', 0)}")
            print(f"   Config references: {ref_stats.get('total_config_refs', 0)}")
            print()
            
            print("🗑️  DELETION STATISTICS:")
            print(f"   Deletion candidates: {del_stats.get('total_candidates', 0)}")
            print(f"   Safe to delete: {del_stats.get('safe_to_delete', 0)}")
            print(f"   Space to free: {del_stats.get('space_to_free_mb', 0):.2f}MB")
            print(f"   Risk breakdown: {del_stats.get('risk_breakdown', {})}")
            print()
            
            print("📄 REPORTS GENERATED:")
            report = result.data.get('report', {})
            if report.get('report_path'):
                print(f"   Enhanced report: {report['report_path']}")
            print()
            
            # Display verification results
            verification = result.data.get('verification', {})
            if verification.get('verification_passed'):
                print("✅ VERIFICATION: No essential files would be deleted")
            else:
                print(f"⚠️  VERIFICATION: {len(verification.get('essential_deleted', []))} essential files at risk")
                print("   Recovery commands available in report")
            print()
            
            print("=" * 80)
            print("✅ DRY RUN TEST COMPLETED SUCCESSFULLY")
            print("=" * 80)
            print()
            print("Next steps:")
            print("1. Review deletion manifest in cortex-brain/cleanup-reports/")
            print("2. Review reorganization plan")
            print("3. Check enhanced cleanup report for recommendations")
            print("4. If satisfied, run with dry_run=False")
            print()
            
            return 0
            
        else:
            print("❌ TEST FAILED")
            print(f"   Error: {result.message}")
            print()
            
            if result.data.get('error'):
                print(f"   Details: {result.data['error']}")
            
            return 1
    
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ TEST FAILED WITH EXCEPTION")
        print("=" * 80)
        print(f"Error: {e}")
        print()
        
        import traceback
        traceback.print_exc()
        
        return 1


if __name__ == '__main__':
    sys.exit(main())
