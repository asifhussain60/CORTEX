"""
CORTEX Align Command - Entry Point Wrapper

Simple wrapper to execute the lightweight align utility.
Replaces the broken SystemAlignmentOrchestrator with a minimal,
reliable validation system.

Usage:
    # From command line
    python3 -m src.operations.align                          # System health check
    python3 -m src.operations.align governance-tokens        # Token budget validation
    
    # From Python code
    from src.operations.align import run_align
    result = run_align()

Subcommands:
    (none)              - Run system alignment validation (default)
    governance-tokens   - Validate governance file token budgets

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.1
Status: PRODUCTION
"""

import sys
from typing import Dict, Any

from src.operations.modules.admin.align_utility import run_align_utility
from src.operations.modules.admin.governance_tokens import validate_token_budgets


def run_align() -> Dict[str, Any]:
    """
    Execute system alignment validation.
    
    This is the primary entry point for the 'align' command.
    It wraps the lightweight align_utility for clean integration.
    
    Returns:
        Dict with:
            - success (bool): True if system is healthy
            - message (str): Summary message
            - report_text (str): Full console output
            - report_data (dict): Structured validation data
    """
    return run_align_utility()


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
        description='CORTEX System Alignment Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # System health check
  python3 -m src.operations.align
  
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
        help='Subcommand to execute (default: system alignment)'
    )
    
    parser.add_argument(
        'action',
        nargs='?',
        default='validate',
        help='Action for subcommand (e.g., validate, report, analyze, optimize)'
    )
    
    args = parser.parse_args()
    
    # Route to appropriate handler
    if args.subcommand == 'governance-tokens':
        result = run_governance_tokens(args.action)
    else:
        # Default: system alignment validation
        result = run_align()
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()
