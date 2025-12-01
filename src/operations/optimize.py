"""
CORTEX Optimize Entry Point

Simple CLI wrapper for OptimizeOperation.
Follows the same pattern as align.py for consistency.

Implements comprehensive optimization from CORTEX-OPTIMIZATION-PLAN-2025-12-01.md

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from operations.optimize_operation import OptimizeOperation


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


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Comprehensive Optimization")
    parser.add_argument('--target', choices=['all', 'organization', 'archives', 'cortex', 'cache', 'consolidation'], 
                       default='all', help='What to optimize')
    parser.add_argument('--aggressive', action='store_true', help='Aggressive optimization')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes only')
    
    args = parser.parse_args()
    
    result = run_optimize(target=args.target, aggressive=args.aggressive, dry_run=args.dry_run)
    
    print(f"\n{'='*60}")
    print(f"CORTEX Optimize Operation")
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


if __name__ == "__main__":
    main()
