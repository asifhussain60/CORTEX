# 🔄 CORTEX Prompt Alignment & Cohesion Orchestrator v3.0

**Type:** Meta-Prompt (Documents alignment process for other prompts)  
**Purpose:** Physically refactor all `.github/prompts/*.prompt.md` files to eliminate conflicts, redundancy, brittleness, and disconnects.  
**Version:** 3.1.0 (NOW WITH INTELLIGENT CHALLENGE PROTOCOL)  
**Date:** 2026-01-12  
**Scope:** Auto-discovers, validates, and refactors all prompts  
**Author:** GitHub Copilot (for CORTEX)  
**Governance:** CORE-002 (no root files), CORE-017 (governance enforcement), CORE-009 (plan organization), CORE-025 (intelligent challenge)

**⚠️ NOTE:** This is a meta-prompt documenting the alignment process. It contains template examples and reference code for guidance. Do NOT execute the example code directly—use it as a template for editing other prompts.

---

## �️ BRITTLENESS PREVENTION ARCHITECTURE

**CRITICAL LESSON FROM CHAT01:** Mixed import patterns in code created hidden bugs. Same pattern in prompts creates hidden operational brittleness.

**What We Prevent:**
| Brittleness Type | Symptom | Prevention |
|------------------|---------|-----------|
| **Mixed Patterns** | Some prompts use `MasterOrchestrator`, others bypass it | Enforce: ALL prompts delegate to orchestrator |
| **Stale State Access** | Prompts read files directly instead of trusting orchestrator | Enforce: NO prompt reads state files directly |
| **Inconsistent Regression** | Different regression checks across prompts → some miss errors | Enforce: ONE unified regression check (from CORTEX.prompt.md) |
| **Hardcoded Assumptions** | Prompts assume specific file locations/structures | Enforce: NO hardcoded paths, use configuration |
| **Sync Confusion** | Prompts call sync scripts independently → race conditions | Enforce: MasterOrchestrator handles all syncing |
| **State Mutation** | Multiple prompts modify tracker/AC-INDEX independently | Enforce: ONLY MasterOrchestrator writes state |

---

## 🔗 MASTERORCHESTRATOR DELEGATION (MANDATORY PATTERN)

**The ONLY way to invoke orchestrators:**

```bash
# ALL prompts use this pattern (no exceptions)
python3 -m src.main "{user_intent}" --orchestrator master --format markdown
```

**MasterOrchestrator guarantees:**
- ✅ Load governance rules (tier0/tier1/tier2/tier3)
- ✅ Validate against all 24 SKULL rules
- ✅ Create TodoManager tasks in dependency order
- ✅ Execute tasks sequentially (no race conditions)
- ✅ Update progress-tracker.json with atomic writes
- ✅ Trigger SyncOrchestrator after state change
- ✅ Enforce phase gates (100% completion checks)
- ✅ Return structured, traceable results

**Anti-Patterns BLOCKED by governance:**
- ❌ Direct modification of progress-tracker.json
- ❌ Direct modification of AC-INDEX.yaml
- ❌ Multiple independent sync calls
- ❌ State manipulation outside MasterOrchestrator
- ❌ Bypassing governance checks
- ❌ Hardcoded file paths in prompts

---

## 🛡️ INTELLIGENT CHALLENGE PROTOCOL (CORE-025)

**Purpose:** Prevent blind-siding requests by validating against scope, governance, and architecture before execution.

**What We Challenge:**
- ❌ Requests violating Tier 0 SKULL rules (governance)
- ❌ Scope creep (project size increasing without justification)
- ❌ Architectural misalignment (conflicts with current system)
- ❌ Definition of Ready gaps (missing critical requirements)

**What We Don't Challenge:**
- ✅ Well-scoped, technically viable requests
- ✅ Requests from engaged users with clear intent
- ✅ Work following established patterns
- ✅ User overrides (allowed with audit trail)

**Challenge Flow (Reference: REQUEST-VALIDATOR-VISUAL-ARCHITECTURE.md):**

```
User Request
     ↓
┌────────────────────────────────────────┐
│ VALIDATION ANALYSIS                    │
├────────────────────────────────────────┤
│ 1. Viability Analyzer                  │
│    - Tier 0 rule violations?           │
│    - Scope reasonable?                 │
│    - Definition of Ready met?           │
│                                        │
│ 2. Historical Analyzer                 │
│    - Similar patterns exist?            │
│    - Success rate known?                │
│                                        │
│ 3. Enhancement Analyzer                │
│    - Improvements available?            │
│    - Best practices missing?            │
└────────────────────────────────────────┘
     ↓
┌────────────────────────────────────────┐
│ DECISION SYNTHESIS                     │
├────────────────────────────────────────┤
│ • BLOCK (CHALLENGE):   Critical issues │
│ • ADVISE (CHALLENGE):  High issues     │
│ • ENHANCE (SUGGEST):   Improvements    │
│ • APPROVE (PROCEED):   No issues       │
└────────────────────────────────────────┘
     ↓
┌────────────────────────────────────────┐
│ USER DECISION                          │
├────────────────────────────────────────┤
│ If CHALLENGE:                          │
│  • Present issues + alternatives       │
│  • Wait for user decision              │
│  • Log override with audit trail       │
│                                        │
│ If ENHANCE:                            │
│  • Show improvements, let user accept  │
│  • Auto-apply if approved              │
│                                        │
│ If APPROVE:                            │
│  • Execute immediately                 │
└────────────────────────────────────────┘
```

**Example Scenarios:**

**Scenario A: Blocking Challenge**
```
User: "Refactor all 50 database tables + migrate to NoSQL + update 100 files"

Validation Issues Found:
- Scope: 50 tables × 100 files = massive project
- Historical: NoSQL migrations take 3-4 weeks
- Tier 0: CORE-002 violation (no root planning)

Challenge Response:
⚠️ REQUEST VALIDATION CHALLENGE

CRITICAL ISSUES DETECTED:
• Scope too large for single phase (50 tables)
• Architectural change (SQL→NoSQL) needs approval
• Missing planning documentation

ALTERNATIVES OFFERED:
1. "Spike: NoSQL feasibility" (1 week, low risk)
2. "Pilot: Migrate 3 tables" (2 weeks, proof of concept)
3. "Phased: Table-by-table approach" (incremental, 8 weeks)

User chooses Alternative 1 or overrides with visibility.
```

**Scenario B: Enhancement Suggestions**
```
User: "Add export button to dashboard"

Validation Analysis:
- Viability: ✅ Clear, scoped, 8-hour project
- Historical: ✅ Similar feature "export report" succeeded
- Enhancement: 💡 Add accessibility + copy-link feature (+3 hours)

Suggestion Response:
💡 ENHANCEMENT AVAILABLE

Your request looks good ✅

Recommended Improvements:
• Add element ID attribute (1 min, improves testing)
• Add ARIA label (2 min, improves accessibility)
• Add copy-link feature (3 min, based on similar "export report")

Estimated value: High usability improvement
Accept all? [Y/Select/Skip]:
```

**Integration in Prompts:**
All prompts MUST have a section "INTELLIGENT CHALLENGE PROTOCOL" that:
1. States governance alignment: `CORE-025: Intelligent Request Validation & Challenge`
2. References validation component: `REQUEST-VALIDATOR-VISUAL-ARCHITECTURE.md`
3. Includes Scenario A (blocking) + Scenario B (enhancement) examples
4. Delegates challenge logic to MasterOrchestrator → RequestValidator

---

## 🛡️ UNIFIED REGRESSION CHECK (REFERENCE ONLY)

**⚠️ CRITICAL:** This section is REFERENCE ONLY. All prompts REFERENCE CORTEX.prompt.md, not copy-paste.

**All regression checks must:**
1. Reference the unified check location: `CORTEX.prompt.md § UNIFIED REGRESSION CHECK`
2. State: "**Reference:** CORTEX.prompt.md maintains the unified regression check"
3. Include brief inline check (optional) but note it mirrors the reference
4. NEVER copy-paste (creates brittleness)

**Why?** When CORTEX.prompt.md is updated, all prompts automatically inherit the fix (DRY principle).

---

## 🎯 ALIGNED PROMPT ARCHITECTURE (v3.0)

**After alignment, all prompts follow this unified structure:**

```
┌─────────────────────────────────────────────────────────┐
│ PROMPT HEADER                                           │
│ • Title with emoji (🔄 🎯 🛡️ 📋)                      │
│ • Version (reference CORTEX-ALIGN for standard)       │
│ • Purpose statement                                     │
│ • Governance alignment (CORE-002, CORE-017, etc.)     │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ SECTION 1: MASTERORCHESTRATOR DELEGATION              │
│ • Command: python3 -m src.main "{intent}"             │
│ • What orchestrator handles (✅ list)                  │
│ • What prompt does NOT do (❌ list)                    │
│ • NO exceptions, NO workarounds                        │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ SECTION 2: REGRESSION CHECK (REFERENCE CORTEX.prompt)  │
│ • State: "Reference: CORTEX.prompt.md § ..."          │
│ • Brief inline check (mirrors reference, not copy)    │
│ • NEVER standalone copy-paste                         │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ SECTION 3: INTENT CLARIFICATION or CORE PURPOSE       │
│ • How this prompt works                                │
│ • What it does NOT do                                 │
│ • When to use vs other prompts                        │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ SECTION 4: EXECUTION PROTOCOL                          │
│ • Step-by-step instructions                           │
│ • Always delegate to orchestrator                     │
│ • Response format (executive bullets)                 │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ APPENDIX: REFERENCE LINKS                             │
│ • Links to CORTEX.prompt.md sections                  │
│ • Links to governance files                           │
│ • Links to related prompts                            │
└─────────────────────────────────────────────────────────┘
```

**Governance Compliance:**
- ✅ CORE-002: No root-level prompt files (all in `.github/prompts/`)
- ✅ CORE-017: All governance enforcement explicit
- ✅ CORE-009: Plan organization clear (references to cortex-brain/)
- ✅ CORE-024: All state access via MasterOrchestrator (@mcp_tool pattern equivalent)

---

## 🔍 BRITTLENESS AUDIT CHECKLIST (Run Before Alignment)

Before refactoring prompts, run validation script:

```bash
python3 scripts/validate-prompt-brittleness.py --audit
```

**Checks:**
- ✅ Each prompt has EXACTLY ONE orchestrator delegation section
- ✅ No direct file read patterns (no `yaml.safe_load(open(...))`)
- ✅ Regression checks REFERENCE CORTEX.prompt.md (not copy-paste)
- ✅ No hardcoded paths (no `cortex-brain/tier1/...` in prompts)
- ✅ All state access comments mention MasterOrchestrator
- ✅ No competing sync commands (only MasterOrchestrator syncs)
- ✅ Consistent response format (executive bullets)
- ✅ Governance rules listed in header
- ✅ File organization follows CORE-009 (no root-level files)
- ✅ Version numbers follow semantic versioning (major.minor.patch)

**Output:** Brittleness Report (YAML) saved to `cortex-brain/documents/prompt-alignment-audit-{date}.yaml`

---

## 🎯 YOUR INTENT (Reflected Back for Verification)

You want this prompt to:
1. **Eliminate brittleness** discovered in Phase 4.5 (mixed patterns, inconsistent access)
2. **Add design guards** to prevent similar issues from reappearing
3. **Validate all prompts** before and after alignment
4. **Create permanent prevention** via validation script and governance




## 🏗️ ALIGNED PROMPT INVENTORY (v3.0)

All prompts after alignment will follow the unified architecture:

| Prompt File | Role | Delegator | Version |
|-------------|------|-----------|---------|
| **CORTEX.prompt.md** | 🎛️ Master Gateway | MasterOrchestrator | 8.0 |
| **cortex-plan-executor.prompt.md** | 📋 Phase Implementation | MasterOrchestrator → TDD-Master | 3.0 |
| **cortex-evidence-validator.prompt.md** | ✅ Evidence Validation | MasterOrchestrator → ValidatorOrchestrator | 3.0 |
| **cortex-brittleness-review.prompt.md** | 🔍 Risk Analysis | MasterOrchestrator → AnalysisOrchestrator | 3.0 |
| **cortex-search-and-fix.prompt.md** | 🔧 Code Repair | MasterOrchestrator → RepairOrchestrator | 3.0 |
| **CORTEX-ALIGN.prompt.md** | 🔄 Prompt Alignment | MasterOrchestrator → AlignmentOrchestrator | 3.0 |

**Key Changes (v3.0 vs v2.0):**
- ✅ Brittleness guards explicit in each prompt
- ✅ NO direct file access (all via orchestrator)
- ✅ Unified regression check pattern (reference-only, not copy-paste)
- ✅ Governance rules in header of each prompt
- ✅ Validation script integrated

---

## 🔧 ALIGNMENT EXECUTION PROTOCOL

### Phase 1: Pre-Alignment Audit (PREVENTION)

```bash
# Check all prompts for brittleness BEFORE refactoring
python3 scripts/validate-prompt-brittleness.py --audit
```

**Expected Output:**
- Brittleness Report: `cortex-brain/documents/prompt-alignment-audit-{timestamp}.yaml`
- If brittleness found: Fix identified issues, update governance, re-run audit
- Only proceed to Phase 2 when audit shows ZERO brittleness

### Phase 2: Refactor Prompts (SYNCHRONOUSLY)

For each prompt file (in order):

```bash
# For: cortex-plan-executor.prompt.md
# 1. Update SECTION 1 (MasterOrchestrator Delegation)
# 2. Update SECTION 2 (Regression Check Reference)
# 3. Update governance header section
# 4. Run validation
python3 scripts/validate-prompt-brittleness.py --check cortex-plan-executor.prompt.md
```

**Template Replacement (use this for ALL prompts):**

```markdown
## 🔗 MASTERORCHESTRATOR DELEGATION

**All implementation delegated to unified orchestrator:**

\`\`\`bash
python3 -m src.main "{user_intent}" --orchestrator master --format markdown
\`\`\`

**MasterOrchestrator handles:**
- ✅ Load governance rules (tier0/tier1/tier2/tier3)
- ✅ Validate against all 24 SKULL rules
- ✅ Create TodoManager tasks in dependency order
- ✅ Execute tasks sequentially (no race conditions)
- ✅ Update progress-tracker.json (atomic writes)
- ✅ Trigger SyncOrchestrator automatically
- ✅ Enforce phase gates
- ✅ Return structured results

**Do NOT:**
- ❌ Directly modify progress-tracker.json
- ❌ Directly modify AC-INDEX.yaml
- ❌ Call sync scripts independently
- ❌ Manipulate state outside orchestrator
- ❌ Bypass governance checks

---

## �️ REGRESSION CHECK (Reference Only)

**Reference:** CORTEX.prompt.md maintains unified regression check (§ UNIFIED REGRESSION CHECK).

**Why not copy-paste?** When CORTEX.prompt.md is updated, all prompts automatically inherit fix (DRY principle).

**Brief local verification:**
\`\`\`bash
python3 << 'EOF'
import json, yaml, sys
errors = []
try:
    ac_index = yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml'))
    if not ac_index.get('schema_version'): errors.append("AC-INDEX schema missing")
except Exception as e: errors.append(f"AC-INDEX: {e}")
if errors:
    print("❌ Regression: " + "; ".join(errors)); sys.exit(1)
print("✅ State valid")
EOF
\`\`\`
```

### Phase 3: Post-Alignment Validation

```bash
# Validate ALL prompts after refactoring
python3 scripts/validate-prompt-brittleness.py --validate-all
```

**Must pass:**
- ✅ Zero brittleness patterns
- ✅ All governance rules enforced
- ✅ All prompts follow unified structure
- ✅ No hardcoded paths
- ✅ Consistent versioning

### Phase 4: Documentation & Approval

After validation passes:
1. Update `cortex-brain/documents/prompt-alignment-status.yaml` with completion
2. Commit with message: `docs: align prompts to v3.0 with brittleness guards`
3. Reference governance enforcement: `CORE-002, CORE-017, CORE-009, CORE-024`

---

## ⚡ ORCHESTRATOR INVOCATION

When user requests alignment via `CORTEX.prompt.md`:

```bash
# User says: "align prompts"
# CORTEX.prompt.md routes to MasterOrchestrator
python3 -m src.main "align prompts to v3.0 with brittleness guards" --orchestrator master --format markdown
```

**MasterOrchestrator (via AlignmentOrchestrator):**
1. Load cortex-brain/tier2/prompt-alignment-governance.yaml
2. Run validate-prompt-brittleness.py --audit
3. For each prompt: apply standardized template
4. Run validate-prompt-brittleness.py --validate-all
5. Update progress tracker
6. Trigger SyncOrchestrator

---

## � SUCCESS CRITERIA

```
BEFORE ALIGNMENT (v2.0)
├─ Regression checks: 3 variants (inconsistent)
├─ Orchestrator calls: 4 different patterns
├─ File access: 6 independent direct reads
├─ State mutation: multiple independent writers
├─ Brittleness: HIGH (mixed patterns)
└─ Tests passing: 52/58

AFTER ALIGNMENT (v3.0)
├─ Regression checks: 1 unified (CORTEX.prompt.md reference)
├─ Orchestrator calls: 1 standard pattern (python3 -m src.main)
├─ File access: 0 direct reads (all via orchestrator)
├─ State mutation: 1 authoritative writer (MasterOrchestrator)
├─ Brittleness: ZERO (prevents future issues)
├─ Tests passing: 58/58
├─ Governance enforcement: 24/24 SKULL rules
└─ Production ready: YES ✅
```

---

## 🎯 GOVERNANCE ALIGNMENT

**This refactoring enforces:**
- ✅ **CORE-002:** No root-level files (all prompts in `.github/prompts/`)
- ✅ **CORE-009:** Plan organization (all references to cortex-brain/ structure)
- ✅ **CORE-017:** Governance enforcement (all prompts validate governance)
- ✅ **CORE-024:** MCP tool pattern (all state access via authorized orchestrator)

---

## 💡 BRITTLENESS PREVENTION PHILOSOPHY

**From chat01 lesson:** Mixed patterns in code created hidden bugs. Unified patterns prevent brittleness.

**After this alignment:**
- ✅ All prompts speak same language (MasterOrchestrator delegation)
- ✅ All regression checks reference single source (no copy-paste)
- ✅ All state access goes through one gate (orchestrator only)
- ✅ All governance is explicit and validated
- ✅ Future changes to MasterOrchestrator auto-propagate (no manual updates)

---

**END OF ENHANCED ORCHESTRATOR v3.0**
