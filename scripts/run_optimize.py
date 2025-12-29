"""
Run CORTEX Comprehensive Optimization Operation

Executes all optimization fixes from CORTEX-OPTIMIZATION-PLAN-2025-12-01.md:
- Phase 1: File organization (move scattered tests/scripts)
- Phase 1: Build artifact cleanup (dist/, publish/, *.db)
- Phase 1: Duplicate removal (templates, logos)
- Phase 2: Archive consolidation
- Database optimization (vacuum)
- Cache optimization

Usage:
    python run_optimize.py              # Run all optimizations
    python run_optimize.py --dry-run    # Preview changes without executing
    python run_optimize.py --target organization  # Only file organization
    python run_optimize.py --aggressive  # Aggressive database optimization

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import argparse
from pathlib import Path

# Add src to path (parent directory's src folder)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from operations.optimize_operation import OptimizeOperation

def run_optimize(dry_run: bool = False, target: str = 'all', aggressive: bool = False):
    """Run comprehensive optimization operation."""
    print("🧠 CORTEX Comprehensive Optimization")
    print("=" * 60)
    print(f"Mode: {'[DRY RUN]' if dry_run else 'EXECUTE'}")
    print(f"Target: {target}")
    print(f"Aggressive: {aggressive}")
    print("=" * 60)
    
    # Create optimizer instance
    optimizer = OptimizeOperation()
    
    # Validate prerequisites
    print("\n📋 Validating prerequisites...")
    validation_result = optimizer.validate()
    
    if not validation_result.success:
        print(f"   ❌ Validation failed: {validation_result.message}")
        return False
    
    print(f"   ✅ {validation_result.message}")
    
    # Execute optimization
    print("\n🔧 Running optimization...")
    result = optimizer.execute(target=target, aggressive=aggressive, dry_run=dry_run)
    
    if result.success:
        print(f"\n✅ {result.message}")
        
        # Show results
        data = result.data
        print("\n📊 Results:")
        print(f"   • Optimizations applied: {len(data['optimizations_applied'])}")
        print(f"   • Space saved: {data['space_saved_mb']:.2f} MB")
        print(f"   • Files moved: {data.get('files_moved', 0)}")
        print(f"   • Files removed: {data.get('files_removed', 0)}")
        print(f"   • Directories cleaned: {data.get('directories_cleaned', 0)}")
        
        if data['optimizations_applied']:
            print("\n   Applied optimizations:")
            for i, opt in enumerate(data['optimizations_applied'], 1):
                print(f"      {i}. {opt}")
        
        if data.get('report_path'):
            print(f"\n📄 Detailed report: {data['report_path']}")
        
        if dry_run:
            print("\n⚠️  This was a DRY RUN - no changes were made.")
            print("   Run without --dry-run to apply changes.")
        
        return True
    else:
        print(f"\n❌ Optimization failed: {result.message}")
        if result.errors:
            print(f"   Errors:")
            for error in result.errors:
                print(f"      - {error}")
        return False

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CORTEX Comprehensive Optimization - Implements fixes from CORTEX-OPTIMIZATION-PLAN-2025-12-01.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_optimize.py                    # Run all optimizations
  python run_optimize.py --dry-run          # Preview changes
  python run_optimize.py --target organization  # Only file organization
  python run_optimize.py --aggressive       # Aggressive optimization

Targets:
  all           - All optimizations (default)
  organization  - File organization (move scattered files)
  archives      - Archive consolidation
  cortex        - Brain, database, and cache optimization
  cache         - Cache optimization only
  consolidation - Markdown documentation consolidation
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without executing them'
    )
    
    parser.add_argument(
        '--target',
        choices=['all', 'organization', 'archives', 'cortex', 'cache', 'consolidation'],
        default='all',
        help='What to optimize (default: all)'
    )
    
    parser.add_argument(
        '--aggressive',
        action='store_true',
        help='Use aggressive optimization for databases'
    )
    
    args = parser.parse_args()
    
    success = run_optimize(
        dry_run=args.dry_run,
        target=args.target,
        aggressive=args.aggressive
    )
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
