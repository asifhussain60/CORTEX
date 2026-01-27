"""
Git History Analyzer for CORTEX.

Provides git history analysis capabilities for the LENS intelligence cycle.
Extracts commit history, blame information, and author attribution.

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


@dataclass
class GitCommit:
    """
    Represents a single git commit.
    
    Attributes:
        hash: Commit SHA hash
        author: Commit author name
        date: Commit date/time
        message: Commit message
        files_changed: List of files modified in this commit
    """
    hash: str
    author: str
    date: datetime
    message: str
    files_changed: List[str] = field(default_factory=list)


@dataclass
class GitBlame:
    """
    Represents blame information for a single line.
    
    Attributes:
        line_number: Line number in the file
        commit_hash: SHA hash of commit that last modified this line
        author: Author who last modified this line
        date: Date when line was last modified
        line_content: The actual line content
    """
    line_number: int
    commit_hash: str
    author: str
    date: datetime
    line_content: str


@dataclass
class GitHistoryResult:
    """
    Result of a git history analysis operation.
    
    Attributes:
        success: Whether operation succeeded
        commits: List of commits found
        blame_info: List of blame information (for blame operations)
        error: Error message if operation failed
        metadata: Additional metadata about the operation
    """
    success: bool
    commits: List[GitCommit] = field(default_factory=list)
    blame_info: List[GitBlame] = field(default_factory=list)
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class GitHistoryAnalyzer:
    """
    Analyzes git history for CORTEX LENS intelligence cycle.
    
    Provides methods to extract:
    - Commit history for files or entire repository
    - Blame information (who last modified each line)
    - Author attribution and contribution patterns
    - Commit message searches
    
    Example:
        ```python
        analyzer = GitHistoryAnalyzer(repo_path=Path("/path/to/repo"))
        
        # Get recent commits
        result = analyzer.get_recent_commits(max_commits=10)
        for commit in result.commits:
            print(f"{commit.hash}: {commit.message}")
        
        # Get blame for a file
        blame_result = analyzer.get_blame("src/main.py")
        for blame in blame_result.blame_info:
            print(f"Line {blame.line_number}: {blame.author}")
        ```
    
    Attributes:
        repo_path: Path to git repository root
        max_commits: Default maximum commits to retrieve
    """
    
    def __init__(self, repo_path: Path, max_commits: int = 100):
        """
        Initialize GitHistoryAnalyzer.
        
        Args:
            repo_path: Path to git repository root
            max_commits: Default maximum commits to retrieve (default: 100)
        """
        self.repo_path = repo_path
        self.max_commits = max_commits
    
    def get_file_history(
        self,
        file_path: str,
        max_commits: Optional[int] = None,
    ) -> GitHistoryResult:
        """
        Get commit history for a specific file.
        
        Args:
            file_path: Path to file (relative to repo root)
            max_commits: Maximum commits to retrieve (default: self.max_commits)
        
        Returns:
            GitHistoryResult with commits that modified this file
        """
        max_commits = max_commits or self.max_commits
        
        cmd = [
            "git",
            "log",
            f"-n{max_commits}",
            "--pretty=format:%H|%an|%ai|%s",
            "--",
            file_path,
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            
            commits = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    commit = self._parse_commit_line(line)
                    if commit:
                        # Add file to files_changed
                        commit.files_changed = [file_path]
                        commits.append(commit)
            
            return GitHistoryResult(
                success=True,
                commits=commits,
                metadata={"file_path": file_path, "max_commits": max_commits},
            )
        
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if hasattr(e, 'stderr') else str(e)
            return GitHistoryResult(
                success=False,
                error=f"Git command failed: {error_msg or 'path not found'}",
                metadata={"file_path": file_path},
            )
        except Exception as e:
            return GitHistoryResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                metadata={"file_path": file_path},
            )
    
    def get_blame(self, file_path: str) -> GitHistoryResult:
        """
        Get blame information for a file (who last modified each line).
        
        Args:
            file_path: Path to file (relative to repo root)
        
        Returns:
            GitHistoryResult with blame_info populated
        """
        cmd = [
            "git",
            "blame",
            "-w",  # Ignore whitespace
            "--line-porcelain",
            file_path,
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            
            blame_info = self._parse_blame_output(result.stdout)
            
            return GitHistoryResult(
                success=True,
                blame_info=blame_info,
                metadata={"file_path": file_path},
            )
        
        except subprocess.CalledProcessError as e:
            return GitHistoryResult(
                success=False,
                error=f"Git blame failed: {e.stderr or 'unknown error'}",
                metadata={"file_path": file_path},
            )
        except Exception as e:
            return GitHistoryResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                metadata={"file_path": file_path},
            )
    
    def get_recent_commits(
        self,
        max_commits: Optional[int] = None,
    ) -> GitHistoryResult:
        """
        Get recent commits from the repository.
        
        Args:
            max_commits: Maximum commits to retrieve (default: self.max_commits)
        
        Returns:
            GitHistoryResult with recent commits
        """
        max_commits = max_commits or self.max_commits
        
        cmd = [
            "git",
            "log",
            f"-n{max_commits}",
            "--pretty=format:%H|%an|%ai|%s",
            "--name-only",
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            
            commits = self._parse_log_with_files(result.stdout)
            
            return GitHistoryResult(
                success=True,
                commits=commits,
                metadata={"max_commits": max_commits},
            )
        
        except subprocess.CalledProcessError as e:
            return GitHistoryResult(
                success=False,
                error=f"Git log failed: {e.stderr or 'Not a git repository'}",
            )
        except Exception as e:
            return GitHistoryResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
            )
    
    def get_commits_by_author(
        self,
        author: str,
        max_commits: Optional[int] = None,
    ) -> GitHistoryResult:
        """
        Get commits by a specific author.
        
        Args:
            author: Author name or email to filter by
            max_commits: Maximum commits to retrieve (default: self.max_commits)
        
        Returns:
            GitHistoryResult with commits by this author
        """
        max_commits = max_commits or self.max_commits
        
        cmd = [
            "git",
            "log",
            f"--author={author}",
            f"-n{max_commits}",
            "--pretty=format:%H|%an|%ai|%s",
            "--name-only",
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            
            commits = self._parse_log_with_files(result.stdout)
            
            return GitHistoryResult(
                success=True,
                commits=commits,
                metadata={"author": author, "max_commits": max_commits},
            )
        
        except subprocess.CalledProcessError as e:
            return GitHistoryResult(
                success=False,
                error=f"Git log failed: {e.stderr or 'unknown error'}",
                metadata={"author": author},
            )
        except Exception as e:
            return GitHistoryResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                metadata={"author": author},
            )
    
    def search_commits(
        self,
        pattern: str,
        max_commits: Optional[int] = None,
    ) -> GitHistoryResult:
        """
        Search commits by message pattern.
        
        Args:
            pattern: String pattern to search in commit messages
            max_commits: Maximum commits to retrieve (default: self.max_commits)
        
        Returns:
            GitHistoryResult with matching commits
        """
        max_commits = max_commits or self.max_commits
        
        cmd = [
            "git",
            "log",
            f"--grep={pattern}",
            f"-n{max_commits}",
            "--pretty=format:%H|%an|%ai|%s",
            "--name-only",
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            
            commits = self._parse_log_with_files(result.stdout)
            
            return GitHistoryResult(
                success=True,
                commits=commits,
                metadata={"pattern": pattern, "max_commits": max_commits},
            )
        
        except subprocess.CalledProcessError as e:
            return GitHistoryResult(
                success=False,
                error=f"Git grep failed: {e.stderr or 'unknown error'}",
                metadata={"pattern": pattern},
            )
        except Exception as e:
            return GitHistoryResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                metadata={"pattern": pattern},
            )
    
    def _parse_commit_line(self, line: str) -> Optional[GitCommit]:
        """
        Parse a single commit line from git log.
        
        Args:
            line: Line in format "hash|author|date|message"
        
        Returns:
            GitCommit or None if parsing fails
        """
        try:
            parts = line.split("|", maxsplit=3)
            if len(parts) < 4:
                return None
            
            hash_val, author, date_str, message = parts
            
            # Parse date (format: 2026-01-27 10:00:00 +0000)
            date = datetime.strptime(date_str.split("+")[0].strip(), "%Y-%m-%d %H:%M:%S")
            
            return GitCommit(
                hash=hash_val,
                author=author,
                date=date,
                message=message,
                files_changed=[],
            )
        
        except (ValueError, IndexError):
            return None
    
    def _parse_blame_line(self, line: str, line_number: int) -> Optional[GitBlame]:
        """
        Parse a single blame line from git blame output.
        
        Args:
            line: Line in format "hash (author date line_num) content"
            line_number: Line number in the file
        
        Returns:
            GitBlame or None if parsing fails
        """
        try:
            # Pattern: abc123 (Author Name 2026-01-27 10:00:00 42) content
            match = re.match(
                r"^([a-f0-9]+)\s+\((.*?)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+\d+\)\s+(.*)",
                line,
            )
            
            if not match:
                return None
            
            commit_hash, author, date_str, line_content = match.groups()
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            
            return GitBlame(
                line_number=line_number,
                commit_hash=commit_hash,
                author=author,
                date=date,
                line_content=line_content,
            )
        
        except (ValueError, AttributeError):
            return None
    
    def _parse_blame_output(self, output: str) -> List[GitBlame]:
        """
        Parse porcelain blame output into GitBlame objects.
        
        Args:
            output: Full output from git blame --line-porcelain
        
        Returns:
            List of GitBlame objects
        """
        blame_info = []
        lines = output.split("\n")
        
        i = 0
        line_number = 1
        current_commit = None
        current_author = None
        current_date = None
        
        while i < len(lines):
            line = lines[i]
            
            # Commit hash line (starts with 40-character SHA-1)
            if line and not line.startswith("\t") and not line.startswith("author"):
                parts = line.split()
                if parts and len(parts[0]) == 40:  # SHA-1 hash
                    current_commit = parts[0]
            
            # Author line
            if line.startswith("author "):
                current_author = line[7:]
            
            # Author time line
            elif line.startswith("author-time "):
                timestamp = int(line[12:])
                current_date = datetime.fromtimestamp(timestamp)
            
            # Content line (starts with tab)
            elif line.startswith("\t"):
                if current_commit and current_author and current_date:
                    blame_info.append(
                        GitBlame(
                            line_number=line_number,
                            commit_hash=current_commit[:7],  # Short hash
                            author=current_author,
                            date=current_date,
                            line_content=line[1:],  # Remove tab
                        )
                    )
                    line_number += 1
                    # Reset for next line
                    current_commit = None
                    current_author = None
                    current_date = None
            
            i += 1
        
        return blame_info
    
    def _parse_log_with_files(self, output: str) -> List[GitCommit]:
        """
        Parse git log output with file names.
        
        Args:
            output: Output from git log with --name-only
        
        Returns:
            List of GitCommit objects with files_changed populated
        """
        commits = []
        lines = output.strip().split("\n")
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if "|" in line and not line.startswith(" ") and not line.startswith("\t"):
                # Parse commit line
                commit = self._parse_commit_line(line)
                if commit:
                    # Next lines are file names until blank line or next commit
                    i += 1
                    files = []
                    while i < len(lines):
                        next_line = lines[i].strip()
                        # Stop if blank line or next commit line
                        if not next_line or "|" in next_line:
                            break
                        files.append(next_line)
                        i += 1
                    
                    commit.files_changed = files
                    commits.append(commit)
                else:
                    i += 1
            else:
                i += 1
        
        return commits
