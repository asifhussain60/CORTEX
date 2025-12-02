"""
TDD CLI - Test-Driven Development Workflow

Command-line interface for TDD utility operations.

Commands:
  start     - Start new TDD session
  test      - Run tests
  pass      - Transition to GREEN phase (tests passing)
  refactor  - Transition to REFACTOR phase
  complete  - Complete TDD session
  status    - Get current session status
  skeleton  - Generate test skeleton

Usage:
  python -m src.operations.tdd start "Feature Name" tests/test_feature.py src/feature.py
  python -m src.operations.tdd test tests/test_feature.py
  python -m src.operations.tdd pass <session-id>
  python -m src.operations.tdd refactor <session-id>
  python -m src.operations.tdd complete <session-id>
  python -m src.operations.tdd status <session-id>
  python -m src.operations.tdd skeleton "Feature Name" tests/test_feature.py src/feature.py

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Import TDD utility operations
from src.operations.modules.tdd.tdd_utility import (
    start_tdd_session,
    run_tests,
    transition_phase,
    get_session_status,
    generate_test_skeleton,
    update_session_metrics,
    complete_session,
    TDDPhase,
    TDDResult
)


def format_result(result: TDDResult, json_output: bool = False) -> str:
    """
    Format TDD result for display.
    
    Args:
        result: TDDResult to format
        json_output: Whether to output as JSON
        
    Returns:
        Formatted string
    """
    if json_output:
        return json.dumps({
            "success": result.success,
            "message": result.message,
            "phase": result.phase.value,
            "test_passed": result.test_passed,
            "details": result.details,
            "errors": result.errors
        }, indent=2)
    
    # Text output
    output = []
    
    # Status indicator
    if result.success:
        output.append(f"✅ {result.message}")
    else:
        output.append(f"❌ {result.message}")
    
    # Phase indicator
    phase_icons = {
        TDDPhase.IDLE: "⚪",
        TDDPhase.RED: "🔴",
        TDDPhase.GREEN: "🟢",
        TDDPhase.REFACTOR: "🔵",
        TDDPhase.COMPLETE: "✅"
    }
    icon = phase_icons.get(result.phase, "⚪")
    output.append(f"\nPhase: {icon} {result.phase.value.upper()}")
    
    # Test results
    if result.test_passed is not None:
        test_icon = "✅" if result.test_passed else "❌"
        output.append(f"Tests: {test_icon} {'Passed' if result.test_passed else 'Failed'}")
    
    # Details
    if result.details:
        output.append(f"\nDetails:\n{result.details}")
    
    # Errors
    if result.errors:
        output.append(f"\n❌ Errors:")
        for error in result.errors:
            output.append(f"  - {error}")
    
    # Test output (if available)
    if result.test_output:
        output.append(f"\n{'=' * 60}")
        output.append("Test Output:")
        output.append('=' * 60)
        output.append(result.test_output)
    
    return "\n".join(output)


def cmd_start(args: argparse.Namespace) -> int:
    """Start TDD session command."""
    test_file = Path(args.test_file).resolve()
    impl_file = Path(args.impl_file).resolve()
    
    result = start_tdd_session(
        feature_name=args.feature_name,
        test_file=test_file,
        impl_file=impl_file
    )
    
    print(format_result(result, args.json))
    return 0 if result.success else 1


def cmd_test(args: argparse.Namespace) -> int:
    """Run tests command."""
    test_file = Path(args.test_file).resolve()
    
    result = run_tests(
        test_file=test_file,
        test_name=args.test_name
    )
    
    print(format_result(result, args.json))
    return 0 if result.success else 1


def cmd_pass(args: argparse.Namespace) -> int:
    """Transition to GREEN phase command."""
    result = transition_phase(
        session_id=args.session_id,
        target_phase=TDDPhase.GREEN
    )
    
    print(format_result(result, args.json))
    return 0 if result.success else 1


def cmd_refactor(args: argparse.Namespace) -> int:
    """Transition to REFACTOR phase command."""
    result = transition_phase(
        session_id=args.session_id,
        target_phase=TDDPhase.REFACTOR
    )
    
    print(format_result(result, args.json))
    return 0 if result.success else 1


def cmd_complete(args: argparse.Namespace) -> int:
    """Complete session command."""
    result = complete_session(args.session_id)
    
    print(format_result(result, args.json))
    return 0 if result.success else 1


def cmd_status(args: argparse.Namespace) -> int:
    """Get session status command."""
    result = get_session_status(args.session_id)
    
    print(format_result(result, args.json))
    return 0 if result.success else 1


def cmd_skeleton(args: argparse.Namespace) -> int:
    """Generate test skeleton command."""
    test_file = Path(args.test_file).resolve()
    impl_file = Path(args.impl_file).resolve()
    
    result = generate_test_skeleton(
        feature_name=args.feature_name,
        test_file=test_file,
        impl_file=impl_file
    )
    
    print(format_result(result, args.json))
    return 0 if result.success else 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="TDD CLI - Test-Driven Development Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="TDD command")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start new TDD session")
    start_parser.add_argument("feature_name", help="Feature name")
    start_parser.add_argument("test_file", help="Test file path")
    start_parser.add_argument("impl_file", help="Implementation file path")
    start_parser.set_defaults(func=cmd_start)
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("test_file", help="Test file path")
    test_parser.add_argument("--test-name", help="Specific test to run")
    test_parser.set_defaults(func=cmd_test)
    
    # Pass command
    pass_parser = subparsers.add_parser("pass", help="Transition to GREEN phase")
    pass_parser.add_argument("session_id", help="Session ID")
    pass_parser.set_defaults(func=cmd_pass)
    
    # Refactor command
    refactor_parser = subparsers.add_parser("refactor", help="Transition to REFACTOR phase")
    refactor_parser.add_argument("session_id", help="Session ID")
    refactor_parser.set_defaults(func=cmd_refactor)
    
    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Complete TDD session")
    complete_parser.add_argument("session_id", help="Session ID")
    complete_parser.set_defaults(func=cmd_complete)
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Get session status")
    status_parser.add_argument("session_id", help="Session ID")
    status_parser.set_defaults(func=cmd_status)
    
    # Skeleton command
    skeleton_parser = subparsers.add_parser("skeleton", help="Generate test skeleton")
    skeleton_parser.add_argument("feature_name", help="Feature name")
    skeleton_parser.add_argument("test_file", help="Test file path")
    skeleton_parser.add_argument("impl_file", help="Implementation file path")
    skeleton_parser.set_defaults(func=cmd_skeleton)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
