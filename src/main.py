"""
CORTEX CLI Entry Point

Command-line interface for CORTEX AI Assistant.

Usage:
    # Interactive mode
    python -m src.main
    
    # Single command
    python -m src.main "help"
    python -m src.main "create tests for auth.py"
    
    # Setup mode
    python -m src.main --setup
    python -m src.main --setup --repo /path/to/repo
    
    # Format options
    python -m src.main "status" --format json
    python -m src.main "help" --format markdown
    
    # Verbose logging
    python -m src.main "implement feature" --verbose

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from src.entry_point.cortex_entry import CortexEntry
from src.config import config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CORTEX AI Assistant - Natural Language Development Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cortex                              # Interactive mode
  cortex "help"                       # Show help
  cortex "create tests for auth.py"  # Single command
  cortex --setup                      # Run setup wizard
  cortex "status" --format json      # JSON output
  cortex --verbose "implement auth"  # Verbose logging
        """
    )
    
    parser.add_argument(
        "message",
        nargs="?",
        help="User message/command (omit for interactive mode)"
    )
    
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run CORTEX setup wizard"
    )
    
    parser.add_argument(
        "--repo",
        type=str,
        help="Repository path for setup (default: current directory)"
    )
    
    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--brain",
        type=str,
        help="Custom brain path (default: auto-detected)"
    )
    
    args = parser.parse_args()
    
    # Initialize CORTEX
    try:
        entry = CortexEntry(
            brain_path=args.brain,
            enable_logging=args.verbose
        )
    except Exception as e:
        print(f"❌ Failed to initialize CORTEX: {e}")
        return 1
    
    # Handle setup mode
    if args.setup:
        print("🧠 CORTEX Setup Wizard\n")
        results = entry.setup(repo_path=args.repo, verbose=True)
        return 0 if results.get("success") else 1
    
    # Handle single command
    if args.message:
        try:
            response = entry.process(
                args.message,
                resume_session=True,
                format_type=args.format
            )
            print(response)
            return 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    # Interactive mode
    print("🧠 CORTEX Interactive Mode")
    print("=" * 60)
    print("Enter your requests in natural language.")
    print("Type 'exit', 'quit', or press Ctrl+C to exit.")
    print("Type 'help' for available commands.")
    print("=" * 60)
    print()
    
    try:
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("\n👋 Goodbye!")
                    break
                
                # Process message
                response = entry.process(
                    user_input,
                    resume_session=True,
                    format_type=args.format
                )
                
                print(f"\n{response}\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
    
    finally:
        # Cleanup
        entry.cleanup()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
