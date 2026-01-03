# CORTEX.prompt.md Lean Specification v5.0

**Date:** 2026-01-03  
**Target Lines:** ~150 lines  
**Target Tokens:** ~2,500 tokens  
**Reduction:** 70% from current (508 lines → 150 lines)  
**Purpose:** Machine-readable intent routing for Master Orchestrator

---

## 🎯 Design Principles

1. **Machine-Readable First:** Strict table format, no prose
2. **Zero Ambiguity:** Exact regex patterns, no interpretation needed
3. **Minimal Context:** External references only, no embedded docs
4. **Protocol Preservation:** All critical rules intact
5. **Backward Compatible:** All existing routing works identically

---

## 📐 Structure Blueprint (7 Sections, ~150 Lines)

### Section 1: Header & Metadata (5 lines)
```markdown
# 🎯 CORTEX Universal Entry Point

**Version:** 5.0.0 | **Status:** ✅ PRODUCTION | **Type:** Machine-Readable Router  
**Author:** Asif Hussain | **Docs:** [Orchestrators](../../documents/orchestrators-quick-ref.md) | [Architecture](../../documents/cortex-architecture-quick-ref.md)  
**Copyright © 2025 Asif Hussain. All rights reserved.**
```

**Rationale:** Minimal metadata + direct links to external docs

---

### Section 2: Core Protocol (30 lines)

```markdown
---

## ⚠️ Parse User Request FIRST

Remove meta-directives before classification:
- `Follow instructions in...` → REMOVE
- `Use *.prompt.md...` → REMOVE
- `Reference file:///...` → REMOVE

---

## 🚨 Planning Detection (HIGHEST PRIORITY)

**Patterns (MUST create plan, NOT implement):**
- `/CORTEX Plan [feature]`
- `plan [feature]`, `create a plan`, `make a plan`

**Rule:** Pattern match → Create plan structure → STOP (do NOT implement)

---

## 🛡️ Hand-Off Protocol

**AUTONOMOUS Orchestrators (🛡️):**
- ❌ FORBIDDEN: Read manifest + execute yourself, summarize, continue after routing
- ✅ REQUIRED: Route → Display progress → STOP (let Python execute)

**GUIDED Orchestrators (📋):**
- ✅ Load manifest → Interpret instructions → Execute workflow

---
```

**Rationale:**
- Planning detection preserved (critical for correct behavior)
- Hand-off protocol compressed to essential rules
- Examples removed (externalized to cortex-protocol-examples.md)

---

### Section 3: Intent Router (80 lines)

```markdown
## 🔀 Intent Router

**Status:** ✅ LIVE - Master Orchestrator (Phase 7)  
**Config:** `cortex-brain/config/master-orchestrator.yaml`  
**Architecture:** User Input → Context Middleware → Pattern Match → Execution

### Routing Table

| Command | Orchestrator | Pattern | Type | Behavior |
|---------|--------------|---------|------|----------|
| `intro`, `hello`, `hi cortex` | Introduction | — | Template | ASCII banner |
| `plan`, `create a plan` | 🛡️ Planning v5 | `^(plan\|create a plan\|make a plan).*$` | Regex | HAND-OFF → Autonomous |
| `ado`, `ado story`, `ado feature` | 🛡️ ADO v2 | `^(ado\|ado story\|ado feature).*$` | Regex | HAND-OFF → Wizard/Auto |
| `vacuum`, `deep clean` | 🛡️ Vacuum v2 | `^(vacuum\|deep clean\|organize files).*$` | Regex | HAND-OFF → Cleanup |
| `cleanup`, `cleanup cache` | 🛡️ Cleanup v2 | `^(cleanup\|cleanup cache\|cleanup logs).*$` | Regex | HAND-OFF → Selective |
| `investigate`, `find root cause` | 🛡️ Investigation | `^(investigate\|find root cause\|why is).*$` | Regex | HAND-OFF → Analysis |
| `tdd`, `start tdd` | 📋 TDD | `^(tdd\|start tdd\|run tests).*$` | Regex | GUIDED workflow |
| `sanitize`, `make generic` | 📋 Sanitization | `^(sanitize\|make generic).*$` | Regex | GUIDED sanitize |
| `debug`, `fix bug` | 📋 Debug | `^(debug\|fix bug\|troubleshoot).*$` | Regex | GUIDED debug |
| `refine`, `improve` | 📋 Refinement | `^(refine\|improve\|optimize).*$` | Regex | GUIDED improve |
| `help`, `show commands` | Help | — | Template | Command list |

**Manifest Path:** `cortex-brain/manifests/orchestrators/{manifest-file}`  
**Template Path:** `cortex-brain/response-templates-v4.yaml`

### Continuation Detection

**AUTO-ROUTE:** "continue", "resume" → Query Tier 1 Working Memory → Last orchestrator  
**Context Injection:** Last 3 sessions metadata (~200 tokens)

### Vision API

**AUTO-ENGAGE:** PNG/JPG/JPEG detected → GPT-4V analysis → Inject context  
**Config:** `auto_detect_images: true`, `auto_analyze_on_detect: true`

---
```

**Rationale:**
- Routing table compressed to essential columns (removed confidence, detailed behavior)
- All 10 orchestrators preserved with exact patterns
- Continuation + Vision collapsed to 2-line summaries
- Configuration paths included for Master Orchestrator parsing

**Key Differences from Current:**
- Removed "Orchestrator Autonomy Matrix" (moved to orchestrators-quick-ref.md)
- Removed progress bar rendering instructions (moved to orchestrators-quick-ref.md)
- Removed routing architecture diagram (moved to cortex-architecture-quick-ref.md)
- Kept only routing table + continuation + vision (minimal essentials)

---

### Section 4: Fallback Handling (5 lines)

```markdown
## ⚠️ Fallback Behavior

- **LLM Classification Failure:** Fallback to keyword matching, log error
- **Orchestrator Execution Failure:** Report error, suggest alternatives
- **Missing Orchestrator:** Inform unavailable, suggest similar
- **Ambiguous Intent:** Ask user to clarify, present options

---
```

**Rationale:** Bullet list only, no verbose descriptions

---

### Section 5: Brain Protection (10 lines)

```markdown
## 🛡️ Brain Protection (SKULL)

| Rule | Enforcement |
|------|-------------|
| TDD_ENFORCEMENT | RED→GREEN→REFACTOR mandatory |
| HOLISTIC_DISCOVERY | Search before create (prevent duplication) |
| REFACTOR_CLEANUP | Remove orphaned/duplicate code |
| GIT_ISOLATION | CORTEX code never in user repos |
| PLANNING_ISOLATION | Planning commands create plans ONLY, never implement |
| HAND_OFF_PROTOCOL | 🛡️ AUTONOMOUS orchestrators execute independently |

**Full rules:** `cortex-brain/brain-protection-rules.yaml` (61 rules)

---
```

**Rationale:** Table preserved, reference to full rules file

---

### Section 6: Document Organization (5 lines)

```markdown
## 📁 Document Organization

**⛔ FORBIDDEN:** Root-level docs (`CORTEX/summary.md`)  
**✅ REQUIRED:** `cortex-brain/documents/{category}/`  
**Categories:** `reports/`, `analysis/`, `summaries/`, `investigations/`, `planning/`, `implementation-guides/`

---
```

**Rationale:** Essential rules only, no examples

---

### Section 7: External References (15 lines)

```markdown
## 📚 External References

**Orchestrator Documentation:**
- [Orchestrators Quick Reference](../../documents/orchestrators-quick-ref.md) - All 10 orchestrators, behaviors, outputs, progress rendering
- [Response Templates](../../response-templates-v4.yaml) - INSTANT/FOCUSED/STRUCTURED/COMPREHENSIVE tiers

**Architecture & Configuration:**
- [Architecture Quick Reference](../../documents/cortex-architecture-quick-ref.md) - Brain tiers, command list
- [Master Orchestrator Config](../../config/master-orchestrator.yaml) - Routing configuration
- [Brain Protection Rules](../../brain-protection-rules.yaml) - 61 SKULL rules

**Learning Materials:**
- [Protocol Examples](../../documents/cortex-protocol-examples.md) - Planning detection, routing, hand-off examples (NOT loaded by default)

---
```

**Rationale:** All externalized content linked, learning materials separated

---

## 📊 Line Count Breakdown

| Section | Lines | Purpose |
|---------|-------|---------|
| 1. Header & Metadata | 5 | Version info + external doc links |
| 2. Core Protocol | 30 | Parse rules, planning detection, hand-off protocol |
| 3. Intent Router | 80 | Routing table, continuation, vision API |
| 4. Fallback Handling | 5 | Error handling rules |
| 5. Brain Protection | 10 | SKULL rules summary |
| 6. Document Organization | 5 | File structure rules |
| 7. External References | 15 | Links to externalized docs |
| **TOTAL** | **150** | **70% reduction from 508 lines** |

---

## 🔍 Token Analysis

| Section | Estimated Tokens |
|---------|------------------|
| Header & Metadata | 80 |
| Core Protocol | 450 |
| Intent Router | 1,200 |
| Fallback Handling | 80 |
| Brain Protection | 180 |
| Document Organization | 80 |
| External References | 230 |
| **TOTAL** | **~2,500** |

**Reduction:** 8,500 tokens → 2,500 tokens = **70% decrease**

---

## ✅ Functional Equivalence Checklist

### Routing Preservation
- [x] All 10 orchestrator patterns preserved exactly
- [x] Planning detection logic intact (HIGHEST PRIORITY)
- [x] Hand-off protocol rules complete (FORBIDDEN + REQUIRED)
- [x] Continuation detection functional
- [x] Vision API auto-engagement configured

### Protocol Enforcement
- [x] Parse User Request rules present
- [x] 🛡️ AUTONOMOUS vs 📋 GUIDED distinction clear
- [x] SKULL rules enforced (with reference to full file)
- [x] Document organization rules enforced

### Master Orchestrator Integration
- [x] Routing table machine-readable (strict format)
- [x] Configuration paths included
- [x] Pattern matching deterministic (regex patterns exact)
- [x] External reference structure clear

---

## 🚨 Critical Validation Tests

### Test 1: Planning Detection
**Input:** `"plan user authentication"`  
**Expected:** Create plan structure → STOP (do NOT implement)  
**Validation:** Planning pattern matches, Hand-Off Protocol triggered

### Test 2: AUTONOMOUS Routing
**Input:** `"vacuum /path/to/dir"`  
**Expected:** Route to Vacuum v2 → Display progress → STOP  
**Validation:** Pattern matches, Master Orchestrator invokes Python

### Test 3: GUIDED Routing
**Input:** `"tdd my_module.py"`  
**Expected:** Load TDD manifest → Interpret instructions → Execute  
**Validation:** Pattern matches, Copilot reads manifest

### Test 4: Continuation
**Input:** `"continue"`  
**Expected:** Query Tier 1 → Route to last orchestrator  
**Validation:** Context middleware loads last 3 sessions

### Test 5: Vision API
**Input:** User attaches image  
**Expected:** Auto-analyze with GPT-4V → Inject context  
**Validation:** Image detection triggers without prompt

### Test 6: Fallback
**Input:** Ambiguous request with MEDIUM confidence  
**Expected:** Ask user to clarify + present options  
**Validation:** Fallback behavior triggers

---

## 📋 Implementation Checklist (Task 6.4.5.4)

- [ ] Backup current CORTEX.prompt.md → `.v4.backup`
- [ ] Implement Section 1 (Header & Metadata)
- [ ] Implement Section 2 (Core Protocol)
- [ ] Implement Section 3 (Intent Router)
- [ ] Implement Section 4 (Fallback Handling)
- [ ] Implement Section 5 (Brain Protection)
- [ ] Implement Section 6 (Document Organization)
- [ ] Implement Section 7 (External References)
- [ ] Verify line count ≤150
- [ ] Verify token count ≤2,500
- [ ] Run validation tests (6 tests above)
- [ ] Update Master Orchestrator (Task 6.4.5.5)

---

## 🎯 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Line Count** | ≤150 | `wc -l CORTEX.prompt.md` |
| **Token Count** | ≤2,500 | Token counter tool |
| **Load Time** | <0.5s | Copilot context load time |
| **Routing Accuracy** | 100% | All 10 orchestrators route correctly |
| **Functional Regression** | 0 | All existing commands work identically |
| **External References** | 3+ | orchestrators-quick-ref, architecture-quick-ref, response-templates |

---

## 📝 Migration Summary

**What Changed:**
- ✅ Reduced from 508 lines to ~150 lines (70% reduction)
- ✅ Externalized orchestrator documentation
- ✅ Removed all examples and prose
- ✅ Compressed protocol to essential rules
- ✅ Created machine-readable routing table

**What Stayed:**
- ✅ All 10 orchestrator patterns (exact)
- ✅ Planning detection logic
- ✅ Hand-off protocol rules
- ✅ SKULL brain protection
- ✅ Continuation detection
- ✅ Vision API configuration

**What's New:**
- ✅ External reference structure
- ✅ Direct links to orchestrators-quick-ref.md
- ✅ Hybrid Ownership Model clarity (🛡️ AUTONOMOUS vs 📋 GUIDED)

---

## 🚀 Next Steps

1. **Task 6.4.5.3:** Create `orchestrators-quick-ref.md` with externalized content
2. **Task 6.4.5.4:** Implement lean CORTEX.prompt.md
3. **Task 6.4.5.5:** Enhance Master Orchestrator to parse lean table
4. **Validate:** All 6 critical tests pass
5. **Document:** Create migration report

---

**Ready for implementation!** 🎯
