# AC-ID: IR-001-02 - Git History Intelligence - Change Frequency
"""
Change Frequency Mapper for CORTEX LENS.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-001-02 - Git History Intelligence

This module identifies hot spots - files that change frequently.

Part of CORTEX LENS context intelligence system.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cortex.brain.analysis.git_history_analyzer import GitHistoryAnalyzer


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class HotSpot:
    """Represents a frequently changed file.
    
    Attributes:
        file_path: Path to the file
        change_count: Number of times file was changed
        last_changed: Date of last change
        authors: List of authors who changed the file
    """
    file_path: str
    change_count: int
    last_changed: Optional[datetime] = None
    authors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "file_path": self.file_path,
            "change_count": self.change_count,
            "last_changed": self.last_changed.isoformat() if self.last_changed else None,
            "authors": self.authors,
        }


# =============================================================================
# CHANGE FREQUENCY MAPPER
# =============================================================================


class ChangeFrequencyMapper:
    """Maps file change frequency to identify hot spots.
    
    Analyzes git history to identify files that change frequently,
    which may indicate areas of active development or instability.
    
    Attributes:
        analyzer: GitHistoryAnalyzer instance
        
    Example:
        >>> analyzer = GitHistoryAnalyzer(Path("/path/to/repo"))
        >>> mapper = ChangeFrequencyMapper(analyzer)
        >>> hot_spots = mapper.get_hot_spots()
        >>> for spot in hot_spots[:10]:
        ...     print(f"{spot.file_path}: {spot.change_count} changes")
    """
    
    def __init__(self, analyzer: "GitHistoryAnalyzer") -> None:
        """Initialize the change frequency mapper.
        
        Args:
            analyzer: GitHistoryAnalyzer instance to use
        """
        self.analyzer = analyzer
        self._cache: Optional[Dict[str, int]] = None
        self._file_authors: Dict[str, List[str]] = {}
        self._file_dates: Dict[str, datetime] = {}
    
    def get_hot_spots(
        self,
        days: Optional[int] = None,
        top_n: int = 20,
    ) -> List[HotSpot]:
        """Get the most frequently changed files.
        
        Args:
            days: Only consider changes within this many days (None = all time)
            top_n: Number of top hot spots to return
            
        Returns:
            List of HotSpot objects, sorted by change frequency
        """
        self._build_cache(days)
        
        if not self._cache:
            return []
        
        # Sort by change count
        sorted_files = sorted(
            self._cache.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:top_n]
        
        hot_spots = []
        for file_path, count in sorted_files:
            hot_spots.append(HotSpot(
                file_path=file_path,
                change_count=count,
                last_changed=self._file_dates.get(file_path),
                authors=list(set(self._file_authors.get(file_path, []))),
            ))
        
        return hot_spots
    
    def get_change_count(self, file_path: Path) -> int:
        """Get change count for a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Number of times file was changed
        """
        self._build_cache()
        
        if not self._cache:
            return 0
        
        return self._cache.get(str(file_path), 0)
    
    def _build_cache(self, days: Optional[int] = None) -> None:
        """Build the change frequency cache.
        
        Args:
            days: Only consider changes within this many days
        """
        if self._cache is not None and days is None:
            return
        
        # Get commits
        if days:
            since = datetime.now() - timedelta(days=days)
            commits = self.analyzer.get_commit_history(max_count=500, since=since)
        else:
            commits = self.analyzer.get_commit_history(max_count=500)
        
        # Count file changes
        file_changes: Counter = Counter()
        self._file_authors = {}
        self._file_dates = {}
        
        for commit in commits:
            files = self.analyzer.get_files_changed_in_commit(commit.hash)
            
            for file_path in files:
                file_changes[file_path] += 1
                
                # Track authors
                if file_path not in self._file_authors:
                    self._file_authors[file_path] = []
                self._file_authors[file_path].append(commit.author)
                
                # Track last change date
                if file_path not in self._file_dates:
                    self._file_dates[file_path] = commit.date
                elif commit.date > self._file_dates[file_path]:
                    self._file_dates[file_path] = commit.date
        
        self._cache = dict(file_changes)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "ChangeFrequencyMapper",
    "HotSpot",
]
