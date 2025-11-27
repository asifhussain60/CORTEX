"""
AST Cache for TDD Workflow Optimization

Caches parsed AST trees to avoid redundant parsing operations.
Invalidates cache when file content changes.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 3 - Milestone 3.2 (Production Optimization)
"""

from typing import Dict, Optional
import ast
import hashlib
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CachedAST:
    """Cached AST tree with metadata."""
    tree: ast.AST
    file_hash: str
    cached_at: datetime
    access_count: int = 0
    file_size: int = 0


class ASTCache:
    """
    Cache for parsed AST trees.
    
    Reduces redundant ast.parse() calls by caching trees and invalidating
    when file content changes (detected via MD5 hash).
    
    Features:
    - LRU eviction when cache full
    - File change detection via content hashing
    - Access counting for eviction strategy
    - Cache statistics tracking
    
    Performance Impact:
    - Expected speedup: 2-5x on repeated parsing
    - Memory usage: ~1-2MB per cached AST (typical Python file)
    """
    
    def __init__(self, max_size: int = 100):
        """
        Initialize AST cache.
        
        Args:
            max_size: Maximum number of AST trees to cache
        """
        self.max_size = max_size
        self.cache: Dict[str, CachedAST] = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, filepath: str) -> Optional[ast.AST]:
        """
        Get cached AST tree if file unchanged.
        
        Args:
            filepath: Absolute path to Python file
            
        Returns:
            Cached AST tree if valid, None otherwise
        """
        if not Path(filepath).exists():
            return None
        
        current_hash = self._compute_file_hash(filepath)
        
        if filepath in self.cache:
            cached = self.cache[filepath]
            if cached.file_hash == current_hash:
                # Cache hit - file unchanged
                cached.access_count += 1
                self.hits += 1
                return cached.tree
            else:
                # File changed - invalidate cache entry
                del self.cache[filepath]
        
        self.misses += 1
        return None
    
    def put(self, filepath: str, tree: ast.AST) -> None:
        """
        Cache AST tree.
        
        Args:
            filepath: Absolute path to Python file
            tree: Parsed AST tree
        """
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        file_hash = self._compute_file_hash(filepath)
        file_size = Path(filepath).stat().st_size
        
        self.cache[filepath] = CachedAST(
            tree=tree,
            file_hash=file_hash,
            cached_at=datetime.now(),
            file_size=file_size
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
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry (lowest access_count)."""
        if not self.cache:
            return
        
        lru_key = min(
            self.cache.items(),
            key=lambda x: (x[1].access_count, x[1].cached_at)
        )[0]
        
        del self.cache[lru_key]
    
    def invalidate(self, filepath: str) -> bool:
        """
        Invalidate specific cache entry.
        
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
    
    def stats(self) -> Dict[str, any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache metrics
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        total_memory = sum(c.file_size for c in self.cache.values())
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "total_accesses": sum(c.access_count for c in self.cache.values()),
            "memory_usage_bytes": total_memory,
            "memory_usage_mb": f"{total_memory / 1024 / 1024:.2f}"
        }
    
    def get_most_accessed(self, limit: int = 10) -> list:
        """
        Get most frequently accessed files.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of (filepath, access_count) tuples
        """
        sorted_items = sorted(
            self.cache.items(),
            key=lambda x: x[1].access_count,
            reverse=True
        )
        
        return [(path, cached.access_count) for path, cached in sorted_items[:limit]]


# Global cache instance (singleton pattern)
_global_ast_cache: Optional[ASTCache] = None


def get_ast_cache(max_size: int = 100) -> ASTCache:
    """
    Get global AST cache instance (singleton).
    
    Args:
        max_size: Maximum cache size (only used on first call)
        
    Returns:
        Global ASTCache instance
    """
    global _global_ast_cache
    
    if _global_ast_cache is None:
        _global_ast_cache = ASTCache(max_size=max_size)
    
    return _global_ast_cache


def parse_file_cached(filepath: str, cache: Optional[ASTCache] = None) -> ast.AST:
    """
    Parse Python file with caching.
    
    Args:
        filepath: Path to Python file
        cache: ASTCache instance (uses global if None)
        
    Returns:
        Parsed AST tree
        
    Raises:
        SyntaxError: If file has syntax errors
        FileNotFoundError: If file doesn't exist
    """
    if cache is None:
        cache = get_ast_cache()
    
    # Try cache first
    tree = cache.get(filepath)
    
    if tree is not None:
        return tree
    
    # Cache miss - parse and cache
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tree = ast.parse(content, filename=filepath)
    cache.put(filepath, tree)
    
    return tree
