# Phase -1 FTS5 Decision - Executive Summary

**Date:** 2025-11-06  
**Phase:** -1.1 (Architecture Validation)  
**Status:** 🔴 BLOCKED - Decision Required  
**Impact:** Critical path blocker

---

## The Problem

During sql.js benchmarking, we discovered that the **standard sql.js package from npm does NOT include FTS5 support**. FTS5 (Full-Text Search 5) is a SQLite extension that must be compiled in at build time.

**Error encountered:**
```
Error: no such module: fts5
```

This means:
- ❌ Cannot use `CREATE VIRTUAL TABLE ... USING fts5()`
- ❌ Tier 2 (Long-Term Knowledge) pattern search blocked
- ❌ Core CORTEX feature unavailable

---

## What Worked Well

✅ **Tier 1 performance:** 0.28ms (177x faster than 50ms target)  
✅ **Concurrency:** No blocking with WAL mode  
✅ **Architecture:** sql.js fundamentals work great

---

## Three Options

### Option 1: Build Custom sql.js with FTS5 ⭐ RECOMMENDED

**What:** Compile our own sql.js with FTS5 enabled

**Effort:** 4-6 hours (one-time)

**Pros:**
- ✅ Full FTS5 performance as designed
- ✅ Maintains browser-only architecture
- ✅ One-time build, reusable across team
- ✅ Future-proof (control over features)

**Cons:**
- ⚠️ Requires Emscripten toolchain setup
- ⚠️ Build complexity for future maintenance
- ⚠️ Team needs build instructions

**Steps:**
1. Install Emscripten SDK (1 hour)
2. Clone sql.js repo (15 min)
3. Modify Makefile: add `-DSQLITE_ENABLE_FTS5` (15 min)
4. Build: `make` (30 min)
5. Test custom WASM (1 hour)
6. Update dashboard to use custom build (1 hour)
7. Document build process (1 hour)

**Timeline Impact:** +4-6 hours to Phase -1

---

### Option 2: Fallback to LIKE Queries

**What:** Use `LIKE '%pattern%'` instead of FTS5

**Effort:** 2-3 hours

**Pros:**
- ✅ Works with standard sql.js
- ✅ Simple implementation
- ✅ No build complexity
- ✅ Quick to implement

**Cons:**
- ❌ 10-50x slower than FTS5
- ❌ Full table scans (no indexes)
- ❌ May not meet <100ms target
- ❌ Degrades as pattern count grows
- ❌ Poor user experience

**Query change:**
```sql
-- Instead of:
SELECT * FROM patterns_fts WHERE patterns_fts MATCH 'authentication'

-- Use:
SELECT * FROM patterns WHERE pattern LIKE '%authentication%' OR context LIKE '%authentication%'
```

**Timeline Impact:** +2-3 hours to Phase -1

---

### Option 3: Server-Side SQLite API

**What:** Python FastAPI serving SQLite queries

**Effort:** 8-12 hours

**Pros:**
- ✅ Full SQLite features (FTS5, all extensions)
- ✅ Better performance than sql.js
- ✅ Easier testing (Python)
- ✅ Centralized data access

**Cons:**
- ❌ Requires server deployment
- ❌ Network latency overhead
- ❌ More complex architecture
- ❌ Loses "browser-only" advantage
- ❌ Deployment complexity

**Architecture change:**
```
Dashboard (React) → HTTP API (FastAPI) → SQLite (Python, native)
```

**Timeline Impact:** +8-12 hours to Phase -1, +4-6 hours to deployment

---

## Comparison Matrix

| Criteria | Custom Build | LIKE Queries | Server API |
|----------|-------------|--------------|------------|
| **Effort** | 4-6 hrs | 2-3 hrs | 8-12 hrs |
| **Complexity** | Medium | Low | High |
| **FTS5 Support** | ✅ Yes | ❌ No | ✅ Yes |
| **Performance** | ⚡ Excellent | ⚠️ Slow | ⚡ Excellent |
| **Deployment** | ✅ Simple | ✅ Simple | ❌ Complex |
| **Maintenance** | ⚠️ Build process | ✅ Easy | ⚠️ Server ops |
| **Architecture** | ✅ Browser-only | ✅ Browser-only | ❌ Client-server |
| **Future-proof** | ✅ Yes | ❌ No | ✅ Yes |

---

## Recommendation

### ⭐ Option 1: Build Custom sql.js with FTS5

**Why:**
1. **Performance:** Maintains <100ms Tier 2 target
2. **Architecture:** Preserves browser-only design
3. **One-time cost:** 4-6 hours now prevents 20-40 hours of rework
4. **Scalable:** FTS5 handles large pattern sets efficiently
5. **User experience:** Fast pattern search as designed

**Risk mitigation:**
- If custom build fails, fallback to Option 2 (LIKE queries) immediately
- Document build process thoroughly for team
- Version control custom WASM binary in repo

**Timeline:**
- Phase -1: 6-8 hrs → 10-14 hrs (+4-6 hrs)
- Total project: 74-93 hrs → 78-99 hrs (+4-6 hrs)
- **ROI:** Prevents 20-40 hrs of future rework (2.5-5x return)

---

## Database Size Issue (Separate)

**Finding:** 900KB vs 270KB target (3.3x over)

**Root cause:** Test data used 1000 conversations (should be 50 FIFO max)

**Solution:**
1. Enforce Tier 1 FIFO limit (50 conversations)
2. Separate databases per tier
3. Re-validate size with correct configuration

**Impact:** No additional effort, just correct configuration

---

## Decision Needed

**Please approve one of:**

- [ ] **Option 1: Build custom sql.js** (RECOMMENDED)
  - I'll proceed with Emscripten setup
  - Build sql.js with FTS5 enabled
  - Test and validate
  - Continue Phase -1.2

- [ ] **Option 2: LIKE query fallback**
  - Accept slower pattern search
  - Update schema (remove FTS5)
  - Continue Phase -1.2 immediately

- [ ] **Option 3: Server-side API**
  - Redesign dashboard architecture
  - Implement FastAPI endpoints
  - Update all phase plans

---

## What This Proves

**Phase -1 is working EXACTLY as designed!**

✅ We caught a critical blocker BEFORE writing 6 phases of code  
✅ We have data-driven evidence (benchmarks)  
✅ We have clear contingency options  
✅ We can make an informed decision now

This is the **value of architecture validation** - catch issues early when they're cheap to fix.

---

**Status:** 🔴 AWAITING DECISION  
**Next:** Implement chosen option → Resume Phase -1.2 (Browser APIs)

