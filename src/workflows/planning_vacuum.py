"""
PlanningVacuum - Cleanup and maintenance for planning artifacts

Handles post-migration cleanup operations:
- Remove empty directories
- Fix broken cross-references
- Archive orphaned files
- Generate cleanup reports

Author: GitHub Copilot
Created: 2025-12-14
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import yaml
import re

logger = logging.getLogger(__name__)


class CleanupAction(Enum):
    """Types of cleanup actions."""
    REMOVE_EMPTY_DIR = "remove_empty_directory"
    ARCHIVE_ORPHAN = "archive_orphaned_file"
    FIX_REFERENCE = "fix_broken_reference"
    UPDATE_REFERENCE = "update_cross_reference"


@dataclass
class CleanupReport:
    """Report of cleanup operations."""
    directories_removed: int = 0
    orphans_archived: int = 0
    references_fixed: int = 0
    
    def __str__(self) -> str:
        """Format report as string."""
        return f"""Cleanup Report:
- Directories removed: {self.directories_removed}
- Orphaned files archived: {self.orphans_archived}
- References fixed: {self.references_fixed}
"""


class PlanningVacuum:
    """
    Vacuum and cleanup operations for planning artifacts.
    
    Features:
    - Remove empty directories recursively
    - Fix broken cross-references
    - Archive orphaned files
    - Generate cleanup reports
    """
    
    PROTECTED_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules"}
    
    def __init__(self, root_directory: Path):
        """
        Initialize vacuum.
        
        Args:
            root_directory: Root directory to clean
            
        Raises:
            ValueError: If directory doesn't exist
        """
        self.root_directory = Path(root_directory)
        
        if not self.root_directory.exists():
            raise ValueError(f"Directory not found: {self.root_directory}")
        
        self._action_history: List[tuple] = []
        self._report = CleanupReport()
    
    def find_empty_directories(self) -> List[Path]:
        """
        Find all empty directories.
        
        Returns:
            List of empty directory paths
        """
        empty_dirs = []
        
        for dirpath in self.root_directory.rglob("*"):
            if not dirpath.is_dir():
                continue
            
            # Skip protected directories
            if dirpath.name in self.PROTECTED_DIRS:
                continue
            
            # Check if directory is empty (no files or subdirectories)
            try:
                if not any(dirpath.iterdir()):
                    empty_dirs.append(dirpath)
            except (PermissionError, OSError):
                logger.warning(f"Cannot access directory: {dirpath}")
        
        return empty_dirs
    
    def vacuum_empty_directories(self) -> List[Path]:
        """
        Remove empty directories recursively.
        
        Returns:
            List of removed directory paths
        """
        removed = []
        
        # Keep removing until no more empty directories found
        while True:
            empty_dirs = self.find_empty_directories()
            
            if not empty_dirs:
                break
            
            # Remove in reverse order (deepest first)
            for directory in sorted(empty_dirs, key=lambda p: len(p.parts), reverse=True):
                try:
                    directory.rmdir()
                    removed.append(directory)
                    self.track_action(CleanupAction.REMOVE_EMPTY_DIR, str(directory))
                    logger.debug(f"Removed empty directory: {directory}")
                except (PermissionError, OSError) as e:
                    logger.warning(f"Cannot remove directory {directory}: {e}")
        
        self._report.directories_removed = len(removed)
        return removed
    
    def find_broken_references(self) -> List[Dict[str, any]]:
        """
        Find broken references in plan files.
        
        Returns:
            List of dicts with file path and broken reference info
        """
        broken = []
        
        # Pattern for markdown links: [text](path)
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
        
        for filepath in self.root_directory.rglob("*.md"):
            try:
                content = filepath.read_text(encoding='utf-8')
                
                for match in link_pattern.finditer(content):
                    link_text = match.group(1)
                    link_path = match.group(2)
                    
                    # Skip external links
                    if link_path.startswith(('http://', 'https://', '#')):
                        continue
                    
                    # Resolve relative path
                    target = (filepath.parent / link_path).resolve()
                    
                    if not target.exists():
                        broken.append({
                            'file': filepath,
                            'link_text': link_text,
                            'link_path': link_path,
                            'target': target
                        })
            
            except (PermissionError, UnicodeDecodeError) as e:
                logger.warning(f"Cannot read file {filepath}: {e}")
        
        return broken
    
    def fix_broken_references(self, plan_id: str) -> int:
        """
        Fix broken references for a specific plan.
        
        Args:
            plan_id: Plan ID to fix references for
            
        Returns:
            Number of references fixed
        """
        fixed_count = 0
        broken = self.find_broken_references()
        
        for broken_ref in broken:
            filepath = broken_ref['file']
            old_path = broken_ref['link_path']
            
            # Try to find the file in new structure
            filename = Path(old_path).name
            
            # Search for file in plan folder
            plan_folder = self.root_directory / plan_id
            if plan_folder.exists():
                for found in plan_folder.rglob(filename):
                    # Calculate relative path from current file to found file
                    try:
                        new_path = Path(found).relative_to(filepath.parent)
                        
                        # Update reference in file
                        content = filepath.read_text(encoding='utf-8')
                        updated_content = content.replace(
                            f"]({old_path})",
                            f"]({new_path})"
                        )
                        filepath.write_text(updated_content, encoding='utf-8')
                        
                        fixed_count += 1
                        self.track_action(CleanupAction.FIX_REFERENCE, str(filepath))
                        logger.debug(f"Fixed reference in {filepath}: {old_path} → {new_path}")
                        break
                    
                    except ValueError:
                        # Cannot create relative path
                        continue
        
        self._report.references_fixed += fixed_count
        return fixed_count
    
    def update_cross_references(self, old_path: str, new_path: str) -> int:
        """
        Update cross-references after file move.
        
        Args:
            old_path: Old file path
            new_path: New file path
            
        Returns:
            Number of references updated
        """
        updated_count = 0
        
        # Find all markdown files
        for filepath in self.root_directory.rglob("*.md"):
            try:
                content = filepath.read_text(encoding='utf-8')
                
                if old_path in content:
                    updated_content = content.replace(old_path, new_path)
                    filepath.write_text(updated_content, encoding='utf-8')
                    
                    updated_count += 1
                    self.track_action(CleanupAction.UPDATE_REFERENCE, str(filepath))
                    logger.debug(f"Updated references in {filepath}")
            
            except (PermissionError, UnicodeDecodeError) as e:
                logger.warning(f"Cannot update file {filepath}: {e}")
        
        return updated_count
    
    def find_orphaned_files(self) -> List[Path]:
        """
        Find orphaned files (without parent plan).
        
        Returns:
            List of orphaned file paths
        """
        orphans = []
        
        # Find all YAML files
        for filepath in self.root_directory.rglob("*.yaml"):
            try:
                content = yaml.safe_load(filepath.read_text(encoding='utf-8'))
                
                if isinstance(content, dict):
                    parent_id = content.get('parent_plan_id')
                    
                    if parent_id:
                        # Check if parent plan exists
                        parent_found = False
                        
                        for parent_file in self.root_directory.rglob("*.yaml"):
                            try:
                                parent_content = yaml.safe_load(
                                    parent_file.read_text(encoding='utf-8')
                                )
                                
                                if isinstance(parent_content, dict):
                                    if parent_content.get('plan_id') == parent_id:
                                        parent_found = True
                                        break
                            
                            except Exception:
                                continue
                        
                        if not parent_found:
                            orphans.append(filepath)
            
            except Exception as e:
                logger.warning(f"Cannot check file {filepath}: {e}")
        
        return orphans
    
    def archive_orphaned_files(self, orphans: List[Path]) -> List[Path]:
        """
        Archive orphaned files to orphaned/ folder.
        
        Args:
            orphans: List of orphaned file paths
            
        Returns:
            List of archived file paths
        """
        archived = []
        
        # Create orphaned directory
        orphaned_dir = self.root_directory / "orphaned"
        orphaned_dir.mkdir(exist_ok=True)
        
        for orphan in orphans:
            try:
                # Move to orphaned directory
                target = orphaned_dir / orphan.name
                
                # Handle name conflicts
                counter = 1
                while target.exists():
                    stem = orphan.stem
                    suffix = orphan.suffix
                    target = orphaned_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                orphan.rename(target)
                archived.append(target)
                self.track_action(CleanupAction.ARCHIVE_ORPHAN, str(orphan))
                logger.debug(f"Archived orphan: {orphan} → {target}")
            
            except (PermissionError, OSError) as e:
                logger.warning(f"Cannot archive file {orphan}: {e}")
        
        # Generate manifest
        if archived:
            self._generate_orphan_manifest(archived)
        
        self._report.orphans_archived = len(archived)
        return archived
    
    def _generate_orphan_manifest(self, archived: List[Path]) -> None:
        """Generate manifest for archived orphaned files."""
        manifest_path = self.root_directory / "orphaned" / "MANIFEST.md"
        
        manifest_content = "# Orphaned Files Manifest\n\n"
        manifest_content += f"Total archived: {len(archived)}\n\n"
        manifest_content += "## Files:\n\n"
        
        for filepath in archived:
            manifest_content += f"- `{filepath.name}`\n"
        
        manifest_path.write_text(manifest_content, encoding='utf-8')
    
    def track_action(self, action: CleanupAction, target: str) -> None:
        """
        Track cleanup action.
        
        Args:
            action: Type of action
            target: Target file/directory path
        """
        self._action_history.append((action, target))
    
    def get_actions(self) -> List[tuple]:
        """
        Get tracked actions.
        
        Returns:
            List of (action, target) tuples
        """
        return self._action_history.copy()
    
    def get_action_history(self) -> List[tuple]:
        """
        Get action history.
        
        Returns:
            List of (action, target) tuples
        """
        return self._action_history.copy()
    
    def generate_cleanup_report(self) -> CleanupReport:
        """
        Generate cleanup report.
        
        Returns:
            CleanupReport object
        """
        return self._report
    
    def run_full_cleanup(self, dry_run: bool = False) -> CleanupReport:
        """
        Run complete cleanup workflow.
        
        Args:
            dry_run: If True, don't modify files
            
        Returns:
            CleanupReport object
        """
        if dry_run:
            # In dry-run mode, just find issues
            empty_dirs = self.find_empty_directories()
            orphans = self.find_orphaned_files()
            broken_refs = self.find_broken_references()
            
            self._report.directories_removed = len(empty_dirs)
            self._report.orphans_archived = len(orphans)
            self._report.references_fixed = len(broken_refs)
        else:
            # Actually perform cleanup
            self.vacuum_empty_directories()
            
            orphans = self.find_orphaned_files()
            if orphans:
                self.archive_orphaned_files(orphans)
        
        return self._report
