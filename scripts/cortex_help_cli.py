#!/usr/bin/env python3
"""
CORTEX Help CLI

Quick command-line access to CORTEX help system.

Usage:
    cortex-help                  # Show concise help
    cortex-help --quick          # Ultra-concise quick reference
    cortex-help --detailed       # Full detailed help
    cortex-help --category       # Help organized by category
    cortex-help platform         # Platform commands only
    cortex-help session          # Session commands only

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.cortex_help import (
    show_help,
    get_quick_reference,
    handle_help_request,
    HelpFormat
)
from src.plugins.command_registry import CommandCategory


def main():
    """CLI entry point for CORTEX help."""
    parser = argparse.ArgumentParser(
        description="CORTEX Help System - Quick command reference",
        epilog="Natural language works everywhere! Commands are optional shortcuts."
    )
    
    parser.add_argument(
        "category",
        nargs="?",
        help="Filter by category: platform, session, workflow, documentation, testing, maintenance"
    )
    
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Show ultra-concise quick reference"
    )
    
    parser.add_argument(
        "--detailed", "-d",
        action="store_true",
        help="Show detailed help with examples"
    )
    
    parser.add_argument(
        "--category", "-c",
        action="store_true",
        help="Show help organized by category"
    )
    
    args = parser.parse_args()
    
    # Determine format
    if args.quick:
        print(get_quick_reference())
    elif args.detailed:
        if args.category:
            cat = _parse_category(args.category)
            print(show_help(HelpFormat.DETAILED, cat))
        else:
            print(show_help(HelpFormat.DETAILED))
    elif args.category or (hasattr(args, 'category') and not args.category):
        print(show_help(HelpFormat.CATEGORY))
    elif args.category:
        # Filter by category
        cat = _parse_category(args.category)
        if cat:
            print(show_help(HelpFormat.CONCISE, cat))
        else:
            print(f"Unknown category: {args.category}")
            print("Available: platform, session, workflow, documentation, testing, maintenance")
            sys.exit(1)
    else:
        # Default: concise help
        print(show_help(HelpFormat.CONCISE))


def _parse_category(category_str: str) -> CommandCategory:
    """Parse category string to enum."""
    if not category_str:
        return None
    
    category_map = {
        'platform': CommandCategory.PLATFORM,
        'workflow': CommandCategory.WORKFLOW,
        'session': CommandCategory.SESSION,
        'documentation': CommandCategory.DOCUMENTATION,
        'docs': CommandCategory.DOCUMENTATION,
        'testing': CommandCategory.TESTING,
        'test': CommandCategory.TESTING,
        'maintenance': CommandCategory.MAINTENANCE,
        'maint': CommandCategory.MAINTENANCE,
        'extension': CommandCategory.EXTENSION,
        'ext': CommandCategory.EXTENSION,
        'custom': CommandCategory.CUSTOM
    }
    
    return category_map.get(category_str.lower())


if __name__ == "__main__":
    main()
