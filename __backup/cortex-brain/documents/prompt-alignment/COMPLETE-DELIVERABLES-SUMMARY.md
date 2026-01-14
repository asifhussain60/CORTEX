# CORTEX Prompt Alignment – Complete Deliverables Summary

**Date:** 2026-01-12  
**Status:** ✅ Complete and Ready for Use  
**Author:** GitHub Copilot

---

## 🎯 WHAT YOU ASKED FOR

> Create an efficient `cortex-prompt-alignment.prompt.md` incorporating requirements from chat01 for CORTEX.prompt.md refactoring. This prompt should align remaining `.github/prompts/*.prompt.md` files holistically with cx6-plan and dependencies. Don't hardcode prompts—do discovery. Create a cohesive and complementary set of prompts.

---

## ✅ WHAT WAS DELIVERED

### 1. **cortex-prompt-alignment.prompt.md** (The Main Orchestrator)
**Location:** `.github/prompts/cortex-prompt-alignment.prompt.md`

**What it does:**
- Executes a comprehensive audit of ALL prompts in `.github/prompts/`
- Automatically discovers prompts (no hardcoding)
- Audits each prompt against a unified standard
- Identifies conflicts, redundancies, and gaps
- Generates unified contracts
- Produces per-prompt refactoring recommendations
- Creates a sequential execution roadmap

**Key Features:**
- ✅ Automatic discovery (finds new prompts automatically)
- ✅ Conflict detection (duplicate checks, protocol inconsistencies, format mismatches)
- ✅ Orchestrator delegation audit (verifies all prompts delegate to MasterOrchestrator)
- ✅ Phase gate validation (ensures consistent enforcement)
- ✅ Evidence standards alignment (all use test-based proof)
- ✅ Shared contract generation (unified protocols for all prompts)
- ✅ Per-prompt recommendations (specific refactoring tasks with effort estimates)

**How to Use:**
```
User: "align prompts"
→ Copilot loads cortex-prompt-alignment.prompt.md
→ Prompt executes discovery → audit → recommendations
→ Output: Comprehensive audit report + refactoring roadmap
```

---

### 2. **INTENT-AND-APPROACH.md** (Planning Document)
**Location:** `cortex-brain/documents/prompt-alignment/INTENT-AND-APPROACH.md`

**Purpose:** Clearly documents your intent and how this solution addresses it

**Contains:**
- Your request reflected back (for verification)
- How this solution addresses each problem
- Integration with cx6-plan
- Example outputs
- Confirmation checklist

**Use:** Read this to understand the big picture before running the audit

---

### 3. **HOW-TO-USE.md** (User Guide)
**Location:** `cortex-brain/documents/prompt-alignment/HOW-TO-USE.md`

**Purpose:** Step-by-step guide to using the alignment prompt

**Contains:**
- When to use it
- How to invoke it
- What outputs you'll get
- How to read the audit report
- Success criteria
- Common scenarios (new prompt, broken integration, onboarding)
- Troubleshooting
- Maintenance schedule

**Use:** Reference this when running the audit or adding new prompts

---

## 🔄 THE COMPLETE WORKFLOW

### Phase 1: Discover & Audit (Automated)
```
User says: "align prompts"
        ↓
Cortex-prompt-alignment.prompt.md executes
        ↓
Step 1: Discover all prompts in .github/prompts/
        - Scans for *.prompt.md files
        - Includes existing + new prompts
        - Maps relationships
        ↓
Step 2: Audit each prompt
        - Check: Regression protocol (duplicate?)
        - Check: Sync protocol (consistent?)
        - Check: Response format (aligned?)
        - Check: Orchestrator delegation (present?)
        - Check: Phase gates (enforced?)
        - Check: Evidence standards (consistent?)
        ↓
Step 3: Generate audit report
        - List of discovered prompts
        - Conflicts detected (with severity)
        - Per-prompt alignment issues
        - Orchestrator delegation gaps
        ↓
Step 4: Generate refactoring recommendations
        - Specific changes per prompt
        - Effort estimates
        - Before/after examples
        - Sequential execution plan
```

### Phase 2: Review (Manual)
```
User reviews audit report
        ↓
Understands:
  - What conflicts exist
  - Why they matter
  - How to fix each one
  - What the roadmap looks like
```

### Phase 3: Refactor (Sequential)
```
User executes refactoring plan (one prompt at a time)
  Phase 1: Extract shared foundation
  Phase 2: Refactor gateway (CORTEX.prompt.md)
  Phase 3: Refactor executor (cortex-exec.prompt.md)
  Phase 4: Refactor validator (cortex-evidence-validator.prompt.md)
  Phase 5: Refactor analyst (cortex-brittleness-review.prompt.md)
  Phase 6: Verify new prompts
        ↓
Result: All prompts aligned to unified contract
```

---

## 🎯 KEY CAPABILITIES OF THE ALIGNMENT PROMPT

### 1. Automatic Discovery (No Hardcoding)
```
✅ Scans .github/prompts/ for ALL *.prompt.md files
✅ Includes new prompts automatically
✅ Maps relationships between prompts
✅ Handles folder changes without code updates
```

### 2. Comprehensive Conflict Detection
```
✅ Regression check redundancy (how many times repeated?)
✅ Sync protocol inconsistency (when/where do syncs happen?)
✅ Response format mismatch (how many formats?)
✅ Orchestrator delegation gaps (which prompts still simulate work?)
✅ Phase gate inconsistency (when are they enforced?)
✅ Evidence standard variance (how are they tracked?)
```

### 3. Unified Contract Generation
```
✅ Shared data model (what all prompts agree on)
✅ Shared regression protocol (ONE definitive version)
✅ Shared sync protocol (ONE definitive version)
✅ Shared response format (references output-standards.md)
✅ Shared orchestrator delegation (MasterOrchestrator only)
✅ Shared phase gates (enforced uniformly)
✅ Shared evidence standards (test-based proof)
```

### 4. Per-Prompt Recommendations
```
For each discovered prompt:
  ✅ What's working (keep as-is)
  ✅ What conflicts (fix this)
  ✅ Specific changes needed (line numbers, before/after)
  ✅ Effort estimate (hours required)
  ✅ Success criteria (how to verify)
```

### 5. Strategic Roadmap
```
✅ Sequential execution (no parallelization)
✅ Effort estimates per phase
✅ Dependencies between phases
✅ Validation checkpoints
✅ Success criteria for entire initiative
```

---

## 📊 ALIGNMENT VECTORS (What Gets Unified)

### Vector 1: Plan Integration
```
master-plan.yaml (phase definitions)
    ↓ ALL prompts MUST align with phases
    ↓ AUDIT VERIFIES: Every prompt respects phase gates
    ↓
    All prompts now use SAME phase enforcement
```

### Vector 2: AC-ID Registry
```
AC-INDEX.yaml (AC definitions)
    ↓ ALL prompts MUST use same evidence standards
    ↓ AUDIT VERIFIES: Every prompt tracks test-based completion
    ↓
    All prompts now use SAME completion criteria
```

### Vector 3: State Management
```
progress-tracker.json (source of truth)
    ↓ ALL prompts MUST read/write same tracker
    ↓ AUDIT VERIFIES: No prompt has private state
    ↓
    All prompts now manage state CONSISTENTLY
```

### Vector 4: Dashboard Sync
```
plan-viewer-data.json (synced dashboard)
    ↓ ALL prompts MUST sync via same protocol
    ↓ AUDIT VERIFIES: All syncs happen at correct points
    ↓
    All prompts now sync UNIFORMLY
```

### Vector 5: Orchestrator Delegation
```
MasterOrchestrator (execution authority)
    ↓ ALL prompts MUST delegate to orchestrator
    ↓ AUDIT VERIFIES: No prompt simulates work directly
    ↓
    All prompts now DELEGATE execution
```

---

## 🏆 BENEFITS OF THIS APPROACH

### For You (User)
- ✅ Single coherent system (no silos, no conflicts)
- ✅ Auto-discovery (new prompts work immediately)
- ✅ Clear mental model (shared contracts)
- ✅ Explicit roadmap (know exactly what to fix)
- ✅ Verification built-in (can validate alignment anytime)

### For New Team Members
- ✅ One source of truth (INTENT-AND-APPROACH.md)
- ✅ User guide (HOW-TO-USE.md)
- ✅ Unified contracts (shared standard)
- ✅ Auto-discovery documentation (no manual updates)

### For Future Development
- ✅ New prompts follow same pattern
- ✅ Conflicts detected automatically
- ✅ Roadmap for integration available
- ✅ Validation checklist provided

### For System Reliability
- ✅ No duplicate regression checks
- ✅ Consistent sync protocols
- ✅ Uniform phase enforcement
- ✅ Clear orchestrator delegation
- ✅ Evidence-based tracking throughout

---

## 📁 DELIVERABLE FILES

### Main Executable
- **`.github/prompts/cortex-prompt-alignment.prompt.md`**
  - 600+ lines
  - The orchestrator prompt that does the alignment audit
  - Executable in GitHub Copilot chat

### Documentation
- **`cortex-brain/documents/prompt-alignment/INTENT-AND-APPROACH.md`**
  - Your intent, reflected back
  - How this solution addresses it
  - Confirmation checklist
  
- **`cortex-brain/documents/prompt-alignment/HOW-TO-USE.md`**
  - Step-by-step user guide
  - Common scenarios
  - Troubleshooting
  - Maintenance schedule

### Generated Artifacts (When Audit Runs)
The alignment prompt will CREATE these when executed:
- **`alignment-audit-{timestamp}.md`** - Full audit report
- **`alignment-refactoring-plan.yaml`** - Per-prompt refactoring roadmap
- **`unified-prompt-contract.yaml`** - Shared contracts for all prompts

---

## 🚀 GETTING STARTED

### Immediate (Right Now)
1. ✅ Read `INTENT-AND-APPROACH.md` (understand the big picture)
2. ✅ Read `HOW-TO-USE.md` (understand how to use it)
3. ✅ Verify the three files exist in correct locations

### Next (When Ready)
1. Say to GitHub Copilot: `"align prompts"`
2. Copilot loads `cortex-prompt-alignment.prompt.md`
3. Prompt executes discovery → audit → recommendations
4. You get comprehensive audit report

### Then (Refactoring Phase)
1. Review audit report
2. Follow refactoring roadmap
3. Execute changes one prompt at a time
4. Validate after each prompt

---

## ✅ SUCCESS CRITERIA (After Alignment Complete)

- ✅ All prompts discovered and audited
- ✅ All conflicts identified and documented
- ✅ Shared contract defined and documented
- ✅ Each prompt has refactoring plan with specific changes
- ✅ No duplicate regression checks across prompts
- ✅ All prompts use same sync protocol
- ✅ All prompts use same response format
- ✅ All prompts delegate to MasterOrchestrator (not simulate work)
- ✅ Phase gates enforced uniformly
- ✅ Evidence standards applied universally
- ✅ New prompts auto-discovered and included

---

## 🔗 RELATIONSHIP TO CHAT01 REQUIREMENTS

Addresses all points from chat01 about CORTEX.prompt.md refactoring:

| Chat01 Requirement | How Alignment Prompt Addresses It |
|--------------------|----------------------------------|
| "Stop simulating work, use actual orchestrators" | Audits ALL prompts, recommends MasterOrchestrator delegation |
| "Clarify user intent in executive bullets before proceeding" | Documents this pattern in unified contract |
| "Use built and active orchestrators" | Verifies all prompts delegate to MasterOrchestrator |
| "Work in complete alignment with cx6-plan" | Audits integration with master-plan, AC-INDEX, tracker |
| "Refactor other areas" | Discovers and audits ALL prompts, not just CORTEX.prompt.md |
| "Challenge me if I'm wrong" | Validates assumptions against actual implementation |

---

## 💭 PHILOSOPHICAL ALIGNMENT

**CORTEX Core Principle:** Orchestration belongs in Python (MasterOrchestrator). Prompts route and coordinate.

**This Alignment Prompt Ensures:** All prompts follow this principle and coordinate coherently.

**After Alignment:** You'll have a unified system where:
- Users have ONE entry point (CORTEX.prompt.md as gateway)
- All specialized prompts know their role
- All speak same language (AC-IDs, phases, evidence bundles)
- All delegate execution to MasterOrchestrator
- All maintain one source of truth (plan + tracker + AC-INDEX)

---

## 📞 NEXT ACTION

**You're all set!**

The alignment orchestrator is ready to use:

```
Say to GitHub Copilot: "align prompts"

Then read the audit report and follow the refactoring roadmap.
```

---

**Status: ✅ COMPLETE AND READY FOR USE**

**Questions?** Review the HOW-TO-USE.md guide or the INTENT-AND-APPROACH.md summary.
