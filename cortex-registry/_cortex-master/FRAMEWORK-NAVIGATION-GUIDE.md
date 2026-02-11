# 🔗 CORTEX Wave Framework Navigation Guide

**Quick Navigation Between Framework Documents**  
**Status:** Active | **Updated:** 2026-02-11

---

## 📑 Three Core Framework Documents

```
┌─────────────────────────────────────────────────────────────────┐
│                    WAVE EXECUTION FRAMEWORK                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. WAVE-EXECUTION-FRAMEWORK-SUMMARY.md (THIS FILE)            │
│     └─ Overview: "What is the framework?"                      │
│     └─ Use Cases: When to read which document                  │
│     └─ Getting Started: First steps                            │
│                                                                 │
│  2. WAVE-EXECUTION-ORCHESTRATION-MASTER.md                     │
│     └─ Master Control: 8 waves with dependencies               │
│     └─ Detailed Specs: Each wave with checkpoints              │
│     └─ Execution Format: Progress bars, summaries              │
│     └─ Deployment Reminders: Per wave                          │
│                                                                 │
│  3. STRATEGIC-DOCUMENTATION-CHECKPOINT-FRAMEWORK.md            │
│     └─ Checkpoint Philosophy: Why embedded docs?               │
│     └─ Template Structure: How to write each checkpoint        │
│     └─ Quality Standards: Validation checklist                 │
│     └─ Wave-by-Wave Breakdown: What to document when           │
│                                                                 │
│  (+ 3 Existing Reference Documents)                            │
│     └─ WAVE-BASED-EXECUTION-PLAN.yaml                          │
│     └─ WAVE-REPRIORITIZATION-2026-02-11.yaml                   │
│     └─ HIGH-ROI-WAVE-PRIORITIZATION.md                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 When to Read Each Document

### You Are... → Read This Document

| Situation | Document | Why |
|-----------|----------|-----|
| **New to framework** | WAVE-EXECUTION-FRAMEWORK-SUMMARY.md (this file) | Overview + getting started |
| **Starting a wave** | WAVE-EXECUTION-ORCHESTRATION-MASTER.md | Execution protocol + format |
| **During wave execution** | STRATEGIC-DOCUMENTATION-CHECKPOINT-FRAMEWORK.md | How to write checkpoint docs |
| **After wave completes** | WAVE-EXECUTION-ORCHESTRATION-MASTER.md | Deployment reminder + summary |
| **Planning improvements** | WAVE-REPRIORITIZATION-2026-02-11.yaml | Dependencies + constraints |
| **Detailed wave specs** | WAVE-BASED-EXECUTION-PLAN.yaml | Technical specifications |
| **ROI analysis** | HIGH-ROI-WAVE-PRIORITIZATION.md | Business justification |

---

## 🚀 5-Minute Quick Start

### 1. Read (5 min)
**File:** WAVE-EXECUTION-FRAMEWORK-SUMMARY.md (this file)

**Learn:** What is the framework? How do the 3 docs fit together?

### 2. Understand (10 min)
**File:** WAVE-EXECUTION-ORCHESTRATION-MASTER.md → "Overview" section (first 1000 words)

**Learn:** What are the 8 waves? What gets delivered when?

### 3. Start (1 min)
**Command:**
```
"start wave 1"
```

**System handles:** All TDD, checkpoints, progress tracking

---

## 📋 Document Relationship Map

```
User says: "start wave 1"
            ↓
      ORCHESTRATION-MASTER.md
      (loads WAVE-1 specs)
            ↓
   Autonomous execution begins
   RED → GREEN → REFACTOR cycles
            ↓
   After major milestone
   Checkpoint trigger
            ↓
      CHECKPOINT-FRAMEWORK.md
      (creates architecture doc)
            ↓
   Back to execution
            ↓
   After all phases
   Generate completion summary
            ↓
      ORCHESTRATION-MASTER.md
      (displays completion + deployment reminder)
```

---

## 🌊 Wave-by-Wave Document Usage

### WAVE-1 Execution

**Before Starting:**
- Read: ORCHESTRATION-MASTER.md → "WAVE-1" section (500 words)
- Understand: What gets built, what gets tested, what gets documented

**During Execution:**
- Checkpoint-1a triggers → Read: CHECKPOINT-FRAMEWORK.md → "CHECKPOINT-1a" section
- Document security gates architecture
- Checkpoint-1b triggers → Read same framework doc → "CHECKPOINT-1b" section

**After Completion:**
- Read: ORCHESTRATION-MASTER.md → "Wave-1 Completion Summary" section
- Deploy to production
- Record deployment date

### WAVE-2 Execution
- Same pattern as Wave-1
- Before: ORCHESTRATION-MASTER.md → "WAVE-2" section
- During: CHECKPOINT-FRAMEWORK.md → "WAVE-2" checkpoints (2a, 2b)
- After: ORCHESTRATION-MASTER.md → "Wave-2 Completion Summary"

*And so on for WAVE-3 through WAVE-8*

---

## 🔍 Cross-Document References

### From ORCHESTRATION-MASTER
When you see:
- **Checkpoint-1a: Architecture Review** → See CHECKPOINT-FRAMEWORK.md for template
- **Dependency Graph** → See WAVE-REPRIORITIZATION-2026-02-11.yaml for detailed deps
- **ROI Analysis** → See HIGH-ROI-WAVE-PRIORITIZATION.md for Wave-6 breakdown

### From CHECKPOINT-FRAMEWORK
When you see:
- **Wave dependencies** → See ORCHESTRATION-MASTER.md for overall timeline
- **Quality standards** → See WAVE-BASED-EXECUTION-PLAN.yaml for governance rules
- **Example checkpoint** → See ORCHESTRATION-MASTER.md → Wave sections

### From WAVE-BASED-EXECUTION-PLAN.yaml
When you see:
- **Phase-XX reference** → See WAVE-ORCHESTRATION-MASTER.md for which wave it belongs to
- **Governance rules** → See CORE-008, CORE-011, etc. in cortex-architect.prompt.md

---

## 📊 Decision Trees: Which Doc Do I Need?

### "I want to start Wave-2"
```
Start here: ORCHESTRATION-MASTER.md
└─ Find: "WAVE-2: Intelligence Layer" section
   ├─ Scope: What gets built
   ├─ Checkpoints: 2a (Agent Architecture), 2b (MCP Integration)
   └─ When to deploy: After 10-14 days + 24h monitoring of Wave-1

Ready? → Command: "start wave 2"
```

### "I need to create Checkpoint-4a documentation"
```
Start here: CHECKPOINT-FRAMEWORK.md
└─ Find: "WAVE-4: Enhancement & UX" section
   └─ Find: "CHECKPOINT-4a: Use Case Documentation"
      ├─ File: cortex-architecture/use-cases.md
      ├─ Content sections: overview, diagram, decisions, integration, examples, testing
      ├─ Word count: 1,200-1,500 words
      ├─ Validation: Use checklist from framework
      └─ Commit: "Docs: Checkpoint-4a Use Case Documentation complete"
```

### "I want to understand Wave-6 ROI"
```
Start here: HIGH-ROI-WAVE-PRIORITIZATION.md
└─ Find: "WAVE-6 ROI Analysis" section
   ├─ ROI Score: 9.2/10 (highest)
   ├─ Consolidation: 26 orchestrators → 15
   ├─ Duration: 14-18 days
   └─ Deliverables: Docs + test suite + cleanup

Then: ORCHESTRATION-MASTER.md → "WAVE-6" section for execution details
```

### "I want to run waves in parallel to save time"
```
Start here: WAVE-ORCHESTRATION-MASTER.md
└─ Find: "Wave Dependency Graph" section
   ├─ Shows: Which waves can run together
   ├─ Example: Wave-3 (Autonomy) independent from Wave-2 (Intelligence)
   ├─ Result: 77-97 days → 55-62 days optimization

Then: WAVE-REPRIORITIZATION-2026-02-11.yaml for detailed dependencies
```

---

## 📈 Framework Usage Statistics

### Expected Usage Over 8 Waves

```
ORCHESTRATION-MASTER.md
├─ First read: 30 minutes (overview + WAVE-1 section)
├─ WAVE-1 start: "start wave 1" command (1 second)
├─ WAVE-1 end: Read completion summary (5 minutes)
├─ Waves 2-8: Read relevant section before each (5 min × 7) = 35 min
└─ Total: ~1 hour across 8 waves

CHECKPOINT-FRAMEWORK.md
├─ First read: 20 minutes (template structure)
├─ During execution: Read checkpoint template when triggered
│   └─ Time per checkpoint: 10-15 minutes to understand format
│   └─ 16 checkpoints × 15 min = 240 minutes total
├─ Actual writing time: 60-90 minutes per checkpoint (outside of framework reading)
└─ Framework contribution: ~4 hours reading + understanding

REFERENCE DOCUMENTS
├─ One-time reads: 1 hour (YAML specs, ROI analysis)
└─ During execution: Skip (already loaded into memory)
```

---

## ✅ Verification Checklist

**Before Starting Wave-1, Verify You Have:**

- [ ] Read WAVE-EXECUTION-FRAMEWORK-SUMMARY.md (this file) → Understand 3-doc structure
- [ ] Read ORCHESTRATION-MASTER.md → "Overview" section → Know what Wave-1 builds
- [ ] Read ORCHESTRATION-MASTER.md → "WAVE-1" section → Understand Wave-1 specifically
- [ ] Read CHECKPOINT-FRAMEWORK.md → Understand documentation checkpoints
- [ ] Confirmed prerequisites (Python 3.9+, MCP server, dependencies)
- [ ] Created git branch for Wave-1
- [ ] Reviewed governance rules (CORE-008 TDD-first mandatory)

**Ready?** → Command: `"start wave 1"`

---

## 🎯 Summary: How These Documents Work Together

```
┌──────────────────────────────────────────────────────────────────┐
│                 WAVE EXECUTION FRAMEWORK                         │
│                                                                  │
│  ORCHESTRATION (MASTER.md)                                       │
│  ├─ What gets built: 8 waves with specific deliverables         │
│  ├─ When it gets built: Timelines + dependencies                │
│  ├─ How it gets built: Autonomous execution + progress bars     │
│  └─ When to deploy: Production deployment after each wave       │
│      │                                                           │
│      └─→ CHECKPOINTS (FRAMEWORK.md)                             │
│          ├─ What gets documented: 16 architecture docs          │
│          ├─ When: During each wave (not deferred)               │
│          ├─ How: Template-based, consistent format              │
│          └─ Quality: Validation checklist per checkpoint        │
│      │                                                           │
│      └─→ REFERENCE DOCS (YAML + existing)                       │
│          ├─ Dependencies: Which waves block which               │
│          ├─ ROI: Why each wave matters (business case)          │
│          ├─ Specs: Technical details of each phase              │
│          └─ Standards: Governance + quality gates               │
│                                                                  │
│  Result:                                                         │
│  ✅ Autonomous execution (silent, progress bars only)           │
│  ✅ Incremental delivery (production deployment per wave)       │
│  ✅ Tech debt paid off (docs embedded, not deferred)            │
│  ✅ Quality assured (TDD mandatory, governance enforced)        │
│  ✅ Handoff ready (comprehensive docs + trained teams)          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Next Steps

### Immediate (Next 5 Minutes)
1. Read rest of this file (navigation guide)
2. Understand 3-doc structure
3. Know where to find information

### Short-term (Next 30 Minutes)
1. Read ORCHESTRATION-MASTER.md overview
2. Understand 8-wave structure + dependencies
3. Read WAVE-1 section in detail

### Before Starting Wave-1 (Before Next Day)
1. Read CHECKPOINT-FRAMEWORK.md once (understand checkpoint structure)
2. Set up production deployment procedure (git tags, monitoring, etc.)
3. Execute: `"start wave 1"`

---

## 📞 Quick Reference Links

| Document | File | Section |
|----------|------|---------|
| Framework Overview | **THIS FILE** | (entire file) |
| Wave Execution | ORCHESTRATION-MASTER.md | Timeline + 8 Waves |
| WAVE-1 Details | ORCHESTRATION-MASTER.md | WAVE-1 section |
| Documentation | CHECKPOINT-FRAMEWORK.md | All checkpoints |
| Wave 1 Checkpoints | CHECKPOINT-FRAMEWORK.md | WAVE-1 section |
| Dependencies | WAVE-REPRIORITIZATION-2026-02-11.yaml | Full dependency graph |
| Technical Specs | WAVE-BASED-EXECUTION-PLAN.yaml | Complete specifications |
| ROI Analysis | HIGH-ROI-WAVE-PRIORITIZATION.md | Wave-6 justification |

---

## ✨ Key Insight

**These 3 documents solve a fundamental problem:**

❌ **Old Way:** Work 15 weeks, test 1 week, write docs from memory
- Docs are inaccurate (decisions forgotten)
- Tech debt accumulates (not paid off)
- Risk is high (failures in week 15 are costly)
- Team doesn't know what's being built

✅ **New Way:** 8 waves, each with docs + tests + deployment
- Docs are accurate (written while fresh)
- Tech debt is paid off incrementally (2-3 hours per wave)
- Risk is distributed (failure in wave 3 doesn't cascade)
- Team onboarding starts immediately (docs available as work progresses)

**Result:** 55-62 days to full production delivery with comprehensive documentation.

---

**Framework Status:** ✅ READY FOR DEPLOYMENT  
**Created:** 2026-02-11 by Asif Hussain  
**Authority:** cortex-architect.prompt.md v15.3
