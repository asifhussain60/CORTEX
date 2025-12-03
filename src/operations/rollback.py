"""
Rollback CLI Wrapper

Command-line interface for rollback utility.
Provides formatted output and user confirmation for rollback operations.

Usage:
    python3 -m src.operations.rollback <checkpoint_id> [--dry-run] [--force] [--yes]

Version: 3.0.0
Author: Asif Hussain
"""

import sys
from pathlib import Path

# Add CORTEX root to path for imports
cortex_root = Path(__file__).resolve().parents[2]
if str(cortex_root) not in sys.path:
    sys.path.insert(0, str(cortex_root))

from src.operations.modules.git.rollback_utility import run_rollback_utility


def run_rollback(**kwargs) -> dict:
    """
    Wrapper for rollback utility - follows CORTEX operations pattern.
    
    Args:
        **kwargs: Arguments passed to run_rollback_utility
        
    Returns:
        Result dictionary from utility
    """
    result = run_rollback_utility(**kwargs)
    return {
        "success": result.success,
        "message": result.message,
        "checkpoint_id": result.checkpoint_id,
        "executed": result.executed,
        "safe": result.safe,
        "warning": result.warning,
        "details": result.details
    }


def main():
    """CLI entry point with formatted output."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX Rollback Utility - Rollback to previous checkpoint",
        epilog="⚠️  WARNING: Rollback will discard all changes after the checkpoint!"
    )
    parser.add_argument("checkpoint_id", help="Checkpoint SHA to rollback to")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    parser.add_argument("--force", action="store_true", help="⚠️  Bypass safety checks (dangerous!)")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔙 CORTEX Rollback Utility")
    print("=" * 60)
    
    if args.force:
        print("\n⚠️  FORCED MODE ENABLED - Safety checks will be bypassed!")
    
    if args.dry_run:
        print("\n📋 DRY-RUN MODE - No changes will be made")
    
    print(f"\nTarget Checkpoint: {args.checkpoint_id[:8] if len(args.checkpoint_id) >= 8 else args.checkpoint_id}")
    print("=" * 60)
    
    # Execute utility
    result = run_rollback(
        checkpoint_id=args.checkpoint_id,
        dry_run=args.dry_run,
        force=args.force,
        skip_confirmation=args.yes
    )
    
    # Display results
    print(f"\nStatus: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Message: {result['message']}")
    
    if result.get("checkpoint_id"):
        print(f"Checkpoint: {result['checkpoint_id'][:8]}")
    
    if result.get("executed") is not None:
        print(f"Executed: {'Yes' if result['executed'] else 'No (preview/cancelled)'}")
    
    if result.get("safe") is not None and not result["safe"]:
        print(f"\n⚠️  Safety: UNSAFE - {result.get('warning', 'Unknown issue')}")
    
    if result.get("details"):
        print(f"\nDetails:\n{'-' * 60}")
        print(result["details"])
        print("-" * 60)
    
    if not result["success"] and result.get("warning"):
        print(f"\n💡 Tip: Use --force to override safety checks (⚠️  will lose uncommitted changes!)")
    
    print("\n" + "=" * 60)
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
