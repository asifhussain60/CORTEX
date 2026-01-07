# Autonomous Orchestrator v5.0 Implementation Plan

**Plan ID:** auto-orch-v5-impl  
**Status:** 🟢 READY FOR IMPLEMENTATION  
**Created:** January 2, 2026

---

## 📁 Plan Structure

```
auto-orch-v5-impl/
├── mst-pure-autonomous.md     # Complete implementation plan (main file)
├── context/
│   └── source-plan.md         # Reference to autonomous-orchestrator-v5 plan
├── artifacts/
│   └── file-name-rules.md     # Filename validation rules (≤20 chars)
├── reports/
│   └── (generated during implementation)
└── tracking/
    └── progress.json          # Progress tracking data
```

---

## 🎯 What This Plan Does

This plan implements the **Pure Autonomous Architecture (Option 1)** from `autonomous-orchestrator-v5/00-MASTER-PLAN-V5.md`.

### Key Transformations

1. **Remove Hybrid Ambiguity**
   - Convert manifests to pure configuration (no natural language)
   - Python orchestrators own ALL execution logic
   - CORTEX becomes thin client (route → invoke → display)

2. **Add State Management**
   - SQLite database for transactional phases
   - ACID transactions with rollback on failure
   - Single source of truth for plan status

3. **Implement MCP Tool**
   - Universal `invoke_orchestrator()` tool
   - Registry maps names to Python classes
   - Integration with CORTEX.prompt.md intent routing

4. **Enforce Filename Standards** (Custom Addition)
   - All filenames ≤20 characters
   - kebab-case format only
   - Validation before file creation
   - Auto-fix for violations

### Orchestrators Affected

All 4 AUTONOMOUS orchestrators will be refactored:

1. **Planning System v5.0** - Context discovery, plan generation
2. **ADO Operations v2.0** - Work item generation, acceptance criteria
3. **Vacuum v2.0** - Filesystem scanning, safe deletion
4. **Cleanup v2.0** - Cache management, log rotation

---

## 📊 Timeline

- **Duration:** 27 days
- **Phases:** 12 (Phase 0 through Phase 11)
- **Target Start:** January 3, 2026
- **Target Completion:** January 30, 2026

---

## 🚀 Getting Started

### Review
1. Read `mst-pure-autonomous.md` for complete details
2. Review `context/source-plan.md` for architecture decisions
3. Check `artifacts/file-name-rules.md` for naming conventions

### Begin Implementation
1. Start with Phase 0: Foundation Setup
2. Create `src/utils/file_name.py` with validation
3. Set up project structure
4. Proceed phase by phase

---

## 📚 Key Documents

### In This Plan
- **mst-pure-autonomous.md** - Complete implementation plan (1800+ lines)
- **context/source-plan.md** - Architecture alignment reference
- **artifacts/file-name-rules.md** - Filename validation specification
- **tracking/progress.json** - Machine-readable progress data

### Source Plans
- `autonomous-orchestrator-v5/00-MASTER-PLAN-V5.md` - Original architecture
- `autonomous-orchestrator-v5/architecture/option-1-analysis.md` - Detailed analysis
- `autonomous-orchestrator-v5/architecture/database-schema.md` - DB design

### CORTEX References
- `.github/prompts/CORTEX.prompt.md` - Intent routing
- `cortex-brain/brain-protection-rules.yaml` - SKULL rules
- `cortex-brain/response-templates-v4.yaml` - Response templates

---

## ✅ Success Criteria

- Zero ambiguity in execution flow
- Atomic phase operations with rollback
- Single source of truth (database)
- Deterministic output (templates + data)
- 100% filename compliance (≤20 chars)
- 100% test coverage
- Plans resumable from any phase

---

## 🎓 Lessons from Previous Plan Issue

**Problem:** The `cortex-arch-changes` plan didn't reflect `autonomous-orchestrator-v5` instructions.

**Root Cause:** Generic "architecture changes" request without explicit reference to autonomous-v5 plan.

**Solution Applied:**
- Explicit source plan reference in `context/source-plan.md`
- Clear alignment checklist
- Direct implementation of Option 1 architecture
- Added custom filename validation per user requirement

---

**Next Action:** Review `mst-pure-autonomous.md` and approve Phase 0 to begin implementation.
