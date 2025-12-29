"""
CLI Wrapper for System Integrity Orchestrator

Usage:
    python scripts/cli_wrappers/system_integrity_wrapper.py [options]

Options:
    --fix / --no-fix          Enable/disable auto-fix (default: enabled)
    --tests / --no-tests      Run test suite (default: enabled)
    --docs / --no-docs        Generate missing docs (default: enabled)
    --legacy / --no-legacy    Cleanup legacy artifacts (default: enabled)
    --organize / --no-organize Reorganize files (default: enabled)
    --verbose                 Verbose output

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.orchestrators.system.system_integrity_orchestrator import SystemIntegrityOrchestrator


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/system-integrity.log', mode='a')
        ]
    )
    
    return logging.getLogger('SystemIntegrity')


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='CORTEX System Integrity Validator and Auto-Fixer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full integrity check with auto-fix (default)
  python scripts/cli_wrappers/system_integrity_wrapper.py

  # Check only, no fixes
  python scripts/cli_wrappers/system_integrity_wrapper.py --no-fix

  # Skip test execution
  python scripts/cli_wrappers/system_integrity_wrapper.py --no-tests

  # Cleanup only
  python scripts/cli_wrappers/system_integrity_wrapper.py --no-tests --no-docs
        """
    )
    
    parser.add_argument(
        '--fix',
        dest='fix_mode',
        action='store_true',
        default=True,
        help='Enable auto-fix (default)'
    )
    parser.add_argument(
        '--no-fix',
        dest='fix_mode',
        action='store_false',
        help='Disable auto-fix (report only)'
    )
    
    parser.add_argument(
        '--tests',
        dest='run_tests',
        action='store_true',
        default=True,
        help='Run test suite (default)'
    )
    parser.add_argument(
        '--no-tests',
        dest='run_tests',
        action='store_false',
        help='Skip test suite'
    )
    
    parser.add_argument(
        '--docs',
        dest='generate_docs',
        action='store_true',
        default=True,
        help='Generate missing docs (default)'
    )
    parser.add_argument(
        '--no-docs',
        dest='generate_docs',
        action='store_false',
        help='Skip doc generation'
    )
    
    parser.add_argument(
        '--legacy',
        dest='cleanup_legacy',
        action='store_true',
        default=True,
        help='Cleanup legacy artifacts (default)'
    )
    parser.add_argument(
        '--no-legacy',
        dest='cleanup_legacy',
        action='store_false',
        help='Skip legacy cleanup'
    )
    
    parser.add_argument(
        '--organize',
        dest='reorganize_files',
        action='store_true',
        default=True,
        help='Reorganize file structure (default)'
    )
    parser.add_argument(
        '--no-organize',
        dest='reorganize_files',
        action='store_false',
        help='Skip file reorganization'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    return parser.parse_args()


def print_summary(result: dict):
    """Print execution summary"""
    print("\n" + "="*80)
    print("CORTEX SYSTEM INTEGRITY CHECK COMPLETE")
    print("="*80)
    
    if result['success']:
        print("✅ Status: SUCCESS")
    else:
        print("❌ Status: FAILED")
    
    print()
    print(f"Issues Found:     {result['issues_found']}")
    print(f"Issues Fixed:     {result['issues_fixed']}")
    print(f"Issues Remaining: {result['issues_remaining']}")
    print()
    print(f"Tests Run:        {result.get('report').tests_run if result.get('report') else 0}")
    print(f"Tests Passed:     {result['tests_passed']}")
    print(f"Tests Failed:     {result['tests_failed']}")
    print()
    print(f"Docs Generated:   {result.get('report').docs_generated if result.get('report') else 0}")
    print(f"Files Relocated:  {result.get('report').files_relocated if result.get('report') else 0}")
    print(f"Files Deleted:    {result.get('report').files_deleted if result.get('report') else 0}")
    print(f"Links Fixed:      {result.get('report').links_fixed if result.get('report') else 0}")
    print()
    print(f"Execution Time:   {result['execution_time']:.2f} seconds")
    print("="*80)
    
    if result['is_complete']:
        print("\n🎉 All issues resolved! System integrity confirmed.")
    else:
        print(f"\n⚠️  {result['issues_remaining']} issues remaining. Check report for details.")
    
    print()


def main():
    """Main entry point"""
    args = parse_args()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    
    logger.info("="*80)
    logger.info("CORTEX System Integrity Orchestrator")
    logger.info("="*80)
    logger.info(f"Fix Mode: {args.fix_mode}")
    logger.info(f"Run Tests: {args.run_tests}")
    logger.info(f"Generate Docs: {args.generate_docs}")
    logger.info(f"Cleanup Legacy: {args.cleanup_legacy}")
    logger.info(f"Reorganize Files: {args.reorganize_files}")
    logger.info("="*80)
    logger.info("")
    
    # Create orchestrator config
    config = {
        'log_level': 'DEBUG' if args.verbose else 'INFO',
        'workspace_root': str(Path.cwd())
    }
    
    # Create orchestrator
    orchestrator = SystemIntegrityOrchestrator(config)
    
    # Execute
    context = {
        'fix_mode': args.fix_mode,
        'run_tests': args.run_tests,
        'generate_docs': args.generate_docs,
        'cleanup_legacy': args.cleanup_legacy,
        'reorganize_files': args.reorganize_files
    }
    
    try:
        result = orchestrator.execute(context)
        
        # Print summary
        print_summary(result)
        
        # Exit code
        if result['success'] and result['is_complete']:
            return 0
        elif result['success']:
            return 1  # Success but issues remain
        else:
            return 2  # Execution failed
            
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}")
        return 3


if __name__ == '__main__':
    sys.exit(main())
