"""Root Database Cleaner

Removes .db files from repository root (governance violation).

Author: CORTEX Framework
Phase: PHASE-VACUUM-REFACTOR S1
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from pathlib import Path
from typing import List
import os

from cortex_intelligence.memory.tier1_learned.orchestrators.cleaners.interface import (
    CleanerInterface,
    CleanupResult,
)


class RootDatabaseCleaner(CleanerInterface):
    """Cleaner for .db files in repository root.
    
    Removes database files from root to comply with CORE-028.
    """
    
    def get_name(self) -> str:
        """Get cleaner name.
        
        Returns:
            Cleaner name
        """
        return "RootDatabaseCleaner"
    
    def get_description(self) -> str:
        """Get cleaner description.
        
        Returns:
            Description
        """
        return "Removes .db files from repository root (CORE-028 violation)"
    
    def clean(self, repo_path: Path, dry_run: bool = False) -> CleanupResult:
        """Execute cleanup operation.
        
        Args:
            repo_path: Path to repository root
            dry_run: If True, don't actually delete files
        
        Returns:
            Cleanup result
        """
        targets = self.get_targets(repo_path)
        
        removed = []
        skipped = []
        errors = []
        bytes_freed = 0
        
        for file_path in targets:
            try:
                # Get file size before deletion
                file_size = file_path.stat().st_size
                
                if not dry_run:
                    file_path.unlink()
                    removed.append(file_path)
                    bytes_freed += file_size
                else:
                    skipped.append(file_path)
                    
            except Exception as e:
                errors.append(f"Failed to remove {file_path}: {e}")
                skipped.append(file_path)
        
        return CleanupResult(
            files_removed=removed,
            files_skipped=skipped,
            bytes_freed=bytes_freed,
            errors=errors,
        )
    
    def get_targets(self, repo_path: Path) -> List[Path]:
        """Get list of .db files in root.
        
        Args:
            repo_path: Path to repository root
        
        Returns:
            List of .db file paths in root
        """
        targets = []
        
        for item in repo_path.iterdir():
            if item.is_file() and item.suffix == ".db":
                targets.append(item)
        
        return targets
