"""
Sweeper Demo - Show how to use the aggressive file sweeper

This script demonstrates the file sweeper plugin in action.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.plugins.sweeper_plugin import SweeperPlugin


def main():
    """Run sweeper demo"""
    print("=" * 80)
    print("CORTEX FILE SWEEPER - Demo")
    print("=" * 80)
    print()
    print("This will scan the CORTEX workspace and move files to Recycle Bin.")
    print("FILES ARE RECOVERABLE - You can restore from Recycle Bin anytime!")
    print()
    print("Target files:")
    print("  - Backup files (*.bak, *.backup, *-BACKUP-*)")
    print("  - Temporary files (*.tmp, *.temp, *.pyc)")
    print("  - Old logs (*.log older than 30 days)")
    print("  - Session reports (SESSION-*.md older than 30 days)")
    print("  - Reference docs (*-REFERENCE.md, *-IMPLEMENTATION.md older than 60 days)")
    print("  - Summary docs (*-SUMMARY.md older than 60 days)")
    print("  - Dated duplicates (file.2024-11-10.md)")
    print()
    print("Protected:")
    print("  - Source code (src/, tests/)")
    print("  - Config files (*.py, *.yaml, *.json)")
    print("  - Brain data (cortex-brain/tier1, tier2, tier3)")
    print("=" * 80)
    print()
    
    # Get workspace root
    workspace_root = Path(__file__).parent.parent
    
    response = input(f"Run sweeper on {workspace_root}? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    # Create and run sweeper
    print()
    print("Initializing sweeper...")
    sweeper = SweeperPlugin()
    
    if not sweeper.initialize():
        print("ERROR: Failed to initialize sweeper")
        return
    
    print("Running sweeper (RECYCLE BIN MODE - files can be restored)...")
    print()
    
    # Execute sweeper
    result = sweeper.execute({"workspace_root": str(workspace_root)})
    
    if not result["success"]:
        print(f"ERROR: {result.get('error', 'Unknown error')}")
        return
    
    # Show results
    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    stats = result["stats"]
    print(f"Files scanned:     {stats['files_scanned']:,}")
    print(f"Files moved:       {stats['files_deleted']:,} (to Recycle Bin)")
    print(f"Files kept:        {stats['files_kept']:,}")
    print(f"Space freed:       {stats['space_freed_mb']:.2f} MB")
    print(f"Execution time:    {stats['execution_time']:.2f}s")
    
    if result.get("errors"):
        print(f"Errors:            {len(result['errors'])}")
        for error in result['errors']:
            print(f"  - {error}")
    
    print("=" * 80)
    print()
    print("✅ Files moved to Recycle Bin - You can restore them anytime!")
    print("Audit log saved in: cortex-brain/sweeper-logs/")
    print()


if __name__ == "__main__":
    main()
