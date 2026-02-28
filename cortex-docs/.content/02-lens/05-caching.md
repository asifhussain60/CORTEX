# LENS Caching

---
title: LENS Caching — Performance Optimization
type: reference
audience: [Software Developers]
last_verified: 2026-02-28
source_of_truth: cortex/lens/cache/ + cortex/lens/cached_lens_orchestrator.py
order: 5
---

## Cache Architecture

LENS caches analyzer results to avoid redundant computation. The cache layer (`cortex/lens/cache/` and `cortex/lens/cache.py`) stores results keyed by file hash + analyzer version.

### Cache Strategy

```
[Request for file analysis]
        │
        ▼
[Compute file hash (content-based)]
        │
        ▼
[Cache lookup: hash + analyzer version]
        │
        ├── HIT → return cached result (0ms)
        └── MISS → run analyzer → store result → return
```

### Invalidation

- **Content change:** File hash changes → cache miss → re-analyze
- **Analyzer update:** Analyzer version increments → cache miss for affected analyzer
- **Manual clear:** Developer can force re-analysis

### Implementation

| Component | Purpose |
|-----------|---------|
| `cortex/lens/cache/` | Cache storage backend |
| `cortex/lens/cache.py` | Cache utilities and helpers |
| `cortex/lens/cached_lens_orchestrator.py` | Cache-aware pipeline that checks cache before launching analyzers |

---

*Verified against cache implementation*
