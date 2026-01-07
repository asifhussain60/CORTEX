"""
Git Status Integration for Vacuum Orchestrator v2.

Provides intelligent analysis of git-tracked vs untracked files
to make informed cleanup decisions.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import subprocess
import logging
from pathlib import Path
from typing import List, Tuple, Set, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GitFileStatus:
    """Git file status information."""
    staged: List[str]
    modified: List[str]
    deleted: List[str]
    untracked: List[str]
    ignored: List[str]


class GitStatusAnalyzer:
    """Analyze git repository status for vacuum operations."""
    
    def __init__(self, repo_path: Path):
        """
        Initialize Git status analyzer.
        
        Args:
            repo_path: Path to git repository root
        """
        self.repo_path = Path(repo_path)
        self.is_git_repo = (self.repo_path / '.git').exists()
    
    def get_status(self) -> GitFileStatus:
        """
        Get comprehensive git status.
        
        Returns:
            GitFileStatus with categorized files
        """
        if not self.is_git_repo:
            logger.warning(f"Not a git repository: {self.repo_path}")
            return GitFileStatus([], [], [], [], [])
        
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            staged = []
            modified = []
            deleted = []
            untracked = []
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                status = line[:2]
                filepath = line[3:].strip()
                
                # Parse git status codes
                if status[0] == 'A' or status[1] == 'A':
                    staged.append(filepath)
                elif status[0] == 'M' or status[1] == 'M':
                    modified.append(filepath)
                elif status[0] == 'D' or status[1] == 'D':
                    deleted.append(filepath)
                elif status.strip() == '??':
                    untracked.append(filepath)
            
            # Get ignored files
            ignored = self._get_ignored_files()
            
            return GitFileStatus(
                staged=staged,
                modified=modified,
                deleted=deleted,
                untracked=untracked,
                ignored=ignored
            )
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Git status failed: {e}")
            return GitFileStatus([], [], [], [], [])
    
    def _get_ignored_files(self) -> List[str]:
        """
        Get list of git-ignored files.
        
        Returns:
            List of ignored file paths
        """
        try:
            result = subprocess.run(
                ['git', 'ls-files', '--others', '--ignored', '--exclude-standard'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        except subprocess.CalledProcessError:
            return []
    
    def is_tracked(self, filepath: str) -> bool:
        """
        Check if file is tracked by git.
        
        Args:
            filepath: Relative path from repo root
        
        Returns:
            True if file is tracked
        """
        try:
            result = subprocess.run(
                ['git', 'ls-files', '--', filepath],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False
    
    def get_untracked_by_category(self, untracked: List[str]) -> Dict[str, List[str]]:
        """
        Categorize untracked files for vacuum decisions.
        
        Args:
            untracked: List of untracked file paths
        
        Returns:
            Dictionary mapping categories to file lists
        """
        categories = {
            'temp_cache': [],
            'build_artifacts': [],
            'logs': [],
            'backups': [],
            'config': [],
            'docs': [],
            'source': [],
            'unknown': []
        }
        
        for filepath in untracked:
            path = Path(filepath)
            suffix = path.suffix.lower()
            name_lower = filepath.lower()
            
            # Categorize by patterns
            if any(x in name_lower for x in ['.pyc', '__pycache__', '.cache', '.tmp', '.swp']):
                categories['temp_cache'].append(filepath)
            elif any(x in name_lower for x in ['build/', 'dist/', 'bin/', 'obj/', '.egg-info']):
                categories['build_artifacts'].append(filepath)
            elif suffix in ['.log'] or 'logs/' in name_lower:
                categories['logs'].append(filepath)
            elif 'backup' in name_lower or suffix == '.bak':
                categories['backups'].append(filepath)
            elif suffix in ['.yaml', '.yml', '.json', '.toml', '.ini', '.env']:
                categories['config'].append(filepath)
            elif suffix in ['.md', '.txt', '.rst', '.pdf']:
                categories['docs'].append(filepath)
            elif suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs']:
                categories['source'].append(filepath)
            else:
                categories['unknown'].append(filepath)
        
        return categories
    
    def safe_to_delete(self, filepath: str) -> Tuple[bool, str]:
        """
        Determine if untracked file is safe to delete.
        
        Args:
            filepath: Relative path from repo root
        
        Returns:
            Tuple of (is_safe, reason)
        """
        path = Path(filepath)
        name_lower = filepath.lower()
        
        # Always safe to delete
        if any(x in name_lower for x in ['.pyc', '__pycache__', '.cache', '.tmp', '.swp']):
            return True, "Temporary/cache file"
        
        # Build artifacts (safe if not explicitly tracked)
        if any(x in name_lower for x in ['build/', 'dist/', 'bin/', 'obj/']):
            if not self.is_tracked(filepath):
                return True, "Build artifact (untracked)"
        
        # Old backups
        if 'backup' in name_lower and any(x in name_lower for x in ['20', '201', '202']):
            return True, "Old backup file"
        
        # Logs older than 30 days (would need file stat check)
        if path.suffix == '.log':
            return True, "Log file"
        
        # Unknown files - require manual review
        return False, "Manual review required"
    
    def suggest_relocation(self, filepath: str) -> str:
        """
        Suggest proper location for misplaced untracked file.
        
        Args:
            filepath: Current file path
        
        Returns:
            Suggested destination path
        """
        path = Path(filepath)
        name_lower = filepath.lower()
        
        # Root-level files should be organized
        if len(path.parts) == 1:
            if path.suffix in ['.md', '.txt']:
                return f'cortex-brain/documents/summaries/{path.name}'
            elif path.suffix in ['.yaml', '.yml', '.json']:
                return f'cortex-brain/config/{path.name}'
            elif path.suffix in ['.py']:
                return f'src/{path.name}'
            elif path.suffix in ['.sh', '.ps1']:
                return f'scripts/{path.name}'
        
        # Backups should go to archives
        if 'backup' in name_lower and not filepath.startswith('cortex-brain/archives/'):
            return f'cortex-brain/archives/backups/{path.name}'
        
        # Reports in wrong subfolder
        if 'report' in name_lower and path.suffix == '.md':
            if not filepath.startswith('cortex-brain/documents/reports/'):
                return f'cortex-brain/documents/reports/{path.name}'
        
        return filepath  # No relocation needed
    
    def get_cleanup_recommendations(self) -> Dict[str, any]:
        """
        Generate comprehensive cleanup recommendations.
        
        Returns:
            Dictionary with recommendations for DELETE, RELOCATE, PRESERVE
        """
        status = self.get_status()
        
        recommendations = {
            'delete': [],
            'relocate': {},
            'preserve': [],
            'review': []
        }
        
        # Categorize untracked files
        categories = self.get_untracked_by_category(status.untracked)
        
        # Temp/cache - safe to delete
        for filepath in categories['temp_cache']:
            recommendations['delete'].append({
                'path': filepath,
                'reason': 'Temporary/cache file',
                'risk': 'LOW'
            })
        
        # Build artifacts - safe to delete if untracked
        for filepath in categories['build_artifacts']:
            recommendations['delete'].append({
                'path': filepath,
                'reason': 'Build artifact (untracked)',
                'risk': 'LOW'
            })
        
        # Logs - review age before delete
        for filepath in categories['logs']:
            recommendations['review'].append({
                'path': filepath,
                'reason': 'Log file - check age',
                'suggested_action': 'DELETE if >30 days old'
            })
        
        # Backups - relocate to archives
        for filepath in categories['backups']:
            new_location = self.suggest_relocation(filepath)
            if new_location != filepath:
                recommendations['relocate'][filepath] = new_location
            else:
                recommendations['preserve'].append(filepath)
        
        # Config, docs, source - preserve
        for category in ['config', 'docs', 'source']:
            recommendations['preserve'].extend(categories[category])
        
        # Unknown - require review
        for filepath in categories['unknown']:
            recommendations['review'].append({
                'path': filepath,
                'reason': 'Unknown file type',
                'suggested_action': 'MANUAL REVIEW'
            })
        
        return recommendations
