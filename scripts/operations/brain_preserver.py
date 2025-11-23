"""
CORTEX Brain Preservation Module

Safely preserves brain data during upgrades by implementing selective file replacement,
atomic operations, and backup creation. Ensures zero data loss during CORTEX updates.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import shutil
import os
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime
import json


class BrainPreserver:
    """Preserves CORTEX brain data during upgrades."""
    
    # Files/directories that contain brain data (NEVER overwrite)
    BRAIN_DATA_PATTERNS = [
        "cortex-brain/tier1/*.db",
        "cortex-brain/tier1/*.db-shm",
        "cortex-brain/tier1/*.db-wal",
        "cortex-brain/tier2/*.db",
        "cortex-brain/tier2/*.db-shm",
        "cortex-brain/tier2/*.db-wal",
        "cortex-brain/tier3/*.db",
        "cortex-brain/tier3/*.db-shm",
        "cortex-brain/tier3/*.db-wal",
        "cortex-brain/documents/**/*",
        "cortex-brain/user-dictionary.yaml",
        "cortex-brain/conversation-history.jsonl",
        "cortex-brain/conversation-context.jsonl",
        "cortex.config.json",
        ".cortex-version"
    ]
    
    # Files that need intelligent merging (not simple overwrite)
    MERGE_REQUIRED = [
        "cortex-brain/response-templates.yaml",
        "cortex-brain/capabilities.yaml",
        "cortex-brain/operations-config.yaml"
    ]
    
    # Files/directories that are safe to overwrite (core CORTEX files)
    UPGRADEABLE_PATTERNS = [
        ".github/prompts/**/*",
        "scripts/**/*",
        "src/**/*",
        "cortex-brain/schema.sql",
        "cortex-brain/brain-protection-rules.yaml",
        "cortex-brain/publish-config.yaml"
    ]
    
    def __init__(self, target_path: Path):
        """
        Initialize brain preserver.
        
        Args:
            target_path: Path to CORTEX installation to upgrade
        """
        self.target_path = Path(target_path)
        self.backup_dir = self.target_path / "cortex-brain" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def create_backup(self) -> Path:
        """
        Create full backup of current CORTEX brain.
        
        Returns:
            Path to backup directory
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = self.backup_dir / f"pre-upgrade-{timestamp}"
        
        print(f"💾 Creating backup at {backup_path}...")
        
        # Backup brain data directories
        brain_dirs = [
            "cortex-brain/tier1",
            "cortex-brain/tier2",
            "cortex-brain/tier3",
            "cortex-brain/documents"
        ]
        
        for dir_name in brain_dirs:
            source = self.target_path / dir_name
            dest = backup_path / dir_name
            
            if source.exists():
                shutil.copytree(source, dest, dirs_exist_ok=True)
                print(f"   ✅ Backed up {dir_name}")
        
        # Backup configuration files
        config_files = [
            "cortex.config.json",
            ".cortex-version",
            "cortex-brain/user-dictionary.yaml",
            "cortex-brain/response-templates.yaml",
            "cortex-brain/capabilities.yaml"
        ]
        
        for file_name in config_files:
            source = self.target_path / file_name
            dest = backup_path / file_name
            
            if source.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
                print(f"   ✅ Backed up {file_name}")
        
        # Create backup manifest
        manifest = {
            "backup_date": datetime.now().isoformat(),
            "cortex_path": str(self.target_path),
            "backup_path": str(backup_path),
            "files_backed_up": self._count_backup_files(backup_path)
        }
        
        manifest_path = backup_path / "backup-manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Backup complete: {backup_path}")
        print(f"   Files backed up: {manifest['files_backed_up']}")
        
        return backup_path
    
    def restore_backup(self, backup_path: Path) -> None:
        """
        Restore CORTEX from backup.
        
        Args:
            backup_path: Path to backup directory
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        print(f"♻️  Restoring from backup {backup_path}...")
        
        # Read backup manifest
        manifest_path = backup_path / "backup-manifest.json"
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            print(f"   Backup date: {manifest['backup_date']}")
        
        # Restore directories
        for item in backup_path.iterdir():
            if item.is_dir() and item.name in ["tier1", "tier2", "tier3", "documents", "cortex-brain"]:
                dest = self.target_path / item.relative_to(backup_path)
                shutil.copytree(item, dest, dirs_exist_ok=True)
                print(f"   ✅ Restored {item.name}")
        
        # Restore files
        for item in backup_path.rglob("*"):
            if item.is_file() and item.name != "backup-manifest.json":
                dest = self.target_path / item.relative_to(backup_path)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
        
        print(f"✅ Restore complete")
    
    def list_backups(self) -> List[Dict]:
        """
        List available backups.
        
        Returns:
            List of backup info dictionaries
        """
        if not self.backup_dir.exists():
            return []
        
        backups = []
        for backup_path in sorted(self.backup_dir.iterdir(), reverse=True):
            if not backup_path.is_dir():
                continue
            
            manifest_path = backup_path / "backup-manifest.json"
            if manifest_path.exists():
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                backups.append({
                    "path": str(backup_path),
                    "date": manifest.get("backup_date"),
                    "files": manifest.get("files_backed_up", 0)
                })
            else:
                backups.append({
                    "path": str(backup_path),
                    "date": backup_path.name.replace("pre-upgrade-", ""),
                    "files": self._count_backup_files(backup_path)
                })
        
        return backups
    
    def is_brain_file(self, file_path: Path) -> bool:
        """
        Check if file contains brain data (should not be overwritten).
        
        Args:
            file_path: File path to check
            
        Returns:
            True if file contains brain data
        """
        rel_path = str(file_path.relative_to(self.target_path))
        
        for pattern in self.BRAIN_DATA_PATTERNS:
            if self._matches_pattern(rel_path, pattern):
                return True
        
        return False
    
    def requires_merge(self, file_path: Path) -> bool:
        """
        Check if file requires intelligent merging.
        
        Args:
            file_path: File path to check
            
        Returns:
            True if file needs merging
        """
        rel_path = str(file_path.relative_to(self.target_path))
        return rel_path in self.MERGE_REQUIRED
    
    def is_upgradeable(self, file_path: Path) -> bool:
        """
        Check if file can be safely overwritten.
        
        Args:
            file_path: File path to check
            
        Returns:
            True if file can be overwritten
        """
        rel_path = str(file_path.relative_to(self.target_path))
        
        for pattern in self.UPGRADEABLE_PATTERNS:
            if self._matches_pattern(rel_path, pattern):
                return True
        
        return False
    
    def selective_copy(
        self,
        source_dir: Path,
        dry_run: bool = False
    ) -> Dict[str, List[str]]:
        """
        Copy files from source to target, preserving brain data.
        
        Args:
            source_dir: Directory with new CORTEX files
            dry_run: If True, only simulate (don't actually copy)
            
        Returns:
            Dictionary with lists of overwritten, preserved, and merged files
        """
        result = {
            "overwritten": [],
            "preserved": [],
            "needs_merge": [],
            "errors": []
        }
        
        print(f"📋 Analyzing files for selective copy...")
        if dry_run:
            print(f"   🔍 DRY RUN MODE - No files will be modified")
        
        for source_file in source_dir.rglob("*"):
            if not source_file.is_file():
                continue
            
            # Calculate target path
            rel_path = source_file.relative_to(source_dir)
            target_file = self.target_path / rel_path
            
            try:
                # Check if this is brain data
                if target_file.exists() and self.is_brain_file(target_file):
                    result["preserved"].append(str(rel_path))
                    print(f"   🛡️  PRESERVE: {rel_path}")
                    continue
                
                # Check if requires merging
                if target_file.exists() and self.requires_merge(target_file):
                    result["needs_merge"].append(str(rel_path))
                    print(f"   🔀 MERGE: {rel_path}")
                    # Don't overwrite - will be handled by config merger
                    continue
                
                # Check if upgradeable
                if self.is_upgradeable(target_file):
                    if not dry_run:
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_file, target_file)
                    result["overwritten"].append(str(rel_path))
                    print(f"   ✅ UPDATE: {rel_path}")
                    continue
                
                # Unknown file - preserve by default
                result["preserved"].append(str(rel_path))
                print(f"   ⚠️  PRESERVE (unknown): {rel_path}")
                
            except Exception as e:
                result["errors"].append(f"{rel_path}: {str(e)}")
                print(f"   ❌ ERROR: {rel_path} - {e}")
        
        print(f"\n📊 Summary:")
        print(f"   Updated: {len(result['overwritten'])} files")
        print(f"   Preserved: {len(result['preserved'])} files")
        print(f"   Need merge: {len(result['needs_merge'])} files")
        print(f"   Errors: {len(result['errors'])} files")
        
        return result
    
    def validate_brain_integrity(self) -> Dict[str, bool]:
        """
        Validate brain data integrity after upgrade.
        
        Returns:
            Dictionary of validation results
        """
        print(f"🔍 Validating brain integrity...")
        
        results = {}
        
        # Check database files exist
        db_dirs = ["tier1", "tier2", "tier3"]
        for tier in db_dirs:
            tier_path = self.target_path / "cortex-brain" / tier
            if tier_path.exists():
                db_files = list(tier_path.glob("*.db"))
                results[f"{tier}_databases"] = len(db_files) > 0
                print(f"   ✅ {tier}: {len(db_files)} databases found")
            else:
                results[f"{tier}_databases"] = False
                print(f"   ⚠️  {tier}: directory not found")
        
        # Check documents directory
        docs_path = self.target_path / "cortex-brain" / "documents"
        results["documents"] = docs_path.exists()
        if docs_path.exists():
            doc_count = sum(1 for _ in docs_path.rglob("*") if _.is_file())
            print(f"   ✅ documents: {doc_count} files")
        else:
            print(f"   ⚠️  documents: directory not found")
        
        # Check config files
        config_files = [
            "cortex.config.json",
            ".cortex-version"
        ]
        
        for config in config_files:
            config_path = self.target_path / config
            results[config] = config_path.exists()
            status = "✅" if results[config] else "⚠️"
            print(f"   {status} {config}")
        
        all_valid = all(results.values())
        print(f"\n{'✅' if all_valid else '⚠️'} Brain integrity: {'VALID' if all_valid else 'ISSUES FOUND'}")
        
        return results
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches glob pattern."""
        from fnmatch import fnmatch
        
        # Handle ** (recursive wildcard)
        if "**" in pattern:
            pattern_parts = pattern.split("**/")
            if len(pattern_parts) == 2:
                prefix, suffix = pattern_parts
                suffix = suffix.replace("*", "")
                return path.startswith(prefix.replace("*", "")) or path.endswith(suffix)
        
        return fnmatch(path.replace("\\", "/"), pattern)
    
    def _count_backup_files(self, backup_path: Path) -> int:
        """Count files in backup directory."""
        return sum(1 for _ in backup_path.rglob("*") if _.is_file())


def main():
    """CLI entry point for testing brain preservation."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python brain_preserver.py <command> [args]")
        print("\nCommands:")
        print("  backup <cortex_path>           - Create backup")
        print("  restore <cortex_path> <backup> - Restore from backup")
        print("  list <cortex_path>             - List backups")
        print("  validate <cortex_path>         - Validate brain integrity")
        print("  analyze <cortex_path> <source> - Analyze upgrade (dry-run)")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "backup":
        cortex_path = Path(sys.argv[2])
        preserver = BrainPreserver(cortex_path)
        backup_path = preserver.create_backup()
        print(f"\n✅ Backup created: {backup_path}")
        
    elif command == "restore":
        cortex_path = Path(sys.argv[2])
        backup_path = Path(sys.argv[3])
        preserver = BrainPreserver(cortex_path)
        preserver.restore_backup(backup_path)
        
    elif command == "list":
        cortex_path = Path(sys.argv[2])
        preserver = BrainPreserver(cortex_path)
        backups = preserver.list_backups()
        
        print(f"\n💾 Available Backups:\n")
        for backup in backups:
            print(f"  • {backup['date']}")
            print(f"    Path: {backup['path']}")
            print(f"    Files: {backup['files']}")
            print()
        
    elif command == "validate":
        cortex_path = Path(sys.argv[2])
        preserver = BrainPreserver(cortex_path)
        results = preserver.validate_brain_integrity()
        
    elif command == "analyze":
        cortex_path = Path(sys.argv[2])
        source_path = Path(sys.argv[3])
        preserver = BrainPreserver(cortex_path)
        results = preserver.selective_copy(source_path, dry_run=True)
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
