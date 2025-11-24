"""
CORTEX Brain Protection Rules Loader with In-Memory Caching

Implements Option 2: Timestamp-Based Validation caching for brain-protection-rules.yaml.
This module provides optimized loading of brain protection rules with intelligent caching.

Performance Targets:
- First load: ~550ms (YAML parsing overhead)
- Subsequent loads: 1-2ms (timestamp check only)
- Cache invalidation: Automatic on file modification

Implementation Date: November 17, 2025
Optimization: Phase 0 Performance Improvement (99.6% load time reduction)

Reference: cortex-brain/documents/reports/BRAIN-PERFORMANCE-REPORT-2025-11-17.md
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


# Global cache variables
_brain_rules_cache: Optional[Dict[str, Any]] = None
_cache_file_mtime: Optional[float] = None
_cache_hit_count: int = 0
_cache_miss_count: int = 0


def load_brain_protection_rules(rules_path: Optional[Path] = None, force_reload: bool = False) -> Dict[str, Any]:
    """
    Load brain protection rules with intelligent caching.
    
    Caching Strategy (Option 2: Timestamp-Based Validation):
    - First call: Load YAML file (~550ms), cache result + file mtime
    - Subsequent calls: Check file mtime (1-2ms)
      - If unchanged: Return cached result (0ms)
      - If changed: Reload YAML, update cache
    - Force reload: Bypass cache, reload file
    
    Args:
        rules_path: Path to brain-protection-rules.yaml (default: cortex-brain/brain-protection-rules.yaml)
        force_reload: Force reload even if cached (for testing)
    
    Returns:
        Dict containing brain protection rules configuration
    
    Performance:
        - Cold cache: ~550ms (full YAML parse)
        - Warm cache (unchanged file): ~1-2ms (mtime check)
        - Warm cache (changed file): ~550ms (reload)
    
    Examples:
        >>> # First call (cold cache)
        >>> rules = load_brain_protection_rules()  # ~550ms
        >>> 
        >>> # Second call (warm cache, file unchanged)
        >>> rules = load_brain_protection_rules()  # ~1-2ms
        >>> 
        >>> # File modified
        >>> # (edit brain-protection-rules.yaml)
        >>> rules = load_brain_protection_rules()  # ~550ms (auto-reload)
    """
    global _brain_rules_cache, _cache_file_mtime, _cache_hit_count, _cache_miss_count
    
    # Determine rules file path
    if rules_path is None:
        project_root = Path(__file__).parent.parent.parent
        rules_path = project_root / "cortex-brain" / "brain-protection-rules.yaml"
    else:
        rules_path = Path(rules_path)
    
    # Validate file exists
    if not rules_path.exists():
        raise FileNotFoundError(f"Brain protection rules not found: {rules_path}")
    
    # Get current file modification time
    current_mtime = os.path.getmtime(rules_path)
    
    # Check cache validity (unless force reload)
    if not force_reload and _brain_rules_cache is not None and _cache_file_mtime == current_mtime:
        # Cache hit - file unchanged
        _cache_hit_count += 1
        return _brain_rules_cache
    
    # Cache miss - need to reload
    _cache_miss_count += 1
    
    # Load YAML file
    with open(rules_path, 'r', encoding='utf-8') as f:
        rules_config = yaml.safe_load(f)
    
    # Update cache
    _brain_rules_cache = rules_config
    _cache_file_mtime = current_mtime
    
    return rules_config


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache performance statistics.
    
    Returns:
        Dict with cache metrics:
        - cached: Whether cache is currently populated
        - hits: Number of cache hits (file unchanged)
        - misses: Number of cache misses (file reloaded)
        - hit_rate: Cache hit rate percentage
        - last_mtime: Last cached file modification timestamp
    
    Example:
        >>> stats = get_cache_stats()
        >>> print(f"Cache hit rate: {stats['hit_rate']:.1f}%")
        Cache hit rate: 99.0%
    """
    global _brain_rules_cache, _cache_file_mtime, _cache_hit_count, _cache_miss_count
    
    total_calls = _cache_hit_count + _cache_miss_count
    hit_rate = (_cache_hit_count / total_calls * 100) if total_calls > 0 else 0.0
    
    return {
        "cached": _brain_rules_cache is not None,
        "hits": _cache_hit_count,
        "misses": _cache_miss_count,
        "total_calls": total_calls,
        "hit_rate": hit_rate,
        "last_mtime": datetime.fromtimestamp(_cache_file_mtime).isoformat() if _cache_file_mtime else None
    }


def clear_cache():
    """
    Clear the rules cache.
    
    Used for testing or when you want to force a fresh reload.
    Next call to load_brain_protection_rules() will reload from disk.
    
    Example:
        >>> clear_cache()
        >>> rules = load_brain_protection_rules()  # Forces reload
    """
    global _brain_rules_cache, _cache_file_mtime, _cache_hit_count, _cache_miss_count
    
    _brain_rules_cache = None
    _cache_file_mtime = None
    # Keep stats for performance tracking
    # _cache_hit_count = 0
    # _cache_miss_count = 0


def reset_cache_stats():
    """
    Reset cache statistics counters.
    
    Used for benchmarking or testing.
    Does not clear the actual cache - use clear_cache() for that.
    
    Example:
        >>> reset_cache_stats()
        >>> # Run benchmark
        >>> stats = get_cache_stats()
    """
    global _cache_hit_count, _cache_miss_count
    
    _cache_hit_count = 0
    _cache_miss_count = 0


# Convenience functions for common cache operations

def is_cached() -> bool:
    """Check if rules are currently cached."""
    return _brain_rules_cache is not None


def get_cache_age_seconds() -> Optional[float]:
    """
    Get age of cached data in seconds.
    
    Returns:
        Seconds since file was last loaded, or None if not cached
    """
    global _cache_file_mtime
    
    if _cache_file_mtime is None:
        return None
    
    return datetime.now().timestamp() - _cache_file_mtime


# Integration with existing BrainProtector class

def patch_brain_protector():
    """
    Patch BrainProtector class to use cached loader.
    
    This replaces BrainProtector._load_rules() with the cached version.
    Call this once at application startup for automatic caching.
    
    Example:
        >>> from src.tier0.brain_protection_loader import patch_brain_protector
        >>> patch_brain_protector()
        >>> 
        >>> # Now all BrainProtector instances use cached loading
        >>> protector = BrainProtector()  # First instance: ~550ms
        >>> protector2 = BrainProtector()  # Second instance: ~1-2ms
    """
    from src.tier0.brain_protector import BrainProtector
    
    # Save original method
    original_load_rules = BrainProtector._load_rules
    
    # Replace with cached version
    def cached_load_rules(self) -> Dict[str, Any]:
        """Load rules using cached loader."""
        return load_brain_protection_rules(rules_path=self.rules_path)
    
    BrainProtector._load_rules = cached_load_rules
    BrainProtector._original_load_rules = original_load_rules


def unpatch_brain_protector():
    """
    Restore BrainProtector to original non-cached loading.
    
    Used for testing or debugging.
    """
    from src.tier0.brain_protector import BrainProtector
    
    if hasattr(BrainProtector, '_original_load_rules'):
        BrainProtector._load_rules = BrainProtector._original_load_rules
        delattr(BrainProtector, '_original_load_rules')
