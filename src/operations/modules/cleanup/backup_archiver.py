"""
Backup Archiver for CORTEX Cleanup

Handles archiving backup files to GitHub before deletion.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import json
import shutil
import subprocess
import logging

logger = logging.getLogger(__name__)


class BackupArchiver:
    """
    Archives backup files to GitHub before deletion.
    
    Creates a .backup-archive directory, copies backups, creates manifest,
    and commits/pushes to GitHub for safety.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def archive_to_github(self, backup_files: List[Path]) -> Dict[str, Any]:
        """
        Archive backup files to GitHub before deletion.
        
        Args:
            backup_files: List of backup file paths to archive
        
        Returns:
            Dict with success status, commit SHA, and archived file count
        """
        if not backup_files:
            return {'success': True, 'message': 'No backups to archive'}
        
        try:
            # Create backup archive directory
            archive_dir = self.project_root / '.backup-archive'
            archive_dir.mkdir(exist_ok=True)
            
            # Create timestamped manifest
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            manifest_file = archive_dir / f'backup-manifest-{timestamp}.json'
            
            # Build manifest
            manifest = {
                'timestamp': datetime.now().isoformat(),
                'backup_count': len(backup_files),
                'total_size_bytes': sum(f.stat().st_size for f in backup_files if f.exists()),
                'files': []
            }
            
            # Copy backups to archive
            for backup_path in backup_files:
                try:
                    if not backup_path.exists():
                        continue
                    
                    relative_path = backup_path.relative_to(self.project_root)
                    archive_subdir = archive_dir / relative_path.parent
                    archive_subdir.mkdir(parents=True, exist_ok=True)
                    
                    dest_path = archive_dir / relative_path
                    shutil.copy2(backup_path, dest_path)
                    
                    manifest['files'].append({
                        'original_path': str(relative_path),
                        'archived_path': str(dest_path.relative_to(self.project_root)),
                        'size_bytes': backup_path.stat().st_size,
                        'modified_time': datetime.fromtimestamp(backup_path.stat().st_mtime).isoformat()
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to copy backup {backup_path}: {e}")
                    continue
            
            # Save manifest
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            # Git operations
            subprocess.run(['git', 'add', '.backup-archive/'], cwd=str(self.project_root), check=True)
            
            commit_msg = f"Archive {len(backup_files)} backup files before cleanup - {timestamp}"
            subprocess.run(['git', 'commit', '-m', commit_msg], cwd=str(self.project_root), check=True)
            
            # Get commit SHA
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                check=True
            )
            commit_sha = result.stdout.strip()
            
            # Push to GitHub
            subprocess.run(['git', 'push'], cwd=str(self.project_root), check=True)
            
            logger.info(f"Archived {len(backup_files)} backups to GitHub (commit: {commit_sha[:8]})")
            
            return {
                'success': True,
                'commit_sha': commit_sha,
                'manifest_file': str(manifest_file.relative_to(self.project_root)),
                'archived_count': len(manifest['files'])
            }
            
        except Exception as e:
            logger.error(f"Failed to archive backups to GitHub: {e}")
            return {
                'success': False,
                'error': str(e)
            }
