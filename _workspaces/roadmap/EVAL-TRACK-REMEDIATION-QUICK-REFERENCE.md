# Eval Track Remediation - Quick Reference

**Date:** 2026-01-22  
**Status:** PLAN COMPLETE  
**Format:** Quick lookup card

---

## Remediation At A Glance

| Phase | Issue(s) | Priority | Effort | Blocker | Decision |
|-------|----------|----------|--------|---------|----------|
| ✅ EVAL-001 | F001-F003 (test validity) | P0 | 2 hrs | — | Test validity assessed |
| AUDIT-001 | F004 (exports unverified) | P0 | 30 min | YES | Collection errors = 0? |
| AUDIT-002 | F005 (PHASE-E unverified) | P0 | 2-3 hrs | YES | ≥90% real implementations? |
| AUDIT-003 | F006 (imports undefined) | P1 | 2-4 hrs | NO | Remediation priority list? |
| AUDIT-004 | F008-F009 (governance) | P1 | 1-2 hrs | NO | ≥95% compliance? |
| CLEANUP-001 | F007 (duplicates) | P2 | 2-3 hrs | NO | Roadmap consolidated? |
| AUDIT-005 | F010 (git checkpoints) | P2 | 1 hr | NO | Commits documented? |
| AUDIT-006 | F011 (docstrings) | P2 | 1-2 hrs | NO | ≥95% docstrings? |
| AUDIT-007 | F012 (coverage) | P2 | 1 hr | NO | ≥85% coverage? |

---

## Critical Path (Must Do First)

```
START
  ↓
AUDIT-001 (30 min)
  ├─ Run: pytest --collect-only
  ├─ Expected: 0 ImportError
  └─ Decision: Proceed or fix exports?
  ↓
AUDIT-002 (2-3 hrs) ⚠️ CRITICAL
  ├─ Sample: 25 of 125 modules
  ├─ Check: Real code or stubs?
  ├─ Test: 100% passing?
  └─ Decision Tree:
     ├─ ≥90% real? → APPROVED (next: KG phases) ✅
     ├─ 70-89% real? → CONDITIONAL (remediate) ⚠️
     └─ <70% real? → BLOCKED (emergency) ❌
  ↓
[Proceed based on AUDIT-002 result]
```

---

## Phase Dependencies

```
AUDIT-001 ──→ AUDIT-002 ──→ KG PHASES (if approved)
              ↓
              AUDIT-003 ────→ (parallel)
              ↓
              AUDIT-004 ────→ (parallel)

CLEANUP-001 ──→ AUDIT-005 ──→ AUDIT-006 ──→ AUDIT-007
(independent)   (parallel)     (parallel)     (parallel)
```

---

## Decision Tree Summary

### AUDIT-001: Test Collection
```
if errors = 0: ✅ PASS → Continue
else: ❌ FAIL → Fix exports (+2-4 hrs)
```

### AUDIT-002: PHASE-E Readiness
```
if real_impl ≥ 90% AND tests ≥ 98%: ✅ APPROVED
  → Proceed with KG phases immediately

elif real_impl 70-89% AND tests ≥ 95%: ⚠️ CONDITIONAL
  → Create remediation AC (+5-7 days)

else: ❌ BLOCKED
  → Reclassify PHASE-E as IN_PROGRESS (+7-14 days)
```

### AUDIT-003: Import Audit
```
if critical_imports = 0: ✅ CLEAR
  → Update test threshold, proceed

elif critical_imports 1-10: ⚠️ MINOR
  → Quick fix task (+2-4 hrs)

else: ❌ MAJOR
  → Comprehensive remediation (+2-4 days)
```

### AUDIT-004: Governance Compliance
```
if compliance ≥ 95%: ✅ APPROVED
  → Proceed with confidence

elif compliance 85-94%: ⚠️ CONDITIONAL
  → Create minor fix AC (+2-3 hrs)

else: ❌ REMEDIATION
  → Comprehensive fix phase (+1-2 days)
```

---

## Timeline Summary

| Phase | Effort | Parallel | Days | Cumulative |
|-------|--------|----------|------|-----------|
| AUDIT-001 | 30 min | — | 1 | 1 |
| AUDIT-002 | 2-3 hrs | — | 1 | 2 |
| AUDIT-003 | 2-4 hrs | YES | 1 | 2 |
| AUDIT-004 | 1-2 hrs | YES | 1 | 2 |
| CLEANUP-001 | 2-3 hrs | YES | 1 | 2 |
| AUDIT-005 | 1 hr | YES | 1 | 2 |
| AUDIT-006 | 1-2 hrs | YES | 1 | 2 |
| AUDIT-007 | 1 hr | YES | 1 | 2 |
| **TOTAL** | **12-18 hrs** | — | **~6 days** | — |
| KG Phases | 11-16 days | (optional) | 11-16 | 17-22 |

---

## Acceptance Criteria (All Phases)

### AUDIT-001
- [ ] Test collection completes without ImportError
- [ ] 0 collection errors documented
- [ ] Audit trail updated with timestamp

### AUDIT-002
- [ ] ≥90% of sampled modules have real implementations
- [ ] ≥98% test pass rate on samples
- [ ] ≥50% coverage on sampled modules
- [ ] Clear decision gate documented

### AUDIT-003
- [ ] 105 files categorized with rationale
- [ ] Remediation priority list created
- [ ] Test threshold updated
- [ ] Strategy documented

### AUDIT-004
- [ ] Type hints compliance ≥95%
- [ ] Docstring compliance ≥95%
- [ ] TDD workflow ≥80% verified
- [ ] Violations (if any) with remediation plan

### CLEANUP-001
- [ ] All duplicates consolidated
- [ ] Orphaned entries archived
- [ ] File remains valid YAML
- [ ] All phase IDs unique

### AUDIT-005
- [ ] All phase completions have git commits
- [ ] Commits follow standard format
- [ ] Convention documented
- [ ] Commit hashes recorded

### AUDIT-006
- [ ] Compliance rate calculated
- [ ] Violations documented with locations
- [ ] Remediation plan (if needed) created
- [ ] Extrapolation to full codebase provided

### AUDIT-007
- [ ] Coverage % documented (overall + by module)
- [ ] Coverage report generated and archived
- [ ] Baseline recorded in cortex-impl-map.yaml
- [ ] Gaps identified with specific files

---

## Success Metrics

**Track-Level Success:**
- [ ] AUDIT-001: Test collection = 0 errors
- [ ] AUDIT-002: ≥90% real implementations
- [ ] AUDIT-003: Import remediation list
- [ ] AUDIT-004: ≥95% governance compliance
- [ ] All cleanup phases complete

**Production Readiness:**
- [ ] All blocking gates PASSED
- [ ] No CRITICAL findings remain
- [ ] Coverage ≥85%
- [ ] Governance compliance ≥95%
- [ ] Git checkpoints in place

---

## Files to Review/Create

### Documents Created (Review These)
- ✅ `EVAL-TRACK-REMEDIATION-PLAN-20260122.md` (40 pages, detailed)
- ✅ `EVAL-TRACK-REMEDIATION-INTEGRATION.md` (YAML specifications)
- ✅ `EVAL-TRACK-REMEDIATION-SUMMARY.md` (executive summary)
- ✅ `EVAL-TRACK-REMEDIATION-QUICK-REFERENCE.md` (this file)

### Documents to Reference
- 📄 `docs/REVIEW-CORTEX-20260122.yaml` (findings F004-F012)
- 📄 `docs/REVIEW-CORTEX-20260122-SUMMARY.md` (review summary)
- 📄 `REVIEW-FINDINGS-CAPTURE-STATUS.md` (what's been captured)

### Action Items
1. ⏳ Review remediation plan
2. ⏳ Integrate 8 phases into cortex-impl-map.yaml
3. ⏳ Execute AUDIT-001 (tomorrow)
4. ⏳ Execute AUDIT-002 (day 2)
5. ⏳ Proceed based on results

---

## Command Reference

### Test Collection Verify (AUDIT-001)
```bash
pytest tests/ --collect-only -q 2>&1 | grep -i "error"
# Expected output: (empty - no errors)
```

### PHASE-E Module Verification (AUDIT-002)
```bash
# Sample check
pytest tests/test_*.py --collect-only -q
pytest tests/test_*.py -v --tb=no -q
pytest tests/ --cov=cortex --cov-report=term-missing
```

### Coverage Analysis (AUDIT-007)
```bash
pytest tests/ --cov=cortex --cov-report=term-missing --cov-report=html
```

### YAML Validation (CLEANUP-001)
```bash
python -c "import yaml; yaml.safe_load(open('cortex-impl-map.yaml'))"
```

### Docstring Check (AUDIT-006)
```bash
pylint cortex/core/ cortex/orchestrators/ cortex/mcp/ \
  --disable=all --enable=missing-docstring
```

---

## Approval Sign-Off

**Remediation Plan Status:** ✅ COMPLETE & READY FOR IMPLEMENTATION

| Item | Owner | Status |
|------|-------|--------|
| Plan review | Technical lead | ⏳ PENDING |
| Approval | Project manager | ⏳ PENDING |
| Roadmap integration | Engineer | ⏳ PENDING |
| Execution start | Engineer | ⏳ PENDING |

---

## Contact & Questions

**Plan Authority:** REVIEW-CORTEX-20260122.yaml (Findings F004-F012)

**Documents:**
- Questions about findings? → See `docs/REVIEW-CORTEX-20260122.yaml`
- Questions about plan? → See `EVAL-TRACK-REMEDIATION-PLAN-20260122.md`
- Questions about integration? → See `EVAL-TRACK-REMEDIATION-INTEGRATION.md`
- Questions about status? → See `REVIEW-FINDINGS-CAPTURE-STATUS.md`

