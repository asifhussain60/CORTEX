#!/usr/bin/env python3
"""
Migrate root-level planning files to appropriate subfolders.
Eliminates all files from planning root directory.

Author: Asif Hussain
Date: December 14, 2025
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

class PlanningRootMigrator:
    """Migrates root-level planning files to hierarchical structure."""
    
    def __init__(self, planning_root: str):
        self.planning_root = Path(planning_root)
        self.migration_map = self._build_migration_map()
        
    def _build_migration_map(self) -> Dict[str, str]:
        """
        Build mapping of files to their destination folders.
        
        Categories:
        - Navigation hubs (README.md, INDEX.md) → Stay temporarily, will be regenerated
        - Active master plans → features/active/cortex-3.0/
        - Vision documents → cortex-4.0/
        - Historical session docs → archived/sessions/
        - Quick reference guides → archived/quick-refs/ (superseded by newer docs)
        - Migration system docs → archived/migrations/
        """
        return {
            # Navigation hubs - will be regenerated after migration
            "README.md": "archived/legacy-navigation/README.md",
            "INDEX.md": "archived/legacy-navigation/INDEX.md",
            
            # Active CORTEX 3.0 master plans → features/active/cortex-3.0/
            "CORTEX-3.0-CONSOLIDATED-ARCHITECTURE-TRACK-A.yaml": "features/active/cortex-3.0/CORTEX-3.0-CONSOLIDATED-ARCHITECTURE-TRACK-A.yaml",
            "CORTEX-3.0-IMPLEMENTATION-PLAN.yaml": "features/active/cortex-3.0/CORTEX-3.0-IMPLEMENTATION-PLAN.yaml",
            "CORTEX-3.0-PARALLEL-TRACK-PLAN.yaml": "features/active/cortex-3.0/CORTEX-3.0-PARALLEL-TRACK-PLAN.yaml",
            "CORTEX-3.1-TOKEN-OPTIMIZATION-PLAN.yaml": "features/active/cortex-3.0/CORTEX-3.1-TOKEN-OPTIMIZATION-PLAN.yaml",
            "CORTEX-UNIFIED-ARCHITECTURE.yaml": "features/active/cortex-3.0/CORTEX-UNIFIED-ARCHITECTURE.yaml",
            "GOVERNANCE-OPTIMIZATION-COPILOT-EFFICIENCY.yaml": "features/active/cortex-3.0/GOVERNANCE-OPTIMIZATION-COPILOT-EFFICIENCY.yaml",
            
            # Active infrastructure plans → features/active/infrastructure/
            "admin-structure-migration-plan.yaml": "features/active/infrastructure/admin-structure-migration-plan.yaml",
            "cortex-onboarding-flow-design.yaml": "features/active/infrastructure/cortex-onboarding-flow-design.yaml",
            "interaction-design.yaml": "features/active/infrastructure/interaction-design.yaml",
            "update-learning-library-plan.yaml": "features/active/infrastructure/update-learning-library-plan.yaml",
            
            # Active enhancement plans → features/active/enhancements/
            "consolidated-implementation-plan.yaml": "features/active/enhancements/consolidated-implementation-plan.yaml",
            "template-enhancement-plan-20251207.yaml": "features/active/enhancements/template-enhancement-plan-20251207.yaml",
            
            # Active tracking docs → features/active/tracking/
            "YAML-MIGRATION-IMPLEMENTATION-TRACKING.yaml": "features/active/tracking/YAML-MIGRATION-IMPLEMENTATION-TRACKING.yaml",
            "YAML-PHASE-TRACKER-DESIGN.yaml": "features/active/tracking/YAML-PHASE-TRACKER-DESIGN.yaml",
            
            # Vision documents → cortex-4.0/ (already has subfolder)
            "cortex-4.0-vision.yaml": "cortex-4.0/cortex-4.0-vision.yaml",
            
            # Historical session docs → archived/sessions/
            "cortex-lens-next-session-prompt.md": "archived/sessions/cortex-lens-next-session-prompt.md",
            "cortex-lens-phase6-completion.md": "archived/sessions/cortex-lens-phase6-completion.md",
            "cortex-lens-plan-v3.md": "archived/sessions/cortex-lens-plan-v3.md",
            "prevalidation-ws-migration-lessons-learned-plan.md": "archived/sessions/prevalidation-ws-migration-lessons-learned-plan.md",
            
            # Quick reference guides → archived/quick-refs/ (superseded)
            "AUTOMATIC-DEBUGGER-ENGAGEMENT-QUICK-REF.md": "archived/quick-refs/AUTOMATIC-DEBUGGER-ENGAGEMENT-QUICK-REF.md",
            "KEY-FILES-INVENTORY.md": "archived/quick-refs/KEY-FILES-INVENTORY.md",
            "LLM-INTENT-ROUTING-MIGRATION.md": "archived/quick-refs/LLM-INTENT-ROUTING-MIGRATION.md",
            
            # Migration system docs → archived/migrations/
            "planning-migration-audit-report.md": "archived/migrations/planning-migration-audit-report.md",
            "planning-migration-deployment-guide.md": "archived/migrations/planning-migration-deployment-guide.md",
            "planning-migration-strategy.md": "archived/migrations/planning-migration-strategy.md",
        }
    
    def execute(self, dry_run: bool = False) -> Tuple[int, List[str]]:
        """
        Execute the migration.
        
        Args:
            dry_run: If True, only print what would be done
            
        Returns:
            Tuple of (files_moved, errors)
        """
        files_moved = 0
        errors = []
        
        print(f"\n{'='*70}")
        print(f"Planning Root Files Migration - {'DRY RUN' if dry_run else 'EXECUTION'}")
        print(f"{'='*70}\n")
        
        # Create necessary subdirectories
        subdirs_needed = set()
        for dest in self.migration_map.values():
            dest_path = self.planning_root / dest
            subdir = dest_path.parent
            subdirs_needed.add(subdir)
        
        print(f"📁 Creating {len(subdirs_needed)} subdirectories...")
        for subdir in sorted(subdirs_needed):
            if not dry_run:
                subdir.mkdir(parents=True, exist_ok=True)
            print(f"   ✓ {subdir.relative_to(self.planning_root)}")
        
        # Migrate files
        print(f"\n📦 Migrating {len(self.migration_map)} files...\n")
        
        for source_name, dest_rel_path in sorted(self.migration_map.items()):
            source_path = self.planning_root / source_name
            dest_path = self.planning_root / dest_rel_path
            
            if not source_path.exists():
                error_msg = f"❌ Source not found: {source_name}"
                print(error_msg)
                errors.append(error_msg)
                continue
            
            if dest_path.exists():
                error_msg = f"⚠️  Destination exists: {dest_rel_path}"
                print(error_msg)
                errors.append(error_msg)
                continue
            
            print(f"   {source_name}")
            print(f"   → {dest_rel_path}")
            
            if not dry_run:
                try:
                    shutil.move(str(source_path), str(dest_path))
                    files_moved += 1
                    print(f"   ✅ Moved\n")
                except Exception as e:
                    error_msg = f"❌ Error moving {source_name}: {e}"
                    print(f"   {error_msg}\n")
                    errors.append(error_msg)
            else:
                print(f"   [Would move]\n")
                files_moved += 1
        
        # Summary
        print(f"\n{'='*70}")
        print(f"Migration {'Simulation' if dry_run else 'Complete'}")
        print(f"{'='*70}")
        print(f"✅ Files moved: {files_moved}")
        print(f"❌ Errors: {len(errors)}")
        
        if errors:
            print(f"\n⚠️  Errors encountered:")
            for error in errors:
                print(f"   - {error}")
        
        return files_moved, errors
    
    def verify_empty_root(self) -> Tuple[bool, List[str]]:
        """
        Verify that planning root has no files (only directories).
        
        Returns:
            Tuple of (is_empty, remaining_files)
        """
        remaining_files = []
        for item in self.planning_root.iterdir():
            if item.is_file():
                remaining_files.append(item.name)
        
        return len(remaining_files) == 0, remaining_files


def main():
    """Execute planning root migration."""
    planning_root = Path(r"D:\PROJECTS\CORTEX\cortex-brain\documents\planning")
    
    if not planning_root.exists():
        print(f"❌ Planning root not found: {planning_root}")
        return 1
    
    migrator = PlanningRootMigrator(str(planning_root))
    
    # Execute migration (not dry run)
    files_moved, errors = migrator.execute(dry_run=False)
    
    if errors:
        print(f"\n⚠️  Migration completed with {len(errors)} errors")
        return 1
    
    # Verify root is empty
    print(f"\n🔍 Verifying root is empty...")
    is_empty, remaining = migrator.verify_empty_root()
    
    if is_empty:
        print(f"✅ Planning root is now clean (no files)")
        return 0
    else:
        print(f"⚠️  {len(remaining)} files still in root:")
        for filename in remaining:
            print(f"   - {filename}")
        return 1


if __name__ == "__main__":
    exit(main())
