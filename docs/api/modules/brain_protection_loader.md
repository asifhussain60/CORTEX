# brain_protection_loader

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


## Table of Contents


### Functions
- [load_brain_protection_rules](#load_brain_protection_rules)
- [get_cache_stats](#get_cache_stats)
- [clear_cache](#clear_cache)
- [reset_cache_stats](#reset_cache_stats)
- [is_cached](#is_cached)
- [get_cache_age_seconds](#get_cache_age_seconds)
- [patch_brain_protector](#patch_brain_protector)
- [unpatch_brain_protector](#unpatch_brain_protector)


## Overview

- **Classes:** 0
- **Functions:** 8
- **Dependencies:** datetime, os, pathlib, src, typing, yaml


## Functions

### load_brain_protection_rules

```python
load_brain_protection_rules(rules_path: Optional[Path], force_reload: bool) -> Dict[str, Any]
```

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


**Parameters:**

- `rules_path` (Optional[Path]) = `None`: Path to brain-protection-rules.yaml (default: cortex-brain/brain-protection-rules.yaml)
- `force_reload` (bool) = `False`: Force reload even if cached (for testing)


**Returns:** Dict[str, Any]
  Dict containing brain protection rules configuration


---

### get_cache_stats

```python
get_cache_stats() -> Dict[str, Any]
```

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


**Returns:** Dict[str, Any]
  Dict with cache metrics: - cached: Whether cache is currently populated - hits: Number of cache hits (file unchanged) - misses: Number of cache misses (file reloaded) - hit_rate: Cache hit rate percentage - last_mtime: Last cached file modification timestamp


---

### clear_cache

```python
clear_cache()
```

Clear the rules cache.

Used for testing or when you want to force a fresh reload.
Next call to load_brain_protection_rules() will reload from disk.

Example:
    >>> clear_cache()
    >>> rules = load_brain_protection_rules()  # Forces reload


---

### reset_cache_stats

```python
reset_cache_stats()
```

Reset cache statistics counters.

Used for benchmarking or testing.
Does not clear the actual cache - use clear_cache() for that.

Example:
    >>> reset_cache_stats()
    >>> # Run benchmark
    >>> stats = get_cache_stats()


---

### is_cached

```python
is_cached() -> bool
```

Check if rules are currently cached.


**Returns:** bool


---

### get_cache_age_seconds

```python
get_cache_age_seconds() -> Optional[float]
```

Get age of cached data in seconds.

Returns:
    Seconds since file was last loaded, or None if not cached


**Returns:** Optional[float]
  Seconds since file was last loaded, or None if not cached


---

### patch_brain_protector

```python
patch_brain_protector()
```

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


---

### unpatch_brain_protector

```python
unpatch_brain_protector()
```

Restore BrainProtector to original non-cached loading.

Used for testing or debugging.


---
