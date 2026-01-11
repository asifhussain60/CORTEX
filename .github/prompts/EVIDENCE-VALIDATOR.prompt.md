# Evidence-Based Status Validation Prompt

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** 2026-01-11  
**Purpose:** Enforce audit-log-backed completion claims across all CORTEX phases

---

## 🎯 Validation Philosophy

**CRITICAL RULE:** Status claims require audit evidence. "Implemented" means tests RAN and PASSED, not "code exists" or "file mentions AC-ID".

**Evidence Hierarchy (priority order):**
1. **Audit logs** → Test execution records with AC-ID tags + PASSED status
2. **Live pytest run** → `pytest --collect-only` + `pytest -k {ac_id}` execution
3. **Pytest markers** → `@pytest.mark.ac_id("AC-XXX-NNN")` in test files
4. **File existence** → Implementation + test file both exist (>1KB each)
5. **NO EVIDENCE** → Mark as "claimed_without_evidence" (❌)

---

## 📋 Validation Protocol

### Step 1: Load Context (REQUIRED)

```bash
# Read tracker state
cat cortex-brain/tier1/tracking/progress-tracker.json

# Read AC registry
cat cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml

# Read master plan
cat cortex-brain/cx6-plan/master-plan.yaml
```

**Validation checkpoint:** Do all 3 files exist and parse correctly?

---

### Step 2: Extract Audit Evidence

```bash
# Method A: SQLite audit database (preferred)
sqlite3 cortex-brain/database/governance.db << 'EOF'
SELECT DISTINCT
    json_extract(metadata, '$.ac_id') as ac_id,
    json_extract(metadata, '$.test_result') as result,
    MAX(timestamp) as last_execution
FROM audit_log
WHERE category = 'TEST_EXECUTION'
    AND json_extract(metadata, '$.ac_id') IS NOT NULL
    AND json_extract(metadata, '$.test_result') = 'PASSED'
GROUP BY ac_id
ORDER BY ac_id;
EOF

# Method B: JSONL audit logs (fallback)
find cortex-brain/audit-logs -name "*.jsonl" -mtime -7 | xargs grep -h '"category":"TEST_EXECUTION"' | \
  jq -r 'select(.metadata.test_result == "PASSED") | .metadata.ac_id' | sort -u
```

**Output:** List of AC-IDs with passing test evidence in last 7 days

---

### Step 3: Run Live Test Validation

```bash
# Collect all tests with AC-ID markers
python3 -m pytest tests/ --collect-only -q 2>&1 | grep -E "test_.*::" > /tmp/all_tests.txt

# Run tests for each claimed AC-ID
for ac_id in AC-AUDIT-001 AC-AUDIT-002 AC-GOV-001; do
    echo "Testing $ac_id..."
    python3 -m pytest tests/ -k "$ac_id" -v --tb=no -q 2>&1 | grep -E "PASSED|FAILED|ERROR"
done
```

**Output:** Test execution results (PASSED/FAILED/ERROR) per AC-ID

---

### Step 4: Cross-Reference Claims vs Evidence

```python
#!/usr/bin/env python3
"""Evidence-based validation logic"""

import json
from pathlib import Path

def validate_phase_claims(tracker_path: Path, audit_evidence: set, live_evidence: set):
    tracker = json.loads(tracker_path.read_text())
    
    results = {
        'verified': [],
        'claimed_without_evidence': [],
        'verification_rate': 0
    }
    
    # Check current phase
    current_phase = tracker['current_phase']
    for ac_id in current_phase.get('ac_ids', []):
        if ac_id in audit_evidence or ac_id in live_evidence:
            results['verified'].append(ac_id)
        else:
            # Last resort: check file existence
            impl_exists = check_implementation_exists(ac_id)
            test_exists = check_test_exists(ac_id)
            
            if impl_exists and test_exists:
                results['verified'].append(ac_id)
            else:
                results['claimed_without_evidence'].append(ac_id)
    
    results['verification_rate'] = len(results['verified']) / len(current_phase['ac_ids']) * 100
    return results

def check_implementation_exists(ac_id: str) -> bool:
    """Check if implementation file exists and is substantial (>1KB)"""
    category = ac_id.split('-')[1].lower()
    search_paths = [
        f"src/infrastructure/*{category}*.py",
        f"src/orchestrators/**/*{category}*.py",
        f"src/tools/*{category}*.py"
    ]
    # Implementation omitted for brevity
    return False

def check_test_exists(ac_id: str) -> bool:
    """Check if test file exists with AC-ID marker"""
    # grep -r "@pytest.mark.ac_id(\"$ac_id\")" tests/
    return False
```

---

### Step 5: Generate Validation Report

**Report Structure:**

```markdown
# Evidence Validation Report
**Generated:** {timestamp}  
**Method:** audit_logs + live_tests + file_checks

## Summary
- **Total AC-IDs Claimed:** {total_claimed}
- **Total AC-IDs Verified:** {total_verified}
- **Verification Rate:** {rate}%

## Evidence Sources
- Audit logs: {count} AC-IDs
- Live tests: {count} AC-IDs
- File checks: {count} AC-IDs
- No evidence: {count} AC-IDs ❌

## Phase-by-Phase Breakdown

### Phase 1: Foundation
- **Claimed:** {claimed_count}/{total_count} ({percentage}%)
- **Verified:** {verified_count}/{total_count} ({percentage}%)
- **Status:** {ACCURATE | INFLATED | STALE}

**Verified AC-IDs:**
- AC-AUDIT-001 ✅ (audit log: 2026-01-10)
- AC-AUDIT-002 ✅ (live test: PASSED)
- AC-GOV-001 ✅ (file check: impl + test exist)

**Claimed Without Evidence:**
- AC-LIFECYCLE-001 ❌ (no impl file)
- AC-EVIDENCE-002 ❌ (test file missing)

### Phase 2: Orchestration Core
...

## Recommended Actions
1. Fix tracker: Update completion counts to {verified_count}
2. Implement missing: {list of AC-IDs}
3. Add test markers: {list of AC-IDs needing @pytest.mark.ac_id}
```

---

### Step 6: Fix Tracker (Optional)

```bash
# Run validator with auto-fix
python3 scripts/audit_based_evidence_validator.py --fix

# Verify corrections
cat cortex-brain/tier1/tracking/progress-tracker.json | jq '.current_phase.completion_percentage'

# Sync to dashboard
python3 scripts/sync_plan_viewer_data.py
```

---

## 🛡️ Validation Rules

### Rule 1: Audit Log Evidence Wins
If audit logs show test execution + PASSED result → AC-ID is verified (regardless of file state)

### Rule 2: 7-Day Freshness Window
Audit evidence older than 7 days triggers re-validation via live test run

### Rule 3: Marker Requirement
New tests MUST include `@pytest.mark.ac_id("AC-XXX-NNN")` decorator

### Rule 4: No Claim Inflation
Tracker completion % MUST NOT exceed verified AC-ID count / total AC-ID count

### Rule 5: Multi-Source Validation
Each AC-ID requires 2+ evidence sources for "VERIFIED" status:
- Audit log + Live test = VERIFIED
- Audit log + File check = VERIFIED
- Live test + Pytest marker = VERIFIED
- File check only = CLAIMED (not verified)

---

## 📊 Expected Outputs

### Current Status (as of 2026-01-11)

**Before Validation:**
- Phase 1: 100% (34/34) ← INFLATED
- Phase 2: 100% (30/30) ← INFLATED
- Phase 3: 100% (20/20) ← INFLATED
- Total: 84/84 (100%) ← FALSE POSITIVE

**After Validation (Evidence-Based):**
- Phase 1: 44% (15/34) ← ACCURATE
- Phase 1.5 (STS): 100% (3/3) ← VERIFIED
- Phase 2: 33% (10/30) ← ACCURATE (MasterOrchestrator partial)
- Phase 3: 0% (0/20) ← NOT STARTED
- Total: 31% (31/102) ← REALITY

**Verification Breakdown:**
- Audit logs: 12 AC-IDs
- Live tests: 10 AC-IDs
- File checks: 9 AC-IDs
- No evidence: 71 AC-IDs ❌

---

## 🔧 Integration Points

### Pre-Commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run evidence validation before commit
python3 scripts/audit_based_evidence_validator.py --audit-only

if [ $? -ne 0 ]; then
    echo "❌ Evidence validation failed. Commit blocked."
    exit 1
fi
```

### CI/CD Pipeline
```yaml
# .github/workflows/evidence-validation.yml
name: Evidence Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run evidence validator
        run: python3 scripts/audit_based_evidence_validator.py
      - name: Check verification rate
        run: |
          RATE=$(jq '.summary.verification_rate' validation-report.json)
          if [ $(echo "$RATE < 80" | bc) -eq 1 ]; then
            echo "❌ Verification rate below 80%: $RATE%"
            exit 1
          fi
```

### MCP Tool Integration
```python
# src/mcp/tools/evidence_validator.py
@mcp.tool()
async def validate_ac_evidence(ac_id: str) -> dict:
    """Validate evidence for specific AC-ID"""
    validator = AuditBasedValidator(workspace_root=Path.cwd())
    return validator.validate_single_ac(ac_id)
```

---

## 🚨 Anti-Patterns (BLOCKED)

| Anti-Pattern | Detection | Mitigation |
|--------------|-----------|------------|
| Claiming completion without tests | No test file matches AC-ID | Block tracker update |
| Passing tests without audit logs | No audit_log entry for AC-ID | Require EnterpriseAuditLogger integration |
| Stale evidence (>30 days) | Audit timestamp check | Trigger re-validation |
| Missing pytest markers | grep finds no `@pytest.mark.ac_id` | Auto-add markers |
| Tracker-plan divergence | completion_percentage mismatch | Sync from master-plan.yaml |

---

## 📚 Quick Reference

### Run Full Validation
```bash
python3 scripts/audit_based_evidence_validator.py
```

### Fix Tracker Automatically
```bash
python3 scripts/audit_based_evidence_validator.py --fix
```

### Validate Single AC-ID
```bash
python3 -c "
from scripts.audit_based_evidence_validator import AuditBasedValidator
from pathlib import Path

validator = AuditBasedValidator(Path.cwd())
result = validator.validate_single_ac('AC-AUDIT-001')
print(f'Status: {result[\"status\"]}')
print(f'Evidence: {result[\"evidence_sources\"]}')
"
```

### Check Verification Rate
```bash
cat cortex-brain/documents/validation/validation-report.json | \
  jq '.summary.verification_rate'
```

---

## 🎯 Success Criteria

**Validation is successful when:**

1. ✅ Verification rate ≥ 80% (31+ AC-IDs verified out of claimed)
2. ✅ All Phase 1 AC-IDs have audit log evidence
3. ✅ Tracker completion % matches evidence-based calculation
4. ✅ No AC-IDs in "implemented" status without test files
5. ✅ Master plan, tracker, and AC-INDEX show consistent numbers
6. ✅ Dashboard reflects verified counts (not inflated claims)

**Current Status:** ❌ 31% verified (31/102) - Needs ~49 more AC-IDs verified

---

## 🔄 Continuous Validation

**Run validation:**
- Before each commit (pre-commit hook)
- After each test run (pytest plugin)
- Daily (cron job)
- On PR creation (GitHub Actions)

**Update tracker:**
- Only via audit_based_evidence_validator.py (not manual edits)
- Require `--evidence-source` flag for manual overrides
- Log all tracker updates to audit trail

---

**Version History:**
- 1.0.0 (2026-01-11): Initial evidence-based validation framework
