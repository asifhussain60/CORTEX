"""
Document Archive Cleaner for CORTEX

Handles cleanup of old archived documentation files.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from pathlib import Path
from datetime import datetime
from typing import Callable
import logging

logger = logging.getLogger(__name__)


class DocumentArchiveCleaner:
    """
    Cleans up old archived documentation files.
    
    Removes archived duplicate documents older than 30 days from:
    - cortex-brain/documents/archive/
    - docs/archive/consolidated/
    """
    
    def __init__(self, project_root: Path, log_action_callback: Callable, metrics):
        self.project_root = project_root
        self._log_action = log_action_callback
        self.metrics = metrics
    
    def cleanup(self, dry_run: bool) -> None:
        """
        Clean up old archived documentation files.
        
        Args:
            dry_run: If True, only preview without deleting
        """
        logger.info("Scanning for old archived documents...")
        
        # Define archive directories
        archive_dirs = [
            self.project_root / 'cortex-brain' / 'documents' / 'archive',
            self.project_root / 'docs' / 'archive' / 'consolidated'
        ]
        
        # Define age threshold (30 days in seconds)
        age_threshold_seconds = 30 * 24 * 60 * 60
        current_time = datetime.now().timestamp()
        
        archived_files = []
        
        for archive_dir in archive_dirs:
            if not archive_dir.exists():
                continue
            
            # Find all .md files in archive
            for archive_file in archive_dir.rglob('*.md'):
                if not archive_file.is_file():
                    continue
                
                # Check file age
                try:
                    file_mtime = archive_file.stat().st_mtime
                    file_age_seconds = current_time - file_mtime
                    
                    if file_age_seconds >= age_threshold_seconds:
                        archived_files.append(archive_file)
                
                except Exception as e:
                    logger.warning(f"Failed to check file age {archive_file}: {e}")
                    continue
        
        if not archived_files:
            logger.info("  No old archived documents found (older than 30 days)")
            return
        
        logger.info(f"Found {len(archived_files)} old archived documents (>30 days):")
        
        total_size_freed = 0
        
        for archive_file in archived_files:
            try:
                relative_path = archive_file.relative_to(self.project_root)
                file_size = archive_file.stat().st_size
                file_age_days = (current_time - archive_file.stat().st_mtime) / (24 * 60 * 60)
                
                logger.info(f"  - {relative_path} ({file_age_days:.0f} days old, {file_size / 1024:.1f}KB)")
                
                if not dry_run:
                    archive_file.unlink()
                    total_size_freed += file_size
                    self.metrics.archived_docs_removed += 1
                    self._log_action('archive_cleanup', archive_file, f"Removed old archive (age: {file_age_days:.0f} days)")
                else:
                    self.metrics.archived_docs_removed += 1
            
            except Exception as e:
                logger.warning(f"Failed to remove {archive_file}: {e}")
                self.metrics.errors.append(f"Failed to remove {archive_file}: {e}")
        
        if not dry_run:
            self.metrics.space_freed_bytes += total_size_freed
            logger.info(f"  ✓ Removed {self.metrics.archived_docs_removed} archived documents ({total_size_freed / 1024:.1f}KB freed)")
            
            # Clean up empty archive directories
            for archive_dir in archive_dirs:
                if archive_dir.exists():
                    try:
                        # Check if directory is empty
                        if not any(archive_dir.iterdir()):
                            archive_dir.rmdir()
                            logger.info(f"  🗑️  Removed empty archive directory: {archive_dir.relative_to(self.project_root)}")
                    except Exception as e:
                        logger.debug(f"Could not remove directory {archive_dir}: {e}")
        else:
            logger.info(f"  [DRY RUN] Would remove {self.metrics.archived_docs_removed} archived documents")
