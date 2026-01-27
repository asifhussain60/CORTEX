"""
Git History Analyzer - MCP Tool for Git History Analysis

AC-ID: AC-MCP-TOOL-015
Provides comprehensive git history analysis for CORTEX and other orchestrators.

Capabilities:
- Remote vs local branch comparison
- Commit divergence detection
- Change impact analysis
- Merge conflict prediction
- Work summary generation

Entry Point: cortex.mcp.tools.git_history_analyzer.GitHistoryAnalyzer

CORE Governance Rules Applied:
- CORE-008: TDD (tests in tests/unit/mcp/tools/test_git_history_analyzer.py)
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
- CORE-013: Specific exception handling
- CORE-027: Audit trail logging
"""

import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class CommitInfo:
    """
    Information about a single commit.
    
    Attributes:
        sha: Commit SHA hash
        author: Commit author name
        email: Author email
        date: Commit timestamp
        message: Commit message (first line)
        full_message: Complete commit message
        files_changed: Number of files changed
        insertions: Lines inserted
        deletions: Lines deleted
    """
    sha: str
    author: str
    email: str
    date: datetime
    message: str
    full_message: str = ""
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0


@dataclass
class BranchDivergence:
    """
    Analysis of divergence between local and remote branches.
    
    Attributes:
        local_branch: Local branch name
        remote_branch: Remote branch name
        commits_ahead: Commits on local not on remote
        commits_behind: Commits on remote not on local
        common_ancestor: SHA of merge base
        is_diverged: Whether branches have diverged
        potential_conflicts: Predicted merge conflicts
    """
    local_branch: str
    remote_branch: str
    commits_ahead: List[CommitInfo] = field(default_factory=list)
    commits_behind: List[CommitInfo] = field(default_factory=list)
    common_ancestor: str = ""
    is_diverged: bool = False
    potential_conflicts: List[str] = field(default_factory=list)


@dataclass
class WorkSummary:
    """
    Summary of work done in a set of commits.
    
    Attributes:
        total_commits: Number of commits
        total_files_changed: Total files modified
        total_insertions: Total lines added
        total_deletions: Total lines removed
        authors: List of authors who contributed
        ac_ids: List of AC-IDs from commit messages
        time_range: Tuple of (earliest, latest) commit dates
        categories: Categorized commits by type (feature, fix, refactor, etc.)
    """
    total_commits: int = 0
    total_files_changed: int = 0
    total_insertions: int = 0
    total_deletions: int = 0
    authors: List[str] = field(default_factory=list)
    ac_ids: List[str] = field(default_factory=list)
    time_range: Optional[Tuple[datetime, datetime]] = None
    categories: Dict[str, List[CommitInfo]] = field(default_factory=dict)


class GitHistoryAnalyzer:
    """
    Analyzes git history for branch divergence and work tracking.
    
    Provides MCP-compatible interface for git history operations that can be
    reused by any orchestrator needing git analysis capabilities.
    
    Usage:
        >>> analyzer = GitHistoryAnalyzer()
        >>> divergence = analyzer.analyze_branch_divergence("CORTEX", "origin/CORTEX")
        >>> if divergence.commits_behind:
        >>>     print(f"Remote has {len(divergence.commits_behind)} new commits")
    """
    
    def __init__(self, repo_path: Optional[Path] = None) -> None:
        """
        Initialize Git History Analyzer.
        
        Args:
            repo_path: Path to git repository. Defaults to current directory.
        """
        self.repo_path = repo_path or Path.cwd()
        logger.info("GitHistoryAnalyzer initialized for repo: %s", self.repo_path)
    
    def fetch_remote(self, remote: str = "origin") -> bool:
        """
        Fetch latest changes from remote repository.
        
        Args:
            remote: Remote name (default: "origin")
            
        Returns:
            bool: True if fetch successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "fetch", remote],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Fetched updates from %s", remote)
            return True
        except subprocess.CalledProcessError as e:
            logger.error("Failed to fetch from %s: %s", remote, e.stderr)
            return False
    
    def get_commit_info(self, commit_sha: str) -> Optional[CommitInfo]:
        """
        Get detailed information about a commit.
        
        Args:
            commit_sha: Commit SHA hash
            
        Returns:
            CommitInfo object or None if commit not found
        """
        try:
            # Get commit details
            result = subprocess.run(
                [
                    "git", "show", commit_sha,
                    "--format=%H%n%an%n%ae%n%at%n%s%n%b",
                    "--no-patch"
                ],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) < 5:
                return None
            
            sha = lines[0]
            author = lines[1]
            email = lines[2]
            timestamp = int(lines[3])
            message = lines[4]
            full_message = '\n'.join(lines[5:]) if len(lines) > 5 else message
            
            # Get stats
            stats_result = subprocess.run(
                ["git", "show", commit_sha, "--stat", "--format="],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            files_changed = 0
            insertions = 0
            deletions = 0
            
            # Parse stats (last line has summary)
            stats_lines = stats_result.stdout.strip().split('\n')
            if stats_lines:
                last_line = stats_lines[-1]
                if "changed" in last_line:
                    parts = last_line.split(',')
                    for part in parts:
                        if "file" in part:
                            files_changed = int(part.split()[0])
                        elif "insertion" in part:
                            insertions = int(part.split()[0])
                        elif "deletion" in part:
                            deletions = int(part.split()[0])
            
            return CommitInfo(
                sha=sha,
                author=author,
                email=email,
                date=datetime.fromtimestamp(timestamp),
                message=message,
                full_message=full_message,
                files_changed=files_changed,
                insertions=insertions,
                deletions=deletions
            )
        
        except subprocess.CalledProcessError as e:
            logger.error("Failed to get commit info for %s: %s", commit_sha, e.stderr)
            return None
    
    def analyze_branch_divergence(
        self, 
        local_branch: str = "CORTEX",
        remote_branch: str = "origin/CORTEX",
        auto_fetch: bool = True
    ) -> BranchDivergence:
        """
        Analyze divergence between local and remote branches.
        
        Args:
            local_branch: Local branch name
            remote_branch: Remote branch name (e.g., "origin/CORTEX")
            auto_fetch: Whether to fetch remote updates first
            
        Returns:
            BranchDivergence object with analysis results
        """
        logger.info("Analyzing divergence: %s vs %s", local_branch, remote_branch)
        
        if auto_fetch:
            remote_name = remote_branch.split('/')[0]
            self.fetch_remote(remote_name)
        
        divergence = BranchDivergence(
            local_branch=local_branch,
            remote_branch=remote_branch
        )
        
        try:
            # Get merge base (common ancestor)
            merge_base = subprocess.run(
                ["git", "merge-base", local_branch, remote_branch],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            divergence.common_ancestor = merge_base.stdout.strip()
            
            # Get commits ahead (local not on remote)
            ahead_result = subprocess.run(
                ["git", "log", f"{remote_branch}..{local_branch}", "--format=%H"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            ahead_shas = ahead_result.stdout.strip().split('\n') if ahead_result.stdout.strip() else []
            divergence.commits_ahead = [
                info for sha in ahead_shas 
                if (info := self.get_commit_info(sha)) is not None
            ]
            
            # Get commits behind (remote not on local)
            behind_result = subprocess.run(
                ["git", "log", f"{local_branch}..{remote_branch}", "--format=%H"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            behind_shas = behind_result.stdout.strip().split('\n') if behind_result.stdout.strip() else []
            divergence.commits_behind = [
                info for sha in behind_shas 
                if (info := self.get_commit_info(sha)) is not None
            ]
            
            divergence.is_diverged = bool(divergence.commits_ahead and divergence.commits_behind)
            
            # Predict potential conflicts (files modified in both branches)
            if divergence.is_diverged:
                divergence.potential_conflicts = self._predict_conflicts(
                    local_branch, remote_branch
                )
            
            logger.info(
                "Divergence analysis complete: %d ahead, %d behind, diverged=%s",
                len(divergence.commits_ahead),
                len(divergence.commits_behind),
                divergence.is_diverged
            )
            
        except subprocess.CalledProcessError as e:
            logger.error("Failed to analyze divergence: %s", e.stderr)
        
        return divergence
    
    def generate_work_summary(self, commits: List[CommitInfo]) -> WorkSummary:
        """
        Generate summary of work from list of commits.
        
        Args:
            commits: List of CommitInfo objects
            
        Returns:
            WorkSummary with aggregated statistics
        """
        summary = WorkSummary()
        summary.total_commits = len(commits)
        
        if not commits:
            return summary
        
        authors_set = set()
        ac_ids_set = set()
        dates = []
        
        # Initialize categories
        categories = {
            "feature": [],
            "fix": [],
            "refactor": [],
            "test": [],
            "docs": [],
            "other": []
        }
        
        for commit in commits:
            summary.total_files_changed += commit.files_changed
            summary.total_insertions += commit.insertions
            summary.total_deletions += commit.deletions
            
            authors_set.add(commit.author)
            dates.append(commit.date)
            
            # Extract AC-IDs
            msg = commit.full_message or commit.message
            if "AC-" in msg:
                import re
                ac_matches = re.findall(r'AC-[A-Z0-9-]+', msg)
                ac_ids_set.update(ac_matches)
            
            # Categorize commit
            msg_lower = commit.message.lower()
            if any(word in msg_lower for word in ["feat", "feature", "implement", "add"]):
                categories["feature"].append(commit)
            elif any(word in msg_lower for word in ["fix", "bug", "issue", "resolve"]):
                categories["fix"].append(commit)
            elif any(word in msg_lower for word in ["refactor", "restructure", "improve"]):
                categories["refactor"].append(commit)
            elif any(word in msg_lower for word in ["test", "testing"]):
                categories["test"].append(commit)
            elif any(word in msg_lower for word in ["doc", "docs", "documentation"]):
                categories["docs"].append(commit)
            else:
                categories["other"].append(commit)
        
        summary.authors = sorted(authors_set)
        summary.ac_ids = sorted(ac_ids_set)
        summary.time_range = (min(dates), max(dates)) if dates else None
        summary.categories = categories
        
        return summary
    
    def _predict_conflicts(self, branch1: str, branch2: str) -> List[str]:
        """
        Predict potential merge conflicts between branches.
        
        Args:
            branch1: First branch name
            branch2: Second branch name
            
        Returns:
            List of file paths that may have conflicts
        """
        try:
            # Get files changed in branch1
            files1_result = subprocess.run(
                ["git", "diff", "--name-only", f"{branch2}...{branch1}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            files1 = set(files1_result.stdout.strip().split('\n'))
            
            # Get files changed in branch2
            files2_result = subprocess.run(
                ["git", "diff", "--name-only", f"{branch1}...{branch2}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            files2 = set(files2_result.stdout.strip().split('\n'))
            
            # Intersection = potential conflicts
            potential_conflicts = sorted(files1 & files2)
            return potential_conflicts
        
        except subprocess.CalledProcessError as e:
            logger.error("Failed to predict conflicts: %s", e.stderr)
            return []


# MCP-compatible singleton accessor
_git_analyzer_instance: Optional[GitHistoryAnalyzer] = None


def get_git_history_analyzer(repo_path: Optional[Path] = None) -> GitHistoryAnalyzer:
    """
    Get singleton instance of GitHistoryAnalyzer.
    
    Args:
        repo_path: Path to git repository
        
    Returns:
        GitHistoryAnalyzer instance
    """
    global _git_analyzer_instance
    if _git_analyzer_instance is None:
        _git_analyzer_instance = GitHistoryAnalyzer(repo_path)
    return _git_analyzer_instance
