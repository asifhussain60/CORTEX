# Continuation Prompt for Phase 6.4.5

**Date:** 2026-01-03  
**Last Update:** Plan updated with new Phase 6.4.5  
**Current Progress:** 50% (Phase 6.4.5 NEXT PRIORITY)

---

## 🎯 Quick Resume

**Say this in your next chat:**
```
Continue with cortex-v5-holistic-refactor plan - Phase 6.4.5
```

Or more specifically:
```
Start Phase 6.4.5: CORTEX.prompt.md Lean Transformation
```

---

## 📊 Current Status

**CORTEX v5 Holistic Refactor:**
- **Overall Progress:** 50%
- **Current Phase:** Phase 6 (Execute Migration Plans)
- **NEXT PRIORITY:** Phase 6.4.5 (CORTEX.prompt.md Lean Transformation)
- **Strategic Decision:** Transform prompt BEFORE continuing orchestrator migrations

**Why This is Critical:**

The CORTEX.prompt.md transformation establishes the **Hybrid Ownership Model** - the architectural foundation that clarifies:
1. How routing decisions are made (pattern matching in code vs LLM interpretation)
2. When Master Orchestrator takes over (🛡️ AUTONOMOUS orchestrators)
3. When Copilot interprets manifests (📋 GUIDED orchestrators)

Without this clarity, continuing orchestrator migrations risks architectural inconsistency.

---

## 🏗️ Phase 6 Migration Breakdown

```
✅ 6.1 ADO v2 Migration              (4h)     COMPLETE
✅ 6.2 Cleanup v2 Migration          (28h)    COMPLETE
✅ 6.3 Vacuum v2 Migration           (40h)    COMPLETE
⏸️ 6.4 Sanitization v2 Migration    (16h)    DEFERRED (pending prompt transformation)
🔴 6.4.5 CORTEX.prompt.md Transform  (8h)     ← YOU ARE HERE (NEXT PRIORITY)
⏸️ 6.5 Debug v2 Migration            (24h)    PENDING APPROVAL
```

**Phase 6.4.5 Strategic Importance:**
- 🔴 **CRITICAL** - Architectural clarity before further migrations
- ⏱️ **Duration:** 1 day (8 hours)
- 🎯 **Goal:** Transform 850-line interpretive prompt → ~150-line machine-readable config
- 🏗️ **Outcome:** Hybrid Ownership Model established and validated

---

## 🎯 Phase 6.4.5 Objectives

### What We're Building

**Before (Current - 850 lines):**
```
CORTEX.prompt.md = routing logic + orchestrator docs + response specs + examples
   ↓
GitHub Copilot interprets entire document
   ↓
Copilot decides how to route based on understanding of prose
```

**After (Target - ~150 lines):**
```
CORTEX.prompt.md = pure routing table + protocol + references
   ↓
GitHub Copilot reads machine-readable table
   ↓
Pattern match → route deterministically (no interpretation)
```

### Hybrid Ownership Model

**🛡️ AUTONOMOUS Orchestrators:**
```
User: "plan user auth"
   ↓
Copilot: Detects pattern `^(plan|create a plan).*$`
   ↓
Copilot: Invokes MasterOrchestrator.handle_request()
   ↓
Copilot: Displays progress table
   ↓
Copilot: STOPS (Python owns execution)
```

**📋 GUIDED Orchestrators:**
```
User: "tdd my_module.py"
   ↓
Copilot: Detects pattern `^(tdd|start tdd).*$`
   ↓
Copilot: Loads manifest YAML
   ↓
Copilot: Interprets and executes manifest instructions
   ↓
Copilot: Returns results
```

---

## 📋 Phase 6.4.5 Sub-Tasks (8 hours)

### 6.4.5.1: Analyze Current CORTEX.prompt.md Structure (2h)
- Read current 850-line prompt
- Categorize content (routing vs docs vs specs)
- Create externalization map
- **Deliverable:** `cortex-brain/documents/analysis/cortex-prompt-structure-analysis.md`

### 6.4.5.2: Create Lean Specification (2h)
- Design ~150-line structure
- Machine-readable Intent Router table
- Protocol specifications (AUTONOMOUS vs GUIDED)
- Reference links to externalized content
- **Deliverable:** `cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/artifacts/cortex-prompt-lean-spec.md`

### 6.4.5.3: Create Orchestrators Quick Reference (2h)
- Externalize orchestrator behavior docs
- Document all 10 orchestrators (5 AUTONOMOUS, 5 GUIDED)
- Include patterns, configs, behaviors, outputs
- **Deliverable:** `cortex-brain/documents/orchestrators-quick-ref.md`

### 6.4.5.4: Implement Lean CORTEX.prompt.md (2h)
- Backup current version (`.v4.backup`)
- Replace with lean version
- Verify <200 lines
- Create migration summary
- **Deliverable:** `.github/prompts/CORTEX.prompt.md` (lean)

### 6.4.5.5: Update Master Orchestrator Integration (2h)
- Enhance `PatternRouter` to parse lean prompt
- Add Markdown table parsing
- Merge with YAML config patterns
- Write tests
- **Deliverable:** Enhanced PatternRouter

---

## ✅ Success Criteria

- [ ] CORTEX.prompt.md reduced to <200 lines
- [ ] Intent Router table is machine-readable (strict format)
- [ ] All orchestrator docs externalized
- [ ] Master Orchestrator can parse prompt directly
- [ ] All existing routing still works (zero functional regression)
- [ ] Pattern matching is deterministic
- [ ] Hybrid Ownership Model documented

---

## 🔄 After Phase 6.4.5 Completion

**Next Steps:**
1. Validate routing works for all 10 orchestrators
2. Resume Phase 6.4 (Sanitization v2 Migration) with clarity on AUTONOMOUS vs GUIDED
3. Continue remaining migrations (Debug v2, etc.)
4. All future orchestrators follow Hybrid Ownership Model

**Benefits Unlocked:**
- ✅ Routing logic in code (testable, versioned)
- ✅ No token budget concerns
- ✅ Deterministic behavior
- ✅ Clear separation: routing vs execution
- ✅ Easier to add new orchestrators (just update table)

---

## 📚 Key Files Referenced in Phase 6.4.5

**To Read:**
- `.github/prompts/CORTEX.prompt.md` (current 850 lines)
- `cortex-brain/config/master-orchestrator.yaml`
- `cortex-brain/response-templates-v4.yaml`
- `cortex-brain/brain-protection-rules.yaml`
- `src/orchestrators/pattern_router.py`
- `src/orchestrators/master_orchestrator.py`

**To Create:**
- `cortex-brain/documents/analysis/cortex-prompt-structure-analysis.md`
- `cortex-brain/documents/orchestrators-quick-ref.md`
- `cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/artifacts/cortex-prompt-lean-spec.md`
- `cortex-brain/documents/reports/cortex-prompt-lean-migration-report.md`
- `.github/prompts/CORTEX.prompt.md.v4.backup`

**To Update:**
- `.github/prompts/CORTEX.prompt.md` (lean version)
- `src/orchestrators/pattern_router.py` (add prompt parsing)
- `tests/orchestrators/test_pattern_router_prompt_parsing.py` (new tests)

---

## 🎓 Context from Previous Work

**What We've Learned from 3 Completed Migrations:**

1. **ADO v2 (Phase 6.1):**
   - Dual-mode architecture (wizard + auto) works well
   - Master Orchestrator routing by mode is effective
   - Conversational wizard requires state tracking

2. **Cleanup v2 (Phase 6.2):**
   - Selective modes (cache/logs/artifacts/full/git) via single orchestrator
   - Safe execution order prevents dependency issues
   - Atomic operations crucial for rollback

3. **Vacuum v2 (Phase 6.3):**
   - Progressive hashing (size → quick → full) optimizes performance
   - 5-level risk classification prevents dangerous deletions
   - Checkpoint system enables safe cleanup

**Pattern:** All successful AUTONOMOUS orchestrators have:
- Clear state management (database or in-memory)
- Rollback capability
- Phase-based execution
- Master Orchestrator routing integration

**This pattern should guide Sanitization v2 and Debug v2 design.**

---

## 🚀 Ready to Start?

When you begin your next session, say:
```
Continue with cortex-v5-holistic-refactor plan - Phase 6.4.5
```

The Cross-Session Context Middleware will:
1. Load this continuation prompt context
2. Route to Planning System v5
3. Resume at Phase 6.4.5, Sub-Task 6.4.5.1

**Let's establish architectural clarity before continuing migrations!** 🎯
