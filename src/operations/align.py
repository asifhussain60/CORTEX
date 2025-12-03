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
Version: 2.0
Status: PRODUCTION (Enhanced)
"""

import sys
from pathlib import Path
from typing import Dict, Any

from src.operations.modules.realignment.realignment_utility import align_system_v2
from src.operations.modules.admin.governance_tokens import validate_token_budgets


def run_align(auto_fix: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    """
    Execute CORTEX Align v2.0 - Holistic system alignment.
    
    This is the MOST CRUCIAL validation step. When user says '/CORTEX align',
    this function runs comprehensive checks to ensure CORTEX is fully operational.
    
    Features:
    - Feature registration validation (all operations in cortex-operations.yaml)
    - Auto-discovery and registration of new features
    - Intent router coverage check (all operations have triggers)
    - Response template validation (all operations have templates)
    - Documentation alignment (docs match implementation)
    - Obsolete code detection and cleanup
    - Module import health check
    - CORTEX.prompt.md optimization validation
    
    Args:
        auto_fix: Automatically fix issues without prompting (default: False)
        dry_run: Preview changes without applying (default: False)
    
    Returns:
        Dict with:
            - success (bool): True if system is healthy
            - checks (dict): Results from all 6 checks
            - fixes_applied (list): List of fixes applied
            - warnings (list): Warnings found
            - errors (list): Errors found
            - report_path (str): Path to detailed report
    """
    # Detect CORTEX root
    cortex_root = Path(__file__).resolve().parents[2]
    project_root = cortex_root
    
    # Run align v2.0
    return align_system_v2(
        project_root=project_root,
        cortex_root=cortex_root,
        auto_fix=auto_fix,
        dry_run=dry_run
    )



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
    
    args = parser.parse_args()
    
    # Route to appropriate handler
    if args.subcommand == 'governance-tokens':
        result = run_governance_tokens(args.action)
    else:
        # Default: CORTEX Align v2.0
        result = run_align(
            auto_fix=args.auto_fix,
            dry_run=args.dry_run
        )
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)



if __name__ == "__main__":
    main()
