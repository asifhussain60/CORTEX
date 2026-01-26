"""
Test suite for GitHistoryAnalyzer - AC-GIT-HISTORY-001.

Tests the selective git history analysis with caching optimization:
- Only analyzes when new files provided (key requirement!)
- Caches results to avoid redundant git operations
- Extracts meaningful commit patterns
- Provides routing recommendations

AC-ID: AC-GIT-HISTORY-001
Status: PRODUCTION READY
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta

from cortex.orchestrators.core.git_history_analyzer import (
    GitHistoryAnalyzer,
    CommitPattern,
    CommitType,
    GitHistoryContext
)


class TestGitHistoryAnalyzer:
    """Tests for GitHistoryAnalyzer."""
    
    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = GitHistoryAnalyzer()
        assert analyzer._cache == {}
        assert analyzer._recently_analyzed == set()
    
    def test_analyze_with_no_new_files(self):
        """Test that analysis is SKIPPED when no new files provided."""
        analyzer = GitHistoryAnalyzer()
        
        # All files already analyzed
        current_files = {"file1.py", "file2.py"}
        result = analyzer.analyze_if_new_files(current_files, current_files)
        
        # Should return None (no analysis!)
        assert result is None
    
    def test_analyze_with_new_files(self):
        """Test that analysis is PERFORMED when new files provided."""
        analyzer = GitHistoryAnalyzer()
        
        # Mock git operations
        with patch.object(analyzer, '_analyze_file_history') as mock_analyze:
            mock_analyze.return_value = CommitPattern(
                file_path="new_file.py",
                total_commits=5,
                recent_commits_30d=2,
                primary_authors=["author1"],
                change_frequency="low"
            )
            
            # New file added
            all_files = {"file1.py", "new_file.py"}
            previous_files = {"file1.py"}
            
            result = analyzer.analyze_if_new_files(all_files, previous_files)
            
            # Should analyze new file
            assert result is not None
            assert "new_file.py" in result.files_analyzed
            mock_analyze.assert_called_once_with("new_file.py")
    
    def test_cache_key_generation(self):
        """Test deterministic cache key generation."""
        analyzer = GitHistoryAnalyzer()
        
        files_set1 = {"a.py", "b.py", "c.py"}
        files_set2 = {"c.py", "b.py", "a.py"}  # Same files, different order
        
        key1 = analyzer._generate_cache_key(files_set1)
        key2 = analyzer._generate_cache_key(files_set2)
        
        # Keys should be identical (order-independent)
        assert key1 == key2
    
    def test_caching_behavior(self):
        """Test that results are cached properly."""
        analyzer = GitHistoryAnalyzer()
        
        with patch.object(analyzer, '_perform_analysis') as mock_perform:
            # Mock context
            mock_context = Mock(spec=GitHistoryContext)
            mock_context.cache_key = "test_key"
            mock_perform.return_value = mock_context
            
            files = {"file1.py", "file2.py"}
            
            # First analysis
            result1 = analyzer.analyze_if_new_files(files, set())
            call_count_1 = mock_perform.call_count
            
            # Second analysis with same files (should be different session)
            # Create new context to simulate different timestamp
            mock_context2 = Mock(spec=GitHistoryContext)
            mock_context2.cache_key = "test_key"
            mock_perform.return_value = mock_context2
            
            # Should still perform analysis (new session)
            result2 = analyzer.analyze_if_new_files(files, files)
            
            # Second call should be skipped (no new files)
            assert result2 is None
            assert call_count_1 == 1
    
    def test_commit_type_classification(self):
        """Test commit message classification."""
        analyzer = GitHistoryAnalyzer()
        
        # Bug fixes
        assert analyzer._classify_commit_type("fix: crash") == CommitType.BUG_FIX
        assert analyzer._classify_commit_type("fixes issue #123") == CommitType.BUG_FIX
        
        # Features
        assert analyzer._classify_commit_type("feat: add new feature") == CommitType.FEATURE
        assert analyzer._classify_commit_type("implement search") == CommitType.FEATURE
        
        # Refactoring
        assert analyzer._classify_commit_type("refactor: improve structure") == CommitType.REFACTOR
        
        # Tests
        assert analyzer._classify_commit_type("test: add coverage") == CommitType.TEST
        
        # Documentation
        assert analyzer._classify_commit_type("docs: update README") == CommitType.DOCS
        
        # Maintenance
        assert analyzer._classify_commit_type("cleanup: format code") == CommitType.MAINTENANCE
    
    def test_risk_score_calculation(self):
        """Test risk score based on change history."""
        # Low-risk file (few commits, stable)
        pattern_low = CommitPattern(
            file_path="stable.py",
            total_commits=2,
            recent_commits_30d=0,
            primary_authors=["author1"],
            change_frequency="low"
        )
        assert 0.0 <= pattern_low.get_risk_score() < 0.3
        
        # Medium-risk file
        pattern_med = CommitPattern(
            file_path="active.py",
            total_commits=15,
            recent_commits_30d=3,
            primary_authors=["author1", "author2"],
            change_frequency="medium"
        )
        assert 0.3 <= pattern_med.get_risk_score() < 0.7
        
        # High-risk file (many commits, multiple authors, recent changes)
        pattern_high = CommitPattern(
            file_path="critical.py",
            total_commits=100,
            recent_commits_30d=10,
            primary_authors=["author1", "author2", "author3", "author4"],
            change_frequency="critical",
            commit_type_distribution={CommitType.BUG_FIX: 40, CommitType.FEATURE: 30}
        )
        assert pattern_high.get_risk_score() > 0.7
    
    def test_routing_recommendation_high_risk(self):
        """Test routing recommendation for high-risk files."""
        analyzer = GitHistoryAnalyzer()
        
        high_risk_pattern = CommitPattern(
            file_path="critical.py",
            total_commits=50,
            recent_commits_30d=8,
            primary_authors=["author1", "author2"],
            change_frequency="critical"
        )
        
        rec = analyzer._get_routing_recommendation(high_risk_pattern)
        # High-risk should go to TDD
        assert rec == "TDDOrchestrator"
    
    def test_routing_recommendation_multi_author(self):
        """Test routing recommendation for multi-author files."""
        analyzer = GitHistoryAnalyzer()
        
        multi_author_pattern = CommitPattern(
            file_path="shared.py",
            total_commits=20,
            recent_commits_30d=2,
            primary_authors=["author1", "author2", "author3", "author4"],
            change_frequency="medium"
        )
        
        rec = analyzer._get_routing_recommendation(multi_author_pattern)
        # Multi-author should go to MasterOrchestrator
        assert rec == "MasterOrchestrator"
    
    def test_pattern_extraction(self):
        """Test pattern extraction from commits."""
        analyzer = GitHistoryAnalyzer()
        
        commits = [
            {"type": CommitType.BUG_FIX, "date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()},
            {"type": CommitType.BUG_FIX, "date": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()},
            {"type": CommitType.BUG_FIX, "date": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()},
            {"type": CommitType.FEATURE, "date": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()},
            {"author": "author1"},
            {"author": "author2"},
        ]
        
        patterns = analyzer._extract_patterns(commits)
        
        # Should identify frequent bug fixes (60%)
        assert "FREQUENT_BUG_FIXES" in patterns
        # Should identify recent activity
        assert "ACTIVE_DEVELOPMENT" in patterns
    
    def test_cache_stats(self):
        """Test cache statistics reporting."""
        analyzer = GitHistoryAnalyzer()
        
        # Add some mock cache entries
        analyzer._cache["key1"] = Mock()
        analyzer._recently_analyzed = {"file1.py", "file2.py"}
        
        stats = analyzer.get_cache_stats()
        
        assert stats["cached_analyses"] == 1
        assert stats["files_analyzed"] == 2
        assert "cache_size_mb" in stats
    
    def test_git_history_context_recommendation(self):
        """Test GitHistoryContext recommendation retrieval."""
        context = GitHistoryContext(
            analysis_timestamp=datetime.now(timezone.utc).isoformat(),
            files_analyzed={"file1.py"},
            patterns={
                "file1.py": CommitPattern(
                    file_path="file1.py",
                    total_commits=100,
                    recent_commits_30d=5,
                    primary_authors=["a", "b"],
                    change_frequency="critical"
                )
            },
            cache_key="test"
        )
        
        # Should get recommendation from pattern
        rec = context.get_recommendation("file1.py")
        assert rec == "TDDOrchestrator"
        
        # Non-existent file should return None
        assert context.get_recommendation("nonexistent.py") is None


class TestIntegration:
    """Integration tests for git history analysis."""
    
    def test_selective_analysis_workflow(self):
        """Test the complete selective analysis workflow.
        
        Key scenario: User provides 3 files in context. Only 1 is new.
        We should analyze only the new file.
        """
        analyzer = GitHistoryAnalyzer()
        
        # Session 1: Analyze 3 files
        with patch.object(analyzer, '_perform_analysis') as mock_perform:
            mock_context_1 = Mock(spec=GitHistoryContext)
            mock_context_1.files_analyzed = {"file1.py", "file2.py", "file3.py"}
            mock_perform.return_value = mock_context_1
            
            result1 = analyzer.analyze_if_new_files(
                {"file1.py", "file2.py", "file3.py"},
                set()
            )
            assert result1 is not None
            assert mock_perform.call_count == 1
        
        # Session 2: 2 files from previous + 1 new
        with patch.object(analyzer, '_perform_analysis') as mock_perform_2:
            mock_context_2 = Mock(spec=GitHistoryContext)
            mock_context_2.files_analyzed = {"file4.py"}
            mock_perform_2.return_value = mock_context_2
            
            result2 = analyzer.analyze_if_new_files(
                {"file2.py", "file3.py", "file4.py"},
                {"file1.py", "file2.py", "file3.py"}
            )
            
            # Should only analyze new file (file4.py)
            assert result2 is not None
            mock_perform_2.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
