"""
CORTEX EPM - Cleanup Manager Module
Manages safe destructive cleanup of generated documentation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
import shutil
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class CleanupManager:
    """Manages backup and cleanup of generated documentation"""
    
    def __init__(self, root_path: Path, dry_run: bool = False):
        self.root_path = root_path
        self.docs_path = root_path / "docs"
        self.dry_run = dry_run
        
        # Paths to preserve (never delete)
        self.preserve_paths = [
            "index.md",
            "assets/",
            "stylesheets/",
            ".gitkeep"
        ]
    
    def create_backup(self, timestamp: str) -> Path:
        """Create backup of current documentation"""
        backup_path = self.root_path / f"docs-backup-{timestamp}"
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create backup: {backup_path}")
            return backup_path
        
        if self.docs_path.exists():
            logger.info(f"Creating backup: {backup_path}")
            shutil.copytree(self.docs_path, backup_path)
            logger.info(f"✓ Backup created: {backup_path}")
        else:
            logger.warning("docs/ does not exist, skipping backup")
        
        return backup_path
    
    def clear_generated_content(self, keep_old: bool = False) -> Dict:
        """
        Clear generated documentation content
        
        Args:
            keep_old: If True, move to docs-old/ instead of deleting
        
        Returns:
            Dictionary with cleanup statistics
        """
        files_removed = 0
        space_freed_mb = 0.0
        
        if self.dry_run:
            logger.info("[DRY RUN] Would clear generated content")
            return {"files_removed": 0, "space_freed_mb": 0.0}
        
        # Directories to clear (but preserve .gitkeep)
        dirs_to_clear = [
            self.docs_path / "diagrams",
            self.docs_path / "images" / "diagrams",
            self.docs_path / "getting-started",
            self.docs_path / "architecture",
            self.docs_path / "operations",
            self.docs_path / "plugins",
            self.docs_path / "reference",
            self.docs_path / "guides"
        ]
        
        for dir_path in dirs_to_clear:
            if not dir_path.exists():
                continue
            
            for item in dir_path.rglob("*"):
                if item.is_file():
                    # Skip preserved files
                    if any(preserve in str(item) for preserve in self.preserve_paths):
                        continue
                    
                    # Calculate size before removal
                    space_freed_mb += item.stat().st_size / (1024 * 1024)
                    
                    if keep_old:
                        # Move to docs-old/
                        old_path = self.root_path / "docs-old" / item.relative_to(self.docs_path)
                        old_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(item), str(old_path))
                    else:
                        # Delete
                        item.unlink()
                    
                    files_removed += 1
        
        logger.info(f"✓ Removed {files_removed} files ({space_freed_mb:.2f} MB)")
        
        return {
            "files_removed": files_removed,
            "space_freed_mb": space_freed_mb
        }
    
    def restore_from_backup(self, backup_path: Path):
        """Restore documentation from backup (rollback)"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would restore from: {backup_path}")
            return
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        logger.info(f"Restoring from backup: {backup_path}")
        
        # Remove current docs/
        if self.docs_path.exists():
            shutil.rmtree(self.docs_path)
        
        # Restore from backup
        shutil.copytree(backup_path, self.docs_path)
        
        logger.info("✓ Restore complete")
