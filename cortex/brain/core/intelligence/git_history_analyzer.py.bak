# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: IR-001-02 - Git History Intelligence
"""
Git History Analyzer for CORTEX LENS.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-001-02 - Git History Intelligence

This module provides git history analysis capabilities including:
- Commit history extraction
- File history tracking
- Rename/move detection
- Temporal context building

Part of CORTEX LENS context intelligence system.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class CommitInfo:
    """Information about a git commit.
    
    Attributes:
        hash: Commit hash (short or full)
        author: Author name
        author_email: Author email
        date: Commit date
        message: Commit message
        files_changed: List of files changed in this commit
    """
    hash: str
    author: str
    author_email: Optional[str] = None
    date: datetime = field(default_factory=datetime.now)
    message: str = ""
    files_changed: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "hash": self.hash,
            "author": self.author,
            "author_email": self.author_email,
            "date": self.date.isoformat(),
            "message": self.message,
            "files_changed": self.files_changed,
        }


@dataclass
class RenameInfo:
    """Information about a file rename operation.
    
    Attributes:
        old_path: Original file path
        new_path: New file path
        commit_hash: Commit where rename occurred
        similarity: Similarity percentage (0-100)
    """
    old_path: str
    new_path: str
    commit_hash: str
    similarity: int = 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "old_path": self.old_path,
            "new_path": self.new_path,
            "commit_hash": self.commit_hash,
            "similarity": self.similarity,
        }


# =============================================================================
# GIT HISTORY ANALYZER
# =============================================================================


class GitHistoryAnalyzer:
    """Analyzes git history for context intelligence.
    
    Provides methods to extract commit history, file changes, and
    refactoring patterns from a git repository.
    
    Attributes:
        repo_path: Path to the git repository
        
    Example:
        >>> analyzer = GitHistoryAnalyzer(Path("/path/to/repo"))
        >>> commits = analyzer.get_commit_history()
        >>> for commit in commits:
        ...     print(f"{commit.hash}: {commit.message}")
    """
    
    def __init__(self, repo_path: Path) -> None:
        """Initialize the git history analyzer.
        
        Args:
            repo_path: Path to the git repository root
        """
        self.repo_path = repo_path
        self._is_repo: Optional[bool] = None
    
    def is_git_repo(self) -> bool:
        """Check if the path is a git repository.
        
        Returns:
            True if path is a valid git repository
        """
        if self._is_repo is not None:
            return self._is_repo
        
        try:
            result = self._run_git_command(["rev-parse", "--git-dir"])
            self._is_repo = result is not None
        except Exception:
            self._is_repo = False
        
        return self._is_repo
    
    def get_commit_history(
        self,
        max_count: int = 100,
        since: Optional[datetime] = None,
    ) -> List[CommitInfo]:
        """Get commit history for the repository.
        
        Args:
            max_count: Maximum number of commits to return
            since: Only return commits after this date
            
        Returns:
            List of CommitInfo objects, newest first
        """
        if not self.is_git_repo():
            return []
        
        args = [
            "log",
            f"--max-count={max_count}",
            "--format=%H|%an|%ae|%aI|%s",
        ]
        
        if since:
            args.append(f"--since={since.isoformat()}")
        
        output = self._run_git_command(args)
        if not output:
            return []
        
        commits = []
        for line in output.strip().split("\n"):
            if not line:
                continue
            
            parts = line.split("|", 4)
            if len(parts) >= 5:
                commit = CommitInfo(
                    hash=parts[0],
                    author=parts[1],
                    author_email=parts[2],
                    date=self._parse_date(parts[3]),
                    message=parts[4],
                )
                commits.append(commit)
        
        return commits
    
    def get_file_history(
        self,
        file_path: Path,
        max_count: int = 50,
    ) -> List[CommitInfo]:
        """Get commit history for a specific file.
        
        Args:
            file_path: Relative path to the file
            max_count: Maximum number of commits to return
            
        Returns:
            List of CommitInfo objects for the file
        """
        if not self.is_git_repo():
            return []
        
        args = [
            "log",
            f"--max-count={max_count}",
            "--format=%H|%an|%ae|%aI|%s",
            "--follow",
            "--",
            str(file_path),
        ]
        
        output = self._run_git_command(args)
        if not output:
            return []
        
        commits = []
        for line in output.strip().split("\n"):
            if not line:
                continue
            
            parts = line.split("|", 4)
            if len(parts) >= 5:
                commit = CommitInfo(
                    hash=parts[0],
                    author=parts[1],
                    author_email=parts[2],
                    date=self._parse_date(parts[3]),
                    message=parts[4],
                    files_changed=[str(file_path)],
                )
                commits.append(commit)
        
        return commits
    
    def get_file_timeline(
        self,
        file_path: Path,
        max_count: int = 50,
    ) -> List[CommitInfo]:
        """Get timeline of changes for a file.
        
        Args:
            file_path: Relative path to the file
            max_count: Maximum number of commits
            
        Returns:
            List of CommitInfo in reverse chronological order
        """
        return self.get_file_history(file_path, max_count)
    
    def get_recent_changes(
        self,
        days: int = 7,
    ) -> List[CommitInfo]:
        """Get commits from the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of recent commits
        """
        since = datetime.now() - timedelta(days=days)
        return self.get_commit_history(max_count=500, since=since)
    
    def get_commit_diff(
        self,
        commit_hash: str,
    ) -> Optional[str]:
        """Get diff for a specific commit.
        
        Args:
            commit_hash: Hash of the commit
            
        Returns:
            Diff string or None if not found
        """
        if not self.is_git_repo():
            return None
        
        args = ["show", "--stat", commit_hash]
        return self._run_git_command(args)
    
    def detect_renames(
        self,
        max_count: int = 100,
    ) -> List[RenameInfo]:
        """Detect file rename operations in history.
        
        Args:
            max_count: Maximum number of commits to search
            
        Returns:
            List of RenameInfo objects
        """
        if not self.is_git_repo():
            return []
        
        args = [
            "log",
            f"--max-count={max_count}",
            "--diff-filter=R",
            "-M",
            "--format=%H",
            "--name-status",
        ]
        
        output = self._run_git_command(args)
        if not output:
            return []
        
        renames = []
        current_hash = ""
        
        for line in output.strip().split("\n"):
            if not line:
                continue
            
            if len(line) == 40 and all(c in "0123456789abcdef" for c in line):
                current_hash = line
            elif line.startswith("R"):
                parts = line.split("\t")
                if len(parts) >= 3:
                    similarity = 100
                    if parts[0].startswith("R"):
                        try:
                            similarity = int(parts[0][1:])
                        except ValueError:
                            pass
                    
                    renames.append(RenameInfo(
                        old_path=parts[1],
                        new_path=parts[2],
                        commit_hash=current_hash,
                        similarity=similarity,
                    ))
        
        return renames
    
    def detect_moves(
        self,
        max_count: int = 100,
    ) -> List[RenameInfo]:
        """Detect file move operations (renames that change directory).
        
        Args:
            max_count: Maximum number of commits to search
            
        Returns:
            List of RenameInfo objects where directory changed
        """
        renames = self.detect_renames(max_count)
        
        moves = []
        for rename in renames:
            old_dir = str(Path(rename.old_path).parent)
            new_dir = str(Path(rename.new_path).parent)
            
            if old_dir != new_dir:
                moves.append(rename)
        
        return moves
    
    def get_files_changed_in_commit(
        self,
        commit_hash: str,
    ) -> List[str]:
        """Get list of files changed in a commit.
        
        Args:
            commit_hash: Hash of the commit
            
        Returns:
            List of file paths changed
        """
        if not self.is_git_repo():
            return []
        
        args = [
            "show",
            "--name-only",
            "--format=",
            commit_hash,
        ]
        
        output = self._run_git_command(args)
        if not output:
            return []
        
        return [f for f in output.strip().split("\n") if f]
    
    def _run_git_command(self, args: List[str]) -> Optional[str]:
        """Run a git command and return output.
        
        Args:
            args: Git command arguments
            
        Returns:
            Command output or None on failure
        """
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode == 0:
                return result.stdout
            return None
        except Exception:
            return None
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse ISO format date string.
        
        Args:
            date_str: ISO format date string
            
        Returns:
            datetime object (timezone-naive)
        """
        try:
            # Handle ISO format with timezone like 2026-01-15T10:30:00+00:00
            # or 2026-01-15T10:30:00-05:00
            # Remove timezone suffix for naive datetime
            if "+" in date_str:
                date_str = date_str.split("+")[0]
            elif date_str.endswith("Z"):
                date_str = date_str.rstrip("Z")
            elif "-" in date_str:
                # Check if the last hyphen is for timezone (format: -HH:MM)
                parts = date_str.rsplit("-", 1)
                if len(parts) == 2 and ":" in parts[1] and len(parts[1]) <= 6:
                    date_str = parts[0]
            
            return datetime.fromisoformat(date_str)
        except ValueError:
            return datetime.now()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "GitHistoryAnalyzer",
    "CommitInfo",
    "RenameInfo",
]
