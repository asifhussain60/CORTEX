"""
Git Checkpoint CLI Wrapper

Command-line interface for git checkpoint utility.
Provides formatted output for checkpoint creation and listing.

Usage:
    python3 -m src.operations.git_checkpoint create [--session SESSION] [--phase PHASE] [--message MESSAGE]
    python3 -m src.operations.git_checkpoint list [--all]

Version: 3.0.0
Author: Asif Hussain
"""

import sys
from pathlib import Path

# Add CORTEX root to path for imports
cortex_root = Path(__file__).resolve().parents[2]
if str(cortex_root) not in sys.path:
    sys.path.insert(0, str(cortex_root))

from src.operations.modules.git.git_checkpoint_utility import run_checkpoint_utility
from datetime import datetime


def run_checkpoint(**kwargs) -> dict:
    """
    Wrapper for checkpoint utility - follows CORTEX operations pattern.
    
    Args:
        **kwargs: Arguments passed to run_checkpoint_utility
        
    Returns:
        Result dictionary from utility
    """
    result = run_checkpoint_utility(**kwargs)
    return {
        "success": result.success,
        "message": result.message,
        "checkpoint_id": result.checkpoint_id,
        "checkpoint_count": result.checkpoint_count,
        "checkpoints": result.checkpoints,
        "details": result.details
    }


def main():
    """CLI entry point with formatted output."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Git Checkpoint Utility")
    parser.add_argument("action", choices=["create", "list"], help="Action to perform")
    parser.add_argument("--session", help="TDD session ID (for create)")
    parser.add_argument("--phase", help="Current phase: RED, GREEN, or REFACTOR (for create)")
    parser.add_argument("--message", help="Custom checkpoint message (for create)")
    parser.add_argument("--all", action="store_true", help="Show all checkpoints including expired (for list)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"🔖 CORTEX Git Checkpoint - {args.action.upper()}")
    print("=" * 60)
    
    # Build kwargs for utility
    kwargs = {"action": args.action}
    
    if args.action == "create":
        if args.session:
            kwargs["session_id"] = args.session
        if args.phase:
            kwargs["phase"] = args.phase
        if args.message:
            kwargs["message"] = args.message
    elif args.action == "list":
        kwargs["list_all"] = args.all
    
    # Execute utility
    result = run_checkpoint(**kwargs)
    
    # Display results
    print(f"\nStatus: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Message: {result['message']}")
    
    if result.get("checkpoint_id"):
        print(f"Checkpoint ID: {result['checkpoint_id'][:8]}")
    
    if result.get("checkpoint_count") is not None:
        print(f"Total Checkpoints: {result['checkpoint_count']}")
    
    if result.get("details"):
        print(f"\nDetails:\n{result['details']}")
    
    if result.get("checkpoints"):
        print("\n📋 Available Checkpoints:")
        print("-" * 60)
        for i, cp in enumerate(result["checkpoints"][:10], 1):  # Show last 10
            timestamp = datetime.fromisoformat(cp["timestamp"])
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{i:2d}. {cp['checkpoint_id'][:8]} | {cp['phase']:10s} | {time_str} | {cp['branch']}")
            if cp.get("message"):
                print(f"    └─ {cp['message']}")
        
        if len(result["checkpoints"]) > 10:
            print(f"\n... and {len(result['checkpoints']) - 10} more checkpoint(s)")
    
    print("=" * 60)
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
