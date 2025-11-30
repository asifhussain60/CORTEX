"""
Code Smell Detection Cache for Refactoring Intelligence Optimization

Caches smell detection results with file hash validation.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 3 - Milestone 3.2 (Production Optimization)
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
from pathlib import Path


@dataclass
class SmellCacheEntry:
    """Cached code smell detection result."""
    smells: List[dict]  # List of detected smells
    file_hash: str  # MD5 hash of file content
    cached_at: datetime
    smell_types: List[str] = field(default_factory=list)  # Types of smells found
    total_smells: int = 0
    ttl: timedelta = field(default_factory=lambda: timedelta(hours=1))
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return datetime.now() - self.cached_at > self.ttl
    
    def is_valid_for_hash(self, file_hash: str) -> bool:
        """Check if cache is valid for given file hash."""
        return self.file_hash == file_hash and not self.is_expired()


class SmellCache:
    """
    Cache for code smell detection results.
    
    Caches smell detection to avoid repeated AST analysis.
    Invalidates when file content changes (via hash comparison).
    
    Features:
    - File hash-based invalidation
    - TTL-based expiration
    - Smell type statistics
    - Memory-efficient storage
    
    Performance Impact:
    - Expected speedup: 5-20x on repeated analysis
    - Memory usage: ~5-20KB per cached file
    """
    
    def __init__(self, default_ttl_hours: int = 1):
        """
        Initialize smell cache.
        
        Args:
            default_ttl_hours: Default time-to-live in hours
        """
        self.cache: Dict[str, SmellCacheEntry] = {}
        self.default_ttl = timedelta(hours=default_ttl_hours)
        self.hits = 0
        self.misses = 0
    
    def get(self, filepath: str, file_hash: Optional[str] = None) -> Optional[List[dict]]:
        """
        Get cached smells if valid.
        
        Args:
            filepath: Path to source file
            file_hash: MD5 hash of file content (computed if None)
            
        Returns:
            List of detected smells if cache valid, None otherwise
        """
        if file_hash is None:
            file_hash = self._compute_file_hash(filepath)
        
        if filepath in self.cache:
            entry = self.cache[filepath]
            
            if entry.is_valid_for_hash(file_hash):
                self.hits += 1
                return entry.smells
            else:
                # Invalid - remove
                del self.cache[filepath]
        
        self.misses += 1
        return None
    
    def put(
        self,
        filepath: str,
        smells: List[dict],
        file_hash: Optional[str] = None,
        ttl_hours: Optional[int] = None
    ) -> None:
        """
        Cache smell detection results.
        
        Args:
            filepath: Path to source file
            smells: List of detected smells
            file_hash: MD5 hash of file content (computed if None)
            ttl_hours: Custom TTL in hours (uses default if None)
        """
        if file_hash is None:
            file_hash = self._compute_file_hash(filepath)
        
        ttl = timedelta(hours=ttl_hours) if ttl_hours else self.default_ttl
        
        smell_types = list(set(smell.get('type', 'unknown') for smell in smells))
        
        self.cache[filepath] = SmellCacheEntry(
            smells=smells,
            file_hash=file_hash,
            cached_at=datetime.now(),
            smell_types=smell_types,
            total_smells=len(smells),
            ttl=ttl
        )
    
    def _compute_file_hash(self, filepath: str) -> str:
        """
        Compute MD5 hash of file content.
        
        Args:
            filepath: Path to file
            
        Returns:
            MD5 hash hex digest
        """
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except (IOError, OSError):
            return ""
    
    def invalidate(self, filepath: str) -> bool:
        """
        Invalidate cache entry for file.
        
        Args:
            filepath: Path to file
            
        Returns:
            True if entry existed and was removed
        """
        if filepath in self.cache:
            del self.cache[filepath]
            return True
        return False
    
    def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            Number of entries removed
        """
        expired_files = [
            filepath
            for filepath, entry in self.cache.items()
            if entry.is_expired()
        ]
        
        for filepath in expired_files:
            del self.cache[filepath]
        
        return len(expired_files)
    
    def stats(self) -> Dict[str, any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache metrics
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        total_smells = sum(entry.total_smells for entry in self.cache.values())
        
        # Count smell types across all cached files
        smell_type_counts = {}
        for entry in self.cache.values():
            for smell_type in entry.smell_types:
                smell_type_counts[smell_type] = smell_type_counts.get(smell_type, 0) + 1
        
        return {
            "files_cached": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "total_smells_cached": total_smells,
            "smell_type_distribution": smell_type_counts,
            "default_ttl_hours": int(self.default_ttl.total_seconds() / 3600)
        }
    
    def get_files_with_smells(self, smell_type: Optional[str] = None) -> List[str]:
        """
        Get list of files with detected smells.
        
        Args:
            smell_type: Filter by specific smell type (returns all if None)
            
        Returns:
            List of filepaths
        """
        if smell_type is None:
            return [
                filepath
                for filepath, entry in self.cache.items()
                if entry.total_smells > 0
            ]
        else:
            return [
                filepath
                for filepath, entry in self.cache.items()
                if smell_type in entry.smell_types
            ]
    
    def get_smell_summary(self) -> Dict[str, int]:
        """
        Get summary of all detected smells by type.
        
        Returns:
            Dictionary mapping smell type to count
        """
        summary = {}
        
        for entry in self.cache.values():
            for smell in entry.smells:
                smell_type = smell.get('type', 'unknown')
                summary[smell_type] = summary.get(smell_type, 0) + 1
        
        return summary


# Global cache instance
_global_smell_cache: Optional[SmellCache] = None


def get_smell_cache(ttl_hours: int = 1) -> SmellCache:
    """
    Get global smell cache instance (singleton).
    
    Args:
        ttl_hours: Default TTL in hours (only used on first call)
        
    Returns:
        Global SmellCache instance
    """
    global _global_smell_cache
    
    if _global_smell_cache is None:
        _global_smell_cache = SmellCache(default_ttl_hours=ttl_hours)
    
    return _global_smell_cache
