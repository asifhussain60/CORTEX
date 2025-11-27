"""
Function Signature Cache

TTL-based caching for function signature analysis results to avoid
re-parsing the same code repeatedly.

Copyright (c) 2024-2025 Asif Hussain. All rights reserved.
"""

import ast
import time
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib


@dataclass
class CachedSignature:
    """Cached function signature analysis result"""
    function_name: str
    parameters: list
    return_type: Optional[str]
    docstring: Optional[str]
    ast_node: ast.FunctionDef
    source_hash: str
    cached_at: float
    access_count: int
    last_accessed: float


class FunctionSignatureCache:
    """
    Caches function signature analysis results with TTL.
    
    Phase 2 Milestone 2.3 - Performance Optimization
    Target: Reduce repeated AST parsing overhead
    """
    
    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        """
        Initialize cache.
        
        Args:
            ttl_seconds: Time-to-live for cache entries (default: 5 minutes)
            max_size: Maximum cache entries (default: 1000)
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.cache: Dict[str, CachedSignature] = {}
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def _generate_key(self, source_code: str, function_name: str) -> str:
        """Generate cache key from source code and function name"""
        # Hash source code for uniqueness
        source_hash = hashlib.sha256(source_code.encode()).hexdigest()[:16]
        return f"{function_name}:{source_hash}"
    
    def _compute_hash(self, source_code: str) -> str:
        """Compute hash of source code for change detection"""
        return hashlib.sha256(source_code.encode()).hexdigest()
    
    def get(
        self,
        source_code: str,
        function_name: str
    ) -> Optional[CachedSignature]:
        """
        Get cached signature if available and not expired.
        
        Args:
            source_code: Source code containing the function
            function_name: Name of function to retrieve
            
        Returns:
            CachedSignature if found and valid, None otherwise
        """
        key = self._generate_key(source_code, function_name)
        
        if key not in self.cache:
            self.misses += 1
            return None
        
        entry = self.cache[key]
        current_time = time.time()
        
        # Check TTL expiration
        if current_time - entry.cached_at > self.ttl_seconds:
            del self.cache[key]
            self.misses += 1
            return None
        
        # Verify source hasn't changed
        current_hash = self._compute_hash(source_code)
        if current_hash != entry.source_hash:
            del self.cache[key]
            self.misses += 1
            return None
        
        # Update access stats
        entry.access_count += 1
        entry.last_accessed = current_time
        self.hits += 1
        
        return entry
    
    def put(
        self,
        source_code: str,
        function_name: str,
        parameters: list,
        return_type: Optional[str],
        docstring: Optional[str],
        ast_node: ast.FunctionDef
    ) -> None:
        """
        Cache function signature analysis result.
        
        Args:
            source_code: Source code containing the function
            function_name: Name of function
            parameters: List of parameter information
            return_type: Return type annotation if present
            docstring: Function docstring if present
            ast_node: AST node for the function
        """
        # Check size limit
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        key = self._generate_key(source_code, function_name)
        source_hash = self._compute_hash(source_code)
        current_time = time.time()
        
        entry = CachedSignature(
            function_name=function_name,
            parameters=parameters,
            return_type=return_type,
            docstring=docstring,
            ast_node=ast_node,
            source_hash=source_hash,
            cached_at=current_time,
            access_count=0,
            last_accessed=current_time
        )
        
        self.cache[key] = entry
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self.cache:
            return
        
        # Find LRU entry
        lru_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_accessed
        )
        
        del self.cache[lru_key]
        self.evictions += 1
    
    def invalidate(self, source_code: str, function_name: str) -> bool:
        """
        Invalidate specific cache entry.
        
        Args:
            source_code: Source code containing the function
            function_name: Name of function to invalidate
            
        Returns:
            True if entry was found and removed, False otherwise
        """
        key = self._generate_key(source_code, function_name)
        
        if key in self.cache:
            del self.cache[key]
            return True
        
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries.
        
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry.cached_at > self.ttl_seconds
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'evictions': self.evictions,
            'ttl_seconds': self.ttl_seconds
        }
    
    def get_entry_info(self, source_code: str, function_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a cached entry.
        
        Args:
            source_code: Source code containing the function
            function_name: Name of function
            
        Returns:
            Dictionary with entry info or None if not found
        """
        key = self._generate_key(source_code, function_name)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        current_time = time.time()
        
        return {
            'function_name': entry.function_name,
            'parameter_count': len(entry.parameters),
            'has_return_type': entry.return_type is not None,
            'has_docstring': entry.docstring is not None,
            'cached_at': datetime.fromtimestamp(entry.cached_at).isoformat(),
            'age_seconds': current_time - entry.cached_at,
            'ttl_remaining': max(0, self.ttl_seconds - (current_time - entry.cached_at)),
            'access_count': entry.access_count,
            'last_accessed': datetime.fromtimestamp(entry.last_accessed).isoformat()
        }


# Global cache instance for module-level access
_global_cache: Optional[FunctionSignatureCache] = None


def get_global_cache() -> FunctionSignatureCache:
    """
    Get or create global cache instance.
    
    Returns:
        Global FunctionSignatureCache instance
    """
    global _global_cache
    
    if _global_cache is None:
        _global_cache = FunctionSignatureCache()
    
    return _global_cache


def reset_global_cache() -> None:
    """Reset global cache instance"""
    global _global_cache
    _global_cache = None
