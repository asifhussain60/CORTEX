"""Evolution Timeline Analyzer

Analyzes git history and refactoring patterns to understand codebase evolution.

Author: CORTEX Framework
Phase: PHASE-97 S4
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import subprocess


@dataclass
class RefactoringEvent:
    """Represents a refactoring event in history.
    
    Attributes:
        timestamp: When refactoring occurred
        file_path: Path to refactored file
        event_type: Type of refactoring (rename, extract, inline, etc.)
        complexity_before: Complexity score before refactoring
        complexity_after: Complexity score after refactoring
        commit_sha: Git commit hash
        author: Commit author
    """
    
    timestamp: datetime
    file_path: str
    event_type: str
    complexity_before: int
    complexity_after: int
    commit_sha: str
    author: str
    
    @property
    def complexity_improvement(self) -> int:
        """Calculate complexity improvement.
        
        Returns:
            Positive if improved, negative if worsened
        """
        return self.complexity_before - self.complexity_after


@dataclass
class EvolutionMilestone:
    """Represents a significant milestone in codebase evolution.
    
    Attributes:
        timestamp: Milestone timestamp
        title: Milestone title
        description: Milestone description
        commits: Associated commit hashes
        impact_score: Impact score (0-100)
    """
    
    timestamp: datetime
    title: str
    description: str
    commits: List[str] = field(default_factory=list)
    impact_score: int = 0


@dataclass
class EvolutionTimeline:
    """Complete evolution timeline for codebase.
    
    Attributes:
        start_date: Timeline start
        end_date: Timeline end
        refactoring_events: List of refactoring events
        milestones: List of evolution milestones
        total_commits: Total commit count
        active_contributors: Set of contributor names
        tech_debt_trend: Tech debt trend (increasing/decreasing/stable)
    """
    
    start_date: datetime
    end_date: datetime
    refactoring_events: List[RefactoringEvent] = field(default_factory=list)
    milestones: List[EvolutionMilestone] = field(default_factory=list)
    total_commits: int = 0
    active_contributors: Set[str] = field(default_factory=set)
    tech_debt_trend: str = "stable"
    
    @property
    def total_refactorings(self) -> int:
        """Get total refactoring count.
        
        Returns:
            Number of refactoring events
        """
        return len(self.refactoring_events)
    
    @property
    def average_complexity_improvement(self) -> float:
        """Calculate average complexity improvement.
        
        Returns:
            Average improvement score
        """
        if not self.refactoring_events:
            return 0.0
        
        improvements = [e.complexity_improvement for e in self.refactoring_events]
        return sum(improvements) / len(improvements)


class EvolutionAnalyzer:
    """Analyzer for codebase evolution and refactoring patterns.
    
    Analyzes git history to identify refactoring events, milestones,
    and evolution trends.
    
    Attributes:
        repo_path: Path to git repository
        _git_available: Whether git is available
    """
    
    def __init__(self, repo_path: Path) -> None:
        """Initialize evolution analyzer.
        
        Args:
            repo_path: Path to git repository
        """
        self.repo_path = repo_path
        self._git_available = self._check_git_available()
    
    def _check_git_available(self) -> bool:
        """Check if git is available and repo is valid.
        
        Returns:
            True if git available and repo valid
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def analyze(
        self,
        target_path: Optional[Path] = None,
        days: int = 90,
    ) -> EvolutionTimeline:
        """Analyze evolution timeline.
        
        Args:
            target_path: Specific path to analyze (None for entire repo)
            days: Number of days to analyze
        
        Returns:
            Evolution timeline
        """
        if not self._git_available:
            return self._empty_timeline()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get git log
        commits = self._get_commits(start_date, end_date, target_path)
        
        # Detect refactoring events
        refactorings = self._detect_refactorings(commits)
        
        # Identify milestones
        milestones = self._identify_milestones(commits)
        
        # Extract contributors
        contributors = {c["author"] for c in commits}
        
        # Calculate tech debt trend
        tech_debt_trend = self._calculate_tech_debt_trend(refactorings)
        
        return EvolutionTimeline(
            start_date=start_date,
            end_date=end_date,
            refactoring_events=refactorings,
            milestones=milestones,
            total_commits=len(commits),
            active_contributors=contributors,
            tech_debt_trend=tech_debt_trend,
        )
    
    def _empty_timeline(self) -> EvolutionTimeline:
        """Create empty timeline for non-git repos.
        
        Returns:
            Empty evolution timeline
        """
        now = datetime.now()
        return EvolutionTimeline(
            start_date=now,
            end_date=now,
        )
    
    def _get_commits(
        self,
        start_date: datetime,
        end_date: datetime,
        target_path: Optional[Path],
    ) -> List[Dict[str, Any]]:
        """Get git commits in date range.
        
        Args:
            start_date: Start date
            end_date: End date
            target_path: Optional path filter
        
        Returns:
            List of commit dicts
        """
        cmd = [
            "git",
            "log",
            f"--since={start_date.strftime('%Y-%m-%d')}",
            f"--until={end_date.strftime('%Y-%m-%d')}",
            "--pretty=format:%H|%an|%ai|%s",
        ]
        
        if target_path:
            cmd.append("--")
            cmd.append(str(target_path))
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode != 0:
                return []
            
            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                
                parts = line.split("|", 3)
                if len(parts) == 4:
                    # Parse timestamp - handle timezone info
                    timestamp_str = parts[2].split()[0:2]  # Take date and time only
                    try:
                        timestamp = datetime.strptime(
                            " ".join(timestamp_str), "%Y-%m-%d %H:%M:%S"
                        )
                    except ValueError:
                        # Fallback to current time if parsing fails
                        timestamp = datetime.now()
                    
                    commits.append({
                        "sha": parts[0],
                        "author": parts[1],
                        "timestamp": timestamp,
                        "message": parts[3],
                    })
            
            return commits
            
        except (subprocess.SubprocessError, ValueError):
            return []
    
    def _detect_refactorings(
        self, commits: List[Dict[str, Any]]
    ) -> List[RefactoringEvent]:
        """Detect refactoring events from commits.
        
        Args:
            commits: List of commits
        
        Returns:
            List of refactoring events
        """
        refactorings = []
        
        # Keywords indicating refactoring
        keywords = [
            "refactor",
            "extract",
            "rename",
            "inline",
            "consolidate",
            "simplify",
            "cleanup",
        ]
        
        for commit in commits:
            message_lower = commit["message"].lower()
            
            for keyword in keywords:
                if keyword in message_lower:
                    # Create refactoring event (complexity scores would come from AST analysis)
                    event = RefactoringEvent(
                        timestamp=commit["timestamp"],
                        file_path="",  # Would be extracted from git diff
                        event_type=keyword,
                        complexity_before=100,  # Placeholder
                        complexity_after=80,    # Placeholder
                        commit_sha=commit["sha"],
                        author=commit["author"],
                    )
                    refactorings.append(event)
                    break
        
        return refactorings
    
    def _identify_milestones(
        self, commits: List[Dict[str, Any]]
    ) -> List[EvolutionMilestone]:
        """Identify evolution milestones from commits.
        
        Args:
            commits: List of commits
        
        Returns:
            List of milestones
        """
        milestones = []
        
        # Keywords indicating milestones
        milestone_keywords = [
            "phase",
            "stage",
            "release",
            "version",
            "milestone",
            "complete",
        ]
        
        for commit in commits:
            message_lower = commit["message"].lower()
            
            for keyword in milestone_keywords:
                if keyword in message_lower:
                    milestone = EvolutionMilestone(
                        timestamp=commit["timestamp"],
                        title=commit["message"][:50],
                        description=commit["message"],
                        commits=[commit["sha"]],
                        impact_score=75,  # Would be calculated from commit analysis
                    )
                    milestones.append(milestone)
                    break
        
        return milestones
    
    def _calculate_tech_debt_trend(
        self, refactorings: List[RefactoringEvent]
    ) -> str:
        """Calculate tech debt trend.
        
        Args:
            refactorings: List of refactoring events
        
        Returns:
            Trend description (increasing/decreasing/stable)
        """
        if not refactorings:
            return "stable"
        
        # Calculate average improvement
        improvements = [e.complexity_improvement for e in refactorings]
        avg_improvement = sum(improvements) / len(improvements)
        
        if avg_improvement > 5:
            return "decreasing"  # Tech debt decreasing (good)
        elif avg_improvement < -5:
            return "increasing"  # Tech debt increasing (bad)
        else:
            return "stable"
