# ValidationCache Performance Benchmark Results

**Test Date:** 2025-11-26 09:40:09  
**Environment:** Python 3.13.7

---

## Summary

| Metric | Baseline (No Cache) | First Run (Cache Miss) | Second Run (Cache Hit) | Speedup |
|--------|---------------------|------------------------|------------------------|---------|
| **Align Time** | 2.10s | 2.24s | 0.05s | **44.8x** |
| **Deploy Time** | 0.50s | 0.54s | 0.54s | **0.9x** |
| **Total Time** | 2.61s | 2.78s | 0.59s | **4.4x** |

---

## Detailed Results

### 1. Baseline (No Cache)
- Align: 2.10s
- Deploy: 0.50s
- Total: 2.61s

### 2. First Run (Cache Miss)
- Align: 2.24s
- Deploy: 0.54s
- Total: 2.78s
- **Cache miss overhead:** 6.4%

### 3. Second Run (Cache Hit)
- Align: 0.05s
- Deploy: 0.54s
- Total: 0.59s

### 4. File Change Invalidation
- Cache hit time: 6.99ms
- Cache miss time: 0.52s
- Invalidation detected: ✅ True

---

## Analysis

### Speedup Achievement
- **Align speedup:** 44.8x (projected: 15x)
- **Deploy speedup:** 0.9x (projected: 10x)
- **Overall speedup:** 4.4x

### Cache Overhead
- First run overhead: 6.4% (projected: <5%)
- Cache hit latency: 47.0ms

### File Tracking
- Invalidation on file change: ✅ Working
- Cache hit performance: 6.99ms

---

## Conclusion

⚠️ **Cache performance below projections**

The ValidationCache provides significant performance improvements for align→deploy workflows:
1. Align operations are **44.8x faster** with warm cache
2. Deploy operations are **0.9x faster** using shared cache
3. Cache overhead on miss is **6.4%** (acceptable)
4. File tracking correctly invalidates stale cache entries

**Recommendation:** Optimize cache implementation further

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
