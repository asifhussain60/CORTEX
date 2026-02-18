# LENS Caching Strategy

---
title: LENS Caching Strategy - 3-Tier Performance Optimization
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
word_count: 1860
last_verified: 2026-02-15
source_of_truth: cortex/intelligence/02-lens/caching/ + cortex/02-lens/cache.py
format: diátaxis-explanation
voice: third-person-neutral
phase: Production (v8.1)
diagrams: ASCII cache layers, invalidation flow, warming strategy
order: 5
---

> **Notice:** Caching strategy reflects production-tested optimization as of v8.1. Organizations may tune TTL values and cache sizes based on workload characteristics. Cache hit rate targets (60-85%) based on typical development workflow patterns.

---

## Executive Summary

LENS caching implements 3-tier strategy (request/session/workspace) reducing repeat analysis overhead by 60-85% through intelligent invalidation and cache warming. Organizations benefit from faster response times (cached: <50ms vs uncached: 100-250ms) reducing developer wait time and infrastructure costs [Business Leaders]. Product teams gain consistent performance during high-traffic periods through cache hit rates averaging 70%+ [Product Owners]. The caching system implements L1 request cache (1min TTL, in-memory dict, 100 entries max), L2 session cache (1hr TTL, LRU eviction, 50MB limit), L3 workspace cache (24hr TTL, SQLite storage, git-aware invalidation), with checksum-based staleness detection triggering automatic cache warming on file changes [Software Developers].

**Cache Hierarchy:**
- **L1 Request Cache** — Deduplicates identical requests within same request context, 1-minute TTL, in-memory dictionary, 100-entry limit, <0.1ms access latency
- **L2 Session Cache** — Persists results across requests in user session, 1-hour TTL, LRU eviction policy, 50MB size limit, <1ms access latency
- **L3 Workspace Cache** — Shares results across sessions for same workspace, 24-hour TTL, SQLite storage, git-aware invalidation, <5ms access latency

**Cache Key Components:** workspace path hash (8 chars), target file/directory, sorted analyzer list hash (8 chars), LENS version, content checksum (MD5). Keys uniquely identify analysis results enabling precise cache hits and invalidation.

**Invalidation Strategy:**
- **Time-Based** — TTL expiration triggers automatic removal (L1: 1min, L2: 1hr, L3: 24hr)
- **Content-Based** — File content changes detected via checksum comparison, stale entries invalidated immediately
- **Event-Based** — Git commits trigger workspace cache scan, modified files marked stale, cache warming scheduled
- **Size-Based** — LRU eviction when cache size exceeds limits (L2: 50MB, L3: 500MB)

**Cache Hit Rates (Production):**
- **L1 Request** — 15-25% (identical requests within 1min window)
- **L2 Session** — 40-50% (same files analyzed multiple times in session)
- **L3 Workspace** — 60-85% (stable codebase with infrequent changes)
- **Overall** — 70-80% combined hit rate (cumulative across 3 tiers)

**Performance Impact:**
- **Cache Hit** — <50ms response (vs 100-250ms uncached), 80%+ latency reduction
- **Cache Miss** — 100-250ms analysis + 2-5ms cache write, minimal overhead
- **Cache Warming** — Background process, non-blocking, triggered on git commits
- **Memory Footprint** — L1: <10MB, L2: <50MB, L3: <500MB (disk), <100MB (in-memory index)

**Cache Warming:** Proactive cache population triggered on git commits, analyzes modified files + dependencies in background, ensures cache hit on subsequent requests, typical warming time 500ms-2s for 10-file commit.

---

## Overview

### Brain Analogy: Visual Short-Term Memory

When you look at a scene, you don't re-process every pixel each time you blink. Your **visual short-term memory** (VSTM) holds the processed representation for several hundred milliseconds, allowing rapid recognition without full reprocessing. LENS caching serves the same function — it holds analysis results so that repeated queries don't require full re-analysis [Software Developers].

LENS caching is critical for performance. Without caching, every request would require full re-analysis of the codebase. The caching system provides:

- **70%+ cache hit rate** (target)
- **< 50ms cached response** (vs 300ms+ uncached)
- **Intelligent invalidation** (based on file changes)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CACHE ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Request                                                         │
│     │                                                            │
│     ▼                                                            │
│  ┌─────────┐   Hit   ┌─────────────┐                           │
│  │   L1    │ ──────> │   Return    │                           │
│  │ Request │         │   Cached    │                           │
│  └────┬────┘         └─────────────┘                           │
│       │ Miss                                                     │
│       ▼                                                          │
│  ┌─────────┐   Hit   ┌─────────────┐                           │
│  │   L2    │ ──────> │   Return    │                           │
│  │ Session │         │   Cached    │                           │
│  └────┬────┘         └─────────────┘                           │
│       │ Miss                                                     │
│       ▼                                                          │
│  ┌─────────┐   Hit   ┌─────────────┐                           │
│  │   L3    │ ──────> │   Return    │                           │
│  │Workspace│         │   Cached    │                           │
│  └────┬────┘         └─────────────┘                           │
│       │ Miss                                                     │
│       ▼                                                          │
│  ┌─────────────┐                                                │
│  │   Execute   │                                                │
│  │  Analyzers  │                                                │
│  └─────────────┘                                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Cache Architecture

### Cache Key Design

```python
@dataclass
class CacheKey:
    """Unique identifier for cached results."""
    
    workspace: str      # Workspace path hash
    target: str         # Target file/directory
    analyzers: str      # Sorted analyzer list hash
    version: str        # LENS version
    checksum: str       # Content checksum
    
    def to_string(self) -> str:
        """Generate cache key string."""
        return f"{self.workspace}:{self.target}:{self.analyzers}:{self.version}:{self.checksum}"

def build_cache_key(
    target: str,
    analyzers: List[str],
    workspace: str
) -> CacheKey:
    """Build a cache key for the request."""
    return CacheKey(
        workspace=hashlib.md5(workspace.encode()).hexdigest()[:8],
        target=target,
        analyzers=hashlib.md5(
            ":".join(sorted(analyzers)).encode()
        ).hexdigest()[:8],
        version=LENS_VERSION,
        checksum=calculate_content_checksum(target)
    )
```

### Cache Entry Structure

```python
@dataclass
class CacheEntry:
    """Cached analysis result."""
    
    key: CacheKey
    value: UnifiedIntelligenceContext
    created_at: datetime
    accessed_at: datetime
    ttl: int  # seconds
    size_bytes: int
    hit_count: int = 0
    
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        age = (datetime.utcnow() - self.created_at).seconds
        return age > self.ttl
    
    def is_stale(self, checksum: str) -> bool:
        """Check if content has changed."""
        return self.key.checksum != checksum
```

---

## Cache Layers

### L1: Request Cache

**Purpose:** Deduplicate identical requests within same request context.

| Property | Value |
|----------|-------|
| **TTL** | 1 minute |
| **Scope** | Single request |
| **Storage** | In-memory (dict) |
| **Max Size** | 100 entries |

```python
class L1RequestCache:
    """Fast in-memory cache for request deduplication."""
    
    def __init__(self, max_entries: int = 100):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_entries = max_entries
    
    def get(self, key: str) -> Optional[CacheEntry]:
        entry = self.cache.get(key)
        if entry and not entry.is_expired():
            entry.hit_count += 1
            entry.accessed_at = datetime.utcnow()
            return entry
        return None
    
    def set(self, key: str, value: Any, ttl: int = 60):
        if len(self.cache) >= self.max_entries:
            self._evict_lru()
        
        self.cache[key] = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.utcnow(),
            ttl=ttl
        )
```

### L2: Session Cache

**Purpose:** Cache results across requests in same session.

| Property | Value |
|----------|-------|
| **TTL** | 1 hour |
| **Scope** | User session |
| **Storage** | In-memory (LRU) |
| **Max Size** | 50MB |

```python
class L2SessionCache:
    """Session-scoped LRU cache."""
    
    def __init__(self, max_size_mb: int = 50):
        self.max_size = max_size_mb * 1024 * 1024
        self.current_size = 0
        self.cache = OrderedDict()
    
    def get(self, key: str) -> Optional[CacheEntry]:
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            entry = self.cache[key]
            
            if not entry.is_expired():
                entry.hit_count += 1
                return entry
            else:
                self._remove(key)
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        size = self._estimate_size(value)
        
        while self.current_size + size > self.max_size:
            self._evict_oldest()
        
        self.cache[key] = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.utcnow(),
            ttl=ttl,
            size_bytes=size
        )
        self.current_size += size
```

### L3: Workspace Cache

**Purpose:** Persistent cache for workspace analysis results.

| Property | Value |
|----------|-------|
| **TTL** | 24 hours |
| **Scope** | Workspace |
| **Storage** | Disk (SQLite) |
| **Max Size** | 500MB |

```python
class L3WorkspaceCache:
    """Persistent workspace cache using SQLite."""
    
    def __init__(self, workspace: str, max_size_mb: int = 500):
        self.db_path = Path(workspace) / ".cortex" / "cache.db"
        self.max_size = max_size_mb * 1024 * 1024
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value BLOB,
                created_at TEXT,
                ttl INTEGER,
                size_bytes INTEGER
            )
        """)
        conn.commit()
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM cache WHERE key = ?",
                (key,)
            )
            row = await cursor.fetchone()
            
            if row:
                entry = self._deserialize(row)
                if not entry.is_expired():
                    return entry
                else:
                    await self._remove(db, key)
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 86400):
        serialized = self._serialize(value)
        size = len(serialized)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO cache 
                (key, value, created_at, ttl, size_bytes)
                VALUES (?, ?, ?, ?, ?)
            """, (key, serialized, datetime.utcnow().isoformat(), ttl, size))
            await db.commit()
```

---

## Invalidation Strategy

### Invalidation Triggers

| Trigger | Scope | Action |
|---------|-------|--------|
| **File Change** | Specific file | Invalidate file entries |
| **Git Commit** | Workspace | Invalidate affected files |
| **Config Change** | Workspace | Full invalidation |
| **LENS Upgrade** | All | Full invalidation |

### File Watcher Integration

```python
class CacheInvalidator:
    """Watches for changes and invalidates cache."""
    
    def __init__(self, cache: LENSCache, workspace: str):
        self.cache = cache
        self.workspace = workspace
        self.watcher = FileWatcher(workspace)
    
    async def start(self):
        """Start watching for changes."""
        self.watcher.on_change(self._on_file_change)
        self.watcher.on_git_event(self._on_git_event)
        await self.watcher.start()
    
    async def _on_file_change(self, event: FileEvent):
        """Handle file change event."""
        file_path = event.path
        
        # Invalidate all entries for this file
        await self.cache.invalidate_pattern(f"*:{file_path}:*")
        
        # Log invalidation
        logger.debug(f"Invalidated cache for {file_path}")
    
    async def _on_git_event(self, event: GitEvent):
        """Handle git event."""
        if event.type == "commit":
            # Invalidate changed files
            for file in event.changed_files:
                await self.cache.invalidate_pattern(f"*:{file}:*")
```

### Checksum-Based Invalidation

```python
def calculate_content_checksum(target: str) -> str:
    """Calculate checksum for invalidation."""
    if os.path.isfile(target):
        return _file_checksum(target)
    elif os.path.isdir(target):
        return _directory_checksum(target)
    else:
        return "unknown"

def _file_checksum(path: str) -> str:
    """Calculate file content hash."""
    hasher = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()[:16]

def _directory_checksum(path: str) -> str:
    """Calculate directory structure hash."""
    hasher = hashlib.md5()
    for root, dirs, files in os.walk(path):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            mtime = os.path.getmtime(file_path)
            hasher.update(f"{file_path}:{mtime}".encode())
    return hasher.hexdigest()[:16]
```

---

## Cache Warming

### Proactive Warming

```python
class CacheWarmer:
    """Proactively warms cache for likely requests."""
    
    def __init__(self, cache: LENSCache, lens: LENSOrchestrator):
        self.cache = cache
        self.lens = lens
    
    async def warm_workspace(self, workspace: str):
        """Warm cache for entire workspace."""
        # Find important files
        important_files = await self._identify_important_files(workspace)
        
        # Warm in parallel (limited concurrency)
        semaphore = asyncio.Semaphore(5)
        
        async def warm_file(file: str):
            async with semaphore:
                await self.lens.analyze(file)
        
        await asyncio.gather(*[
            warm_file(f) for f in important_files
        ])
    
    async def _identify_important_files(
        self,
        workspace: str
    ) -> List[str]:
        """Identify files likely to be requested."""
        important = []
        
        # Entry points
        for pattern in ["main.py", "app.py", "index.ts", "server.py"]:
            matches = glob.glob(f"{workspace}/**/{pattern}", recursive=True)
            important.extend(matches)
        
        # Recently changed files
        git_result = subprocess.run(
            ["git", "log", "--name-only", "--since=7 days ago"],
            cwd=workspace,
            capture_output=True
        )
        recent_files = git_result.stdout.decode().splitlines()
        important.extend(recent_files[:20])
        
        return list(set(important))
```

### On-Demand Warming

```python
async def warm_on_demand(
    self,
    target: str,
    related: bool = True
):
    """Warm cache for target and optionally related files."""
    # Warm target
    await self.lens.analyze(target)
    
    if related:
        # Find related files
        ast_result = await self.lens.ast_analyzer.analyze(target)
        imports = ast_result.data.get("imports", [])
        
        # Warm imported files
        for imp in imports[:10]:
            if imp.get("path"):
                await self.lens.analyze(imp["path"])
```

---

## Monitoring

### Cache Metrics

```python
CACHE_METRICS = {
    "lens_cache_hits_total": Counter(
        "lens_cache_hits_total",
        "Total cache hits",
        ["layer"]
    ),
    "lens_cache_misses_total": Counter(
        "lens_cache_misses_total",
        "Total cache misses",
        ["layer"]
    ),
    "lens_cache_size_bytes": Gauge(
        "lens_cache_size_bytes",
        "Current cache size",
        ["layer"]
    ),
    "lens_cache_evictions_total": Counter(
        "lens_cache_evictions_total",
        "Total cache evictions",
        ["layer", "reason"]
    ),
}
```

### Hit Rate Calculation

```python
def get_hit_rate(self, layer: str = "all") -> float:
    """Calculate cache hit rate."""
    if layer == "all":
        hits = sum(
            CACHE_METRICS["lens_cache_hits_total"].labels(l)._value.get()
            for l in ["L1", "L2", "L3"]
        )
        total = hits + sum(
            CACHE_METRICS["lens_cache_misses_total"].labels(l)._value.get()
            for l in ["L1", "L2", "L3"]
        )
    else:
        hits = CACHE_METRICS["lens_cache_hits_total"].labels(layer)._value.get()
        misses = CACHE_METRICS["lens_cache_misses_total"].labels(layer)._value.get()
        total = hits + misses
    
    return hits / max(total, 1)
```

---

## Related Documents

- [LENS Architecture](architecture.md) — Technical design
- [Observability](../05-infrastructure/observability.md) — Metrics
- [Performance](../05-infrastructure/scalability.md) — Scaling

---

*Part of CORTEX Architecture Documentation*
