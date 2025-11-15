# Windows File Locking - Root Cause Analysis & Solution Plan

**Date:** 2025-11-11  
**Issue:** PermissionError [WinError 32] during parallel test execution  
**Impact:** ~16 tests failing intermittently on Windows  
**Priority:** HIGH (blocks Phase 1 completion)

---

## 🔍 Root Cause Analysis

### The Problem

**Windows file locking occurs because:**

1. **Each test creates its own temp database fixture**
   - 8+ test files use `NamedTemporaryFile(suffix='.db', delete=False)`
   - Each creates a separate fixture instead of using `conftest.py`
   - Results in duplicate fixture logic across codebase

2. **SQLite connections aren't properly closed before file deletion**
   - Fixtures call `db_path.unlink()` in cleanup
   - But SQLite connection may still be open inside test
   - Windows locks files while any process has them open

3. **Parallel execution (pytest-xdist) amplifies the issue**
   - 8 worker processes run simultaneously
   - Each worker creates/deletes temp files
   - Race conditions between workers accessing same DB

4. **`delete=False` + manual `unlink()` pattern is fragile**
   - Requires explicit cleanup in finally blocks
   - If test crashes, file never gets cleaned up
   - Windows doesn't allow unlinking open files

### Evidence

**Files with duplicate fixtures:**
```
tests/tier1/fifo/test_queue_manager.py         ❌ Duplicate temp_db fixture
tests/tier1/entities/test_entity_extractor.py   ❌ Duplicate temp_db fixture  
tests/tier1/messages/test_message_store.py      ❌ Duplicate temp_db fixture
tests/tier1/conversations/test_conversation_manager.py ❌ Duplicate temp_db fixture
tests/tier2/knowledge_graph/test_pattern_store.py ❌ Duplicate fixture
```

**All 5 files use the SAME pattern:**
```python
@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    if db_path.exists():
        db_path.unlink()  # ❌ Fails if DB still open
```

### Why Our Current Fix Isn't Complete

**What we did:**
- ✅ Added `in_memory_db()` fixture to conftest.py
- ✅ Added parallel detection to `temp_db()` 
- ✅ Fixed EntityExtractor schema

**What we missed:**
- ❌ Individual test files still use LOCAL fixtures (not conftest.py)
- ❌ SQLite connections created inside tests aren't tracked
- ❌ No connection cleanup enforcement
- ❌ File-based tests still run in parallel

---

## 🎯 Comprehensive Solution Plan

### Strategy: 3-Tier Approach

#### Tier 1: Immediate Fix (30 min) - **USE IN-MEMORY DATABASES**
**Goal:** Eliminate file locking by avoiding files entirely

```yaml
approach: Replace file-based fixtures with in-memory databases
rationale: 
  - SQLite ":memory:" DBs can't have locking issues
  - No cleanup needed (auto-deleted on connection close)
  - Works in parallel without conflicts
  - Faster test execution (no disk I/O)

actions:
  1_delete_duplicate_fixtures:
    files:
      - tests/tier1/fifo/test_queue_manager.py
      - tests/tier1/entities/test_entity_extractor.py
      - tests/tier1/messages/test_message_store.py
      - tests/tier1/conversations/test_conversation_manager.py
    action: Remove local temp_db fixtures
    time: 5 minutes
  
  2_update_fixtures_to_use_conftest:
    action: Change fixtures to use conftest.py fixtures
    pattern: |
      # OLD (in each file)
      @pytest.fixture
      def temp_db():
          with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
              db_path = Path(f.name)
          yield db_path
          db_path.unlink()
      
      # NEW (use conftest.py)
      # No fixture needed - use conftest.in_memory_db or conftest.temp_db
    time: 10 minutes
  
  3_update_test_classes:
    action: Change fixtures parameter from temp_db to in_memory_db
    pattern: |
      # OLD
      def queue_manager(temp_db):
          return QueueManager(temp_db)
      
      # NEW
      def queue_manager(in_memory_db):
          db_path = ":memory:"  # For modules expecting path
          mgr = QueueManager(db_path)
          mgr.db_path = in_memory_db  # Override with connection
          return mgr
    time: 15 minutes

impact: Fixes 90% of locking issues immediately
```

#### Tier 2: Connection Tracking (1 hour) - **ENFORCE CLEANUP**
**Goal:** Ensure all connections are properly closed

```yaml
approach: Create connection registry in conftest.py
rationale:
  - Track every SQLite connection opened in tests
  - Auto-close connections at test teardown
  - Catch leaked connections early

implementation:
  file: tests/conftest.py
  code: |
    @pytest.fixture(autouse=True)
    def track_db_connections(request):
        '''Track and cleanup all SQLite connections in test.'''
        connections = []
        
        # Monkey-patch sqlite3.connect to track connections
        original_connect = sqlite3.connect
        
        def tracked_connect(*args, **kwargs):
            conn = original_connect(*args, **kwargs)
            connections.append(conn)
            return conn
        
        sqlite3.connect = tracked_connect
        
        try:
            yield
        finally:
            # Restore original connect
            sqlite3.connect = original_connect
            
            # Close all tracked connections
            for conn in connections:
                try:
                    conn.close()
                except Exception:
                    pass
  
  benefits:
    - Zero-configuration cleanup
    - Works with any test
    - Catches connection leaks
    - Prevents file locking at source

time: 1 hour (includes testing)
```

#### Tier 3: Parallel Safety (30 min) - **ISOLATE WORKERS**
**Goal:** Ensure workers can't interfere with each other

```yaml
approach: Use worker-specific database paths
rationale:
  - Each pytest-xdist worker gets unique temp directory
  - No cross-worker file access
  - Safe for tests that MUST use files (e.g., schema migration tests)

implementation:
  file: tests/conftest.py
  code: |
    @pytest.fixture
    def isolated_temp_db(tmp_path, worker_id):
        '''Create worker-isolated temp database.'''
        if worker_id == "master":
            # Serial execution
            db_path = tmp_path / "test.db"
        else:
            # Parallel execution - worker-specific path
            db_path = tmp_path / f"test_{worker_id}.db"
        
        yield db_path
        
        # Cleanup with retry (Windows-safe)
        for attempt in range(3):
            try:
                if db_path.exists():
                    db_path.unlink()
                break
            except PermissionError:
                time.sleep(0.1 * (attempt + 1))

benefits:
  - Works for file-based tests
  - No worker conflicts
  - Graceful retry on Windows
  - Fallback for in-memory migration

time: 30 minutes
```

---

## 📋 Implementation Checklist

### Phase 1A: Delete Duplicate Fixtures (5 min)
- [ ] Remove `temp_db` fixture from `tests/tier1/fifo/test_queue_manager.py`
- [ ] Remove `temp_db` fixture from `tests/tier1/entities/test_entity_extractor.py`
- [ ] Remove `temp_db` fixture from `tests/tier1/messages/test_message_store.py`
- [ ] Remove `temp_db` fixture from `tests/tier1/conversations/test_conversation_manager.py`
- [ ] Remove duplicate fixture from `tests/tier2/knowledge_graph/test_pattern_store.py`

### Phase 1B: Update Test Files (15 min)
- [ ] Update `test_queue_manager.py` to use `conftest.in_memory_db`
- [ ] Update `test_entity_extractor.py` to use `conftest.in_memory_db`
- [ ] Update `test_message_store.py` to use `conftest.in_memory_db`
- [ ] Update `test_conversation_manager.py` to use `conftest.in_memory_db`
- [ ] Update module constructors to accept `:memory:` or connection object

### Phase 1C: Verify Fix (10 min)
- [ ] Run: `pytest tests/tier1/ -n auto --tb=no -q`
- [ ] Confirm: No WinError 32 failures
- [ ] Confirm: Pass rate increases to 90%+

### Phase 2: Connection Tracking (1 hour)
- [ ] Implement `track_db_connections` autouse fixture
- [ ] Test with: `pytest tests/tier1/fifo/ -v`
- [ ] Verify connection cleanup logging
- [ ] Run full suite: `pytest -n auto`

### Phase 3: Worker Isolation (30 min)  
- [ ] Implement `isolated_temp_db` fixture
- [ ] Update tests that REQUIRE file-based DBs
- [ ] Test parallel execution: `pytest -n auto`
- [ ] Verify no cross-worker interference

---

## 🎯 Expected Outcomes

### After Phase 1 (Immediate Fix):
- ✅ **90% of locking issues eliminated**
- ✅ **Tests run 30-50% faster** (in-memory > file I/O)
- ✅ **No more WinError 32 on most tests**
- ✅ **Cleaner test code** (no duplicate fixtures)

### After Phase 2 (Connection Tracking):
- ✅ **100% of connections properly closed**
- ✅ **Connection leaks caught immediately**
- ✅ **Zero manual cleanup needed**
- ✅ **Works with any new tests automatically**

### After Phase 3 (Worker Isolation):
- ✅ **Safe parallel execution on Windows**
- ✅ **No race conditions between workers**
- ✅ **Supports file-based tests when needed**
- ✅ **Graceful degradation on locking errors**

---

## 📊 Success Metrics

| Metric | Before | Target | After Phase 1 | After Phase 2+3 |
|--------|--------|--------|---------------|-----------------|
| WinError 32 Failures | 16 | 0 | ~2 | 0 |
| Pass Rate | 86% | 95% | 92% | 98% |
| Tier1 Test Time | 8s | <5s | 4s | 4s |
| Duplicate Fixtures | 5 | 0 | 0 | 0 |
| Connection Leaks | Unknown | 0 | Unknown | 0 |

---

## 🚀 Why This Plan Is Better

### Previous Approach (Partial Fix):
- ✅ Added fixtures to conftest.py
- ❌ Didn't remove duplicate fixtures
- ❌ Didn't enforce usage
- ❌ Didn't track connections
- **Result:** Issue persists because tests still use local fixtures

### New Approach (Comprehensive):
1. **Eliminates root cause** (file-based DBs)
2. **Removes code duplication** (centralized fixtures)
3. **Enforces best practices** (autouse fixture)
4. **Prevents future issues** (connection tracking)
5. **Works on all platforms** (Windows-safe)

---

## 🔧 Technical Deep Dive

### Why In-Memory Databases Work Better

**File-Based DB Problems:**
```python
# ❌ PROBLEM: File exists on disk
db = sqlite3.connect("temp.db")
# Windows locks "temp.db" - no other process can delete it
db.close()
# Even after close, brief window where file is locked
os.unlink("temp.db")  # ❌ May fail: WinError 32
```

**In-Memory DB Solution:**
```python
# ✅ SOLUTION: No file, no locking
db = sqlite3.connect(":memory:")
# DB exists only in RAM
db.close()
# DB vanishes - nothing to clean up
```

### Why Connection Tracking Matters

**Without Tracking:**
```python
def test_something():
    conn1 = sqlite3.connect("test.db")
    # ... test code ...
    # ❌ Forgot to close conn1
    # File still locked when fixture tries to cleanup
```

**With Tracking:**
```python
@pytest.fixture(autouse=True)
def track_connections():
    connections = []
    # Intercept all sqlite3.connect() calls
    # ...
    yield
    # Auto-close ALL connections
    for conn in connections:
        conn.close()
    # ✅ Guaranteed cleanup
```

---

## 📝 Implementation Notes

### Backward Compatibility
- ✅ Old tests work with new fixtures (drop-in replacement)
- ✅ Modules accepting `Path` can accept `:memory:` string
- ✅ Connection tracking is transparent (autouse fixture)

### Migration Path
1. **Week 1:** Phase 1 (immediate fix, low risk)
2. **Week 2:** Phase 2 (connection tracking, medium risk)
3. **Week 3:** Phase 3 (worker isolation, low risk)

### Rollback Plan
- All changes are in test files only (not production code)
- Git revert restores original fixtures
- No schema changes needed
- Can implement incrementally per test file

---

## 🎯 Next Steps

### Option A: Quick Fix Now (30 min)
**Implement Phase 1 only** - Gets us to 90%+ pass rate immediately

### Option B: Complete Fix (2 hours)
**Implement all 3 phases** - Production-grade solution, prevents future issues

### Option C: Incremental (1 week)
**Phase 1 now, Phase 2+3 next session** - Balanced approach

**Recommendation:** **Option A (Quick Fix)** to unblock Phase 1, then Option B next session

---

*This analysis provides both immediate tactical fixes and strategic long-term solutions for Windows file locking in the test suite.*
