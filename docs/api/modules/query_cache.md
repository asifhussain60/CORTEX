# query_cache

CORTEX 3.0 Phase 2 - Intelligent Query Cache
============================================

High-performance caching layer for brain queries with adaptive intelligence.
Optimizes query response times through smart caching strategies.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Phase: Phase 2 - Brain Performance Optimization (Task 2)
Integration: Query Cache + Performance Engine + Brain Tiers


## Table of Contents

### Classes
- [CacheStrategy](#cachestrategy)
- [QueryType](#querytype)
- [CacheEntry](#cacheentry)
- [CacheMetrics](#cachemetrics)
- [QueryCacheEngine](#querycacheengine)
- [SmartQueryCache](#smartquerycache)


## Overview

- **Classes:** 6
- **Functions:** 0
- **Dependencies:** collections, dataclasses, datetime, enum, hashlib, json, logging, pathlib, pickle, threading, time, typing


## Classes

### CacheStrategy

```python
class CacheStrategy(Enum)
```

Cache strategy types.



---

### QueryType

```python
class QueryType(Enum)
```

Query type classification.



---

### CacheEntry

```python
class CacheEntry
```

**Decorators:** `dataclass`

Cache entry with metadata.


**Attributes:**

- `key`: str
- `value`: Any
- `query_type`: QueryType
- `timestamp`: datetime
- `access_count`: int
- `last_accessed`: datetime
- `size_bytes`: int
- `ttl_seconds`: int
- `performance_impact`: float



---

### CacheMetrics

```python
class CacheMetrics
```

**Decorators:** `dataclass`

Cache performance metrics.


**Attributes:**

- `hits`: int
- `misses`: int
- `hit_rate`: float
- `total_requests`: int
- `average_response_time_ms`: float
- `memory_usage_mb`: float
- `entries_count`: int
- `evictions`: int



---

### QueryCacheEngine

```python
class QueryCacheEngine
```

Intelligent query cache with adaptive strategies.

Features:
- Multi-strategy caching (LRU, LFU, TTL, Adaptive)
- Query type-specific optimization
- Memory-aware eviction
- Performance monitoring
- Thread-safe operations


**Methods:**

  #### `get`

  ```python
  get(self, query: str, query_type: QueryType) -> Optional[Any]
  ```

  Get cached query result.

Args:
    query: Query string
    query_type: Type of query for optimization
    
Returns:
    Cached result or None if not found

  **Parameters:**

  - `self`
  - `query` (str): Query string
  - `query_type` (QueryType) = `QueryType.GENERAL`: Type of query for optimization


  **Returns:** Optional[Any]
    Cached result or None if not found


  #### `put`

  ```python
  put(self, query: str, result: Any, query_type: QueryType, execution_time_ms: float) -> bool
  ```

  Cache query result.

Args:
    query: Query string
    result: Query result to cache
    query_type: Type of query
    execution_time_ms: Original query execution time
    
Returns:
    True if cached successfully

  **Parameters:**

  - `self`
  - `query` (str): Query string
  - `result` (Any): Query result to cache
  - `query_type` (QueryType) = `QueryType.GENERAL`: Type of query
  - `execution_time_ms` (float) = `0.0`: Original query execution time


  **Returns:** bool
    True if cached successfully


  #### `invalidate`

  ```python
  invalidate(self, query: str, query_type: QueryType) -> int
  ```

  Invalidate cache entries.

Args:
    query: Specific query to invalidate (optional)
    query_type: Query type to invalidate (optional)
    
Returns:
    Number of entries invalidated

  **Parameters:**

  - `self`
  - `query` (str) = `None`: Specific query to invalidate (optional)
  - `query_type` (QueryType) = `None`: Query type to invalidate (optional)


  **Returns:** int
    Number of entries invalidated


  #### `cleanup_expired`

  ```python
  cleanup_expired(self) -> int
  ```

  Remove expired entries.

  **Parameters:**

  - `self`


  **Returns:** int


  #### `get_metrics`

  ```python
  get_metrics(self) -> CacheMetrics
  ```

  Get cache performance metrics.

  **Parameters:**

  - `self`


  **Returns:** CacheMetrics


  #### `get_top_queries`

  ```python
  get_top_queries(self, limit: int) -> List[Tuple[str, int]]
  ```

  Get most frequently accessed queries.

  **Parameters:**

  - `self`
  - `limit` (int) = `10`


  **Returns:** List[Tuple[str, int]]


  #### `optimize_cache`

  ```python
  optimize_cache(self) -> Dict[str, Any]
  ```

  Optimize cache performance.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### SmartQueryCache

```python
class SmartQueryCache
```

High-level interface for smart query caching.

Features:
- Automatic cache key generation
- Query type detection
- Performance monitoring
- Integration with optimization engine


**Methods:**

  #### `cached_query`

  ```python
  cached_query(self, query: str, execute_func, *args, **kwargs) -> Any
  ```

  Execute query with intelligent caching.

Args:
    query: Query string
    execute_func: Function to execute if not cached
    *args, **kwargs: Arguments for execute_func
    
Returns:
    Query result (cached or fresh)

  **Parameters:**

  - `self`
  - `query` (str): Query string
  - `execute_func`: Function to execute if not cached
  - `*args`
  - `**kwargs`


  **Returns:** Any
    Query result (cached or fresh)


  #### `get_cache_stats`

  ```python
  get_cache_stats(self) -> Dict[str, Any]
  ```

  Get comprehensive cache statistics.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---
