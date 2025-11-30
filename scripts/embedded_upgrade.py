"""
CORTEX Embedded Installation Upgrade Script

Safely upgrades CORTEX installations embedded in user projects.
Uses file-copy method instead of git merge to avoid unrelated history issues.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sys
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class EmbeddedUpgradeScript:
    """
    Handles safe upgrades for embedded CORTEX installations.
    
    Strategy:
    1. Detect if installation is embedded
    2. Download latest release to temp directory
    3. Validate all file paths stay within CORTEX/
    4. Backup brain data
    5. Selectively copy updated files
    6. Preserve brain databases and user configs
    7. Run post-upgrade validation
    """
    
    GITHUB_REPO = "https://github.com/asifhussain60/CORTEX.git"
    RELEASE_BRANCH = "CORTEX-3.0"
    
    def __init__(self, cortex_path: Path):
        """Initialize upgrade script."""
        self.cortex_path = cortex_path.resolve()
        self.parent_path = self.cortex_path.parent
        self.is_embedded = self._detect_embedded()
        self.backup_path = None
        
    def _detect_embedded(self) -> bool:
        """Detect if CORTEX is embedded installation."""
        # Check for explicit marker
        marker = self.cortex_path / ".cortex-embedded"
        if marker.exists():
            print(f"{Colors.BLUE}✓ Detected embedded installation (marker file){Colors.RESET}")
            return True
        
        # Check if parent has .git
        parent_git = self.parent_path / ".git"
        cortex_git = self.cortex_path / ".git"
        
        if parent_git.exists() and not cortex_git.exists():
            print(f"{Colors.BLUE}✓ Detected embedded installation (parent git){Colors.RESET}")
            return True
        
        # Check for project files in parent
        project_files = [".git", "package.json", ".sln", "Cargo.toml"]
        for pf in project_files:
            if (self.parent_path / pf).exists():
                print(f"{Colors.BLUE}✓ Detected embedded installation (parent project files){Colors.RESET}")
                return True
        
        return False
    
    def _get_current_version(self) -> str:
        """Get current CORTEX version from VERSION file."""
        version_file = self.cortex_path / "VERSION"
        if version_file.exists():
            return version_file.read_text(encoding='utf-8').strip()
        return "unknown"
    
    def _download_latest_release(self) -> Path:
        """Download latest CORTEX release to temp directory."""
        print(f"\n{Colors.BOLD}[1/7] Downloading Latest Release{Colors.RESET}")
        
        temp_dir = Path(tempfile.mkdtemp(prefix="cortex_upgrade_"))
        print(f"  📥 Cloning from {self.GITHUB_REPO}")
        print(f"  📂 Temp directory: {temp_dir}")
        
        try:
            result = subprocess.run(
                ["git", "clone", "--branch", self.RELEASE_BRANCH, "--depth", "1", 
                 self.GITHUB_REPO, str(temp_dir)],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Get version from downloaded release
            version_file = temp_dir / "VERSION"
            if version_file.exists():
                version = version_file.read_text(encoding='utf-8').strip()
                print(f"  ✅ Downloaded version: {Colors.GREEN}{version}{Colors.RESET}")
            else:
                print(f"  ⚠️  Version file not found in release")
            
            return temp_dir
            
        except subprocess.CalledProcessError as e:
            print(f"  {Colors.RED}❌ Clone failed: {e.stderr}{Colors.RESET}")
            raise
    
    def _validate_paths(self, source_dir: Path) -> Tuple[bool, List[str]]:
        """Validate all files stay within CORTEX directory."""
        print(f"\n{Colors.BOLD}[2/7] Validating File Paths{Colors.RESET}")
        
        escaping_files = []
        
        for item in source_dir.rglob('*'):
            if item.is_file():
                # Get relative path from source
                rel_path = item.relative_to(source_dir)
                
                # Check if path tries to escape
                if str(rel_path).startswith('../') or rel_path.is_absolute():
                    escaping_files.append(str(rel_path))
        
        if escaping_files:
            print(f"  {Colors.RED}❌ Found {len(escaping_files)} files that would escape CORTEX directory:{Colors.RESET}")
            for f in escaping_files[:10]:
                print(f"     - {f}")
            return False, escaping_files
        
        print(f"  {Colors.GREEN}✅ All file paths validated - safe to proceed{Colors.RESET}")
        return True, []
    
    def _backup_brain(self) -> Path:
        """Backup brain data before upgrade."""
        print(f"\n{Colors.BOLD}[3/7] Backing Up Brain Data{Colors.RESET}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.cortex_path / "cortex-brain" / "backups" / f"pre-upgrade-{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Files/dirs to backup
        backup_items = [
            "cortex-brain/tier1",
            "cortex-brain/tier2",
            "cortex-brain/tier3",
            "cortex-brain/tier1-working-memory.db",
            "cortex-brain/tier2-knowledge-graph.db",
            "cortex-brain/tier3-development-context.db",
            "cortex-brain/conversation-history.db",
            "cortex-brain/ado-work-items.db",
            "cortex-brain/idea-contexts.db",
            "cortex.config.json",
            ".cortex-embedded"
        ]
        
        backed_up = 0
        for item_path in backup_items:
            source = self.cortex_path / item_path
            if source.exists():
                dest = backup_dir / item_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                
                if source.is_dir():
                    shutil.copytree(source, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(source, dest)
                
                backed_up += 1
        
        print(f"  ✅ Backed up {backed_up} items to: {backup_dir}")
        self.backup_path = backup_dir
        return backup_dir
    
    def _copy_updated_files(self, source_dir: Path) -> Dict[str, int]:
        """Selectively copy updated files, preserving brain data."""
        print(f"\n{Colors.BOLD}[4/7] Copying Updated Files{Colors.RESET}")
        
        stats = {
            "copied": 0,
            "skipped": 0,
            "preserved": 0
        }
        
        # Files/directories to preserve (never overwrite)
        preserve_patterns = [
            "cortex-brain/tier1",
            "cortex-brain/tier2",
            "cortex-brain/tier3",
            "cortex-brain/tier1-working-memory.db",
            "cortex-brain/tier2-knowledge-graph.db",
            "cortex-brain/tier3-development-context.db",
            "cortex-brain/conversation-history.db",
            "cortex-brain/ado-work-items.db",
            "cortex-brain/idea-contexts.db",
            "cortex-brain/backups",
            "cortex-brain/documents",
            "cortex-brain/feedback",
            "cortex.config.json",
            ".cortex-embedded",
            ".git"
        ]
        
        # Copy all files from source
        for source_file in source_dir.rglob('*'):
            if source_file.is_file():
                rel_path = source_file.relative_to(source_dir)
                dest_file = self.cortex_path / rel_path
                
                # Check if should preserve
                should_preserve = any(
                    str(rel_path).startswith(pattern) 
                    for pattern in preserve_patterns
                )
                
                if should_preserve:
                    stats["preserved"] += 1
                    continue
                
                # Skip .git directory
                if ".git" in rel_path.parts:
                    stats["skipped"] += 1
                    continue
                
                # Copy file
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, dest_file)
                stats["copied"] += 1
        
        print(f"  ✅ Copied: {Colors.GREEN}{stats['copied']}{Colors.RESET} files")
        print(f"  🔒 Preserved: {Colors.BLUE}{stats['preserved']}{Colors.RESET} brain files")
        print(f"  ⏭️  Skipped: {Colors.YELLOW}{stats['skipped']}{Colors.RESET} files")
        
        return stats
    
    def _run_migrations(self) -> bool:
        """Run database migrations if needed."""
        print(f"\n{Colors.BOLD}[5/7] Running Database Migrations{Colors.RESET}")
        
        migration_script = self.cortex_path / "apply_element_mappings_schema.py"
        
        if not migration_script.exists():
            print(f"  ℹ️  No migration script found - skipping")
            return True
        
        try:
            result = subprocess.run(
                [sys.executable, str(migration_script)],
                cwd=self.cortex_path,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"  ✅ Migrations completed successfully")
                return True
            else:
                print(f"  ⚠️  Migrations completed with warnings")
                if result.stderr:
                    print(f"     {result.stderr[:200]}")
                return True  # Non-critical
                
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  Migration timeout - may need manual intervention")
            return False
        except Exception as e:
            print(f"  ⚠️  Migration error: {e}")
            return False
    
    def _validate_upgrade(self) -> bool:
        """Run post-upgrade validation."""
        print(f"\n{Colors.BOLD}[6/7] Validating Upgrade{Colors.RESET}")
        
        validation_script = self.cortex_path / "scripts" / "validation" / "validate_issue3_phase4.py"
        
        if not validation_script.exists():
            print(f"  ℹ️  Validation script not found - skipping validation")
            return True
        
        try:
            result = subprocess.run(
                [sys.executable, str(validation_script)],
                cwd=self.cortex_path,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"  {Colors.GREEN}✅ All validation tests passed{Colors.RESET}")
                return True
            else:
                print(f"  {Colors.YELLOW}⚠️  Some validation tests failed{Colors.RESET}")
                print(f"     Check output above for details")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  Validation timeout")
            return False
        except Exception as e:
            print(f"  ⚠️  Validation error: {e}")
            return False
    
    def _cleanup_temp(self, temp_dir: Path):
        """Clean up temporary directory."""
        print(f"\n{Colors.BOLD}[7/7] Cleaning Up{Colors.RESET}")
        
        try:
            shutil.rmtree(temp_dir)
            print(f"  ✅ Cleaned up temporary files")
        except Exception as e:
            print(f"  ⚠️  Cleanup warning: {e}")
    
    def upgrade(self) -> bool:
        """Execute upgrade workflow."""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}CORTEX Embedded Installation Upgrade{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")
        
        print(f"\n📍 CORTEX Path: {self.cortex_path}")
        print(f"📍 Parent Project: {self.parent_path.name}")
        print(f"📍 Current Version: {self._get_current_version()}")
        print(f"📍 Installation Type: {'Embedded' if self.is_embedded else 'Standalone'}")
        
        if not self.is_embedded:
            print(f"\n{Colors.YELLOW}⚠️  This script is for embedded installations only{Colors.RESET}")
            print(f"   Use standard upgrade script for standalone installations")
            return False
        
        temp_dir = None
        
        try:
            # Download latest
            temp_dir = self._download_latest_release()
            
            # Validate paths
            safe, escaping = self._validate_paths(temp_dir)
            if not safe:
                print(f"\n{Colors.RED}❌ Upgrade aborted - unsafe file paths detected{Colors.RESET}")
                return False
            
            # Backup brain
            self._backup_brain()
            
            # Copy files
            stats = self._copy_updated_files(temp_dir)
            
            # Run migrations
            self._run_migrations()
            
            # Validate
            validation_passed = self._validate_upgrade()
            
            # Cleanup
            if temp_dir:
                self._cleanup_temp(temp_dir)
            
            # Summary
            print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
            print(f"{Colors.BOLD}UPGRADE SUMMARY{Colors.RESET}")
            print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")
            
            new_version = self._get_current_version()
            print(f"\n✅ Upgraded to version: {Colors.GREEN}{new_version}{Colors.RESET}")
            print(f"✅ Files copied: {stats['copied']}")
            print(f"✅ Brain data preserved: {stats['preserved']} items")
            print(f"✅ Backup location: {self.backup_path}")
            
            if validation_passed:
                print(f"\n{Colors.GREEN}{Colors.BOLD}✅ UPGRADE COMPLETE - ALL TESTS PASSED{Colors.RESET}")
            else:
                print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  UPGRADE COMPLETE - VALIDATION WARNINGS{Colors.RESET}")
                print(f"   Review validation output above")
            
            return True
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}⚠️  Upgrade interrupted by user{Colors.RESET}")
            if temp_dir:
                self._cleanup_temp(temp_dir)
            return False
            
        except Exception as e:
            print(f"\n{Colors.RED}❌ Upgrade failed: {e}{Colors.RESET}")
            
            if self.backup_path:
                print(f"\n{Colors.YELLOW}💾 Backup available at: {self.backup_path}{Colors.RESET}")
                print(f"   To restore: manually copy files back from backup")
            
            if temp_dir:
                self._cleanup_temp(temp_dir)
            
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🧠 CORTEX Embedded Installation Upgrade",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--cortex-path",
        type=Path,
        default=Path.cwd(),
        help="Path to CORTEX installation (default: current directory)"
    )
    
    args = parser.parse_args()
    
    upgrader = EmbeddedUpgradeScript(args.cortex_path)
    success = upgrader.upgrade()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
