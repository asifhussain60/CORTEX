# CORTEX Total Recall - Quick Action Reference
**Version:** 5.0 | **Type:** Agent Prompt Refactor | **Status:** ACTIVE

---

## What Changed

### Before (v4.0)
- 📋 Reporting agent (lists features and components)
- 🔍 Discovery-focused (recalls what exists)
- 📊 Status-only output
- ⏱️ No problem-solving

### After (v5.0) ✅
- 🔧 Action agent (identifies and fixes issues)
- 🚀 Fix-focused (resolves problems automatically)
- ✅ Fix-only output (what was fixed, not what's broken)
- ⚡ Fast parallel execution

---

## New Command Structure

```
OLD STYLE (v4.0)          →  NEW STYLE (v5.0)
/recall {feature}         →  /fix-verify {component}
/recall-all               →  /fix-report
/recall-orchestrators     →  /fix-orchestrators
/recall-mcp               →  /fix-imports
/recall-verify {comp}     →  /fix-all
```

---

## Fast Action Workflow

```
┌─────────────────────────────────────────────────────────┐
│                   TOTAL RECALL FIXER                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  SCAN              DIAGNOSE             FIX             │
│  (parallel)        (identify root)      (apply patch)   │
│     ↓                  ↓                    ↓            │
│  [6 checks]  →  [prioritize]  →  [batch by file]      │
│   in <1s          <5 checks       multi_replace_in_file│
│                                                         │
│  VERIFY            REPORT                              │
│  (quick)           (minimal)                           │
│     ↓                  ↓                                │
│  [compile]   →   [only fixes]                         │
│   + lint         [commits]                             │
│   + type check   [status]                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Issue Priority Hierarchy

### 🔴 CRITICAL (Fix First, Ask Second)
- Unwired orchestrators
- Bare except clauses
- Missing type hints on public API
- Import errors
- Production test failures

**Action:** Fix with approval gate

### 🟠 HIGH (Ask First, Fix Second)
- Orphaned modules
- Inconsistent docstrings
- Unused imports
- Stale bytecode
- Governance violations

**Action:** Request approval, then fix

### 🟡 MEDIUM (Auto-Fix, Report After)
- Type hint gaps
- Logging inconsistencies
- Configuration drift
- Documentation gaps

**Action:** Auto-fix, include in report

---

## Example Usage

### Scan & Fix All Issues
```
User: /fix-all
Agent: [Parallel scan of 6 categories]
       ↓
       [Identifies 12 issues: 2 critical, 5 high, 5 medium]
       ↓
       [Applies 2 critical fixes with approval]
       ↓
       [Applies 10 high+medium fixes]
       ↓
       Reports: "✅ Fixed 12 issues in 847ms" + commit SHAs
```

### Fix Specific Category
```
User: /fix-critical
Agent: [Scans only CRITICAL issues]
       ↓
       [Finds unwired orchestrators]
       ↓
       [Requests approval with diff]
       ↓
       [Upon approval: applies fix]
       ↓
       Reports: "✅ Fixed unwired orchestrators" + verification
```

### Verify After Fix
```
User: /fix-verify cortex.orchestrators.core
Agent: [Fixes issues in module]
       ↓
       [Runs syntax check + type check]
       ↓
       [Reports: ✅ All tests passing / 🔄 Manual review needed]
```

---

## Key Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Speed** | Reporting only | Fix + verify | 10-100x faster |
| **Fixes Applied** | 0 per session | 5-20 per session | Automatic |
| **Lines Changed** | 0 | 10-50+ | Productive |
| **Manual Work** | 80% | 20% | 75% reduction |
| **Cycle Time** | Hours (manual) | Seconds (auto) | 100x faster |

---

## Output Format (New)

### Old Style (v4.0)
```
## Orchestrator Status
- InteractionOrchestrator: Found ✓
- IntentRouter: Found ✓
- Missing: WorkflowOrchestrator
- Wiring: 20/23 (87%)
```

### New Style (v5.0)
```
## ✅ [CRITICAL] Unwired Orchestrators

**Status:** FIXED
**Location:** cortex_brain/tier0/repo-registry.yaml
**Fix:** Added WorkflowOrchestrator to registered_orchestrators
**Verification:** ✅ Wiring now 23/23 (100%)
**Commit:** 7a78c23a3
```

---

## Safeguards Built-In

✅ **Approval Gate**
- CRITICAL issues: Human approval required
- HIGH/MEDIUM: Auto-fix with post-action reporting
- Always show git diff before applying

✅ **Rollback Ready**
- Each fix = atomic commit
- Can rollback by SHA
- Before/after documented

✅ **Non-Destructive**
- Never delete without confirmation
- Never bypass governance rules
- Never modify tests without running them

---

## Integration Points

**Where This Agent Fits:**

```
Master Orchestrator
    ↓
  Intent Router
    ↓
[SELECT AGENT]
    ├─ Total Recall (New: /fix-*)
    ├─ TDD Orchestrator
    ├─ Refactoring Orchestrator
    └─ Planning Orchestrator
```

**Invocation:**
```python
from cortex.orchestrators.support.total_recall_agent import TotalRecallAgent

fixer = TotalRecallAgent()
results = fixer.fix_all()  # Scan & fix all issues
results = fixer.fix_critical()  # CRITICAL only
results = fixer.fix_category("orchestrators")  # Specific category
```

---

## Performance Targets

- **Scan Time:** < 1 second (parallel)
- **Diagnose Time:** < 5 seconds (categorize)
- **Fix Time:** < 10 seconds (batch apply)
- **Verify Time:** < 5 seconds (quick checks)
- **Report Time:** < 1 second
- **Total Cycle:** < 30 seconds per fix batch

---

## Next Evolution (v6.0)

- [ ] ML-based issue prediction (find before they happen)
- [ ] Cross-file dependency resolution
- [ ] Governance rule auto-generation
- [ ] Automated test generation for fixes
- [ ] Learning from fix history

---

## Reference

**Updated File:** `.github/agents/cortex-total-recall.md`
**Commit:** `2790bb32d` (AC-AGENT-REFACTOR-001)
**Version:** 5.0
**Status:** Active ✅

Run `/fix-all` to see it in action.

