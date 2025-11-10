# CI/CD Workflow Monitoring Guide

**Date:** November 10, 2025  
**Branch:** CORTEX-2.0  
**Commit:** 5605a1b (Mac Phase 5.3 & 5.4)

---

## 🚀 Workflows Triggered

The following GitHub Actions workflows should now be running:

1. **macOS Test Suite** (`.github/workflows/macos-tests.yml`)
2. **Cross-Platform Matrix** (`.github/workflows/cross-platform.yml`)
3. **Performance Benchmarks** (`.github/workflows/benchmarks.yml`)

---

## 📊 How to Monitor

### GitHub UI

1. **Navigate to Actions tab:**
   ```
   https://github.com/asifhussain60/CORTEX/actions
   ```

2. **Check workflow status:**
   - Look for workflows with commit message: "feat(mac-track): Complete Phase 5.3 & 5.4"
   - Status indicators:
     - 🟡 Yellow dot = Running
     - ✅ Green check = Passed
     - ❌ Red X = Failed

3. **View detailed logs:**
   - Click on workflow run
   - Expand job steps
   - Check test output

### Command Line

```bash
# Check latest workflow runs (requires GitHub CLI)
gh run list --branch CORTEX-2.0 --limit 5

# Watch specific workflow
gh run watch

# View workflow details
gh run view <run-id>
```

---

## ✅ Expected Results

### 1. macOS Test Suite (macos-tests.yml)

**Expected Jobs:** 3 (Python 3.9, 3.10, 3.11)

**Expected Steps:**
- ✅ Checkout code
- ✅ Set up Python
- ✅ Install dependencies
- ✅ Run unit tests
- ✅ Run Mac-specific tests (7 tests passing)
- ✅ Upload coverage to Codecov
- ✅ Archive test results

**Success Criteria:**
- All Python versions pass
- Mac-specific tests: 7/7 passing
- Code coverage report uploaded

**Approximate Duration:** 3-5 minutes per Python version

---

### 2. Cross-Platform Matrix (cross-platform.yml)

**Expected Jobs:** 5 total
- Ubuntu + Python 3.9, 3.10, 3.11 (3 jobs)
- macOS + Python 3.9 (1 job)
- Windows + Python 3.9 (1 job)

**Expected Steps:**
- ✅ Platform detection working
- ✅ Path resolution working
- ✅ Core tests passing
- ✅ Platform-specific tests (macOS only)

**Success Criteria:**
- All 5 jobs pass
- No cross-platform regressions
- Platform-specific tests run correctly

**Approximate Duration:** 4-6 minutes total

---

### 3. Performance Benchmarks (benchmarks.yml)

**Expected Jobs:** 2
- Benchmark on macOS
- Compare with baseline

**Expected Steps:**
- ✅ YAML loading benchmarks
- ✅ Config loading benchmarks
- ✅ SQLite query benchmarks
- ✅ Memory profiling
- ✅ Upload benchmark results

**Success Criteria:**
- Benchmarks complete without errors
- Results uploaded as artifacts
- No major performance regressions

**Approximate Duration:** 2-3 minutes

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ModuleNotFoundError` or `ImportError`

**Check:**
```bash
# Verify requirements.txt is complete
cat requirements.txt

# Check if dependencies installed correctly
pip list | grep -E "pytest|pyyaml|sqlite"
```

**Solution:** Add missing dependencies to requirements.txt

---

#### 2. Test Failures

**Problem:** Tests failing in CI but passing locally

**Common Causes:**
- Path differences (macOS vs Linux)
- Missing environment variables
- Database initialization issues
- Platform-specific behavior

**Check:**
- Review test logs in GitHub Actions
- Compare with local test run
- Check for hardcoded paths

---

#### 3. Workflow Syntax Errors

**Problem:** Workflow doesn't start or shows syntax error

**Check:**
```bash
# Validate workflow syntax locally
brew install actionlint  # macOS
actionlint .github/workflows/*.yml
```

**Solution:** Fix YAML syntax errors

---

#### 4. Coverage Upload Issues

**Problem:** Codecov upload fails

**Check:**
- Ensure `coverage.xml` is generated
- Check Codecov token (if required)
- Verify network connectivity

**Solution:**
- Add `continue-on-error: true` (already added)
- Check Codecov dashboard

---

## 📈 What to Look For

### Good Signs ✅

- All workflow jobs show green checkmarks
- Test summary shows expected pass rate:
  - Mac-specific: 7/7 passing
  - Overall edge cases: 40/46 passing
- Coverage report uploaded successfully
- No timeout or resource errors
- Benchmark results within expected ranges

### Warning Signs ⚠️

- Some jobs yellow (still running after 10+ minutes)
- Test failures unrelated to Mac work
- Resource constraints (memory, disk)
- Intermittent network errors

### Red Flags ❌

- All jobs failing
- Syntax errors in workflow files
- Authentication failures
- Critical test failures in core functionality

---

## 📝 Next Steps After Validation

### If All Pass ✅

1. **Document success:**
   - Update MAC-COMPLETION-SUMMARY.md
   - Add CI badge to README

2. **Create Week 12 sync checkpoint:**
   - Prepare merge plan for Windows track
   - Identify any conflicts
   - Update STATUS.md

3. **Begin Phase 5 integration planning:**
   - Schedule sync meeting
   - Plan full feature branch merge
   - Prepare release notes

### If Failures Occur ❌

1. **Investigate failures:**
   - Download workflow logs
   - Reproduce locally if possible
   - Identify root cause

2. **Fix issues:**
   - Create fix branch
   - Add tests for the fix
   - Push and re-validate

3. **Update documentation:**
   - Document the issue
   - Add to troubleshooting guide
   - Update workflow if needed

---

## 🔗 Quick Links

**GitHub Actions:**
- Actions tab: https://github.com/asifhussain60/CORTEX/actions
- Workflow files: `.github/workflows/`

**Documentation:**
- MAC-COMPLETION-SUMMARY.md
- MAC-PARALLEL-TRACK-DESIGN.md
- Tests: `tests/platform/test_macos_edge_cases.py`

**Related Issues:**
- Phase 5.3 tracking
- Phase 5.4 tracking
- CORTEX 2.0 milestone

---

## ⏱️ Expected Timeline

**Initial validation:** 10-15 minutes (all 3 workflows)

**Monitoring period:** 24 hours
- Check for any delayed failures
- Monitor scheduled runs (daily, weekly)
- Verify artifact uploads

**Follow-up:** Week 11
- Review coverage trends
- Check benchmark comparisons
- Plan any optimizations

---

*Generated: November 10, 2025*  
*Push commit: 5605a1b*  
*Next review: November 11, 2025 (24 hours)*
