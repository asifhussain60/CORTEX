# CORTEX Track:Eval - Efficient Copilot Request Guide
**Last Updated:** 2026-01-22 | **Status:** Ready for execution

---

## 🚀 MOST EFFICIENT REQUEST (Copy-Paste Ready)

### **Option 1: Ultra-Minimal (Recommended)**
```
Execute: python /Users/asifhussain/PROJECTS/CORTEX/scripts/execute-track-eval-silent.py
```
**What it does:** Runs 8 audit phases silently. Takes 10-15 minutes. Returns JSON results.  
**Output:** Summary on stderr, full JSON on stdout → eval-results.json  
**Exit code:** 0 if all pass, 1 if blocker detected

---

### **Option 2: With Save & Git Commit**
```
Run: ./scripts/run-track-eval-silent.sh --save --commit
```
**What it does:** Executes track:eval, saves results.json, commits to git.  
**Output:** Results + git commit message  
**Time:** 12-15 minutes

---

### **Option 3: Copy-Paste Shell Command**
```bash
cd /Users/asifhussain/PROJECTS/CORTEX && \
python scripts/execute-track-eval-silent.py > eval-results.json 2>&1 && \
jq '.phases[] | "\(.phase): \(.status)"' eval-results.json && \
echo "" && \
jq '.summary' eval-results.json
```
**What it does:** Execute, show phase results, show summary  
**Output:** Clean summary of all 8 phases  

---

## 💡 REQUEST PATTERNS

### Pattern 1: "Execute silently and report only blockers"
```
@copilot Execute: 
  python scripts/execute-track-eval-silent.py 2>/dev/null | \
  jq 'if .blockers | length > 0 then .blockers else "✓ NO BLOCKERS" end'
```

### Pattern 2: "Execute and give me yes/no on pass"
```
@copilot Run python scripts/execute-track-eval-silent.py and return only:
  - "YES: All 8/8 phases passed" OR
  - "NO: Blocker on {phase-name}"
```

### Pattern 3: "Execute with progress"
```
@copilot Run python scripts/execute-track-eval-silent.py 2>&1 | grep -E '^\[|^✓|^⚠|^✗'
```

### Pattern 4: "Execute specific phase only"
```
@copilot Run only PHASE-AUDIT-002 (the blocking phase):
  python scripts/execute-track-eval-silent.py --phase 2
```

---

## 📊 EXPECTED OUTPUT

### If ALL PHASES PASS ✓
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

### If PHASE-AUDIT-002 FAILS ⚠
```
▶ Executing TRACK:EVAL (8 phases)...
  [1/8] ✓ PHASE-AUDIT-001-EXPORT-VERIFY
  [2/8] ⚠ PHASE-AUDIT-002-PHASE-E-VERIFY
  [3-8] ⊘ SKIPPED (blocker)

============================================================
TRACK:EVAL EXECUTION SUMMARY
============================================================
Phases: 8 | ✓ 1 | ⚠ 0 | ⊘ 6 | ✗ 0

BLOCKERS:
  ⚠ PHASE-AUDIT-002: 68% real implementation (need ≥90%)

⚠ 1 phase needs attention
============================================================
```
→ See `docs/EVAL-TRACK-REMEDIATION-PLAN-20260122.md` for recovery

---

## 🔧 ONE-LINER COMMANDS

### Quick test (5-10 min)
```bash
cd /Users/asifhussain/PROJECTS/CORTEX && timeout 600 python scripts/execute-track-eval-silent.py 2>&1 | tail -20
```

### Full execution with results saved
```bash
cd /Users/asifhussain/PROJECTS/CORTEX && python scripts/execute-track-eval-silent.py > eval-results.json 2>eval-progress.log && echo "✓ Complete" && cat eval-progress.log
```

### Just show pass/fail
```bash
cd /Users/asifhussain/PROJECTS/CORTEX && python scripts/execute-track-eval-silent.py 2>&1 | grep -E '^Phases:|^✓|^⚠'
```

### Show detailed failures only
```bash
cd /Users/asifhussain/PROJECTS/CORTEX && python scripts/execute-track-eval-silent.py 2>/dev/null | jq '.phases[] | select(.status != "PASS")'
```

---

## 🎯 WHAT THE PHASES CHECK

| Phase | What It Does | Blocking? | Time |
|-------|-------------|-----------|------|
| 1. EXPORT-VERIFY | Test collection has 0 errors | YES | 2 min |
| 2. PHASE-E-VERIFY | 90%+ real implementations | YES | 3-5 min |
| 3. IMPORT-MIGRATION | 105 imports categorized | NO | 2 min |
| 4. GOVERNANCE | Type hints/docstrings ≥95% | NO | 2 min |
| 5. ROADMAP | Duplicates removed, YAML valid | NO | 2 min |
| 6. GIT-CHECKPOINT | Recent commits formatted | NO | 1 min |
| 7. DOCSTRING | Static analysis of docs | NO | 2 min |
| 8. COVERAGE | Coverage baseline established | NO | 1-2 min |

---

## ⏱️ TIMELINE

- **Execution time:** 10-15 minutes
- **If PHASE-AUDIT-002 blocks:** Add 7-14 days for remediation
- **After all PASS:** Proceed to PHASE-KG-001 (Knowledge Graph)

---

## 🎯 RECOMMENDED COPILOT REQUEST

**Paste this into Copilot:**

```
@copilot Execute CORTEX track:eval phases silently:

1. Run: python /Users/asifhussain/PROJECTS/CORTEX/scripts/execute-track-eval-silent.py

2. Capture output to eval-results.json

3. Extract and display ONLY:
   - Total phases: X
   - Passed: X
   - Warnings: X
   - Blockers: X (if any)

4. Format:
   ✓ 8/8 phases passed
   
   OR if blockers:
   
   ⚠ Blockers detected:
   - PHASE-AUDIT-002: 68% real (need 90%)

5. Exit code: 0 if all pass, 1 otherwise

6. Minimum verbosity, no test details

Start immediately, silence not required but preferred.
```

---

## 📋 VERIFICATION CHECKLIST

Before running, verify:
- [ ] Python 3.10+ available: `python --version`
- [ ] pytest installed: `pytest --version`
- [ ] cortex module importable: `python -c "import cortex"`
- [ ] Git configured: `git config user.name`
- [ ] On CORTEX branch: `git branch | grep CORTEX`

```bash
# Quick verify
cd /Users/asifhussain/PROJECTS/CORTEX
python --version && pytest --version && python -c "import cortex" && echo "✓ Ready"
```

---

## 🔄 AFTER EXECUTION

### If all phases PASS (✓ 8/8):
1. Update roadmap: Mark phases as COMPLETED
2. Commit results: `git commit -m "EVAL-TRACK: All 8 phases passed"`
3. Proceed to: PHASE-KG-001

### If PHASE-AUDIT-002 blocks (⚠):
1. Review: `docs/EVAL-TRACK-REMEDIATION-PLAN-20260122.md`
2. Remediation time: 7-14 days estimated
3. Re-run: `python scripts/execute-track-eval-silent.py` after fixes

### If other phases warn (⚠):
1. Review findings in `eval-results.json`
2. Create tickets for non-blocking items
3. Continue if no critical blockers

---

## 🚨 EMERGENCY OPTION

If you need it done NOW and want to skip the script:

```bash
cd /Users/asifhussain/PROJECTS/CORTEX
# 1. Quick test collection check
pytest tests/ --collect-only -q 2>&1 | head -20

# 2. Quick PHASE-E sample check  
find cortex/domain_brain -name '*.py' -type f | head -5 | xargs wc -l | tail -1

# 3. Quick coverage
pytest cortex/core/ --cov=cortex.core --cov-report=term-missing -q 2>&1 | tail -3
```

---

## 💬 COPILOT INSTRUCTION (For Next Run)

Save this as your default instruction:

> **"When I ask to execute track:eval, run this command with minimal output:**  
> `python /Users/asifhussain/PROJECTS/CORTEX/scripts/execute-track-eval-silent.py`  
> **Show only the summary line (Phases: X | ✓ X | ⚠ X | ✗ X) and any blockers. No other details."**

---

**Ready to execute. Run any of the commands above.**
