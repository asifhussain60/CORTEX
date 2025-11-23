"""
CORTEX Upgrade Orchestrator

Coordinates all upgrade modules to safely upgrade CORTEX installations.
Implements rollback mechanism and provides comprehensive upgrade workflow.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sys
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import shutil

# Import CORTEX upgrade modules
sys.path.insert(0, str(Path(__file__).parent))

from version_detector import VersionDetector
from github_fetcher import GitHubFetcher
from brain_preserver import BrainPreserver
from config_merger import ConfigMerger
from schema_migrator import SchemaMigrator


class UpgradeOrchestrator:
    """Orchestrates complete CORTEX upgrade workflow."""
    
    def __init__(self, cortex_path: Optional[Path] = None):
        """
        Initialize upgrade orchestrator.
        
        Args:
            cortex_path: Path to CORTEX installation, or None to auto-detect
        """
        self.detector = VersionDetector(cortex_path)
        self.cortex_path = self.detector.cortex_path
        self.fetcher = GitHubFetcher()
        self.preserver = BrainPreserver(self.cortex_path)
        self.merger = ConfigMerger()
        self.migrator = SchemaMigrator(self.cortex_path)
        
        self.backup_path = None
        self.upgrade_successful = False
        
    def upgrade(
        self,
        version: Optional[str] = None,
        dry_run: bool = False,
        skip_backup: bool = False
    ) -> bool:
        """
        Perform complete CORTEX upgrade.
        
        Args:
            version: Specific version to upgrade to, or None for latest
            dry_run: If True, preview changes without applying
            skip_backup: If True, skip backup creation (NOT RECOMMENDED)
            
        Returns:
            True if upgrade successful
        """
        print(f"\n🧠 CORTEX Upgrade System v5.3.0")
        print(f"=" * 60)
        
        if dry_run:
            print(f"🔍 DRY RUN MODE - No changes will be made\n")
        
        # Step 1: Version detection
        print(f"\n[1/8] Version Detection")
        info = self.detector.get_upgrade_info()
        
        if info["deployment_type"] == "setup":
            print(f"❌ Error: No existing CORTEX installation found")
            print(f"   Use '/CORTEX setup' for fresh installation")
            return False
        
        print(f"   Current: {info['current_version']}")
        print(f"   Latest:  {info['latest_version']}")
        
        if not info["upgrade_available"] and version is None:
            print(f"✅ Already at latest version")
            return True
        
        # Step 2: Create backup
        if not skip_backup and not dry_run:
            print(f"\n[2/8] Creating Backup")
            try:
                self.backup_path = self.preserver.create_backup()
            except Exception as e:
                print(f"❌ Backup failed: {e}")
                return False
        else:
            print(f"\n[2/8] Backup (skipped)")
        
        # Step 3: Fetch latest release
        print(f"\n[3/8] Fetching Release")
        try:
            if not dry_run:
                zip_path = self.fetcher.download_release(version)
                extracted_path = self.fetcher.extract_package(zip_path)
            else:
                print(f"   [DRY RUN] Would download version {version or 'latest'}")
                extracted_path = self.cortex_path  # Use current for dry run analysis
        except Exception as e:
            print(f"❌ Download failed: {e}")
            self._rollback()
            return False
        
        # Step 4: Selective file copy (preserve brain)
        print(f"\n[4/8] Updating Core Files")
        try:
            results = self.preserver.selective_copy(extracted_path, dry_run=dry_run)
            
            if results["errors"]:
                print(f"❌ File copy errors detected")
                self._rollback()
                return False
                
        except Exception as e:
            print(f"❌ File copy failed: {e}")
            self._rollback()
            return False
        
        # Step 5: Merge configurations
        print(f"\n[5/8] Merging Configurations")
        try:
            config_files = [
                ("response-templates.yaml", self.merger.merge_response_templates),
                ("capabilities.yaml", self.merger.merge_capabilities)
            ]
            
            for config_file, merge_func in config_files:
                local_file = self.cortex_path / "cortex-brain" / config_file
                upgrade_file = extracted_path / "cortex-brain" / config_file
                
                if local_file.exists() and upgrade_file.exists():
                    if not dry_run:
                        merge_func(local_file, upgrade_file, local_file)
                    else:
                        print(f"   [DRY RUN] Would merge {config_file}")
                        
        except Exception as e:
            print(f"❌ Config merge failed: {e}")
            self._rollback()
            return False
        
        # Step 6: Apply schema migrations
        print(f"\n[6/8] Applying Schema Migrations")
        try:
            migration_results = self.migrator.migrate_all_databases(dry_run=dry_run)
            
            if not all(migration_results.values()):
                print(f"❌ Some migrations failed")
                self._rollback()
                return False
                
        except Exception as e:
            print(f"❌ Schema migration failed: {e}")
            self._rollback()
            return False
        
        # Step 7: Validate brain integrity
        print(f"\n[7/8] Validating Brain Integrity")
        try:
            validation_results = self.preserver.validate_brain_integrity()
            
            if not all(validation_results.values()):
                print(f"❌ Brain integrity validation failed")
                self._rollback()
                return False
                
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            self._rollback()
            return False
        
        # Step 8: Update version file
        print(f"\n[8/8] Updating Version File")
        try:
            if not dry_run:
                new_version = version or self.detector.get_latest_version()
                self.detector.create_version_file(
                    version=new_version,
                    deployment_type="upgrade"
                )
        except Exception as e:
            print(f"❌ Version update failed: {e}")
            self._rollback()
            return False
        
        # Cleanup
        if not dry_run:
            self.fetcher.cleanup()
        
        # Success
        print(f"\n" + "=" * 60)
        if dry_run:
            print(f"✅ DRY RUN COMPLETE - No changes were made")
            print(f"\n   To apply this upgrade, run:")
            print(f"   /CORTEX upgrade")
        else:
            print(f"✅ UPGRADE SUCCESSFUL!")
            print(f"\n   From: {info['current_version']}")
            print(f"   To:   {version or self.detector.get_latest_version()}")
            
            if self.backup_path:
                print(f"\n   Backup: {self.backup_path}")
                print(f"   (Can be removed after verifying upgrade)")
        
        print(f"=" * 60 + "\n")
        
        self.upgrade_successful = True
        return True
    
    def _rollback(self) -> None:
        """Rollback failed upgrade."""
        if not self.backup_path or not self.backup_path.exists():
            print(f"\n⚠️  No backup available for rollback")
            return
        
        print(f"\n♻️  Rolling back upgrade...")
        
        try:
            self.preserver.restore_backup(self.backup_path)
            print(f"✅ Rollback successful")
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            print(f"   Manual restore required from: {self.backup_path}")


def main():
    """CLI entry point for CORTEX upgrade."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX Upgrade System - Safely upgrade CORTEX installations"
    )
    parser.add_argument(
        "--version",
        type=str,
        help="Specific version to upgrade to (default: latest)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview upgrade without making changes"
    )
    parser.add_argument(
        "--skip-backup",
        action="store_true",
        help="Skip backup creation (NOT RECOMMENDED)"
    )
    parser.add_argument(
        "--cortex-path",
        type=Path,
        help="Path to CORTEX installation (default: auto-detect)"
    )
    
    args = parser.parse_args()
    
    try:
        orchestrator = UpgradeOrchestrator(args.cortex_path)
        success = orchestrator.upgrade(
            version=args.version,
            dry_run=args.dry_run,
            skip_backup=args.skip_backup
        )
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Upgrade interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
