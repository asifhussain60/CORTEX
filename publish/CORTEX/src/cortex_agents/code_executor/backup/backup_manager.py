"""Backup manager for file operations."""

import os
import shutil
import tempfile
from typing import Optional
from datetime import datetime


class BackupManager:
    """Manages file backups for safe operations."""
    
    def __init__(self, operation_id: Optional[str] = None):
        """
        Initialize backup manager.
        
        Args:
            operation_id: Optional operation identifier for backup directory
        """
        self.operation_id = operation_id or f"op_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.backup_dir = None
    
    def create_backup_dir(self) -> str:
        """
        Create a temporary backup directory.
        
        Returns:
            Path to backup directory
        """
        if not self.backup_dir:
            self.backup_dir = tempfile.mkdtemp(prefix=f"cortex_backup_{self.operation_id}_")
        return self.backup_dir
    
    def get_backup_dir(self) -> Optional[str]:
        """
        Get the current backup directory path.
        
        Returns:
            Path to backup directory, or None if not created
        """
        return self.backup_dir
    
    def backup_file(self, file_path: str) -> Optional[str]:
        """
        Backup a file to the backup directory.
        
        Args:
            file_path: Path to backup
        
        Returns:
            Path to backup file, or None on failure
        """
        if not file_path or not os.path.exists(file_path):
            return None
        
        # Ensure backup directory exists
        if not self.backup_dir:
            self.create_backup_dir()
        
        try:
            # Create relative path structure in backup
            rel_path = os.path.basename(file_path)
            backup_path = os.path.join(self.backup_dir, rel_path)
            
            # Copy file
            shutil.copy2(file_path, backup_path)
            
            return backup_path
            
        except Exception as e:
            # Silently fail - backup is optional
            return None
    
    def restore_file(self, backup_path: str, original_path: str) -> bool:
        """
        Restore a file from backup.
        
        Args:
            backup_path: Path to backup file
            original_path: Path to restore to
        
        Returns:
            True if restore succeeded
        """
        if not backup_path or not os.path.exists(backup_path):
            return False
        
        try:
            shutil.copy2(backup_path, original_path)
            return True
        except Exception:
            return False
    
    def rollback_all(self) -> bool:
        """
        Rollback all changes from backup directory.
        
        Note: This is a simplified implementation.
        Real implementation would need to track original paths.
        
        Returns:
            True if rollback information is available
        """
        if not self.backup_dir or not os.path.exists(self.backup_dir):
            return False
        
        # In real implementation, would restore all files
        # For now, just indicate backup is available
        return True
    
    def cleanup(self) -> None:
        """Clean up backup directory."""
        if self.backup_dir and os.path.exists(self.backup_dir):
            try:
                shutil.rmtree(self.backup_dir)
            except Exception:
                pass  # Best effort cleanup
