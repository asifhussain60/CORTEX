"""
Pattern Cache for Edge Case Analysis Optimization

Caches edge case pattern matches to avoid repeated regex/AST analysis.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 3 - Milestone 3.2 (Production Optimization)
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class PatternMatch:
    """Cached edge case pattern match result."""
    patterns: List[str]  # Matched pattern names (e.g., "empty_string", "none_value")
    locations: List[int]  # Line numbers where patterns found
    confidence: float  # Overall confidence score (0.0-1.0)
    matched_at: datetime = field(default_factory=datetime.now)
    parameter_names: List[str] = field(default_factory=list)  # Parameter names analyzed


class PatternCache:
    """
    Cache for edge case pattern matches.
    
    Avoids repeated pattern matching on same functions.
    Invalidates when file changes (coordinated with ASTCache).
    
    Cache Key: (filepath, function_name)
    
    Performance Impact:
    - Expected speedup: 3-10x on repeated analysis
    - Memory usage: ~1-5KB per cached function
    """
    
    def __init__(self, ttl_minutes: int = 60):
        """
        Initialize pattern cache.
        
        Args:
            ttl_minutes: Time-to-live for cache entries (minutes)
        """
        self.cache: Dict[str, Dict[str, PatternMatch]] = {}
        # Structure: filepath -> function_name -> PatternMatch
        
        self.ttl = timedelta(minutes=ttl_minutes)
        self.hits = 0
        self.misses = 0
    
    def get(self, filepath: str, function_name: str) -> Optional[PatternMatch]:
        """
        Get cached pattern match.
        
        Args:
            filepath: Path to source file
            function_name: Function name
            
        Returns:
            PatternMatch if cached and valid, None otherwise
        """
        if filepath not in self.cache:
            self.misses += 1
            return None
        
        if function_name not in self.cache[filepath]:
            self.misses += 1
            return None
        
        match = self.cache[filepath][function_name]
        
        # Check TTL
        if datetime.now() - match.matched_at > self.ttl:
            del self.cache[filepath][function_name]
            self.misses += 1
            return None
        
        self.hits += 1
        return match
    
    def put(
        self,
        filepath: str,
        function_name: str,
        patterns: List[str],
        locations: List[int],
        confidence: float,
        parameter_names: List[str] = None
    ) -> None:
        """
        Cache pattern match result.
        
        Args:
            filepath: Path to source file
            function_name: Function name
            patterns: Matched pattern names
            locations: Line numbers
            confidence: Overall confidence score
            parameter_names: Parameter names analyzed
        """
        if filepath not in self.cache:
            self.cache[filepath] = {}
        
        self.cache[filepath][function_name] = PatternMatch(
            patterns=patterns,
            locations=locations,
            confidence=confidence,
            parameter_names=parameter_names or []
        )
    
    def invalidate_file(self, filepath: str) -> int:
        """
        Invalidate all patterns for a file.
        
        Args:
            filepath: Path to file
            
        Returns:
            Number of entries invalidated
        """
        if filepath in self.cache:
            count = len(self.cache[filepath])
            del self.cache[filepath]
            return count
        return 0
    
    def invalidate_function(self, filepath: str, function_name: str) -> bool:
        """
        Invalidate specific function pattern.
        
        Args:
            filepath: Path to file
            function_name: Function name
            
        Returns:
            True if entry existed and was removed
        """
        if filepath in self.cache and function_name in self.cache[filepath]:
            del self.cache[filepath][function_name]
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
        total_files = len(self.cache)
        total_functions = sum(len(funcs) for funcs in self.cache.values())
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "files_cached": total_files,
            "functions_cached": total_functions,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "ttl_minutes": int(self.ttl.total_seconds() / 60)
        }
    
    def get_cached_patterns_summary(self) -> Dict[str, Set[str]]:
        """
        Get summary of all cached patterns by file.
        
        Returns:
            Dictionary mapping filepath to set of pattern names
        """
        summary = {}
        
        for filepath, functions in self.cache.items():
            all_patterns = set()
            for match in functions.values():
                all_patterns.update(match.patterns)
            summary[filepath] = all_patterns
        
        return summary
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            Number of entries removed
        """
        removed_count = 0
        now = datetime.now()
        
        files_to_remove = []
        
        for filepath, functions in self.cache.items():
            functions_to_remove = []
            
            for function_name, match in functions.items():
                if now - match.matched_at > self.ttl:
                    functions_to_remove.append(function_name)
                    removed_count += 1
            
            for function_name in functions_to_remove:
                del functions[function_name]
            
            if not functions:
                files_to_remove.append(filepath)
        
        for filepath in files_to_remove:
            del self.cache[filepath]
        
        return removed_count


# Global cache instance
_global_pattern_cache: Optional[PatternCache] = None


def get_pattern_cache(ttl_minutes: int = 60) -> PatternCache:
    """
    Get global pattern cache instance (singleton).
    
    Args:
        ttl_minutes: TTL in minutes (only used on first call)
        
    Returns:
        Global PatternCache instance
    """
    global _global_pattern_cache
    
    if _global_pattern_cache is None:
        _global_pattern_cache = PatternCache(ttl_minutes=ttl_minutes)
    
    return _global_pattern_cache
