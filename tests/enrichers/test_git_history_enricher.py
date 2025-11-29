"""
Tests for Git History Enricher.

This module validates file-level change analysis from git history.
"""

import pytest
from pathlib import Path
from datetime import datetime
from src.enrichers.git_history_enricher import GitHistoryEnricher


class TestGitHistoryEnricher:
    """Test git history enrichment with file-level analysis."""
    
    def test_enricher_initialization(self):
        """Verify enricher initializes with repository path."""
        enricher = GitHistoryEnricher()
        assert enricher.repo_path.exists()
    
    def test_get_file_history_returns_list(self):
        """Verify get_file_history returns list of changes."""
        enricher = GitHistoryEnricher()
        
        # Use a known file that exists
        history = enricher.get_file_history("README.md")
        
        assert isinstance(history, list)
    
    def test_file_history_includes_commit_sha(self):
        """Verify each history entry includes commit SHA."""
        enricher = GitHistoryEnricher()
        
        history = enricher.get_file_history("README.md", max_commits=5)
        
        if len(history) > 0:
            for entry in history:
                assert "sha" in entry
                assert len(entry["sha"]) > 0
    
    def test_file_history_includes_message(self):
        """Verify each history entry includes commit message."""
        enricher = GitHistoryEnricher()
        
        history = enricher.get_file_history("README.md", max_commits=5)
        
        if len(history) > 0:
            for entry in history:
                assert "message" in entry
    
    def test_file_history_includes_author(self):
        """Verify each history entry includes author."""
        enricher = GitHistoryEnricher()
        
        history = enricher.get_file_history("README.md", max_commits=5)
        
        if len(history) > 0:
            for entry in history:
                assert "author" in entry
    
    def test_file_history_includes_date(self):
        """Verify each history entry includes date."""
        enricher = GitHistoryEnricher()
        
        history = enricher.get_file_history("README.md", max_commits=5)
        
        if len(history) > 0:
            for entry in history:
                assert "date" in entry
    
    def test_file_history_respects_max_commits(self):
        """Verify max_commits parameter limits results."""
        enricher = GitHistoryEnricher()
        
        history = enricher.get_file_history("README.md", max_commits=3)
        
        assert len(history) <= 3
    
    def test_nonexistent_file_returns_empty_list(self):
        """Verify nonexistent file returns empty list."""
        enricher = GitHistoryEnricher()
        
        history = enricher.get_file_history("nonexistent-file-12345.txt")
        
        assert history == []
    
    def test_get_recent_changes_returns_dict(self):
        """Verify get_recent_changes returns dictionary."""
        enricher = GitHistoryEnricher()
        
        changes = enricher.get_recent_changes(days=7)
        
        assert isinstance(changes, dict)
        assert "total_commits" in changes
        assert "files_changed" in changes
    
    def test_get_file_statistics_returns_dict(self):
        """Verify get_file_statistics returns statistics."""
        enricher = GitHistoryEnricher()
        
        stats = enricher.get_file_statistics("README.md")
        
        assert isinstance(stats, dict)
        if stats:  # If file has history
            assert "total_commits" in stats
            assert "first_commit_date" in stats
