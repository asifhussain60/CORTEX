# CORTEX Track:Eval Silent Execution - Copilot Request Template

## Quick Reference - TLDR

**Execute all 8 audit phases with minimal output:**

```
@cortex-eval-exec TRACK:EVAL silently
```

---

## What You're Requesting

This single command silently executes **8 audit/cleanup phases** in sequence:

1. **PHASE-AUDIT-001** - Test collection verification
2. **PHASE-AUDIT-002** - PHASE-E production readiness (BLOCKING)
3. **PHASE-AUDIT-003** - Import migration audit
4. **PHASE-AUDIT-004** - Governance compliance check
5. **CLEANUP-PHASE-001** - Roadmap maintenance
6. **PHASE-AUDIT-005** - Git checkpoint verification
7. **PHASE-AUDIT-006** - Docstring compliance
8. **PHASE-AUDIT-007** - Coverage baseline

---

## Output Format

**Minimal Stderr Output:**
```
▶ Executing TRACK:EVAL (8 phases)...
  [1/8] ✓ PHASE-AUDIT-001-EXPORT-VERIFY
  [2/8] ✓ PHASE-AUDIT-002-PHASE-E-VERIFY
  [3/8] ✓ PHASE-AUDIT-003-IMPORT-MIGRATION-AUDIT
  [4/8] ✓ PHASE-AUDIT-004-GOVERNANCE-COMPLIANCE-CHECK
  [5/8] ✓ CLEANUP-PHASE-001-ROADMAP-MAINTENANCE
  [6/8] ✓ PHASE-AUDIT-005-GIT-CHECKPOINT-VERIFY
  [7/8] ✓ PHASE-AUDIT-006-DOCSTRING-COMPLIANCE-CHECK
  [8/8] ✓ PHASE-AUDIT-007-COVERAGE-BASELINE-ESTABLISH

============================================================
TRACK:EVAL EXECUTION SUMMARY
============================================================
Phases: 8 | ✓ 8 | ⚠ 0 | ⊘ 0 | ✗ 0

✓ ALL PHASES PASSED
============================================================
```

**Stdout: Full JSON results** (for programmatic processing)
```json
{
  "start_time": "2026-01-22T14:30:00",
  "end_time": "2026-01-22T14:45:30",
  "phases": {
    "PHASE-AUDIT-001-EXPORT-VERIFY": {
      "status": "PASS",
      "checks": {"collection_errors": 0},
      "ac_001_01": "PASS"
    },
    ...
  },
  "blockers": [],
  "summary": {...}
}
```

---

## Key Features

✓ **Silent execution** - Only essential feedback on stderr  
✓ **Fast** - Typical runtime 10-15 minutes  
✓ **Blocking gates** - Stops on critical failures  
✓ **JSON output** - Machine-readable results  
✓ **Minimal verbosity** - No test details, only summary  

---

## Different Request Formats

### 1. **Most Efficient (Recommended)**
```
@cortex Execute TRACK:EVAL silently. Output JSON to cortex-eval-results.json
```

### 2. **With Detailed Report**
```
@cortex Execute TRACK:EVAL. Generate HTML report cortex-eval-report.html
```

### 3. **Specific Phase Only**
```
@cortex Execute PHASE-AUDIT-002 only. Output summary to stdout
```

### 4. **With Git Commit**
```
@cortex Execute TRACK:EVAL. Commit results as "EVAL-TRACK: 8 phases executed [summary]"
```

---

## Expected Blockers & Recovery

### Blocker 1: PHASE-AUDIT-001 fails
```
❌ Test collection has ImportError
→ Review errors with: pytest tests/ --collect-only
→ Fix imports, re-run phase
```

### Blocker 2: PHASE-AUDIT-002 fails  
```
❌ PHASE-E implementation <70% real
→ Review: EVAL-TRACK-REMEDIATION-PLAN-20260122.md
→ May require 5-14 days remediation
```

### Recovery: Run single phase
```
python scripts/execute-track-eval-silent.py --phase PHASE-AUDIT-001 --verbose
```

---

## Usage Examples

### Example 1: Quick Check
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python scripts/execute-track-eval-silent.py 2>/dev/null | jq '.summary'
```

**Output:**
```json
{
  "total_phases": 8,
  "passed": 8,
  "warnings": 0,
  "blockers": 0,
  "duration_minutes": 12.5,
  "timestamp": "2026-01-22T14:45:30"
}
```

### Example 2: Full Report with Git Commit
```bash
python scripts/execute-track-eval-silent.py > eval-results.json 2>eval-stderr.log
git add eval-results.json eval-stderr.log
git commit -m "EVAL-TRACK: All 8 phases executed - 8/8 PASS"
```

### Example 3: Monitor in Real-time
```bash
# Watch stderr progress
python scripts/execute-track-eval-silent.py 2>&1 | tee eval.log

# Then query results
jq '.phases[] | {phase: .phase, status: .status}' eval-results.json
```

---

## Integration with Roadmap

Once all phases pass (✓ 8/8), update `cortex-impl-map.yaml`:

```yaml
# Mark all TRACK:EVAL phases COMPLETED
PHASE-AUDIT-001-EXPORT-VERIFY:
  status: "COMPLETED"
  completed_date: "2026-01-22T14:45:30Z"
  results_file: "eval-results.json"
```

Then proceed to PHASE-KG-001 (Knowledge Graph track).

---

## Copilot Request Pattern

**Most Efficient Silent Request:**

```
@copilot Execute CORTEX track:eval with this pattern:
1. Run: python scripts/execute-track-eval-silent.py
2. Capture output to eval-results-YYYY-MM-DD.json
3. Extract summary: jq '.summary' eval-results.json
4. Show only: "Phases: X | ✓ X | ⚠ X | ✗ X"
5. If blockers exist, output blocker names only
6. Return JSON for downstream processing
7. Exit code: 0 if all PASS, 1 if any FAIL/BLOCKER
```

---

## Files Referenced

- **Execution Script:** `scripts/execute-track-eval-silent.py`
- **Roadmap:** `_workspaces/roadmap/cortex-impl-map.yaml`
- **Remediation Plan:** `docs/EVAL-TRACK-REMEDIATION-PLAN-20260122.md`
- **Results Output:** `eval-results-[timestamp].json`

---

## Next Steps

1. ✓ Run: `python scripts/execute-track-eval-silent.py`
2. Review `eval-results.json` for any warnings/blockers
3. If PHASE-AUDIT-002 fails → Follow remediation plan (7-14 days)
4. If all PASS → Proceed to PHASE-KG-001
5. Commit results: `git commit -m "EVAL-TRACK: X/8 phases passed"`

---

**Last Updated:** 2026-01-22  
**Authority:** Review Findings F004-F012 Remediation  
**Status:** Ready for execution
