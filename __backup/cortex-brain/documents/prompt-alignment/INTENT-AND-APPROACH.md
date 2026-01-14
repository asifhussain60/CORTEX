# CORTEX Prompt Alignment Initiative – Intent & Approach Summary

**Date:** 2026-01-12  
**Status:** Planning Complete → Ready for Execution  
**Document Purpose:** Confirm understanding before proceeding with refactoring

---

## 🎯 YOUR REQUEST (Reflected Back)

### What You Asked For
> "Create an efficient cortex-prompt-alignment.prompt.md. Incorporate requirements from #chat01.md for CORTEX.prompt.md refactoring. This new prompt should align **remaining** .github/prompts/*.prompt.md files holistically with cx6-plan and all dependencies. Don't hardcode prompts—do discovery. Create a **cohesive and complementary set** of prompts instead of fixing each individually."

### Why This Matters
- **Current State:** 5+ prompts working in silos with duplicated logic, conflicting instructions, and missing orchestrator delegation
- **Problem:** Manual prompt-by-prompt alignment misses critical interdependencies and conflicts
- **Goal:** Single unified system where prompts are complementary specialists, not isolated actors

---

## 🔄 YOUR EVOLUTION (From Chat01)

| Issue | Challenge | Refactoring Approach |
|-------|-----------|----------------------|
| "Prompt simulates orchestration manually" | User challenged: Shouldn't MasterOrchestrator be in charge? | ✅ This alignment prompt audits if ALL prompts delegate to MasterOrchestrator |
| "One prompt does too much" | User asked: What else are you wrong about? | ✅ This prompt discovers ALL prompts, audits ALL assumptions |
| "No shared mental model" | User said: Check holistically, verify against implementation | ✅ This prompt validates current architecture against actual code (master_orchestrator.py, governance_merger.py, etc.) |

---

## 🏗️ WHAT THE ALIGNMENT PROMPT DOES

### Discovery Phase (Automatic)
- Scans `.github/prompts/` for ALL `*.prompt.md` files (not hardcoded)
- Includes new prompts automatically if they match pattern
- Maps relationships between prompts (which calls which)

### Audit Phase (Verification)
For each discovered prompt, it checks:
- ✅ Is it delegating to MasterOrchestrator or simulating work?
- ✅ Are regression checks consistent with other prompts?
- ✅ Are sync protocols (dashboard) standardized?
- ✅ Are response formats aligned to output-standards.md?
- ✅ Does it read/write state correctly?
- ✅ Does it follow phase gates?

### Conflict Detection (Analysis)
Identifies:
- 🚨 Duplicate regression checks (suggests consolidation)
- 🚨 Sync protocol inconsistencies (suggests standardization)
- 🚨 Response format mismatches (suggests unification)
- 🚨 Orchestrator delegation gaps (suggests refactoring)
- 🚨 Manual state manipulation (suggests delegation)

### Unified Contract Generation (Synthesis)
Creates:
- 📋 Shared data model (what all prompts agree on)
- 📋 Shared regression protocol (single definitive version)
- 📋 Shared sync protocol (single definitive version)
- 📋 Shared response format (references output-standards.md)
- 📋 Shared orchestrator delegation pattern (MasterOrchestrator only)

### Per-Prompt Recommendations (Action Plan)
For each prompt, documents:
- What's working (keep as-is)
- What conflicts (fix this)
- How to fix it (specific changes needed)
- Effort estimate (hours required)

---

## 🔗 HOW IT INTEGRATES WITH CX6-PLAN

### Alignment Vectors
```
cx6-plan/master-plan.yaml
  ↓
  All prompts MUST execute against SAME phases/AC-IDs
  ↓
  Alignment audit VERIFIES this consistency

AC-INDEX.yaml (AC-ID registry)
  ↓
  All prompts MUST use same evidence standards
  ↓
  Alignment audit VERIFIES this consistency

progress-tracker.json (source of truth)
  ↓
  All prompts MUST update same tracker
  ↓
  Alignment audit VERIFIES this consistency

plan-viewer-data.json (synced dashboard)
  ↓
  All prompts MUST sync via same protocol
  ↓
  Alignment audit VERIFIES this consistency
```

### What This Prevents
- ❌ One prompt syncing dashboard while another doesn't
- ❌ One prompt using different evidence standards than another
- ❌ One prompt enforcing phase gates while another ignores them
- ❌ One prompt reading state directly while another delegates to orchestrator
- ❌ New prompts accidentally breaking the unified system

---

## 📋 OUTPUT YOU'LL GET

### 1. Alignment Audit Report
```
Sample excerpt:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CORTEX PROMPT ALIGNMENT AUDIT REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DISCOVERED PROMPTS: 5
  • CORTEX.prompt.md (Gateway)
  • cortex-exec.prompt.md (Executor)
  • cortex-evidence-validator.prompt.md (Validator)
  • cortex-brittleness-review.prompt.md (Analyst)
  • cortex-search-and-fix.prompt.md (Fixer)

CONFLICTS DETECTED: 3 HIGH PRIORITY
  ❌ Regression Check Redundancy (3 different implementations)
  ❌ Sync Protocol Inconsistency (syncs at different points)
  ❌ Response Format Mismatch (3 different formats)

ORCHESTRATOR DELEGATION: GAPS FOUND
  ⚠️ cortex-exec.prompt.md (still reads state directly)
  ⚠️ cortex-evidence-validator.prompt.md (manual test parsing)

PHASE GATES: INCONSISTENTLY ENFORCED
  ⚠️ cortex-exec.prompt.md (enforces after AC-ID)
  ⚠️ CORTEX.prompt.md (enforces after phase)
  → Should be: All enforce at phase boundaries uniformly
```

### 2. Per-Prompt Alignment Cards
```
Prompt: cortex-exec.prompt.md
Version: 3.0.0
Status: NEEDS REFACTOR

Alignment Issues:
  [HIGH] Manual state read/update (should delegate)
  [HIGH] Sync protocol differs from other prompts
  [MEDIUM] Regression check duplicates 2 others

Recommended Fixes:
  1. Add MasterOrchestrator delegation statement
  2. Consolidate regression check to shared protocol
  3. Standardize sync to unified pattern
```

### 3. Shared Contract Document
```
UNIFIED DATA MODEL:
  - AC-ID: AC-{CATEGORY}-{NNN}
  - Phase: 1-4 from master-plan.yaml
  - Evidence: Test results (PASSED/FAILED/SKIPPED)
  - Completion: Evidence-backed, never aspirational

UNIFIED REGRESSION CHECK:
  1. AC-INDEX.yaml parses ✓
  2. progress-tracker.json parses ✓
  3. master-plan.yaml parses ✓
  → If any fails: HALT

UNIFIED SYNC PROTOCOL:
  After EVERY state write:
  1. Update progress-tracker.json
  2. python3 scripts/sync_plan_viewer_data.py
  3. Verify: plan-viewer-data.json matches
```

### 4. Refactoring Roadmap
```
PHASE 1: Establish Shared Foundation (1 day)
PHASE 2: Refactor Gateway (cortex.prompt.md) (1 day)
PHASE 3: Refactor Executor (cortex-exec.prompt.md) (1 day)
PHASE 4: Refactor Validator (cortex-evidence-validator.prompt.md) (1 day)
PHASE 5: Refactor Analyst (cortex-brittleness-review.prompt.md) (0.5 days)
PHASE 6: Verify New Prompts (0.5 days)

Total: 4 days (sequential execution)
```

---

## 🎯 NEXT STEPS (After Alignment Audit)

### You Will Have:
1. ✅ Complete audit of ALL prompts
2. ✅ Unified contract that ALL prompts must follow
3. ✅ Specific refactoring tasks per prompt
4. ✅ Effort estimates for each change
5. ✅ Clear path to coherent system

### You Can Then:
- Use the audit report to guide refactoring
- Execute refactoring sequentially (one prompt at a time)
- Validate each refactored prompt against shared contract
- Test integration after each prompt is updated
- Verify dashboard sync works uniformly

### Result:
- **One unified system** where prompts are complementary specialists
- **Clear mental model** for future prompt development
- **Elimination of conflicts** that could cause failures
- **Auto-discovery** mechanism for new prompts
- **Self-documenting contracts** that prevent drift

---

## ✅ CONFIRMATION CHECKLIST

Before I generate the alignment audit, confirm:

- [x] You want **automatic discovery** (scan folder for ALL prompts, not hardcoded)?
- [x] You want **shared contracts** (one regression check, one sync protocol, one response format)?
- [x] You want **orchestrator delegation audit** (verify all prompts delegate to MasterOrchestrator)?
- [x] You want **per-prompt recommendations** (specific refactoring tasks with effort estimates)?
- [x] You want **unified data model** (all prompts speak same language)?
- [x] You want **phase gate consistency** (all enforce gates at same points)?
- [x] You want **evidence standards alignment** (all use same test-based proof)?
- [x] You want **sequential refactoring plan** (not all at once)?
- [x] You want **integration with cx6-plan** (master-plan, AC-INDEX, tracker, dashboard)?

---

## 🚀 READY TO EXECUTE

**The `cortex-prompt-alignment.prompt.md` is now available in `.github/prompts/`**

To run the alignment audit:
```bash
# Invoke the alignment prompt
# User says: "align prompts" or "coordinate all prompts"

# Output: Comprehensive audit + recommendations
```

**This is a ONE-TIME orchestration prompt that:**
- Audits current state
- Generates recommendations
- Provides refactoring roadmap
- Documents unified contracts

**After refactoring, you'll have:**
- All prompts following shared contracts
- No duplicate logic
- Clear delegation to MasterOrchestrator
- Unified response formats
- Consistent sync protocols
- Auto-discovery of new prompts

---

**Status: Ready for Execution** ✅
