"""
Git History Enricher for file-level change analysis.

This module provides file-level git history analysis including commit tracking,
change statistics, and recent activity monitoring.

Example:
    >>> enricher = GitHistoryEnricher()
    >>> history = enricher.get_file_history("src/main.py", max_commits=10)
    >>> for commit in history:
    ...     print(f"{commit['sha'][:7]}: {commit['message']}")
    >>> 
    >>> stats = enricher.get_file_statistics("src/main.py")
    >>> print(f"Total commits: {stats['total_commits']}")
"""

import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class GitHistoryEnricher:
    """
    Enriches file context with git history analysis.
    
    Provides methods to retrieve file-level commit history, change statistics,
    and recent activity for enhanced context awareness.
    
    Attributes:
        repo_path: Path to git repository root
    """
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize enricher with repository path.
        
        Args:
            repo_path: Path to git repository (default: current directory)
        """
        if repo_path is None:
            repo_path = Path.cwd()
        
        self.repo_path = repo_path
    
    def get_file_history(
        self, 
        file_path: str, 
        max_commits: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get commit history for specific file.
        
        Args:
            file_path: Relative path to file from repository root
            max_commits: Maximum number of commits to retrieve (default: 50)
        
        Returns:
            List of commit dictionaries with keys: sha, message, author, date
            Returns empty list if file doesn't exist or has no history
        
        Example:
            >>> enricher = GitHistoryEnricher()
            >>> history = enricher.get_file_history("README.md", max_commits=5)
            >>> if history:
            ...     print(f"Most recent: {history[0]['message']}")
        """
        try:
            # Git log format: %H = full hash, %s = subject, %an = author name, %ai = author date ISO
            cmd = [
                "git", "log",
                f"-{max_commits}",
                "--format=%H|%s|%an|%ai",
                "--follow",
                "--",
                file_path
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            # Parse output
            history = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('|', 3)
                if len(parts) == 4:
                    history.append({
                        "sha": parts[0],
                        "message": parts[1],
                        "author": parts[2],
                        "date": parts[3]
                    })
            
            return history
        
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return []
    
    def get_recent_changes(self, days: int = 7) -> Dict[str, Any]:
        """
        Get summary of recent repository changes.
        
        Args:
            days: Number of days to look back (default: 7)
        
        Returns:
            Dictionary with keys: total_commits, files_changed, authors
        
        Example:
            >>> enricher = GitHistoryEnricher()
            >>> changes = enricher.get_recent_changes(days=7)
            >>> print(f"{changes['total_commits']} commits in last 7 days")
        """
        try:
            # Get commits from last N days
            since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            cmd = [
                "git", "log",
                f"--since={since_date}",
                "--format=%H",
                "--no-merges"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {"total_commits": 0, "files_changed": [], "authors": []}
            
            commits = [line for line in result.stdout.strip().split('\n') if line]
            
            return {
                "total_commits": len(commits),
                "files_changed": [],  # Can be enhanced with --name-only
                "authors": []  # Can be enhanced with author extraction
            }
        
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return {"total_commits": 0, "files_changed": [], "authors": []}
    
    def get_file_statistics(self, file_path: str) -> Dict[str, Any]:
        """
        Get statistical summary for file's git history.
        
        Args:
            file_path: Relative path to file from repository root
        
        Returns:
            Dictionary with keys: total_commits, first_commit_date, last_commit_date
            Returns empty dict if file has no history
        
        Example:
            >>> enricher = GitHistoryEnricher()
            >>> stats = enricher.get_file_statistics("src/main.py")
            >>> if stats:
            ...     print(f"File has {stats['total_commits']} commits")
        """
        history = self.get_file_history(file_path, max_commits=1000)
        
        if not history:
            return {}
        
        return {
            "total_commits": len(history),
            "first_commit_date": history[-1]["date"] if history else None,
            "last_commit_date": history[0]["date"] if history else None
        }
