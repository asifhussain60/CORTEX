"""
CORTEX Universal YAML Cache - Timestamp-Based Caching

Provides reusable caching functionality for frequently-accessed YAML files.
Based on proven optimization pattern from Phase 0 (99.9% load time reduction).

Performance Targets:
- First load: ~100-550ms (YAML parsing overhead, file-dependent)
- Subsequent loads: 0.1-2ms (timestamp check only)
- Cache invalidation: Automatic on file modification

Implementation Date: November 21, 2025
Optimization: Phase 1 - Apply timestamp caching to multiple YAML files

Reference: cortex-brain/documents/analysis/optimization-principles.yaml
Pattern: pattern_4_timestamp_caching

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class YAMLCache:
    """
    Universal YAML caching with timestamp-based invalidation.
    
    Supports multiple cached files simultaneously with independent cache management.
    
    Example:
        >>> cache = YAMLCache()
        >>> 
        >>> # First load (cold cache)
        >>> data = cache.load('cortex-brain/response-templates.yaml')  # ~200ms
        >>> 
        >>> # Second load (warm cache, file unchanged)
        >>> data = cache.load('cortex-brain/response-templates.yaml')  # ~0.1ms
        >>> 
        >>> # Different file
        >>> rules = cache.load('cortex-brain/brain-protection-rules.yaml')  # ~150ms
        >>> rules = cache.load('cortex-brain/brain-protection-rules.yaml')  # ~0.1ms
    """
    
    def __init__(self):
        """Initialize YAML cache."""
        # Cache structure: {file_path: {'data': parsed_yaml, 'mtime': file_mtime}}
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._stats: Dict[str, Dict[str, int]] = {}  # Per-file stats
        
    def load(
        self, 
        file_path: str | Path, 
        force_reload: bool = False,
        encoding: str = 'utf-8'
    ) -> Dict[str, Any]:
        """
        Load YAML file with caching.
        
        Args:
            file_path: Path to YAML file (absolute or relative to project root)
            force_reload: Force reload even if cached (for testing)
            encoding: File encoding (default: utf-8)
        
        Returns:
            Parsed YAML data as dictionary
        
        Raises:
            FileNotFoundError: If YAML file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        
        Performance:
            - Cold cache: ~100-550ms (depends on file size/complexity)
            - Warm cache (unchanged): ~0.1-2ms (mtime check only)
            - Warm cache (changed): ~100-550ms (reload)
        """
        # Convert to Path and resolve
        path = Path(file_path)
        if not path.is_absolute():
            # Resolve relative to project root
            project_root = Path(__file__).parent.parent.parent
            path = (project_root / path).resolve()
        
        path_str = str(path)
        
        # Validate file exists
        if not path.exists():
            raise FileNotFoundError(f"YAML file not found: {path}")
        
        # Initialize stats for this file if needed
        if path_str not in self._stats:
            self._stats[path_str] = {'hits': 0, 'misses': 0}
        
        # Get current file modification time
        current_mtime = os.path.getmtime(path)
        
        # Check cache validity (unless force reload)
        if not force_reload and path_str in self._cache:
            cached_entry = self._cache[path_str]
            if cached_entry['mtime'] == current_mtime:
                # Cache hit - file unchanged
                self._stats[path_str]['hits'] += 1
                logger.debug(f"YAML cache HIT: {path.name} (mtime unchanged)")
                return cached_entry['data']
        
        # Cache miss - need to reload
        self._stats[path_str]['misses'] += 1
        logger.debug(f"YAML cache MISS: {path.name} (loading from disk)")
        
        # Load YAML file
        try:
            with open(path, 'r', encoding=encoding) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {path}: {e}")
            raise
        
        # Update cache
        self._cache[path_str] = {
            'data': data,
            'mtime': current_mtime
        }
        
        return data
    
    def get_stats(self, file_path: Optional[str | Path] = None) -> Dict[str, Any]:
        """
        Get cache performance statistics.
        
        Args:
            file_path: Optional specific file to get stats for. 
                      If None, returns aggregated stats for all files.
        
        Returns:
            Dict with cache metrics:
            - If file_path specified:
                - cached: Whether file is currently cached
                - hits: Number of cache hits
                - misses: Number of cache misses
                - hit_rate: Cache hit rate percentage
                - last_mtime: Last cached modification timestamp
            - If file_path is None:
                - total_files: Number of files in cache
                - total_hits: Total cache hits across all files
                - total_misses: Total cache misses
                - overall_hit_rate: Overall hit rate percentage
                - files: Per-file statistics
        
        Example:
            >>> cache = YAMLCache()
            >>> cache.load('file1.yaml')
            >>> cache.load('file1.yaml')
            >>> stats = cache.get_stats('file1.yaml')
            >>> print(f"Hit rate: {stats['hit_rate']:.1f}%")
            Hit rate: 50.0%
        """
        if file_path is not None:
            # Single file stats
            path = Path(file_path)
            if not path.is_absolute():
                project_root = Path(__file__).parent.parent.parent
                path = (project_root / path).resolve()
            
            path_str = str(path)
            
            if path_str not in self._stats:
                return {
                    'cached': False,
                    'hits': 0,
                    'misses': 0,
                    'hit_rate': 0.0,
                    'last_mtime': None
                }
            
            stats = self._stats[path_str]
            total_calls = stats['hits'] + stats['misses']
            hit_rate = (stats['hits'] / total_calls * 100) if total_calls > 0 else 0.0
            
            cached_entry = self._cache.get(path_str)
            last_mtime = None
            if cached_entry:
                last_mtime = datetime.fromtimestamp(cached_entry['mtime']).isoformat()
            
            return {
                'cached': path_str in self._cache,
                'hits': stats['hits'],
                'misses': stats['misses'],
                'total_calls': total_calls,
                'hit_rate': hit_rate,
                'last_mtime': last_mtime
            }
        else:
            # Aggregated stats
            total_hits = sum(s['hits'] for s in self._stats.values())
            total_misses = sum(s['misses'] for s in self._stats.values())
            total_calls = total_hits + total_misses
            overall_hit_rate = (total_hits / total_calls * 100) if total_calls > 0 else 0.0
            
            # Build per-file stats
            files_stats = {}
            for path_str in self._stats:
                file_name = Path(path_str).name
                stats = self._stats[path_str]
                file_total = stats['hits'] + stats['misses']
                file_hit_rate = (stats['hits'] / file_total * 100) if file_total > 0 else 0.0
                
                files_stats[file_name] = {
                    'path': path_str,
                    'hits': stats['hits'],
                    'misses': stats['misses'],
                    'hit_rate': file_hit_rate
                }
            
            return {
                'total_files': len(self._cache),
                'total_hits': total_hits,
                'total_misses': total_misses,
                'total_calls': total_calls,
                'overall_hit_rate': overall_hit_rate,
                'files': files_stats
            }
    
    def clear(self, file_path: Optional[str | Path] = None):
        """
        Clear cache for specific file or all files.
        
        Args:
            file_path: Optional file to clear. If None, clears all files.
        
        Example:
            >>> cache.clear('response-templates.yaml')  # Clear one file
            >>> cache.clear()  # Clear all
        """
        if file_path is not None:
            # Clear specific file
            path = Path(file_path)
            if not path.is_absolute():
                project_root = Path(__file__).parent.parent.parent
                path = (project_root / path).resolve()
            
            path_str = str(path)
            
            if path_str in self._cache:
                del self._cache[path_str]
                logger.debug(f"Cleared cache for: {path.name}")
        else:
            # Clear all files
            self._cache.clear()
            logger.debug("Cleared entire YAML cache")
    
    def reset_stats(self, file_path: Optional[str | Path] = None):
        """
        Reset statistics counters.
        
        Args:
            file_path: Optional file to reset stats for. If None, resets all.
        
        Note:
            Does not clear the actual cache - use clear() for that.
        """
        if file_path is not None:
            # Reset specific file stats
            path = Path(file_path)
            if not path.is_absolute():
                project_root = Path(__file__).parent.parent.parent
                path = (project_root / path).resolve()
            
            path_str = str(path)
            
            if path_str in self._stats:
                self._stats[path_str] = {'hits': 0, 'misses': 0}
        else:
            # Reset all stats
            for path_str in self._stats:
                self._stats[path_str] = {'hits': 0, 'misses': 0}
    
    def is_cached(self, file_path: str | Path) -> bool:
        """
        Check if file is currently cached.
        
        Args:
            file_path: Path to check
        
        Returns:
            True if file is cached, False otherwise
        """
        path = Path(file_path)
        if not path.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            path = (project_root / path).resolve()
        
        return str(path) in self._cache
    
    def get_cache_age_seconds(self, file_path: str | Path) -> Optional[float]:
        """
        Get age of cached data in seconds.
        
        Args:
            file_path: Path to check
        
        Returns:
            Seconds since file was last loaded, or None if not cached
        """
        path = Path(file_path)
        if not path.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            path = (project_root / path).resolve()
        
        path_str = str(path)
        
        if path_str not in self._cache:
            return None
        
        cached_mtime = self._cache[path_str]['mtime']
        return datetime.now().timestamp() - cached_mtime


# Global singleton instance for convenience
_global_cache: Optional[YAMLCache] = None


def get_global_cache() -> YAMLCache:
    """
    Get global YAML cache instance (singleton pattern).
    
    Returns:
        Global YAMLCache instance
    
    Example:
        >>> from src.utils.yaml_cache import get_global_cache
        >>> cache = get_global_cache()
        >>> data = cache.load('cortex-brain/response-templates.yaml')
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = YAMLCache()
    return _global_cache


def load_yaml_cached(file_path: str | Path, force_reload: bool = False) -> Dict[str, Any]:
    """
    Convenience function to load YAML with global cache.
    
    Args:
        file_path: Path to YAML file
        force_reload: Force reload even if cached
    
    Returns:
        Parsed YAML data
    
    Example:
        >>> from src.utils.yaml_cache import load_yaml_cached
        >>> data = load_yaml_cached('cortex-brain/response-templates.yaml')
    """
    cache = get_global_cache()
    return cache.load(file_path, force_reload=force_reload)


def get_cache_stats(file_path: Optional[str | Path] = None) -> Dict[str, Any]:
    """
    Convenience function to get cache stats from global cache.
    
    Args:
        file_path: Optional specific file. If None, returns all stats.
    
    Returns:
        Cache statistics dictionary
    """
    cache = get_global_cache()
    return cache.get_stats(file_path)


def clear_cache(file_path: Optional[str | Path] = None):
    """
    Convenience function to clear global cache.
    
    Args:
        file_path: Optional specific file. If None, clears all.
    """
    cache = get_global_cache()
    cache.clear(file_path)


# Performance testing utilities

def benchmark_cache_performance(file_path: str | Path, iterations: int = 10) -> Dict[str, Any]:
    """
    Benchmark cache performance for a file.
    
    Args:
        file_path: YAML file to benchmark
        iterations: Number of iterations (default: 10)
    
    Returns:
        Dict with benchmark results:
        - cold_load_ms: Time for first load (cold cache)
        - warm_load_ms: Average time for cached loads
        - speedup: Speedup factor (cold / warm)
        - improvement_percent: Performance improvement percentage
    
    Example:
        >>> results = benchmark_cache_performance('cortex-brain/response-templates.yaml')
        >>> print(f"Speedup: {results['speedup']:.1f}x")
    """
    import time
    
    cache = YAMLCache()
    path = Path(file_path)
    
    # Cold cache test
    cache.clear(path)
    start = time.perf_counter()
    cache.load(path)
    cold_time_ms = (time.perf_counter() - start) * 1000
    
    # Warm cache test
    warm_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        cache.load(path)
        warm_times.append((time.perf_counter() - start) * 1000)
    
    warm_avg_ms = sum(warm_times) / len(warm_times)
    speedup = cold_time_ms / warm_avg_ms if warm_avg_ms > 0 else 0
    improvement = ((cold_time_ms - warm_avg_ms) / cold_time_ms * 100) if cold_time_ms > 0 else 0
    
    return {
        'file': str(path.name),
        'cold_load_ms': round(cold_time_ms, 2),
        'warm_load_ms': round(warm_avg_ms, 3),
        'speedup': round(speedup, 1),
        'improvement_percent': round(improvement, 1),
        'iterations': iterations
    }
