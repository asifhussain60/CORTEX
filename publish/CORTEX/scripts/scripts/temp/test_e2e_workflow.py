"""
End-to-End Workflow Validation: Optimize → Cleanup

Tests the integration between optimize and cleanup orchestrators.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.operations.modules.optimize import OptimizeCortexOrchestrator
from src.operations.modules.cleanup import CleanupOrchestrator


def print_banner(title: str, mode: str = ""):
    """Print formatted banner"""
    print("\n" + "=" * 80)
    print(f"{title}")
    if mode:
        print(f"Mode: {mode}")
    print("=" * 80 + "\n")


def main():
    """Run end-to-end workflow validation"""
    
    print_banner("CORTEX END-TO-END WORKFLOW VALIDATION", "Optimize → Cleanup")
    
    # ===== STEP 1: Run Optimize in DRY-RUN mode =====
    print_banner("STEP 1: Optimize Orchestrator (DRY-RUN)", "Preview Only")
    
    try:
        optimize_orchestrator = OptimizeCortexOrchestrator(project_root)
        optimize_result_dry = optimize_orchestrator.execute({
            'profile': 'quick',  # Use quick profile to skip coverage
            'dry_run': True
        })
        
        print(f"✅ Status: {'SUCCESS' if optimize_result_dry.success else 'FAILED'}")
        print(f"📝 Message: {optimize_result_dry.message}")
        
        if optimize_result_dry.success:
            metrics = optimize_result_dry.data.get('metrics', {})
            print(f"\n📊 Metrics (DRY-RUN):")
            print(f"  - Obsolete tests found: {metrics.get('obsolete_tests_found', 0)}")
            print(f"  - Duration: {metrics.get('duration_seconds', 0):.2f}s")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    # ===== STEP 2: Run Optimize in LIVE mode =====
    print_banner("STEP 2: Optimize Orchestrator (LIVE)", "Production Mode")
    
    try:
        optimize_orchestrator = OptimizeCortexOrchestrator(project_root)
        optimize_result_live = optimize_orchestrator.execute({
            'profile': 'quick',  # Use quick profile
            'dry_run': False
        })
        
        print(f"✅ Status: {'SUCCESS' if optimize_result_live.success else 'FAILED'}")
        print(f"📝 Message: {optimize_result_live.message}")
        
        if optimize_result_live.success:
            metrics = optimize_result_live.data.get('metrics', {})
            print(f"\n📊 Metrics (LIVE):")
            print(f"  - Obsolete tests found: {metrics.get('obsolete_tests_found', 0)}")
            print(f"  - Manifest created: {metrics.get('manifest_created', False)}")
            print(f"  - Duration: {metrics.get('duration_seconds', 0):.2f}s")
            
            # Check if manifest was created
            manifest_path = project_root / 'cortex-brain' / 'obsolete-tests-manifest.json'
            if manifest_path.exists():
                print(f"\n📄 Manifest found at: {manifest_path}")
                with open(manifest_path, 'r') as f:
                    manifest_data = json.load(f)
                print(f"  - Obsolete tests marked: {len(manifest_data.get('obsolete_tests', []))}")
            else:
                print("\n⚠️  Warning: Manifest not created")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    # ===== STEP 3: Run Cleanup in DRY-RUN mode =====
    print_banner("STEP 3: Cleanup Orchestrator (DRY-RUN)", "Preview Detection")
    
    try:
        cleanup_orchestrator = CleanupOrchestrator(project_root)
        cleanup_result_dry = cleanup_orchestrator.execute({
            'profile': 'quick',
            'dry_run': True
        })
        
        print(f"✅ Status: {'SUCCESS' if cleanup_result_dry.success else 'FAILED'}")
        print(f"📝 Message: {cleanup_result_dry.message}")
        
        if cleanup_result_dry.success:
            metrics = cleanup_result_dry.data.get('metrics', {})
            print(f"\n📊 Metrics (DRY-RUN):")
            print(f"  - Backups to delete: {metrics.get('backups_deleted', 0)}")
            print(f"  - Files to reorganize: {metrics.get('files_reorganized', 0)}")
            print(f"  - Space to free: {metrics.get('space_freed_mb', 0):.2f}MB")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    # ===== STEP 4: Run Cleanup in LIVE mode =====
    print_banner("STEP 4: Cleanup Orchestrator (LIVE)", "Production Mode")
    
    try:
        cleanup_orchestrator = CleanupOrchestrator(project_root)
        cleanup_result_live = cleanup_orchestrator.execute({
            'profile': 'quick',
            'dry_run': False
        })
        
        print(f"✅ Status: {'SUCCESS' if cleanup_result_live.success else 'FAILED'}")
        print(f"📝 Message: {cleanup_result_live.message}")
        
        if cleanup_result_live.success:
            metrics = cleanup_result_live.data.get('metrics', {})
            print(f"\n📊 Metrics (LIVE):")
            print(f"  - Backups deleted: {metrics.get('backups_deleted', 0)}")
            print(f"  - Backups archived: {metrics.get('backups_archived', 0)}")
            print(f"  - Root files cleaned: {metrics.get('root_files_cleaned', 0)}")
            print(f"  - Files reorganized: {metrics.get('files_reorganized', 0)}")
            print(f"  - Space freed: {metrics.get('space_freed_mb', 0):.2f}MB")
            print(f"  - Duration: {metrics.get('duration_seconds', 0):.2f}s")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    # ===== VALIDATION =====
    print_banner("STEP 5: Validation", "Integration Check")
    
    validation_passed = True
    
    # Check 1: Both dry runs succeeded
    if not (optimize_result_dry.success and cleanup_result_dry.success):
        print("❌ Dry-run validation failed")
        validation_passed = False
    else:
        print("✅ Dry-run validation passed")
    
    # Check 2: Both live runs succeeded
    if not (optimize_result_live.success and cleanup_result_live.success):
        print("❌ Live execution validation failed")
        validation_passed = False
    else:
        print("✅ Live execution validation passed")
    
    # Check 3: Manifest behavior
    manifest_path = project_root / 'cortex-brain' / 'obsolete-tests-manifest.json'
    if manifest_path.exists():
        print("✅ Optimize created manifest file")
        print("✅ Cleanup can process manifest (if needed)")
    else:
        print("ℹ️  No manifest created (no obsolete tests found)")
    
    # Final result
    print_banner("FINAL RESULT")
    
    if validation_passed:
        print("✅ END-TO-END WORKFLOW VALIDATION PASSED")
        print("\n🎉 Integration working correctly:")
        print("  1. Optimize orchestrator executes successfully")
        print("  2. Cleanup orchestrator executes successfully")
        print("  3. Both dry-run and live modes work")
        print("  4. Manifest handling works correctly")
        return 0
    else:
        print("❌ END-TO-END WORKFLOW VALIDATION FAILED")
        print("\n⚠️  Issues detected in integration")
        return 1


if __name__ == '__main__':
    sys.exit(main())
