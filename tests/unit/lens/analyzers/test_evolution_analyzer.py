"""Unit Tests for Evolution Timeline Analyzer

Tests git history analysis and refactoring pattern detection.

Author: CORTEX Framework
Phase: PHASE-97 S4
CORE Rules: CORE-008 (TDD)
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch
import subprocess

from cortex.lens.analyzers.evolution_analyzer import (
    EvolutionAnalyzer,
    EvolutionMilestone,
    EvolutionTimeline,
    RefactoringEvent,
)


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create temporary git repository.
    
    Args:
        tmp_path: Pytest temporary directory
    
    Returns:
        Path to git repository
    """
    # Initialize git repo
    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        capture_output=True,
    )
    
    # Configure git
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_path,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        capture_output=True,
    )
    
    # Create initial commit
    test_file = tmp_path / "test.py"
    test_file.write_text("def foo(): pass")
    subprocess.run(
        ["git", "add", "."],
        cwd=tmp_path,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=tmp_path,
        capture_output=True,
    )
    
    return tmp_path


@pytest.fixture
def analyzer(git_repo: Path) -> EvolutionAnalyzer:
    """Create evolution analyzer instance.
    
    Args:
        git_repo: Git repository path
    
    Returns:
        EvolutionAnalyzer instance
    """
    return EvolutionAnalyzer(repo_path=git_repo)


class TestRefactoringEvent:
    """Test suite for RefactoringEvent."""
    
    def test_complexity_improvement_positive(self) -> None:
        """Test complexity improvement calculation (positive)."""
        event = RefactoringEvent(
            timestamp=datetime.now(),
            file_path="test.py",
            event_type="refactor",
            complexity_before=100,
            complexity_after=80,
            commit_sha="abc123",
            author="test",
        )
        
        assert event.complexity_improvement == 20
    
    def test_complexity_improvement_negative(self) -> None:
        """Test complexity improvement calculation (negative)."""
        event = RefactoringEvent(
            timestamp=datetime.now(),
            file_path="test.py",
            event_type="change",
            complexity_before=80,
            complexity_after=100,
            commit_sha="abc123",
            author="test",
        )
        
        assert event.complexity_improvement == -20


class TestEvolutionTimeline:
    """Test suite for EvolutionTimeline."""
    
    def test_total_refactorings(self) -> None:
        """Test total refactorings count."""
        now = datetime.now()
        timeline = EvolutionTimeline(
            start_date=now,
            end_date=now,
            refactoring_events=[
                RefactoringEvent(
                    timestamp=now,
                    file_path="a.py",
                    event_type="refactor",
                    complexity_before=100,
                    complexity_after=80,
                    commit_sha="abc",
                    author="test",
                ),
                RefactoringEvent(
                    timestamp=now,
                    file_path="b.py",
                    event_type="extract",
                    complexity_before=90,
                    complexity_after=70,
                    commit_sha="def",
                    author="test",
                ),
            ],
        )
        
        assert timeline.total_refactorings == 2
    
    def test_average_complexity_improvement(self) -> None:
        """Test average complexity improvement calculation."""
        now = datetime.now()
        timeline = EvolutionTimeline(
            start_date=now,
            end_date=now,
            refactoring_events=[
                RefactoringEvent(
                    timestamp=now,
                    file_path="a.py",
                    event_type="refactor",
                    complexity_before=100,
                    complexity_after=80,  # +20 improvement
                    commit_sha="abc",
                    author="test",
                ),
                RefactoringEvent(
                    timestamp=now,
                    file_path="b.py",
                    event_type="extract",
                    complexity_before=90,
                    complexity_after=70,  # +20 improvement
                    commit_sha="def",
                    author="test",
                ),
            ],
        )
        
        assert timeline.average_complexity_improvement == 20.0
    
    def test_average_complexity_improvement_empty(self) -> None:
        """Test average complexity improvement with no refactorings."""
        now = datetime.now()
        timeline = EvolutionTimeline(
            start_date=now,
            end_date=now,
        )
        
        assert timeline.average_complexity_improvement == 0.0


class TestEvolutionAnalyzer:
    """Test suite for EvolutionAnalyzer."""
    
    def test_init(self, analyzer: EvolutionAnalyzer) -> None:
        """Test analyzer initialization.
        
        Args:
            analyzer: Evolution analyzer instance
        """
        assert analyzer.repo_path is not None
        assert analyzer._git_available is True
    
    def test_init_non_git_repo(self, tmp_path: Path) -> None:
        """Test initialization with non-git directory.
        
        Args:
            tmp_path: Pytest temporary directory
        """
        analyzer = EvolutionAnalyzer(repo_path=tmp_path)
        
        assert analyzer._git_available is False
    
    def test_analyze_empty_repo(self, analyzer: EvolutionAnalyzer) -> None:
        """Test analyze on new repository.
        
        Args:
            analyzer: Evolution analyzer instance
        """
        # Use large date range to catch initial commit
        timeline = analyzer.analyze(days=365)
        
        assert isinstance(timeline, EvolutionTimeline)
        assert timeline.total_commits >= 1  # At least initial commit
        assert timeline.start_date < timeline.end_date
    
    def test_analyze_non_git_repo(self, tmp_path: Path) -> None:
        """Test analyze on non-git repository.
        
        Args:
            tmp_path: Pytest temporary directory
        """
        analyzer = EvolutionAnalyzer(repo_path=tmp_path)
        timeline = analyzer.analyze()
        
        assert timeline.total_commits == 0
        assert len(timeline.refactoring_events) == 0
        assert len(timeline.milestones) == 0
    
    def test_analyze_with_refactoring_commits(self, git_repo: Path) -> None:
        """Test analyze detects refactoring commits.
        
        Args:
            git_repo: Git repository path
        """
        # Create refactoring commit
        test_file = git_repo / "refactor.py"
        test_file.write_text("def bar(): pass")
        subprocess.run(
            ["git", "add", "."],
            cwd=git_repo,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Refactor: Extract method bar"],
            cwd=git_repo,
            capture_output=True,
        )
        
        analyzer = EvolutionAnalyzer(repo_path=git_repo)
        timeline = analyzer.analyze(days=1)
        
        assert timeline.total_refactorings >= 1
        assert any(e.event_type == "refactor" for e in timeline.refactoring_events)
    
    def test_analyze_with_milestone_commits(self, git_repo: Path) -> None:
        """Test analyze detects milestone commits.
        
        Args:
            git_repo: Git repository path
        """
        # Create milestone commit
        test_file = git_repo / "milestone.py"
        test_file.write_text("# Phase 1 complete")
        subprocess.run(
            ["git", "add", "."],
            cwd=git_repo,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Phase 1 Complete: Feature X"],
            cwd=git_repo,
            capture_output=True,
        )
        
        analyzer = EvolutionAnalyzer(repo_path=git_repo)
        timeline = analyzer.analyze(days=1)
        
        assert len(timeline.milestones) >= 1
        assert any("phase" in m.title.lower() for m in timeline.milestones)
    
    def test_tech_debt_trend_decreasing(self, analyzer: EvolutionAnalyzer) -> None:
        """Test tech debt trend calculation (decreasing).
        
        Args:
            analyzer: Evolution analyzer instance
        """
        refactorings = [
            RefactoringEvent(
                timestamp=datetime.now(),
                file_path="a.py",
                event_type="refactor",
                complexity_before=100,
                complexity_after=80,  # +20
                commit_sha="abc",
                author="test",
            ),
            RefactoringEvent(
                timestamp=datetime.now(),
                file_path="b.py",
                event_type="simplify",
                complexity_before=90,
                complexity_after=70,  # +20
                commit_sha="def",
                author="test",
            ),
        ]
        
        trend = analyzer._calculate_tech_debt_trend(refactorings)
        
        assert trend == "decreasing"
    
    def test_tech_debt_trend_increasing(self, analyzer: EvolutionAnalyzer) -> None:
        """Test tech debt trend calculation (increasing).
        
        Args:
            analyzer: Evolution analyzer instance
        """
        refactorings = [
            RefactoringEvent(
                timestamp=datetime.now(),
                file_path="a.py",
                event_type="change",
                complexity_before=80,
                complexity_after=100,  # -20
                commit_sha="abc",
                author="test",
            ),
        ]
        
        trend = analyzer._calculate_tech_debt_trend(refactorings)
        
        assert trend == "increasing"
    
    def test_tech_debt_trend_stable(self, analyzer: EvolutionAnalyzer) -> None:
        """Test tech debt trend calculation (stable).
        
        Args:
            analyzer: Evolution analyzer instance
        """
        refactorings = [
            RefactoringEvent(
                timestamp=datetime.now(),
                file_path="a.py",
                event_type="change",
                complexity_before=100,
                complexity_after=98,  # +2
                commit_sha="abc",
                author="test",
            ),
        ]
        
        trend = analyzer._calculate_tech_debt_trend(refactorings)
        
        assert trend == "stable"
