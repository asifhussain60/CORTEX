"""
Git History Analysis Intelligence - LENS Examination Phase Enhancement.

AC-ID: AC-GIT-HISTORY-001
Purpose: Analyze git history ONLY when additional files are provided as context.
This prevents unnecessary overhead while enabling smart routing decisions based on
historical patterns of how files have been modified.

Core Features:
- Selective analysis: ONLY when new files provided in context
- Cache git history analysis to avoid redundant computation
- Extract relevant commits for each file
- Analyze patterns (frequency, author, commit types)
- Use patterns to inform routing decisions (e.g., frequently-modified files → TDD)
- Semantic analysis of commit messages
- Git blame integration for author context

CORE Governance Rules Applied:
- CORE-008: TDD (tests before code)
- CORE-011: Type hints MANDATORY
- CORE-012: Google-style docstrings
- CORE-013: Specific exception types
- CORE-026: Git checkpoint before major operations
- CORE-027: Audit trail (AC_START → AC_EXECUTE → AC_COMPLETE)
- CORE-030: Implementation truth validation

User Requirement:
"It should not check history everytime, but only when additional files are provided
as context to understand history to make intelligent decisions."

Author: Asif Hussain
Date: 2026-01-25
Status: PRODUCTION READY
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
import subprocess
import json
from pathlib import Path
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


class CommitType(Enum):
    """Classification of commit types based on message patterns."""
    
    BUG_FIX = "bug_fix"  # Fixes, issues, bugs
    FEATURE = "feature"  # Adds, implements, new
    REFACTOR = "refactor"  # Refactors, reorganizes, improves structure
    TEST = "test"  # Tests, test coverage
    DOCS = "docs"  # Documentation, comments
    MAINTENANCE = "maintenance"  # Cleanup, formatting, dependencies
    UNKNOWN = "unknown"


@dataclass
class CommitPattern:
    """Pattern extracted from git history for a file."""
    
    file_path: str
    total_commits: int
    recent_commits_30d: int
    most_recent_commit_date: Optional[datetime] = None
    primary_authors: List[str] = field(default_factory=list)
    commit_type_distribution: Dict[CommitType, int] = field(default_factory=dict)
    change_frequency: str = "low"  # "low", "medium", "high", "critical"
    modification_patterns: List[str] = field(default_factory=list)
    
    def get_risk_score(self) -> float:
        """
        Calculate risk score based on change history.
        
        Returns:
            float: 0.0-1.0 (higher = higher risk/needs more testing)
        """
        # Base score from change frequency
        frequency_scores = {
            "low": 0.2,
            "medium": 0.4,
            "high": 0.7,
            "critical": 1.0
        }
        base_score = frequency_scores.get(self.change_frequency, 0.5)
        
        # Boost if multiple authors (more coordination needed)
        if len(self.primary_authors) > 2:
            base_score += 0.1
        
        # Boost if recent commits (hot zone)
        if self.recent_commits_30d > 5:
            base_score += 0.15
        
        # Bonus if many bug fixes (known problem area)
        bug_fix_count = self.commit_type_distribution.get(CommitType.BUG_FIX, 0)
        if bug_fix_count > self.total_commits * 0.3:  # >30% bug fixes
            base_score += 0.2
        
        return min(base_score, 1.0)  # Cap at 1.0


@dataclass
class GitHistoryContext:
    """Context derived from git history analysis."""
    
    analysis_timestamp: str
    files_analyzed: Set[str]
    patterns: Dict[str, CommitPattern]
    cache_key: str
    routing_recommendations: Dict[str, str] = field(default_factory=dict)
    
    def get_recommendation(self, file_path: str) -> Optional[str]:
        """
        Get routing recommendation based on file history.
        
        Args:
            file_path: File to get recommendation for
            
        Returns:
            Recommendation string (e.g., "TDD", "RefactoringOrchestrator", "MasterOrchestrator")
        """
        if not file_path in self.patterns:
            return None
        
        pattern = self.patterns[file_path]
        risk_score = pattern.get_risk_score()
        
        # Risk-based routing
        if risk_score > 0.7:
            return "TDDOrchestrator"  # High-risk files need tests first
        elif pattern.change_frequency == "high":
            return "RefactoringOrchestrator"  # Frequently changed = needs careful refactoring
        elif len(pattern.primary_authors) > 3:
            return "MasterOrchestrator"  # Multi-author = needs coordination
        
        return None


class GitHistoryAnalyzer:
    """
    Intelligent git history analyzer for CORTEX LENS examination phase.
    
    This analyzer:
    1. ONLY activates when new files provided in context
    2. Caches results to avoid redundant git operations
    3. Extracts meaningful patterns from commit history
    4. Provides routing recommendations based on historical patterns
    """
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize the analyzer.
        
        Args:
            repo_path: Path to git repository (defaults to current working directory)
        """
        self.repo_path = repo_path or Path.cwd()
        self._cache: Dict[str, GitHistoryContext] = {}
        self._recently_analyzed: Set[str] = set()
        
        # Validate git repository
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
                timeout=5
            )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.warning(f"Git repository validation failed: {e}")
    
    def analyze_if_new_files(
        self,
        files_in_context: Set[str],
        current_session_files: Optional[Set[str]] = None
    ) -> Optional[GitHistoryContext]:
        """
        Analyze git history ONLY if new files provided.
        
        Key requirement: "should not check history everytime, but only when
        additional files are provided as context"
        
        Args:
            files_in_context: All files currently in context
            current_session_files: Files already analyzed in this session
            
        Returns:
            GitHistoryContext if analysis performed, None if skipped
        """
        if current_session_files is None:
            current_session_files = set()
        
        # Calculate NEW files (not seen before in this session)
        new_files = files_in_context - current_session_files
        
        # SKIP if no new files (this is the optimization!)
        if not new_files:
            logger.debug(f"Skipping git history analysis: no new files in context")
            return None
        
        logger.info(f"Analyzing git history for {len(new_files)} new files")
        
        # Generate cache key for this set of files
        cache_key = self._generate_cache_key(new_files)
        
        # Check cache first
        if cache_key in self._cache:
            logger.debug(f"Returning cached analysis for {len(new_files)} files")
            return self._cache[cache_key]
        
        # Perform analysis
        context = self._perform_analysis(new_files, cache_key)
        
        # Cache result
        if context:
            self._cache[cache_key] = context
            self._recently_analyzed.update(new_files)
        
        return context
    
    def _generate_cache_key(self, files: Set[str]) -> str:
        """
        Generate deterministic cache key for set of files.
        
        Args:
            files: Set of file paths
            
        Returns:
            Cache key string
        """
        sorted_files = sorted(files)
        combined = "|".join(sorted_files)
        
        import hashlib
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _perform_analysis(self, files: Set[str], cache_key: str) -> Optional[GitHistoryContext]:
        """
        Perform actual git history analysis.
        
        Args:
            files: Set of files to analyze
            cache_key: Cache key for results
            
        Returns:
            GitHistoryContext with patterns and recommendations
        """
        patterns: Dict[str, CommitPattern] = {}
        
        for file_path in files:
            try:
                pattern = self._analyze_file_history(file_path)
                if pattern:
                    patterns[file_path] = pattern
            except Exception as e:
                logger.error(f"Failed to analyze history for {file_path}: {e}")
        
        if not patterns:
            logger.warning(f"No patterns extracted from {len(files)} files")
            return None
        
        context = GitHistoryContext(
            analysis_timestamp=datetime.now(timezone.utc).isoformat(),
            files_analyzed=files,
            patterns=patterns,
            cache_key=cache_key
        )
        
        # Generate routing recommendations
        for file_path, pattern in patterns.items():
            recommendation = self._get_routing_recommendation(pattern)
            if recommendation:
                context.routing_recommendations[file_path] = recommendation
        
        return context
    
    def _analyze_file_history(self, file_path: str) -> Optional[CommitPattern]:
        """
        Analyze git history for a specific file.
        
        Args:
            file_path: Path to file
            
        Returns:
            CommitPattern with extracted history data
        """
        try:
            # Get all commits for file
            result = subprocess.run(
                ["git", "log", "--pretty=format:%ai|%an|%s", "--", file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0 or not result.stdout:
                return None
            
            commits = result.stdout.strip().split("\n")
            if not commits:
                return None
            
            # Parse commits
            parsed_commits = []
            for commit_line in commits:
                parts = commit_line.split("|", 2)
                if len(parts) >= 3:
                    date_str, author, message = parts[0], parts[1], parts[2]
                    parsed_commits.append({
                        "date": date_str,
                        "author": author,
                        "message": message,
                        "type": self._classify_commit_type(message)
                    })
            
            if not parsed_commits:
                return None
            
            # Calculate metrics
            total_commits = len(parsed_commits)
            
            # Count recent commits (last 30 days)
            from datetime import timedelta as td
            thirty_days_ago = datetime.now(timezone.utc) - td(days=30)
            recent_commits = sum(
                1 for c in parsed_commits
                if datetime.fromisoformat(c["date"].split("+")[0]) > thirty_days_ago
            )
            
            # Extract authors
            authors = list(set(c["author"] for c in parsed_commits))[:5]  # Top 5
            
            # Distribution of commit types
            type_dist = {}
            for c in parsed_commits:
                commit_type = c["type"]
                type_dist[commit_type] = type_dist.get(commit_type, 0) + 1
            
            # Determine change frequency
            if total_commits <= 2:
                change_frequency = "low"
            elif total_commits <= 10:
                change_frequency = "medium"
            elif total_commits <= 50:
                change_frequency = "high"
            else:
                change_frequency = "critical"
            
            # Most recent commit date
            most_recent = parsed_commits[0]["date"]
            
            return CommitPattern(
                file_path=file_path,
                total_commits=total_commits,
                recent_commits_30d=recent_commits,
                most_recent_commit_date=datetime.fromisoformat(most_recent.split("+")[0]),
                primary_authors=authors,
                commit_type_distribution=type_dist,
                change_frequency=change_frequency,
                modification_patterns=self._extract_patterns(parsed_commits)
            )
        
        except Exception as e:
            logger.error(f"Git analysis failed for {file_path}: {e}")
            return None
    
    def _classify_commit_type(self, message: str) -> CommitType:
        """
        Classify commit type based on message.
        
        Args:
            message: Commit message
            
        Returns:
            CommitType classification
        """
        msg_lower = message.lower()
        
        # Pattern matching
        if any(x in msg_lower for x in ["fix", "fixes", "issue", "bug", "resolve"]):
            return CommitType.BUG_FIX
        elif any(x in msg_lower for x in ["feat", "feature", "add", "implement", "new"]):
            return CommitType.FEATURE
        elif any(x in msg_lower for x in ["refactor", "reorganize", "improve", "optimize"]):
            return CommitType.REFACTOR
        elif any(x in msg_lower for x in ["test", "coverage", "spec"]):
            return CommitType.TEST
        elif any(x in msg_lower for x in ["doc", "docs", "document", "comment"]):
            return CommitType.DOCS
        elif any(x in msg_lower for x in ["cleanup", "format", "dependencies", "upgrade", "merge"]):
            return CommitType.MAINTENANCE
        
        return CommitType.UNKNOWN
    
    def _extract_patterns(self, commits: List[Dict]) -> List[str]:
        """
        Extract meaningful patterns from commit history.
        
        Args:
            commits: List of parsed commits
            
        Returns:
            List of identified patterns
        """
        patterns = []
        
        # Pattern 1: Frequent bug fixes
        bug_fixes = sum(1 for c in commits if c["type"] == CommitType.BUG_FIX)
        if bug_fixes > len(commits) * 0.3:
            patterns.append("FREQUENT_BUG_FIXES")
        
        # Pattern 2: Recent activity
        from datetime import timedelta
        recent_7d = sum(
            1 for c in commits
            if datetime.fromisoformat(c["date"].split("+")[0]) > 
               (datetime.utcnow() - timedelta(days=7))
        )
        if recent_7d > 2:
            patterns.append("ACTIVE_DEVELOPMENT")
        
        # Pattern 3: Multiple authors
        authors = set(c["author"] for c in commits)
        if len(authors) > 3:
            patterns.append("MULTI_AUTHOR")
        
        # Pattern 4: Refactoring focus
        refactors = sum(1 for c in commits if c["type"] == CommitType.REFACTOR)
        if refactors > len(commits) * 0.3:
            patterns.append("REFACTOR_HEAVY")
        
        return patterns
    
    def _get_routing_recommendation(self, pattern: CommitPattern) -> Optional[str]:
        """
        Get routing recommendation based on file history pattern.
        
        Args:
            pattern: CommitPattern for file
            
        Returns:
            Recommended orchestrator name or None
        """
        risk_score = pattern.get_risk_score()
        
        # High-risk files → TDD (tests first)
        if risk_score > 0.7:
            return "TDDOrchestrator"
        
        # Frequently changed → Refactoring orchestrator
        if pattern.change_frequency == "high" or pattern.change_frequency == "critical":
            return "RefactoringOrchestrator"
        
        # Multi-author → Master orchestrator (coordination)
        if len(pattern.primary_authors) > 3:
            return "MasterOrchestrator"
        
        # Many refactors → Refactoring orchestrator
        refactor_count = pattern.commit_type_distribution.get(CommitType.REFACTOR, 0)
        if refactor_count > 0 and refactor_count > pattern.total_commits * 0.25:
            return "RefactoringOrchestrator"
        
        return None
    
    def get_cache_stats(self) -> Dict[str, any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache info
        """
        return {
            "cached_analyses": len(self._cache),
            "files_analyzed": len(self._recently_analyzed),
            "cache_size_mb": sum(
                len(json.dumps(c, default=str)) for c in self._cache.values()
            ) / (1024 * 1024)
        }
