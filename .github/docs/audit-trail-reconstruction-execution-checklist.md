# AUDIT TRAIL RECONSTRUCTION - EXECUTION CHECKLIST

**Status:** AWAITING APPROVAL  
**Scope:** Complete rebuild of Phases 1-13 audit trails with evidence-based validation  
**Est. Time:** 20-40 hours  
**Rollback Available:** Yes (`pre-audit-remediation-2026-01-15` tag)

---

## Pre-Execution Decision Points

### Decision 1: Database Cleanup
**Question:** Delete all audit logs for Phases 1-13 (176 ACs)?

- [ ] YES - Start fresh with only real workflow evidence
- [ ] NO - Keep current logs but improve validation going forward

**Impact if YES:**
- Clean database, zero ambiguity about what's real vs. fake
- Must re-run tests to regenerate audit trail
- More work now, but perfect foundation for Phase 14+

**Impact if NO:**
- Keep imperfect audit trail from current state
- Faster (no rebuild), but mixed real + fake entries remain
- Phase 14 will inherit uncertainty

### Decision 2: Phase YAML Enhancement
**Question:** Update all 13 phase YAML files with detailed acceptance criteria?

- [ ] YES - Full transformation to evidence-based model
- [ ] PARTIAL - Just AR-* and FR-* phases (most critical)
- [ ] NO - Leave as-is, only improve tests

**Impact if YES:**
- Clear documentation of what "completion" means
- Test files know exactly what to validate and log
- 13 phase files × 6-12 ACs/phase = ~100+ updates
- Est. 8 hours work

**Impact if PARTIAL:**
- Cover foundational requirements (governance, audit)
- Less work (~4 hours)
- Later phases (11-13) less detailed

**Impact if NO:**
- Minimal documentation changes
- Tests still log, but phase files vague
- Faster initial rebuild (~4 hours less)

### Decision 3: Test Re-run Approach
**Question:** How to re-run 500+ tests with audit logging?

- [ ] ALL-AT-ONCE - Run full test suite in parallel with logging enabled
  - Fastest (1-2 hours)
  - Risk: If one fails, hard to debug
  - Best if: Tests are all passing

- [ ] PHASE-BY-PHASE - Run Phase 1, validate, then Phase 2, etc.
  - Slower (8 hours)
  - Safer: Can fix issues phase-by-phase
  - Best if: Want to catch and fix problems incrementally

- [ ] AC-BY-AC - For each AC, run its specific tests, validate audit trail
  - Slowest (16 hours)
  - Safest: Can validate evidence for each AC individually
  - Best if: Need maximum visibility into what's happening

---

## Execution Steps (IF APPROVED)

### Step 1: Pre-Flight Checks (30 min)
- [ ] Current branch clean? (No uncommitted changes)
- [ ] Latest commit is `ca2d2d493`?
- [ ] Backup created: `governance.db.backup.2026-01-15` exists
- [ ] Tag exists: `pre-audit-remediation-2026-01-15`
- [ ] Test suite runs successfully: `pytest tests/ -q` passes

### Step 2: Database Cleanup (15 min)
```bash
# Delete audit logs for all Phases 1-13
sqlite3 cortex-brain/state/governance.db << 'EOF'
BEGIN TRANSACTION;

-- Keep only Phase-10 (locked) and non-AC entries
DELETE FROM audit_log 
WHERE ac_id IS NOT NULL
  AND ac_id NOT LIKE 'EX-%';  -- EX = PHASE-10, keep these

-- Verify deletion
SELECT COUNT(*) as remaining_ac_entries FROM audit_log WHERE ac_id IS NOT NULL;

COMMIT;
EOF
```

Result: Clean database with only PHASE-10 entries

### Step 3: Update Phase YAML Files (2-8 hours)
**IF DECISION 2 = YES:**
- [ ] Update phase-01.yaml (expand AR-*, FR-* sections)
- [ ] Update phase-02.yaml (expand OR-* sections)
- [ ] ... (repeat for all 13 phases)
- [ ] Validate YAML syntax: `yamllint phases/*.yaml`

**IF DECISION 2 = PARTIAL:**
- [ ] Update only phase-01.yaml through phase-04.yaml
- [ ] Leave phase-07 through phase-13 as-is

**IF DECISION 2 = NO:**
- [ ] Skip this step entirely

### Step 4: Update Test Infrastructure (1 hour)
- [ ] Review `AuditLogger` class in test utils
- [ ] Verify all phase tests use `@audit_mode('STRICT')` decorator
- [ ] Verify test base class calls `logger.checkpoint()` for each criterion
- [ ] Test that test framework logs AC_START before first test, AC_COMPLETE after last

### Step 5: Re-run Tests with Audit Logging (1-8 hours)

**IF DECISION 3 = ALL-AT-ONCE:**
```bash
pytest tests/unit/ tests/integration/ -n auto --audit-mode STRICT -v
# Parallel execution, all tests log to audit_log
```

**IF DECISION 3 = PHASE-BY-PHASE:**
```bash
# For each phase:
pytest tests/unit/test_ar*.py --audit-mode STRICT -v
# Validate audit trail for phase
pytest tests/integration/test_audit_trail_integrity.py::TestAuditTrailIntegrity::test_all_ac_ids_have_complete_lifecycle -v
# Move to next phase if passed
```

**IF DECISION 3 = AC-BY-AC:**
```bash
# For each AC:
pytest tests/unit/test_ar_*.py::*AR_002* --audit-mode STRICT -v
# Validate AC-AR-002-01, AR-002-02, AR-002-03 individually
python scripts/validate_ac_audit_trail.py AR-002-01
# If not good, fix test and re-run
```

### Step 6: Validation (1-2 hours)
- [ ] Run compliance test: `pytest tests/integration/test_audit_trail_integrity.py -v`
- [ ] Verify: All 176 ACs have AC_START, AC_EXECUTE(N), AC_COMPLETE
- [ ] Verify: Timestamps show real execution (not backdated)
- [ ] Verify: Metadata contains evidence (not just claims)
- [ ] Verify: Hash chains unbroken
- [ ] Generate report: `pytest tests/integration/test_audit_trail_integrity.py::TestAuditRemediationProgress -v`

### Step 7: Phase-Tracker Update (30 min)
- [ ] Update `cortex-master.yaml` phase_tracker:
  ```yaml
  PHASE-01:
    audit_verification:
      verified: true
      entry_count: 108  # 36 ACs × 3 events
      hash_chain_valid: true
      remediation_required: false
    locked: true
  ```
- [ ] Repeat for all phases 1-13

### Step 8: Git Commit (15 min)
- [ ] Commit phase YAML updates: `git add phases/*.yaml && git commit -m "phases 1-13: update acceptance criteria with evidence-based validation"`
- [ ] Commit database: `git add cortex-brain/state/governance.db && git commit -m "governance.db: rebuilt audit trail with real workflow evidence"`
- [ ] Commit phase-tracker: `git add .github/roadmap/cortex-master.yaml && git commit -m "phase-tracker: all phases 1-13 verified and locked"`
- [ ] Tag completion: `git tag -a phase-13-audit-rebuild-complete -m "Audit trail reconstruction complete: all 176 ACs verified"`

### Step 9: Final Verification (30 min)
- [ ] Run full test suite: `pytest tests/ -q` (should pass)
- [ ] Run audit trail tests: `pytest tests/integration/test_audit_trail_integrity.py -v` (should pass)
- [ ] Verify git log shows clean commit history
- [ ] Verify all phases locked in cortex-master.yaml

### Step 10: Documentation Update (30 min)
- [ ] Update `.github/docs/current-status.md` with new state
- [ ] Update `audit-remediation-2026-01-15-findings.md` with completion info
- [ ] Archive old findings to `.github/evidence/`

---

## Abort Conditions

**Stop and rollback if:**

1. Tests fail during re-run and can't be quickly fixed
   - Rollback: `git reset --hard pre-audit-remediation-2026-01-15`
   - Restore DB: `cp governance.db.backup.2026-01-15 governance.db`

2. YAML updates introduce syntax errors
   - Rollback: `git checkout phases/`
   - Re-apply with validation

3. Hash chain breaks during rebuild
   - Indicates database corruption
   - Rollback: `cp governance.db.backup.2026-01-15 governance.db`

4. More than 10 tests fail
   - Indicates systematic problem
   - Abort rebuild, diagnose root cause

---

## Success Indicators

After execution complete:
- ✅ All 176 ACs have 3+ audit entries (START, EXECUTE, COMPLETE)
- ✅ `test_audit_trail_integrity.py` shows 100% compliance
- ✅ Phase-tracker shows all phases `verified: true, locked: true`
- ✅ Git log shows clean rebuild commits
- ✅ Database size reasonable (~10-50MB for audit trail)
- ✅ All tests pass: `pytest tests/ -q` → OK

---

## Approval Checklist

**I approve this audit trail reconstruction plan:**

- [ ] Understand the scope (delete logs, rebuild with evidence)
- [ ] Accept 20-40 hour time commitment
- [ ] Understand risks and rollback procedures
- [ ] Approve Decision 1: Database cleanup (YES/NO)
- [ ] Approve Decision 2: Phase YAML enhancement (YES/PARTIAL/NO)
- [ ] Approve Decision 3: Test re-run approach (ALL-AT-ONCE/PHASE-BY-PHASE/AC-BY-AC)
- [ ] Commit to seeing this through to completion

**Approved by:** _____________  
**Date:** _____________  
**Notes:** _____________

---

## Next Steps After Approval

1. Respond with approval and decisions (1-3 above)
2. I proceed with Step 1-10 execution
3. Real-time status updates during rebuild
4. Final validation report with compliance metrics
5. Phase 14 ready to launch with evidence-based pattern

