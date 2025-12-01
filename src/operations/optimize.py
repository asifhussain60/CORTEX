"""
CORTEX Optimize Entry Point

Unified CLI wrapper for all optimization operations:
- Token optimization (governance files)
- File system optimization (organization/archives/cache)
- Database consolidation

Usage:
    optimize tokens <command>       # Token optimization
    optimize files <target>         # File system optimization
    optimize all                    # Everything

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from operations.optimize_operation import OptimizeOperation
from operations.optimize_tokens import TokenOptimizer, safe_print


def run_optimize(target: str = 'all', aggressive: bool = False, dry_run: bool = False):
    """
    Run CORTEX comprehensive optimize operation.
    
    Args:
        target: What to optimize (organization/archives/cortex/cache/consolidation/all)
        aggressive: Use aggressive optimization for databases
        dry_run: Preview changes without executing
    
    Returns:
        Dict with success, message, and optimization results
    """
    optimizer = OptimizeOperation()
    result = optimizer.execute(target=target, aggressive=aggressive, dry_run=dry_run)
    
    return {
        "success": result.success,
        "message": result.message,
        "data": result.data,
    }


def run_token_optimization(command: str):
    """
    Run token optimization command.
    
    Args:
        command: Token optimization command (status/auto/quick/full/rollback/validate)
    """
    optimizer = TokenOptimizer(dry_run=False)
    
    if command == "status":
        optimizer.show_status()
    elif command == "auto":
        optimizer.optimize_auto()
    elif command == "quick":
        optimizer.optimize_quick()
    elif command == "full":
        optimizer.optimize_full()
    elif command == "rollback":
        optimizer.rollback_last()
    elif command == "validate":
        from operations.modules.admin.governance_tokens import validate_token_budgets
        result = validate_token_budgets()
        safe_print(result["report_text"])
    else:
        safe_print(f"❌ Unknown token command: {command}")
        safe_print("   Valid commands: status, auto, quick, full, rollback, validate")
        sys.exit(1)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX Unified Optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Token optimization
  optimize tokens status           # Check current token usage
  optimize tokens auto             # Auto-select optimization strategy
  optimize tokens quick            # Quick optimization (~1 hour)
  optimize tokens full             # Full optimization (~3-4 hours)
  optimize tokens rollback         # Undo last optimization
  
  # File system optimization
  optimize files all               # Optimize everything
  optimize files organization      # Organize documents only
  optimize files archives          # Clean archives only
  optimize files cache             # Clear caches only
  
  # Combined
  optimize all                     # Token + file system optimization
        """
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='category', help='Optimization category')
    
    # Token optimization subcommand
    token_parser = subparsers.add_parser('tokens', help='Token optimization (governance files)')
    token_parser.add_argument(
        'command',
        choices=['status', 'auto', 'quick', 'full', 'rollback', 'validate'],
        help='Token optimization command'
    )
    
    # File optimization subcommand
    file_parser = subparsers.add_parser('files', help='File system optimization')
    file_parser.add_argument(
        'target',
        choices=['all', 'organization', 'archives', 'cortex', 'cache', 'consolidation'],
        default='all',
        help='What to optimize'
    )
    file_parser.add_argument('--aggressive', action='store_true', help='Aggressive optimization')
    file_parser.add_argument('--dry-run', action='store_true', help='Preview changes only')
    
    # All optimization subcommand
    subparsers.add_parser('all', help='Run all optimizations')
    
    args = parser.parse_args()
    
    # Handle no subcommand (show help)
    if not args.category:
        parser.print_help()
        sys.exit(1)
    
    # Route to appropriate handler
    if args.category == 'tokens':
        run_token_optimization(args.command)
    
    elif args.category == 'files':
        result = run_optimize(
            target=args.target,
            aggressive=args.aggressive,
            dry_run=args.dry_run
        )
        
        print(f"\n{'='*60}")
        print(f"CORTEX File System Optimization")
        print(f"{'='*60}\n")
        print(result["message"])
        
        if result.get("data"):
            data = result["data"]
            print(f"\nOptimization Details:")
            print(f"  Total actions: {len(data.get('optimizations_applied', []))}")
            print(f"  Space saved: {data.get('space_saved_mb', 0):.2f} MB")
            print(f"  Files moved: {data.get('files_moved', 0)}")
            print(f"  Files removed: {data.get('files_removed', 0)}")
            print(f"  Directories cleaned: {data.get('directories_cleaned', 0)}")
            
            if data.get('optimizations_applied'):
                print(f"\n  Applied optimizations:")
                for i, opt in enumerate(data['optimizations_applied'], 1):
                    print(f"    {i}. {opt}")
        
        sys.exit(0 if result["success"] else 1)
    
    elif args.category == 'all':
        safe_print("🚀 Running comprehensive CORTEX optimization")
        safe_print("━" * 80)
        safe_print("")
        
        # Step 1: Token optimization
        safe_print("📊 Step 1/2: Token Optimization")
        safe_print("")
        run_token_optimization('auto')
        
        safe_print("")
        safe_print("━" * 80)
        
        # Step 2: File system optimization
        safe_print("📊 Step 2/2: File System Optimization")
        safe_print("")
        result = run_optimize(target='all', aggressive=False, dry_run=False)
        print(result["message"])
        
        safe_print("")
        safe_print("✅ All optimizations complete")
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
