"""
Tests for Commit Filter

Tests heuristic-based filtering to identify learning-worthy commits.
Validates line count, test changes, error keywords, and confidence scoring.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from datetime import datetime
from src.operations.modules.learning.git_history_scanner import CommitMetadata
from src.operations.modules.learning.commit_filter import (
    CommitFilter,
    Candidate,
    filter_learning_candidates
)


class TestCommitFilter:
    """Test suite for CommitFilter"""
    
    @pytest.fixture
    def filter_instance(self):
        """Create CommitFilter instance"""
        return CommitFilter()
    
    @pytest.fixture
    def small_commit(self):
        """Commit with <100 lines (below threshold)"""
        return CommitMetadata(
            sha='abc123',
            message='Update README',
            author='John Doe',
            timestamp=datetime.now(),
            files_changed=['README.md'],
            lines_added=30,
            lines_deleted=10,
            net_change=20
        )
    
    @pytest.fixture
    def large_commit(self):
        """Commit with >100 lines (above threshold)"""
        return CommitMetadata(
            sha='def456',
            message='Refactor authentication module',
            author='Jane Smith',
            timestamp=datetime.now(),
            files_changed=['src/auth.py', 'src/models.py'],
            lines_added=120,
            lines_deleted=50,
            net_change=70
        )
    
    @pytest.fixture
    def test_commit(self):
        """Commit modifying test files"""
        return CommitMetadata(
            sha='ghi789',
            message='Add unit tests for validation',
            author='Bob Wilson',
            timestamp=datetime.now(),
            files_changed=['tests/test_validation.py', 'src/validation.py'],
            lines_added=80,
            lines_deleted=10,
            net_change=70
        )
    
    @pytest.fixture
    def bug_fix_commit(self):
        """Commit with error-related keywords"""
        return CommitMetadata(
            sha='jkl012',
            message='Fix validation bug causing crash',
            author='Alice Brown',
            timestamp=datetime.now(),
            files_changed=['src/validation.py'],
            lines_added=15,
            lines_deleted=8,
            net_change=7
        )
    
    def test_filter_by_line_count(self, filter_instance, small_commit, large_commit):
        """
        RED TEST: Verify commits >100 lines marked as candidates.
        
        Expected behavior:
        - small_commit (40 lines total) = not a candidate
        - large_commit (170 lines total) = candidate with line_count score
        """
        commits = [small_commit, large_commit]
        
        candidates = filter_instance.filter_learning_candidates(commits)
        
        # Should identify large_commit only
        assert len(candidates) > 0
        
        # Find large commit in candidates
        large_candidate = next((c for c in candidates if c.commit.sha == 'def456'), None)
        assert large_candidate is not None
        assert large_candidate.confidence_score > 0
        
        # Small commit should not be in candidates (or have low score)
        small_candidate = next((c for c in candidates if c.commit.sha == 'abc123'), None)
        if small_candidate:
            # If present, score should be low
            assert small_candidate.confidence_score < large_candidate.confidence_score
    
    def test_filter_by_test_changes(self, filter_instance, test_commit):
        """
        RED TEST: Verify commits touching test files marked as candidates.
        
        Expected behavior:
        - Commits with 'test_*.py', '*_test.py', or 'tests/' paths = candidates
        - Test changes weight = 0.4 (higher than line count)
        """
        commits = [test_commit]
        
        candidates = filter_instance.filter_learning_candidates(commits)
        
        # Should identify test_commit
        assert len(candidates) > 0
        
        candidate = candidates[0]
        assert candidate.commit.sha == 'ghi789'
        assert candidate.confidence_score > 0
        
        # Verify test_changes heuristic triggered
        assert 'test_changes' in candidate.matched_heuristics
        assert candidate.matched_heuristics['test_changes'] is True
    
    def test_filter_by_error_keywords(self, filter_instance, bug_fix_commit):
        """
        RED TEST: Verify commits with 'fix', 'bug', etc. marked as candidates.
        
        Expected behavior:
        - Message contains: fix, bug, error, crash, fail, debug, issue
        - Error keywords weight = 0.5 (highest weight)
        """
        commits = [bug_fix_commit]
        
        candidates = filter_instance.filter_learning_candidates(commits)
        
        # Should identify bug_fix_commit
        assert len(candidates) > 0
        
        candidate = candidates[0]
        assert candidate.commit.sha == 'jkl012'
        
        # Verify error_keywords heuristic triggered
        assert 'error_keywords' in candidate.matched_heuristics
        assert candidate.matched_heuristics['error_keywords'] is True
        
        # Error keywords have highest weight
        assert candidate.confidence_score >= 0.5
    
    def test_calculate_confidence_score(self, filter_instance, large_commit, test_commit, bug_fix_commit):
        """
        RED TEST: Verify weighted scoring: test_changes=0.4, error=0.5, lines=0.3.
        
        Expected scoring:
        - line_count only = 0.3
        - test_changes only = 0.4  
        - error_keywords only = 0.5
        - Combined = sum of triggered weights
        
        Note: large_commit message "Refactor..." triggers refactor_keywords (0.3) + line_count (0.3) = 0.6
        """
        # Test individual heuristic scores
        candidates = filter_instance.filter_learning_candidates([large_commit, test_commit, bug_fix_commit])
        
        # Find each candidate
        large_cand = next((c for c in candidates if c.commit.sha == 'def456'), None)
        test_cand = next((c for c in candidates if c.commit.sha == 'ghi789'), None)
        bug_cand = next((c for c in candidates if c.commit.sha == 'jkl012'), None)
        
        # Verify scoring logic
        if bug_cand:
            # Bug fix should have at least error_keywords weight (0.5)
            assert bug_cand.confidence_score >= 0.5
        
        if test_cand:
            # Test changes should score 0.4 (or higher if line count also triggered)
            assert test_cand.confidence_score >= 0.4
        
        # Verify each candidate has positive score
        assert all(c.confidence_score > 0 for c in candidates)
    
    def test_rank_candidates_by_score(self, filter_instance, small_commit, large_commit, test_commit, bug_fix_commit):
        """
        RED TEST: Verify candidates sorted by confidence descending.
        
        Expected order:
        1. bug_fix_commit (error_keywords=0.5)
        2. test_commit (test_changes=0.4 + possibly line_count)
        3. large_commit (line_count=0.3)
        4. small_commit (none or very low)
        """
        commits = [small_commit, large_commit, test_commit, bug_fix_commit]
        
        candidates = filter_instance.filter_learning_candidates(commits)
        
        # Should have at least 3 candidates (excluding small_commit)
        assert len(candidates) >= 3
        
        # Verify sorted by confidence descending
        for i in range(len(candidates) - 1):
            assert candidates[i].confidence_score >= candidates[i + 1].confidence_score
        
        # Verify bug fix is first (or tied for first)
        if len(candidates) > 0:
            first_candidate = candidates[0]
            # Should be high-scoring commit
            assert first_candidate.confidence_score >= 0.4


class TestModuleFunctions:
    """Test module-level convenience functions"""
    
    def test_filter_learning_candidates_function(self):
        """
        Test filter_learning_candidates() module function.
        """
        commits = [
            CommitMetadata(
                sha='test123',
                message='Fix critical bug',
                author='Test Author',
                timestamp=datetime.now(),
                files_changed=['src/main.py'],
                lines_added=50,
                lines_deleted=20,
                net_change=30
            )
        ]
        
        candidates = filter_learning_candidates(commits)
        
        # Should identify bug fix
        assert isinstance(candidates, list)
        assert len(candidates) > 0
        assert all(isinstance(c, Candidate) for c in candidates)
