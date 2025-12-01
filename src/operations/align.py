"""
CORTEX Align Command - Entry Point Wrapper

Simple wrapper to execute the lightweight align utility.
Replaces the broken SystemAlignmentOrchestrator with a minimal,
reliable validation system.

Usage:
    # From command line
    python3 -m src.operations.align
    
    # From Python code
    from src.operations.align import run_align
    result = run_align()

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
Status: PRODUCTION
"""

import sys
from typing import Dict, Any

from src.operations.modules.admin.align_utility import run_align_utility


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


def main():
    """CLI entry point for direct execution."""
    result = run_align()
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()
