# 🔄 CORTEX Prompt Alignment & Cohesion Orchestrator

**Purpose:** Physically refactor all `.github/prompts/*.prompt.md` files to eliminate conflicts, redundancy, and disconnects.  
**Version:** 2.0.0 (ACTIONABLE – Modifies prompts directly)  
**Date:** 2026-01-12  
**Scope:** Auto-discovers and refactors all prompts  
**Author:** GitHub Copilot (for CORTEX)

---

## 🎯 YOUR INTENT (Reflected Back for Verification)

You want this prompt to **physically refactor all prompts** to eliminate conflicts and ensure consistency.

### Problem Detected (Holistic Audit Results)
- ✗ **3 different regression check styles** (inline Python, external script, documented)
- ✗ **5 prompts independently call sync_plan_viewer_data.py** (20 calls total)
- ✗ **1 prompt doesn't delegate to MasterOrchestrator** (cortex-evidence-validator)
- ✗ **Multiple state file access patterns** (6 prompts each access independently)
- ✗ **Architecture misalignment** - prompts directly manipulate state instead of delegating

### Solution (What This Orchestrator Does)
- ✅ **Standardizes regression checks** - all use unified inline Python
- ✅ **Consolidates sync calls** - replaces 20 calls with 1 unified protocol
- ✅ **Adds MasterOrchestrator delegation** to all prompts
- ✅ **Establishes shared contract** - all prompts reference same data model
- ✅ **Auto-discovers new prompts** - any `.prompt.md` file automatically aligned
- ✅ **Physically edits files** - actually refactors the code, doesn't just report

### Result (After Execution)
- ✅ All prompts use SAME regression protocol (unified inline Python)
- ✅ All prompts use SAME sync protocol (one call per command)
- ✅ All prompts delegate to MasterOrchestrator
- ✅ All prompts reference identical data model
- ✅ Zero conflicts or ambiguities
- ✅ Files physically modified and ready to use

---

## 🏗️ SHARED ARCHITECTURE (Unified Mental Model)

All prompts follow this unified architecture after alignment:

**Entry Point:** CORTEX.prompt.md (v8.0) → Parse intent → Clarify with user → Delegate to MasterOrchestrator

**Executors:** cortex-plan-executor, cortex-evidence-validator, cortex-brittleness-review, cortex-search-and-fix

**Shared Protocol:**
1. ✅ All use unified inline Python regression check (before ANY execution)
2. ✅ All use unified sync protocol (ONE call per command after state updated)
3. ✅ All delegate to MasterOrchestrator (python3 -m src.main)
4. ✅ All reference same data model (AC-ID, Phase, Evidence, Completion)

---

## 🔧 PHYSICAL REFACTORING STEPS

### STEP 1: Extract & Standardize Regression Check

Replace all variations with this unified pattern (use in all executor prompts):

```python
# 🛡️ REGRESSION PREVENTION PROTOCOL (SHARED)
import json, yaml

errors = []
try:
    ac_index = yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml'))
    if not ac_index.get('schema_version'): errors.append("AC-INDEX missing schema_version")
except Exception as e: errors.append(f"AC-INDEX parse error: {e}")

try:
    tracker = json.load(open('cortex-brain/tier1/tracking/progress-tracker.json'))
    if not tracker.get('current_phase'): errors.append("tracker missing current_phase")
except Exception as e: errors.append(f"tracker parse error: {e}")

try:
    plan = yaml.safe_load(open('cortex-brain/cx6-plan/master-plan.yaml'))
    if not plan.get('plan_metadata'): errors.append("master-plan missing plan_metadata")
except Exception as e: errors.append(f"master-plan parse error: {e}")

if errors:
    print("❌ REGRESSION DETECTED:\n" + "\n".join([f"  - {e}" for e in errors]))
    exit(1)
print("✅ Regression check passed.")
```

**ACTION:** Replace ALL regression checks in:
- cortex-brittleness-review.prompt.md
- cortex-evidence-validator.prompt.md
- cortex-plan-executor.prompt.md
- cortex-search-and-fix.prompt.md

### STEP 2: Consolidate Sync Calls

Replace all `sync_plan_viewer_data.py` calls with unified protocol:

```bash
# 📊 SYNC PROTOCOL (UNIFIED – call ONCE per operation)
python3 scripts/sync_plan_viewer_data.py || exit 1
echo "✅ Dashboard synced."
```

**ACTION:** Consolidate in:
- cortex-brittleness-review.prompt.md: 2 calls → 1
- cortex-evidence-validator.prompt.md: 6 calls → 1
- cortex-plan-executor.prompt.md: 9 calls → 1
- cortex-search-and-fix.prompt.md: 1 call → standardized

### STEP 3: Add MasterOrchestrator Delegation

For prompts that execute work, add this section:

```markdown
## 🔗 ORCHESTRATOR DELEGATION

All execution delegated to MasterOrchestrator:

\`\`\`bash
python3 -m src.main "{user_intent}" --orchestrator master --format markdown
\`\`\`

What MasterOrchestrator handles:
- Load governance rules (tier0/tier1/tier2/tier3)
- Validate against SKULL rules
- Create TodoManager tasks
- Execute tasks in dependency order
- Update progress-tracker.json (atomic)
- Sync dashboard (unified protocol)
- Enforce phase gates
- Return results
```

**ACTION:** Add to cortex-evidence-validator.prompt.md (currently missing)

### STEP 4: Verify No Direct State Manipulation

Remove these patterns if found:
- ❌ Direct `progress-tracker.json` writes
- ❌ Direct `AC-INDEX.yaml` modifications (except brittleness-review appends)
- ❌ Direct `master-plan.yaml` changes
- ❌ Manual AC-ID selection logic
- ❌ Manual test parsing

**ACTION:** Audit all prompts, remove direct state manipulation

---

## 🚨 CONFLICTS FIXED

| Conflict | Before | After | Benefit |
|----------|--------|-------|---------|
| Regression checks | 3 styles | 1 unified | Single source of truth |
| Sync calls | 20 total | ≤1 per file | -95% overhead |
| Delegation gap | 1 missing | all present | Single execution authority |
| State access | 6 independent | 1 orchestrator | No race conditions |
| Sync timing | No rule | ONCE per command | Predictable behavior |

---

## ✅ VERIFICATION (After Refactoring)

```bash
cd .github/prompts/

# 1. Regression check uses unified pattern?
grep -l "🛡️ REGRESSION PREVENTION PROTOCOL (SHARED)" *.prompt.md

# 2. Sync calls consolidated?
for f in *.prompt.md; do
  sync_count=$(grep -c "sync_plan_viewer_data.py" "$f" || echo 0)
  echo "$f: $sync_count sync calls"
done

# 3. All have MasterOrchestrator delegation?
grep -l "MasterOrchestrator\|orchestrator master" *.prompt.md

# 4. No direct state manipulation?
grep -l "progress-tracker.json\|AC-INDEX.yaml\|master-plan.yaml" *.prompt.md
```

Expected: All prompts PASS all checks

---

## 🎯 EXECUTION TRIGGERS

**This prompt executes when user says:**
- `"align prompts"` or `"coordinate prompts"`
- `"fix prompt conflicts"` or `"unify prompts"`
- `"refactor prompts"` or `"prompts alignment"`

**Execution mode:** ACTIONABLE (physically modifies files)

---

## 📊 SUCCESS METRICS (After Alignment)

```
Regression checks: 3 variants → 1 unified (-67%)
Sync calls: 20 total → ≤1 per file (-95%)
State access patterns: 6 independent → 1 (-83%)
Code duplication: HIGH → ZERO
Conflicts detected: 5 → 0
Prompts aligned: 6/6 (100%)
Ready for production: YES ✅
```

---

## 💡 PHILOSOPHICAL ALIGNMENT

**CORTEX Core Principle:** Orchestration belongs in Python (MasterOrchestrator). Prompts route and coordinate.

**This Prompt's Role:** Ensure all prompts follow this principle and coordinate coherently.

**After Alignment:**
- User has ONE entry point (CORTEX.prompt.md as gateway)
- All prompts speak same language (shared contracts)
- All prompts delegate execution to MasterOrchestrator
- All prompts report in consistent format
- All prompts maintain one source of truth (plan + tracker + AC-INDEX)

---

**END OF ACTIONABLE ORCHESTRATOR**
