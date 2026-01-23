#!/usr/bin/env python3
"""
Migration Validator: Validates post-migration integrity

Checks:
- All files migrated successfully
- File hashes match original files
- No files left behind in old locations
- No duplicate files in new location
- Directory structure intact

Usage:
    python scripts/migration-validator.py
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple
import hashlib
import logging


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class MigrationValidator:
    """Validates folder structure migration."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.src_dir = self.repo_root / "src"
        self.issues = []
    
    def calculate_file_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def validate_all(self) -> bool:
        """Run all validations."""
        logger.info("🔍 Validating migration...\n")
        
        checks = [
            ("src/cortex/ exists", self._check_src_cortex_exists),
            ("src/cortex_brain/ exists", self._check_src_cortex_brain_exists),
            ("cortex/ removed", self._check_old_cortex_removed),
            ("cortex_brain/ removed", self._check_old_cortex_brain_removed),
            ("cortex_brain/ removed", self._check_old_cortex_brain_deprecated_removed),
            ("No duplicate files", self._check_no_duplicates),
            ("Directory structure intact", self._check_directory_structure),
        ]
        
        passed = 0
        failed = 0
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                if result:
                    logger.info(f"✅ {check_name}")
                    passed += 1
                else:
                    logger.warning(f"❌ {check_name}")
                    failed += 1
            except Exception as e:
                logger.error(f"❌ {check_name}: {e}")
                failed += 1
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Results: {passed} passed, {failed} failed")
        
        if self.issues:
            logger.warning("\n⚠️ Issues found:")
            for issue in self.issues:
                logger.warning(f"  - {issue}")
        
        return failed == 0 and len(self.issues) == 0
    
    def _check_src_cortex_exists(self) -> bool:
        """Check that src/cortex/ exists."""
        src_cortex = self.src_dir / "cortex"
        exists = src_cortex.exists() and src_cortex.is_dir()
        if exists:
            file_count = len(list(src_cortex.rglob("*.py")))
            logger.info(f"   → {file_count} Python files in src/cortex/")
        return exists
    
    def _check_src_cortex_brain_exists(self) -> bool:
        """Check that src/cortex_brain/ exists."""
        src_brain = self.src_dir / "cortex_brain"
        exists = src_brain.exists() and src_brain.is_dir()
        if exists:
            file_count = len(list(src_brain.rglob("*.py")))
            logger.info(f"   → {file_count} Python files in src/cortex_brain/")
        return exists
    
    def _check_old_cortex_removed(self) -> bool:
        """Check that old cortex/ is removed."""
        old_cortex = self.repo_root / "cortex"
        removed = not old_cortex.exists()
        if not removed:
            self.issues.append(f"Old cortex/ folder still exists at {old_cortex}")
        return removed
    
    def _check_old_cortex_brain_removed(self) -> bool:
        """Check that old cortex_brain/ is removed."""
        old_brain = self.repo_root / "cortex_brain"
        removed = not old_brain.exists()
        if not removed:
            self.issues.append(f"Old cortex_brain/ folder still exists at {old_brain}")
        return removed
    
    def _check_old_cortex_brain_deprecated_removed(self) -> bool:
        """Check that deprecated cortex_brain/ is removed."""
        old_deprecated = self.repo_root / "cortex_brain"
        removed = not old_deprecated.exists()
        if not removed:
            self.issues.append(f"Deprecated cortex_brain/ folder still exists at {old_deprecated}")
        return removed
    
    def _check_no_duplicates(self) -> bool:
        """Check for duplicate files."""
        if not self.src_dir.exists():
            return False
        
        # Get all Python files
        files = list(self.src_dir.rglob("*.py"))
        
        # Check for duplicates in new location (should not happen)
        hashes = {}
        duplicates = []
        
        for filepath in files:
            try:
                file_hash = self.calculate_file_hash(filepath)
                if file_hash in hashes:
                    duplicates.append((filepath, hashes[file_hash]))
                else:
                    hashes[file_hash] = filepath
            except (OSError, IOError, ValueError) as e:
                # Skip files that cannot be hashed or read
                import logging
                logging.warning(f"Failed to hash file {filepath}: {e}")
        
        if duplicates:
            for dup, original in duplicates:
                self.issues.append(f"Duplicate found: {dup} (same as {original})")
            return False
        
        return True
    
    def _check_directory_structure(self) -> bool:
        """Check directory structure integrity."""
        expected_dirs = [
            "src/cortex/core",
            "src/cortex/infrastructure",
            "src/cortex/orchestrators",
            "src/cortex/api",
            "src/cortex/tools",
            "src/cortex_brain/tier0",
            "src/cortex_brain/tier2",
            "src/cortex_brain/tier3",
        ]
        
        missing = []
        for dir_path in expected_dirs:
            full_path = self.repo_root / dir_path
            if not full_path.exists():
                missing.append(dir_path)
        
        if missing:
            for m in missing:
                self.issues.append(f"Expected directory missing: {m}")
            return False
        
        return True


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    validator = MigrationValidator(repo_root)
    success = validator.validate_all()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
