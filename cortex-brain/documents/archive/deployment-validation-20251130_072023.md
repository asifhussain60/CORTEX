# Deployment Validation Report

**Timestamp:** 2025-11-30 07:20:23
**Version:** 3.3.0
**Overall Status:** ❌ FAILED

## Summary

- **Total Gates:** 16
- **Passed:** 8
- **Failed:** 8
- **Errors:** 7
- **Warnings:** 1

## Gate Results

### Gate 1: Integration Scores (ERROR)

**Status:** ❌ FAILED

**Message:** No alignment report provided

### Gate 2: Test Coverage (ERROR)

**Status:** ❌ FAILED

**Message:** No pytest cache found - run tests before deployment

### Gate 3: No Mocks in Production (ERROR)

**Status:** ❌ FAILED

**Message:** Found 5 mock/stub patterns in production code

### Gate 4: Documentation Sync (WARNING)

**Status:** ✅ PASSED

**Message:** Documentation appears synchronized

### Gate 5: Version Consistency (ERROR)

**Status:** ✅ PASSED

**Message:** Version consistent: 3.4.0

### Gate 6: Template Format Validation (ERROR)

**Status:** ❌ FAILED

**Message:** Template format has 15 critical violations

### Gate 7: Git Checkpoint System (ERROR)

**Status:** ❌ FAILED

**Message:** Git Checkpoint System incomplete: 1 critical issues

### Gate 8: Swagger/OpenAPI Documentation (ERROR)

**Status:** ✅ PASSED

**Message:** Swagger/OpenAPI documentation valid (4/4 checks passed)

### Gate 9: Timeframe Estimator Module (WARNING)

**Status:** ✅ PASSED

**Message:** Timeframe Estimator fully integrated (7/7 checks passed)

### Gate 10: Production File Validation (WARNING)

**Status:** ✅ PASSED

**Message:** Production validation passed with warnings: 26 items will be excluded by deploy_cortex.py

### Gate 11: CORTEX Brain Operational (ERROR)

**Status:** ✅ PASSED

**Message:** CORTEX Brain fully operational: All 6 checks passed

### Gate 12: Next Steps Formatting (ERROR)

**Status:** ✅ PASSED

**Message:** All Next Steps sections comply with formatting rules. No violations detected.

### Gate 13: TDD Mastery Integration (ERROR)

**Status:** ❌ FAILED

**Message:** TDD Mastery integration incomplete: 1 issues. Git checkpoint system not fully wired into TDD workflow. Production deployment BLOCKED. Issues: tdd-mastery-guide.md doesn't document git checkpoint integration

### Gate 14: User Feature Packaging (ERROR)

**Status:** ✅ PASSED

**Message:** All user features packaged successfully. 5 features validated.

### Gate 15: Admin/User Separation (ERROR)

**Status:** ❌ FAILED

**Message:** Deployment manifest not found. Cannot validate admin/user separation.

### Gate 16: Align EPM User-Only (WARNING)

**Status:** ❌ FAILED

**Message:** Setup EPM exposes admin operations: deploy. EPM should only show user-facing operations. WARNING: Deployment allowed but admin operations should be hidden from EPM.

## Blocking Errors

- No alignment report provided
- No pytest cache found - run tests before deployment
- Found 5 mock/stub patterns in production code
- Template format has 15 critical violations
- Git Checkpoint System incomplete: 1 critical issues
- TDD Mastery integration incomplete: 1 issues. Git checkpoint system not fully wired into TDD workflow. Production deployment BLOCKED. Issues: tdd-mastery-guide.md doesn't document git checkpoint integration
- Deployment manifest not found. Cannot validate admin/user separation.

## Warnings (Non-Blocking)

- Setup EPM exposes admin operations: deploy. EPM should only show user-facing operations. WARNING: Deployment allowed but admin operations should be hidden from EPM.

