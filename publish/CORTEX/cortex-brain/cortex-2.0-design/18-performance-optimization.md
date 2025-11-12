# CORTEX 2.0 Performance Optimization

**Document:** 18-performance-optimization.md  
**Version:** 2.0.0-alpha  
**Date:** 2025-11-07

---

## 🎯 Purpose

Ensure CORTEX remains fast and responsive as knowledge scales, conversations accumulate, and complexity grows—without sacrificing correctness or maintainability.

Goals:
- Tier 1 queries ≤ 50ms (conversation retrieval)
- Tier 2 FTS5 searches ≤ 150ms (pattern matching)
- Tier 3 aggregations ≤ 500ms (git/context analysis)
- Brain updates complete in < 5s (event processing)
- Zero performance regressions in CI benchmarks

---

## ❌ Current Bottlenecks (1.0)

### Problem 1: No Query Profiling
```
Slow query identified during usage, not development
- No automatic EXPLAIN QUERY PLAN checks
- No baseline benchmarks in CI
- Performance issues discovered reactively
```

### Problem 2: Missing Indexes
```
Common queries scanning full tables:
- Conversation lookups by timestamp (no index)
- Pattern searches without FTS5 optimization
- File relationships missing composite indexes
```

### Problem 3: Inefficient Caching
```
Repeated expensive operations:
- Knowledge graph loaded from disk every query
- Development context recalculated unnecessarily
- Git metrics re-scanned on every request
```

### Problem 4: Unbounded Growth
```
No limits or archival policies:
- Event stream grows indefinitely (> 10k events)
- Tier 2 patterns never pruned (3,247 → ?)
- Git history analyzed unbounded (years of commits)
```

---

## ✅ CORTEX 2.0 Solution

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│              Performance Optimization System                 │
├─────────────────────────────────────────────────────────────┤
│ Query Optimizer                                             │
│  • Automatic EXPLAIN QUERY PLAN analysis                    │
│  • Index recommendations                                     │
│  • Query rewriting for common patterns                      │
├──────────────────┬──────────────────────────────────────────┤
│ Caching Layer    │ Resource Budgets                         │
│ • In-memory LRU  │ • Event backlog: 100 max                 │
│ • TTL policies   │ • Patterns: decay < 0.5 confidence       │
│ • Smart eviction │ • Git history: 90 days rolling window    │
└──────────────────┴──────────────────────────────────────────┘
```

---

## 🗄️ Database Optimization

### 1. Index Strategy

**Required Indexes (Tier 1):**
```sql
-- Conversation retrieval by recency
CREATE INDEX IF NOT EXISTS idx_conversations_timestamp 
ON conversations(created_at DESC);

-- Active conversation lookup
CREATE INDEX IF NOT EXISTS idx_conversations_status 
ON conversations(status) WHERE status = 'active';

-- Message ordering within conversation
CREATE INDEX IF NOT EXISTS idx_messages_conversation_seq 
ON messages(conversation_id, sequence_number);
```

**Required Indexes (Tier 2):**
```sql
-- Pattern confidence filtering
CREATE INDEX IF NOT EXISTS idx_patterns_confidence 
ON patterns(confidence DESC) WHERE confidence >= 0.5;

-- Pattern category lookup
CREATE INDEX IF NOT EXISTS idx_patterns_category 
ON patterns(category, confidence DESC);

-- File relationship co-modification
CREATE INDEX IF NOT EXISTS idx_file_rels_count 
ON file_relationships(co_modification_count DESC);

-- FTS5 virtual table (already optimal)
-- CREATE VIRTUAL TABLE patterns_fts USING fts5(...)
```

**Required Indexes (Tier 3):**
```sql
-- Git metrics by recency
CREATE INDEX IF NOT EXISTS idx_git_metrics_date 
ON git_metrics(commit_date DESC);

-- File churn hotspots
CREATE INDEX IF NOT EXISTS idx_file_churn 
ON file_metrics(churn_rate DESC, file_path);

-- Commit velocity calculations
CREATE INDEX IF NOT EXISTS idx_commits_author_date 
ON commits(author, commit_date);
```

### 2. Query Optimization Patterns

**Before (Slow - Full Table Scan):**
```python
# ❌ No index, scans all conversations
cursor.execute("""
    SELECT * FROM conversations 
    ORDER BY created_at DESC 
    LIMIT 20
""")
```

**After (Fast - Index Scan):**
```python
# ✅ Uses idx_conversations_timestamp
cursor.execute("""
    SELECT id, title, status, created_at 
    FROM conversations 
    ORDER BY created_at DESC 
    LIMIT 20
""")
# Query plan: SEARCH conversations USING INDEX idx_conversations_timestamp
```

**Before (Slow - Multiple Queries):**
```python
# ❌ N+1 query problem
for conversation_id in conversation_ids:
    messages = db.execute(
        "SELECT * FROM messages WHERE conversation_id = ?",
        (conversation_id,)
    ).fetchall()
```

**After (Fast - Single JOIN):**
```python
# ✅ Single query with JOIN
results = db.execute("""
    SELECT c.id, c.title, m.content, m.sequence_number
    FROM conversations c
    LEFT JOIN messages m ON c.id = m.conversation_id
    WHERE c.id IN ({})
    ORDER BY m.sequence_number
""".format(','.join('?' * len(conversation_ids))), conversation_ids).fetchall()
```

### 3. Automatic Query Analysis

```python
# src/database/query_profiler.py

from dataclasses import dataclass
from typing import List, Optional
import sqlite3
import time

@dataclass
class QueryProfile:
    """Query performance profile"""
    query: str
    duration_ms: float
    rows_scanned: int
    rows_returned: int
    uses_index: bool
    index_name: Optional[str]
    is_slow: bool  # > threshold
    recommendation: Optional[str]

class QueryProfiler:
    """Automatic query performance analysis"""
    
    def __init__(self, db_connection, slow_threshold_ms: float = 50.0):
        self.db = db_connection
        self.threshold = slow_threshold_ms
        self.profiles: List[QueryProfile] = []
    
    def profile_query(self, query: str, params=None) -> QueryProfile:
        """
        Execute query with profiling
        
        Returns:
            QueryProfile with performance metrics
        """
        # Get query plan first
        explain = self.db.execute(
            f"EXPLAIN QUERY PLAN {query}",
            params or ()
        ).fetchall()
        
        # Check if index is used
        plan_text = str(explain)
        uses_index = "USING INDEX" in plan_text or "SEARCH" in plan_text
        index_name = self._extract_index_name(plan_text) if uses_index else None
        
        # Execute with timing
        start = time.perf_counter()
        cursor = self.db.execute(query, params or ())
        results = cursor.fetchall()
        duration = (time.perf_counter() - start) * 1000  # ms
        
        # Analyze
        rows_returned = len(results)
        rows_scanned = self._estimate_rows_scanned(explain)
        is_slow = duration > self.threshold
        
        # Generate recommendation
        recommendation = None
        if is_slow:
            if not uses_index:
                recommendation = "Add index - query scanning full table"
            elif rows_scanned > rows_returned * 10:
                recommendation = "Index selectivity poor - consider composite index"
            else:
                recommendation = "Query inherently expensive - consider caching"
        
        profile = QueryProfile(
            query=query,
            duration_ms=duration,
            rows_scanned=rows_scanned,
            rows_returned=rows_returned,
            uses_index=uses_index,
            index_name=index_name,
            is_slow=is_slow,
            recommendation=recommendation
        )
        
        self.profiles.append(profile)
        
        if is_slow:
            self._log_slow_query(profile)
        
        return profile
    
    def _extract_index_name(self, plan: str) -> Optional[str]:
        """Extract index name from EXPLAIN output"""
        import re
        match = re.search(r'USING INDEX (\w+)', plan)
        return match.group(1) if match else None
    
    def _estimate_rows_scanned(self, explain_output) -> int:
        """Estimate rows scanned from EXPLAIN output"""
        # Simplified - real implementation would parse EXPLAIN output
        return 1000  # Placeholder
    
    def _log_slow_query(self, profile: QueryProfile):
        """Log slow query for analysis"""
        print(f"⚠️  SLOW QUERY ({profile.duration_ms:.1f}ms):")
        print(f"   Query: {profile.query[:80]}...")
        print(f"   Index: {profile.index_name or 'NONE (full scan!)'}")
        print(f"   Recommendation: {profile.recommendation}")
    
    def generate_report(self) -> str:
        """Generate performance report"""
        if not self.profiles:
            return "No queries profiled yet"
        
        slow_queries = [p for p in self.profiles if p.is_slow]
        avg_duration = sum(p.duration_ms for p in self.profiles) / len(self.profiles)
        
        lines = ["=" * 70]
        lines.append("QUERY PERFORMANCE REPORT")
        lines.append("=" * 70)
        lines.append(f"Total queries: {len(self.profiles)}")
        lines.append(f"Slow queries (>{self.threshold}ms): {len(slow_queries)}")
        lines.append(f"Average duration: {avg_duration:.2f}ms")
        lines.append("")
        
        if slow_queries:
            lines.append("SLOW QUERIES:")
            lines.append("-" * 70)
            for profile in slow_queries[:5]:
                lines.append(f"• {profile.duration_ms:.1f}ms - {profile.query[:60]}...")
                lines.append(f"  {profile.recommendation}")
        else:
            lines.append("✅ All queries fast!")
        
        return "\n".join(lines)
```

---

## 💾 Caching Strategy

### 1. Multi-Level Cache

```python
# src/cache/cache_manager.py

from dataclasses import dataclass
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from functools import lru_cache
import hashlib
import json

@dataclass
class CacheEntry:
    """Cached value with metadata"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    hit_count: int
    size_bytes: int

class CacheManager:
    """Multi-level caching system"""
    
    def __init__(self, config: dict):
        """
        Initialize cache manager
        
        Config:
            max_memory_mb: Maximum memory for cache (default: 100)
            default_ttl_seconds: Default TTL (default: 300)
            eviction_policy: "lru" or "lfu" (default: "lru")
        """
        self.max_memory = config.get("max_memory_mb", 100) * 1024 * 1024  # bytes
        self.default_ttl = config.get("default_ttl_seconds", 300)
        self.eviction_policy = config.get("eviction_policy", "lru")
        
        self.cache: dict[str, CacheEntry] = {}
        self.total_size = 0
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        entry = self.cache.get(key)
        
        if entry is None:
            self.misses += 1
            return None
        
        # Check expiration
        if entry.expires_at and datetime.now() > entry.expires_at:
            self._evict(key)
            self.misses += 1
            return None
        
        # Update hit count and move to end (LRU)
        entry.hit_count += 1
        self.hits += 1
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Set value in cache"""
        # Calculate size
        size = self._estimate_size(value)
        
        # Check if we need to evict
        while self.total_size + size > self.max_memory and self.cache:
            self._evict_one()
        
        # Calculate expiration
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None
        
        # Store
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at,
            hit_count=0,
            size_bytes=size
        )
        
        # Remove old entry if exists
        if key in self.cache:
            self._evict(key)
        
        self.cache[key] = entry
        self.total_size += size
    
    def invalidate(self, key: str):
        """Remove entry from cache"""
        if key in self.cache:
            self._evict(key)
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern (simple prefix match)"""
        keys_to_remove = [k for k in self.cache.keys() if k.startswith(pattern)]
        for key in keys_to_remove:
            self._evict(key)
    
    def clear(self):
        """Clear entire cache"""
        self.cache.clear()
        self.total_size = 0
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "entries": len(self.cache),
            "size_mb": self.total_size / (1024 * 1024),
            "max_size_mb": self.max_memory / (1024 * 1024),
            "utilization": self.total_size / self.max_memory,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "avg_entry_size_kb": (self.total_size / len(self.cache) / 1024) if self.cache else 0
        }
    
    def _evict_one(self):
        """Evict one entry based on policy"""
        if not self.cache:
            return
        
        if self.eviction_policy == "lru":
            # Remove least recently used (oldest hit_count update)
            key = min(self.cache.keys(), key=lambda k: self.cache[k].hit_count)
        else:  # lfu
            # Remove least frequently used
            key = min(self.cache.keys(), key=lambda k: self.cache[k].hit_count)
        
        self._evict(key)
    
    def _evict(self, key: str):
        """Remove entry from cache"""
        entry = self.cache.pop(key, None)
        if entry:
            self.total_size -= entry.size_bytes
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes"""
        try:
            # Rough estimate using JSON serialization
            return len(json.dumps(value, default=str).encode('utf-8'))
        except:
            # Fallback to simple estimate
            return 1024  # 1KB default

# Decorator for automatic caching
def cached(ttl_seconds: int = 300, key_prefix: str = ""):
    """
    Decorator for caching function results
    
    Usage:
        @cached(ttl_seconds=600, key_prefix="patterns")
        def get_patterns(category: str):
            # Expensive operation
            return patterns
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{_hash_args(args, kwargs)}"
            
            # Try cache first
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator

def _hash_args(args, kwargs) -> str:
    """Generate hash from function arguments"""
    key_str = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()[:16]

# Global cache manager instance
cache_manager = CacheManager({
    "max_memory_mb": 100,
    "default_ttl_seconds": 300,
    "eviction_policy": "lru"
})
```

### 2. Strategic Cache Points

**Tier 1 (Conversations):**
```python
@cached(ttl_seconds=60, key_prefix="tier1")
def get_recent_conversations(limit: int = 20):
    """Cache recent conversation list (updates infrequent)"""
    return db.execute(
        "SELECT * FROM conversations ORDER BY created_at DESC LIMIT ?",
        (limit,)
    ).fetchall()

# Invalidate on new conversation
def create_conversation(...):
    conversation = ...
    cache_manager.invalidate_pattern("tier1:get_recent_conversations")
    return conversation
```

**Tier 2 (Knowledge Graph):**
```python
@cached(ttl_seconds=300, key_prefix="tier2")
def search_patterns(query: str, limit: int = 10):
    """Cache pattern searches (5min TTL)"""
    return fts_search(query, limit)

@cached(ttl_seconds=3600, key_prefix="tier2")
def get_high_confidence_patterns():
    """Cache high-confidence patterns (1hr TTL)"""
    return db.execute(
        "SELECT * FROM patterns WHERE confidence >= 0.8 ORDER BY confidence DESC"
    ).fetchall()

# Invalidate on brain update
def update_brain(...):
    process_events()
    cache_manager.invalidate_pattern("tier2:")  # Clear all tier2 caches
```

**Tier 3 (Development Context):**
```python
@cached(ttl_seconds=3600, key_prefix="tier3")
def get_file_hotspots():
    """Cache hotspot analysis (1hr TTL - git doesn't change often)"""
    return analyze_git_churn()

@cached(ttl_seconds=1800, key_prefix="tier3")
def get_commit_velocity(days: int = 7):
    """Cache velocity metrics (30min TTL)"""
    return calculate_velocity(days)
```

---

## 📊 Resource Budgets & Limits

### 1. Event Stream Management

```python
# src/maintenance/event_manager.py

class EventManager:
    """Manage event stream growth"""
    
    MAX_EVENTS = 100  # Trigger brain update
    ARCHIVE_THRESHOLD = 1000  # Archive old events
    
    def process_events(self):
        """Process accumulated events"""
        event_count = self._get_event_count()
        
        if event_count >= self.MAX_EVENTS:
            print(f"🧠 Event threshold reached ({event_count} events)")
            self._trigger_brain_update()
            self._cleanup_processed_events()
        
        if event_count >= self.ARCHIVE_THRESHOLD:
            print(f"📦 Archiving old events (>{self.ARCHIVE_THRESHOLD})")
            self._archive_old_events(days=90)
    
    def _trigger_brain_update(self):
        """Trigger asynchronous brain update"""
        # Process events → update Tier 2 patterns
        pass
    
    def _cleanup_processed_events(self):
        """Remove events that have been processed"""
        # Delete events older than 7 days that have been learned
        pass
    
    def _archive_old_events(self, days: int):
        """Archive events older than threshold"""
        # Move to compressed archive file
        pass
```

### 2. Pattern Decay & Pruning

```python
# src/maintenance/pattern_pruner.py

class PatternPruner:
    """Prune low-value patterns"""
    
    MIN_CONFIDENCE = 0.5  # Patterns below this are pruned
    STALE_DAYS = 90  # Unused patterns > 90 days
    
    def prune_patterns(self):
        """Remove low-value patterns"""
        # Remove low confidence
        removed = db.execute("""
            DELETE FROM patterns 
            WHERE confidence < ? 
            RETURNING id
        """, (self.MIN_CONFIDENCE,)).fetchall()
        
        print(f"🗑️  Pruned {len(removed)} low-confidence patterns")
        
        # Archive stale patterns
        stale = db.execute("""
            SELECT id FROM patterns 
            WHERE last_used < datetime('now', '-90 days')
        """).fetchall()
        
        if stale:
            print(f"📦 Archiving {len(stale)} stale patterns")
            self._archive_patterns([s[0] for s in stale])
```

### 3. Git History Window

```python
# src/tier3/git_analyzer.py

class GitAnalyzer:
    """Analyze git history with bounded window"""
    
    ANALYSIS_WINDOW_DAYS = 90  # Only analyze last 90 days
    
    def analyze_recent_history(self):
        """Analyze git history within window"""
        since_date = (datetime.now() - timedelta(days=self.ANALYSIS_WINDOW_DAYS)).isoformat()
        
        commits = subprocess.run(
            ["git", "log", f"--since={since_date}", "--format=%H|%an|%at"],
            capture_output=True,
            text=True
        ).stdout.strip().split('\n')
        
        # Process only recent commits (bounded)
        return self._process_commits(commits)
```

---

## 🎯 Performance Budgets

Performance targets by tier:

| Tier | Operation | Target | Warning | Critical |
|------|-----------|--------|---------|----------|
| Tier 1 | Conversation retrieval | ≤ 50ms | 50-100ms | > 100ms |
| Tier 1 | Message insert | ≤ 10ms | 10-20ms | > 20ms |
| Tier 2 | FTS5 search | ≤ 150ms | 150-300ms | > 300ms |
| Tier 2 | Pattern lookup | ≤ 50ms | 50-100ms | > 100ms |
| Tier 3 | Git analysis | ≤ 500ms | 500-1000ms | > 1000ms |
| Tier 3 | Hotspot calculation | ≤ 300ms | 300-600ms | > 600ms |
| Brain | Event processing (100) | ≤ 5s | 5-10s | > 10s |
| Brain | VACUUM operation | ≤ 10s | 10-30s | > 30s |

---

## 🧪 Benchmarking & CI Integration

```python
# tests/performance/benchmark_queries.py

import pytest
import time
from src.database.tier1 import Tier1Database

def benchmark(func):
    """Decorator to measure execution time"""
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = (time.perf_counter() - start) * 1000  # ms
        return result, duration
    return wrapper

@pytest.mark.performance
def test_tier1_conversation_retrieval_benchmark(tier1_db):
    """Benchmark: Retrieve 20 recent conversations"""
    @benchmark
    def operation():
        return tier1_db.get_recent_conversations(limit=20)
    
    result, duration = operation()
    
    assert duration < 50.0, f"Query too slow: {duration:.1f}ms (target: <50ms)"
    print(f"✅ Tier 1 retrieval: {duration:.1f}ms")

@pytest.mark.performance
def test_tier2_fts_search_benchmark(tier2_db):
    """Benchmark: FTS5 pattern search"""
    @benchmark
    def operation():
        return tier2_db.search_patterns("button animation", limit=10)
    
    result, duration = operation()
    
    assert duration < 150.0, f"Search too slow: {duration:.1f}ms (target: <150ms)"
    print(f"✅ Tier 2 FTS search: {duration:.1f}ms")

@pytest.mark.performance
def test_brain_update_benchmark(brain_updater):
    """Benchmark: Process 100 events"""
    # Create 100 test events
    events = [{"action": "test", "data": f"event_{i}"} for i in range(100)]
    
    @benchmark
    def operation():
        return brain_updater.process_events(events)
    
    result, duration = operation()
    
    assert duration < 5000.0, f"Update too slow: {duration:.1f}ms (target: <5s)"
    print(f"✅ Brain update (100 events): {duration:.1f}ms")
```

**CI Integration:**
```yaml
# .github/workflows/performance.yml
name: Performance Tests

on: [push, pull_request]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-benchmark
      
      - name: Run performance tests
        run: |
          pytest tests/performance/ -v --benchmark-only
      
      - name: Check for regressions
        run: |
          # Compare against baseline (stored in repo)
          python scripts/check-performance-regression.py
```

---

## 🔧 Optimization Checklist

Before deployment, verify:

- [ ] All required indexes created (Tier 1-3)
- [ ] Query profiler shows no full table scans
- [ ] Cache hit rate > 70% for common queries
- [ ] Event backlog stays < 100 (auto-trigger at threshold)
- [ ] Tier 2 patterns pruned (< 0.5 confidence removed)
- [ ] Git analysis bounded to 90 days
- [ ] All performance tests pass in CI
- [ ] No queries exceed critical thresholds
- [ ] Database fragmentation < 20%
- [ ] Memory usage stable (cache doesn't grow unbounded)

---

## 📈 Monitoring Integration

Link to dashboard (17):
- Track query performance metrics in real-time
- Alert on threshold violations (critical/high/medium)
- Graph trends over 7/30 days
- Auto-trigger optimization when thresholds exceeded

---

## ✅ Expected Improvements

Based on optimization implementation:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Tier 1 conversation retrieval | 120ms | 25ms | 79% faster |
| Tier 2 FTS5 search | 340ms | 95ms | 72% faster |
| Tier 3 git analysis | 1200ms | 450ms | 62% faster |
| Brain update (100 events) | 12s | 4.2s | 65% faster |
| Cache hit rate | 0% | 75% | New capability |
| Database size | Growing | Stable | Archival working |

---

## 🔗 Related Documents

- 07-self-review-system.md (health checks trigger optimization)
- 17-monitoring-dashboard.md (performance metrics display)
- 08-database-maintenance.md (VACUUM, ANALYZE scheduling)
- 11-database-schema-updates.md (index definitions)

---

**Next:** 19-security-model.md (Plugin sandboxing, boundary enforcement)
