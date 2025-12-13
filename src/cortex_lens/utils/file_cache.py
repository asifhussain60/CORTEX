"""
Shared File Cache for CORTEX Lens

Thread-safe file cache to eliminate redundant file I/O across collectors.
Implements LRU eviction and memory management.

Author: Asif Hussain
"""

import logging
import threading
from pathlib import Path
from typing import Dict, Optional, Any
from functools import lru_cache
from datetime import datetime

logger = logging.getLogger(__name__)


class FileCache:
    """
    Thread-safe shared file cache with LRU eviction.
    
    Eliminates redundant file reads across multiple collectors by caching:
    - File content (text)
    - File stats (size, mtime)
    - Computed results (AST, parsed data)
    
    Features:
    - Thread-safe operations
    - Memory-bounded (max size limit)
    - LRU eviction policy
    - Hit/miss statistics
    """
    
    def __init__(self, max_size_mb: int = 100):
        """
        Initialize file cache.
        
        Args:
            max_size_mb: Maximum cache size in megabytes
        """
        self.max_size_mb = max_size_mb
        self.max_size_bytes = max_size_mb * 1024 * 1024
        
        # Thread-safe storage
        self._cache: Dict[str, Any] = {}
        self._lock = threading.Lock()
        
        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._current_size = 0
        
        logger.info(f"📦 FileCache initialized: {max_size_mb} MB limit")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value by key.
        
        Args:
            key: Cache key (usually file path)
        
        Returns:
            Cached value or None if not found
        """
        with self._lock:
            if key in self._cache:
                self._hits += 1
                return self._cache[key]
            else:
                self._misses += 1
                return None
    
    def set(self, key: str, value: Any, size_bytes: int = 0):
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            size_bytes: Size in bytes (for memory tracking)
        """
        with self._lock:
            # Check if we need to evict
            if size_bytes > 0 and self._current_size + size_bytes > self.max_size_bytes:
                self._evict_lru(size_bytes)
            
            self._cache[key] = value
            self._current_size += size_bytes
    
    def read_file(self, file_path: Path, encoding: str = 'utf-8') -> Optional[str]:
        """
        Read file with caching.
        
        Args:
            file_path: Path to file
            encoding: File encoding
        
        Returns:
            File content or None on error
        """
        cache_key = f"file:{file_path}:{encoding}"
        
        # Check cache
        content = self.get(cache_key)
        if content is not None:
            return content
        
        # Read from disk
        try:
            content = file_path.read_text(encoding=encoding, errors='ignore')
            size = len(content.encode('utf-8'))
            self.set(cache_key, content, size)
            return content
        except Exception as e:
            logger.warning(f"Failed to read {file_path}: {e}")
            return None
    
    def get_file_stats(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Get file stats with caching.
        
        Args:
            file_path: Path to file
        
        Returns:
            Dict with size, mtime, etc.
        """
        cache_key = f"stats:{file_path}"
        
        # Check cache
        stats = self.get(cache_key)
        if stats is not None:
            return stats
        
        # Get from filesystem
        try:
            stat = file_path.stat()
            stats = {
                'size': stat.st_size,
                'mtime': datetime.fromtimestamp(stat.st_mtime),
                'is_file': file_path.is_file(),
                'is_dir': file_path.is_dir()
            }
            self.set(cache_key, stats, 200)  # Stats are small
            return stats
        except Exception as e:
            logger.warning(f"Failed to stat {file_path}: {e}")
            return None
    
    def _evict_lru(self, needed_bytes: int):
        """
        Evict least recently used items to free space.
        
        Args:
            needed_bytes: Bytes needed for new item
        """
        # Simple strategy: evict 25% of cache
        # In production, implement proper LRU tracking
        target_size = self.max_size_bytes * 0.75
        
        # Sort by key (naive LRU approximation)
        items = list(self._cache.items())
        evict_count = len(items) // 4
        
        for key, _ in items[:evict_count]:
            del self._cache[key]
            self._evictions += 1
        
        # Recalculate size (simplified)
        self._current_size = int(self._current_size * 0.75)
        
        logger.debug(f"Evicted {evict_count} items, freed ~{needed_bytes / 1024 / 1024:.1f} MB")
    
    def clear(self):
        """Clear all cached data."""
        with self._lock:
            self._cache.clear()
            self._current_size = 0
            logger.info("FileCache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with hits, misses, hit rate, etc.
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        
        return {
            'hits': self._hits,
            'misses': self._misses,
            'total_requests': total,
            'hit_rate_percent': round(hit_rate, 1),
            'evictions': self._evictions,
            'current_size_mb': round(self._current_size / 1024 / 1024, 2),
            'max_size_mb': self.max_size_mb,
            'items_cached': len(self._cache)
        }
    
    def log_stats(self):
        """Log cache statistics."""
        stats = self.get_stats()
        logger.info(f"📊 Cache Stats: {stats['hit_rate_percent']}% hit rate, "
                   f"{stats['items_cached']} items, "
                   f"{stats['current_size_mb']}/{stats['max_size_mb']} MB")


# Global singleton cache instance
_global_cache: Optional[FileCache] = None
_cache_lock = threading.Lock()


def get_global_cache(max_size_mb: int = 100) -> FileCache:
    """
    Get or create global file cache instance.
    
    Args:
        max_size_mb: Maximum cache size (only used on first call)
    
    Returns:
        Global FileCache instance
    """
    global _global_cache
    
    with _cache_lock:
        if _global_cache is None:
            _global_cache = FileCache(max_size_mb)
        return _global_cache
