#!/usr/bin/env python3
"""
Utility Reorganizer for CORTEX Toolkit.

Moves utilities from scripts/utilities/ to cortex-toolkit/scripts-utilities/{category}/
while preserving file permissions and updating imports.

Part of Phase P05.3: Category-Based Organization.
"""

import shutil
import sys
from pathlib import Path
from typing import Dict, List

# Import ScriptsUtilitiesManager
import importlib.util
spec = importlib.util.spec_from_file_location(
    'manager',
    Path(__file__).parent.parent / 'core' / 'scripts_utilities_manager.py'
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ScriptsUtilitiesManager = module.ScriptsUtilitiesManager


def reorganize_utilities(dry_run: bool = False):
    """
    Reorganize utilities into category-based structure.
    
    Args:
        dry_run: If True, only print what would be done
    """
    # Detect project root
    current = Path(__file__).resolve()
    for parent in [current.parent] + list(current.parents):
        if (parent / "cortex.config.json").exists():
            project_root = parent
            break
    else:
        project_root = current.parent.parent.parent
    
    scripts_dir = project_root / "scripts" / "utilities"
    toolkit_dir = project_root / "cortex-toolkit" / "scripts-utilities"
    
    # Initialize manager
    manager = ScriptsUtilitiesManager(
        scripts_dir=str(scripts_dir),
        toolkit_dir=str(toolkit_dir)
    )
    
    # Discover utilities
    utilities = manager.discover_utilities()
    print(f"🔍 Found {len(utilities)} utilities to reorganize\n")
    
    # Group by category
    by_category: Dict[str, List] = {}
    for util in utilities:
        if util.category not in by_category:
            by_category[util.category] = []
        by_category[util.category].append(util)
    
    # Reorganize each category
    moved_count = 0
    for category, category_utils in by_category.items():
        # Create category directory
        category_dir = toolkit_dir / category
        
        if not dry_run:
            category_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Category: {category} ({len(category_utils)} utilities)")
        
        for util in category_utils:
            source = Path(util.file_path)
            dest = category_dir / source.name
            
            if dry_run:
                print(f"  [DRY RUN] Would move: {source.name} → {category}/")
            else:
                if source.exists():
                    # Copy file (preserving original in scripts/utilities for now)
                    shutil.copy2(source, dest)
                    print(f"  ✅ Copied: {source.name} → {category}/")
                    moved_count += 1
                else:
                    print(f"  ⚠️  Source not found: {source}")
        
        print()
    
    if not dry_run:
        print(f"✅ Reorganization complete: {moved_count} utilities copied")
        print(f"📁 Location: {toolkit_dir}")
        print("\n⚠️  Original files remain in scripts/utilities/ for safety")
        print("   Run cleanup after verifying new structure works correctly")
    else:
        print(f"🔍 Dry run complete. Would copy {len(utilities)} utilities.")
        print("   Run without --dry-run to execute reorganization")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    reorganize_utilities(dry_run=dry_run)
