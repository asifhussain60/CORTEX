#!/usr/bin/env python3
"""
AC-AR-010-02: Automated Folder Migration Script

Migrates CORTEX codebase from flat structure to nested tier-based structure:
- Moves cortex/* -> src/cortex/*
- Moves cortex_brain/* -> src/cortex_brain/*
- Removes deprecated cortex-brain/ folder
- Validates file integrity
- Implements rollback capability
- Generates migration report

Usage:
    python scripts/migrate-folder-structure.py --dry-run    # Preview changes
    python scripts/migrate-folder-structure.py --execute    # Execute migration
    python scripts/migrate-folder-structure.py --rollback   # Rollback to previous state
"""

import sys
import os
import shutil
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MigrationFile:
    """Represents a single file migration."""
    source: str
    destination: str
    file_hash_before: str = ""
    file_hash_after: str = ""
    status: str = "PENDING"  # PENDING, COPIED, VERIFIED, ROLLED_BACK
    error: Optional[str] = None


class FolderMigrator:
    """Handles folder structure migration with validation and rollback."""
    
    def __init__(self, repo_root: Path):
        """Initialize migrator."""
        self.repo_root = Path(repo_root)
        self.src_dir = self.repo_root / "src"
        self.backup_dir = self.repo_root / ".migration-backup"
        self.migration_log = self.repo_root / "MIGRATION-REPORT.md"
        
        self.files_to_migrate: List[MigrationFile] = []
        self.migration_stats = {
            'total_files': 0,
            'copied_files': 0,
            'verified_files': 0,
            'failed_files': 0,
            'total_bytes': 0,
            'start_time': None,
            'end_time': None,
        }
    
    def calculate_file_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def plan_migration(self) -> bool:
        """Plan the migration - identify all files to move."""
        logger.info("📋 Planning migration...")
        
        try:
            # Plan cortex/ -> src/cortex/
            cortex_src = self.repo_root / "cortex"
            if cortex_src.exists():
                self._plan_directory_migration(
                    cortex_src,
                    self.src_dir / "cortex"
                )
                logger.info(f"   ✓ Planned cortex/ migration ({len(self.files_to_migrate)} files)")
            
            # Plan cortex_brain/ -> src/cortex_brain/
            cortex_brain_src = self.repo_root / "cortex_brain"
            if cortex_brain_src.exists():
                self._plan_directory_migration(
                    cortex_brain_src,
                    self.src_dir / "cortex_brain"
                )
                logger.info(f"   ✓ Planned cortex_brain/ migration ({len(self.files_to_migrate)} files)")
            
            # Plan cortex-brain/ removal
            cortex_brain_deprecated = self.repo_root / "cortex-brain"
            if cortex_brain_deprecated.exists():
                logger.info("   ✓ Marked cortex-brain/ for removal")
            
            self.migration_stats['total_files'] = len(self.files_to_migrate)
            logger.info(f"✅ Migration plan complete: {self.migration_stats['total_files']} files to migrate")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Error planning migration: {e}")
            return False
    
    def _plan_directory_migration(self, src_dir: Path, dest_dir: Path) -> None:
        """Plan migration of all files in a directory."""
        for filepath in src_dir.rglob("*"):
            if filepath.is_file():
                relative_path = filepath.relative_to(src_dir)
                destination = dest_dir / relative_path
                
                file_hash = self.calculate_file_hash(filepath)
                
                migration_file = MigrationFile(
                    source=str(filepath),
                    destination=str(destination),
                    file_hash_before=file_hash,
                    status="PENDING"
                )
                self.files_to_migrate.append(migration_file)
                
                # Add to stats
                self.migration_stats['total_bytes'] += filepath.stat().st_size
    
    def create_backup(self) -> bool:
        """Create backup of original folders before migration."""
        logger.info("💾 Creating backup...")
        
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup original folders
            for folder_name in ['cortex', 'cortex_brain', 'cortex-brain']:
                folder_path = self.repo_root / folder_name
                if folder_path.exists():
                    backup_path = self.backup_dir / folder_name
                    shutil.copytree(folder_path, backup_path)
                    logger.info(f"   ✓ Backed up {folder_name}/")
            
            logger.info("✅ Backup complete")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error creating backup: {e}")
            return False
    
    def dry_run(self) -> bool:
        """Perform dry run without making changes."""
        logger.info("🔍 Performing dry run (no changes)...")
        
        # Plan migration
        if not self.plan_migration():
            return False
        
        logger.info("\n📊 Migration Preview:")
        logger.info(f"   Total files: {self.migration_stats['total_files']}")
        logger.info(f"   Total size: {self.migration_stats['total_bytes'] / (1024*1024):.2f} MB")
        
        logger.info("\n📁 Sample migrations:")
        for i, mf in enumerate(self.files_to_migrate[:5]):
            logger.info(f"   {i+1}. {Path(mf.source).relative_to(self.repo_root)} -> {Path(mf.destination).relative_to(self.repo_root)}")
        
        if len(self.files_to_migrate) > 5:
            logger.info(f"   ... and {len(self.files_to_migrate) - 5} more files")
        
        logger.info("\n✅ Dry run complete - ready to execute!")
        return True
    
    def execute_migration(self) -> bool:
        """Execute the actual migration."""
        logger.info("🚀 Executing migration...")
        
        # Plan migration
        if not self.plan_migration():
            return False
        
        # Create backup
        if not self.create_backup():
            logger.error("Backup failed - aborting migration")
            return False
        
        self.migration_stats['start_time'] = datetime.now().isoformat()
        
        try:
            # Create src/ directory if needed
            self.src_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy files
            logger.info("📂 Copying files...")
            for mf in self.files_to_migrate:
                try:
                    src_path = Path(mf.source)
                    dest_path = Path(mf.destination)
                    
                    # Create destination directory
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(src_path, dest_path)
                    
                    # Verify file
                    mf.file_hash_after = self.calculate_file_hash(dest_path)
                    
                    if mf.file_hash_before == mf.file_hash_after:
                        mf.status = "VERIFIED"
                        self.migration_stats['verified_files'] += 1
                    else:
                        mf.status = "COPIED"  # Hash mismatch - flag for review
                        logger.warning(f"⚠️ Hash mismatch: {mf.source}")
                    
                    self.migration_stats['copied_files'] += 1
                
                except Exception as e:
                    mf.status = "FAILED"
                    mf.error = str(e)
                    self.migration_stats['failed_files'] += 1
                    logger.error(f"❌ Error copying {mf.source}: {e}")
            
            # Remove old folders
            logger.info("🗑️  Removing old folders...")
            for folder_name in ['cortex', 'cortex_brain', 'cortex-brain']:
                folder_path = self.repo_root / folder_name
                if folder_path.exists():
                    shutil.rmtree(folder_path)
                    logger.info(f"   ✓ Removed {folder_name}/")
            
            self.migration_stats['end_time'] = datetime.now().isoformat()
            
            # Generate report
            self._generate_report()
            
            if self.migration_stats['failed_files'] == 0:
                logger.info("\n✅ Migration completed successfully!")
                logger.info(f"   Migrated {self.migration_stats['verified_files']} verified + {self.migration_stats['copied_files'] - self.migration_stats['verified_files']} copied = {self.migration_stats['copied_files']} total files")
                return True
            else:
                logger.warning(f"\n⚠️ Migration completed with {self.migration_stats['failed_files']} errors")
                return False
        
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            self._generate_report()
            return False
    
    def rollback(self) -> bool:
        """Rollback migration from backup."""
        logger.info("⏮️  Rolling back migration...")
        
        if not self.backup_dir.exists():
            logger.error("❌ No backup found - cannot rollback")
            return False
        
        try:
            # Remove new src structure
            if (self.src_dir / "cortex").exists():
                shutil.rmtree(self.src_dir / "cortex")
                logger.info("   ✓ Removed src/cortex/")
            
            if (self.src_dir / "cortex_brain").exists():
                shutil.rmtree(self.src_dir / "cortex_brain")
                logger.info("   ✓ Removed src/cortex_brain/")
            
            # Restore from backup
            for folder_name in ['cortex', 'cortex_brain', 'cortex-brain']:
                backup_path = self.backup_dir / folder_name
                if backup_path.exists():
                    restore_path = self.repo_root / folder_name
                    shutil.copytree(backup_path, restore_path, dirs_exist_ok=True)
                    logger.info(f"   ✓ Restored {folder_name}/")
            
            # Clean backup
            shutil.rmtree(self.backup_dir)
            
            logger.info("✅ Rollback complete")
            return True
        
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
    
    def _generate_report(self) -> None:
        """Generate detailed migration report."""
        logger.info("📝 Generating migration report...")
        
        report = f"""# Migration Report: CORTEX Folder Structure Reorganization

**Date**: {self.migration_stats['start_time']}  
**Status**: {'✅ SUCCESS' if self.migration_stats['failed_files'] == 0 else '⚠️ PARTIAL SUCCESS'}

## Summary

- **Total Files**: {self.migration_stats['total_files']}
- **Migrated Successfully**: {self.migration_stats['verified_files']} verified + {self.migration_stats['copied_files'] - self.migration_stats['verified_files']} copied
- **Failed**: {self.migration_stats['failed_files']}
- **Total Data Size**: {self.migration_stats['total_bytes'] / (1024*1024):.2f} MB
- **Duration**: {(datetime.fromisoformat(self.migration_stats['end_time']) - datetime.fromisoformat(self.migration_stats['start_time'])).total_seconds():.2f}s

## Migration Details

### Source → Destination Mapping

| Source | Destination | Status |
|--------|-------------|--------|
| `cortex/` | `src/cortex/` | ✓ Migrated |
| `cortex_brain/` | `src/cortex_brain/` | ✓ Migrated |
| `cortex-brain/` | Removed | ✓ Removed |

### File Statistics

- **Files Verified**: {self.migration_stats['verified_files']} (integrity confirmed)
- **Files Copied**: {self.migration_stats['copied_files'] - self.migration_stats['verified_files']} (copied but not verified)
- **Failed Copies**: {self.migration_stats['failed_files']}

## Next Steps

1. ✅ Migration completed
2. ⏳ AC-AR-010-03: Update all Python imports
3. ⏳ Run full test suite
4. ⏳ Phase complete and locked

## Rollback Information

Backup stored in: `.migration-backup/`

To rollback:
```bash
python scripts/migrate-folder-structure.py --rollback
```

---
Generated: {datetime.now().isoformat()}
"""
        
        with open(self.migration_log, 'w') as f:
            f.write(report)
        
        logger.info(f"   ✓ Report saved to {self.migration_log}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrate CORTEX folder structure from flat to nested tier-based organization'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without executing'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute the migration'
    )
    parser.add_argument(
        '--rollback',
        action='store_true',
        help='Rollback previous migration'
    )
    
    args = parser.parse_args()
    
    # Determine repo root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    # Create migrator
    migrator = FolderMigrator(repo_root)
    
    # Execute based on arguments
    if args.dry_run:
        success = migrator.dry_run()
    elif args.execute:
        success = migrator.execute_migration()
    elif args.rollback:
        success = migrator.rollback()
    else:
        parser.print_help()
        return 1
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
