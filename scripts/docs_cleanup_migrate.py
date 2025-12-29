#!/usr/bin/env python3
"""
CORTEX Documentation Cleanup - Phase 2: Safe Migration

Moves manual files to proper locations before deletion.

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


class DocumentationMigration:
    """Migrate manual files to proper locations."""
    
    def __init__(self, cortex_root: Path, manifest_path: Path):
        self.cortex_root = cortex_root
        self.manifest_path = manifest_path
        
        # Load manifest
        with open(manifest_path, 'r') as f:
            self.manifest = json.load(f)
        
        # Migration targets
        self.guides_dir = cortex_root / "cortex-brain" / "documents" / "guides"
        self.reports_dir = cortex_root / "cortex-brain" / "documents" / "reports"
        self.archive_dir = cortex_root / "cortex-brain" / "archives" / "manual-docs-2025-11-18"
        
        # Results
        self.migrations = []
        self.errors = []
    
    def create_migration_plan(self) -> list:
        """Create migration plan for manual files."""
        print("📋 Creating migration plan...")
        
        migrations = []
        
        for file in self.manifest.get("manual_files", []):
            src = self.cortex_root / file
            
            # Determine destination based on filename
            filename = Path(file).name
            
            if "REPORT" in filename.upper():
                dest = self.reports_dir / filename
                reason = "Generation report"
            elif "GUIDE" in filename.upper():
                dest = self.guides_dir / filename
                reason = "User guide"
            elif filename.endswith(".backup"):
                dest = self.archive_dir / filename
                reason = "Backup file"
            else:
                dest = self.guides_dir / filename
                reason = "Manual documentation"
            
            migrations.append({
                "source": str(src),
                "destination": str(dest),
                "reason": reason,
                "exists": src.exists()
            })
        
        print(f"  ✅ Created migration plan for {len(migrations)} files")
        return migrations
    
    def execute_migrations(self, migrations: list, dry_run: bool = False):
        """Execute file migrations."""
        print(f"\n🚚 {'[DRY RUN] ' if dry_run else ''}Executing migrations...")
        
        for migration in migrations:
            src = Path(migration["source"])
            dest = Path(migration["destination"])
            
            if not src.exists():
                self.errors.append(f"Source not found: {src}")
                print(f"  ❌ Source not found: {src.name}")
                continue
            
            if dry_run:
                print(f"  [DRY RUN] Would move: {src.name} → {dest.parent.name}/")
                continue
            
            # Create destination directory
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file (keep original for now)
            try:
                shutil.copy2(src, dest)
                self.migrations.append(migration)
                print(f"  ✅ Migrated: {src.name} → {dest.parent.name}/")
            except Exception as e:
                self.errors.append(f"Failed to migrate {src}: {e}")
                print(f"  ❌ Failed: {src.name} - {e}")
    
    def create_archive(self, dry_run: bool = False):
        """Create full archive of all manual files."""
        print(f"\n📦 {'[DRY RUN] ' if dry_run else ''}Creating archive...")
        
        if dry_run:
            print(f"  [DRY RUN] Would create archive at: {self.archive_dir}")
            return
        
        # Create archive directory
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all manual files to archive
        for file in self.manifest.get("manual_files", []):
            src = self.cortex_root / file
            if src.exists():
                dest = self.archive_dir / src.name
                try:
                    shutil.copy2(src, dest)
                    print(f"  ✅ Archived: {src.name}")
                except Exception as e:
                    print(f"  ❌ Failed to archive {src.name}: {e}")
    
    def create_migration_report(self, output_path: Path):
        """Create migration report."""
        report = {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "manifest_used": str(self.manifest_path),
            
            "summary": {
                "total_migrations": len(self.migrations),
                "successful": len(self.migrations),
                "failed": len(self.errors)
            },
            
            "migrations": self.migrations,
            "errors": self.errors,
            
            "destinations": {
                "guides": str(self.guides_dir),
                "reports": str(self.reports_dir),
                "archive": str(self.archive_dir)
            }
        }
        
        # Write report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Migration report saved: {output_path}")
        return report
    
    def print_summary(self):
        """Print migration summary."""
        print("\n" + "="*60)
        print("📊 MIGRATION SUMMARY")
        print("="*60)
        
        print(f"\n✅ Successful Migrations: {len(self.migrations)}")
        print(f"❌ Failed Migrations: {len(self.errors)}")
        
        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"    • {error}")


def main():
    """Run Phase 2: Safe Migration."""
    print("🧠 CORTEX Documentation Cleanup - Phase 2: Migration")
    print("="*60)
    
    cortex_root = Path(__file__).parent.parent
    manifest_path = cortex_root / "cortex-brain" / "cleanup-reports" / "cleanup-manifest-2025-11-18.json"
    
    if not manifest_path.exists():
        print(f"❌ Manifest not found: {manifest_path}")
        print("   Run Phase 1 (discovery) first!")
        return
    
    # Initialize migration
    migration = DocumentationMigration(cortex_root, manifest_path)
    
    # Create migration plan
    migrations = migration.create_migration_plan()
    
    # Execute migrations (real run)
    migration.execute_migrations(migrations, dry_run=False)
    
    # Create archive
    migration.create_archive(dry_run=False)
    
    # Create report
    report_path = cortex_root / "cortex-brain" / "cleanup-reports" / "migration-report-2025-11-18.json"
    migration.create_migration_report(report_path)
    
    # Print summary
    migration.print_summary()
    
    print("\n" + "="*60)
    print("✅ Phase 2 Complete - Manual files migrated")
    print("="*60)
    print(f"\n📄 Report: {report_path}")
    print("\n🔍 Next Step: Run Phase 3 (Cleanup Execution)")


if __name__ == "__main__":
    main()
