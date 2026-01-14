# How to Use cortex-prompt-alignment.prompt.md

**Quick Guide to Executing the Alignment Orchestrator**

---

## 🎯 What This Prompt Does (In Plain English)

This prompt is a **one-time auditor** that:
1. **Discovers** all prompts in `.github/prompts/` (including new ones)
2. **Audits** each prompt against a unified standard
3. **Finds conflicts** (duplicate logic, inconsistent protocols)
4. **Generates recommendations** (specific refactoring tasks)
5. **Creates a roadmap** (sequential refactoring plan)

**Result:** You get a detailed audit report + specific next steps to make all prompts work as one cohesive system.

---

## ✅ WHEN TO USE IT

Use this prompt when:
- ✅ Adding new prompts to `.github/prompts/`
- ✅ Refactoring existing prompts
- ✅ Ensuring consistency across the system
- ✅ Onboarding new team members
- ✅ Periodic alignment checks (monthly/quarterly)
- ✅ Integrating major changes to MasterOrchestrator

**Do NOT use this prompt for:**
- ❌ Day-to-day implementation work (use `cortex-exec.prompt.md`)
- ❌ Running tests (use `cortex-evidence-validator.prompt.md`)
- ❌ Risk analysis (use `cortex-brittleness-review.prompt.md`)

---

## 🚀 HOW TO INVOKE IT

### Option 1: From GitHub Copilot Chat
```
User: "align prompts"
User: "coordinate all prompts"
User: "check prompt cohesion"

→ Copilot loads cortex-prompt-alignment.prompt.md
→ Prompt executes discovery → audit → recommendations
```

### Option 2: Manually (if you prefer explicit control)
```bash
# Create a new chat with this file loaded as context:
# @cortex-prompt-alignment.prompt.md

# Then ask:
User: "execute the alignment audit"
```

---

## 📊 WHAT YOU'LL GET

### Primary Output: Audit Report
**Location:** `cortex-brain/documents/prompt-alignment/alignment-audit-{timestamp}.md`

Contains:
- List of discovered prompts
- Conflicts detected (with severity)
- Per-prompt alignment issues
- Orchestrator delegation gaps
- Regression check redundancies
- Sync protocol inconsistencies
- Response format mismatches

### Secondary Output: Refactoring Roadmap
**Location:** `cortex-brain/documents/prompt-alignment/alignment-refactoring-plan.yaml`

Contains:
- Per-prompt refactoring tasks
- Specific line numbers to change
- Before/after examples
- Effort estimates
- Execution sequence
- Success criteria per prompt

### Tertiary Output: Unified Contract
**Location:** `cortex-brain/documents/prompt-alignment/unified-prompt-contract.yaml`

Contains:
- Shared data model (what all prompts agree on)
- Shared regression check protocol
- Shared sync protocol
- Shared response format
- Shared orchestrator delegation pattern
- Shared phase gate enforcement
- Shared evidence standards

---

## 🔄 EXECUTION FLOW

### Step 1: Run Alignment Audit
```
User: "align prompts"
→ Prompt discovers all prompts
→ Prompt audits each against unified standard
→ Prompt generates audit report + recommendations
```

### Step 2: Review Results
```
Output: Audit report with conflicts & recommendations

Typical findings:
  ❌ 3 redundant regression checks
  ❌ 2 different sync protocols
  ❌ 4 response format variations
  ⚠️ 2 prompts with manual state manipulation
  ⚠️ Phase gates enforced inconsistently
```

### Step 3: Plan Refactoring
```
Output: Refactoring roadmap with per-prompt tasks

Typical roadmap:
  Phase 1: Extract shared protocols (1 day)
  Phase 2: Refactor gateway (1 day)
  Phase 3: Refactor executor (1 day)
  Phase 4: Refactor validator (1 day)
  Phase 5: Refactor analyst (0.5 days)
  Phase 6: Verify new prompts (0.5 days)
```

### Step 4: Execute Refactoring
```
Use the recommendations from the audit report.

For each prompt:
  1. Open the prompt in editor
  2. Make changes recommended in audit report
  3. Test the prompt (run a simple command)
  4. Move to next prompt
```

### Step 5: Validate (Optional)
```
User: "validate prompt alignment"
→ Prompt runs same audit again
→ Confirms all conflicts resolved
→ Reports: "✅ All prompts aligned"
```

---

## 💡 EXAMPLE: Reading the Audit Report

### Conflict: Regression Check Redundancy
```
❌ REGRESSION CHECK REDUNDANCY

Found 3 implementations of the same check:

  cortex-exec.prompt.md (Lines 45-72)
  - Checks AC-INDEX.yaml parses
  - Checks progress-tracker.json parses
  - Checks master-plan.yaml parses

  cortex-evidence-validator.prompt.md (Lines 31-58)
  - Checks AC-INDEX.yaml exists
  - Checks progress-tracker.json valid
  - Checks plan-viewer-data.json synced

  CORTEX.prompt.md (Lines 128-145)
  - Checks AC-INDEX.yaml can be loaded
  - Checks tracker.json is valid JSON

RECOMMENDATION:
  Create ONE shared regression check protocol
  All prompts call the same procedure:
    python3 scripts/validate_plan_integrity.py
  Delete duplicate code from each prompt
  Add reference: "See shared contract for regression protocol"
```

### Gap: Orchestrator Delegation
```
⚠️ ORCHESTRATOR DELEGATION GAP

Prompt: cortex-exec.prompt.md (Lines 200-250)

Issue:
  This prompt reads progress-tracker.json directly
  Selects next AC-ID manually
  Updates state directly
  
  Per CORTEX architecture:
  - MasterOrchestrator should read tracker
  - TodoManager should select AC-IDs
  - MasterOrchestrator should update state

RECOMMENDATION:
  Replace manual state management with:
    python3 -m src.main "implement {ac_id}" --orchestrator master
  
  Remove lines 200-250 (manual selection logic)
  Add lines 205-210 (orchestrator delegation)
  Result: Same behavior, clear responsibility
```

---

## 🎯 SUCCESS CRITERIA

After executing the alignment audit, you should have:

- ✅ **Complete inventory** of all prompts
- ✅ **Clear conflicts** documented with severity
- ✅ **Specific recommendations** for each prompt
- ✅ **Unified contracts** that all prompts must follow
- ✅ **Execution roadmap** with effort estimates
- ✅ **Before/after examples** for refactoring
- ✅ **Validation checklist** for confirming success

---

## 📋 CHECKLISTS FOR COMMON SCENARIOS

### Scenario 1: Adding a New Prompt
```
You created: cortex-new-feature.prompt.md

Step 1: Run alignment audit
  → Prompt will auto-discover your new prompt
  → Will check it against unified contract
  → Will report any issues

Step 2: Review audit report
  → Look for conflicts with your new prompt
  → Check if it follows shared protocols

Step 3: Fix any issues
  → Use recommendations from audit
  → Ensure it delegates to MasterOrchestrator
  → Ensure it uses shared sync protocol
```

### Scenario 2: Fixing Broken Integration
```
Problem: Dashboard not syncing after prompt runs

Step 1: Run alignment audit
  → Will find which prompts don't sync
  → Will find inconsistent sync protocols

Step 2: Review recommendations
  → Use unified sync protocol from shared contract
  → Apply to broken prompts

Step 3: Test
  → Run broken prompt again
  → Verify dashboard syncs now
```

### Scenario 3: Onboarding New Team Member
```
New member doesn't understand how prompts work together

Step 1: Have them read the audit report
  → Shows all prompts + roles
  → Shows how they connect
  → Shows unified contracts

Step 2: Have them review refactoring roadmap
  → Shows execution patterns
  → Shows coordination model
  → Shows delegation architecture

Step 3: Direct them to shared contract
  → Shows unified data model
  → Shows standard protocols
  → Shows what all prompts must follow
```

---

## 🔄 MAINTENANCE (Monthly or After Major Changes)

**Re-run alignment audit when:**
- New prompts added
- Major changes to orchestrators
- Plan structure changes
- New AC-ID categories added
- Integration failures discovered

**Quick re-run:**
```bash
User: "validate prompt alignment"
→ Runs lightweight check
→ Reports any new conflicts
```

---

## 🚫 COMMON MISTAKES TO AVOID

| ❌ Don't | ✅ Do Instead |
|----------|-------------|
| Hardcode prompt names | Let prompt discover them |
| Edit prompts directly without audit | Run audit first, then refactor by plan |
| Mix manual state updates with orchestrator calls | Always delegate to MasterOrchestrator |
| Sync dashboard at different points | Use unified sync protocol |
| Create new regression checks | Reference shared protocol |
| Forget to sync after updating prompts | Run sync script after every refactoring session |
| Deploy prompt changes without validation | Run alignment validator after changes |

---

## 📞 TROUBLESHOOTING

### Problem: "Alignment prompt not discovering all prompts"
**Solution:**
- Verify `.github/prompts/` exists
- Check that your new prompt has `.prompt.md` extension
- Ensure file is readable (not locked/ignored)
- Re-run prompt with verbose output

### Problem: "Audit says my prompt is broken, but it works"
**Solution:**
- Re-read the specific conflict in audit report
- Check if conflict is real (e.g., does regression check truly duplicate others?)
- If you disagree, document the reasoning
- Discuss with team before refactoring

### Problem: "Refactoring roadmap seems too long"
**Solution:**
- Roadmap is SEQUENTIAL (one prompt at a time)
- Each step is ~1 day or less
- You can do it incrementally (1 prompt/week)
- You don't need to do everything at once

---

## 🎓 LEARNING RESOURCES

To understand the unified contract better:
1. Read: `cortex-brain/documents/prompt-alignment/unified-prompt-contract.yaml`
2. Review: `.github/prompts/PROMPT-INTEGRATION.md` (how prompts should work together)
3. Check: `.github/prompts/output-standards.md` (unified response format)
4. Study: `src/orchestrators/core/master_orchestrator.py` (how orchestrators actually work)

---

## 📝 NEXT STEPS

1. **Read this guide** (you're doing it now ✓)
2. **Review INTENT-AND-APPROACH.md** (understand what alignment means)
3. **Run alignment audit** (invoke prompt, get recommendations)
4. **Review audit report** (understand current conflicts)
5. **Plan refactoring** (decide which prompts to fix first)
6. **Execute refactoring** (fix one prompt at a time)
7. **Validate** (confirm all conflicts resolved)
8. **Document** (update this guide with learnings)

---

**Status: Ready to Use** ✅

To get started: Say `"align prompts"` to GitHub Copilot
