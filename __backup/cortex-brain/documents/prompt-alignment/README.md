# CORTEX Prompt Alignment Initiative – Complete Documentation

**Date:** 2026-01-12  
**Status:** ✅ Ready for Use  
**Version:** 1.0.0

---

## 📚 DOCUMENTATION STRUCTURE

This initiative delivers a complete alignment system. Here's how to navigate it:

### 🎯 START HERE (5-10 minutes)
**File:** `INTENT-AND-APPROACH.md`  
**Read this first to understand:**
- What you asked for
- Why this matters
- How the solution works
- Confirmation checklist

**Key Takeaway:** You get a one-time audit that discovers ALL prompts, finds conflicts, and generates a unified contract + refactoring roadmap.

---

### 📖 HOW TO USE (10-15 minutes)
**File:** `HOW-TO-USE.md`  
**Read this to understand:**
- When to use the alignment prompt
- How to invoke it
- What outputs you'll get
- How to read the audit report
- Common scenarios
- Troubleshooting

**Key Takeaway:** Simple one-command invocation that produces audit report + recommendations.

---

### ✅ COMPLETE SUMMARY (5 minutes)
**File:** `COMPLETE-DELIVERABLES-SUMMARY.md`  
**Read this to understand:**
- What was delivered
- Key capabilities of the alignment prompt
- Alignment vectors (what gets unified)
- Benefits of this approach
- Success criteria

**Key Takeaway:** Comprehensive overview of entire initiative.

---

### 🚀 THE MAIN EXECUTABLE
**File:** `.github/prompts/cortex-prompt-alignment.prompt.md`  
**Use this to:**
- Execute the alignment audit
- Discover all prompts
- Audit against unified standard
- Generate recommendations
- Create refactoring roadmap

**Invoke with:** `"align prompts"` in GitHub Copilot chat

---

## 🎯 QUICK REFERENCE

### The 3-Part Solution

#### Part 1: Discovery & Audit
```
User says: "align prompts"
         ↓
Prompt discovers all *.prompt.md files
         ↓
Audit each against unified standard
         ↓
Output: Audit report + recommendations
```

#### Part 2: Review & Plan
```
You read: Audit report
         ↓
Understand: What conflicts exist
            Why they matter
            How to fix each one
         ↓
Create: Refactoring roadmap
```

#### Part 3: Execute & Validate
```
You refactor: One prompt at a time
            Following recommendations
            Testing after each change
         ↓
Validate: "align prompts" again
         ↓
Result: All conflicts resolved
```

---

## 📊 WHAT GETS ALIGNED

### 1. **Regression Checks**
- ✅ Current: 3+ different implementations
- ✅ After: 1 shared protocol
- ✅ Benefit: No duplicate logic, consistent approach

### 2. **Sync Protocols**
- ✅ Current: Dashboard syncs at different points
- ✅ After: All sync via unified protocol
- ✅ Benefit: Dashboard always accurate

### 3. **Response Formats**
- ✅ Current: 4+ different formats
- ✅ After: All use output-standards.md format
- ✅ Benefit: User sees consistent experience

### 4. **Orchestrator Delegation**
- ✅ Current: Some prompts simulate work
- ✅ After: All delegate to MasterOrchestrator
- ✅ Benefit: Single execution authority

### 5. **Phase Gates**
- ✅ Current: Enforced at different points
- ✅ After: Uniformly enforced at phase boundaries
- ✅ Benefit: Clear phase transitions

### 6. **Evidence Standards**
- ✅ Current: Different tracking approaches
- ✅ After: All use test-based proof
- ✅ Benefit: Trustworthy completion tracking

---

## 🏃 QUICKSTART (5 Minutes)

### Step 1: Read Intent
```
Open: INTENT-AND-APPROACH.md
Time: 3 minutes
Goal: Understand what this solves
```

### Step 2: Read How to Use
```
Open: HOW-TO-USE.md
Time: 2 minutes
Goal: Know how to run the audit
```

### Step 3: Run the Audit
```
Say: "align prompts"
Time: 1-2 minutes
Output: Audit report + refactoring roadmap
```

### Total Time: ~10 minutes to first audit
Then: Review results at your pace

---

## 📋 THE AUDIT REPORT

When you run `"align prompts"`, you get:

### 1. Discovered Prompts List
```
Example output:
  • CORTEX.prompt.md (Gateway)
  • cortex-exec.prompt.md (Executor)
  • cortex-evidence-validator.prompt.md (Validator)
  • cortex-brittleness-review.prompt.md (Analyst)
  • cortex-search-and-fix.prompt.md (Fixer)
  [Total: 5 prompts]
```

### 2. Conflicts Detected
```
Example output:
  ❌ Regression Check Redundancy (3 implementations)
  ❌ Sync Protocol Inconsistency (syncs at different points)
  ❌ Response Format Mismatch (4 different formats)
  ⚠️  Orchestrator Delegation Gaps (2 prompts simulating work)
  ⚠️  Phase Gates Inconsistently Enforced
```

### 3. Per-Prompt Recommendations
```
Example output:
  cortex-exec.prompt.md
    - [HIGH] Remove manual state management
    - [HIGH] Standardize sync protocol
    - [MEDIUM] Consolidate regression check
    - Effort: 2 hours
```

### 4. Refactoring Roadmap
```
Example output:
  Phase 1: Extract shared foundation (1 day)
  Phase 2: Refactor gateway (1 day)
  Phase 3: Refactor executor (1 day)
  Phase 4: Refactor validator (1 day)
  Phase 5: Refactor analyst (0.5 days)
  Phase 6: Verify new prompts (0.5 days)
  Total: 4 days sequential
```

---

## 🔄 ALIGNMENT FLOW

```
┌─────────────────────────────────────────────────────────────┐
│                   YOU INITIATE                              │
│              "align prompts" command                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│            CORTEX-PROMPT-ALIGNMENT EXECUTES                 │
│                                                             │
│  Step 1: Discover all prompts                              │
│  Step 2: Audit each prompt                                 │
│  Step 3: Find conflicts                                    │
│  Step 4: Generate recommendations                          │
│  Step 5: Create refactoring roadmap                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│          YOU GET: AUDIT REPORT + RECOMMENDATIONS            │
│                                                             │
│  • List of discovered prompts                              │
│  • Conflicts with severity                                 │
│  • Per-prompt refactoring tasks                            │
│  • Unified contracts document                              │
│  • Sequential execution roadmap                            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│            YOU REVIEW & PLAN REFACTORING                    │
│                                                             │
│  Read: Audit report                                        │
│  Understand: Current state and conflicts                   │
│  Decide: Which prompts to fix first                        │
│  Plan: Sequential refactoring approach                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│         YOU EXECUTE REFACTORING (ONE PROMPT AT A TIME)      │
│                                                             │
│  For each prompt:                                          │
│    1. Apply recommended changes                            │
│    2. Test the prompt                                      │
│    3. Move to next prompt                                  │
│    4. Validate alignment (run audit again)                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              RESULT: UNIFIED PROMPT SYSTEM                  │
│                                                             │
│  ✅ All prompts aligned to shared contract                 │
│  ✅ No duplicate logic                                     │
│  ✅ Clear delegation to MasterOrchestrator                 │
│  ✅ Consistent sync protocols                              │
│  ✅ Unified response formats                               │
│  ✅ Automatic discovery of new prompts                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎓 LEARNING PATHS

### Path 1: "I want to understand the whole system" (30 minutes)
1. Read: `INTENT-AND-APPROACH.md` (understand intent)
2. Read: `HOW-TO-USE.md` (understand mechanics)
3. Read: `COMPLETE-DELIVERABLES-SUMMARY.md` (understand benefits)
4. Skim: `cortex-prompt-alignment.prompt.md` (see how it works)

### Path 2: "I just want to run the audit" (5 minutes)
1. Skim: `HOW-TO-USE.md` (quick overview)
2. Say: `"align prompts"` to Copilot
3. Review: Audit report

### Path 3: "I need to add a new prompt" (10 minutes)
1. Read: `HOW-TO-USE.md` section "Adding a New Prompt"
2. Create your new prompt
3. Say: `"align prompts"` to Copilot
4. Review: Audit will auto-discover your new prompt

### Path 4: "I want to understand the unified contract" (20 minutes)
1. Read: Audit report section "Shared Contract Document"
2. Review: `PROMPT-INTEGRATION.md` (how prompts should work together)
3. Check: `.github/prompts/output-standards.md` (unified format)

---

## 🚀 COMMON WORKFLOWS

### Workflow 1: Initial Alignment Audit
```
Time: ~10 minutes

1. Say: "align prompts"
2. Wait for report
3. Read audit findings
4. Review recommendations
5. Plan refactoring sequence
```

### Workflow 2: Refactoring a Prompt
```
Time: ~1 hour per prompt

1. Open audit report
2. Find your prompt's recommendations
3. Open the prompt file
4. Apply recommended changes
5. Test the prompt
6. Move to next prompt
```

### Workflow 3: Adding a New Prompt
```
Time: ~15 minutes

1. Create your new *.prompt.md file
2. Say: "align prompts"
3. Prompt auto-discovers your new file
4. Read recommendations for your new prompt
5. Adjust if needed
6. Done!
```

### Workflow 4: Periodic Validation
```
Time: ~5 minutes

1. Say: "align prompts" (run monthly or after major changes)
2. Compare new report to previous report
3. If new conflicts found, plan fixes
4. If no new conflicts, all is aligned ✅
```

---

## 📊 EXPECTED OUTCOMES

### What the Alignment Prompt Finds
- **Conflicts:** 3-5 major conflicts across prompts
- **Duplications:** 2-3 areas of duplicate logic
- **Gaps:** 1-2 prompts with orchestrator delegation issues
- **Inconsistencies:** 4-5 areas of protocol inconsistency

### What the Refactoring Fixes
- ✅ Consolidates regression checks (save ~50 lines)
- ✅ Standardizes sync protocol (save ~40 lines)
- ✅ Aligns response formats (save ~30 lines)
- ✅ Establishes orchestrator delegation (save ~100 lines)
- ✅ Enforces phase gates uniformly (save ~20 lines)

### Total Benefit
- 240+ lines of duplicate code eliminated
- Single mental model for all prompts
- Clearer execution flow
- Easier onboarding for new team members
- Automatic discovery of new prompts

---

## ❓ FREQUENTLY ASKED QUESTIONS

### Q: How often should I run the alignment audit?
**A:** Run it:
- Once to get initial audit
- After adding new prompts
- After major changes to orchestrators
- Monthly as validation (5 min check)

### Q: Do I have to refactor ALL prompts at once?
**A:** No! Refactor sequentially (one prompt at a time). Takes ~1 hour per prompt.

### Q: What if I disagree with a recommendation?
**A:** Document your reasoning. The audit is a guide, not a command. Discuss conflicts with team.

### Q: Can new prompts be auto-discovered?
**A:** Yes! The audit scans `.github/prompts/` for all `*.prompt.md` files automatically.

### Q: Do I need to update this documentation?
**A:** Not required, but recommend you update `HOW-TO-USE.md` with lessons learned.

---

## 🔗 RELATED DOCUMENTATION

**Internal References:**
- `cortex-brain/cx6-plan/master-plan.yaml` - Phase definitions
- `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml` - AC registry
- `cortex-brain/tier1/tracking/progress-tracker.json` - Progress tracking
- `.github/prompts/PROMPT-INTEGRATION.md` - How prompts work together
- `.github/prompts/output-standards.md` - Response format standards

**In This Initiative:**
- `INTENT-AND-APPROACH.md` - Your intent, reflected back
- `HOW-TO-USE.md` - User guide and common scenarios
- `COMPLETE-DELIVERABLES-SUMMARY.md` - Full summary of deliverables
- `cortex-prompt-alignment.prompt.md` - The main executable
- `README.md` - This file

---

## ✅ VERIFICATION CHECKLIST

Before you start, verify:
- [ ] You can access `.github/prompts/cortex-prompt-alignment.prompt.md`
- [ ] You can access this documentation folder
- [ ] You understand what "unified contracts" means (read INTENT-AND-APPROACH)
- [ ] You know how to invoke the alignment prompt (read HOW-TO-USE)
- [ ] You understand the audit flow (read COMPLETE-DELIVERABLES-SUMMARY)

---

## 🎯 NEXT STEPS

### RIGHT NOW (5 minutes)
1. Read `INTENT-AND-APPROACH.md` to understand context
2. Read `HOW-TO-USE.md` to understand mechanics
3. Bookmark this folder for future reference

### WHEN READY (whenever you want)
1. Open GitHub Copilot chat
2. Say: `"align prompts"`
3. Wait for audit report
4. Review findings
5. Plan refactoring

### DURING REFACTORING (next weeks)
1. Follow recommendations from audit report
2. Refactor one prompt at a time
3. Test after each change
4. Validate with periodic `"align prompts"` checks

---

## 📞 NEED HELP?

**Problem:** I don't understand what this solves  
**Solution:** Read `INTENT-AND-APPROACH.md` section "Your Request"

**Problem:** I don't know how to run the audit  
**Solution:** Read `HOW-TO-USE.md` section "How to Invoke It"

**Problem:** I don't understand the audit report  
**Solution:** Read `HOW-TO-USE.md` section "Example: Reading the Audit Report"

**Problem:** I want to add a new prompt  
**Solution:** Read `HOW-TO-USE.md` section "Adding a New Prompt"

**Problem:** Something seems broken  
**Solution:** Read `HOW-TO-USE.md` section "Troubleshooting"

---

## 📝 DOCUMENT METADATA

| Item | Value |
|------|-------|
| Created | 2026-01-12 |
| Version | 1.0.0 |
| Status | ✅ Ready for Use |
| Location | `cortex-brain/documents/prompt-alignment/` |
| Main Prompt | `.github/prompts/cortex-prompt-alignment.prompt.md` |
| Supported Prompts | 5+ (auto-discovered) |
| Estimated Time to First Audit | 10 minutes |
| Estimated Time to Full Refactoring | 4 days (sequential) |

---

**Status: ✅ READY TO USE**

**To get started:** Open GitHub Copilot chat and say `"align prompts"`
