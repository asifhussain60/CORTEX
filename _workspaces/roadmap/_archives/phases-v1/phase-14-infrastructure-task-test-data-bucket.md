# Phase 14: Infrastructure Task - Test Data Bucket Implementation

**Title:** PM-014-01: Test Data Bucket Implementation in Governance Database  
**Phase:** PHASE-14-PRODUCTION-ROLLOUT (Infrastructure Task)  
**Prerequisite:** After audit trail cleanup (AUDIT-REMEDIATION-2026-01-15 complete)  
**Estimated Time:** 1 hour  
**Dependencies:** None (parallel track)  
**Priority:** LOW (Enhancement, not blocking)

---

## Context

During AUDIT-REMEDIATION-2026-01-15, we identified test infrastructure that needs better organization:

- **141 test AC-IDs** with ~1,197 audit entries (BRITTLE-*, DASH-*, ACC-*, CI7-*, etc.)
- **Intentional hash chain violations** (test harness data, validates error detection)
- **Currently mixed** with production audit logs
- **Need better separation** for Phase 14 and future phases

We deliberately kept this test data because:
1. ✅ **Regression Testing:** Validates our hash chain validation works
2. ✅ **Error Detection:** Tests that we properly catch and report hash violations
3. ✅ **Infrastructure:** Provides test harness data for future test frameworks

This task implements proper organization.

---

## Acceptance Criteria

### AC-PM-014-01-01: Test Data Bucket Table Created

**Criterion:** `test_data_bucket` table exists in governance.db with proper schema

**What Proves It:**
- Table exists: `SELECT COUNT(*) FROM test_data_bucket;` returns 0 (empty to start)
- Schema has columns: `ac_id_pattern`, `description`, `purpose`, `created_at`
- Table can be queried from all test code

**How to Test:**
```bash
# Connect to database
sqlite3 cortex_brain/state/governance.db

# Verify schema
.schema test_data_bucket

# Verify columns exist
SELECT sql FROM sqlite_master WHERE type='table' AND name='test_data_bucket';

# Should show:
# CREATE TABLE test_data_bucket (
#   id INTEGER PRIMARY KEY AUTOINCREMENT,
#   ac_id_pattern TEXT NOT NULL,
#   description TEXT,
#   purpose TEXT,
#   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
```

**Audit Evidence:**
```yaml
operation: AC_EXECUTE
should_log:
  - "database_schema: test_data_bucket_created=true"
  - "table_schema: columns=5, primary_key=id, indexed=ac_id_pattern"
  - "verification: query_test_data_bucket_returns_empty=true"
```

---

### AC-PM-014-01-02: Populate Test Data Bucket with Known Patterns

**Criterion:** All test AC-ID patterns registered in test_data_bucket

**What Proves It:**
- 9+ test patterns are registered with descriptions
- Each pattern has `purpose` field (regression, harness, validation, etc.)
- Query returns all patterns: `SELECT COUNT(*) FROM test_data_bucket;` ≥ 9

**How to Test:**
```bash
# Query all patterns
SELECT ac_id_pattern, purpose, description FROM test_data_bucket ORDER BY ac_id_pattern;

# Should return patterns like:
# BRITTLE-*     | regression_testing | "Test brittle component fixes"
# DASH-*        | regression_testing | "Dashboard regression tests"
# ACC-*         | test_harness       | "Acceptance criteria harness"
# CI7-*         | ci_testing         | "CI/CD integration testing"
# ... etc
```

**Audit Evidence:**
```yaml
operation: AC_EXECUTE
should_log:
  - "test_data_registration: patterns_registered=9"
  - "pattern_details: purpose=regression_testing, count=3"
  - "pattern_details: purpose=test_harness, count=4"
  - "pattern_details: purpose=ci_testing, count=2"
  - "verification: all_patterns_queryable=true"
```

---

### AC-PM-014-01-03: Create Filtered Query Views

**Criterion:** Database views for clean production-only and test-only queries

**What Proves It:**
- View `audit_log_production` shows only real phase ACs (AR-*, FR-*, BR-*, etc.)
- View `audit_log_test_artifacts` shows only test data
- Both views work correctly and return correct data

**How to Test:**
```bash
# Production-only view (should return ~2,820 entries from 100+ real ACs)
SELECT COUNT(*) FROM audit_log_production;

# Should return real AC-IDs only
SELECT DISTINCT ac_id FROM audit_log_production 
WHERE ac_id LIKE 'AR-%' OR ac_id LIKE 'FR-%'
LIMIT 10;

# Test-only view (should return ~1,197 entries from 141 test ACs)
SELECT COUNT(*) FROM audit_log_test_artifacts;

# Should return test patterns only
SELECT DISTINCT ac_id FROM audit_log_test_artifacts
WHERE ac_id LIKE 'BRITTLE-%' OR ac_id LIKE 'DASH-%'
LIMIT 10;
```

**Audit Evidence:**
```yaml
operation: AC_EXECUTE
should_log:
  - "view_creation: audit_log_production=created"
  - "view_query_test: production_count=2820, test_count=1197"
  - "view_verification: filters_work_correctly=true"
  - "view_performance: query_time<100ms"
```

---

### AC-PM-014-01-04: Update Compliance Tests to Use Filtered View

**Criterion:** test_audit_trail_integrity.py updated to query production-only view

**What Proves It:**
- Tests use `FROM audit_log_production` (not `FROM audit_log`)
- Test failures reduced (hash chain validation no longer sees test data issues)
- All 4 core validation tests pass: 4/4 ✅

**How to Test:**
```bash
# Run validation tests with new view
pytest tests/integration/test_audit_trail_integrity.py::TestAuditTrailIntegrity -v

# Should show improved results:
# test_all_ac_ids_have_complete_lifecycle PASSED ✅
# test_lifecycle_events_are_chronologically_ordered PASSED ✅
# test_hash_chain_integrity PASSED ✅ (now only validates real data)
# test_no_fake_retroactive_entries PASSED ✅

# Should still show test failures for test data:
# (These failures are now EXPECTED - testing test data itself)
```

**Audit Evidence:**
```yaml
operation: AC_EXECUTE
should_log:
  - "test_update: files_modified=1 (test_audit_trail_integrity.py)"
  - "test_query_migration: old_query=FROM audit_log, new_query=FROM audit_log_production"
  - "test_results: core_tests_passing=4/4"
  - "test_results: test_data_tests_showing_expected_failures=yes"
  - "regression_check: existing_test_passing_count=2812, regression_detected=no"
```

---

### AC-PM-014-01-05: Documentation Update

**Criterion:** Developer documentation explains test data organization

**What Proves It:**
- File created: `.github/docs/test-data-bucket-guide.md`
- Explains test data patterns and purposes
- Shows how to query production-only data
- Explains how to add new test patterns

**How to Test:**
```bash
# File exists
ls -lh .github/docs/test-data-bucket-guide.md

# Contains required sections
grep -E "^## |### " .github/docs/test-data-bucket-guide.md | head -15

# Should show sections like:
# ## Overview
# ## Test Data Patterns
# ## Querying Test Data
# ## Adding New Patterns
# ## Production-Only Queries
```

**Audit Evidence:**
```yaml
operation: AC_EXECUTE
should_log:
  - "documentation_created: file=test-data-bucket-guide.md"
  - "documentation_sections: overview, patterns, queries, examples=4"
  - "verification: file_readable=true, complete=true"
```

---

## Implementation Plan

### Step 1: Create Table (5 min)
```sql
CREATE TABLE test_data_bucket (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ac_id_pattern TEXT NOT NULL UNIQUE,
  description TEXT,
  purpose TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT valid_pattern CHECK(ac_id_pattern LIKE '%-%' OR ac_id_pattern LIKE '%*')
);

CREATE INDEX idx_test_data_bucket_pattern ON test_data_bucket(ac_id_pattern);
```

### Step 2: Populate Patterns (10 min)
```sql
INSERT INTO test_data_bucket (ac_id_pattern, description, purpose) VALUES
('BRITTLE-%', 'Brittle component fixes', 'regression_testing'),
('DASH-%', 'Dashboard regression tests', 'regression_testing'),
('ACC-%', 'Acceptance criteria harness', 'test_harness'),
('CI7-%', 'CI/CD integration', 'ci_testing'),
('ACC-%', 'Automation control tests', 'test_harness'),
('ENH-%', 'Enhancement AC-IDs', 'feature_testing'),
('INT-%', 'Integration testing', 'integration'),
('NFR-%', 'Non-functional requirements', 'nfr_testing'),
('P-%', 'Parallel phase tests', 'parallel_testing'),
('REL-%', 'Release testing', 'release_testing'),
('S-%', 'Scheduler tests', 'scheduler_testing'),
('SC-%', 'Security control tests', 'security_testing'),
('PH-%', 'Phase health checks', 'health_testing'),
('PHASE8-%', 'Phase 8 tests', 'phase_testing');
```

### Step 3: Create Views (10 min)
```sql
-- Production-only audit log
CREATE VIEW audit_log_production AS
SELECT * FROM audit_log
WHERE ac_id IS NOT NULL
  AND ac_id NOT IN (SELECT ac_id_pattern FROM test_data_bucket)
  AND NOT EXISTS (
    SELECT 1 FROM test_data_bucket tb
    WHERE audit_log.ac_id LIKE REPLACE(tb.ac_id_pattern, '*', '%')
  );

-- Test-only audit log
CREATE VIEW audit_log_test_artifacts AS
SELECT * FROM audit_log
WHERE ac_id IS NOT NULL
  AND (
    EXISTS (
      SELECT 1 FROM test_data_bucket tb
      WHERE audit_log.ac_id LIKE REPLACE(tb.ac_id_pattern, '*', '%')
    )
  );
```

### Step 4: Update Tests (20 min)
- Update `test_audit_trail_integrity.py` to use `audit_log_production`
- Keep separate test for `audit_log_test_artifacts` (validation that error detection works)
- Verify all tests still pass

### Step 5: Document (15 min)
- Create `.github/docs/test-data-bucket-guide.md`
- Add examples of querying each view
- Document how to add new test patterns

---

## Success Criteria

✅ All acceptance criteria met  
✅ Tests pass with production-only queries  
✅ Test data properly isolated  
✅ Documentation complete  
✅ Zero production impact  
✅ Ready for future phases  

---

## Notes

**Why Now (Phase 14):**
- Infrastructure work that supports Phase 14+ testing
- Not critical for OTEL integration (OB-002-*) but improves testing infrastructure
- Can be done in parallel with OTEL work
- Sets foundation for future phases (Phase 15, 16)

**Why Not Before:**
- Audit trail reconstruction (Phases 1-13) was priority
- Test data was useful for validation during reconstruction
- Better to refactor after main audit trail work is stable

**Reusability:**
- Pattern can be extended for Phase 15, 16
- Documentation serves as template for other test harness improvements
- Views are reusable across all test suites

---

## Related Documentation

- `.github/docs/TEST-DATA-ARTIFACTS-DECISION.md` - Strategic decision document
- `.github/docs/AUDIT-TRAIL-RECONSTRUCTION-COMPLETION-REPORT.md` - Context from cleanup
- `tests/integration/test_audit_trail_integrity.py` - Validation framework

---

## Estimated Effort

| Task | Time |
|------|------|
| Create table | 5 min |
| Populate patterns | 10 min |
| Create views | 10 min |
| Update tests | 20 min |
| Documentation | 15 min |
| **Total** | **~1 hour** |

Can be completed in parallel with OTEL implementation or as a separate enhancement during Phase 14.
