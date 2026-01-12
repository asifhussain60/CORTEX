# Evidence-Based Status Validation Prompt (Plan-Integrated)

**Version:** 3.0.0  
**Author:** Asif Hussain  
**Date:** 2026-01-12  
**Purpose:** Fast, automated validation of AC-ID completion claims against test evidence with plan integration

---

## 🔗 PLAN INTEGRATION (CRITICAL)

**This validator ensures cx6-plan consistency:**

| Plan Asset | Validation Role |
|------------|-----------------|
| `master-plan.yaml` | Phase sequencing, AC-ID dependencies |
| `AC-INDEX.yaml` | AC-ID definitions (count must match tracker) |
| `progress-tracker.json` | Completion claims (must have test evidence) |
| `plan-viewer-data.json` | Dashboard data (must sync from tracker) |

**Validation Chain:**
```
AC-INDEX (defines) → progress-tracker (claims) → tests (proves) → plan-viewer (displays)
```

---

## 🛡️ REGRESSION PREVENTION

**Before validation, check plan integrity:**

```bash
# Pre-validation regression check
python3 << 'EOF'
import json, yaml, sys

# Check AC-INDEX.yaml AC-ID count
ac_index = yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml'))
ac_count = ac_index.get('total_ac_count', 0)

# Check progress-tracker.json
tracker = json.load(open('cortex-brain/tier1/tracking/progress-tracker.json'))
tracker_phases = tracker.get('phases', {})

# Validate consistency
print(f"AC-INDEX total: {ac_count}")
print(f"Tracker phases: {len(tracker_phases)}")

# Regression: If AC-INDEX changed, tracker may be stale
if ac_count > 102:  # Original baseline
    print(f"⚠️ New AC-IDs detected ({ac_count} vs baseline 102). Verify tracker updated.")
    
sys.exit(0)
EOF
```

---

## 🎯 Core Principle

**SINGLE SOURCE OF TRUTH:** Test execution results (PASSED/FAILED) = AC completion evidence.

No speculation. No file checks. No proxy metrics. **Only test results count.**

---

## ⚡ ONE-COMMAND VALIDATION

```bash
# The entire validation workflow in one command
python3 scripts/audit_based_evidence_validator.py --fast --sync
```

**What happens:**
1. Run all tests: `pytest tests/ -v --tb=no -q`
2. Parse PASSED/FAILED by AC-ID marker
3. Update tracker.json with evidence only
4. Sync dashboard: `python3 scripts/sync_plan_viewer_data.py`
5. Display verification summary

**Output:** One-line summary + verification rate
```
✅ Verified 77/102 AC-IDs (75.5%) | 1360 tests passing | Dashboard synced
```

---

## 🚀 Fast Validation Loop (For Phase Implementation)

**Before each feature commit:**

```bash
# 1. Run only tests for current phase
AC_PATTERN="AC-ORCH-*"  # Example: Pattern for Phase 2
python3 -m pytest tests/ -k "$AC_PATTERN" -v --tb=short

# 2. Quick validation for this phase
python3 scripts/audit_based_evidence_validator.py --phase current --sync

# 3. If ≥80% verified → commit allowed. If <80% → block commit
```

**Exit codes:**
- `0` = Verification rate ≥ 80% (proceed)
- `1` = Verification rate < 80% (block)
- `2` = Invalid phase (error)

---

## � Evidence Extraction (Efficient)

### Method 1: Live Test Execution (PRIMARY - Always use this)

```bash
# Run all tests and capture output
pytest tests/ -v --tb=no -q > /tmp/test_output.txt 2>&1

# Extract evidence: AC-ID + PASSED/FAILED status
cat /tmp/test_output.txt | grep -E "AC-[A-Z]+-[0-9]{3}" | \
  grep -E "PASSED|FAILED" | sort -u
```

**Why:** Direct test evidence, no intermediaries, instant.

### Method 2: Audit Database Query (FALLBACK - Use if tests stale)

```bash
# Query SQLite for last 7 days of test execution
sqlite3 cortex-brain/database/audit.db << 'EOF'
SELECT 
  SUBSTR(event_data, INSTR(event_data, 'AC-'), 11) as ac_id,
  CASE 
    WHEN event_data LIKE '%PASSED%' THEN 'PASSED'
    WHEN event_data LIKE '%FAILED%' THEN 'FAILED'
    ELSE 'UNKNOWN'
  END as status,
  MAX(timestamp) as last_run
FROM events
WHERE timestamp > datetime('now', '-7 days')
  AND event_type = 'TEST_EXECUTION'
GROUP BY ac_id, status
ORDER BY ac_id;
EOF
```

**Why:** Backup when live tests unavailable (e.g., CI environment).

---

## ✅ Validation Rules (Simplified)

| Rule | Effect |
|------|--------|
| **Test passes** → AC marked verified ✅ | Immutable fact |
| **Test fails** → AC marked partial ⚠️ | Indicates work needed |
| **No test** → AC marked planned 📋 | Not ready |
| **Verification rate < 80%** → Phase gate BLOCKS | Sequential requirement |
| **Test never ran** → Cannot verify | Requires explicit test run |

---

## 🎯 Three Validation Modes

### Mode 1: Full System Validation (Comprehensive)

```bash
python3 scripts/audit_based_evidence_validator.py --full
```

**Use case:** End of phase, before deployment, stakeholder reporting

**Output:**
```
SYSTEM VALIDATION REPORT
========================

Phase 1: Foundation
  Claimed: 34/34 (100%)
  Verified: 30/34 (88.2%) ✅
  Gap: AC-AUDIT-008, AC-GOV-002, AC-STATE-001, AC-EVIDENCE-002

Phase 2: Orchestration Core
  Claimed: 24/24 (100%)
  Verified: 20/24 (83.3%) ✅
  Gap: AC-ORCH-004, AC-TODO-003, AC-PLAN-001, AC-PLAN-002

Overall: 77/102 (75.5% verified)
Status: GATE PASSED (≥80% required for phases 1-2)
```

### Mode 2: Phase Validation (Fast)

```bash
python3 scripts/audit_based_evidence_validator.py --phase 2
```

**Use case:** During phase implementation, checking if gate conditions met

**Output:**
```
PHASE 2 VALIDATION (Orchestration Core)
======================================

Claimed: 24/24 AC-IDs
Verified: 20/24 (83.3%) ✅

VERIFIED:
  ✅ AC-ORCH-001 through AC-ORCH-003 (3/3)
  ✅ AC-TODO-001 through AC-TODO-002 (2/2)
  ✅ ... (15 more)

GAPS (Needs Implementation):
  ❌ AC-ORCH-004 - Request transformation (0 tests)
  ❌ AC-TODO-003 - Dependency resolution (2/3 tests passing)
  ❌ ... (2 more)

Gate Status: PASSED (83.3% ≥ 80%)
```

### Mode 3: Single AC-ID Validation (Debugging)

```bash
python3 scripts/audit_based_evidence_validator.py --ac AC-ORCH-007
```

**Use case:** Debug why specific AC-ID marked incomplete

**Output:**
```
AC-ORCH-007: Governance-to-Todo Pipeline Integration

Implementation: ✅ src/orchestrators/master_orchestrator.py (992 lines)
Test File: ✅ tests/orchestrators/test_master_orchestrator.py (450 lines)
Test Marker: ✅ @pytest.mark.ac_id("AC-ORCH-007")

Test Results:
  • test_execute_governance_pipeline ... PASSED
  • test_error_handling_in_pipeline ... PASSED
  • test_todo_creation_from_governance ... PASSED
  Total: 3/3 PASSED ✅

Evidence Status: VERIFIED ✅
Last Test Run: 2026-01-11 22:15 UTC
```

---

## 🔧 Integration: Tracker Update Protocol

**After validation completes:**

```python
# 1. Load tracker
tracker = json.load(open('cortex-brain/tier1/tracking/progress-tracker.json'))

# 2. Extract verified counts from test results
verified_count = len([ac for ac in test_results if test_results[ac] == 'PASSED'])
total_claimed = len(current_phase['ac_ids'])

# 3. Update tracker (EVIDENCE ONLY)
tracker['current_phase']['verified_count'] = verified_count
tracker['current_phase']['total_count'] = total_claimed
tracker['current_phase']['verification_rate'] = (verified_count / total_claimed) * 100
tracker['last_updated'] = timestamp

# 4. Save tracker
json.dump(tracker, open('cortex-brain/tier1/tracking/progress-tracker.json', 'w'))

# 5. Sync dashboard
subprocess.run(['python3', 'scripts/sync_plan_viewer_data.py'], check=True)

# 6. Return status
return {
    'verified': verified_count,
    'total': total_claimed,
    'rate': tracker['current_phase']['verification_rate'],
    'synced': True
}
```

**Critical:** Tracker ONLY updated by validator, never manual edits.

---

## � Pre-Commit Hook (Auto-Enforce)

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Only validate if tracker.json or tests/ changed
if ! git diff --cached --quiet cortex-brain/tier1/tracking/progress-tracker.json tests/; then
    echo "🔍 Running evidence validation..."
    python3 scripts/audit_based_evidence_validator.py --phase current --check-only
    
    if [ $? -eq 1 ]; then
        echo "❌ Evidence validation failed. Commit blocked."
        echo "   Run: python3 scripts/audit_based_evidence_validator.py --phase current"
        echo "   To see gaps, then implement missing tests."
        exit 1
    fi
fi
exit 0
```

**Effect:** Prevents committing tracker changes that violate evidence rules.

---

## 🚨 Anti-Patterns Blocked by Validator

| Pattern | Detection | Prevention |
|---------|-----------|-----------|
| Mark AC complete with no tests | grep finds 0 tests | Validator rejects |
| Inflate tracker % manually | Tracker % > verified % | Auto-fix or block commit |
| Old evidence (>7 days) | timestamp check | Force re-run |
| Invalid AC-ID format | `AC-XXX-NNN` check | Reject in marker validation |
| Forgot to add test marker | No `@pytest.mark.ac_id()` | Warn in output |

---

## 📚 Usage Examples

### Example 1: Quick Phase Gate Check

```bash
$ python3 scripts/audit_based_evidence_validator.py --phase 1

Phase 1 gate check:
✅ 30/34 verified (88.2%) - GATE PASSED
Dashboard synced. Ready to advance to Phase 2.
```

### Example 2: Find Gaps Before Committing

```bash
$ python3 scripts/audit_based_evidence_validator.py --phase 2 --verbose

Phase 2 detailed report:

VERIFIED (20/24):
  ✅ AC-ORCH-001-003, AC-TODO-001-002, ...

GAPS (4 AC-IDs):
  ❌ AC-ORCH-004 (0 tests - needs implementation)
  ❌ AC-TODO-003 (2/3 tests failing - needs debug)
  ❌ AC-PLAN-001 (test marked SKIP - re-enable)
  ❌ AC-PLAN-002 (no pytest marker - add @pytest.mark.ac_id)

Fix required before gate can pass.
```

### Example 3: Full System Status

```bash
$ python3 scripts/audit_based_evidence_validator.py --full --json > status.json

$ cat status.json | jq '.phases[] | {name, verified, total, rate}'

{
  "name": "Phase 1: Foundation",
  "verified": 30,
  "total": 34,
  "rate": 88.2
}
{
  "name": "Phase 2: Orchestration Core",
  "verified": 20,
  "total": 24,
  "rate": 83.3
}
...

Total across all phases: 77/102 (75.5%) verified
```

---

## ✅ Success Criteria (Measurable)

**Validation succeeds when:**

1. ✅ Test execution completes: `pytest tests/ -v` runs without hang
2. ✅ Evidence extraction works: AC-ID markers found in test output
3. ✅ Tracker updates: `progress-tracker.json` reflects test results
4. ✅ Dashboard syncs: `plan-viewer-data.json` matches tracker
5. ✅ Phase gates enforced: Completion % matches verified AC-IDs
6. ✅ No data corruption: JSON parses, no truncation

**Current Status (as of 2026-01-12):**
- ✅ Tests: 1360 passing (96.5%)
- ✅ Verified AC-IDs: 77/102 (75.5%)
- ✅ Phase 1: 88.2% verified (gate passed)
- ✅ Phase 2: 83.3% verified (gate passed)
- ✅ Tracker + Dashboard synced
- ✅ All gates operational

---

## 🔄 Continuous Validation Integration

**Run validator automatically:**

1. **After each test run** (pytest plugin)
   ```bash
   pytest tests/ --validator-sync
   ```

2. **Before each commit** (pre-commit hook)
   ```bash
   python3 scripts/audit_based_evidence_validator.py --phase current --check-only
   ```

3. **On phase completion** (CI gate)
   ```yaml
   if: job == 'test'
   run: python3 scripts/audit_based_evidence_validator.py --phase current
   ```

4. **Manual verification** (on demand)
   ```bash
   python3 scripts/audit_based_evidence_validator.py --full
   ```

---

## 🎯 Validator Implementation Priority

**What validator MUST do (MVP):**
1. ✅ Parse pytest output for AC-ID markers
2. ✅ Count PASSED vs FAILED tests
3. ✅ Update tracker with verified counts
4. ✅ Sync dashboard
5. ✅ Return exit code (0 = pass, 1 = fail)

**Nice-to-have (Phase 4+):**
- Report formatting improvements
- Audit database integration
- Trend analysis
- Predictive gap filling

---

## 🔗 OUTPUT STANDARDS COMPLIANCE

**All validation outputs MUST follow `output-standards.md`:**

### Evidence Storage
- ✅ Evidence bundles in `cortex-brain/tier1/evidence-bundles/AC-{ID}/`
- ✅ Format: manifest.yaml + test-results.json + audit-trace.jsonl
- ❌ DO NOT scatter evidence across documents/reports/

### Progress Updates
- ✅ Update ONLY `progress-tracker.json` (not plan-viewer-data.json directly)
- ✅ Sync dashboard: `python3 scripts/sync_plan_viewer_data.py`
- ❌ DO NOT edit dashboard data directly

### Reporting
- ✅ Use executive bullet format (✅ Outcomes / ⚙️ In Progress / ⚠️ Risks)
- ✅ Translate AC-IDs to human-readable capability names
- ❌ DO NOT show raw AC-ID codes in user output

---

## 🛡️ REGRESSION SAFEGUARDS

### Validation Integrity Checks

```bash
# Check 1: AC-INDEX.yaml parseable
python3 -c "import yaml; yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml'))"

# Check 2: progress-tracker.json parseable
python3 -c "import json; json.load(open('cortex-brain/tier1/tracking/progress-tracker.json'))"

# Check 3: Sync script exists and works
python3 scripts/sync_plan_viewer_data.py --check-only
```

### Post-Validation Verification

```bash
# After any tracker update, verify sync
python3 << 'EOF'
import json
from pathlib import Path

tracker = json.load(open('cortex-brain/tier1/tracking/progress-tracker.json'))
viewer = json.load(open('cortex-brain/cx6-plan/viewer/plan-viewer-data.json'))

# Compare key metrics
tracker_complete = tracker.get('current_phase', {}).get('completed_count', 0)
viewer_complete = viewer.get('phases', [{}])[0].get('completed', 0)

if tracker_complete != viewer_complete:
    print(f"⚠️ SYNC DRIFT: tracker={tracker_complete}, viewer={viewer_complete}")
    print("Run: python3 scripts/sync_plan_viewer_data.py")
else:
    print(f"✅ Tracker and viewer in sync: {tracker_complete} AC-IDs complete")
EOF
```

---

## 📊 PROMPT COHESION

**This validator integrates with other prompts:**

| Prompt | Integration |
|--------|-------------|
| `CORTEX.prompt.md` | Calls validator for "validate plan" / "check status" |
| `cortex-exec.prompt.md` | Calls validator after each AC-ID implementation |
| `cortex-brittleness-review.prompt.md` | Uses validator data for risk assessment |

**Shared Contracts:**
- Validator writes to `progress-tracker.json` ONLY
- Validator triggers `sync_plan_viewer_data.py` after updates
- Validator uses AC-INDEX.yaml as reference for AC-ID definitions
- Validator outputs follow `output-standards.md` format

---

## 📋 ARCHITECTURE ENHANCEMENT PROTOCOL

**When validation reveals need for new capabilities:**

1. **DO NOT implement** new validation features inline
2. **Document in:** `cortex-brain/documents/future-enhancements/validation-{capability}.yaml`
3. **Report:** `📋 Enhancement documented: {title} - requires review`
4. **Continue** with existing validation scope

---

**Version History:**
- 1.0.0 (2026-01-11): Comprehensive validation framework (overly complex)
- 2.0.0 (2026-01-12): **OPTIMIZED** - Single command, fast validation, test-evidence-only
- 3.0.0 (2026-01-12): **PLAN-INTEGRATED** - Regression prevention, cohesive prompt integration, output standards compliance
