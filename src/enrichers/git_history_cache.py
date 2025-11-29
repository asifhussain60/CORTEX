"""
Git History Cache with 1-hour TTL.

This module provides caching for git history queries to reduce repeated
git command execution. Cache expires after 1 hour.

Example:
    >>> cache = GitHistoryCache()
    >>> commits = [{"sha": "abc123", "message": "Fix bug"}]
    >>> cache.store_history(commits)
    >>> 
    >>> # Retrieve within 1 hour
    >>> result = cache.get_history()
    >>> print(result)  # Returns commits
    >>> 
    >>> # After 1 hour
    >>> result = cache.get_history()
    >>> print(result)  # Returns None (stale)
"""

from pathlib import Path
import json
from datetime import datetime, timedelta, UTC
from typing import Optional, List, Dict, Any


class GitHistoryCache:
    """
    Cache for git history with 1-hour TTL.
    
    Stores git commit history in .cortex/metadata/history-cache.json
    with automatic expiration after 1 hour.
    
    Attributes:
        metadata_dir: Path to .cortex/metadata directory
        cache_file: Path to history-cache.json
        ttl_hours: Time-to-live in hours (default: 1)
    """
    
    def __init__(self, metadata_dir: Optional[Path] = None):
        """
        Initialize cache with metadata directory.
        
        Args:
            metadata_dir: Path to metadata directory (default: .cortex/metadata)
        """
        if metadata_dir is None:
            metadata_dir = Path(".cortex/metadata")
        
        self.metadata_dir = metadata_dir
        self.cache_file = metadata_dir / "history-cache.json"
        self.ttl_hours = 1
    
    def store_history(self, commits: List[Dict[str, Any]]) -> None:
        """
        Store commit history in cache with current timestamp.
        
        Args:
            commits: List of commit dictionaries with keys: sha, message, author, date
        
        Example:
            >>> cache = GitHistoryCache()
            >>> commits = [
            ...     {
            ...         "sha": "abc123",
            ...         "message": "Fix authentication",
            ...         "author": "dev@example.com",
            ...         "date": "2025-11-28T12:00:00Z"
            ...     }
            ... ]
            >>> cache.store_history(commits)
        """
        cache_data = {
            "cached_at": datetime.now(UTC).isoformat(),
            "commits": commits
        }
        
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file.write_text(json.dumps(cache_data, indent=2))
    
    def get_history(self) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve cached history if fresh (< 1 hour old).
        
        Returns:
            List of commit dictionaries if cache is fresh, None if stale or missing
        
        Example:
            >>> cache = GitHistoryCache()
            >>> result = cache.get_history()
            >>> if result is None:
            ...     print("Cache miss - fetch from git")
            ... else:
            ...     print(f"Cache hit - {len(result)} commits")
        """
        if not self.cache_file.exists():
            return None
        
        try:
            cache_data = json.loads(self.cache_file.read_text())
            cached_at = datetime.fromisoformat(cache_data["cached_at"])
            
            # Check if cache is fresh
            age = datetime.now(UTC) - cached_at
            if age < timedelta(hours=self.ttl_hours):
                return cache_data["commits"]
            
            # Cache is stale
            return None
        
        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache
            return None
    
    def clear_cache(self) -> None:
        """
        Clear cached history by deleting cache file.
        
        Example:
            >>> cache = GitHistoryCache()
            >>> cache.clear_cache()
        """
        if self.cache_file.exists():
            self.cache_file.unlink()
