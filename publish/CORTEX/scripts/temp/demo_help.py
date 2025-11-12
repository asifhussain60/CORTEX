"""
CORTEX Help System Demo

Shows all help formats for easy testing and viewing.

Usage:
    python demo_help.py
    python demo_help.py --format concise
    python demo_help.py --format detailed
    python demo_help.py --format category
    python demo_help.py --format quick
"""

import sys
from src.cortex_help import (
    show_help,
    get_quick_reference,
    handle_help_request,
    HelpFormat
)


def main():
    """Demo the help system."""
    if len(sys.argv) > 1 and sys.argv[1] == "--format":
        format_arg = sys.argv[2] if len(sys.argv) > 2 else "concise"
        
        if format_arg == "concise":
            print(show_help(HelpFormat.CONCISE))
        elif format_arg == "detailed":
            print(show_help(HelpFormat.DETAILED))
        elif format_arg == "category":
            print(show_help(HelpFormat.CATEGORY))
        elif format_arg == "quick":
            print(get_quick_reference())
        else:
            print(f"Unknown format: {format_arg}")
            print("Available: concise, detailed, category, quick")
    else:
        print("=" * 80)
        print("CONCISE HELP (Default)")
        print("=" * 80)
        print(show_help(HelpFormat.CONCISE))
        
        print("\n\n")
        print("=" * 80)
        print("QUICK REFERENCE (Ultra-Concise)")
        print("=" * 80)
        print(get_quick_reference())
        
        print("\n\n")
        print("=" * 80)
        print("CATEGORY OVERVIEW")
        print("=" * 80)
        print(show_help(HelpFormat.CATEGORY))
        
        print("\n\n")
        print("=" * 80)
        print("DETAILED HELP")
        print("=" * 80)
        print(show_help(HelpFormat.DETAILED))
        
        print("\n\n")
        print("=" * 80)
        print("INTELLIGENT HANDLING EXAMPLES")
        print("=" * 80)
        
        test_requests = [
            "show help",
            "quick reference",
            "detailed help",
            "show platform commands",
            "help"
        ]
        
        for request in test_requests:
            print(f"\nRequest: '{request}'")
            print("-" * 40)
            result = handle_help_request(request)
            # Show first 200 chars of response
            preview = result[:200] + "..." if len(result) > 200 else result
            print(preview)


if __name__ == "__main__":
    main()
