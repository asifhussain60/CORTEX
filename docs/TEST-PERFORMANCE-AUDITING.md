# Test Performance Auditing - Enterprise Solution

## Overview

CORTEX now includes an enterprise-level test performance auditing system that automatically tracks, logs, and reports on test execution performance. This solves the "hanging tests" problem by providing real-time visibility into test performance metrics.

## Problem Solved

**Before:** Tests would hang indefinitely with no visibility into which test was slow or stuck
**After:** Complete audit trail of all test execution with automatic detection of:
- Hanging tests (timeout detection via pytest-timeout)
- Slow tests (>1s threshold with automatic alerts)
- Very slow tests (>5s - requires investigation)

## Components

### 1. **Pytest Plugin: `cortex/testing/pytest_plugin_audit.py`**

Automatically integrated via `tests/conftest.py`. Tracks every test execution in real-time:

```python
# Automatic registration
config.pluginmanager.register(cortex_test_audit_plugin, name="cortex_test_audit")
```

**Features:**
- Real-time test start/stop tracking
- Automatic performance metrics collection
- Structured JSON logging
- Slow test detection and warnings
- Session-level statistics

### 2. **Enterprise Audit Logger**

Produces structured audit logs in `test_audit_trail.log`:

```
2026-01-21T15:00:00Z | cortex_test_audit | INFO | 🚀 TEST SESSION START
2026-01-21T15:00:00Z | cortex_test_audit | INFO | ✅ PASSED | 0.045s | tests/unit/intent_router/test_classifier.py::TestIntentClassifier::test_classify_single
2026-01-21T15:00:01Z | cortex_test_audit | WARNING | 🐢 SLOW TEST: tests/unit/core/test_orchestrator.py::TestOrchestrator::test_complex_workflow took 2.341s
2026-01-21T15:00:05Z | cortex_test_audit | INFO | ✅ SESSION COMPLETE - Passed: 128, Failed: 0, Skipped: 1, Errors: 0 | Total Duration: 5.23s
```

### 3. **Performance Audit Database**

SQLite database (`cortex_brain/state/test_audit.db`) with:
- Test execution metrics (start/end time, duration, status)
- Audit session tracking
- Query interface for slow/hanging test analysis

### 4. **CLI Tools**

#### A. **Shell Script Wrapper** (`scripts/test-audit.sh`)

Easy-to-use CLI for test auditing:

```bash
# Run tests with audit
./scripts/test-audit.sh run tests/unit/core/

# Show slow tests
./scripts/test-audit.sh slow

# Show hanging tests
./scripts/test-audit.sh hanging

# Generate report
./scripts/test-audit.sh report

# Analyze with custom threshold
./scripts/test-audit.sh analyze --threshold 2.0

# Watch logs live
./scripts/test-audit.sh logs
```

#### B. **Python Auditor** (`scripts/test-performance-auditor.py`)

Standalone Python tool for detailed analysis:

```bash
# Run with audit tracking
python scripts/test-performance-auditor.py run tests/unit/core/

# Generate report
python scripts/test-performance-auditor.py report

# Analyze slow tests
python scripts/test-performance-auditor.py analyze --threshold-seconds 1.5
```

## Usage Examples

### Example 1: Quick Test Run with Audit

```bash
$ ./scripts/test-audit.sh run tests/unit/intent_router/

🚀 Running Tests with Performance Audit
📝 Audit log: /path/to/test_audit_trail.log
💾 Database:  /path/to/cortex_brain/state/test_audit.db

[... test execution ...]

📊 Test Performance Summary
🐢 Top 20 Slowest Tests:
   2.341s  ✅ PASSED  tests/unit/core/orchestrator/test_master.py::TestMaster::test_complex_workflow
   1.892s  ✅ PASSED  tests/unit/domain_brain/test_adapter.py::TestAdapter::test_extract_entities
   1.234s  ✅ PASSED  tests/unit/core/test_governance.py::TestGovernance::test_rules_enforcement
   ...
```

### Example 2: Find Hanging Tests

```bash
$ ./scripts/test-audit.sh hanging

🚨 HANGING/ERRORED TESTS (Needs Investigation):
  • tests/unit/core/orchestrator/test_heavy_workflow.py::test_orchestrator_with_timeout
    Status: ERROR
    Error: Timeout exceeded after 30 seconds
```

### Example 3: Analyze Slow Tests

```bash
$ ./scripts/test-audit.sh analyze --threshold 1.0

🔍 Analyzing Test Performance (threshold: 1.0s)

📈 Found 12 slow tests:
   2.341s  tests/unit/core/orchestrator/test_master.py::TestMaster::test_complex_workflow
   1.892s  tests/unit/domain_brain/test_adapter.py::TestAdapter::test_extract_entities
   1.234s  tests/unit/core/test_governance.py::TestGovernance::test_rules_enforcement
   1.100s  tests/unit/api/test_endpoints.py::TestEndpoints::test_concurrent_requests
```

### Example 4: Run Specific Test with Audit

```bash
$ ./scripts/test-audit.sh run tests/unit/core/orchestrator/ -k "test_master" -v

[... test execution with performance tracking ...]
```

### Example 5: Watch Audit Log Live

```bash
$ ./scripts/test-audit.sh logs

# Terminal shows real-time log updates as tests run in another terminal
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Run Tests with Performance Audit
  run: ./scripts/test-audit.sh run tests/ --tb=short

- name: Upload Performance Report
  uses: actions/upload-artifact@v2
  with:
    name: test-performance
    path: |
      test_audit_trail.log
      test_performance_report.json
      cortex_brain/state/test_audit.db
```

## Key Features

### 1. **Automatic Timeout Protection**

Combined with `pytest-timeout` plugin:
- Default: 30 seconds per test
- Configurable per test via `@pytest.mark.timeout(seconds)`
- Prevents infinite loops and hanging

### 2. **Real-Time Alerts**

Automatic detection of:
- **Slow tests** (>1s): Yellow warning
- **Very slow tests** (>5s): Red error alert
- **Timeouts**: Immediate notification

### 3. **Enterprise Audit Trail**

Every test execution creates structured audit record:
- Test ID
- Start/end time
- Duration
- Status (PASSED/FAILED/ERROR/TIMEOUT)
- Error message (first 500 chars)
- Timestamp

### 4. **Performance Analysis**

Query interface to find:
- Top N slowest tests
- Hanging/errored tests
- Tests exceeding threshold
- Session statistics

### 5. **Production-Ready**

- Thread-safe database access
- JSON-formatted logs for parsing
- No test environment pollution
- Graceful degradation if plugin fails

## Database Schema

```sql
CREATE TABLE test_metrics (
    id INTEGER PRIMARY KEY,
    test_id TEXT UNIQUE,           -- Full test node ID
    test_file TEXT,                -- File path
    test_class TEXT,               -- Class name
    test_method TEXT,              -- Method name
    status TEXT,                   -- PASSED/FAILED/ERROR/TIMEOUT
    start_time REAL,               -- Unix timestamp
    end_time REAL,                 -- Unix timestamp
    duration_seconds REAL,         -- Calculated duration
    error_message TEXT,            -- Error details
    recorded_at TEXT               -- ISO timestamp
);

CREATE TABLE audit_sessions (
    id INTEGER PRIMARY KEY,
    session_id TEXT UNIQUE,        -- Unique session ID
    started_at TEXT,               -- ISO timestamp
    completed_at TEXT,             -- ISO timestamp
    total_tests INTEGER,           -- Total tests in session
    passed INTEGER,                -- Passed count
    failed INTEGER,                -- Failed count
    errors INTEGER,                -- Error count
    timeouts INTEGER,              -- Timeout count
    skipped INTEGER,               -- Skipped count
    total_duration_seconds REAL    -- Total duration
);
```

## Troubleshooting

### Audit Log Not Created

If `test_audit_trail.log` is not created:

1. Check conftest.py is loaded:
   ```bash
   python3 -m pytest tests/ -v 2>&1 | grep "cortex_test_audit"
   ```

2. Check permissions:
   ```bash
   ls -la cortex/testing/pytest_plugin_audit.py
   ```

3. Manual logging setup:
   ```bash
   python3 -c "from cortex.testing.pytest_plugin_audit import cortex_test_audit_plugin; print('Plugin loaded')"
   ```

### Tests Run Slower with Audit

Audit overhead is minimal (<1% in most cases). If noticeable:
- Audit log disk I/O: Write to tmpfs or SSD
- Database queries: Batch inserts happen at session end

### Filtering Slow Tests

Use pytest's `-k` option:

```bash
# Run only tests that are slow
./scripts/test-audit.sh run tests/ -k "test_" --tb=short

# Then analyze
./scripts/test-audit.sh slow
```

## Future Enhancements

1. **Performance Trends**
   - Track performance over time
   - Detect regressions automatically

2. **Test Failure Analysis**
   - Correlate failures with slow execution
   - Identify flaky tests

3. **Resource Monitoring**
   - Memory usage per test
   - CPU utilization patterns

4. **Integration**
   - Slack notifications for hanging tests
   - Dashboard for test metrics
   - Integration with monitoring systems

## Files

| File | Purpose |
|------|---------|
| `cortex/testing/pytest_plugin_audit.py` | Pytest plugin for tracking |
| `scripts/test-performance-auditor.py` | Enterprise auditor tool |
| `scripts/test-audit.sh` | CLI wrapper for easy usage |
| `tests/conftest.py` | Plugin registration |
| `test_audit_trail.log` | Structured audit log |
| `cortex_brain/state/test_audit.db` | SQLite audit database |
| `test_performance_report.json` | JSON performance report |

## Quick Start

1. **Run tests with audit:**
   ```bash
   ./scripts/test-audit.sh run tests/unit/core/
   ```

2. **View slow tests:**
   ```bash
   ./scripts/test-audit.sh slow
   ```

3. **Find hanging tests:**
   ```bash
   ./scripts/test-audit.sh hanging
   ```

4. **Generate report:**
   ```bash
   ./scripts/test-audit.sh report
   ```

That's it! Enterprise-level test performance auditing enabled.
