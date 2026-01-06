#!/usr/bin/env python3
"""
Cleanup Script: Move Orphaned Plans into Epic Folder

This script identifies and moves misplaced plan folders from
cortex-brain/documents/planning/active/ root into their parent epic folder.

Usage:
    python3 scripts/cleanup_orphaned_plans.py --dry-run          # Preview changes
    python3 scripts/cleanup_orphaned_plans.py --execute          # Execute moves
    python3 scripts/cleanup_orphaned_plans.py --archive          # Archive to backups/
"""

import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime


class OrphanedPlanCleanup:
    """Cleanup utility for misplaced plan folders."""
    
    def __init__(self, active_dir: Path = None, epic_name: str = "cortex5-enhancement-epic"):
        self.active_dir = active_dir or Path("cortex-brain/documents/planning/active")
        self.epic_name = epic_name
        self.epic_folder = self.active_dir / epic_name
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def detect_orphaned_plans(self):
        """Detect plans that should be inside epic but are at root."""
        if not self.active_dir.exists():
            print(f"❌ Active directory not found: {self.active_dir}")
            return []
        
        # Known epic folders (don't move these)
        epic_folders = {
            "cortex5-enhancement-epic",
            "cortex5-remediation",
            "cortex-v5-epic",
            "cortex-v5-remediation-epic"
        }
        
        orphaned_plans = []
        for item in self.active_dir.iterdir():
            if not item.is_dir():
                continue
            
            # Skip known epics
            if item.name in epic_folders:
                continue
            
            # Identify child plans (patterns that indicate non-epic plans)
            child_plan_patterns = [
                'plan-',           # UUID-based plans
                'a01-', 'a19-',    # A## prefixed plans
                'continue-',       # Continue plans
                'fix-',            # Fix plans
                'investigate-',    # Investigation plans
                'test-',           # Test plans
                'script-'          # Script plans
            ]
            
            if any(item.name.startswith(pattern) for pattern in child_plan_patterns):
                orphaned_plans.append(item)
        
        return sorted(orphaned_plans, key=lambda x: x.name)
    
    def preview_cleanup(self):
        """Preview what would be moved (dry run)."""
        print("=" * 70)
        print("🔍 ORPHANED PLANS CLEANUP PREVIEW")
        print("=" * 70)
        print(f"\n📁 Active Directory: {self.active_dir}")
        print(f"📦 Target Epic: {self.epic_name}")
        print()
        
        if not self.epic_folder.exists():
            print(f"❌ Epic folder not found: {self.epic_folder}")
            print("   Cannot proceed without target epic folder.")
            return
        
        orphaned_plans = self.detect_orphaned_plans()
        
        if not orphaned_plans:
            print("✅ No orphaned plans found! Directory is clean.")
            return
        
        print(f"⚠️  Found {len(orphaned_plans)} orphaned plans:\n")
        
        for i, plan in enumerate(orphaned_plans, 1):
            target = self.epic_folder / plan.name
            status = "⚠️ EXISTS" if target.exists() else "✅ READY"
            
            print(f"{i:2}. {status} {plan.name}")
            print(f"    → {self.epic_name}/{plan.name}")
        
        print(f"\n📊 Summary:")
        print(f"   - Plans to move: {len(orphaned_plans)}")
        print(f"   - Target folder: {self.epic_folder}")
        print()
        print("💡 To execute: python3 scripts/cleanup_orphaned_plans.py --execute")
    
    def execute_cleanup(self):
        """Execute the cleanup (move files)."""
        print("=" * 70)
        print("🛠️  EXECUTING ORPHANED PLANS CLEANUP")
        print("=" * 70)
        print()
        
        if not self.epic_folder.exists():
            print(f"❌ Epic folder not found: {self.epic_folder}")
            return
        
        orphaned_plans = self.detect_orphaned_plans()
        
        if not orphaned_plans:
            print("✅ No orphaned plans to move.")
            return
        
        moved_count = 0
        skipped_count = 0
        
        for plan in orphaned_plans:
            target = self.epic_folder / plan.name
            
            if target.exists():
                print(f"⚠️  SKIP (target exists): {plan.name}")
                skipped_count += 1
                continue
            
            try:
                shutil.move(str(plan), str(target))
                print(f"✅ MOVED: {plan.name} → {self.epic_name}/{plan.name}")
                moved_count += 1
            except Exception as e:
                print(f"❌ ERROR moving {plan.name}: {e}")
        
        print()
        print(f"📊 Cleanup Summary:")
        print(f"   - Plans moved: {moved_count}")
        print(f"   - Plans skipped: {skipped_count}")
        print(f"   - Total processed: {len(orphaned_plans)}")
    
    def archive_orphaned_plans(self):
        """Archive orphaned plans to backups/ directory."""
        print("=" * 70)
        print("📦 ARCHIVING ORPHANED PLANS")
        print("=" * 70)
        print()
        
        backup_dir = Path(f"backups/orphaned-plans-{self.timestamp}")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        orphaned_plans = self.detect_orphaned_plans()
        
        if not orphaned_plans:
            print("✅ No orphaned plans to archive.")
            return
        
        archived_count = 0
        
        # Create manifest
        manifest = backup_dir / "ARCHIVE-MANIFEST.md"
        with open(manifest, 'w') as f:
            f.write(f"# Orphaned Plans Archive\n\n")
            f.write(f"**Date:** {datetime.now().isoformat()}\n")
            f.write(f"**Source:** {self.active_dir}\n")
            f.write(f"**Reason:** Plan folder flooding cleanup\n\n")
            f.write(f"## Archived Plans\n\n")
        
        for plan in orphaned_plans:
            target = backup_dir / plan.name
            
            try:
                shutil.copytree(str(plan), str(target))
                print(f"✅ ARCHIVED: {plan.name}")
                archived_count += 1
                
                # Update manifest
                with open(manifest, 'a') as f:
                    f.write(f"- `{plan.name}/`\n")
            except Exception as e:
                print(f"❌ ERROR archiving {plan.name}: {e}")
        
        print()
        print(f"📊 Archive Summary:")
        print(f"   - Plans archived: {archived_count}")
        print(f"   - Archive location: {backup_dir}")
        print(f"   - Manifest: {manifest}")
        print()
        print("💡 Original plans NOT deleted. Run with --execute to move them.")


def main():
    parser = argparse.ArgumentParser(
        description="Cleanup orphaned plan folders in active/ directory"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Preview changes without executing (default)"
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help="Execute the cleanup (move files)"
    )
    parser.add_argument(
        '--archive',
        action='store_true',
        help="Archive orphaned plans to backups/ before moving"
    )
    parser.add_argument(
        '--epic',
        type=str,
        default="cortex5-enhancement-epic",
        help="Target epic folder name (default: cortex5-enhancement-epic)"
    )
    
    args = parser.parse_args()
    
    # Default to dry-run if no action specified
    if not (args.execute or args.archive):
        args.dry_run = True
    
    cleanup = OrphanedPlanCleanup(epic_name=args.epic)
    
    if args.archive:
        cleanup.archive_orphaned_plans()
    elif args.execute:
        # Confirm before executing
        print("⚠️  WARNING: This will MOVE plan folders!")
        response = input("Continue? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            cleanup.execute_cleanup()
        else:
            print("❌ Cancelled.")
    else:
        cleanup.preview_cleanup()


if __name__ == "__main__":
    main()
