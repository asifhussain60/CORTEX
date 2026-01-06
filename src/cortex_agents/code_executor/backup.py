"""
BackupManager - File backup and rollback for safe code execution

Purpose: Provides automatic backup and recovery for file operations
Author: CORTEX AutoGen
Created: 2026-01-05
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class BackupManager:
    """
    Manages file backups for safe code execution operations.
    
    Features:
    - Automatic backup before file modifications
    - Rollback capability
    - Backup expiration and cleanup
    - Multiple backup retention
    """
    
    def __init__(self, backup_root: Optional[Path] = None):
        """
        Initialize BackupManager.
        
        Args:
            backup_root: Root directory for backups (default: .cortex/backups)
        """
        if backup_root is None:
            # Default to .cortex/backups in current working directory
            backup_root = Path.cwd() / ".cortex" / "backups"
        
        self.backup_root = Path(backup_root)
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        # Track active backups for this session
        self._backup_map: Dict[str, Path] = {}
        
        logger.info(f"BackupManager initialized: {self.backup_root}")
    
    def backup_file(self, file_path: Path) -> Optional[Path]:
        """
        Create backup of a file before modification.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Path to backup file, or None if backup failed
        """
        try:
            file_path = Path(file_path).resolve()
            
            if not file_path.exists():
                logger.warning(f"Cannot backup non-existent file: {file_path}")
                return None
            
            # Create timestamp-based backup directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.backup_root / f"backup_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Preserve relative path structure
            try:
                # Try to make relative to cwd
                rel_path = file_path.relative_to(Path.cwd())
            except ValueError:
                # If not relative to cwd, use absolute path structure
                rel_path = Path(*file_path.parts[1:])  # Remove root /
            
            backup_path = backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(file_path, backup_path)
            
            # Track backup
            self._backup_map[str(file_path)] = backup_path
            
            logger.info(f"✅ Backed up: {file_path} → {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"❌ Backup failed for {file_path}: {e}")
            return None
    
    def restore_file(self, file_path: Path) -> bool:
        """
        Restore file from most recent backup.
        
        Args:
            file_path: Path to file to restore
            
        Returns:
            True if restored successfully, False otherwise
        """
        try:
            file_path_str = str(Path(file_path).resolve())
            
            if file_path_str not in self._backup_map:
                logger.warning(f"No backup found for: {file_path}")
                return False
            
            backup_path = self._backup_map[file_path_str]
            
            if not backup_path.exists():
                logger.error(f"Backup file missing: {backup_path}")
                return False
            
            # Restore file
            shutil.copy2(backup_path, file_path)
            
            logger.info(f"✅ Restored: {file_path} from {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Restore failed for {file_path}: {e}")
            return False
    
    def has_backup(self, file_path: Path) -> bool:
        """
        Check if a file has a backup available.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if backup exists
        """
        file_path_str = str(Path(file_path).resolve())
        return file_path_str in self._backup_map
    
    def get_backup_path(self, file_path: Path) -> Optional[Path]:
        """
        Get backup path for a file.
        
        Args:
            file_path: Original file path
            
        Returns:
            Backup path if exists, None otherwise
        """
        file_path_str = str(Path(file_path).resolve())
        return self._backup_map.get(file_path_str)
    
    def list_backups(self) -> Dict[str, Path]:
        """
        List all active backups in this session.
        
        Returns:
            Dict mapping original paths to backup paths
        """
        return self._backup_map.copy()
    
    def cleanup_old_backups(self, days: int = 7) -> int:
        """
        Remove backups older than specified days.
        
        Args:
            days: Maximum age of backups to keep
            
        Returns:
            Number of backups removed
        """
        removed_count = 0
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        
        try:
            for backup_dir in self.backup_root.iterdir():
                if not backup_dir.is_dir():
                    continue
                
                # Check directory creation time
                dir_time = backup_dir.stat().st_ctime
                
                if dir_time < cutoff_time:
                    shutil.rmtree(backup_dir)
                    removed_count += 1
                    logger.info(f"🗑️  Removed old backup: {backup_dir}")
            
            logger.info(f"✅ Cleanup complete: {removed_count} old backups removed")
            return removed_count
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return removed_count
    
    def clear_session(self):
        """Clear the current session's backup tracking."""
        self._backup_map.clear()
        logger.info("Session backup tracking cleared")


# Global instance for convenience
_global_backup_manager: Optional[BackupManager] = None


def get_backup_manager() -> BackupManager:
    """Get or create global BackupManager instance."""
    global _global_backup_manager
    
    if _global_backup_manager is None:
        _global_backup_manager = BackupManager()
    
    return _global_backup_manager
