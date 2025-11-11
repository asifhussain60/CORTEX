"""
CORTEX Workspace Cleanup CLI

Command-line interface for comprehensive workspace cleanup:
- Backup file management with GitHub archival
- Root folder organization
- File reorganization to correct locations
- MD file consolidation (removes duplicates)
- Bloat detection for entry points/orchestrators
- Automatic optimization trigger

Usage:
    python cleanup_workspace.py                    # Standard cleanup
    python cleanup_workspace.py --profile quick    # Quick cleanup
    python cleanup_workspace.py --profile comprehensive --optimize  # Full cleanup with optimization
    python cleanup_workspace.py --dry-run          # Preview changes without executing

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.operations.modules.cleanup import CleanupOrchestrator


def setup_logging(verbose: bool = False) -> None:
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                project_root / 'logs' / 'cleanup' / f'cleanup-{datetime.now().strftime("%Y%m%d-%H%M%S")}.log'
            )
        ]
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='CORTEX Workspace Cleanup - Comprehensive workspace maintenance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cleanup_workspace.py                      # Standard cleanup
  python cleanup_workspace.py --profile quick      # Quick cleanup (backups + root)
  python cleanup_workspace.py --profile comprehensive  # Full cleanup + optimization
  python cleanup_workspace.py --dry-run            # Preview without executing
  python cleanup_workspace.py --verbose            # Detailed logging

Profiles:
  quick         - Backups and root folder cleanup (fastest)
  standard      - Backups, root, and file reorganization (recommended)
  comprehensive - Full cleanup with MD consolidation, bloat detection, and optimization
        """
    )
    
    parser.add_argument(
        '--profile',
        choices=['quick', 'standard', 'comprehensive'],
        default='standard',
        help='Cleanup profile (default: standard)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without executing'
    )
    
    parser.add_argument(
        '--no-optimize',
        action='store_true',
        help='Skip optimization orchestrator trigger (comprehensive profile only)'
    )
    
    parser.add_argument(
        '--optimize-profile',
        choices=['quick', 'standard', 'comprehensive'],
        default='standard',
        help='Optimization profile if triggered (default: standard)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_dir = project_root / 'logs' / 'cleanup'
    log_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(args.verbose)
    
    logger = logging.getLogger(__name__)
    
    # Display banner
    print("=" * 80)
    print("CORTEX WORKSPACE CLEANUP")
    print("=" * 80)
    print(f"Profile: {args.profile}")
    print(f"Dry Run: {args.dry_run}")
    print(f"Project Root: {project_root}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    try:
        # Create orchestrator
        orchestrator = CleanupOrchestrator(project_root)
        
        # Check prerequisites
        logger.info("Checking prerequisites...")
        prereq_result = orchestrator.check_prerequisites({})
        
        if not prereq_result['prerequisites_met']:
            logger.error("Prerequisites not met:")
            for issue in prereq_result['issues']:
                logger.error(f"  - {issue}")
            return 1
        
        logger.info("✅ Prerequisites met")
        print()
        
        # Execute cleanup
        context = {
            'profile': args.profile,
            'dry_run': args.dry_run,
            'skip_optimization': args.no_optimize or args.profile != 'comprehensive',
            'optimization_profile': args.optimize_profile
        }
        
        result = orchestrator.execute(context)
        
        # Display results
        print()
        print("=" * 80)
        if result.success:
            print("✅ CLEANUP COMPLETED SUCCESSFULLY")
        else:
            print("❌ CLEANUP FAILED")
        print("=" * 80)
        print()
        
        if result.success:
            metrics = result.data['metrics']
            
            print("Results Summary:")
            print(f"  Backups Deleted:      {metrics['backups_deleted']}")
            print(f"  Backups Archived:     {metrics['backups_archived']}")
            print(f"  Root Files Cleaned:   {metrics['root_files_cleaned']}")
            print(f"  Files Reorganized:    {metrics['files_reorganized']}")
            print(f"  MD Files Consolidated: {metrics['md_files_consolidated']}")
            print(f"  Bloated Files Found:  {metrics['bloated_files_found']}")
            print(f"  Space Freed:          {metrics['space_freed_mb']:.2f}MB")
            print(f"  Git Commits:          {metrics['git_commits_created']}")
            print(f"  Optimization Triggered: {'Yes' if metrics['optimization_triggered'] else 'No'}")
            print(f"  Duration:             {metrics['duration_seconds']:.2f}s")
            print()
            
            # Display warnings
            if metrics.get('warnings'):
                print("Warnings:")
                for warning in metrics['warnings']:
                    print(f"  ⚠️  {warning}")
                print()
            
            # Display recommendations
            if result.data.get('report', {}).get('recommendations'):
                print("Recommendations:")
                for rec in result.data['report']['recommendations']:
                    print(f"  💡 {rec}")
                print()
            
            logger.info(f"Cleanup completed successfully: {result.message}")
            return 0
        else:
            print(f"Error: {result.message}")
            logger.error(f"Cleanup failed: {result.message}")
            return 1
            
    except KeyboardInterrupt:
        print()
        logger.warning("Cleanup interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
