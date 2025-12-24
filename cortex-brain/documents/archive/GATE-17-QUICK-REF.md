# CORTEX 3.2.1 Deployment Gates Quick Reference

**Total Gates:** 17  
**Critical (ERROR):** 15  
**Warning (Non-blocking):** 2  
**Last Updated:** November 30, 2025

---

## All Deployment Gates

| # | Gate Name | Severity | Purpose | Key Validation |
|---|-----------|----------|---------|----------------|
| 1 | Integration Scores | ERROR | System alignment >80% | Orchestrator integration validated |
| 2 | Test Coverage | ERROR | All tests passing | Zero test failures allowed |
| 3 | No Mocks in Production | ERROR | Real implementations only | No mock/stub code in production paths |
| 4 | Documentation Sync | WARNING | Docs match code | Prompts reflect actual capabilities |
| 5 | Version Consistency | ERROR | Version files match | VERSION, setup.py, package.json aligned |
| 6 | Template Format Validation | ERROR | Response templates valid | YAML syntax + required fields present |
| 7 | Git Checkpoint System | ERROR | Checkpoint enforcement | TDD commits enforced, RED→GREEN validated |
| 8 | Swagger/OpenAPI Documentation | ERROR | API docs operational | OpenAPI spec generation works |
| 9 | Timeframe Estimator Module | WARNING | Time estimation works | Estimation orchestrator functional |
| 10 | Production File Validation | WARNING | Entry points valid | Module orchestrators exist and loadable |
| 11 | CORTEX Brain Operational | ERROR | Brain databases accessible | Tier 1-3 DBs exist and queryable |
| 12 | Next Steps Formatting | ERROR | Response format compliance | 5-part response structure enforced |
| 13 | TDD Mastery Integration | ERROR | TDD workflow operational | State machine + processor integrated |
| 14 | User Feature Packaging | ERROR | User features deployable | Modules packaged for user deployment |
| 15 | Admin/User Separation | ERROR | Admin ops protected | Admin-only operations not in user modules |
| 16 | Align EPM User-Only | WARNING | EPM shows user ops only | No admin commands in Setup EPM |
| 17 | **Incremental Work Management** | **ERROR** | **Length limit prevention** | **3-layer architecture validated** |

---

## Gate 17: Incremental Work Management System (NEW)

**Added:** November 30, 2025  
**CORTEX Version:** 3.2.1  
**Severity:** ERROR (blocks deployment)

### What It Validates

✅ **Layer 1: ResponseSizeMonitor**
- File exists: `src/utils/response_monitor.py`
- Token estimation working
- Auto-chunking >3.5K tokens
- 23 tests passing

✅ **Layer 2: IncrementalWorkExecutor**
- File exists: `src/orchestrators/base_incremental_orchestrator.py`
- WorkChunk/WorkCheckpoint dataclasses present
- Dependency management working
- Checkpoint creation operational
- 23 tests passing

✅ **Layer 3: TDD Orchestrator**
- File exists: `src/orchestrators/tdd_orchestrator.py`
- RED→GREEN→REFACTOR phases implemented
- Inherits from IncrementalWorkExecutor
- Phase-specific handlers present
- 24 tests passing

✅ **Integration**
- ResponseSizeMonitor integrated
- Progress tracking enabled
- Checkpoint system operational
- **Total: 70 passing tests**

### Why It Matters

**Problem Solved:** "Sorry, the response hit the length limit" errors

**Before Gate 17:**
- TDD workflows with 10+ requirements would fail
- Planning large features would hit token limits
- Code reviews of 500+ lines would error out
- No automatic chunking or checkpoint system

**After Gate 17:**
- TDD workflows with 20+ requirements complete successfully
- Automatic chunking to ≤500 tokens per response
- Checkpoints at phase boundaries for user control
- Length limit errors eliminated

### Validation Process

1. **File Existence Check**
   - Validates all 3 layer files exist
   - Validates all 3 test files exist

2. **Component Validation**
   - Scans source code for required classes/methods
   - Validates inheritance hierarchy
   - Checks integration points

3. **Test Execution**
   - Runs pytest on all 3 test files (30s timeout each)
   - Parses output for pass/fail status
   - Counts passing tests (must be 70+)

4. **Integration Validation**
   - Confirms ResponseSizeMonitor used in Layer 2/3
   - Confirms IncrementalWorkExecutor inheritance in Layer 3
   - Confirms progress tracking integrated
   - Confirms checkpoint system operational

### Success Criteria

All of the following must be true:

1. ✅ Layer 1 file exists with all required methods
2. ✅ Layer 2 file exists with all required components
3. ✅ Layer 3 file exists with all required phases
4. ✅ All 3 test files exist
5. ✅ All 70 tests passing (23 + 23 + 24)
6. ✅ Integration points validated

**If any criterion fails:** Deployment BLOCKED

---

## Running Gate Validation

### Test Single Gate

```python
from src.deployment.deployment_gates import DeploymentGates
from pathlib import Path

gates = DeploymentGates(Path.cwd())
result = gates._validate_incremental_work_system()

print(f"Status: {result['passed']}")
print(f"Message: {result['message']}")
```

### Test All Gates

```python
from src.deployment.deployment_gates import DeploymentGates
from pathlib import Path

gates = DeploymentGates(Path.cwd())
result = gates.validate_all_gates()

print(f"Overall: {'PASSED' if result['passed'] else 'FAILED'}")
print(f"Errors: {len(result['errors'])}")
print(f"Warnings: {len(result['warnings'])}")
```

### Via Deployment Script

```bash
# Full deployment with all gates
python scripts/deploy_cortex.py

# Deployment gates run automatically
# Gate 17 will block if incremental system incomplete
```

---

## Troubleshooting Gate 17 Failures

### Error: "Layer 1 (ResponseSizeMonitor) not found"

**Cause:** Missing `src/utils/response_monitor.py`

**Fix:**
```bash
# Restore from Phase 1 implementation
git checkout origin/CORTEX-3.0 -- src/utils/response_monitor.py
git checkout origin/CORTEX-3.0 -- tests/test_response_monitor.py
```

### Error: "Layer 2 (IncrementalWorkExecutor) incomplete"

**Cause:** Missing methods in `base_incremental_orchestrator.py`

**Fix:**
```bash
# Restore from Phase 2 implementation
git checkout origin/CORTEX-3.0 -- src/orchestrators/base_incremental_orchestrator.py
git checkout origin/CORTEX-3.0 -- tests/test_base_incremental_orchestrator.py
```

### Error: "Layer 3 (TDD Orchestrator) incomplete"

**Cause:** Missing phases or methods in `tdd_orchestrator.py`

**Fix:**
```bash
# Restore from Phase 3 implementation
git checkout origin/CORTEX-3.0 -- src/orchestrators/tdd_orchestrator.py
git checkout origin/CORTEX-3.0 -- tests/test_tdd_orchestrator.py
```

### Error: "Tests failing"

**Cause:** Test suite has failures

**Fix:**
```bash
# Run specific test suite to see failures
pytest tests/test_response_monitor.py -v
pytest tests/test_base_incremental_orchestrator.py -v
pytest tests/test_tdd_orchestrator.py -v

# Fix failing tests before deployment
```

---

## Gate Execution Time

| Gate | Avg Time | Max Time | Notes |
|------|----------|----------|-------|
| 1-16 | 0.1-5s | 10s | File checks, pattern matching |
| **17** | **30-90s** | **120s** | **Runs 70 tests via pytest** |

**Total Deployment Validation:** ~2-3 minutes

---

## Implementation Files

**Gate Logic:** `src/deployment/deployment_gates.py`
- Line 186-199: Gate 17 execution
- Line 2050-2295: `_validate_incremental_work_system()` method

**Validated Files:**
1. `src/utils/response_monitor.py` (Layer 1)
2. `src/orchestrators/base_incremental_orchestrator.py` (Layer 2)
3. `src/orchestrators/tdd_orchestrator.py` (Layer 3)

**Test Files:**
1. `tests/test_response_monitor.py` (23 tests)
2. `tests/test_base_incremental_orchestrator.py` (23 tests)
3. `tests/test_tdd_orchestrator.py` (24 tests)

**Documentation:**
- `cortex-brain/documents/reports/gate-17-implementation-complete.md` - Implementation details
- `cortex-brain/documents/reports/phase-3-tdd-orchestrator-complete.md` - Phase 3 report
- `cortex-brain/documents/analysis/incremental-work-management-analysis.md` - Architecture

---

## FAQ

**Q: Why is Gate 17 ERROR severity instead of WARNING?**

A: The incremental work management system is **critical infrastructure**. Without it, CORTEX will repeatedly hit length limit errors during TDD workflows, feature planning, and code reviews. This degrades user experience and makes CORTEX unusable for complex tasks.

**Q: Can I skip Gate 17 for testing?**

A: No. Gate 17 runs as part of `validate_all_gates()` and cannot be individually disabled. If you need to test deployment without the incremental system, you must implement stub versions of all 3 layers.

**Q: What if I add a 4th layer (e.g., Planning Orchestrator)?**

A: Update Gate 17 to validate the new layer:
1. Add Layer 4 file existence check
2. Add Layer 4 component validation
3. Add Layer 4 test execution
4. Update success message to show 4 layers

**Q: How often should Gate 17 run?**

A: Gate 17 runs automatically during:
- Every deployment (`deploy cortex` command)
- CI/CD pipeline runs
- Pre-release validation

For development, run manually via `python scripts/deploy_cortex.py --dry-run`

---

**Status:** ✅ Gate 17 operational and enforcing incremental work management system presence in all CORTEX deployments.
