# 🔍 Maintenance Wiring Persistence Gap - Root Cause Analysis

**Date:** December 29, 2025  
**Author:** Asif Hussain  
**Severity:** 🔴 CRITICAL - System Architecture Flaw  
**Status:** ⚠️ ACTIVE ISSUE

---

## 🎯 Problem Statement

When `cortex-maintenance.prompt.md` is executed on Machine A and changes are committed/pushed to remote, pulling those changes on Machine B results in an "unwired" system again. **Maintenance wiring does NOT persist across machines.**

---

## 🔬 Root Cause Analysis

### What Maintenance Scripts ACTUALLY Do

After deep investigation of the maintenance pipeline:

```
Phase 2: python3 scripts/cortex_system_doctor.py --quick
Phase 3: python3 scripts/cortex_system_doctor.py --phase diagnose --phase scan
Phase 4: python3 scripts/check_wiring_integrity.py
```

**Critical Discovery:** These scripts are **DIAGNOSTIC ONLY** - they:

✅ **DO:**
- ✅ Scan for unwired components
- ✅ Generate health reports (JSON/Markdown)
- ✅ Calculate wiring coverage percentage
- ✅ Identify missing registrations
- ✅ Suggest fixes (with `--fix` flag)

❌ **DO NOT:**
- ❌ Actually modify source code
- ❌ Update `agent_registry.py`
- ❌ Wire orchestrators into `cortex-operations.yaml`
- ❌ Update manifest files
- ❌ Modify `planning_orchestrator.py` to call interactive mode

### The False Assumption

**We assumed:** Running maintenance "fixes wiring" and commits should persist.

**Reality:** Maintenance only **REPORTS** wiring gaps. The actual wiring fixes must be done **manually** or via separate scripts.

---

## 🧩 Why "Wiring" Appears Machine-Specific

When maintenance runs on different machines, it produces IDENTICAL reports showing:

```json
{
  "planning_orchestrator": {
    "decision_logic": "❌ Method exists but not called in execute()",
    "agent_registration": "❌ InteractivePlanner not in registry",
    "execution_routing": "❌ No conditional routing in execute()",
    "interactive_method": "⚠️ interactive_plan_creation exists but not used"
  }
}
```

**The wiring gaps are consistent because the SOURCE CODE itself hasn't changed.**

What varies by machine:
- ❓ Local `.gitignore` patterns (reports not committed?)
- ❓ Different script execution paths
- ❓ Python environment differences
- ❓ Cached module imports

---

## 🔍 Evidence from Codebase

### Evidence 1: `check_wiring_integrity.py` is Read-Only

```python
# Line 469 - Only WRITES report files
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump({
        'timestamp': report.timestamp,
        'total': report.total_components,
        'wired': report.wired_components,
        'unwired': report.unwired_components,
        # ...
    }, f, indent=2)
```

**No code modification logic present.**

### Evidence 2: `cortex_system_doctor.py` is Diagnostic-Only

```python
# Lines 735-764 - Only WRITES health reports
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("# 🩺 CORTEX System Doctor Report\n\n")
    f.write(f"**Generated:** {report.timestamp}\n")
    # ...
```

**No source code patching logic present.**

### Evidence 3: Planning Orchestrator Already Has Wiring Code

```python
# src/orchestrators/planning/planning_orchestrator.py
def _should_use_interactive_mode(self, **kwargs) -> bool:
    # Line 474 - Method EXISTS

def execute(self, **kwargs) -> OrchestratorResult:
    # Line 515 - Method EXISTS
    
    if self._should_use_interactive_mode(**kwargs):
        # Line 548 - CONDITIONAL ROUTING EXISTS
```

**The wiring code is ALREADY THERE but not connected to the right places.**

### Evidence 4: Interactive Session Module Exists

```bash
$ ls -lah src/orchestrators/planning/interactive_session.py
-rw-r--r--  1 user  staff   33K Dec 27 15:00 interactive_session.py
```

**648 lines of interactive workflow code exist but aren't called.**

---

## 🎯 The Real Problem

### Problem 1: Incomplete Wiring in Source Code

The maintenance scripts correctly identify that:

1. **Decision Logic** (`_should_use_interactive_mode`) exists but isn't integrated into the main `execute()` flow properly
2. **Agent Registry** doesn't include `InteractivePlanner` (no `agent_registry.py` file found)
3. **Execution Routing** has conditional logic but something in the flow is broken
4. **Interactive Method** (`interactive_plan_creation`) exists but isn't wired to the agent

### Problem 2: Reports Aren't Committed

```bash
# Check .gitignore
$ grep -E "health-reports|reports" .gitignore
cortex-brain/health-reports/
cortex-brain/*-reports/
```

**Health reports are gitignored!** So even if maintenance runs on Machine A, the diagnostic reports **don't get committed**, making it appear like Machine B is starting fresh.

### Problem 3: No Auto-Wiring Scripts

Maintenance identifies gaps but doesn't include **auto-wire repair scripts** that:
- Update source code
- Register agents
- Wire orchestrators
- Commit changes

---

## 🔧 What SHOULD Happen

### Ideal Maintenance Flow

```
1. RUN: python3 scripts/cortex_system_doctor.py
   └─> DIAGNOSE: Find unwired components
   
2. RUN: python3 scripts/auto_wire_orchestrators.py  # ❌ MISSING
   └─> FIX: Update planning_orchestrator.py
   └─> FIX: Create/update agent_registry.py
   └─> FIX: Wire to cortex-operations.yaml
   
3. RUN: python3 scripts/check_wiring_integrity.py
   └─> VERIFY: All components now wired (100%)
   
4. COMMIT: git add src/ && git commit -m "fix: auto-wire orchestrators"
   
5. PUSH: git push origin CORTEX-4.0
   
6. PULL on Machine B: git pull origin CORTEX-4.0
   └─> SOURCE CODE now includes wiring fixes
   └─> Maintenance on Machine B shows 100% wired
```

### Current Flow (Broken)

```
1. RUN: Maintenance scripts (diagnostic only)
2. GENERATE: Reports in cortex-brain/health-reports/
3. COMMIT: Reports are gitignored, so nothing commits
4. PUSH: No changes pushed (or only report changes)
5. PULL on Machine B: No source code changes received
6. Machine B runs maintenance: Same gaps reported
```

---

## 🚨 Impact Assessment

| Area | Impact | Severity |
|------|--------|----------|
| **Developer Experience** | Every machine requires manual wiring | 🔴 HIGH |
| **CI/CD Reliability** | Build servers always report unwired | 🔴 HIGH |
| **Maintenance Credibility** | Users lose trust in "maintenance fixed it" | 🟡 MEDIUM |
| **Documentation Accuracy** | Maintenance docs promise wiring, don't deliver | 🔴 HIGH |
| **Team Onboarding** | New developers can't rely on git pull | 🔴 HIGH |

---

## ✅ Recommended Solutions

### Solution 1: Create Auto-Wiring Scripts (RECOMMENDED)

**Priority:** 🔴 CRITICAL  
**Effort:** 2-3 hours  
**Impact:** Fully automated wiring

**Implementation:**

```bash
# New script: scripts/auto_wire_orchestrators.py
```

Features:
- ✅ Parse wiring gap reports
- ✅ Update `planning_orchestrator.py` to wire `_should_use_interactive_mode`
- ✅ Create `src/cortex_agents/agent_registry.py` if missing
- ✅ Register `InteractivePlanner` in registry
- ✅ Update `cortex-operations.yaml` with orchestrator mappings
- ✅ Generate git-committable changes
- ✅ Verify 100% wiring post-fix

**Usage:**
```bash
# Run after maintenance diagnostic
python3 scripts/cortex_system_doctor.py --quick
python3 scripts/auto_wire_orchestrators.py --execute  # NEW
python3 scripts/check_wiring_integrity.py              # Verify 100%
```

---

### Solution 2: Update Maintenance Documentation

**Priority:** 🟡 HIGH  
**Effort:** 30 minutes  
**Impact:** Clarify expectations

**Changes to `cortex-maintenance.prompt.md`:**

```markdown
## Phase 4: Wiring Integrity

```bash
# Phase 4a: DETECT wiring gaps
python3 scripts/check_wiring_integrity.py

# Phase 4b: AUTO-WIRE components ← NEW STEP
python3 scripts/auto_wire_orchestrators.py --execute

# Phase 4c: VERIFY 100% coverage
python3 scripts/check_wiring_integrity.py
```

**⚠️ CRITICAL:** Phase 4b MUST run to persist wiring across machines.

**Expected Outcome:**
- ✅ Source code modified (planning_orchestrator.py, agent_registry.py)
- ✅ Changes committed to git
- ✅ git pull on other machines receives wiring fixes
```

---

### Solution 3: Add Pre-Push Git Hook

**Priority:** 🟢 MEDIUM  
**Effort:** 30 minutes  
**Impact:** Prevent unwired code from being pushed

**Implementation:**

```bash
# .git/hooks/pre-push
#!/bin/bash

echo "🔌 Checking wiring integrity before push..."

python3 scripts/check_wiring_integrity.py --pre-commit

if [ $? -ne 0 ]; then
  echo "❌ PUSH BLOCKED: Unwired components detected"
  echo "Run: python3 scripts/auto_wire_orchestrators.py --execute"
  exit 1
fi

echo "✅ All components wired - push allowed"
exit 0
```

---

### Solution 4: CI/CD Validation

**Priority:** 🟢 MEDIUM  
**Effort:** 1 hour  
**Impact:** Catch unwired components in PR reviews

**GitHub Actions Workflow:**

```yaml
name: Wiring Integrity Check

on: [push, pull_request]

jobs:
  check-wiring:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Check Wiring Integrity
        run: |
          python3 scripts/check_wiring_integrity.py
          
      - name: Upload Wiring Report
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: wiring-report
          path: cortex-brain/health-reports/wiring-report-*.json
```

---

## 📋 Action Items

### Immediate (This Week)

- [ ] **Create** `scripts/auto_wire_orchestrators.py` (Solution 1)
- [ ] **Test** auto-wiring on planning orchestrator
- [ ] **Verify** wiring persists after git pull on second machine
- [ ] **Update** `cortex-maintenance.prompt.md` with Phase 4b (Solution 2)
- [ ] **Document** auto-wiring script usage in maintenance guide

### Short-Term (Next Week)

- [ ] **Implement** pre-push git hook (Solution 3)
- [ ] **Create** CI/CD workflow for wiring validation (Solution 4)
- [ ] **Add** wiring status badge to README
- [ ] **Write** troubleshooting guide for wiring issues

### Long-Term (Next Sprint)

- [ ] **Extend** auto-wiring to ADO orchestrator
- [ ] **Extend** auto-wiring to all orchestrators with interactive mode
- [ ] **Create** wiring dashboard (visual representation)
- [ ] **Automate** periodic wiring health checks (cron job)

---

## 🧪 Verification Steps

After implementing Solution 1 (auto-wiring script):

```bash
# On Machine A (original)
git checkout -b fix/auto-wiring
python3 scripts/cortex_system_doctor.py --quick
python3 scripts/auto_wire_orchestrators.py --execute
python3 scripts/check_wiring_integrity.py
# Expected: 100% wiring coverage

git add src/orchestrators/ src/cortex_agents/ cortex-operations.yaml
git commit -m "fix: auto-wire planning orchestrator interactive mode"
git push origin fix/auto-wiring

# On Machine B (fresh pull)
git pull origin fix/auto-wiring
python3 scripts/check_wiring_integrity.py
# Expected: 100% wiring coverage (NO manual fixes needed)
```

**Success Criteria:** Machine B shows 100% wiring without running auto-wire script.

---

## 📚 References

- **Wiring Gap Analysis:** `cortex-brain/documents/analysis/interactive-workflow-wiring-gap-analysis.md`
- **Maintenance Prompt:** `.github/prompts/cortex-maintenance.prompt.md` (Phase 1.5, Phase 4)
- **Planning Orchestrator:** `src/orchestrators/planning/planning_orchestrator.py`
- **Interactive Session:** `src/orchestrators/planning/interactive_session.py`
- **Wiring Checker:** `scripts/check_wiring_integrity.py`
- **System Doctor:** `scripts/cortex_system_doctor.py`

---

## 🎯 Conclusion

**The maintenance scripts are working as designed** - they correctly identify wiring gaps. The problem is:

1. **No auto-repair mechanism** exists to FIX the gaps
2. **Reports are gitignored** so diagnostics don't persist
3. **Manual wiring is required** on each machine

**Solution:** Implement `auto_wire_orchestrators.py` to make wiring fixes commit-able and persistent across git operations.

**Next Step:** Create the auto-wiring script and update maintenance documentation.

---

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
