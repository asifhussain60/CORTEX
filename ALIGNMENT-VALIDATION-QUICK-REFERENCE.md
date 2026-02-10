# CORTEX Alignment Validation - Quick Reference

**Last Updated:** 2026-02-10  
**Authority:** cortex-architect.prompt.md v15.0 + Phase 70  
**Status:** ✅ PRODUCTION-GRADE TOOLING AVAILABLE

---

## 🚀 Quick Start

### 1. Run Alignment Audit
```bash
# Full audit report
python scripts/audit_alignment.py

# Strict mode (fails if P0/P1 gaps)
python scripts/audit_alignment.py --strict

# Generate markdown report
python scripts/audit_alignment.py --report
```

### 2. Check Current Status
```bash
# View alignment metrics
python scripts/audit_alignment.py | grep "Status:"

# Expected output: ✅ PRODUCTION READY (after Phase 70 S2)
```

### 3. Integrate into CI/CD
```bash
# GitHub Actions will run on every push (see .github/workflows/alignment-check.yml)
# Status badge visible in GitHub UI
# Slack notifications on failures
```

---

## 📊 Gap Categories & Resolution

### P0 - CRITICAL (Production Blocking)
**Status:** Phase 70 S2 (In Progress)  
**Action:** IMPLEMENT or DELETE immediately  
**Examples:**
- RefactoringOrchestrator (missing implementation)
- PlanningOrchestrator (missing implementation)

**Resolution Path:**
1. Review gap details in `phase-70-implementation-backlog.md`
2. Follow TASK-70-S2-00X execution plan
3. Update wiring.yaml on completion
4. Re-run audit to verify

### P1 - HIGH (Test Quality)
**Status:** Phase 70 S2 (In Progress)  
**Action:** DELETE stub tests or IMPLEMENT real assertions  
**Examples:**
- 620 tests with `assert True`
- 257 tests with `pytest.skip("Implementation pending")`

**Resolution Path:**
1. `grep -rn "assert True" tests/` to find stubs
2. Delete if no real assertion value
3. Run `pytest` to verify no import errors
4. Re-run audit

### P2 - MEDIUM (Technical Debt)
**Status:** Phase 70 S3 (Planned)  
**Action:** DEFER with phase target or MARK_INTERNAL  
**Examples:**
- Support orchestrators (23 wired but not implemented)
- STUB code with explicit phase targets

**Resolution Path:**
1. Review `phase-70-implementation-backlog.md` for decisions
2. Update wiring.yaml: add `status: 'planned'` or `internal_only: true`
3. Document phase target for deferred items
4. Re-run audit

### P3 - LOW (Orphaned Code)
**Status:** Phase 70 S3 (Planned)  
**Action:** Mark as internal or delete if unused  
**Examples:**
- 154 implementations not registered in wiring.yaml

**Resolution Path:**
1. `grep -rn "ClassName" cortex/ --include="*.py"` to check usage
2. If only definition found: `internal_only: true` or DELETE
3. If callers exist: mark `internal_only: true`
4. Document in wiring.yaml

---

## 🔍 Using the Audit Tool

### Basic Usage
```bash
python scripts/audit_alignment.py
```

**Output:**
- Gap count by type (WIRED_NOT_IMPLEMENTED, STUB_TEST, etc.)
- Severity breakdown (P0/P1/P2/P3)
- Specific component details with remediation suggestions
- Production readiness status

### Strict Mode (for CI/CD)
```bash
python scripts/audit_alignment.py --strict
```

**Behavior:**
- ✅ Exit code 0 if P0/P1 gaps resolved
- ❌ Exit code 1 if ANY P0/P1 gaps detected
- **Use in:** CI/CD pipelines to block deployment

### Report Generation
```bash
python scripts/audit_alignment.py --report
```

**Output:**
- Generates `ALIGNMENT-AUDIT-REPORT.md`
- Complete markdown table with all gaps
- Suitable for team reports and dashboards

---

## 📋 Phase 70 TASK Execution

### For Autonomous Implementation
Each TASK has specific steps in `phase-70-implementation-backlog.md`:

1. **TASK-70-S2-001:** RefactoringOrchestrator (8h)
   - Move from cortex/refactoring → cortex/orchestrators/domain
   - Adapt to IOrchestrator interface
   - Add MCP adapter + LENS integration

2. **TASK-70-S2-002:** PlanningOrchestrator (12h)
   - TDD implementation from scratch
   - Phase planning + risk assessment logic
   - MCP adapter + LENS integration

3. **TASK-70-S2-003:** Delete 620 Stub Tests (4h)
   - `grep -rn "assert True" tests/` → delete all
   - Verify no import errors
   - Update coverage metrics

4. **TASK-70-S2-004:** Archive 257 Skipped Tests (2h)
   - Move to tests/_archived_legacy/
   - Document which phases restore them
   - Update active test count

5. **TASK-70-S3-001 through S3-003:** Cleanup & Documentation (5h)
6. **TASK-70-S4-001:** CI/CD Automation (4h)

### Execution Flow
```
Phase 70 S1 Complete ✅
         ↓
Execute TASK-70-S2-00X (IMPLEMENT & DELETE)
         ↓
Run audit_alignment.py --report
         ↓
S2 Complete: Commit with "Phase 70 S2: Complete"
         ↓
Execute TASK-70-S3-00X (DEFER & CLEANUP)
         ↓
S3 Complete: Update wiring.yaml
         ↓
Execute TASK-70-S4-001 (CI/CD GATES)
         ↓
Phase 70 Complete: Production Ready ✅
```

---

## 🎯 Success Metrics

### After Phase 70 S2 (Week 1-2)
```
┌─────────────────────────────────────────────┐
│ ALIGNMENT STATUS                            │
├─────────────────────────────────────────────┤
│ Wiring Gaps (P0/P1):     0/2 ✅             │
│ Stub Tests:             0/620 ✅             │
│ Skipped Tests (active):  <10 ✅              │
│ STUB Code (deferred):    25 (documented) ✅  │
│ Alignment Score:        95% ✅              │
│ Production Ready (P0/P1): YES ✅             │
└─────────────────────────────────────────────┘
```

### After Phase 70 S4 (Week 3-4)
```
┌─────────────────────────────────────────────┐
│ CONTINUOUS MONITORING                       │
├─────────────────────────────────────────────┤
│ CI/CD Gate Status:      ACTIVE ✅           │
│ GitHub Actions:         Configured ✅        │
│ Slack Notifications:    Enabled ✅           │
│ Regression Prevention:  <0.5%/week ✅        │
│ Alignment Score:        99%+ ✅             │
│ Production Ready (Full): YES ✅              │
└─────────────────────────────────────────────┘
```

---

## 🔐 Continuous Validation Setup

### GitHub Actions (Automated)
File: `.github/workflows/alignment-check.yml`

```yaml
on:
  push:
    branches: [main, develop]
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6am

jobs:
  alignment:
    runs-on: ubuntu-latest
    steps:
      - name: Alignment Check
        run: python scripts/audit_alignment.py --strict
      - name: Slack Notification
        if: failure()
        run: # Send to #cortex-dev
```

### Pre-Commit Hook (Fast Feedback)
```bash
#!/bin/bash
# .git/hooks/pre-commit (created by Phase 70 S4)

python scripts/audit_alignment.py --strict
if [ $? -ne 0 ]; then
  echo "❌ Alignment check failed. Fix gaps before committing."
  exit 1
fi
```

### Local Development
```bash
# Before committing
python scripts/audit_alignment.py --strict

# Weekly comprehensive audit
python scripts/audit_alignment.py --report > ~/weekly-audit.md
```

---

## 📞 Support & Escalation

### I Found a New Gap
1. Run `python scripts/audit_alignment.py`
2. Identify gap type (WIRED_NOT_IMPLEMENTED, STUB_TEST, etc.)
3. Classify severity (P0/P1/P2/P3) using matrix in `cortex-architect.md`
4. Open issue or update Phase 70 implementation backlog

### CI/CD Pipeline Failed
1. Check GitHub Actions log
2. Run locally: `python scripts/audit_alignment.py --strict`
3. Review failure details in `ALIGNMENT-AUDIT-REPORT.md`
4. Fix gaps using TASK templates

### Questions About Alignment
- **Spec Question:** See `cortex-architect.md` § "Mandatory Alignment Checks"
- **Tool Question:** See script docstring: `python scripts/audit_alignment.py --help`
- **Phase 70 Question:** See `cortex-registry/_cortex-master/phases/active/phase-70-alignment-remediation.yaml`

---

## 📚 Reference Files

| File | Purpose |
|------|---------|
| `scripts/audit_alignment.py` | Automated gap detection tool |
| `scripts/phase-70-gap-triage.py` | Gap decision generator |
| `cortex-registry/_cortex-master/phase-70-gap-triage-matrix.yaml` | Gap decisions (YAML) |
| `cortex-registry/_cortex-master/phase-70-implementation-backlog.md` | TASK execution guide |
| `cortex-registry/_cortex-master/phases/active/phase-70-alignment-remediation.yaml` | Full phase spec |
| `.github/agents/core/cortex-architect.md` | Alignment checks (v15.0) |
| `.github/prompts/cortex-architect.prompt.md` | Authority spec (v15.0) |

---

**Version:** 1.0  
**Last Updated:** 2026-02-10  
**Status:** ✅ READY FOR PRODUCTION USE  
**Authority:** Phase 70 S1 Complete (AC-PHASE70-S1-001 ✅)
