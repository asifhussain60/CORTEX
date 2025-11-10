# Performance CI/CD Integration

**Phase:** 6.1 - Performance Optimization  
**Task:** CI/CD Gates  
**Status:** ✅ COMPLETE

---

## 🎯 Overview

Performance tests are automatically run on every push and pull request to prevent performance regressions. Tests fail if any operation exceeds the established baseline thresholds.

---

## 🚀 GitHub Actions Workflow

**File:** `.github/workflows/performance.yml`

### Triggers

1. **Push to branches:** `main`, `CORTEX-2.0`, `develop`
2. **Pull requests** to these branches
3. **Daily schedule:** 2 AM UTC (catches gradual performance drift)
4. **Manual trigger:** `workflow_dispatch` for on-demand testing

### Jobs

#### 1. Performance Tests (`performance`)

**Duration:** ~6-8 seconds  
**Strategy:** Fast tests → Slow tests → Profiler

**Steps:**
- ✅ Checkout repository (full history for git metrics)
- ✅ Set up Python 3.11
- ✅ Cache pip dependencies
- ✅ Install dependencies (pytest, pytest-benchmark, pyyaml)
- ✅ Initialize CORTEX brain databases (Tier 1, 2, 3)
- ✅ Run fast performance tests (18 tests, ~2s)
- ✅ Run slow performance tests (6 tests, ~8s)
- ✅ Run full profiler (optional, logs only)
- ✅ Upload performance reports as artifacts
- ✅ Check for regressions (fail build if thresholds exceeded)
- ✅ Comment on PR with results

**Thresholds Enforced:**
- Tier 1: ≤50ms (baseline: 0.48ms)
- Tier 2: ≤150ms (baseline: 0.72ms)
- Tier 3: ≤500ms (baseline: 52.51ms)
- Operations: <5000ms (baseline: 1431ms)
- Help: <1000ms (baseline: 462ms)
- Environment Setup: <5000ms (baseline: 3758ms)

#### 2. Benchmark Comparison (`benchmark-comparison`)

**Runs on:** Pull requests only  
**Purpose:** Compare PR performance vs base branch

**Steps:**
- ✅ Run profiler on PR branch
- ✅ Checkout base branch
- ✅ Run profiler on base branch
- ✅ Upload comparison artifacts
- ✅ Add comparison summary to PR

---

## 📊 Test Execution

### Local Testing (Before Push)

```bash
# Run all performance tests
pytest tests/performance/ -v

# Run fast tests only (exclude slow operations)
pytest tests/performance/ -v -m "performance and not slow"

# Run specific tier tests
pytest tests/performance/ -v -k "tier1"
pytest tests/performance/ -v -k "tier2"
pytest tests/performance/ -v -k "tier3"

# Run with detailed timing info
pytest tests/performance/ -v --durations=10
```

### CI Execution

Tests run automatically on push/PR:

```yaml
# Fast tests (18 tests, ~2s)
pytest tests/performance/ -v -m "performance and not slow"

# Slow tests (6 tests, ~8s)  
pytest tests/performance/ -v -m "slow"

# Full profiler (optional, for reports)
python scripts/profile_performance.py
```

---

## 🔍 Monitoring & Alerts

### Build Status

GitHub Actions shows performance test status:
- ✅ **Green:** All tests passed, no regressions
- ❌ **Red:** Performance regression detected, build fails

### PR Comments

Automated comment on every PR:

```
## 🚀 Performance Test Results

✅ All performance tests passed!

### Test Summary
- Fast tests: ✅ PASSED
- Slow tests: ✅ PASSED

### Performance Thresholds
| Tier | Target | Baseline | Status |
|------|--------|----------|--------|
| Tier 1 | ≤50ms | 0.48ms | ✅ 100× faster |
| Tier 2 | ≤150ms | 0.72ms | ✅ 208× faster |
| Tier 3 | ≤500ms | 52.51ms | ✅ 10× faster |
| Operations | <5000ms | 1431ms | ✅ 3.5× faster |

📊 [View detailed performance report](...)
```

### Daily Monitoring

**Schedule:** 2 AM UTC daily cron job

**Purpose:** Catch performance drift over time
- Database growth
- Dependency updates
- Environmental changes

**Notification:** GitHub Actions failure notifications

---

## 📈 Performance Artifacts

Every CI run produces artifacts:

### 1. Performance Report
**File:** `performance-report.txt`  
**Contents:**
- Tier 1, 2, 3 profiling results
- Operation timings
- Hotspot analysis
- Performance summary

**Retention:** 30 days

### 2. JSON Logs
**Files:** `logs/performance-report-*.json`  
**Contents:**
- Machine-readable metrics
- Timestamp data
- Detailed breakdowns

**Retention:** 30 days

### 3. Comparison (PR only)
**Files:**
- `pr-performance.txt` (PR branch)
- `base-performance.txt` (base branch)

**Retention:** 30 days

---

## ⚠️ Failure Handling

### When Tests Fail

**Symptom:** CI build turns red with "Performance regression detected"

**Steps to diagnose:**

1. **Check test output:**
   ```bash
   # Look for assertion failures
   pytest tests/performance/ -v --tb=short
   ```

2. **Identify slow operation:**
   ```
   AssertionError: Tier 3 analyze_file_hotspots REGRESSION: 
   312.45ms (baseline: 258ms, target: ≤300ms)
   ```

3. **Run profiler locally:**
   ```bash
   python scripts/profile_performance.py
   ```

4. **Compare with baseline:**
   - Baseline: `cortex-brain/cortex-2.0-design/PHASE-6.1-PERFORMANCE-BASELINE.md`
   - Current: Output from profiler

5. **Fix the regression:**
   - Add caching
   - Optimize queries
   - Add database indexes
   - Reduce I/O operations

6. **Re-test locally:**
   ```bash
   pytest tests/performance/ -v
   ```

7. **Push fix and verify CI passes**

### Common Regressions

#### Tier 1 Slowdown (>50ms)
**Causes:**
- Missing database indexes
- Full table scans
- Increased data volume

**Fix:**
- Add indexes: `CREATE INDEX IF NOT EXISTS idx_...`
- Verify EXPLAIN QUERY PLAN
- Implement FIFO conversation pruning

#### Tier 2 Slowdown (>150ms)
**Causes:**
- FTS5 not being used
- Pattern table growth
- Missing indexes

**Fix:**
- Verify FTS5 MATCH queries
- Prune low-confidence patterns (<0.5)
- Rebuild FTS5 index: `INSERT INTO patterns_fts(patterns_fts) VALUES('rebuild')`

#### Tier 3 Slowdown (>500ms)
**Causes:**
- Git operations unbounded
- File hotspot analysis overhead
- No caching

**Fix:**
- Limit analysis window (90 days max)
- Add git metrics caching (TTL: 1 hour)
- Optimize subprocess calls

#### Operation Slowdown (>5000ms)
**Causes:**
- Network I/O
- File system operations
- Subprocess overhead

**Fix:**
- Add operation-level caching
- Parallelize independent tasks
- Reduce git operations

---

## 🔧 Configuration

### Adjusting Thresholds

**File:** `tests/performance/test_performance_regression.py`

```python
# Update thresholds if baseline changes
TIER1_THRESHOLD_MS = 50.0  # Current: 0.48ms avg
TIER2_THRESHOLD_MS = 150.0  # Current: 0.72ms avg
TIER3_THRESHOLD_MS = 500.0  # Current: 52.51ms avg
TIER3_HOTSPOT_THRESHOLD_MS = 300.0  # Hotspot: 258ms
OPERATION_THRESHOLD_MS = 5000.0  # Current: 1431ms avg
```

**When to adjust:**
- ✅ After optimization (lower threshold)
- ✅ After architectural change (re-baseline)
- ❌ To make tests pass (that's regression!)

### Disabling Tests Temporarily

**Use sparingly!** Only for known issues being actively fixed.

```yaml
# .github/workflows/performance.yml
- name: Run fast performance tests
  run: |
    pytest tests/performance/ -v -m "performance and not slow"
  continue-on-error: true  # ⚠️ Allows failures (use cautiously)
```

**Better approach:** Skip specific test:

```python
@pytest.mark.skip(reason="Known regression - fixing in PR #123")
def test_tier3_analyze_file_hotspots_performance(...):
    ...
```

---

## 📚 References

- **Performance Baseline:** `cortex-brain/cortex-2.0-design/PHASE-6.1-PERFORMANCE-BASELINE.md`
- **Test Suite:** `tests/performance/test_performance_regression.py`
- **Profiler:** `scripts/profile_performance.py`
- **CI Workflow:** `.github/workflows/performance.yml`
- **Optimization Guide:** `cortex-brain/cortex-2.0-design/18-performance-optimization.md`

---

## ✅ Success Criteria

Phase 6.1 Task 6 complete when:
- [x] GitHub Actions workflow created (`.github/workflows/performance.yml`)
- [x] Performance tests run on push/PR
- [x] Build fails if thresholds exceeded
- [x] PR comments show test results
- [x] Daily monitoring enabled
- [x] Artifacts uploaded (performance reports)
- [x] Documentation complete (this file)

---

**Status:** ✅ COMPLETE  
**Last Updated:** 2025-11-10  
**CI Integration:** Active on `main`, `CORTEX-2.0`, `develop` branches
