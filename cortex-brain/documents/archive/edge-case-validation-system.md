# Edge Case Validation System - CORTEX 3.0

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** December 17, 2025

---

## Overview

Comprehensive edge case validation system for CORTEX 3.0 unified planning system. Implements safety checks across four priority tiers with automatic user notification during planning workflows.

## Architecture

```
EdgeCaseValidator
├── Security (Immediate)
│   ├── Input sanitization (#6)
│   ├── Filesystem-safe names (#5)
│   └── Session file locking (#2)
├── Stability (Short-term)
│   ├── Rollback safety (#9)
│   ├── Analysis timeout (#11, #12)
│   ├── Idempotency checks (#17)
│   └── Max iterations (#10)
├── Robustness (Medium-term)
│   ├── Concurrent session prevention (#1)
│   ├── Stale session cleanup (#8)
│   ├── Disk space checks (#14)
│   └── Max sessions limit (#15)
└── Quality of Life (Long-term)
    ├── Session expiry (#19)
    ├── Complexity analysis (#20)
    └── Progress callbacks (#22)
```

## Integration Points

### 1. Planning Orchestrator (DoR)

```python
# Integrated into validate_dor()
validation_report = self.edge_case_validator.validate_planning_request(
    feature_name=feature_name,
    feature_description=description,
    acceptance_criteria=acceptance_criteria,
    active_sessions=active_sessions,
    current_session_count=current_session_count
)

if not validation_report.passed:
    # Critical issues block execution
    for issue in validation_report.critical_issues:
        errors.append(f"[{issue.category.upper()}] {issue.message}")
```

### 2. Session Operations

```python
# File locking for safe concurrent access
if not self.edge_case_validator.acquire_session_file_lock(session_id):
    return {'error': 'Session locked by another process'}

try:
    # Perform session operation
    pass
finally:
    self.edge_case_validator.release_session_file_lock(session_id)
```

### 3. Analysis Timeout Protection

```python
# Timeout validation during AST/Lens analysis
elapsed = time.time() - start_time
timeout_issue = self.edge_case_validator.validate_analysis_timeout("AST", elapsed)

if timeout_issue and timeout_issue.severity.name == "CRITICAL":
    logger.warning(f"⏰ {timeout_issue.message}")
    # Use partial results or stub data
```

### 4. Plan Promotion (Rollback Safety)

```python
# Validate before promotion
rollback_issue = self.edge_case_validator.validate_rollback_safety(
    plan_id=session.plan_id,
    temp_plan_path=temp_plan_path,
    permanent_plan_path=permanent_plan_path
)

if rollback_issue and rollback_issue.severity.name == "CRITICAL":
    return {'error': rollback_issue.message}
```

## Validation Categories

### Immediate (Security)

| Issue | Check | Action |
|-------|-------|--------|
| #6 Code Injection | Regex patterns for eval/exec/import | Block with error |
| #5 Filesystem Safety | Alphanumeric + hyphen/underscore only | Block with error |
| #2 Session Locking | Threading.Lock per session | Wait or timeout |

### Short-term (Stability)

| Issue | Check | Action |
|-------|-------|--------|
| #9 Rollback Safety | Temp exists, permanent backup | Warn + auto-fix |
| #11 AST Timeout | Elapsed vs threshold | Partial results |
| #12 Lens Timeout | Elapsed vs threshold | Stub data |
| #17 Idempotency | State matches expected | Block with error |
| #10 Max Iterations | Count vs limit | Warn at 80%, block at 100% |

### Medium-term (Robustness)

| Issue | Check | Action |
|-------|-------|--------|
| #1 Concurrent Sessions | Multiple active for same plan | Warn user |
| #8 Stale Cleanup | Age > expiry threshold | Auto-cleanup on startup |
| #14 Disk Space | Free space < threshold | Block with error |
| #15 Max Sessions | Count vs limit | Warn at 80%, block at 100% |

### Long-term (Quality of Life)

| Issue | Check | Action |
|-------|-------|--------|
| #19 Session Expiry | Age > expiry hours | Warn, auto-close |
| #20 Complexity Mismatch | Heuristic vs estimated tier | Info message |
| #22 Progress Callbacks | Logged at each step | Info logging |

## Configuration

```python
EdgeCaseValidator(
    sessions_dir=Path("cortex-brain"),
    max_sessions=10,              # Max concurrent sessions
    min_disk_space_gb=1.0,        # Min required disk space
    analysis_timeout=300,         # 5 minutes for AST/Lens
    session_expiry_hours=24,      # 24 hours until expiry
    max_iterations=50             # Max refinement iterations
)
```

## User Experience

### Clean Request (No Issues)

```
🔍 Edge case validation: ✅ All validation checks passed
```

### With Warnings (Non-blocking)

```
🔍 Edge case validation: ⚠️  2 warning(s)

⚠️  [ROBUSTNESS] Multiple concurrent sessions detected: 2 active
  → Mitigation: Close or complete existing sessions before starting new ones

⚠️  [QUALITY_OF_LIFE] Session expiring soon: 2.3h remaining
  → Mitigation: Consider completing or extending session
```

### With Critical Issues (Blocking)

```
🔍 Edge case validation: ❌ 1 critical issue(s)

❌ [SECURITY] 'feature_name' contains invalid characters: 'user@auth!'. Only alphanumeric, hyphen, underscore allowed
  → Mitigation: Remove special characters and spaces

Execution blocked - fix critical issues to proceed.
```

## Testing

Comprehensive test suite with 50+ test cases:

```bash
pytest tests/orchestration_3_0/core/test_edge_case_validator.py -v
```

### Test Coverage

- ✅ Input sanitization (eval, exec, import, path traversal)
- ✅ Filesystem-safe names (special chars, spaces, length)
- ✅ Session file locking (concurrent access, timeouts)
- ✅ Rollback safety (missing temp, existing permanent)
- ✅ Analysis timeout (within limit, exceeded, approaching)
- ✅ Idempotency (correct state, incorrect state)
- ✅ Max iterations (within limit, exceeded, approaching)
- ✅ Concurrent sessions (single, multiple)
- ✅ Stale session cleanup (expired vs recent)
- ✅ Max sessions limit (within, at limit, approaching)
- ✅ Session expiry (recent, expired, expiring soon)
- ✅ Complexity analysis (matching, mismatched)
- ✅ Progress callbacks (invocable, logging)
- ✅ Comprehensive validation (clean, with issues)

## Auto-fixable Issues

Some issues can be automatically fixed:

| Issue | Auto-fix Action |
|-------|-----------------|
| #5 Invalid chars | Replace with hyphens |
| #9 Existing permanent | Create timestamped backup |
| #11/#12 Timeout | Use partial/stub data |

```python
if rollback_issue and rollback_issue.auto_fixable:
    logger.info(f"🔧 Auto-fixing: {rollback_issue.mitigation}")
    # Perform auto-fix
```

## Monitoring

Edge case validation events are logged for monitoring:

```python
logger.info("🔍 Edge case validation: {report.get_summary()}")
logger.warning(f"⚠️  {issue.message}")
logger.error(f"❌ {issue.message}")
```

Severity levels map to log levels:
- `CRITICAL` → `ERROR` (blocks execution)
- `WARNING` → `WARNING` (allows execution with notice)
- `INFO` → `INFO` (informational only)

## Future Enhancements

1. **Configurable thresholds** - Per-project validation settings
2. **Custom validators** - Plugin system for project-specific checks
3. **Metrics collection** - Track validation failures over time
4. **User preferences** - Allow users to adjust warning thresholds
5. **Integration with CI/CD** - Pre-commit validation hooks

## References

- Implementation: `src/orchestration_3_0/core/edge_case_validator.py`
- Tests: `tests/orchestration_3_0/core/test_edge_case_validator.py`
- Integration: `src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py`
- Original spec: User request for 22 edge case checks

---

**Note:** This system is deeply integrated into CORTEX 3.0 unified planning system and validates all user interactions during the back-and-forth refinement process. Edge cases are brought to user attention proactively, preventing issues before they occur.
