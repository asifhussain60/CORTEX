# CORTEX ValidationCache Troubleshooting Guide

**Version:** 1.0  
**Last Updated:** November 26, 2025  
**Author:** CORTEX Team  

---

## Overview

This guide covers common cache issues, diagnostics, and recovery procedures for CORTEX ValidationCache system.

---

## Common Issues

### 1. Stale Cache Results

**Symptoms:**
- Validation shows outdated results
- Changes to code not reflected in align/deploy
- Cache hit rate high but results incorrect

**Diagnosis:**
```bash
# Check cache age
python src/caching/cache_health.py

# View cache entries
python -c "from src.caching import get_cache; cache = get_cache(); print(cache.get_all_keys('align'))"
```

**Solution:**
```bash
# Clear cache for specific operation
python -c "from src.caching import get_cache; get_cache().invalidate('align')"

# Clear all cache
python -c "from src.caching import get_cache; get_cache().invalidate()"
```

**Prevention:**
- ValidationCache automatically invalidates when tracked files change (SHA256 hash tracking)
- If file tracking not working, check that file paths are correctly specified
- Review cache TTL settings (default: 3600s for most operations)

---

### 2. Low Hit Rate

**Symptoms:**
- Cache hit rate <40%
- Operations not getting faster on repeated runs
- Dashboard shows mostly misses

**Diagnosis:**
```bash
# View detailed cache statistics
python src/operations/cache_dashboard.py --detailed

# Check which operations have low hit rates
python src/caching/cache_health.py --json | python -m json.tool
```

**Root Causes:**
1. **Frequent file changes:** Cache invalidates on every change
2. **Short TTL:** Cache entries expiring too quickly
3. **Incorrect file tracking:** Wrong files being tracked for invalidation
4. **Cache warming not running:** Git hooks not triggering background warming

**Solutions:**

**For frequent file changes:**
- This is normal during active development
- Cache will be more effective in CI/CD pipelines
- Use `--no-cache` flag if cache is slowing you down

**For TTL issues:**
```python
# Increase TTL in integration code
cache.set('operation', 'key', result, files=files, ttl_seconds=7200)  # 2 hours
```

**For file tracking issues:**
```python
# Verify tracked files are correct
# Example from optimize_system_orchestrator.py:
governance_path = self.project_root / "src" / "tier0" / "governance.yaml"
result = self._check_governance_drift(context)
cache.set("optimize", "governance_drift_analysis", result, 
          files=[governance_path], ttl_seconds=3600)
```

**For cache warming:**
```bash
# Verify git hooks are installed
ls -la .git/hooks/post-checkout .git/hooks/post-merge

# Manually trigger warming
python src/caching/cache_warmer.py --wait
```

---

### 3. Cache Corruption

**Symptoms:**
- "Database is locked" errors
- Cache operations fail silently
- Health check reports corruption

**Diagnosis:**
```bash
# Run health check
python src/caching/cache_health.py

# Check database integrity
sqlite3 cortex-brain/cache/validation_cache.db "PRAGMA integrity_check;"
```

**Recovery:**
```bash
# Option 1: Clear corrupted cache
rm cortex-brain/cache/validation_cache.db
python -c "from src.caching import get_cache; get_cache()"  # Reinitialize

# Option 2: Repair database
sqlite3 cortex-brain/cache/validation_cache.db ".recover" | sqlite3 cache_recovered.db
mv cache_recovered.db cortex-brain/cache/validation_cache.db
```

**Prevention:**
- Don't manually edit cache database
- Don't interrupt operations while cache is writing
- Use proper shutdown procedures

---

### 4. Large Cache Size

**Symptoms:**
- Cache database >100MB
- Disk space warnings
- Slow cache operations

**Diagnosis:**
```bash
# Check cache size
python src/caching/cache_health.py

# View size by operation
python -c "
from src.caching import get_cache
import sqlite3
cache = get_cache()
conn = sqlite3.connect(cache.cache_db)
cursor = conn.execute('SELECT operation, COUNT(*), SUM(LENGTH(result_json))/1024/1024 as mb FROM cache_entries GROUP BY operation')
for row in cursor:
    print(f'{row[0]}: {row[1]} entries, {row[2]:.2f}MB')
conn.close()
"
```

**Solutions:**

**Clear old entries:**
```bash
# Clear entries older than 7 days
python -c "
from src.caching import get_cache
from datetime import datetime, timedelta
import sqlite3
cache = get_cache()
conn = sqlite3.connect(cache.cache_db)
cutoff = (datetime.now() - timedelta(days=7)).isoformat()
conn.execute('DELETE FROM cache_entries WHERE timestamp < ?', (cutoff,))
conn.commit()
print(f'Deleted entries older than 7 days')
conn.close()
"

# Clear specific operation
python -c "from src.caching import get_cache; get_cache().invalidate('cleanup')"
```

**Adjust TTL:**
- Reduce TTL for operations that change frequently
- Use shorter TTL during development, longer in production

---

### 5. Performance Degradation

**Symptoms:**
- Operations slower than expected even with cache
- Cache hit but still takes long time
- Dashboard shows good hit rate but poor performance

**Diagnosis:**
```bash
# Benchmark specific operation
time python run_alignment.py

# Check cache overhead
python tests/benchmarks/benchmark_cache_performance.py
```

**Root Causes:**
1. **Cache lookup overhead:** Database queries taking too long
2. **Large cached results:** Deserializing large JSON objects is slow
3. **Too many tracked files:** File hash calculation is expensive
4. **Database fragmentation:** SQLite database needs optimization

**Solutions:**

**Optimize database:**
```bash
sqlite3 cortex-brain/cache/validation_cache.db "VACUUM;"
sqlite3 cortex-brain/cache/validation_cache.db "ANALYZE;"
```

**Reduce tracked files:**
```python
# Instead of tracking entire directory
files = list((self.project_root / "src").rglob("*.py"))  # ❌ Slow

# Track only specific files
files = [self.project_root / "src" / "file.py"]  # ✅ Fast
```

**Use cache warming:**
```bash
# Pre-populate cache in background
python src/caching/cache_warmer.py &
```

---

## Debugging Techniques

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('src.caching')
logger.setLevel(logging.DEBUG)
```

### Inspect Cache Contents

```python
from src.caching import get_cache

cache = get_cache()

# List all keys for operation
keys = cache.get_all_keys('align')
print(f"Align cache keys: {keys}")

# Get statistics
stats = cache.get_stats('align')
print(f"Hit rate: {stats['hit_rate']*100:.1f}%")
print(f"Hits: {stats['hits']}, Misses: {stats['misses']}")

# Get specific entry
result = cache.get('align', 'orchestrators', [])
if result:
    print(f"Cached orchestrators: {len(result)}")
else:
    print("Cache miss")
```

### Trace File Hash Changes

```python
from src.caching import get_cache
from pathlib import Path
import hashlib

# Calculate file hash manually
file_path = Path("src/operations/align.py")
with open(file_path, 'rb') as f:
    current_hash = hashlib.sha256(f.read()).hexdigest()

print(f"Current hash: {current_hash}")

# Compare with cached hash
cache = get_cache()
import sqlite3
conn = sqlite3.connect(cache.cache_db)
cursor = conn.execute(
    "SELECT file_hashes_json FROM cache_entries WHERE operation='align' LIMIT 1"
)
row = cursor.fetchone()
if row:
    import json
    cached_hashes = json.loads(row[0])
    cached_hash = cached_hashes.get(str(file_path))
    print(f"Cached hash: {cached_hash}")
    print(f"Match: {current_hash == cached_hash}")
conn.close()
```

### Monitor Cache Performance

```python
# Run operation with timing
import time
from src.caching import get_cache

cache = get_cache()

# First run (cache miss)
start = time.time()
# ... run operation ...
miss_time = time.time() - start

# Clear stats
cache._stats = {'hits': 0, 'misses': 0, 'invalidations': 0}

# Second run (cache hit)
start = time.time()
# ... run operation again ...
hit_time = time.time() - start

print(f"Cache miss: {miss_time:.2f}s")
print(f"Cache hit: {hit_time:.2f}s")
print(f"Speedup: {miss_time/hit_time:.1f}x")
```

---

## Cache Maintenance

### Regular Maintenance Tasks

**Weekly:**
```bash
# Check cache health
python src/caching/cache_health.py

# View cache statistics
python src/operations/cache_dashboard.py
```

**Monthly:**
```bash
# Clear entries older than 30 days
python -c "
from src.caching import get_cache
from datetime import datetime, timedelta
import sqlite3
cache = get_cache()
conn = sqlite3.connect(cache.cache_db)
cutoff = (datetime.now() - timedelta(days=30)).isoformat()
deleted = conn.execute('DELETE FROM cache_entries WHERE timestamp < ?', (cutoff,)).rowcount
conn.commit()
print(f'Deleted {deleted} old entries')
conn.close()
"

# Optimize database
sqlite3 cortex-brain/cache/validation_cache.db "VACUUM; ANALYZE;"
```

**After Major Refactoring:**
```bash
# Clear all cache
python -c "from src.caching import get_cache; get_cache().invalidate()"
```

---

## Best Practices

### 1. Cache Key Naming

Use descriptive, unique keys:
```python
# ❌ Bad
cache.set('align', 'data', result, files)

# ✅ Good
cache.set('align', 'orchestrator_discovery', result, files)
cache.set('align', f'integration_score:{feature_name}', result, files)
```

### 2. File Tracking

Track only relevant files:
```python
# ❌ Bad - tracks entire project
files = list(Path('.').rglob('*.py'))

# ✅ Good - tracks only relevant files
files = [
    Path('src/operations/align.py'),
    Path('src/validation/integration_scorer.py')
]
```

### 3. TTL Selection

Choose appropriate TTL based on operation:
```python
# Fast-changing data (tests during development)
cache.set('align', 'test_results', result, files, ttl_seconds=1800)  # 30 min

# Slow-changing data (governance rules)
cache.set('optimize', 'governance_drift', result, files, ttl_seconds=7200)  # 2 hours

# Rarely-changing data (orchestrator discovery)
cache.set('align', 'orchestrators', result, files, ttl_seconds=86400)  # 24 hours
```

### 4. Error Handling

Don't cache errors:
```python
try:
    result = expensive_operation()
    cache.set('operation', 'key', result, files)
    return result
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return error_result  # Don't cache this!
```

### 5. Cache Warming

Use background warming for better UX:
```python
# In git hooks or startup
from src.caching.cache_warmer import warm_cache_after_git_operation
warm_cache_after_git_operation()  # Non-blocking
```

---

## Performance Targets

**Expected Cache Performance:**

| Operation | First Run | Cache Hit | Target Speedup |
|-----------|-----------|-----------|----------------|
| align | 60-90s | 8-15s | 6-10x |
| deploy | 100-200s | 12-22s | 8-15x |
| optimize | 30-60s | 5-10s | 5-8x |
| cleanup | 15-30s | 3-5s | 4-6x |

**Cache Hit Rate Targets:**

| Scenario | Target Hit Rate |
|----------|----------------|
| Development (frequent changes) | 30-50% |
| CI/CD (stable code) | 70-90% |
| Production deployment | 80-95% |

If performance is significantly worse than targets, review this troubleshooting guide.

---

## Emergency Procedures

### Complete Cache Reset

```bash
# 1. Stop all CORTEX operations
# 2. Backup cache (optional)
cp cortex-brain/cache/validation_cache.db cortex-brain/cache/validation_cache.backup.db

# 3. Delete cache
rm cortex-brain/cache/validation_cache.db

# 4. Reinitialize
python -c "from src.caching import get_cache; get_cache()"

# 5. Warm cache
python src/caching/cache_warmer.py --wait
```

### Disable Caching Temporarily

```python
# In operation code, skip cache
USE_CACHE = False

if USE_CACHE:
    cached = cache.get('operation', 'key', files)
    if cached:
        return cached

# Always compute
result = expensive_operation()

if USE_CACHE:
    cache.set('operation', 'key', result, files)

return result
```

---

## Getting Help

If issues persist after following this guide:

1. Check cache health: `python src/caching/cache_health.py`
2. Review logs: `tail -f logs/cortex.log`
3. Run diagnostics: `python src/operations/cache_dashboard.py --detailed`
4. Report issue with:
   - Cache health output
   - Dashboard statistics
   - Reproduction steps
   - Expected vs actual behavior

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
