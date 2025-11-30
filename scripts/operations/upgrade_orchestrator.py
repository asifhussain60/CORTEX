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
        self.is_embedded = self._detect_embedded_installation()
    
    def _detect_embedded_installation(self) -> bool:
        """
        Detect if CORTEX is embedded in another project.
        
        Returns:
            True if CORTEX is embedded (subfolder of another project)
        """
        # Check for explicit embedded marker
        marker_file = self.cortex_path / ".cortex-embedded"
        if marker_file.exists():
            return True
        
        # Check if parent directory is a git repository
        parent_git = self.cortex_path.parent / ".git"
        cortex_git = self.cortex_path / ".git"
        
        # If parent has .git but CORTEX doesn't, it's embedded
        if parent_git.exists() and not cortex_git.exists():
            return True
        
        # Check if parent directory name suggests it's a project root
        # (e.g., NOOR-CANVAS, MY-PROJECT, etc.)
        parent_name = self.cortex_path.parent.name
        cortex_name = self.cortex_path.name
        
        if cortex_name == "CORTEX" and parent_name != "CORTEX":
            # CORTEX is a subdirectory with a different parent name
            # Check if parent has typical project files
            project_indicators = [
                ".git", "package.json", "requirements.txt", 
                ".sln", ".csproj", "Cargo.toml", "go.mod"
            ]
            
            for indicator in project_indicators:
                if (self.cortex_path.parent / indicator).exists():
                    return True
        
        return False
    
    def _is_git_repository(self) -> bool:
        """Check if CORTEX is a git repository."""
        return (self.cortex_path / ".git").exists()
    
    def _has_git_remote(self, remote_name: str = "cortex-upstream") -> bool:
        """Check if git remote is configured."""
        if not self._is_git_repository():
            return False
        
        import subprocess
        result = subprocess.run(
            ["git", "remote", "get-url", remote_name],
            cwd=self.cortex_path,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def _validate_file_paths(self, base_path: Path) -> Dict[str, bool]:
        """
        Validate that all files in upgrade stay within CORTEX directory.
        
        Args:
            base_path: Base path to check files against
            
        Returns:
            Dict with validation results
        """
        import subprocess
        
        results = {
            "all_safe": True,
            "escaping_files": [],
            "total_files": 0
        }
        
        # Get list of files that would be added/modified
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD..cortex-upstream/CORTEX-3.0"],
            cwd=self.cortex_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            files = result.stdout.strip().split('\n')
            results["total_files"] = len([f for f in files if f])
            
            for file in files:
                if not file:
                    continue
                
                # Check if file path tries to escape CORTEX directory
                # Look for paths starting with ../ or absolute paths
                if file.startswith('../') or Path(file).is_absolute():
                    results["all_safe"] = False
                    results["escaping_files"].append(file)
                
                # Check if file would be created outside CORTEX
                full_path = self.cortex_path / file
                try:
                    # Resolve to absolute path and check if it's under CORTEX
                    resolved = full_path.resolve()
                    if not str(resolved).startswith(str(self.cortex_path.resolve())):
                        results["all_safe"] = False
                        results["escaping_files"].append(file)
                except Exception:
                    # If we can't resolve, assume it's unsafe
                    results["all_safe"] = False
                    results["escaping_files"].append(file)
        
        return results
    
    def _git_upgrade(self, branch: str = "CORTEX-3.0", dry_run: bool = False) -> bool:
        """
        Upgrade using git pull (preferred method).
        
        Args:
            branch: Branch to pull from
            dry_run: If True, only check for updates
            
        Returns:
            True if upgrade successful
        """
        import subprocess
        
        # Check if this is an embedded installation
        if self.is_embedded:
            print(f"⚠️  Detected embedded CORTEX installation")
            print(f"   Git merge not supported for embedded installations")
            print(f"   Falling back to selective file copy method")
            return False
        
        print(f"🔄 Using git-based upgrade (faster, cleaner)")
        
        # Fetch latest
        print(f"   Fetching from upstream...")
        if not dry_run:
            result = subprocess.run(
                ["git", "fetch", "cortex-upstream"],
                cwd=self.cortex_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Git fetch failed: {result.stderr}")
                return False
        else:
            print(f"   [DRY RUN] Would fetch cortex-upstream")
        
        # Check if there are updates
        result = subprocess.run(
            ["git", "log", "--oneline", f"HEAD..cortex-upstream/{branch}"],
            cwd=self.cortex_path,
            capture_output=True,
            text=True
        )
        
        commits_behind = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
        if commits_behind == 0:
            print(f"✅ Already up to date with upstream")
            return True
        
        print(f"   Found {commits_behind} new commits")
        
        if dry_run:
            print(f"   [DRY RUN] Would merge {commits_behind} commits")
            return True
        
        # Save current HEAD for rollback
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.cortex_path,
            capture_output=True,
            text=True
        )
        original_head = result.stdout.strip()
        
        # Merge with conflict resolution
        print(f"   Merging updates...")
        result = subprocess.run(
            ["git", "merge", f"cortex-upstream/{branch}", "-X", "theirs", "--no-edit"],
            cwd=self.cortex_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            # Try allow-unrelated-histories
            print(f"   Standard merge failed, trying with --allow-unrelated-histories...")
            result = subprocess.run(
                ["git", "merge", f"cortex-upstream/{branch}", "-X", "theirs", "--allow-unrelated-histories", "--no-edit"],
                cwd=self.cortex_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Git merge failed")
                print(f"   Error: {result.stderr}")
                # Reset to clean state
                subprocess.run(["git", "merge", "--abort"], cwd=self.cortex_path)
                subprocess.run(["git", "reset", "--hard", original_head], cwd=self.cortex_path)
                return False
        
        print(f"✅ Git upgrade complete")
        return True
        
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
        print(f"\n🧠 CORTEX Upgrade System v3.2.0")
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
        
        # Step 3: Choose upgrade method (git-aware, embedded-aware)
        print(f"\n[3/8] Choosing Upgrade Method")
        
        # Check for embedded installation
        if self.is_embedded:
            print(f"   🔒 Embedded installation detected")
            print(f"   Using safe file-copy method to preserve directory structure")
            use_git = False
        elif self._is_git_repository() and self._has_git_remote():
            print(f"   ✅ Detected git repository with upstream remote")
            
            # Validate paths before attempting git merge
            print(f"\n   Validating file paths...")
            validation = self._validate_file_paths(self.cortex_path)
            
            if not validation["all_safe"]:
                print(f"   ⚠️  WARNING: {len(validation['escaping_files'])} files would escape CORTEX directory:")
                for file in validation["escaping_files"][:5]:  # Show first 5
                    print(f"      - {file}")
                if len(validation["escaping_files"]) > 5:
                    print(f"      ... and {len(validation['escaping_files']) - 5} more")
                print(f"   🔒 Switching to safe file-copy method")
                use_git = False
            else:
                print(f"   ✅ All {validation['total_files']} files are safe")
                use_git = True
        else:
            print(f"   ℹ️  No git remote, using download method")
            use_git = False
        
        # Git-based upgrade (preferred)
        if use_git:
            print(f"\n[4/8] Git-Based Upgrade")
            try:
                git_success = self._git_upgrade(dry_run=dry_run)
                
                if git_success:
                    # Skip to validation (steps 5-8)
                    print(f"\n[5/8] Skipping file copy (git handled)")
                    print(f"\n[6/8] Skipping config merge (git handled)")
                    
                    # Apply schema migrations
                    print(f"\n[7/8] Applying Schema Migrations")
                    if not dry_run:
                        migration_results = self.migrator.migrate_all_databases(dry_run=False)
                        if not all(migration_results.values()):
                            print(f"❌ Some migrations failed")
                            self._rollback()
                            return False
                    else:
                        print(f"   [DRY RUN] Would apply database migrations")
                    
                    # Validate brain integrity
                    print(f"\n[8/8] Validating Brain Integrity")
                    if not dry_run:
                        validation_results = self.preserver.validate_brain_integrity()
                        if not all(validation_results.values()):
                            print(f"❌ Brain integrity validation failed")
                            self._rollback()
                            return False
                    else:
                        print(f"   [DRY RUN] Would validate brain integrity")
                    
                    # Success
                    self._print_success_message(info, version, dry_run)
                    self.upgrade_successful = True
                    return True
                else:
                    print(f"⚠️  Git upgrade failed, falling back to download method")
                    use_git = False
            except Exception as e:
                print(f"❌ Git upgrade error: {e}")
                print(f"   Falling back to download method")
                use_git = False
        
        # Download-based upgrade (fallback)
        if not use_git:
            print(f"\n[4/8] Fetching Release")
            try:
                if not dry_run:
                    zip_path = self.fetcher.download_release(version)
                    extracted_path = self.fetcher.extract_package(zip_path)
                    
                    # Validate extracted package
                    print(f"\n   Validating package integrity...")
                    validation = self.fetcher.validate_extracted_package(extracted_path)
                    if not all(validation.values()):
                        raise RuntimeError("Downloaded package is incomplete or corrupted")
                else:
                    print(f"   [DRY RUN] Would download version {version or 'latest'}")
                    extracted_path = self.cortex_path  # Use current for dry run analysis
            except Exception as e:
                print(f"❌ Download failed: {e}")
                self._rollback()
                return False
        
        # Step 4: Selective file copy (preserve brain)
        print(f"\n[5/8] Updating Core Files")
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
        print(f"\n[6/8] Merging Configurations")
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
        print(f"\n[7/8] Applying Schema Migrations")
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
        print(f"\n[8/8] Validating Brain Integrity")
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
        
        # Cleanup
        if not dry_run:
            self.fetcher.cleanup()
        
        # Success - Update VERSION file
        if not dry_run:
            self._update_version_file(version or self.detector.get_latest_version())
        
        self._print_success_message(info, version, dry_run)
        self.upgrade_successful = True
        return True
    
    def _update_version_file(self, new_version: str) -> None:
        """Update VERSION file after successful upgrade."""
        version_file = self.cortex_path / "VERSION"
        
        # Ensure version has v prefix
        if not new_version.startswith('v'):
            new_version = f'v{new_version}'
        
        try:
            with open(version_file, 'w', encoding='utf-8') as f:
                f.write(f"{new_version}\n")
            print(f"   ✅ VERSION file updated: {new_version}")
        except Exception as e:
            print(f"   ⚠️  Could not update VERSION file: {e}")
    
    def _print_success_message(self, info: Dict, version: Optional[str], dry_run: bool) -> None:
        """Print upgrade success message."""
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
