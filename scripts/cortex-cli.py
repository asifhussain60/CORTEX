#!/usr/bin/env python3
"""
CORTEX CLI Bridge - Universal MCP Orchestrator Invocation.

Enables GitHub Copilot to invoke autonomous Python orchestrators via run_in_terminal.
This script bridges the gap between Copilot's terminal access and Python MCP infrastructure.

Usage:
    python scripts/cortex-cli.py <orchestrator_name> "<user_request>" [--option key=value]

Examples:
    # Planning orchestrator
    python scripts/cortex-cli.py planning_system "create plan for database migration"
    
    # Master orchestrator with continuation
    python scripts/cortex-cli.py master_orchestrator "continue with plan" --option phase=3
    
    # Cleanup orchestrator
    python scripts/cortex-cli.py cleanup_orchestrator_v2 "clean cache files" --option mode=cache
    
    # ADO orchestrator
    python scripts/cortex-cli.py ado_orchestrator_v2 "create user story for login feature"

Architecture:
    GitHub Copilot (Intent Router)
        ↓ (via run_in_terminal)
    cortex-cli.py (CLI Bridge) ← YOU ARE HERE
        ↓ (imports)
    src/mcp/tools/invoke_orchestrator.py (Universal Invocation Tool)
        ↓ (uses)
    src/mcp/registry.py (Orchestrator Registry)
        ↓ (loads)
    Autonomous Python Orchestrators (7,067 lines of code activated)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
Version: 1.0.0
Created: January 3, 2026 (Phase 1.5)
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.mcp.tools.invoke_orchestrator import invoke_orchestrator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_options(option_args: list[str]) -> Dict[str, Any]:
    """
    Parse --option key=value arguments into dictionary.
    
    Args:
        option_args: List of "key=value" strings
    
    Returns:
        Dictionary of parsed options
    
    Examples:
        ["mode=cache", "dry_run=true"] → {"mode": "cache", "dry_run": True}
        ["phase=3", "verbose=false"] → {"phase": 3, "verbose": False}
    """
    options = {}
    
    for arg in option_args:
        if '=' not in arg:
            logger.warning(f"Skipping invalid option format: {arg} (expected key=value)")
            continue
        
        key, value = arg.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        # Type coercion
        if value.lower() == 'true':
            options[key] = True
        elif value.lower() == 'false':
            options[key] = False
        elif value.isdigit():
            options[key] = int(value)
        elif value.replace('.', '', 1).isdigit():
            options[key] = float(value)
        else:
            options[key] = value
    
    return options


def format_output(result: Dict[str, Any]) -> str:
    """
    Format orchestrator result for terminal display.
    
    Args:
        result: Result dictionary from invoke_orchestrator
    
    Returns:
        Formatted string for terminal output
    """
    lines = []
    lines.append("=" * 80)
    lines.append(f"🧠 CORTEX Orchestrator Execution: {result.get('orchestrator', 'unknown')}")
    lines.append("=" * 80)
    lines.append("")
    
    status = result.get('status', 'unknown')
    if status == 'success':
        lines.append("✅ STATUS: SUCCESS")
    elif status == 'error':
        lines.append("❌ STATUS: ERROR")
    else:
        lines.append(f"⚠️ STATUS: {status.upper()}")
    
    lines.append("")
    
    # Execution time
    exec_time = result.get('execution_time')
    if exec_time:
        lines.append(f"⏱️  Execution Time: {exec_time:.2f}s")
        lines.append("")
    
    # Summary
    summary = result.get('summary')
    if summary:
        lines.append("📋 SUMMARY:")
        lines.append(summary)
        lines.append("")
    
    # Progress
    progress = result.get('progress')
    if progress:
        lines.append("📊 PROGRESS:")
        lines.append(json.dumps(progress, indent=2))
        lines.append("")
    
    # Artifacts
    artifacts = result.get('artifacts', [])
    if artifacts:
        lines.append("📦 ARTIFACTS GENERATED:")
        for artifact in artifacts:
            lines.append(f"  • {artifact}")
        lines.append("")
    
    # Error details
    if status == 'error':
        error = result.get('error', 'Unknown error')
        lines.append("❌ ERROR DETAILS:")
        lines.append(error)
        lines.append("")
    
    # Continuation prompt
    continuation = result.get('continuation_prompt')
    if continuation:
        lines.append("🔄 CONTINUATION PROMPT:")
        lines.append(continuation)
        lines.append("")
    
    lines.append("=" * 80)
    
    return "\n".join(lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CORTEX CLI Bridge - Universal MCP Orchestrator Invocation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Planning orchestrator
  python scripts/cortex-cli.py planning_system "create plan for database migration"
  
  # Master orchestrator with continuation
  python scripts/cortex-cli.py master_orchestrator "continue with plan" --option phase=3
  
  # Cleanup orchestrator with mode
  python scripts/cortex-cli.py cleanup_orchestrator_v2 "clean cache files" --option mode=cache
  
  # ADO orchestrator
  python scripts/cortex-cli.py ado_orchestrator_v2 "create user story for login feature"

For more information: See .github/prompts/CORTEX.prompt.md
        """
    )
    
    parser.add_argument(
        'orchestrator_name',
        help='Name of orchestrator to invoke (e.g., planning_system, cleanup_orchestrator_v2)'
    )
    
    parser.add_argument(
        'user_request',
        help='User request in natural language (quoted string)'
    )
    
    parser.add_argument(
        '--option',
        action='append',
        default=[],
        dest='options',
        metavar='KEY=VALUE',
        help='Execution options as key=value pairs (repeatable)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output raw JSON instead of formatted text'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Configure debug logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Parse options
    options = parse_options(args.options)
    logger.debug(f"Parsed options: {options}")
    
    try:
        # Invoke orchestrator via MCP tool
        logger.info(f"Invoking orchestrator: {args.orchestrator_name}")
        logger.info(f"User request: {args.user_request}")
        
        result = invoke_orchestrator(
            orchestrator_name=args.orchestrator_name,
            user_request=args.user_request,
            options=options if options else None
        )
        
        # Output result
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(format_output(result))
        
        # Exit code based on status
        if result.get('status') == 'success':
            sys.exit(0)
        else:
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"CLI bridge error: {str(e)}", exc_info=args.debug)
        
        error_result = {
            "status": "error",
            "orchestrator": args.orchestrator_name,
            "error": str(e),
            "error_type": type(e).__name__
        }
        
        if args.json:
            print(json.dumps(error_result, indent=2))
        else:
            print("=" * 80)
            print("❌ CORTEX CLI BRIDGE ERROR")
            print("=" * 80)
            print(f"\nOrchestrator: {args.orchestrator_name}")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print("\nFor debug details, run with --debug flag")
            print("=" * 80)
        
        sys.exit(1)


if __name__ == '__main__':
    main()
