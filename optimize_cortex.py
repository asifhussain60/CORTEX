#!/usr/bin/env python3
"""
CORTEX Optimization CLI

Command-line interface for running CORTEX optimizations.

Usage:
    python optimize_cortex.py                    # Run standard optimization
    python optimize_cortex.py --profile quick     # Quick optimization
    python optimize_cortex.py --profile full      # Full optimization with all checks

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import argparse
import sys
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.operations.modules.optimization import OptimizeCortexOrchestrator


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('cortex-optimization.log')
        ]
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='CORTEX Optimization Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          Run standard optimization
  %(prog)s --profile quick          Quick optimization (tests + analysis)
  %(prog)s --profile comprehensive  Full optimization with all improvements
  %(prog)s --verbose                Show detailed debug output
  %(prog)s --dry-run               Show what would be done without changes
        """
    )
    
    parser.add_argument(
        '--profile',
        choices=['quick', 'standard', 'comprehensive'],
        default='standard',
        help='Optimization profile to use (default: standard)'
    )
    
    parser.add_argument(
        '--project-root',
        type=Path,
        default=Path(__file__).parent.parent,
        help='CORTEX project root directory (default: auto-detect)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be optimized without making changes'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose debug output'
    )
    
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip SKULL tests (not recommended)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Validate project root
    if not args.project_root.exists():
        logger.error(f"Project root not found: {args.project_root}")
        sys.exit(1)
    
    logger.info("=" * 80)
    logger.info("CORTEX OPTIMIZATION ORCHESTRATOR")
    logger.info("=" * 80)
    logger.info(f"Profile: {args.profile}")
    logger.info(f"Project Root: {args.project_root}")
    logger.info(f"Dry Run: {args.dry_run}")
    logger.info("")
    
    # Create orchestrator
    orchestrator = OptimizeCortexOrchestrator(project_root=args.project_root)
    
    # Validate prerequisites
    is_valid, issues = orchestrator.validate_prerequisites({
        'project_root': args.project_root
    })
    
    if not is_valid:
        logger.error("Prerequisites not met:")
        for issue in issues:
            logger.error(f"  - {issue}")
        sys.exit(1)
    
    # Execute optimization
    try:
        context = {
            'project_root': args.project_root,
            'profile': args.profile,
            'dry_run': args.dry_run,
            'skip_tests': args.skip_tests
        }
        
        result = orchestrator.execute(context)
        
        if result.success:
            logger.info("\n" + "=" * 80)
            logger.info("OPTIMIZATION SUCCESSFUL")
            logger.info("=" * 80)
            
            # Display metrics
            if 'metrics' in result.data:
                metrics = result.data['metrics']
                logger.info(f"\nMetrics:")
                logger.info(f"  Duration: {metrics['duration_seconds']:.2f}s")
                logger.info(f"  Issues identified: {metrics['issues_identified']}")
                logger.info(f"  Optimizations applied: {metrics['optimizations_succeeded']}")
                logger.info(f"  Git commits: {len(metrics['git_commits'])}")
                
                if metrics['git_commits']:
                    logger.info(f"\nGit commits:")
                    for commit_hash in metrics['git_commits']:
                        logger.info(f"    {commit_hash[:8]}")
            
            # Display report
            if 'report' in result.data:
                logger.info(f"\nDetailed Report:")
                logger.info(result.data['report'])
            
            sys.exit(0)
        else:
            logger.error("\n" + "=" * 80)
            logger.error("OPTIMIZATION FAILED")
            logger.error("=" * 80)
            logger.error(f"\nMessage: {result.message}")
            
            if result.errors:
                logger.error(f"\nErrors:")
                for error in result.errors:
                    logger.error(f"  - {error}")
            
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("\nOptimization interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"\nFatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
