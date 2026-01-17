# CORTEX Remediation Integration: Manual Master Plan Update Guide
## Adding PHASE-REMEDIATION-05 to cortex-master.yaml

**Date:** 2026-01-17  
**Status:** READY FOR MANUAL INTEGRATION  
**Files Created:** ✅ phase-remediation-05-brittleness-hallucination.yaml

---

## QUICK SUMMARY

This guide shows how to manually integrate the new **PHASE-REMEDIATION-05-BRITTLENESS-HALLUCINATION** phase into the CORTEX master implementation plan.

### What's Been Done ✅
- Phase YAML created: `.github/roadmap/phases/phase-remediation-05-brittleness-hallucination.yaml`
- Integration guide created: This document
- Master plan integration documentation: `CORTEX-MASTER-PLAN-INTEGRATION-REMEDIATION-05.md`

### What Needs to Happen Next ⏳
- Manually add phase_tracker entry to `cortex-master.yaml`
- Update metadata AC counts
- Commit all changes

---

## STEP-BY-STEP INTEGRATION

### Step 1: Locate Insertion Point in Master Plan

**File:** `/Users/asifhussain/PROJECTS/CORTEX/.github/roadmap/cortex-master.yaml`

**Find:** Look for the section `PHASE-REMEDIATION-04:` around line 2663

**Context (lines 2855-2900):**
```yaml
      PRODUCTION READINESS: ✅ VERIFIED
      - All critical blockers resolved
      - Test suite stable and reliable
      - Ready to proceed to PHASE-18

  PHASE-17-DOMAIN-BRAIN:
    title: "Domain Brain: Strategic Knowledge Centralization..."
    ...
```

### Step 2: Insert New Phase Entry

**After line 2890** (right before `PHASE-17-DOMAIN-BRAIN:`), add:

```yaml
  PHASE-REMEDIATION-05-BRITTLENESS-HALLUCINATION:
    title: "Brittleness & Hallucination Prevention Remediation (12 AC-IDs)"
    description: |
      Comprehensive remediation of 12 findings from enhanced critical review (2026-01-17):
      - 3 CRITICAL fixes (database, telemetry, boundary enforcement)
      - 3 HIGH priority fixes (sandbox locking, timeouts, documentation)
      - 4 MEDIUM priority fixes (path resolution, AC tracking, pytest config, test naming)
      - 2 LOW priority fixes (confidence scoring, intent fuzzing)
    status: "NOT_STARTED"
    locked: false
    ac_count: 12
    completed_ac_ids: 0
    priority: "P1"
    blocking: true
    requires: "PHASE-REMEDIATION-04"
    required_for: "PRODUCTION_DEPLOYMENT"
    estimated_hours: 24
    estimated_days: 5
    completion_target: "2026-02-07"
    phase_yaml: "phases/phase-remediation-05-brittleness-hallucination.yaml"
    
    ac_breakdown:
      critical: 3
      high: 3
      medium: 4
      low: 2
      total: 12
    
    notes: |
      PHASE-REMEDIATION-05: Brittleness & Hallucination Prevention (12 AC-IDs)
      
      SOURCE: CORTEX-REVIEW-BRITTLENESS-HALLUCINATION-2026-01-17.md
      
      CRITICAL FIXES (Week 1 - Staging Enabler):
      1. AC-FIX-BRITTLENESS-001: Database Connection Lifecycle (81 tests failing)
      2. AC-FIX-BRITTLENESS-002: Telemetry Thread Safety (race condition)
      3. AC-HALLUCINATION-ENFORCEMENT-001: Boundary Enforcement Integration
      
      HIGH PRIORITY FIXES (Week 2-3 - Robustness):
      4. AC-FIX-BRITTLENESS-003: ExecutionSandbox History Locking
      5. AC-FIX-BRITTLENESS-004: Timeout Configuration
      6. AC-HALLUCINATION-ISOLATION-DOC-002: Sandbox Isolation Documentation
      
      MEDIUM/LOW PRIORITY FIXES (Week 4+ - Polish):
      7-12. Path resolution, AC tracking, pytest config, test naming, scoring, fuzzing
      
      TOTAL EFFORT: 20-28 hours over 3-4 weeks
      TIMELINE: Jan 18 - Feb 7, 2026
      OUTCOME: 100% production readiness achieved, staging deployment enabled
```

### Step 3: Update Metadata AC Count

**Find:** Line ~31 in metadata section where it says:
```yaml
total_ac_ids: 275  # 257 complete + 6 (PHASE-REMEDIATION-04) + 12 (PHASE-19 & 20)
```

**Change to:**
```yaml
total_ac_ids: 287  # 258 complete + 6 (REMEDIATION-04) + 12 (REMEDIATION-05) + 12 (DOMAIN-17) + 4 (PHASE-18) + 6 (PHASE-19) + 6 (PHASE-20) + 15 (PRODUCTION-READINESS) + 2 others
```

### Step 4: Update AC Breakdown Summary (Optional but Recommended)

**Find:** Metadata section with ac_breakdown lists, add:
```yaml
remediation_05: 12  # PHASE-REMEDIATION-05 🆕 NEW - Brittleness & Hallucination Prevention
```

---

## ALTERNATIVE: Automated Python Insertion

If manual editing is error-prone, you can use this Python script:

```python
#!/usr/bin/env python3
import sys

# Read master plan
with open('/Users/asifhussain/PROJECTS/CORTEX/.github/roadmap/cortex-master.yaml', 'r') as f:
    lines = f.readlines()

# Find the insertion point (right before PHASE-17-DOMAIN-BRAIN)
insertion_point = None
for i, line in enumerate(lines):
    if line.strip().startswith('PHASE-17-DOMAIN-BRAIN:'):
        insertion_point = i
        break

if insertion_point is None:
    print("❌ Could not find PHASE-17-DOMAIN-BRAIN")
    sys.exit(1)

# Prepare new phase text (see STEP 2 above)
new_phase_text = """  PHASE-REMEDIATION-05-BRITTLENESS-HALLUCINATION:
    title: "Brittleness & Hallucination Prevention Remediation (12 AC-IDs)"
    description: "Comprehensive remediation of 12 findings from enhanced critical review (2026-01-17)"
    status: "NOT_STARTED"
    locked: false
    ac_count: 12
    completed_ac_ids: 0
    priority: "P1"
    blocking: true
    requires: "PHASE-REMEDIATION-04"
    required_for: "PRODUCTION_DEPLOYMENT"
    estimated_hours: 24
    estimated_days: 5
    completion_target: "2026-02-07"
    phase_yaml: "phases/phase-remediation-05-brittleness-hallucination.yaml"

"""

# Insert the new phase
lines.insert(insertion_point, new_phase_text)

# Write back
with open('/Users/asifhussain/PROJECTS/CORTEX/.github/roadmap/cortex-master.yaml', 'w') as f:
    f.writelines(lines)

print("✅ Phase inserted successfully")
```

---

## FILES CHECKLIST

### ✅ Files Already Created

1. **Phase YAML:**
   - Path: `.github/roadmap/phases/phase-remediation-05-brittleness-hallucination.yaml`
   - Size: 14.9 KB
   - Contains: Full AC breakdown, testing strategy, git checkpoints, success criteria
   - Status: ✅ READY

2. **Integration Documentation:**
   - `CORTEX-MASTER-PLAN-INTEGRATION-REMEDIATION-05.md` (This file for reference)
   - `CORTEX-REMEDIATION-ROADMAP-2026-01-17.md` (Detailed action plan)
   - Status: ✅ READY

3. **Supporting Documents (from original review):**
   - `CORTEX-REVIEW-BRITTLENESS-HALLUCINATION-2026-01-17.md` (Full findings)
   - `CORTEX-REVIEW-EXECUTIVE-SUMMARY-2026-01-17.md` (Executive overview)
   - `CORTEX-GAPS-INDEX-2026-01-17.md` (Dependency reference)
   - Status: ✅ READY

### ⏳ Files Needing Update

1. **Master Plan (`cortex-master.yaml`):**
   - Location: `.github/roadmap/cortex-master.yaml`
   - Change: Add PHASE-REMEDIATION-05-BRITTLENESS-HALLUCINATION entry after PHASE-REMEDIATION-04
   - Update: Metadata total_ac_ids
   - Status: ⏳ PENDING MANUAL UPDATE

---

## GIT COMMIT WORKFLOW

### Commit 1: Add Phase YAML and Documentation
```bash
git add .github/roadmap/phases/phase-remediation-05-brittleness-hallucination.yaml
git add CORTEX-MASTER-PLAN-INTEGRATION-REMEDIATION-05.md
git add CORTEX-INTEGRATION-MANUAL-UPDATE-GUIDE.md
git commit -m "feat: PHASE-REMEDIATION-05 specification and integration guide

- Add phase YAML with 12 AC-IDs for brittleness/hallucination remediation
- 3 CRITICAL fixes (database, telemetry, boundary enforcement)
- 3 HIGH priority fixes (sandbox, timeouts, documentation)
- 4 MEDIUM/2 LOW priority fixes (paths, tracking, pytest, scoring, fuzzing)
- Effort: 20-28 hours over 3-4 weeks
- Timeline: Jan 18 - Feb 7, 2026
- Production readiness: 93.8% → 100%

Source: CORTEX-REVIEW-BRITTLENESS-HALLUCINATION-2026-01-17.md
Refs: CORTEX-REMEDIATION-ROADMAP-2026-01-17.md"
```

### Commit 2: Update Master Plan (after manual edits)
```bash
git add .github/roadmap/cortex-master.yaml
git commit -m "feat: Integrate PHASE-REMEDIATION-05 into master plan

- Add phase_tracker entry for PHASE-REMEDIATION-05-BRITTLENESS-HALLUCINATION
- Update total_ac_ids from 275 to 287
- Phase positioned after PHASE-REMEDIATION-04
- Blocking: true (required for production deployment)
- Status: NOT_STARTED (ready for week 1 implementation)"
```

---

## VERIFICATION STEPS

### After Manual Integration, Verify:

```bash
# 1. Check YAML syntax
cd /Users/asifhussain/PROJECTS/CORTEX
python3 -c "import yaml; yaml.safe_load(open('.github/roadmap/cortex-master.yaml'))" && echo "✅ YAML valid"

# 2. Verify phase can be found
grep "PHASE-REMEDIATION-05-BRITTLENESS-HALLUCINATION:" .github/roadmap/cortex-master.yaml

# 3. Verify phase YAML file exists
ls -la .github/roadmap/phases/phase-remediation-05-brittleness-hallucination.yaml

# 4. Count total AC-IDs in phase tracker
grep -c "^  [A-Z].*:$" .github/roadmap/cortex-master.yaml | head -1

# 5. Verify phase is NOT locked (should show: locked: false)
grep -A2 "PHASE-REMEDIATION-05-BRITTLENESS-HALLUCINATION:" .github/roadmap/cortex-master.yaml | grep locked
```

---

## AC-ID QUICK REFERENCE

After integration, these 12 AC-IDs will be part of the master plan:

| AC-ID | Title | Priority | Effort |
|-------|-------|----------|--------|
| AC-FIX-BRITTLENESS-001 | Database Connections | CRITICAL | 4h |
| AC-FIX-BRITTLENESS-002 | Telemetry Thread Safety | CRITICAL | 3h |
| AC-HALLUCINATION-ENFORCEMENT-001 | Boundary Enforcement | CRITICAL | 2h |
| AC-FIX-BRITTLENESS-003 | Sandbox Locking | HIGH | 2h |
| AC-FIX-BRITTLENESS-004 | Timeout Configuration | HIGH | 3h |
| AC-HALLUCINATION-ISOLATION-DOC-002 | Sandbox Isolation Docs | HIGH | 4h |
| AC-BRITTLENESS-PATH-RESOLUTION-005 | Path Resolution | MEDIUM | 2h |
| AC-TRACKING-STATUS-GAP-001 | AC Tracking | MEDIUM | 2h |
| AC-PYTEST-CONFIG-GAP-002 | Pytest Config | LOW | 0.5h |
| AC-TEST-NAMING-GAP-003 | Test Naming | LOW | 0.5h |
| AC-HALLUCINATION-CONFIDENCE-SCORING-003 | Confidence Scoring | LOW | 2h |
| AC-HALLUCINATION-INTENT-FUZZING-004 | Intent Fuzzing | LOW | 2h |
| **TOTAL** | | | **27h** |

---

## NEXT ACTIONS (AFTER INTEGRATION)

### Immediate (After Git Commits)
1. ✅ Phase YAML created and committed
2. ✅ Integration documentation committed
3. ✅ Master plan updated with new phase
4. ⏳ Team review and approval

### Week 1 (Starting Jan 18)
1. Create git checkpoint: `git commit -m "checkpoint: pre-PHASE-REMEDIATION-05"`
2. Assign owners to 12 AC-IDs
3. Begin AC-FIX-BRITTLENESS-001 (database connections)

### Week 1 Completion
1. Complete 3 CRITICAL fixes
2. Run full test suite (verify 100% pass rate)
3. Load test (100 sequential connections, 10x throughput)
4. Team review + staging deployment approval

### Weeks 2-3
1. Complete 3 HIGH priority fixes
2. Run robustness tests
3. Verify timeout configurations

### Weeks 4+
1. Complete 6 MEDIUM/LOW priority fixes
2. Final testing and sign-off
3. Production deployment readiness (target Feb 10)

---

## SUCCESS CRITERIA

After all 12 AC-IDs are complete:

- ✅ 270/275 ACs complete (98.2%)
- ✅ 100% test pass rate maintained
- ✅ All 12 findings resolved
- ✅ Staging deployment enabled
- ✅ Production ready (Feb 10 target)
- ✅ Audit trail: 36 entries (12 ACs × 3 events)

---

## REFERENCES

| Document | Purpose |
|----------|---------|
| `phase-remediation-05-brittleness-hallucination.yaml` | Phase specification |
| `CORTEX-REVIEW-BRITTLENESS-HALLUCINATION-2026-01-17.md` | Full findings |
| `CORTEX-REMEDIATION-ROADMAP-2026-01-17.md` | Detailed action plan |
| `CORTEX-MASTER-PLAN-INTEGRATION-REMEDIATION-05.md` | Integration guide |
| `cortex-master.yaml` | Master plan (manual update needed) |

---

**Status:** READY FOR MANUAL INTEGRATION  
**Last Updated:** 2026-01-17 19:30 UTC  
**Next Step:** Update cortex-master.yaml as described in "STEP-BY-STEP INTEGRATION"

