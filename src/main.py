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

Performance Optimization:
    - Fast-path routing for simple commands (help, version, status)
    - Lazy loading of heavy dependencies (tiers, agents, orchestrators)
    - Component caching for repeated invocations
    - Target: <50ms for fast commands, <1.7s for full initialization

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import argparse
import time
from pathlib import Path
from typing import Optional

# Fast-path handler loaded eagerly (lightweight)
from src.entry_point.fast_commands import FastCommandHandler, is_fast_command

# CortexEntry loaded lazily (heavy)
from src.utils.lazy_loader import lazy_import

_entry_module = lazy_import('src.entry_point.cortex_entry')


def main():
    """Main CLI entry point with performance optimization."""
    start_time = time.perf_counter()
    
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
    
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Show performance profiling information"
    )
    
    args = parser.parse_args()
    
    # FAST PATH: Handle simple commands without full initialization
    if args.message and not args.setup and is_fast_command(args.message):
        try:
            handler = FastCommandHandler(brain_path=Path(args.brain) if args.brain else None)
            response = handler.handle(args.message, format_type=args.format)
            print(response)
            
            if args.profile:
                elapsed = (time.perf_counter() - start_time) * 1000
                print(f"\n⚡ Fast-path response time: {elapsed:.2f}ms")
            
            return 0
        except Exception as e:
            print(f"[ERROR] Fast-path handler failed: {e}")
            # Fall through to full initialization
    
    # FULL PATH: Complex operations require full CortexEntry
    try:
        CortexEntry = _entry_module.CortexEntry
        entry = CortexEntry(
            brain_path=args.brain,
            enable_logging=args.verbose
        )
        
        if args.profile:
            init_time = (time.perf_counter() - start_time) * 1000
            print(f"⚙️ Initialization time: {init_time:.2f}ms")
    except Exception as e:
        print(f"[ERROR] Failed to initialize CORTEX: {e}")
        return 1
    
    # Handle setup mode
    if args.setup:
        print("CORTEX Setup Wizard\n")
        results = entry.setup(repo_path=args.repo, verbose=True)
        
        if args.profile:
            elapsed = (time.perf_counter() - start_time) * 1000
            print(f"\n⚙️ Total time: {elapsed:.2f}ms")
        
        return 0 if results.get("success") else 1
    
    # Handle single command
    if args.message:
        try:
            command_start = time.perf_counter()
            response = entry.process(
                args.message,
                resume_session=True,
                format_type=args.format
            )
            print(response)
            
            if args.profile:
                command_time = (time.perf_counter() - command_start) * 1000
                total_time = (time.perf_counter() - start_time) * 1000
                print(f"\n⚙️ Command time: {command_time:.2f}ms")
                print(f"⚙️ Total time: {total_time:.2f}ms")
            
            return 0
        except Exception as e:
            print(f"[ERROR] {e}")
            return 1
    
    # Interactive mode
    print("CORTEX Interactive Mode")
    print("=" * 60)
    print("Enter your requests in natural language.")
    print("Type 'exit', 'quit', or press Ctrl+C to exit.")
    print("Type 'help' for available commands.")
    print("=" * 60)
    print()
    
    if args.profile:
        startup_time = (time.perf_counter() - start_time) * 1000
        print(f"⚙️ Startup time: {startup_time:.2f}ms\n")
    
    try:
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("\nGoodbye!")
                    break
                
                command_start = time.perf_counter()
                response = entry.process(
                    user_input,
                    resume_session=True,
                    format_type=args.format
                )
                
                print(f"\n{response}\n")
                
                if args.profile:
                    command_time = (time.perf_counter() - command_start) * 1000
                    print(f"⚙️ Response time: {command_time:.2f}ms\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except EOFError:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\n[ERROR] {e}\n")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
    
    finally:
        # Cleanup
        entry.cleanup()
        
        if args.profile:
            # Show lazy loading stats
            from src.utils.lazy_loader import get_load_stats
            stats = get_load_stats()
            if stats['modules_loaded'] > 0:
                print("\n" + "="*60)
                print(f"📊 Loaded {stats['modules_loaded']} modules")
                print(f"⚡ Total load time: {stats['total_load_time']:.2f}ms")
                print(f"⚡ Average: {stats['avg_load_time']:.2f}ms")
                print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
