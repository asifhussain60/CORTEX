"""
Git History Scanner

Scans git history for specified timeframe and extracts commit metadata.
Used by learning library update orchestrator to identify learning-worthy commits.

Features:
- Configurable timeframe (default 24 hours)
- Extracts: sha, message, author, timestamp, files, line counts
- Handles non-git directories gracefully
- Reuses subprocess pattern from GitMetricsCollector

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Cache for git log results (session-level cache)
_commit_cache: Dict[str, List['CommitMetadata']] = {}


@dataclass
class CommitMetadata:
    """
    Metadata extracted from git commit.
    
    Attributes:
        sha: Commit hash (short or full)
        message: Commit message (first line)
        author: Commit author name
        timestamp: Commit timestamp
        files_changed: List of modified file paths
        lines_added: Total lines added across all files
        lines_deleted: Total lines deleted across all files
        net_change: lines_added - lines_deleted
    """
    sha: str
    message: str
    author: str
    timestamp: datetime
    files_changed: List[str]
    lines_added: int
    lines_deleted: int
    net_change: int


class GitHistoryScanner:
    """
    Scans git repository history and extracts commit metadata.
    
    Uses subprocess to call git log with --numstat for line counts.
    Follows pattern from src/tier3/metrics/git_metrics.py.
    
    Example:
        scanner = GitHistoryScanner(repo_path=Path.cwd())
        commits = scanner.scan_commits(since_hours=24)
        
        for commit in commits:
            print(f"{commit.sha}: {commit.lines_added} lines added")
    """
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize git history scanner.
        
        Args:
            repo_path: Path to git repository (default: current directory)
        """
        if repo_path is None:
            repo_path = Path.cwd()
        
        self.repo_path = Path(repo_path)
    
    def scan_commits(self, since_hours: int = 24, use_cache: bool = True) -> List[CommitMetadata]:
        """
        Scan git commits within specified timeframe.
        
        Args:
            since_hours: Number of hours to look back (default: 24)
            use_cache: Whether to use cached results (default: True)
            
        Returns:
            List of CommitMetadata objects, newest first
        """
        # Check cache first
        cache_key = f"{self.repo_path}:{since_hours}"
        if use_cache and cache_key in _commit_cache:
            logger.debug(f"Using cached results for {cache_key}")
            return _commit_cache[cache_key]
        
        try:
            # Calculate since timestamp
            since_time = self._calculate_since_time(since_hours)
            since_str = since_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Build git log command
            # Format: timestamp|author|sha followed by numstat lines
            cmd = self._build_git_command(since_str)
            
            # Execute git command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False  # Don't raise on non-zero exit
            )
            
            if result.returncode != 0:
                logger.warning(f"Git command failed: {result.stderr}")
                return []
            
            # Parse output
            commits = self._parse_git_log_output(result.stdout)
            
            # Cache results
            if use_cache:
                _commit_cache[cache_key] = commits
            
            return commits
            
        except (FileNotFoundError, subprocess.SubprocessError) as e:
            logger.warning(f"Git not available or not a git repo: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error scanning git history: {e}")
            return []
    
    def _calculate_since_time(self, hours: int) -> datetime:
        """Calculate since timestamp from hours."""
        return datetime.now() - timedelta(hours=hours)
    
    def _build_git_command(self, since_str: str) -> List[str]:
        """Build git log command with parameters."""
        return [
            "git", "-C", str(self.repo_path), "log",
            f"--since={since_str}",
            "--pretty=format:%ad|%an|%H|%s",
            "--date=iso-strict",
            "--numstat"
        ]
    
    def _parse_git_log_output(self, output: str) -> List[CommitMetadata]:
        """
        Parse git log output into CommitMetadata objects.
        
        Format:
            2025-12-07T10:30:00-05:00|John Doe|abc123def|Fix validation bug
            50\t10\tsrc/module.py
            20\t5\ttests/test_module.py
            (blank line)
            2025-12-06T14:20:00-05:00|Jane Smith|def456ghi|Add feature
            100\t50\tsrc/core.py
        
        Args:
            output: Raw git log output
            
        Returns:
            List of CommitMetadata objects
        """
        commits = []
        lines = output.split('\n')
        
        current_commit = None
        current_files = []
        current_lines_added = 0
        current_lines_deleted = 0
        
        for line in lines:
            line = line.strip()
            
            if not line:
                # Blank line = end of commit
                if current_commit:
                    commits.append(CommitMetadata(
                        sha=current_commit['sha'],
                        message=current_commit['message'],
                        author=current_commit['author'],
                        timestamp=current_commit['timestamp'],
                        files_changed=current_files,
                        lines_added=current_lines_added,
                        lines_deleted=current_lines_deleted,
                        net_change=current_lines_added - current_lines_deleted
                    ))
                    
                    # Reset for next commit
                    current_commit = None
                    current_files = []
                    current_lines_added = 0
                    current_lines_deleted = 0
                continue
            
            if '|' in line and '\t' not in line:
                # Commit header line
                parts = line.split('|', 3)
                if len(parts) >= 4:
                    timestamp_str, author, sha, message = parts
                    current_commit = {
                        'timestamp': self._parse_timestamp(timestamp_str),
                        'author': author,
                        'sha': sha[:8],  # Short SHA
                        'message': message
                    }
            
            elif '\t' in line and current_commit:
                # Numstat line: added\tdeleted\tfilename
                parts = line.split('\t', 2)
                if len(parts) >= 3:
                    added_str, deleted_str, filename = parts
                    
                    # Handle binary files (shown as '-')
                    try:
                        added = int(added_str) if added_str != '-' else 0
                        deleted = int(deleted_str) if deleted_str != '-' else 0
                        
                        current_files.append(filename)
                        current_lines_added += added
                        current_lines_deleted += deleted
                    except ValueError:
                        # Skip malformed lines
                        pass
        
        # Handle last commit if no trailing blank line
        if current_commit:
            commits.append(CommitMetadata(
                sha=current_commit['sha'],
                message=current_commit['message'],
                author=current_commit['author'],
                timestamp=current_commit['timestamp'],
                files_changed=current_files,
                lines_added=current_lines_added,
                lines_deleted=current_lines_deleted,
                net_change=current_lines_added - current_lines_deleted
            ))
        
        return commits
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """
        Parse ISO 8601 timestamp from git log.
        
        Args:
            timestamp_str: ISO format timestamp
            
        Returns:
            datetime object
        """
        try:
            # Handle ISO 8601 with timezone
            return datetime.fromisoformat(timestamp_str)
        except ValueError:
            # Fallback to now if parsing fails
            logger.warning(f"Failed to parse timestamp: {timestamp_str}")
            return datetime.now()


def scan_commits(repo_path: Optional[Path] = None, 
                since_hours: int = 24) -> List[CommitMetadata]:
    """
    Convenience function to scan git commits.
    
    Args:
        repo_path: Path to git repository (default: current directory)
        since_hours: Number of hours to look back (default: 24)
        
    Returns:
        List of CommitMetadata objects
    """
    scanner = GitHistoryScanner(repo_path=repo_path)
    return scanner.scan_commits(since_hours=since_hours)
