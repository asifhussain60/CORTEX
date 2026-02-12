# CORTEX Wave Execution Quick Start
**Version:** 1.0 | **Date:** 2026-02-12 | **Mode:** Silent Autonomous ✅

---

## 🚀 START HERE

### Current Status
- ✅ **Wave 7 COMPLETE** (Orchestrator Consolidation, 233 tests)
- ✅ **Wave 8 COMPLETE** (Planning Capability, 108 tests)
- ⚪ **Wave 1 IN PROGRESS** (Foundation Security, 20/107 tests)

### Next Action
**Start WAVE-A (Session 1)** — 2-3 hours

---

## 📋 WAVE-A: Critical Blockers Resolution

### What It Does
1. Fixes 4 test import errors (blocking 21,441 tests)
2. Implements ENH-063 Phase 2: Reliability & Performance
   - Circuit breakers for git operations
   - Async git operations
   - Debug orchestrator race condition fix
3. Adds 15 new tests (RED→GREEN→REFACTOR)

### How to Execute

#### Option 1: Single Command (Recommended)
```
/implement WAVE-A: Fix test imports + ENH-063 Phase 2 (circuit breakers, async git, race condition)

Authority: cortex-registry/_cortex-master/SESSION-SCOPED-WAVES.md
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-A-20260212-01
Token Budget: <150k

Scope:
1. Fix 4 test import errors (SharedContext)
2. Circuit breakers for git operations
3. Async git operations
4. Debug orchestrator race condition fix
5. 15+ new tests (RED→GREEN→REFACTOR)
6. Update master plan documentation

Success: All tests passing + 2 commits + docs updated
```

#### Option 2: Step-by-Step (if needed)
```
# Step 1: Fix test imports
/implement Fix 4 test import errors (SharedContext in phase_context_resolver.py)
Files: tests/unit/agents/test_master_plan_auditor_integration.py, 
       tests/unit/agents/test_meta_auditor_integration.py,
       tests/unit/infrastructure/test_prometheus_metrics.py,
       tests/unit/orchestrators/core/test_phase_resolver_collaboration.py

# Step 2: ENH-063 Phase 2
/implement ENH-063 Phase 2: Circuit breakers, async git, race condition fix
Authority: cortex-registry/_cortex-master/enhancements/ENH-063.yaml
Tests: 15+ new (RED→GREEN→REFACTOR)
```

---

## ✅ Success Criteria

After WAVE-A completes, you should see:

### Test Output
```bash
$ python3 -m pytest tests/ -v --tb=short
...
======================= 21,456 passed in 180.23s =======================
```

### Git Log
```bash
$ git log --oneline -2
abc1234 AC-WAVE-A-002: ENH-063 Phase 2 complete (Reliability) ✅ 15/15 passing
def5678 AC-WAVE-A-001: Fix test imports (SharedContext) ✅
```

### Documentation Updates
```bash
$ grep "ENH-063" cortex-registry/_cortex-master/index.yaml
  - ENH-063 phase_1: "✅ complete (20 tests)"
  - ENH-063 phase_2: "✅ complete (15 tests)"
  - ENH-063 progress: "33% (2/6 phases)"
```

---

## 📊 Full Execution Plan (Waves A-E)

| Session | Wave | Duration | Status | Deliverable |
|---------|------|----------|--------|-------------|
| **1** | **WAVE-A** | **2-3h** | **⚪ PENDING** | **Test fixes + ENH-063 Phase 2** |
| 2 | WAVE-B | 2-3h | ⚪ BLOCKED | ENH-063 Phase 3+4 (logging, RBAC) |
| 3 | WAVE-C | 2-3h | ⚪ BLOCKED | ENH-063 Phase 5+6 + integration |
| 4 | WAVE-D | 1-2h | ⚪ BLOCKED | ENH-066 docs + phase-54 |
| 5 | WAVE-E | 2-3h | ⚪ BLOCKED | phase-51 + phase-48 S1-S3 |

**Milestone:** Wave 1 Foundation Complete (ENH-063, ENH-066, phase-54, phase-51, phase-48)

---

## 🔍 Verification Commands

### Before Starting
```bash
# Pull latest
git pull origin CORTEX

# Check current tests (should show 4 errors)
python3 -m pytest tests/ --co -q
# Expected: 21,441 tests collected, 4 errors

# Verify clean state
git status
# Expected: nothing to commit, working tree clean
```

### After Completion
```bash
# Verify all tests pass
python3 -m pytest tests/ -v --tb=short
# Expected: 21,456 passed (21,441 + 15 new)

# Check commits
git log --oneline -2
# Expected: 2 commits (AC-WAVE-A-001, AC-WAVE-A-002)

# Verify documentation
cat cortex-registry/_cortex-master/index.yaml | grep -A 5 "ENH-063"
# Expected: phase_2 marked complete

# Push commits
git push origin CORTEX
```

---

## 🚨 Troubleshooting

### Issue: Test imports still failing
**Symptom:** `ImportError: cannot import name 'SharedContext'`

**Solution:**
```bash
# Check if SharedContext exists
grep -r "class SharedContext" cortex/

# If not found, it may be named differently
grep -r "SharedContext" cortex/orchestrators/core/phase_context_resolver.py

# Update test imports to match actual class name
```

### Issue: Circuit breaker tests failing
**Symptom:** `AssertionError: Circuit breaker did not open`

**Solution:**
- Verify circuit breaker logic: open after 3 consecutive failures
- Check test setup: ensure 3 failures triggered before assertion
- Review `cortex/repositories/git_operations.py` implementation

### Issue: Async tests timing out
**Symptom:** `asyncio.TimeoutError`

**Solution:**
- Increase test timeout: `@pytest.mark.timeout(30)`
- Check for deadlocks: verify all `await` statements
- Use `asyncio.run()` in tests, not `asyncio.get_event_loop()`

---

## 📚 Reference Documents

| Document | Purpose | Path |
|----------|---------|------|
| **Session-Scoped Waves** | Complete wave specifications | `cortex-registry/_cortex-master/SESSION-SCOPED-WAVES.md` |
| **Implementation Reality Sync** | Truth table (docs vs code) | `cortex-registry/_cortex-master/IMPLEMENTATION-REALITY-SYNC-2026-02-12.md` |
| **Master Index** | High-level wave status | `cortex-registry/_cortex-master/index.yaml` |
| **ENH-063 Spec** | Production remediation details | `cortex-registry/_cortex-master/enhancements/ENH-063.yaml` |

---

## 🎯 After WAVE-A: Next Steps

1. **Verify completion:**
   - All tests passing (21,456)
   - 2 commits pushed
   - Documentation updated

2. **Proceed to WAVE-B:**
   ```
   /implement WAVE-B: ENH-063 Phase 3+4 (structured logging, tracing, RBAC)
   
   Authority: cortex-registry/_cortex-master/SESSION-SCOPED-WAVES.md
   Mode: Silent autonomous
   Session: WAVE-B-20260212-02
   Depends: WAVE-A complete
   ```

3. **Track progress:**
   - Update session log (manual or automated)
   - Monitor test count growth
   - Verify wave dependencies satisfied

---

## 💡 Pro Tips

### 1. Silent Mode Benefits
- ✅ No interruptions (autonomous execution)
- ✅ ASCII progress bars (visual feedback)
- ✅ Report at end (summary with commits)
- ❌ No confirmations (just execute)

### 2. Session Duration
- Typical: 2-3 hours actual work
- Includes: Analysis + TDD + Testing + Documentation
- Token budget: <200k (fits in single Copilot session)

### 3. TDD Workflow
```
1. RED phase: Write failing tests (5-10 min)
2. GREEN phase: Implement minimal code to pass (20-40 min)
3. REFACTOR phase: Clean up, optimize, document (10-20 min)
4. Commit: AC-* marker + test count
5. Repeat for next task
```

### 4. Commit Quality
- ✅ AC-* markers (audit trail)
- ✅ Test counts (verification)
- ✅ Clear descriptions
- ✅ Files listed
- ❌ No "WIP" commits
- ❌ No uncommitted changes

---

**Status:** ✅ READY TO START WAVE-A  
**Next Command:** Copy WAVE-A `/implement` block above  
**Expected Duration:** 2-3 hours  
**Expected Result:** 21,456 tests passing + 2 commits + ENH-063 33% complete

---

*Generated: 2026-02-12 | Quick Start Guide v1.0*
