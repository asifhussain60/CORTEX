"""
Git Recovery Manifest Generator for CORTEX Cleanup

Creates comprehensive manifests of deleted files with git commit hashes
and file content snapshots for easy recovery.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import subprocess
import hashlib
import logging

logger = logging.getLogger(__name__)


class GitRecoveryManifest:
    """
    Generates comprehensive manifests for git recovery of deleted files.
    
    Capabilities:
    - Captures git commit hash for each deleted file
    - Records file content hash (SHA256)
    - Stores file metadata (size, mtime, path)
    - Generates recovery commands
    - Enables bulk or selective recovery
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.manifest_dir = project_root / 'cortex-brain' / 'cleanup-manifests'
        self.manifest_dir.mkdir(parents=True, exist_ok=True)
        
    def create_deletion_manifest(
        self,
        files_to_delete: List[Path],
        operation_type: str = "cleanup",
        dry_run: bool = False
    ) -> Path:
        """
        Create comprehensive deletion manifest with git recovery info.
        
        Args:
            files_to_delete: List of file paths to be deleted
            operation_type: Type of cleanup operation
            dry_run: If True, creates manifest but doesn't verify git hashes
            
        Returns:
            Path to created manifest file
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        manifest_path = self.manifest_dir / f'deletion-manifest-{operation_type}-{timestamp}.json'
        
        manifest = {
            'metadata': {
                'created': datetime.now().isoformat(),
                'operation_type': operation_type,
                'dry_run': dry_run,
                'project_root': str(self.project_root),
                'total_files': len(files_to_delete),
            },
            'files': [],
            'recovery': {
                'instructions': self._generate_recovery_instructions(),
                'bulk_recovery_command': None
            }
        }
        
        total_size = 0
        
        for file_path in files_to_delete:
            if not file_path.exists():
                continue
            
            try:
                file_info = self._capture_file_info(file_path, dry_run)
                manifest['files'].append(file_info)
                total_size += file_info['size_bytes']
                
            except Exception as e:
                logger.warning(f"Could not capture info for {file_path}: {e}")
                manifest['files'].append({
                    'path': str(file_path.relative_to(self.project_root)),
                    'error': str(e),
                    'captured': False
                })
        
        manifest['metadata']['total_size_bytes'] = total_size
        manifest['metadata']['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        
        # Generate bulk recovery command
        if manifest['files']:
            manifest['recovery']['bulk_recovery_command'] = self._generate_bulk_recovery_cmd(manifest['files'])
        
        # Save manifest
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"✓ Deletion manifest created: {manifest_path.relative_to(self.project_root)}")
        logger.info(f"  Files tracked: {len(manifest['files'])}")
        logger.info(f"  Total size: {manifest['metadata']['total_size_mb']} MB")
        
        return manifest_path
    
    def create_reorganization_manifest(
        self,
        file_moves: List[Tuple[Path, Path]],
        dry_run: bool = False
    ) -> Path:
        """
        Create manifest for file reorganization (moves).
        
        Args:
            file_moves: List of (old_path, new_path) tuples
            dry_run: If True, creates manifest but doesn't verify git hashes
            
        Returns:
            Path to created manifest file
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        manifest_path = self.manifest_dir / f'reorganization-manifest-{timestamp}.json'
        
        manifest = {
            'metadata': {
                'created': datetime.now().isoformat(),
                'operation_type': 'reorganization',
                'dry_run': dry_run,
                'project_root': str(self.project_root),
                'total_moves': len(file_moves),
            },
            'moves': [],
            'recovery': {
                'instructions': "To reverse moves, use the 'reverse_command' for each file or run the bulk_reverse_command",
                'bulk_reverse_command': None
            }
        }
        
        reverse_commands = []
        
        for old_path, new_path in file_moves:
            try:
                old_relative = old_path.relative_to(self.project_root) if old_path.is_absolute() else old_path
                new_relative = new_path.relative_to(self.project_root) if new_path.is_absolute() else new_path
                
                move_info = {
                    'old_path': str(old_relative),
                    'new_path': str(new_relative),
                    'git_commit': self._get_git_commit_hash(old_path) if not dry_run else None,
                    'reverse_command': f'git mv "{new_relative}" "{old_relative}"'
                }
                
                manifest['moves'].append(move_info)
                reverse_commands.append(move_info['reverse_command'])
                
            except Exception as e:
                logger.warning(f"Could not capture move info for {old_path}: {e}")
        
        # Generate bulk reverse command
        if reverse_commands:
            manifest['recovery']['bulk_reverse_command'] = ' && '.join(reverse_commands)
        
        # Save manifest
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"✓ Reorganization manifest created: {manifest_path.relative_to(self.project_root)}")
        logger.info(f"  Moves tracked: {len(manifest['moves'])}")
        
        return manifest_path
    
    def _capture_file_info(self, file_path: Path, dry_run: bool) -> Dict[str, Any]:
        """Capture comprehensive file information for recovery"""
        
        relative_path = file_path.relative_to(self.project_root)
        
        info = {
            'path': str(relative_path),
            'absolute_path': str(file_path),
            'size_bytes': file_path.stat().st_size,
            'size_mb': round(file_path.stat().st_size / (1024 * 1024), 4),
            'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            'content_hash': self._calculate_file_hash(file_path),
            'git_commit': self._get_git_commit_hash(file_path) if not dry_run else None,
            'git_log_snippet': self._get_git_log_snippet(file_path) if not dry_run else None,
            'recovery_command': f'git restore --source={self._get_git_commit_hash(file_path) or "HEAD"} "{relative_path}"' if not dry_run else None
        }
        
        return info
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content"""
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            return f"ERROR: {e}"
    
    def _get_git_commit_hash(self, file_path: Path) -> Optional[str]:
        """Get the last git commit hash that modified this file"""
        try:
            relative_path = file_path.relative_to(self.project_root)
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%H', '--', str(relative_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            
            return None
            
        except Exception as e:
            logger.debug(f"Could not get git commit for {file_path}: {e}")
            return None
    
    def _get_git_log_snippet(self, file_path: Path) -> Optional[str]:
        """Get brief git log for the file"""
        try:
            relative_path = file_path.relative_to(self.project_root)
            result = subprocess.run(
                ['git', 'log', '-1', '--oneline', '--', str(relative_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            
            return None
            
        except Exception as e:
            logger.debug(f"Could not get git log for {file_path}: {e}")
            return None
    
    def _generate_recovery_instructions(self) -> List[str]:
        """Generate human-readable recovery instructions"""
        return [
            "RECOVERY INSTRUCTIONS:",
            "",
            "1. Review this manifest to identify files you want to recover",
            "",
            "2. To recover a single file:",
            "   git restore --source=<git_commit> \"<path>\"",
            "   (Use the 'recovery_command' from each file entry)",
            "",
            "3. To recover all files:",
            "   Use the 'bulk_recovery_command' at the end of this manifest",
            "",
            "4. Alternative - recover from git history:",
            "   git log --all -- <path>  # Find the commit",
            "   git checkout <commit> -- <path>  # Restore the file",
            "",
            "5. If file was never committed:",
            "   Cannot recover from git - file was created after last commit",
            "   Check system trash/recycle bin if available",
            "",
            "NOTE: Recovery commands assume files are deleted but committed to git history"
        ]
    
    def _generate_bulk_recovery_cmd(self, files: List[Dict[str, Any]]) -> str:
        """Generate single command to recover all files"""
        
        recovery_commands = []
        
        for file_info in files:
            if 'recovery_command' in file_info and file_info['recovery_command']:
                recovery_commands.append(file_info['recovery_command'])
        
        if not recovery_commands:
            return "# No recovery commands available (files not in git history)"
        
        # Join with && for sequential execution
        return ' && '.join(recovery_commands)
    
    def load_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        """Load existing manifest"""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def recover_from_manifest(
        self,
        manifest_path: Path,
        file_paths: Optional[List[str]] = None,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Recover files from a manifest.
        
        Args:
            manifest_path: Path to deletion manifest
            file_paths: Specific files to recover (None = all)
            dry_run: If True, only show what would be recovered
            
        Returns:
            Dict with recovery stats
        """
        manifest = self.load_manifest(manifest_path)
        
        stats = {
            'attempted': 0,
            'succeeded': 0,
            'failed': 0,
            'errors': []
        }
        
        files_to_recover = manifest['files']
        
        if file_paths:
            files_to_recover = [f for f in files_to_recover if f['path'] in file_paths]
        
        for file_info in files_to_recover:
            if 'recovery_command' not in file_info:
                stats['failed'] += 1
                stats['errors'].append(f"{file_info['path']}: No recovery command")
                continue
            
            stats['attempted'] += 1
            
            if dry_run:
                logger.info(f"[DRY RUN] Would run: {file_info['recovery_command']}")
                stats['succeeded'] += 1
            else:
                try:
                    result = subprocess.run(
                        file_info['recovery_command'],
                        shell=True,
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"✓ Recovered: {file_info['path']}")
                        stats['succeeded'] += 1
                    else:
                        logger.error(f"✗ Failed to recover {file_info['path']}: {result.stderr}")
                        stats['failed'] += 1
                        stats['errors'].append(f"{file_info['path']}: {result.stderr}")
                        
                except Exception as e:
                    logger.error(f"✗ Error recovering {file_info['path']}: {e}")
                    stats['failed'] += 1
                    stats['errors'].append(f"{file_info['path']}: {e}")
        
        return stats
