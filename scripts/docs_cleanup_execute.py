#!/usr/bin/env python3
"""
CORTEX Documentation Cleanup - Phase 3: Cleanup Execution

Physically deletes non-generated files from docs/ directory.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Date: 2025-11-18
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import sys

# Add CORTEX root to path
CORTEX_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(CORTEX_ROOT))


class DocumentationCleanup:
    """Execute documentation cleanup."""
    
    def __init__(self, cortex_root: Path, manifest_path: Path):
        self.cortex_root = cortex_root
        self.manifest_path = manifest_path
        
        # Load manifest
        with open(manifest_path, 'r') as f:
            self.manifest = json.load(f)
        
        # Results
        self.deleted_files = []
        self.deleted_dirs = []
        self.kept_files = []
        self.errors = []
    
    def create_backup(self):
        """Create full backup of docs/ directory."""
        print("💾 Creating full backup of docs/ directory...")
        
        docs_path = self.cortex_root / "docs"
        backup_path = self.cortex_root / "cortex-brain" / "archives" / "docs-backup-2025-11-18"
        
        if backup_path.exists():
            print(f"  ⚠️  Backup already exists: {backup_path}")
            return
        
        try:
            shutil.copytree(docs_path, backup_path)
            print(f"  ✅ Backup created: {backup_path}")
        except Exception as e:
            print(f"  ❌ Backup failed: {e}")
            raise
    
    def delete_files(self, file_list: list, category: str, dry_run: bool = False):
        """Delete files from list."""
        print(f"\n🗑️  {'[DRY RUN] ' if dry_run else ''}Deleting {category} files...")
        
        for file_path_str in file_list:
            file_path = self.cortex_root / file_path_str
            
            if not file_path.exists():
                print(f"  ⚠️  File not found (already deleted?): {file_path.name}")
                continue
            
            if dry_run:
                print(f"  [DRY RUN] Would delete: {file_path_str}")
                continue
            
            try:
                file_path.unlink()
                self.deleted_files.append(file_path_str)
                print(f"  ✅ Deleted: {file_path.name}")
            except Exception as e:
                self.errors.append(f"Failed to delete {file_path}: {e}")
                print(f"  ❌ Failed: {file_path.name} - {e}")
    
    def delete_empty_directories(self, dry_run: bool = False):
        """Delete empty directories in docs/."""
        print(f"\n📁 {'[DRY RUN] ' if dry_run else ''}Deleting empty directories...")
        
        docs_path = self.cortex_root / "docs"
        
        # Get all directories, sorted by depth (deepest first)
        all_dirs = sorted([d for d in docs_path.rglob("*") if d.is_dir()],
                         key=lambda x: len(x.parts), reverse=True)
        
        for dir_path in all_dirs:
            # Skip static asset directories
            if any(x in str(dir_path) for x in ["assets", "images", "stylesheets", "overrides"]):
                continue
            
            # Check if empty
            if not any(dir_path.iterdir()):
                if dry_run:
                    print(f"  [DRY RUN] Would delete empty dir: {dir_path.relative_to(self.cortex_root)}")
                    continue
                
                try:
                    dir_path.rmdir()
                    self.deleted_dirs.append(str(dir_path.relative_to(self.cortex_root)))
                    print(f"  ✅ Deleted empty dir: {dir_path.name}/")
                except Exception as e:
                    print(f"  ❌ Failed to delete {dir_path.name}/: {e}")
    
    def verify_generated_files_intact(self):
        """Verify generated files still exist."""
        print("\n✅ Verifying generated files are intact...")
        
        all_intact = True
        for file_path_str in self.manifest.get("generated_files", []):
            file_path = self.cortex_root / file_path_str
            if file_path.exists():
                self.kept_files.append(file_path_str)
            else:
                all_intact = False
                self.errors.append(f"Generated file missing: {file_path}")
                print(f"  ❌ Missing: {file_path.name}")
        
        if all_intact:
            print(f"  ✅ All {len(self.kept_files)} generated files intact")
        
        return all_intact
    
    def create_cleanup_report(self, output_path: Path):
        """Create cleanup execution report."""
        report = {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "manifest_used": str(self.manifest_path),
            
            "summary": {
                "deleted_files": len(self.deleted_files),
                "deleted_directories": len(self.deleted_dirs),
                "kept_files": len(self.kept_files),
                "errors": len(self.errors)
            },
            
            "deleted_files": self.deleted_files,
            "deleted_directories": self.deleted_dirs,
            "kept_files": self.kept_files,
            "errors": self.errors
        }
        
        # Write report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Cleanup report saved: {output_path}")
        return report
    
    def print_summary(self):
        """Print cleanup summary."""
        print("\n" + "="*60)
        print("📊 CLEANUP SUMMARY")
        print("="*60)
        
        print(f"\n🗑️  Files Deleted: {len(self.deleted_files)}")
        print(f"📁 Directories Deleted: {len(self.deleted_dirs)}")
        print(f"✅ Files Kept (Generated): {len(self.kept_files)}")
        print(f"❌ Errors: {len(self.errors)}")
        
        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"    • {error}")


def main():
    """Run Phase 3: Cleanup Execution."""
    print("🧠 CORTEX Documentation Cleanup - Phase 3: Execution")
    print("="*60)
    
    cortex_root = Path(__file__).parent.parent
    manifest_path = cortex_root / "cortex-brain" / "cleanup-reports" / "cleanup-manifest-2025-11-18.json"
    
    if not manifest_path.exists():
        print(f"❌ Manifest not found: {manifest_path}")
        print("   Run Phase 1 (discovery) first!")
        return
    
    # Initialize cleanup
    cleanup = DocumentationCleanup(cortex_root, manifest_path)
    
    # Step 1: Create backup
    cleanup.create_backup()
    
    # Step 2: Delete manual files (already migrated in Phase 2)
    cleanup.delete_files(cleanup.manifest.get("manual_files", []), "manual")
    
    # Step 3: Delete unknown files (need review, but we'll keep them for now)
    # Skip for safety - these need manual review
    print("\n⚠️  Skipping 'unknown' files - need manual review")
    print(f"   ({len(cleanup.manifest.get('unknown_files', []))} files)")
    
    # Step 4: Delete empty directories
    cleanup.delete_empty_directories()
    
    # Step 5: Verify generated files intact
    cleanup.verify_generated_files_intact()
    
    # Step 6: Create report
    report_path = cortex_root / "cortex-brain" / "cleanup-reports" / "cleanup-execution-report-2025-11-18.json"
    cleanup.create_cleanup_report(report_path)
    
    # Print summary
    cleanup.print_summary()
    
    print("\n" + "="*60)
    print("✅ Phase 3 Complete - Cleanup executed")
    print("="*60)
    print(f"\n📄 Report: {report_path}")
    print("\n⚠️  Note: 'Unknown' files preserved for manual review")
    print("🔍 Next Step: Run Phase 4 (Generator Enhancement)")


if __name__ == "__main__":
    main()
