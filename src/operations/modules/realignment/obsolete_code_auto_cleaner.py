"""
Obsolete Code Auto-Cleanup for CORTEX Align v2.0

Safely removes obsolete files with automatic backup creation.
Handles deletion of orphaned tests, deprecated scripts, and obsolete orchestrators.

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class CleanupResult:
    """Result of cleanup operation."""
    success: bool
    files_removed: List[Path] = field(default_factory=list)
    files_backed_up: List[Path] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    backup_dir: Optional[Path] = None
    space_freed_mb: float = 0.0


class ObsoleteCodeAutoCleaner:
    """Automatically removes obsolete code with safety backups."""
    
    def __init__(self, cortex_root: Path):
        """
        Initialize the auto-cleaner.
        
        Args:
            cortex_root: Root directory of CORTEX installation
        """
        self.cortex_root = cortex_root
        self.backup_root = cortex_root / "cortex-brain" / "backups" / "obsolete-code"
        self.backup_root.mkdir(parents=True, exist_ok=True)
    
    def create_backup_dir(self) -> Path:
        """
        Create timestamped backup directory.
        
        Returns:
            Path to backup directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.backup_root / f"cleanup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir
    
    def is_safe_to_delete(self, file_path: Path) -> tuple[bool, str]:
        """
        Check if file is safe to delete.
        
        Args:
            file_path: Path to file
        
        Returns:
            Tuple of (is_safe, reason)
        """
        # Safety checks
        if not file_path.exists():
            return False, "File does not exist"
        
        # Never delete from protected directories
        protected_keywords = ['tier0', 'tier1', 'tier2', 'tier3', 'brain-protection']
        if any(keyword in str(file_path).lower() for keyword in protected_keywords):
            return False, "Protected directory"
        
        # Never delete configuration files
        if file_path.suffix in ['.yaml', '.json', '.toml'] and file_path.name in [
            'cortex.config.json', 'brain-protection-rules.yaml', 'cortex-operations.yaml'
        ]:
            return False, "Critical configuration file"
        
        # Only delete Python files, test files, or known obsolete patterns
        allowed_patterns = ['.py', '.pyc', '_OLD', '_deprecated', '_backup', '_temp', '.bak', '~']
        if not any(pattern in str(file_path) for pattern in allowed_patterns):
            return False, "Not a safe deletion candidate"
        
        return True, "Safe to delete"
    
    def backup_file(self, file_path: Path, backup_dir: Path) -> Optional[Path]:
        """
        Backup a file before deletion.
        
        Args:
            file_path: Path to file to backup
            backup_dir: Directory to store backup
        
        Returns:
            Path to backed up file or None on error
        """
        try:
            # Preserve relative path structure
            rel_path = file_path.relative_to(self.cortex_root)
            backup_path = backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(file_path, backup_path)
            logger.debug(f"Backed up {rel_path} to {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to backup {file_path}: {e}")
            return None
    
    def delete_file(self, file_path: Path) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: Path to file to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path.unlink()
            logger.debug(f"Deleted {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {file_path}: {e}")
            return False
    
    def cleanup_files(
        self,
        files_to_remove: List[Path],
        dry_run: bool = False
    ) -> CleanupResult:
        """
        Clean up obsolete files with backup.
        
        Args:
            files_to_remove: List of files to remove
            dry_run: If True, don't actually delete files
        
        Returns:
            CleanupResult with details
        """
        result = CleanupResult(success=True)
        
        if not files_to_remove:
            logger.info("No files to clean up")
            return result
        
        # Create backup directory
        backup_dir = self.create_backup_dir()
        result.backup_dir = backup_dir
        
        logger.info(f"🧹 Cleaning up {len(files_to_remove)} obsolete files...")
        if dry_run:
            logger.info("   (DRY RUN - no files will be deleted)")
        
        space_freed = 0.0
        
        for file_path in files_to_remove:
            # Safety check
            is_safe, reason = self.is_safe_to_delete(file_path)
            if not is_safe:
                logger.warning(f"   ⚠️  Skipping {file_path.name}: {reason}")
                result.errors.append(f"Skipped {file_path}: {reason}")
                continue
            
            # Calculate size
            if file_path.exists():
                size_bytes = file_path.stat().st_size
                space_freed += size_bytes / (1024 * 1024)  # Convert to MB
            
            if dry_run:
                logger.info(f"   [DRY RUN] Would remove: {file_path.relative_to(self.cortex_root)}")
                result.files_removed.append(file_path)
                continue
            
            # Backup file
            backup_path = self.backup_file(file_path, backup_dir)
            if backup_path:
                result.files_backed_up.append(backup_path)
            else:
                result.errors.append(f"Failed to backup {file_path}")
                result.success = False
                continue
            
            # Delete file
            if self.delete_file(file_path):
                result.files_removed.append(file_path)
                logger.info(f"   ✅ Removed: {file_path.relative_to(self.cortex_root)}")
            else:
                result.errors.append(f"Failed to delete {file_path}")
                result.success = False
        
        result.space_freed_mb = round(space_freed, 2)
        
        # Summary
        if not dry_run:
            logger.info(f"   📦 Backup location: {backup_dir}")
            logger.info(f"   💾 Space freed: {result.space_freed_mb} MB")
            logger.info(f"   ✅ {len(result.files_removed)} files removed")
            if result.errors:
                logger.warning(f"   ⚠️  {len(result.errors)} errors occurred")
        
        return result
    
    def cleanup_obsolete_tests(
        self,
        obsolete_tests: List[Path],
        dry_run: bool = False
    ) -> CleanupResult:
        """
        Clean up obsolete test files.
        
        Args:
            obsolete_tests: List of test files to remove
            dry_run: If True, don't actually delete files
        
        Returns:
            CleanupResult
        """
        logger.info("🧪 Cleaning up obsolete tests...")
        return self.cleanup_files(obsolete_tests, dry_run)
    
    def cleanup_obsolete_scripts(
        self,
        obsolete_scripts: List[Path],
        dry_run: bool = False
    ) -> CleanupResult:
        """
        Clean up obsolete script files.
        
        Args:
            obsolete_scripts: List of script files to remove
            dry_run: If True, don't actually delete files
        
        Returns:
            CleanupResult
        """
        logger.info("📜 Cleaning up obsolete scripts...")
        return self.cleanup_files(obsolete_scripts, dry_run)
    
    def cleanup_obsolete_orchestrators(
        self,
        obsolete_orchestrators: List[Path],
        dry_run: bool = False
    ) -> CleanupResult:
        """
        Clean up obsolete orchestrator files.
        
        Args:
            obsolete_orchestrators: List of orchestrator files to remove
            dry_run: If True, don't actually delete files
        
        Returns:
            CleanupResult
        """
        logger.info("🎭 Cleaning up obsolete orchestrators...")
        return self.cleanup_files(obsolete_orchestrators, dry_run)
    
    def rollback_cleanup(self, backup_dir: Path) -> bool:
        """
        Rollback a cleanup operation by restoring from backup.
        
        Args:
            backup_dir: Path to backup directory
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Rolling back cleanup from {backup_dir}...")
            
            # Restore all files from backup
            for backup_file in backup_dir.rglob('*'):
                if backup_file.is_file():
                    rel_path = backup_file.relative_to(backup_dir)
                    original_path = self.cortex_root / rel_path
                    original_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup_file, original_path)
                    logger.info(f"   ✅ Restored: {rel_path}")
            
            logger.info("✅ Rollback complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
