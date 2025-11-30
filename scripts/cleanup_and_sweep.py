"""
Integrated Cleanup & Sweep Script for CORTEX

Combines real cleanup orchestrator with sweeper plugin:
1. Runs CleanupOrchestrator (backup management, organization, etc.)
2. Runs SweeperPlugin (aggressive file cleanup with Recycle Bin)

This is the PRODUCTION cleanup - uses real implementations, not demos.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.operations.modules.cleanup import CleanupOrchestrator
from src.plugins.sweeper_plugin import SweeperPlugin


def print_banner():
    """Print operation banner"""
    print("=" * 80)
    print("CORTEX INTEGRATED CLEANUP & SWEEP")
    print("=" * 80)
    print()
    print("Author:     Asif Hussain")
    print("Copyright:  © 2024-2025 Asif Hussain. All rights reserved.")
    print("License:    Proprietary")
    print("Repository: https://github.com/asifhussain60/CORTEX")
    print()
    print("=" * 80)
    print()
    print("This script performs two-stage cleanup:")
    print("  1. CLEANUP ORCHESTRATOR - Backup management, organization, optimization")
    print("  2. SWEEPER PLUGIN - Aggressive file cleanup (Recycle Bin mode)")
    print()
    print("All deleted files are RECOVERABLE from OS Recycle Bin!")
    print("=" * 80)
    print()


def run_cleanup_orchestrator(workspace_root: Path, dry_run: bool = False) -> dict:
    """
    Run the real CleanupOrchestrator.
    
    Args:
        workspace_root: Path to CORTEX workspace
        dry_run: If True, preview changes without executing
    
    Returns:
        Dict with success status and metrics
    """
    print("\n" + "=" * 80)
    print("STAGE 1: CLEANUP ORCHESTRATOR")
    print("=" * 80)
    print()
    
    try:
        # Initialize orchestrator
        orchestrator = CleanupOrchestrator(workspace_root)
        
        # Check prerequisites
        print("Checking prerequisites...")
        prereq_result = orchestrator.check_prerequisites({})
        
        if not prereq_result['prerequisites_met']:
            print("❌ Prerequisites not met:")
            for issue in prereq_result['issues']:
                print(f"  - {issue}")
            return {"success": False, "error": "Prerequisites not met"}
        
        print("✅ Prerequisites met")
        print()
        
        # Execute cleanup
        mode = "DRY RUN" if dry_run else "LIVE"
        print(f"Running cleanup in {mode} mode...")
        print()
        
        result = orchestrator.execute({
            'profile': 'standard',
            'dry_run': dry_run,
            'skip_optimization': False
        })
        
        if result.success:
            metrics = result.data['metrics']
            
            print()
            print("✅ CLEANUP ORCHESTRATOR COMPLETED")
            print()
            print(f"Backups Deleted:      {metrics['backups_deleted']}")
            print(f"Backups Archived:     {metrics['backups_archived']}")
            print(f"Root Files Cleaned:   {metrics['root_files_cleaned']}")
            print(f"Files Reorganized:    {metrics['files_reorganized']}")
            print(f"MD Files Consolidated: {metrics['md_files_consolidated']}")
            print(f"Space Freed:          {metrics['space_freed_mb']:.2f} MB")
            print(f"Duration:             {metrics['duration_seconds']:.2f}s")
            print()
            
            return {
                "success": True,
                "metrics": metrics
            }
        else:
            print(f"❌ CLEANUP FAILED: {result.message}")
            return {
                "success": False,
                "error": result.message
            }
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def run_sweeper(workspace_root: Path) -> dict:
    """
    Run the SweeperPlugin for aggressive cleanup.
    
    Args:
        workspace_root: Path to CORTEX workspace
    
    Returns:
        Dict with success status and stats
    """
    print("\n" + "=" * 80)
    print("STAGE 2: SWEEPER PLUGIN")
    print("=" * 80)
    print()
    
    try:
        # Initialize sweeper
        print("Initializing sweeper...")
        sweeper = SweeperPlugin()
        
        if not sweeper.initialize():
            print("❌ Failed to initialize sweeper")
            return {"success": False, "error": "Initialization failed"}
        
        print("Running sweeper (RECYCLE BIN MODE - files can be restored)...")
        print()
        
        # Execute sweeper
        result = sweeper.execute({"workspace_root": str(workspace_root)})
        
        if not result["success"]:
            print(f"❌ SWEEPER FAILED: {result.get('error', 'Unknown error')}")
            return result
        
        # Show results
        stats = result["stats"]
        
        print()
        print("✅ SWEEPER COMPLETED")
        print()
        print(f"Files scanned:     {stats['files_scanned']:,}")
        print(f"Files moved:       {stats['files_deleted']:,} (to Recycle Bin)")
        print(f"Files kept:        {stats['files_kept']:,}")
        print(f"Space freed:       {stats['space_freed_mb']:.2f} MB")
        print(f"Execution time:    {stats['execution_time']:.2f}s")
        print()
        print("Audit log: cortex-brain/sweeper-logs/")
        print()
        
        if result.get("errors"):
            print(f"⚠️  Errors: {len(result['errors'])}")
            for error in result['errors']:
                print(f"  - {error}")
            print()
        
        return result
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Main execution"""
    print_banner()
    
    workspace_root = Path(__file__).parent.parent
    
    # Get user confirmation
    print(f"Workspace: {workspace_root}")
    print()
    response = input("Run integrated cleanup? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Cancelled.")
        return
    
    # Ask about dry-run for cleanup orchestrator
    dry_run_response = input("Dry-run mode for Cleanup Orchestrator? (yes/no): ").strip().lower()
    dry_run = dry_run_response in ['yes', 'y']
    
    start_time = datetime.now()
    
    # Stage 1: Cleanup Orchestrator
    cleanup_result = run_cleanup_orchestrator(workspace_root, dry_run=dry_run)
    
    if not cleanup_result["success"]:
        print("\n" + "=" * 80)
        print("❌ CLEANUP ORCHESTRATOR FAILED - ABORTING")
        print("=" * 80)
        return
    
    # Stage 2: Sweeper (always live mode - uses Recycle Bin)
    sweeper_result = run_sweeper(workspace_root)
    
    # Final summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print()
    
    if cleanup_result["success"] and sweeper_result["success"]:
        print("✅ ALL STAGES COMPLETED SUCCESSFULLY")
        print()
        
        # Combined metrics
        cleanup_metrics = cleanup_result.get("metrics", {})
        sweeper_stats = sweeper_result.get("stats", {})
        
        total_space_freed = (
            cleanup_metrics.get('space_freed_mb', 0) +
            sweeper_stats.get('space_freed_mb', 0)
        )
        
        print(f"Total space freed:    {total_space_freed:.2f} MB")
        print(f"Total duration:       {duration:.2f}s")
        print()
        print("Stage 1 (Orchestrator):")
        print(f"  Backups cleaned:    {cleanup_metrics.get('backups_deleted', 0)}")
        print(f"  Files reorganized:  {cleanup_metrics.get('files_reorganized', 0)}")
        print(f"  Space freed:        {cleanup_metrics.get('space_freed_mb', 0):.2f} MB")
        print()
        print("Stage 2 (Sweeper):")
        print(f"  Files moved:        {sweeper_stats.get('files_deleted', 0)}")
        print(f"  Space freed:        {sweeper_stats.get('space_freed_mb', 0):.2f} MB")
        print()
        print("✅ All files moved to Recycle Bin are fully recoverable!")
        
    else:
        print("⚠️  SOME STAGES FAILED")
        print()
        if not cleanup_result["success"]:
            print(f"Stage 1: ❌ {cleanup_result.get('error', 'Unknown error')}")
        else:
            print("Stage 1: ✅")
        
        if not sweeper_result["success"]:
            print(f"Stage 2: ❌ {sweeper_result.get('error', 'Unknown error')}")
        else:
            print("Stage 2: ✅")
    
    print()
    print("=" * 80)
    print(f"Completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == "__main__":
    main()
