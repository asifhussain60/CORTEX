"""
CORTEX Code Refinement CLI

Quick access to code refinement operations including path hardening.

Usage:
    python scripts/refine.py paths --dry-run
    python scripts/refine.py paths --module tier1 --apply
    python scripts/refine.py paths --apply-all
    
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
root_path = Path(__file__).parent.parent
src_path = root_path / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from batch_path_hardening import PathHardeningOrchestrator


def refine_paths(args):
    """Execute path hardening refinement."""
    orchestrator = PathHardeningOrchestrator()
    
    # Determine dry-run mode
    dry_run = not args.apply and not args.apply_all
    
    # Execute
    print(f"{'🔍 PREVIEWING' if dry_run else '✅ APPLYING'} path hardening changes...")
    result = orchestrator.execute(module=args.module, dry_run=dry_run)
    
    # Generate report
    report = orchestrator.generate_report(result)
    print(report)
    
    # Success message
    if not dry_run:
        print("\n✅ Path hardening complete!")
        print(f"   {result.replacements_made} replacements in {result.files_processed} files")
    else:
        print("\n💡 This was a dry run. Use --apply or --apply-all to apply changes.")
    
    return 0 if not result.errors else 1


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CORTEX Code Refinement Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview path hardening for tier1
  python scripts/refine.py paths --module tier1 --dry-run
  
  # Apply path hardening to operations module
  python scripts/refine.py paths --module operations --apply
  
  # Apply all path hardening fixes
  python scripts/refine.py paths --apply-all
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Refinement operation')
    
    # Path hardening command
    paths_parser = subparsers.add_parser(
        'paths',
        help='Fix hardcoded development paths'
    )
    paths_parser.add_argument(
        '--module',
        help='Specific module to process (e.g., tier1, operations)',
        default=None
    )
    paths_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying (default)'
    )
    paths_parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply changes to specified module'
    )
    paths_parser.add_argument(
        '--apply-all',
        action='store_true',
        help='Apply all changes (processes entire src/)'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'paths':
        return refine_paths(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
