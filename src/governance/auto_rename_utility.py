"""
Auto-rename utility for fixing file naming violations.

Provides safe rename operations with collision detection and dry-run mode.
"""

from pathlib import Path
from typing import Union, Dict
from src.governance.naming_convention_enforcer import NamingConventionEnforcer


class AutoRenameUtility:
    """
    Automatically renames files to follow naming conventions.
    
    Usage:
        utility = AutoRenameUtility()
        new_path = utility.rename("userService.py", dry_run=False)
    """
    
    def __init__(self):
        """Initialize utility with enforcer."""
        self.enforcer = NamingConventionEnforcer()
    
    def rename(self, filepath: Union[str, Path], dry_run: bool = True) -> Path:
        """
        Rename file to follow naming convention.
        
        Args:
            filepath: File to rename
            dry_run: If True, only return suggested name without renaming
            
        Returns:
            New filepath (or suggested filepath if dry_run=True)
        """
        filepath = Path(filepath)
        
        # Check if already valid
        if self.enforcer.check(filepath.name):
            return filepath
        
        # Get suggested name
        suggested_name = self.enforcer.suggest_name(filepath.name)
        new_path = filepath.parent / suggested_name
        
        if dry_run:
            return new_path
        
        # Check for collision
        if new_path.exists() and new_path != filepath:
            raise FileExistsError(f"Target file already exists: {new_path}")
        
        # Perform rename
        filepath.rename(new_path)
        return new_path
    
    def would_collide(self, filepath: Union[str, Path]) -> bool:
        """
        Check if renaming would cause a collision.
        
        Args:
            filepath: File to check
            
        Returns:
            True if collision would occur
        """
        filepath = Path(filepath)
        
        # Get suggested name
        suggested_name = self.enforcer.suggest_name(filepath.name)
        new_path = filepath.parent / suggested_name
        
        # Check if target exists and is different file
        return new_path.exists() and new_path != filepath
    
    def batch_rename(self, filepaths: list, dry_run: bool = True) -> Dict[str, dict]:
        """
        Rename multiple files.
        
        Args:
            filepaths: List of files to rename
            dry_run: If True, only suggest names without renaming
            
        Returns:
            Dict mapping original path to result
        """
        results = {}
        
        for filepath in filepaths:
            filepath = Path(filepath)
            
            try:
                new_path = self.rename(filepath, dry_run=dry_run)
                results[str(filepath)] = {
                    "success": True,
                    "new_path": str(new_path),
                    "renamed": new_path != filepath
                }
            except Exception as e:
                results[str(filepath)] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
