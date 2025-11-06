# Decision: Build Custom sql.js with FTS5 Support

**Date:** 2025-11-06  
**Status:** ✅ Accepted  
**Deciders:** Project team (based on Phase -1 benchmarking)  
**Tags:** #architecture #performance #fts5 #sql.js #phase-minus-1

---

## Context

During Phase -1.1 (Architecture Validation), we benchmarked the standard sql.js package from npm to validate CORTEX performance assumptions for browser-based SQLite access.

**Critical Finding:**
The standard sql.js package **does not include FTS5 (Full-Text Search 5)** extension support. FTS5 is a SQLite extension that must be compiled in at build time.

**Error encountered:**
```
Error: no such module: fts5
```

**Impact:**
- ❌ Cannot use `CREATE VIRTUAL TABLE ... USING fts5()`
- ❌ Tier 2 (Long-Term Knowledge) pattern search blocked
- ❌ Core CORTEX feature unavailable with standard sql.js

**Benchmark Results:**
- ✅ Tier 1 performance: 0.28ms (177x faster than 50ms target)
- ✅ Concurrency: No blocking with WAL mode
- ❌ FTS5: Not available in standard build
- ❌ Database size: 900KB vs 270KB target (fixable with FIFO limits)

---

## Decision

**Build a custom sql.js with FTS5 enabled.**

We will:
1. Set up Emscripten toolchain
2. Clone sql.js repository
3. Modify Makefile to enable FTS5: `-DSQLITE_ENABLE_FTS5`
4. Build custom WASM binary
5. Deploy custom build to dashboard
6. Document build process for team

**Timeline:** +4-6 hours to Phase -1 (acceptable investment)

---

## Alternatives Considered

### Option 1: Build Custom sql.js with FTS5 ⭐ CHOSEN

**Pros:**
- ✅ Full FTS5 performance as designed (<100ms pattern search)
- ✅ Maintains browser-only architecture
- ✅ One-time build, reusable across team
- ✅ Future-proof (control over SQLite features)
- ✅ No runtime performance penalty

**Cons:**
- ⚠️ Requires Emscripten toolchain setup
- ⚠️ Build complexity for future maintenance
- ⚠️ Team needs build instructions
- ⚠️ +4-6 hours to Phase -1

**Why chosen:**
- One-time investment prevents 20-40 hours of future rework
- Maintains elegant browser-only design
- Delivers full performance targets
- Best long-term solution

---

### Option 2: Fallback to LIKE Queries

**Pros:**
- ✅ Works with standard sql.js (no build required)
- ✅ Simple implementation
- ✅ No build complexity
- ✅ Quick to implement (+2-3 hours)

**Cons:**
- ❌ 10-50x slower than FTS5
- ❌ Full table scans (no indexes)
- ❌ May not meet <100ms target
- ❌ Degrades as pattern count grows
- ❌ Poor user experience

**Query change:**
```sql
-- Instead of FTS5:
SELECT * FROM patterns_fts WHERE patterns_fts MATCH 'authentication'

-- LIKE fallback:
SELECT * FROM patterns 
WHERE pattern LIKE '%authentication%' 
   OR context LIKE '%authentication%'
```

**Why not chosen:**
- Unacceptable performance degradation
- Fails to meet core design targets
- Creates technical debt
- Poor long-term scalability

---

### Option 3: Server-Side SQLite API

**Pros:**
- ✅ Full SQLite features (FTS5, all extensions)
- ✅ Better performance than sql.js
- ✅ Easier testing (Python)
- ✅ Centralized data access

**Cons:**
- ❌ Requires server deployment (+8-12 hours)
- ❌ Network latency overhead
- ❌ More complex architecture
- ❌ Loses "browser-only" advantage
- ❌ Deployment complexity

**Architecture change:**
```
Dashboard (React) → HTTP API (FastAPI) → SQLite (Python, native)
```

**Why not chosen:**
- Violates core design principle (browser-only)
- Adds deployment complexity
- Network latency overhead
- Overkill for current requirements

---

## Consequences

### Positive Consequences

✅ **Performance targets met**
- Tier 2 pattern search will meet <100ms target
- FTS5 scales efficiently to large pattern sets
- No performance degradation vs original design

✅ **Architecture preserved**
- Maintains browser-only design
- No server dependency
- Simple deployment (static files)

✅ **Future-proof**
- Control over SQLite extensions
- Can enable other features as needed
- No vendor lock-in to npm package

✅ **One-time cost**
- 4-6 hours now prevents 20-40 hours of rework
- Build process documented for team
- Custom WASM versioned in git

### Negative Consequences

⚠️ **Build complexity**
- Team needs Emscripten toolchain
- Build process must be documented
- Maintenance burden on sql.js updates

⚠️ **Initial effort**
- +4-6 hours to Phase -1
- Learning curve for Emscripten
- Testing custom build required

### Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Build fails** | High | Low | Fallback to LIKE queries immediately |
| **WASM too large** | Medium | Low | Strip unused SQLite features, compress |
| **Browser incompatible** | High | Very Low | Test on Chrome/Firefox/Safari/Edge |
| **Maintenance burden** | Medium | Medium | Document build, automate with CI/CD |

---

## Implementation

### Phase -1.1: Custom sql.js Build (4-6 hours)

#### Step 1: Install Emscripten SDK (1 hour)
```bash
# Download Emscripten
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk

# Install latest
./emsdk install latest
./emsdk activate latest

# Set environment
source ./emsdk_env.sh
```

#### Step 2: Clone sql.js and Enable FTS5 (30 min)
```bash
# Clone sql.js
git clone https://github.com/sql-js/sql.js.git
cd sql.js

# Edit Makefile to enable FTS5
# Add to CFLAGS: -DSQLITE_ENABLE_FTS5
sed -i 's/CFLAGS=/CFLAGS=-DSQLITE_ENABLE_FTS5 /' Makefile
```

#### Step 3: Build Custom WASM (30 min)
```bash
# Build
npm install
npm run rebuild

# Output: dist/sql-wasm.wasm, dist/sql-wasm.js
```

#### Step 4: Test Custom Build (1 hour)
```bash
# Copy to CORTEX project
cp dist/sql-wasm.* ../CORTEX/dashboard/public/

# Update benchmark to use custom build
# Re-run: npm run benchmark

# Verify FTS5 works
```

#### Step 5: Update Dashboard (1 hour)
```typescript
// dashboard/src/lib/db.ts
import initSqlJs from 'sql.js';

// Load custom WASM
const SQL = await initSqlJs({
  locateFile: (file: string) => `/sql-wasm.wasm`
});
```

#### Step 6: Document Build Process (1 hour)
```markdown
# docs/guides/BUILD-SQL-JS.md
- Prerequisites
- Build steps
- Testing
- Deployment
- Troubleshooting
```

### Timeline Impact

**Original Phase -1:** 6-8 hours
- Benchmark sql.js: 2 hours ✅
- Browser API testing: 2 hours
- Lock contention: 1 hour
- Dashboard prototype: 2 hours
- Validation report: 1 hour

**Revised Phase -1:** 10-14 hours (+4-6 hours)
- Benchmark sql.js: 2 hours ✅
- **Build custom sql.js:** 4-6 hours 🆕
- Browser API testing: 2 hours
- Lock contention: 1 hour
- Dashboard prototype: 2 hours
- Validation report: 1 hour

**Total project impact:** 74-93 hrs → 78-99 hrs (+4-6 hrs)

---

## References

### Related Documents
- Phase -1 Findings: `PHASE-MINUS-1-FINDINGS.md`
- FTS5 Decision Summary: `FTS5-DECISION-SUMMARY.md`
- Implementation Plan v2.0: `IMPLEMENTATION-PLAN-V2.md`

### Benchmark Results
- Test database: `tests/performance/test-cortex-brain.db`
- Benchmark script: `tests/performance/benchmark-sql-js.spec.ts`
- Results: See `PHASE-MINUS-1-FINDINGS.md`

### External Resources
- sql.js repository: https://github.com/sql-js/sql.js
- Emscripten SDK: https://emscripten.org/
- SQLite FTS5 docs: https://www.sqlite.org/fts5.html

---

## Evolution

### 2025-11-06: Initial Decision
- Discovered FTS5 missing during Phase -1.1 benchmarking
- Evaluated 3 options (custom build, LIKE queries, server API)
- Chose custom sql.js build for best balance of performance and simplicity
- Accepted +4-6 hour timeline impact as acceptable investment

### Future Reviews
- After Phase 1 completion: Validate FTS5 performance meets targets
- After Phase 6 migration: Confirm no performance regressions
- Quarterly: Review sql.js updates, rebuild if needed

---

**Status:** ✅ Accepted and In Progress  
**Next:** Complete Emscripten setup → Build custom WASM → Test FTS5 → Resume Phase -1.2

