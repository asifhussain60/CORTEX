"""
Tests for Git History Cache with TTL.

This module validates 1-hour TTL cache for git history queries.
"""

import pytest
from pathlib import Path
import json
from datetime import datetime, timedelta, UTC
from src.enrichers.git_history_cache import GitHistoryCache


class TestGitHistoryCache:
    """Test git history caching with 1-hour TTL."""
    
    def test_cache_initialization(self):
        """Verify cache initializes with metadata directory."""
        cache = GitHistoryCache()
        assert cache.metadata_dir.exists()
        assert cache.metadata_dir.name == "metadata"
    
    def test_cache_stores_commit_history(self):
        """Verify cache can store commit history."""
        cache = GitHistoryCache()
        
        test_commits = [
            {
                "sha": "abc123",
                "message": "Test commit",
                "author": "test@example.com",
                "date": "2025-11-28T12:00:00Z"
            }
        ]
        
        cache.store_history(test_commits)
        
        # Verify file exists
        cache_file = cache.metadata_dir / "history-cache.json"
        assert cache_file.exists()
    
    def test_cache_retrieves_fresh_history(self):
        """Verify cache returns data if < 1 hour old."""
        cache = GitHistoryCache()
        
        test_commits = [
            {
                "sha": "def456",
                "message": "Fresh commit",
                "author": "fresh@example.com",
                "date": "2025-11-28T13:00:00Z"
            }
        ]
        
        cache.store_history(test_commits)
        
        # Retrieve immediately (should be fresh)
        result = cache.get_history()
        
        assert result is not None
        assert len(result) == 1
        assert result[0]["sha"] == "def456"
    
    def test_cache_returns_none_for_stale_data(self):
        """Verify cache returns None if > 1 hour old."""
        cache = GitHistoryCache()
        cache_file = cache.metadata_dir / "history-cache.json"
        
        # Write cache with old timestamp (2 hours ago)
        old_timestamp = datetime.now(UTC) - timedelta(hours=2)
        old_data = {
            "cached_at": old_timestamp.isoformat(),
            "commits": [
                {
                    "sha": "old123",
                    "message": "Stale commit"
                }
            ]
        }
        
        cache_file.write_text(json.dumps(old_data))
        
        # Retrieve (should return None due to staleness)
        result = cache.get_history()
        
        assert result is None
    
    def test_cache_returns_none_if_no_cache_exists(self):
        """Verify cache returns None if cache file doesn't exist."""
        cache = GitHistoryCache()
        cache_file = cache.metadata_dir / "history-cache.json"
        
        # Ensure cache doesn't exist
        if cache_file.exists():
            cache_file.unlink()
        
        result = cache.get_history()
        
        assert result is None
    
    def test_cache_clears_old_data(self):
        """Verify cache can clear stale data."""
        cache = GitHistoryCache()
        
        # Store some data
        test_commits = [{"sha": "clear123", "message": "To be cleared"}]
        cache.store_history(test_commits)
        
        cache_file = cache.metadata_dir / "history-cache.json"
        assert cache_file.exists()
        
        # Clear cache
        cache.clear_cache()
        
        assert not cache_file.exists()
    
    def test_ttl_boundary_59_minutes(self):
        """Verify data at 59 minutes is still fresh."""
        cache = GitHistoryCache()
        cache_file = cache.metadata_dir / "history-cache.json"
        
        # Write cache with 59 minutes old timestamp
        almost_stale = datetime.now(UTC) - timedelta(minutes=59)
        data = {
            "cached_at": almost_stale.isoformat(),
            "commits": [{"sha": "boundary123", "message": "Boundary test"}]
        }
        
        cache_file.write_text(json.dumps(data))
        
        result = cache.get_history()
        
        # Should still be fresh at 59 minutes
        assert result is not None
        assert result[0]["sha"] == "boundary123"
    
    def test_ttl_boundary_61_minutes(self):
        """Verify data at 61 minutes is stale."""
        cache = GitHistoryCache()
        cache_file = cache.metadata_dir / "history-cache.json"
        
        # Write cache with 61 minutes old timestamp
        stale = datetime.now(UTC) - timedelta(minutes=61)
        data = {
            "cached_at": stale.isoformat(),
            "commits": [{"sha": "stale123", "message": "Stale test"}]
        }
        
        cache_file.write_text(json.dumps(data))
        
        result = cache.get_history()
        
        # Should be stale at 61 minutes
        assert result is None
