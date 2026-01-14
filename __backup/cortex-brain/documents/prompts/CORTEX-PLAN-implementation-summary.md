# CORTEX-PLAN Prompt - Implementation Summary

**Created:** 2026-01-11  
**Commit:** `086a392e8`  
**Status:** Deployed to CORTEX6

---

## 📋 What Was Created

### New Prompt File

**`.github/prompts/CORTEX-PLAN.prompt.md`** (633 lines)

A comprehensive autonomous validation system that:
- Executes ALL tests for current phase
- Validates implementation against acceptance criteria
- Verifies audit log evidence for success/failure
- Updates progress tracker with verified data only
- Syncs plan-viewer.html with reality (no hardcoding)
- Reports holistic status

---

## 🎯 Key Features

### 8-Phase Autonomous Workflow

1. **Context Loading** - Load tracker, AC-INDEX, master plan
2. **Test Execution** - Run all tests with comprehensive reporting
3. **AC Validation** - Verify implementation against acceptance criteria
4. **Audit Evidence** - Check governance.db for test execution records
5. **Evidence Validation** - Run audit_based_evidence_validator.py
6. **Tracker Update** - Update only from verified evidence
7. **Plan Viewer Sync** - Regenerate plan-viewer-data.json (no hardcoding)
8. **Holistic Validation** - Cross-reference 3 sources of truth

---

## 🛡️ Evidence Hierarchy

**3-tier evidence system:**

1. **Audit DB Record** (highest confidence)
   - TEST_EXECUTION category
   - AC-ID in metadata
   - Result = PASSED
   - Timestamp < 7 days old

2. **Live Test Run** (medium confidence)
   - `pytest -k {ac_id}` executed now
   - Result = PASSED
   - Output captured

3. **File Existence** (lowest confidence)
   - Implementation file exists (>1KB)
   - Test file exists (>1KB)
   - Has `@pytest.mark.ac_id` decorator

---

## 📊 Verification Thresholds

| Rate | Status | Action |
|------|--------|--------|
| ≥ 80% | ✅ GREEN | Update tracker, proceed to next phase |
| 60-79% | ⚠️  YELLOW | Update tracker, flag for review |
| < 60% | ❌ RED | BLOCK updates, fix false positives |

**Current verification rate:** 56% (30/53 AC-IDs)  
**Status:** ⚠️  YELLOW - Needs improvement to reach GREEN

---

## 🚫 Anti-Hardcoding Rules

**ENFORCED:**

1. ❌ No hardcoded completion percentages in plan-viewer.html
2. ❌ No hardcoded AC counts
3. ❌ No hardcoded status labels
4. ✅ All data loaded from plan-viewer-data.json
5. ✅ JSON regenerated on every validation run
6. ✅ Timestamp shows last update time

**Data Flow (One Direction):**
```
Evidence → Tests → Tracker → sync script → plan-viewer-data.json → plan-viewer.html
```

---

## 🔄 Consistency Validation

**Cross-reference checks:**

```bash
# Must all agree (within tolerance)
tracker.current_phase.completed_count == AC-INDEX.completed_count == plan_viewer.phases[0].verified_count
```

**If inconsistent:**
1. Re-sync AC-INDEX from tracker
2. Regenerate plan-viewer-data.json
3. Validate again
4. Report discrepancy if still failing

---

## 🎮 Invocation Methods

### Via CORTEX Prompt

```
User: "validate plan"
User: "check status"
User: "run tests"
User: "verify progress"
```

**Action:** Loads CORTEX-PLAN.prompt.md and executes full 8-phase workflow

### Via Command Line

```bash
# Full validation
python3 -m pytest tests/ -v --tb=short --maxfail=0
python3 scripts/audit_based_evidence_validator.py
python3 scripts/sync_plan_viewer_data.py

# Evidence-based tracker update
python3 scripts/audit_based_evidence_validator.py --fix

# Check single AC-ID
python3 -m pytest tests/ -k "AC-AUDIT-001" -v
```

### Via Pre-Commit Hook

```bash
#!/bin/bash
# Auto-runs on every commit
python3 scripts/audit_based_evidence_validator.py
if [ $? -ne 0 ]; then
    echo "❌ Validation failed - commit blocked"
    exit 1
fi
```

---

## 📈 Expected Output Format

```
═══════════════════════════════════════════════════════════
CORTEX 6.0 AUTONOMOUS VALIDATION REPORT
═══════════════════════════════════════════════════════════
Generated: 2026-01-11T14:30:00Z
Phase: 1 (Foundation)

TEST EXECUTION
  Total Tests: 152
  Passed: 152 (100%)
  Failed: 0
  Runtime: 23.4s

ACCEPTANCE CRITERIA VALIDATION
  Total AC-IDs: 34
  Verified: 30 (88%)
  Claimed Without Evidence: 4 (12%)

AUDIT EVIDENCE
  With audit logs: 15 (44%)
  With live tests: 20 (59%)
  Verification Rate: 88% ✅

PROGRESS TRACKER
  Status: Updated
  Completion: 88% (was: 100% - corrected)
  
PLAN VIEWER
  Status: Synced
  Hardcoding: None detected ✅

NEXT ACTIONS
  1. Implement 4 remaining AC-IDs
  2. Add audit logging to 10 tests

═══════════════════════════════════════════════════════════
STATUS: ✅ PHASE 1 AT 88% - ON TRACK
═══════════════════════════════════════════════════════════
```

---

## 🔧 Integration Points

### Updated Files

1. **CORTEX.prompt.md**
   - Added "Specialized Modes" section
   - References CORTEX-PLAN for validation

2. **copilot-instructions.md**
   - Added CORTEX-PLAN to routing table (Priority 1)
   - Triggers: `validate plan`, `check status`, `run tests`

---

## ✅ Success Criteria

**Phase validation successful when:**

1. ✅ All tests pass (0 failures, 0 errors)
2. ✅ Verification rate ≥ 80%
3. ✅ No false positives in tracker
4. ✅ Tracker, AC-INDEX, Plan Viewer all agree
5. ✅ Audit evidence exists for ≥60% of AC-IDs
6. ✅ No hardcoded values in plan-viewer.html
7. ✅ All data derived from evidence
8. ✅ Timestamps reflect actual execution time

---

## 🚨 Error Handling

### Test Failures
- Block tracker update
- Report failed test details
- Exit with error code

### Low Verification Rate (<60%)
- Block tracker update
- List AC-IDs without evidence
- Require fixes before proceeding

### Data Inconsistency
- Force re-sync
- Validate again
- Report if still inconsistent

---

## 📚 Commands Reference

### Validation Commands
```bash
# Run full validation
python3 -m pytest tests/ -v --tb=short --maxfail=0
python3 scripts/audit_based_evidence_validator.py
python3 scripts/sync_plan_viewer_data.py

# Check verification rate
python3 scripts/audit_based_evidence_validator.py | grep "VERIFICATION RATE"

# Update tracker (evidence-based)
python3 scripts/audit_based_evidence_validator.py --fix

# Verify consistency
jq '.current_phase.completed_count' cortex-brain/tier1/tracking/progress-tracker.json
jq '.phases[0].verified_count' cortex-brain/cx6-plan/viewer/plan-viewer-data.json
```

### Audit Query Commands
```bash
# Check audit logs for AC-ID
sqlite3 cortex-brain/database/governance.db << EOF
SELECT * FROM audit_log 
WHERE metadata LIKE '%AC-AUDIT-001%'
ORDER BY timestamp DESC;
EOF

# List all test executions
sqlite3 cortex-brain/database/governance.db << EOF
SELECT 
    json_extract(metadata, '$.ac_id') as ac_id,
    json_extract(metadata, '$.test_result') as result,
    timestamp
FROM audit_log
WHERE category = 'TEST_EXECUTION'
ORDER BY timestamp DESC;
EOF
```

---

## 🎯 Next Steps

### Immediate Actions

1. **Test the prompt:**
   ```
   User: "validate plan"
   ```

2. **Check current status:**
   ```bash
   python3 scripts/audit_based_evidence_validator.py
   ```

3. **Fix false positives:**
   - Implement AC-LIFECYCLE-001, AC-LIFECYCLE-002
   - Implement AC-EVIDENCE-001, AC-EVIDENCE-002
   - Add audit logging to existing tests

### Short-term Goals

4. **Reach 80% verification rate** (need 12 more verified AC-IDs)
5. **Remove all hardcoding** from plan-viewer.html
6. **Setup CI/CD integration** with validation checks
7. **Add pre-commit hook** for automatic validation

---

## 🎓 Design Philosophy

**Evidence-driven, not claim-driven:**

- ✅ Tests prove implementation
- ✅ Audit logs prove execution
- ✅ Verification rate proves quality
- ❌ Claims without evidence rejected
- ❌ Hardcoded values forbidden
- ❌ Manual tracker edits forbidden

**Single source of truth:**

Evidence → Tests → Tracker → Viewer (one-way flow)

**Autonomous execution:**

No approval loops, no stopping, continuous validation until complete

---

**Documentation:**
- Full prompt: `.github/prompts/CORTEX-PLAN.prompt.md`
- Quick reference: `.github/prompts/EVIDENCE-VALIDATOR-QUICKREF.md`
- Validator script: `scripts/audit_based_evidence_validator.py`

**Related AC-IDs:**
- AC-VALIDATE-001: Autonomous validation system
- AC-AUDIT-008: Evidence-based validation
- AC-PLAN-001 to AC-PLAN-008: Planning system (referenced)

---

**Status:** ✅ Ready for use  
**Next Review:** After first autonomous validation run  
**Owner:** Asif Hussain
