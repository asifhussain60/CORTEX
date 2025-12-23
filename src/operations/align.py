"""
CORTEX Align v2.0 Command - Entry Point Wrapper

Enhanced system alignment with intelligent maintenance capabilities:
- Feature registration validation
- Auto-discovery and registration
- Intent router coverage check
- Response template validation
- Documentation alignment
- Obsolete code detection
- Module import health check
- CORTEX.prompt.md optimization validation

Usage:
    # From command line
    python3 -m src.operations.align                          # Full system alignment v2.0
    python3 -m src.operations.align --auto-fix               # Auto-fix issues
    python3 -m src.operations.align --dry-run                # Preview changes
    python3 -m src.operations.align governance-tokens        # Token budget validation
    
    # From Python code
    from src.operations.align import run_align
    result = run_align()

Subcommands:
    (none)              - Run CORTEX Align v2.0 holistic system check (default)
    governance-tokens   - Validate governance file token budgets

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 3.0
Status: PRODUCTION (Enhanced - CORTEX v3.9 Compatible)
"""

import sys
from pathlib import Path
from typing import Dict, Any

from src.operations.modules.realignment.realignment_utility import align_system
from src.operations.modules.admin.governance_tokens import validate_token_budgets


def run_align(
    auto_fix: bool = False, 
    dry_run: bool = False,
    force_full: bool = False,
    quick_mode: bool = False
) -> Dict[str, Any]:
    """
    Execute CORTEX Align v3.2 - Holistic system alignment with incremental support.
    
    This is the MOST CRUCIAL validation step. When user says '/CORTEX align',
    this function runs comprehensive checks to ensure CORTEX is fully operational.
    
    Features (v3.2):
    - Incremental validation (only check changed features)
    - File change detection via SHA256 checksums
    - Auto-discovery and wiring validation for new features
    - Admin vs User context detection
    - Performance metrics tracking
    - Feature registration validation (all operations in cortex-operations.yaml)
    - Intent router coverage check (all operations have triggers)
    - Response template validation (all operations have templates)
    - Documentation alignment (docs match implementation)
    - Obsolete code detection and cleanup
    - Module import health check
    - CORTEX.prompt.md optimization validation
    
    Args:
        auto_fix: Automatically fix issues without prompting (default: False)
        dry_run: Preview changes without applying (default: False)
        force_full: Force full scan even if incremental is possible (default: False)
        quick_mode: Infrastructure checks only, skip feature validation (default: False)
    
    Returns:
        Dict with:
            - success (bool): True if system is healthy
            - checks (dict): Results from all checks
            - fixes_applied (list): List of fixes applied
            - warnings (list): Warnings found
            - errors (list): Errors found
            - report_path (str): Path to detailed report
            - performance (dict): Performance metrics
    """
    # Detect CORTEX root
    cortex_root = Path(__file__).resolve().parents[2]
    project_root = cortex_root
    
    # Determine which align system to use based on flags
    if force_full or quick_mode:
        # Use lightweight align utility with incremental support
        from src.operations.modules.admin.align_utility import run_align_utility
        return run_align_utility(force_full=force_full, quick_mode=quick_mode)
    else:
        # Use full align v2.0 system (realignment with auto-fix)
        result = align_system(
            project_root=project_root,
            cortex_root=cortex_root,
            auto_fix=auto_fix,
            dry_run=dry_run
        )
        
        # Add performance metrics if not present
        if 'performance' not in result:
            result['performance'] = {
                'features_checked': 0,
                'features_skipped': 0,
                'duration_seconds': 0.0
            }
        
        return result



def run_governance_tokens(command: str = 'validate') -> Dict[str, Any]:
    """
    Execute governance token budget validation.
    
    Validates that CORTEX governance files stay within token budgets
    to prevent GitHub Copilot premature summarization.
    
    Args:
        command: Subcommand ('validate', 'report', 'analyze', 'optimize')
    
    Returns:
        Dict with:
            - success (bool): True if all files within budget
            - message (str): Summary message
            - report_text (str): Full console output
            - report_data (dict): Structured validation data
    """
    # Currently only 'validate' and 'report' are implemented
    # 'analyze' and 'optimize' coming soon
    if command in ['validate', 'report']:
        return validate_token_budgets()
    else:
        return {
            'success': False,
            'message': f"Subcommand '{command}' not yet implemented",
            'report_text': f"❌ '{command}' command coming soon",
            'report_data': None
        }


def main():
    """CLI entry point for direct execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='CORTEX Align v2.0 - Holistic System Alignment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full system alignment check
  python3 -m src.operations.align
  
  # Auto-fix issues without prompting
  python3 -m src.operations.align --auto-fix
  
  # Preview changes (dry run)
  python3 -m src.operations.align --dry-run
  
  # Governance token validation
  python3 -m src.operations.align governance-tokens
  python3 -m src.operations.align governance-tokens validate
  python3 -m src.operations.align governance-tokens report
"""
    )
    
    parser.add_argument(
        'subcommand',
        nargs='?',
        default=None,
        choices=['governance-tokens'],
        help='Subcommand to execute (default: system alignment v2.0)'
    )
    
    parser.add_argument(
        'action',
        nargs='?',
        default='validate',
        help='Action for subcommand (e.g., validate, report, analyze, optimize)'
    )
    
    parser.add_argument(
        '--auto-fix',
        action='store_true',
        help='Automatically fix issues without prompting'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )
    
    parser.add_argument(
        '--full',
        action='store_true',
        help='Force full scan even if incremental is possible'
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Infrastructure checks only, skip feature validation'
    )
    
    args = parser.parse_args()
    
    # Route to appropriate handler
    if args.subcommand == 'governance-tokens':
        result = run_governance_tokens(args.action)
    else:
        # Default: CORTEX Align v3.2
        result = run_align(
            auto_fix=args.auto_fix,
            dry_run=args.dry_run,
            force_full=args.full,
            quick_mode=args.quick
        )
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)



if __name__ == "__main__":
    main()
