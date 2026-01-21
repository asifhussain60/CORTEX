# Test Execution Strategy with Continuous Progress Monitoring

## Overview

This document defines how to use the new test progress monitoring system for:
- **Real-time feedback** during long-running tests
- **Hanging test detection** with automatic reporting
- **Test suite analytics** for continuous improvement
- **Phased execution** with progress tracking

## System Components

### 1. Test Progress Monitor (`cortex/devx/test_progress_monitor.py`)

**Real-time progress tracking with hanging detection**

```bash
# Direct usage
from cortex.devx.test_progress_monitor import run_tests_with_progress

exit_code = run_tests_with_progress(
    test_path='tests/unit/infrastructure/',
    pytest_args=['-q', '--tb=no'],
    hang_timeout=30,  # Report hanging after 30s of no output
    verbose=True
)
```

**Features:**
- ✓ Live test counter (Passed/Failed/Errors)
- ✓ Tests per second rate calculation
- ✓ Current test name display
- ✓ Hanging detection with alerts at 30s and 60s
- ✓ Final metrics summary

### 2. pytest-monitor Command

**Wrapper for running pytest with progress**

```bash
# Basic usage
./scripts/pytest-monitor tests/unit/core/ -v --tb=short

# With custom hang timeout
./scripts/pytest-monitor tests/unit/infrastructure/ -q --hang-timeout=60

# Quiet mode (minimal output)
./scripts/pytest-monitor tests/ --quiet
```

### 3. Pytest Progress Plugin (`cortex/devx/pytest_progress_plugin.py`)

**Automatic progress reporting built into pytest**

Automatically enabled in pytest.ini - no setup needed.

```
[PYTEST PROGRESS] Collected 354 tests
[PYTEST PROGRESS] 50/354 - 45✓ 3✗ 1⚠ (127.3 tests/sec) - test_ac_deletion
[PYTEST PROGRESS] 100/354 - 89✓ 8✗ 3⚠ (156.2 tests/sec) - test_governance_compliance
```

### 4. Test Analytics Dashboard (`scripts/test-analytics.py`)

**Comprehensive test suite analysis and reporting**

```bash
# Analyze single test suite
python3 scripts/test-analytics.py tests/unit/core/

# Analyze multiple suites
python3 scripts/test-analytics.py tests/unit/core/ tests/unit/infrastructure/ tests/unit/domain_brain/

# Output: Detailed report with health score, pass rates, hanging detection
```

**Output includes:**
- Collection metrics (total, errors)
- Execution metrics (passed/failed/errors/skipped)
- Quality metrics (pass rate, health score 0-100)
- Hanging detection alerts
- JSON report saved to `_workspaces/roadmap/analytics/`

## Phased Test Execution Strategy

### Phase 1: COLLECTION (2-5 seconds)

**Verify all tests are discoverable without import errors**

```bash
python3 -m pytest tests/ --collect-only -q
```

Expected output:
```
[PYTEST PROGRESS] Collected 7598 tests
```

**Stop if:** Collection errors > 0 (indicates import/syntax problems)

### Phase 2: INFRASTRUCTURE VERIFICATION (5-15 seconds)

**Verify core test infrastructure and timeout handling**

```bash
pytest-monitor tests/unit/core/hallucination_prevention/ -q --tb=no
```

Expected: No hanging detected, 80%+ pass rate

### Phase 3: CRITICAL MODULE TESTING (15-45 seconds)

**Test P0-CRITICAL modules with progress tracking**

```bash
pytest-monitor tests/unit/core/orchestrator/test_conversation_protocol.py -q
pytest-monitor tests/unit/core/intent/ -q --tb=no
pytest-monitor tests/unit/domain_brain/ -q --hang-timeout=60
```

### Phase 4: COMPREHENSIVE SUITE ANALYSIS (60-300 seconds)

**Full analytics on all test suites**

```bash
python3 scripts/test-analytics.py \
  tests/unit/core/ \
  tests/unit/domain_brain/ \
  tests/unit/infrastructure/ \
  tests/integration/
```

**Output:** Health scores per module, recommendations for improvements

### Phase 5: HANGI NG INVESTIGATION (if needed)

**Detect and diagnose hanging tests**

```bash
pytest-monitor tests/unit/infrastructure/ --hang-timeout=10 -v
```

When hanging detected:
- Note the test name from progress output
- Run in isolation: `pytest tests/path/to/test.py -v -s`
- Apply timeout: `pytest tests/path/to/test.py -v --timeout=5`

## Integration with PHASE-E Autonomous Loop

### Real-time Progress During TDD Implementation

```python
# In PHASE-E implementation loop
from cortex.devx.test_progress_monitor import run_tests_with_progress

module_name = "hallucination_prevention"
exit_code = run_tests_with_progress(
    test_path=f"tests/unit/core/{module_name}/",
    pytest_args=['-q', '--tb=short'],
    hang_timeout=30,
    verbose=True
)

if exit_code == 0:
    print(f"✓ {module_name}: All tests passing - Proceeding to next module")
else:
    print(f"⚠ {module_name}: Some tests failing - Fix before advancing")
```

### Automatic Hanging Detection

If a module test suite hangs:

1. **Auto-detected:** Progress monitor detects no output for 30s
2. **Alert shown:** `⚠️ HANGING DETECTED: No output for 35s. Current test: test_ac_deletion`
3. **Critical alert:** At 60s: `🔴 CRITICAL HANG: 65s without output! Test likely deadlocked`
4. **Process management:** Can optionally auto-kill and skip with `--auto-kill-hanging`

## Usage Examples

### Example 1: Quick Core Module Check (60 seconds)

```bash
#!/bin/bash
echo "Quick core module health check..."
python3 scripts/test-analytics.py tests/unit/core/
```

**Output:**
```
========================================
TEST ANALYTICS SUMMARY
========================================

Collection Phase:
  Total Collected:    354
  Collection Errors:  0

Execution Phase:
  Total Run:          354
  ✓ Passed:           304
  ✗ Failed:           32
  ⚠ Errors:           18
  - Skipped:          0

Quality Metrics:
  Pass Rate:          85.9%
  Health Score:       75/100

========================================
```

### Example 2: Monitor Long-Running Test (Infrastructure - 5+ minutes)

```bash
./scripts/pytest-monitor tests/unit/infrastructure/ -q \
  --hang-timeout=30 \
  --verbose-progress
```

**Continuous output:**
```
[TEST PROGRESS] Starting tests: python3 -m pytest tests/unit/infrastructure/ -q
[TEST PROGRESS] Test Collection: 287 tests discovered
[TEST PROGRESS] Progress: 0✓ 0✗ 0⚠ (0.0 tests/sec) - Current: test_connection_pool_create
[TEST PROGRESS] Progress: 50✓ 3✗ 1⚠ (67.3 tests/sec) - test_circuit_breaker_open
[TEST PROGRESS] Progress: 100✓ 5✗ 2⚠ (78.1 tests/sec) - test_retry_backoff
...
[TEST PROGRESS] Tests Complete: 276✓ 8✗ 3⚠ (Duration: 312.4s)
```

### Example 3: Investigate Hanging Test

```bash
# First, identify hanging test with short timeout
./scripts/pytest-monitor tests/unit/infrastructure/ \
  --hang-timeout=5 -v

# Output shows:
# ⚠️ HANGING DETECTED: No output for 5.2s. Current test: test_complex_pooling_scenario

# Then run just that test with debug
pytest tests/unit/infrastructure/test_connection_pool.py::test_complex_pooling_scenario -vv -s

# Apply timeout
pytest tests/unit/infrastructure/test_connection_pool.py::test_complex_pooling_scenario -v --timeout=10
```

## Configuration

### pytest.ini Settings

```ini
# Automatic progress plugin
addopts = -v --tb=short -p cortex.devx.pytest_progress_plugin

# Hanging timeout
timeout = 30
timeout_method = thread

# Hanging detection verbosity
# (managed by pytest_progress_plugin)
markers =
    slow: Tests taking >5 seconds
    hanging: Suspected hanging test
```

### Environment Variables

```bash
# Control progress reporting
export PYTEST_PROGRESS_VERBOSE=1     # Enable verbose progress
export PYTEST_HANG_TIMEOUT=60        # Set hanging timeout to 60s

# Control analytics
export PYTEST_ANALYTICS_DIR="/path/to/analytics"  # Custom analytics directory
```

## Recommended Phased Test Execution for PHASE-E

```bash
#!/bin/bash
# PHASE-E Test Execution Loop

echo "PHASE-E: TDD Implementation Loop"
echo "================================"

MODULES=(
  "hallucination_prevention"
  "conversation_protocol"
  "governance"
  "domain_brain"
  "infrastructure"
)

for MODULE in "${MODULES[@]}"; do
    echo ""
    echo "[$(date '+%H:%M:%S')] Testing: $MODULE"
    echo "─────────────────────────────────"
    
    # Run with progress monitoring
    ./scripts/pytest-monitor "tests/unit/core/$MODULE/" \
      -q --tb=short --hang-timeout=45
    
    if [ $? -eq 0 ]; then
        echo "✓ $MODULE: PASS - Proceeding"
    else
        echo "✗ $MODULE: FAIL - Investigating"
        # Run failed tests with verbose output
        ./scripts/pytest-monitor "tests/unit/core/$MODULE/" -v --tb=long
        break  # Stop loop on first failure
    fi
done

echo ""
echo "[$(date '+%H:%M:%S')] Final Analytics"
echo "─────────────────────────────────"
python3 scripts/test-analytics.py tests/unit/core/
```

## Troubleshooting

### Issue: Tests running but no progress output

**Solution:** Tests are running but output buffering is hiding progress.

```bash
# Force unbuffered output
export PYTHONUNBUFFERED=1
./scripts/pytest-monitor tests/unit/core/ -q

# Or use pytest -s flag
pytest tests/unit/core/ -s -v
```

### Issue: Hanging detected but tests complete quickly

**Solution:** Increase hang timeout for slow systems.

```bash
./scripts/pytest-monitor tests/unit/infrastructure/ --hang-timeout=60
```

### Issue: Progress plugin not loading

**Solution:** Ensure cortex package is in PYTHONPATH.

```bash
export PYTHONPATH="/Users/asifhussain/PROJECTS/CORTEX:$PYTHONPATH"
pytest tests/ -v
```

## Benefits

✓ **Never silent long-running tests** - Always know what's happening
✓ **Automatic hanging detection** - Saves debugging time
✓ **Performance baselines** - Track tests/sec over time
✓ **Quality metrics** - Health scores guide improvement prioritization
✓ **Autonomous PHASE-E** - Progress feedback during 15-20 day implementation
✓ **Problem diagnosis** - Quick identification of problem modules

## Next Steps

1. Enable pytest progress plugin in pytest.ini (already done)
2. Run `pytest-monitor tests/unit/core/` to verify setup
3. Integrate into CI/CD pipeline for all test runs
4. Collect analytics weekly to track trends
5. Use health scores to prioritize module fixes
